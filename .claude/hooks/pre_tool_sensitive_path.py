#!/usr/bin/env python3
"""
PreToolUse hook (T146) — fires before every Edit, Write and Bash tool call.

Asks the human first when the call touches a path listed in
`.claude/sensitive-paths.txt` (`.env*`, secrets, production configs, infra),
unless the active task's guide predicted that exact path under
`## Files to Change (Predicted)`.

Decisions, and the direction every uncertainty resolves:

* Sensitive and not predicted -> `ask`, the reason naming the path and pattern.
* Sensitive and predicted, or not sensitive -> no output, exit 0: "no decision,
  normal permission flow applies". Deliberately NOT `allow` — `allow` skips the
  permission prompt for the *whole* call, which grants more than this hook's
  concern (see tasks/TASK_REVIEW_T146.md, "Assumption check").
* Malformed stdin, an unreadable pattern file, or a helper module that fails to
  import -> `ask`. Fail toward the human, never a silent allow (AC5).

Board mode `online` (T157, NFR-005): guides are pulled from the board, whose text anyone
with workspace access can write, so no guide's prediction exempts a sensitive path — it
always asks. An unusable `.claude/board.json` counts as online here (the safe side).

Online approve-once (T314): the trust source is the user's own yes, never board text.
Approvals apply to Edit and Write only: their `file_path` is exact. Every Bash call
that touches a sensitive path asks, as before, approved or not. When this hook asks
about an Edit or Write in online mode with an active task, it writes
`.claude/state/pending/<tool_use_id>.json` = `{"task_id": T, "keys": [...]}`. If the
user says yes, the call runs and the PostToolUse recorder
`post_tool_sensitive_approval.py` moves exactly those keys under T into
`.claude/state/sensitive-approvals.json` (gitignored), but only when the event's
`permission_mode` is `default` or `auto` (the modes where an `ask` shows the prompt).
Keys are files only, never a directory: one key per file, root-relative under the
project root, else its absolute realpath. A later Edit or Write in T of an approved
file gets no output (no decision, never `allow`). When the key differs from the path
as written (a symlink), the ask names both: `config/prod.json → .env`. No active task
-> no approval, every call asks. Always sensitive and never approvable (hard-coded
below, not in the pattern list): `.claude/state` and everything under it, any file
named `sensitive-approvals.json*`, any file named `sensitive-paths.txt` (the list itself,
T316), and `.claude` or `.claude/state` named in a Bash
call that changes directory or uses `-C`. A symlinked or bad approval file counts as
empty. Local mode neither reads nor writes any of it. To withdraw every approval,
delete the file.

Bash: the command's heredoc bodies and its *data* quoted spans are removed with
`lib/shell_data.py` first — the only sanctioned way to separate command text from
data (T099's three fail-opens came from fresh regexes). Quoted spans T099 classes
as executable are kept, so `bash -c "cat > .env"` still asks. What is left is
split into tokens and each token is checked as a path.

Folder-level calls (T363, option C): a Bash segment whose command is `rm -r`, `find -delete`,
`find -exec`/`-execdir`/`-ok`/`-okdir` running `rm`/`mv`/`shred`/`unlink`/`rmdir`/`truncate`,
`mv` (its sources), `git checkout`, or `git restore` (not `--staged` alone) asks when one of its
arguments, or a folder its glob matches, is a folder under the project root or the cwd that holds
a sensitive path: a walk (one budget of `FOLDER_WALK_MAX` entries per call, `.git` skipped) finds a
listed or protected file in it, or the walk cannot finish or cannot read a folder. A `cd`/`pushd`
segment, wrapped or not, adds its target to the folders later segments are judged against (T374). A `{a,b}` brace token is expanded and each
expansion is checked as a path; a token over `MAX_BRACE_EXPANSIONS` paths asks.

Under `[admin]` (T371): when the session tag `[admin]` holds (`auto_mode.session_request`, which
honours `[stop]`, another tag and a resume), the hook does not ask. A call that only reads
(`READ_ONLY_COMMANDS`, words dequoted, no environment prefix, redirect or `tee`) gets no output. Any
other call gets no decision (the normal permission flow, never `allow`) after one JSON line (time,
session, agent, task, tool, target, paths, patterns) is appended to
`<anchors base>/<repo slug>/sensitive-admin-<session>.jsonl` (the folder must be ours, mode 0700 and
not a link; the file is opened `O_APPEND|O_NOFOLLOW`, 0600), and an `additionalContext` note asks for a
line in the task's final report. A call that touches the guard's own files (`PROTECTED_PATTERNS`)
still asks, a read included, and so does any call whose log line cannot be written.

Recorded limitations (cut list, TASK_GUIDE_T146; T363):
* Paths built from variables (`cat "$F"`, `${f}itive-paths.txt`), `eval`, and the code of
  `python -c` / `node -e` spans are not resolved (T363 option C).
* The folder rule knows only the verbs above: `git reset --hard`, `git clean`, `git stash`,
  `cp -r`, `rsync --delete`, `tar -x`, `ln -sf`, a script or an alias acting on a folder do not
  ask (T363 option C). Nor does a destructive command inside quoted code (`bash -c "rm -rf x"`,
  `sh -c '…'`, `find -exec sh -c '…'`, `env -S "…"`), one fed its folders by `xargs` (`… | xargs rm -rf`,
  `xargs rm -rf config`), a folder named through a variable (`$PWD/config`), or
  `git -C <dir> restore` (T374).
  A folder outside both roots is never walked (a sibling worktree).
* A Bash command that only *reads* a sensitive path (`grep KEY .env`) asks too —
  reads and writes are not cheaply distinguishable in a command string.
* A glob inside a kept quoted span is expanded too, as code (T342), except when the
  span's segment command is on `NO_GLOB_COMMAND_PATTERN` (`grep`, `egrep`, `fgrep`,
  `rg`, `sed`, `sort`, `cut`, `tr`: they neither glob nor run a shell) and the span
  carries no executor (`SPAN_EXECUTOR_PATTERN`) and, for `sed`, no `e` command
  (`SED_EXECUTE_PATTERN`). The outer shell does not expand quoted text, so
  `sed 's/ - .*//'` names no file. Every other quoted span (`su -c`, `xargs`, `awk`,
  `git add '.c*'`, `find -name`) still expands: unknown resolves toward code. Its
  literal tokens are still checked in every case.
* Globs are expanded against the project root (the hook's `cwd`), not against the
  directory a `cd` in the command moves to.
"""
import glob
import itertools
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
PATTERNS_RELPATH = os.path.join(".claude", "sensitive-paths.txt")
PREDICTED_HEADING = "Files to Change (Predicted)"
# What is passed to read_guide_section: its slicer puts `\b` after the heading,
# which can never match after a closing `)`. The slicer accepts a trailing
# qualifier, so the bare prefix resolves `## Files to Change (Predicted)`.
PREDICTED_LOOKUP = "Files to Change"
TAG = "[hook:sensitive-path]"
# T314: the online approval state. `.claude/state` and everything under it is always
# sensitive, protected here rather than by a line in `.claude/sensitive-paths.txt`, so
# a project's list edit cannot drop it.
STATE_RELDIR = ".claude/state"
STATE_PATTERN = STATE_RELDIR + "/**"
APPROVALS_RELPATH = STATE_RELDIR + "/sensitive-approvals.json"
PENDING_RELDIR = STATE_RELDIR + "/pending"
# S2: the approval file's name is sensitive in any directory (a `cd .claude` call can
# write it under a relative path no root-anchored pattern sees).
APPROVALS_NAME_PATTERNS = ("sensitive-approvals.json", "sensitive-approvals.json.*")
# T316: the pattern list itself, by name in any directory (a `cd .claude` call can write it
# under a relative path). Without it an edit of the list could drop every line, with no ask.
LIST_NAME_PATTERN = os.path.basename(PATTERNS_RELPATH)
PROTECTED_PATTERNS = (STATE_PATTERN,) + APPROVALS_NAME_PATTERNS + (LIST_NAME_PATTERN,)
# S2: a Bash token naming `.claude` or `.claude/state` asks when the call changes
# directory or uses `-C`, because then a relative path may land in the state folder.
DIR_CHANGE_TOKENS = {"cd", "pushd", "-C", "--directory"}
STATE_PARENTS = (".claude", STATE_RELDIR)
APPROVABLE_TOOLS = ("Edit", "Write")
TOOL_USE_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,200}\Z")

# Guarded like pre_bash_block_unsafe_merge.py: an unguarded ImportError exits 1
# with empty stdout, which the harness treats as a non-blocking error and lets
# the call through — the silent allow AC5 forbids. The failure is kept and
# turned into an `ask` in main().
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
try:
    from project_root import exit_outside_kit_project  # noqa: E402
    from project_root import project_root as project_dir  # noqa: E402
    exit_outside_kit_project()  # T232: first, so a broken lib stays silent in a non-kit project
    from guide_sections import read_guide_section  # noqa: E402
    from shell_data import strip_heredoc_bodies, strip_quoted_spans  # noqa: E402
    from shell_data import SEGMENT_BOUNDARY_PATTERN, SPAN_EXECUTOR_PATTERN  # noqa: E402
    from task_context import resolve_task_id  # noqa: E402
    from board.moments import board_mode  # noqa: E402
    import auto_mode  # noqa: E402
    from trace_chain import ANCHOR_DIR_ENV, DEFAULT_ANCHOR_BASE, repo_slug  # noqa: E402
    IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - exercised via subprocess test
    IMPORT_ERROR = exc

# Where a shell token ends. Quote characters are separators too, because a
# quoted span T099 keeps as code (`bash -c "cat > .env"`) arrives with its quotes.
# `:` too (T314): `git show :.env` and `HEAD:.env` read the file; splitting only adds asks.
TOKEN_PATTERN = re.compile(r"[^\s;&|<>()`'\"=:]+")
GLOB_CHARS = re.compile(r"[*?\[]")
# T342: a segment whose command neither globs its arguments nor runs a shell. Anchored at the
# segment start like shell_data's DATA_COMMAND_PATTERN: only `VAR=value` and a path may come
# first, so `sudo sed`, `xargs grep` keep the default (expand). Short on purpose: a command
# missing here over-asks, a command wrongly added here hides a path.
NO_GLOB_COMMAND_PATTERN = re.compile(
    r"\s*(?:[A-Za-z_]\w*=\S*\s+)*(?:[\w.\-/]*/)?"
    r"(grep|egrep|fgrep|rg|sed|sort|cut|tr)(?:\s|\Z)"
)
# GNU sed runs a shell for the `e` command (`1e cmd`, `e cmd`) and the `s///e` flag, which may
# sit anywhere in the flag run (`/ge`, `/eg`, `/3ew f`). Any `e` inside a run of flag letters
# and digits counts, so a word like `gem` over-asks: the safe side.
SED_EXECUTE_PATTERN = re.compile(r"(?<![A-Za-z])[gpIiMmw0-9]*e[gpIiMmw0-9]*(?![A-Za-z])")
MAX_GLOB_MATCHES = 200
BACKTICK_SPAN_PATTERN = re.compile(r"`([^`]+)`")
# A quoted word right after an output redirect (`>`, `>>`, `>|`, `&>`, `2>`).
# strip_quoted_spans treats every quoted span behind `echo`/`printf` as data,
# but a redirect target is where the output is written, not data.
QUOTED_REDIRECT_TARGET_PATTERN = re.compile(r"""(?:&|\d*)>[>|]?\s*(?:"([^"]*)"|'([^']*)')""")
# T363 (option C): a segment whose command deletes or moves a whole folder asks when one of its
# arguments is a folder that holds a sensitive path. The verbs are C's list; any other verb is a
# recorded limitation (header). `rm` and `find` count only with the flags that act on a tree.
FOLDER_VERBS = {"rm", "find", "mv", "git"}
RM_TREE_FLAGS = re.compile(r"-[A-Za-z]*[rR]|--recursive\Z")
FIND_ACTION_FLAGS = {"-delete", "-exec", "-execdir", "-ok", "-okdir"}
GIT_FOLDER_SUBCOMMANDS = {"checkout", "restore"}
COMMAND_PREFIXES = {"sudo", "env", "command", "builtin", "nice", "nohup", "time", "exec", "timeout"}
# T374: a wrapper option that takes its value as the next word (`timeout -s KILL`, `sudo -u root`),
# so the value is not read as the command. Each segment is read twice, with these skips and
# without them, and the folder rule judges both readings: an entry that is wrong (an option that
# takes no value) or missing can then only add an ask, never hide the command (T374 round 1).
# `env -S` is not here: its value is the command line itself.
PREFIX_VALUE_OPTIONS = {
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "sudo": {"-u", "--user", "-g", "--group", "-C", "--close-from", "-h", "--host", "-p", "--prompt",
             "-U", "--other-user", "-D", "--chdir", "-r", "--role", "-t", "--type", "-R", "--chroot",
             "-T", "--command-timeout"},
    "env": {"-u", "--unset", "-C", "--chdir", "-P", "-a", "--argv0"},
    "nice": {"-n", "--adjustment"},
    "time": {"-o", "--output", "-f", "--format"},
    "exec": {"-a"},
}
# `find -exec`/`-ok` asks only when the command it runs deletes or moves (round 1: `-exec grep`
# reads); `-delete` always does.
FIND_DESTRUCTIVE_EXEC = {"rm", "mv", "shred", "unlink", "rmdir", "truncate"}
# A token whose `{a,b}` groups would expand to more than this many paths is not expanded: the
# check asks instead (round 1: the expansion is exponential, and a hook that times out is silent).
MAX_BRACE_EXPANSIONS = 1000
DIR_CHANGE_COMMANDS = {"cd", "pushd"}
# T374 round 3: the folders a call may have moved to. A `cd` segment adds its target to the set and
# keeps the old folders, so a later segment is judged against every folder it may run in: a `cd`
# that moves the shell (`cd`, `FOO=1 cd`, `command cd`, `\cd`) and one that does not (`sudo cd`)
# are both covered without telling them apart. The set can double with each `cd`: past the cap the
# check asks (a `ValueError` main() turns into an ask), never drops a folder (T374 round 4).
MAX_CD_FOLDERS = 64
# T371: under `[admin]` a call that only reads passes with no log. A read is a Bash call whose every
# segment runs one of these commands, with no output redirect or `tee` anywhere; anything else is a
# write (an unknown command too) and is logged. Short on purpose: a command missing here only adds a
# log line.
# Only programs that cannot write or run anything (round 1: `rg --pre`, `file -C`, and `git`, whose
# repository config can run a program on `diff`/`log`, are writes).
READ_ONLY_COMMANDS = {"ls", "cat", "head", "tail", "grep", "egrep", "fgrep", "wc", "stat", "find"}
FIND_WRITE_FLAG_PREFIXES = ("-delete", "-exec", "-ok", "-fprint", "-fls")
ADMIN_LOG_PREFIX = "sensitive-admin-"
# The walk of a folder stops after this many entries; a folder it could not finish counts as
# holding a sensitive path (toward the human). Overridable for tests.
FOLDER_WALK_MAX = 20000
FOLDER_WALK_ENV = "CLAUDE_SENSITIVE_FOLDER_WALK_MAX"
BRACE_PATTERN = re.compile(r"\{[^{}]*,[^{}]*\}")


# --- Pattern file ------------------------------------------------------------

def pattern_file_path(root):
    """The project's list; the plugin's own copy only when the project has none (T233).

    A hook run from a plugin cache sits at `<plugin>/.claude/hooks`, so the copy shipped with the
    plugin is `<plugin>/.claude/sensitive-paths.txt`. In the `setup.sh` install the two paths are
    the same file, so nothing changes there. A project file that exists but cannot be read is
    still returned, so the caller asks; it never falls back.
    """
    project_file = os.path.join(root, PATTERNS_RELPATH)
    if os.path.lexists(project_file):
        return project_file
    plugin_file = os.path.join(os.path.dirname(HOOKS_DIR), "sensitive-paths.txt")
    return plugin_file if os.path.lexists(plugin_file) else project_file


def expand_braces(pattern):
    """`prod*.{yml,json}` -> [`prod*.yml`, `prod*.json`]. Nested groups recurse."""
    match = re.search(r"\{([^{}]*)\}", pattern)
    if not match:
        return [pattern]
    head, tail = pattern[:match.start()], pattern[match.end():]
    expanded = []
    for option in match.group(1).split(","):
        expanded.extend(expand_braces(head + option + tail))
    return expanded


def glob_to_regex(glob_pattern):
    """Translate one brace-free glob: `*` stays in a directory, `**` crosses them."""
    out = []
    i = 0
    while i < len(glob_pattern):
        if glob_pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob_pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif glob_pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif glob_pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(glob_pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def parse_patterns(text):
    """Return `[(raw_line, negated, has_slash, [compiled regex, ...]), ...]`.

    Windows separators are normalised to `/`. A pattern with no `/` matches a
    file name in any directory; one with a `/` matches from the project root.
    """
    patterns = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        negated = raw.startswith("!")
        body = raw[1:] if negated else raw
        body = body.replace("\\", "/").lstrip("/")
        if not body:
            continue
        regexes = [glob_to_regex(g) for g in expand_braces(body)]
        patterns.append((raw, negated, "/" in body, regexes))
    return patterns


def load_patterns(path):
    """Read and parse the pattern file. Raises OSError when it is unreadable."""
    with open(path, encoding="utf-8") as f:
        return parse_patterns(f.read())


# --- Path matching -----------------------------------------------------------

def _within(path, root):
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        return None
    if rel == "." or rel == ".." or rel.startswith(".." + os.sep):
        return None
    return rel.replace(os.sep, "/")


def path_forms(path, cwd, roots):
    """Every form a path is checked in, as `(anchored, path_string)` pairs.

    Anchored: relative to a root it lies under (the project dir or the call's
    cwd — a Stage 3 agent's cwd is its own worktree). Both the path as given and
    its resolved form are checked, so a symlink cannot route around a pattern.
    A path under no root is *floating*: a `/` pattern may match from any of its
    directories, which over-asks rather than guesses an anchor.
    """
    path = path.replace("\\", "/")
    absolute = os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))
    forms = []
    for candidate in {absolute, os.path.realpath(absolute)}:
        anchored = [rel for rel in (_within(candidate, r) for r in roots) if rel]
        if anchored:
            forms.extend((True, rel) for rel in anchored)
        else:
            forms.append((False, candidate.replace(os.sep, "/").lstrip("/")))
    return forms


def _pattern_matches(has_slash, regexes, anchored, path_string):
    if not has_slash:
        name = path_string.rsplit("/", 1)[-1]
        return any(rx.match(name) for rx in regexes)
    # Each path is also tried as a directory, so `infra/**` covers `infra`
    # itself: `rm -rf infra` removes the whole tree the pattern protects.
    if anchored:
        candidates = [path_string]
    else:
        parts = path_string.split("/")
        candidates = ["/".join(parts[i:]) for i in range(len(parts))]
    return any(rx.match(c) or rx.match(c + "/") for rx in regexes for c in candidates)


def matching_pattern(forms, patterns):
    """The pattern line that marks this path sensitive, or None. Last match wins."""
    for anchored, path_string in forms:
        verdict = None
        for raw, negated, has_slash, regexes in patterns:
            if _pattern_matches(has_slash, regexes, anchored, path_string):
                verdict = None if negated else raw
        if verdict:
            return verdict
    return None


# --- Bash tokens -------------------------------------------------------------

def command_tokens(command, cwd):
    """Path-like tokens of the command text left after shell_data strips data.

    A token carrying glob characters is expanded against the filesystem the way
    the shell would (`cat .env*`), and kept as written too. Quoted redirect
    targets are collected before shell_data strips them as data (`echo x > ".env"`).
    A glob in a quoted span `unexpanded_globs` marks is not expanded (T342).
    """
    unheredoc = strip_heredoc_bodies(command)
    tokens = [double or single
              for double, single in QUOTED_REDIRECT_TARGET_PATTERN.findall(unheredoc)
              if double or single]
    text = strip_quoted_spans(unheredoc)
    masked = unexpanded_globs(text)
    for match in TOKEN_PATTERN.finditer(text):
        start, end = match.span()
        tokens.append(match.group())
        if BRACE_PATTERN.search(match.group()):  # T363: `.claude/{a,b}` names both paths
            tokens.extend(capped_brace_expansion(match.group()))
        if GLOB_CHARS.search(masked[start:end]):
            matches = glob.iglob(os.path.join(cwd, match.group()), recursive=True)
            tokens.extend(itertools.islice(matches, MAX_GLOB_MATCHES))
    return tokens


def unexpanded_globs(text):
    """`text` with the glob characters of every quoted span the shell leaves unexpanded
    replaced by `_`, same length, so token offsets line up (T342).

    A span counts only when its segment command matches `NO_GLOB_COMMAND_PATTERN`, the span
    has no executor and, behind `sed`, no `e` command. The scan mirrors shell_data's
    `strip_quoted_spans`: quotes pair with the next same quote, a segment boundary outside a
    span starts a new segment, and an unterminated quote or a backslash-escaped opening quote
    ends the scan, so the tail keeps its globs (`\\\\"` over-asks: the safe side). Quote characters are token separators, so no token mixes a span with outside text.
    """
    out = list(text)
    segment_start = 0
    i = 0
    while i < len(text):
        char = text[i]
        if char in "\"'":
            if i and text[i - 1] == "\\":
                break  # `\"` is a literal quote: what follows is unquoted (Stage 4 P1)
            close = text.find(char, i + 1)
            if close == -1:
                break
            span = text[i:close + 1]
            command = NO_GLOB_COMMAND_PATTERN.match(text[segment_start:i])
            if (command and not SPAN_EXECUTOR_PATTERN.search(span)
                    and not (command.group(1) == "sed" and SED_EXECUTE_PATTERN.search(span))):
                for k in range(i + 1, close):
                    if GLOB_CHARS.match(text, k):
                        out[k] = "_"
            i = close + 1
            continue
        boundary = SEGMENT_BOUNDARY_PATTERN.match(text, i)
        if boundary:
            segment_start = boundary.end()
            i = boundary.end()
            continue
        i += 1
    return "".join(out)


# --- Predicted paths ---------------------------------------------------------

def predicted_paths(task_id, tasks_dirs):
    """Backticked paths in the first column of the task's predicted-files table."""
    if not task_id:
        return set()
    for tasks_dir in tasks_dirs:
        body = read_guide_section(task_id, PREDICTED_LOOKUP, tasks_dir)
        if body is None:
            continue
        paths = set()
        for line in body.splitlines():
            cells = line.strip().strip("|").split("|")
            if not line.strip().startswith("|") or not cells:
                continue
            for span in BACKTICK_SPAN_PATTERN.findall(cells[0]):
                normalized = span.strip().replace("\\", "/")
                while normalized.startswith("./"):
                    normalized = normalized[2:]
                if normalized:
                    paths.add(normalized)
        return paths
    return set()


def is_predicted(forms, predicted):
    return any(anchored and path_string in predicted for anchored, path_string in forms)


# --- Online approvals (T314) -------------------------------------------------

def _rel(root, relpath):
    return os.path.join(root, *relpath.split("/"))


def approvals_file(root):
    return _rel(root, APPROVALS_RELPATH)


def pending_file(root, tool_use_id):
    """`.claude/state/pending/<tool_use_id>.json`, or None for an id unsafe as a file name."""
    if not isinstance(tool_use_id, str) or not TOOL_USE_ID_PATTERN.match(tool_use_id):
        return None
    return os.path.join(_rel(root, PENDING_RELDIR), tool_use_id + ".json")


def state_is_real(root, path):
    """True when `.claude/state` is a real folder of this project and `path` (no symlink) is in it."""
    state = _rel(root, STATE_RELDIR)
    if os.path.islink(state) or os.path.islink(path):
        return False
    real_state = os.path.join(os.path.realpath(root), *STATE_RELDIR.split("/"))
    return (os.path.realpath(state) == real_state
            and os.path.realpath(path).startswith(real_state + os.sep))


def read_json_in_state(root, path):
    """The JSON at `path` under a real `.claude/state`, else None."""
    if not state_is_real(root, path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_json_in_state(root, path, data):
    """Write `data` to `path` atomically; refuse a symlinked or foreign `.claude/state`."""
    for step in ("check", "create"):
        if step == "create":
            os.makedirs(os.path.dirname(path), exist_ok=True)
        if not state_is_real(root, path):
            raise OSError(f"{STATE_RELDIR} is not this project's own folder")
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)


def read_approvals(root):
    """The approval file as `{task_id: [key, ...]}`. Anything unusable -> `{}` (asks)."""
    data = read_json_in_state(root, approvals_file(root))
    if not isinstance(data, dict):
        return {}
    return {task: [p for p in paths if isinstance(p, str)]
            for task, paths in data.items()
            if isinstance(task, str) and isinstance(paths, list)}


def is_state_key(key):
    """Never approvable: anything under `.claude/state`, or a `sensitive-approvals.json*` file."""
    name = key.rsplit("/", 1)[-1]
    return (key == STATE_RELDIR or key.startswith(STATE_RELDIR + "/")
            or name == "sensitive-approvals.json" or name.startswith("sensitive-approvals.json."))


def file_key(path, cwd, root):
    """The one approval key of a file: root-relative under the root, else its absolute
    realpath. None for a directory or anything under `.claude/state` (never approvable).
    Built from the path as the OS sees it: no `\\` rewrite and no lexical `normpath` first,
    because on Linux `\\` is a file-name character (`a\\..\\b` is one new file, not `b`).
    None for a key that holds a `\\`: such a file is never approvable, it always asks."""
    real = os.path.realpath(os.path.join(cwd, path))
    if os.path.isdir(real) or "\\" in real:
        return None
    key = _within(real, os.path.realpath(root)) or real.replace(os.sep, "/")
    return None if is_state_key(key) else key


def _walk_cap():
    try:
        return max(0, int(os.environ.get(FOLDER_WALK_ENV, FOLDER_WALK_MAX)))
    except ValueError:
        return FOLDER_WALK_MAX


def capped_brace_expansion(token):
    """`expand_braces(token)`, or a `ValueError` (main() then asks) when its groups would give more
    than `MAX_BRACE_EXPANSIONS` paths. Counted before expanding, innermost groups first."""
    count, rest = 1, token
    while True:
        group = BRACE_PATTERN.search(rest)
        if not group:
            break
        count *= group.group().count(",") + 1
        if count > MAX_BRACE_EXPANSIONS:
            raise ValueError(f"a brace token expands to more than {MAX_BRACE_EXPANSIONS} paths")
        rest = rest[:group.start()] + "x" + rest[group.end():]
    return expand_braces(token)


def held_sensitive_path(folder, cwd, roots, patterns, budget):
    """`(path, pattern)` of the first sensitive file under `folder`, or None. `.git` is skipped.
    `budget` (`[entries left]`) is shared by every folder of the call and counts folders and files.
    A walk that runs out of budget, or cannot list a folder, counts as a hit (T363 AC 4)."""
    errors = []
    for top, dirs, files in os.walk(folder, onerror=errors.append):
        if errors:
            return (folder, "a folder that could not be read")
        dirs[:] = [d for d in dirs if d != ".git"]
        budget[0] -= len(dirs) + len(files)
        if budget[0] < 0:
            return (folder, f"more than {_walk_cap()} entries, not all checked")
        for name in files:
            path = os.path.join(top, name)
            pattern = matching_pattern(path_forms(path, cwd, roots), patterns)
            if pattern:
                return (path, pattern)
    if errors:  # round 1: an unreadable folder that is the last one reached
        return (folder, "a folder that could not be read")
    return None


def _segment_command(words, skip_values=True):
    """The command word of a segment and its arguments, past `VAR=value` words and the
    `COMMAND_PREFIXES` wrappers (`sudo`, `env`, …) and their options; a path prefix is dropped."""
    i = 0
    while i < len(words):
        word = words[i]
        if re.match(r"[A-Za-z_]\w*=", word):
            i += 1
        elif os.path.basename(word) in COMMAND_PREFIXES:
            wrapper = os.path.basename(word)
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if skip_values and words[i] in PREFIX_VALUE_OPTIONS.get(wrapper, ()) else 1
            if wrapper == "timeout" and i < len(words):
                i += 1  # its duration
        else:
            return os.path.basename(word.lstrip("\\")), words[i + 1:]
    return None, []


def _folder_arguments(verb, args):
    """The arguments a destructive `verb` acts on as a tree, or [] when this use is not one."""
    paths = [a for a in args if not a.startswith("-") and a not in ("{}", ";", "+")]
    if verb == "rm":
        return paths if any(RM_TREE_FLAGS.match(a) for a in args) else []
    if verb == "find":
        runs = [os.path.basename(args[k + 1]) for k, a in enumerate(args[:-1])
                if a in FIND_ACTION_FLAGS and a != "-delete"]
        if "-delete" not in args and not FIND_DESTRUCTIVE_EXEC.intersection(runs):
            return []
        start = []
        for a in args:  # find's start paths come before the first expression word
            if a.startswith(("-", "(", "!")):
                break
            start.append(a)
        return start or ["."]
    if verb == "mv":
        return paths[:-1] if len(paths) > 1 else paths  # the sources; the target is not removed
    if verb == "git":
        sub = next((a for a in args if not a.startswith("-")), None)
        if sub not in GIT_FOLDER_SUBCOMMANDS:
            return []
        if sub == "restore" and ({"--staged", "-S"} & set(args)) and not (
                {"--worktree", "-W"} & set(args)):
            return []  # the index only, not the files
        return paths[1:]
    return []


def folder_hits(command, cwd, roots, patterns):
    """T363 (option C): `[(folder, forms, pattern)]` for each folder a destructive segment acts on
    that holds a sensitive path. A folder under neither root is skipped (a sibling worktree). A
    `cd`/`pushd` segment moves the folder later segments resolve against."""
    text = strip_quoted_spans(strip_heredoc_bodies(command))
    hits, wheres, budget, walked = [], [cwd], [_walk_cap()], set()
    for segment in SEGMENT_BOUNDARY_PATTERN.split(text):
        # the shell drops quotes and backslashes inside a word too (`-de''lete` is `-delete`, T371)
        words = [re.sub(r"[\"'\\()]", "", re.split(r"\d*[<>]", w, 1)[0]) for w in segment.split()]
        words = [w for w in words if w and not w.startswith(("<", ">", "2>", "&>"))]
        readings = [_segment_command(words)]
        plain = _segment_command(words, skip_values=False)
        if plain != readings[0]:
            readings.append(plain)
        for verb, args in readings:
            if verb in DIR_CHANGE_COMMANDS:
                target = next((a for a in args if not a.startswith("-")), None)
                if target:
                    moved = [os.path.normpath(os.path.join(w, os.path.expanduser(target))) for w in wheres]
                    wheres = list(dict.fromkeys(wheres + moved))
                    if len(wheres) > MAX_CD_FOLDERS:
                        raise ValueError(f"the command changes folder into more than {MAX_CD_FOLDERS} "
                                         "possible folders")
        targets = [a for v, rest in readings if v in FOLDER_VERBS for a in _folder_arguments(v, rest)]
        for arg, where in dict.fromkeys((a, w) for a in targets for w in wheres):
            # each (argument, folder) once: both readings and every `cd` folder share the budget
            base = os.path.join(where, os.path.expanduser(arg))
            folders = ([base] if not GLOB_CHARS.search(arg) else
                       list(itertools.islice(glob.iglob(base), MAX_GLOB_MATCHES)))
            for folder in dict.fromkeys(os.path.normpath(f) for f in folders):
                if folder in walked:
                    continue
                walked.add(folder)
                if not os.path.isdir(folder) or not any(
                        _within(folder, r) or os.path.realpath(folder) == os.path.realpath(r)
                        for r in roots):
                    continue
                found = held_sensitive_path(folder, cwd, roots, patterns, budget)
                if found:
                    hits.append((arg, path_forms(folder, cwd, roots), found[1]))
    return hits


def admin_in_force(event):
    """T371: True when `[admin]` holds for this call: the session tag, or the latest request the user
    typed (outside code spans and quotes, `[stop]` in it turns it off). Read only from the
    transcript, as the merge gate reads it; any doubt is False (the hook asks)."""
    # The session tag only: every typed `[admin]` sets it, and it is the reader that honours `[stop]`,
    # another tag and a resume (round 1: a fallback to the latest request kept a pre-resume tag).
    session = auto_mode.session_request(event.get("transcript_path"))
    return session is not None and session[0] == "admin"


def only_reads(tool_name, tool_input):
    """T371: True when the call can only read (see `READ_ONLY_COMMANDS`); an Edit or Write never is."""
    if tool_name != "Bash":
        return False
    text = strip_quoted_spans(strip_heredoc_bodies(tool_input.get("command") or ""))
    if re.search(r"[<>]|\btee\b", text):
        return False
    seen = False
    for segment in SEGMENT_BOUNDARY_PATTERN.split(text):
        # the shell drops quotes and backslashes inside a word (`-de''lete` is `-delete`)
        words = [re.sub(r"[\"'\\()]", "", w) for w in segment.split()]
        words = [w for w in words if w]
        if not words:
            continue
        seen = True
        if re.match(r"[A-Za-z_]\w*=", words[0]):
            return False  # an environment prefix can make a reader run a program
        for verb, args in (_segment_command(words), _segment_command(words, skip_values=False)):
            if verb not in READ_ONLY_COMMANDS:
                return False
            if verb == "find" and any(a.startswith(FIND_WRITE_FLAG_PREFIXES) for a in args):
                return False
    return seen


def admin_log_path(root, session_id):
    """`<anchors base>/<repo slug>/sensitive-admin-<session>.jsonl` (the folder `.claude/settings.json`
    denies agents write access to), or a `ValueError` (main() asks)."""
    base = os.environ.get(ANCHOR_DIR_ENV) or os.path.expanduser(DEFAULT_ANCHOR_BASE)
    if not os.path.isabs(base):
        raise ValueError("the anchors folder is not an absolute path")
    if not isinstance(session_id, str) or not auto_mode.SESSION_ID.fullmatch(session_id):
        raise ValueError("no session id to name the [admin] approval log")
    return os.path.join(base, repo_slug(root), f"{ADMIN_LOG_PREFIX}{session_id}.jsonl")


def log_admin_approval(root, event, task_id, listed):
    """T371: append one JSON line for an approved write; the path of the log. Any failure raises
    (main() then asks): the approval exists only with its log line."""
    path = admin_log_path(root, event.get("session_id"))
    folder = os.path.dirname(path)
    os.makedirs(folder, mode=0o700, exist_ok=True)
    info = os.lstat(folder)  # round 1: the folder itself must be ours, private, and not a link
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077 \
            or info.st_uid != os.getuid():
        raise ValueError(f"the [admin] approval log folder {folder} is a link, shared or not ours")
    tool_input = event.get("tool_input") or {}
    target = tool_input.get("command") if event.get("tool_name") == "Bash" else tool_input.get("file_path")
    line = {"time": datetime.now(timezone.utc).isoformat(), "session": event.get("session_id"),
            "decision": "not asked by the hook ([admin])",
            "agent": event.get("agent_id"), "task": task_id, "tool": event.get("tool_name"),
            "target": str(target)[:2000], "paths": [p for p, _ in listed],
            "patterns": [pat for _, pat in listed]}
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.write(fd, (json.dumps(line, sort_keys=True) + "\n").encode("utf-8"))
    finally:
        os.close(fd)
    return path


def sensitive_hits(tool_name, tool_input, cwd, roots, patterns):
    """`[(path, forms, pattern), ...]` for every sensitive path of the call.

    `.claude/state/**` is appended as the last pattern, so no `!` line in the
    project's list can unmark it (last match wins).
    """
    patterns = patterns + parse_patterns("\n".join(PROTECTED_PATTERNS))
    paths = candidate_paths(tool_name, tool_input, cwd)
    changes_dir = tool_name == "Bash" and any(t in DIR_CHANGE_TOKENS for t in paths)
    hits = []
    for path in paths:
        forms = path_forms(path, cwd, roots)
        pattern = matching_pattern(forms, patterns)
        if not pattern and changes_dir and any(
                anchored and f in STATE_PARENTS for anchored, f in forms):
            pattern = STATE_PATTERN
        if pattern:
            hits.append((path, forms, pattern))
    if tool_name == "Bash":
        hits.extend(folder_hits(tool_input["command"], cwd, roots, patterns))
    return hits


def written_key(path, cwd, root):
    """The path as written, in key form but unresolved: shows when a symlink moves the key.
    No `\\` rewrite, as in `file_key`."""
    absolute = os.path.normpath(os.path.join(cwd, path))
    return _within(absolute, root) or absolute.replace(os.sep, "/")


def is_online(roots):
    """Board mode online for any root; an unusable board.json counts as online (T157)."""
    return any(board_mode(r) != "local" for r in roots)


# --- Hook protocol -----------------------------------------------------------

def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": f"{TAG} {reason}",
        }
    }))
    sys.exit(0)


def candidate_paths(tool_name, tool_input, cwd):
    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path")
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError(f"{tool_name} call has no file_path")
        return [file_path]
    command = tool_input.get("command")
    if not isinstance(command, str):
        raise ValueError("Bash call has no command string")
    return command_tokens(command, cwd)


def record_pending(root, tool_use_id, task_id, keys):
    """What this ask covers, for the PostToolUse recorder. A failed write only means
    no approval is recorded: the ask still goes out."""
    path = pending_file(root, tool_use_id)
    if path is None:
        return
    try:
        write_json_in_state(root, path, {"task_id": task_id, "keys": keys})
    except Exception:
        pass


def main():
    if IMPORT_ERROR is not None:
        ask(f"Sensitive-path check unavailable ({type(IMPORT_ERROR).__name__}: "
            f"{IMPORT_ERROR}) — cannot tell whether this call touches a sensitive "
            "path. Restore .claude/hooks/lib/.")

    try:
        event = json.load(sys.stdin)
        tool_name = event["tool_name"]
        tool_input = event["tool_input"]
        if not isinstance(tool_input, dict):
            raise ValueError("tool_input is not an object")
    except Exception as exc:
        ask(f"Malformed hook input ({type(exc).__name__}: {exc}) — cannot tell "
            "whether this call touches a sensitive path.")

    if tool_name not in ("Edit", "Write", "Bash"):
        sys.exit(0)

    root = project_dir()
    patterns_file = pattern_file_path(root)
    try:
        patterns = load_patterns(patterns_file)
    except Exception as exc:
        ask(f"Sensitive-path list unreadable ({patterns_file}: "
            f"{type(exc).__name__}) — cannot tell whether this call touches a "
            "sensitive path. Restore .claude/sensitive-paths.txt.")

    try:
        cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else None
        cwd = cwd or os.getcwd()
        roots = [root, cwd]
        hits = sensitive_hits(tool_name, tool_input, cwd, roots, patterns)
        if not hits:
            sys.exit(0)

        task_id = resolve_task_id(event)
        board_text = is_online(roots)
        predicted = set() if board_text else predicted_paths(
            task_id, [os.path.join(root, "tasks"), os.path.join(cwd, "tasks")]
        )
        online_task = board_text and task_id
        approvable = tool_name in APPROVABLE_TOOLS
        approved = (set(read_approvals(root).get(task_id, []))
                    if online_task and approvable else set())
        unpredicted, keys = [], []
        for p, forms, pat in hits:
            protected = pat in PROTECTED_PATTERNS
            key = None if protected else file_key(p, cwd, root)
            if is_predicted(forms, predicted) and not protected:
                continue
            if key and key in approved:
                continue
            shown = p if not key or key == written_key(p, cwd, root) else f"{p} \u2192 {key}"
            unpredicted.append((shown, pat))
            if key and key not in keys:
                keys.append(key)
        if not unpredicted:
            sys.exit(0)
        if admin_in_force(event) and not any(pat in PROTECTED_PATTERNS for _, pat in unpredicted):
            # T371: the guard's own files always ask, a read form included (round 1, V1)
            if only_reads(tool_name, tool_input):
                sys.exit(0)  # a read passes under [admin], with no log
            log = log_admin_approval(root, event, task_id, unpredicted)
            note = ("[admin]: the sensitive-path hook did not ask about this " + tool_name + " call (" +
                    ", ".join(f"{p} (pattern `{pat}`)" for p, pat in unpredicted) +
                    f"); not asked, logged to {log}. The normal permission flow still applies. "
                    "Add one line for it to the task's final report.")
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                     "additionalContext": note}}))
            sys.exit(0)  # no decision: the normal permission flow; never `allow`
        if online_task and keys and approvable:
            record_pending(root, event.get("tool_use_id"), task_id, keys)
    except SystemExit:
        raise
    except Exception as exc:
        ask(f"Sensitive-path check failed ({type(exc).__name__}: {exc}) — "
            "asking rather than guessing.")

    listed = ", ".join(f"{p} (pattern `{pat}`)" for p, pat in unpredicted)
    owner = (f"the active task {task_id} does not list it under '## {PREDICTED_HEADING}'"
             if task_id else "no active task predicts it")
    if board_text:
        owner = ("board mode is online, where guides come from the board and cannot "
                 "pre-authorise a sensitive path")
        if task_id and keys and tool_name in APPROVABLE_TOOLS:
            owner += (f". After you approve, a later Edit or Write of these files in {task_id} "
                      "will not ask again")
        elif task_id and keys:
            owner += (f". A Bash call always asks; after you approve an Edit or Write of these "
                      f"files in {task_id}, a later Edit or Write of them will not ask again")
    ask(f"This {tool_name} call touches a sensitive path: {listed}. "
        f"Listed in .claude/sensitive-paths.txt and {owner}.")


if __name__ == "__main__":
    main()
