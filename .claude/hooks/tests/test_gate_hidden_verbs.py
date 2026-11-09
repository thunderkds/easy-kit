#!/usr/bin/env python3
"""T296 — the merge gate no longer lets a hidden git verb or a `git merge` option value through
(`tasks/TASK_GUIDE_T296.md` rows 1-3 and 6-8; findings P2-1, P2-2, P3-1, P3-3, P3-4 of
`tasks/GATE_HUNT_2026-11-08.md`).

  * Row 1 — under `[auto]` and `[admin]` a command whose git word, git verb or wrapper chain is not
    a plain literal word is blocked, and so is `git send-pack`. With no tag nothing changes.
  * Row 2 — the commands `[admin]` allows today are still allowed; ordinary `[auto]` commands too.
  * Row 3 — the value of a `git merge` option is never read as the branch.
  * Row 5 — the trace gate reads a command the way the shell does (backslash, line continuation).
  * Row 6 — a branch push to a clone whose `origin` is another remote is refused.
  * Row 7 — the refusal for `git log --output=` names its reason; the doc names what the code does.
  * Row 8 — a corpus of old results: every old answer holds except the shapes of rows 1, 3 and 5.

Every board, guide, transcript and git repo here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_gate_hidden_verbs.py -q
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import G, MERGE, PUSH, gate, git, kanban, merge_gate, write  # noqa: E402
from test_admin_tag import (  # noqa: E402
    AFTER, admin_session, auto_verified, human, reason, session, transcript)

assert gate  # the fixture, imported for pytest

ROOT = Path(__file__).resolve().parents[3]
TRACKS = ROOT / "docs" / "claude-md" / "tracks.md"
B = "feat/t900-x"

# Row 1: each of these really pushed under `[auto]` and `[admin]` before T296 (the gate hunt).
HIDDEN_FORMS = [
    f"v=push; git $v origin {B}",
    f"g=git; $g push origin {B}",
    f"v=pu; git ${{v}}sh origin {B}",
    f"git {{p..p}}ush origin {B}",
    f"git $'push' origin {B}",
    f"$'git' push origin {B}",
    f'env -i git "push" origin {B}',
    f'timeout 20 git "push" origin {B}',
    f'nice git "push" origin {B}',
    f"bash -c 'git \"push\" origin {B}'",
    f"git send-pack ../origin.git {B}",
]
# More of the same family: wrapper chains, option values, other quoting, other publishing verbs.
HIDDEN_MORE = [
    f"v=merge; git $v {B}", f"v=pull; git $v", f"git -C /x $v origin {B}",
    f"env FOO=1 git $v origin {B}", f'env -u HOME git "push" origin {B}',
    f'timeout -k 5 20 git "push" origin {B}', f'sudo -u root git "push" origin {B}',
    f'nohup git "push" origin {B}', f'command git "$v" origin {B}', f'exec git "push" origin {B}',
    f'time -p git "push" origin {B}', f"/usr/bin/git $'push' origin {B}",
    f"$g -C /x push origin {B}", f"timeout 20 $g push origin {B}",
    f"git ${{v}}sh origin {B}", f"git pu* origin {B}", f"git p?sh origin {B}", f"git `echo push` x",
    f"=git push origin {B}", f"bash -c '$g push origin {B}'", f'sh -c "git \\"push\\" origin {B}"',
    f"git http-push https://example.invalid/r.git {B}", f"git -C /x send-pack ../o.git {B}",
    f'echo hi; timeout 5 git "push" x', f"true && v=push && git $v origin {B}",
    f'strace -f git "push" origin {B}', f"flock /tmp/l git $'push' origin {B}",
    f"env -S 'git \"push\" origin {B}'", f'xargs -I{{}} git "push" {{}}', f'{{ git "push" x; }}',
    f'if true; then git "push" x; fi', f"for b in a; do git $v x; done", f'exec -a x git "push" x',
    f'echo hi | xargs git "push"', f'(git "push" origin {B})', f'/usr/bin/env git "$v" x',
]
# Never blocked in auto mode: data, commits and ordinary tools stay allowed.
BENIGN = [
    "git status", "git log --oneline -5", "git diff --stat", "git add -A && git commit -m x",
    'git commit -m "git push later"', "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\"",
    'git commit -m "$(date)"', "echo done", 'grep -n "git push" notes.md', "python3 -m pytest -q",
    "pytest tests/test_x.py", 'pytest -k "a*"', "cd /tmp && ls", "ls *.py", "echo {a,b}",
    'git -C "$d" status', 'git -C "$d" log -1', "git fetch origin", "git checkout -b fix/t900-x",
    "git branch -m fix/t900-y", "git stash", "git rebase main", "git merge-base HEAD main",
    "git remote -v", "git tag v1", "git reset --hard HEAD", "git log --format='%H' | head -3",
    'x="$(git rev-parse HEAD)"; echo $x', "echo $HOME", "echo $(date)", "make test",
    '"$VENV/bin/pytest" -q', "$PY -m pytest -q", '"$PY" -m pytest -q tests', "$HOME/bin/tool run",
    "env -i pytest", "timeout 20 pytest", "nice pytest", "timeout 20 git status", "nice git log",
    "env -i git status", "bash -c 'git status'", 'bash -c "echo hi"', "gh pr create --title t",
    "python3 -c 'print(1)'", "FOO=$X pytest -q", "env FOO=$X pytest", "timeout $T pytest -q",
    "cp git x", "man git", "ls git", "echo git $v", 'grep git "$f"', '[ "$x" = a ] && echo hi',
    "which git", "command -v git", "git --version", "git commit -m x && git log -1",
    "for f in a b; do git add $f; done", "if [ -f x ]; then git status; fi", "xargs -n1 git status",
    "ln -s /usr/bin/git ~/bin/git", "docker run -v $PWD:/x img", "curl -s https://x/{a,b}",
    "find . -name x | xargs -I{} cp {} /tmp", "timeout 20 pytest -q", "timeout -k 5 20 python3 -m pytest",
    'env FOO=$X pytest -k "$Y"',
]


@pytest.mark.parametrize("command", HIDDEN_FORMS + HIDDEN_MORE)
def test_row1_unit_a_hidden_verb_form_is_flagged(command):
    assert merge_gate.hidden_git_verb(command), command


@pytest.mark.parametrize("command", BENIGN)
def test_row1_unit_ordinary_commands_are_not_flagged(command):
    assert not merge_gate.hidden_git_verb(command), command


def test_row1_unit_a_long_wrapper_chain_is_read_fast_and_flagged():
    """One pass over the words: a chain of 300 wrappers must not blow up (a DoS of the hook)."""
    import time
    started = time.time()
    assert merge_gate.hidden_git_verb("env " * 300 + 'git "push" origin x')
    assert time.time() - started < 2
    deep = merge_gate._Scan()
    merge_gate._scan_simple(["ls"], merge_gate.HIDDEN_DEPTH_LIMIT + 1, set(), deep)
    assert deep.doubt  # nested too deep: doubt


@pytest.mark.parametrize("command", HIDDEN_FORMS)
@pytest.mark.parametrize("tag", ["[admin]", "[auto]"])
def test_row1_the_gate_blocks_each_hidden_form_in_auto_and_admin_mode(gate, tmp_path, command, tag):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    path = admin_session(tmp_path, fx, request="merge and push T900 " + tag)
    text = reason(command, fx.wt, path)
    assert text is not None and "cannot push/merge" in text, (command, text)


@pytest.mark.parametrize("command", HIDDEN_FORMS)
def test_row1_with_no_tag_the_hidden_forms_behave_as_before(gate, tmp_path, command):
    """The hidden-verb check is an auto-mode rule (`hidden_git_verb`'s docstring): no tag, no change."""
    fx = gate(kanban(done=("T900",)))
    assert reason(command, fx.wt, None) is None
    assert reason(command, fx.wt, transcript(tmp_path, [human("thanks", AFTER)])) is None


@pytest.mark.parametrize("command", [
    f"v=push; git $v origin {B}", f'timeout 20 git "push" origin {B}', "git send-pack ../origin.git " + B])
def test_row1_the_block_names_the_reason(gate, tmp_path, command):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    text = reason(command, fx.wt, admin_session(tmp_path, fx))
    assert "cannot tell" in text and "hidden form" in text, text


AUTO_OK = ["git status", "git log --oneline -5", "git diff --stat", "git add -A && git commit -m x",
           "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\"", 'grep -n "git push" notes.md', "echo done",
           "python3 -m pytest -q", "cd /tmp && ls", '$PY -m pytest -q', 'timeout $T pytest -q',
           'git -C "$d" status']


@pytest.mark.parametrize("command", AUTO_OK)
@pytest.mark.parametrize("tag", ["[admin]", "[auto]"])
def test_row2_ordinary_commands_stay_allowed_in_auto_mode(gate, tmp_path, command, tag):
    fx = gate(kanban(done=("T900",)))
    path = transcript(tmp_path, [human("go " + tag, AFTER)])
    assert reason(command, fx.main, path) is None, command


def _verified(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    return fx, session(tmp_path, fx, "do it [admin]")


def test_row2_admin_still_allows_its_push_and_merge_forms(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    assert reason(PUSH + " origin " + B, fx.wt, path) is None
    assert reason(G + "-C " + fx.main + " merge " + B, fx.root, path) is None
    assert reason(G + "--no-pager merge " + B, fx.main, path) is None
    assert reason("cd " + fx.main + " && " + MERGE + " " + B, fx.root, path) is None
    assert reason(MERGE + " --no-ff -m 'T900 merge' " + B, fx.main, path) is None


# ── Row 3 — the value of a `git merge` option is never the branch ────────────────────────────
MERGE_SOURCE_CASES = [  # (args, branch names the gate must read)
    (["--message", B], []), (["-m", B], []), (["--file", B], []), (["-F", B], []),
    (["-s", "ours", B], [B]), (["-X", "theirs", B], [B]), (["--cleanup=strip", B], [B]),
    (["--cleanup", "strip", B], [B]), (["--strategy", "ours", B], [B]),
    (["--strategy-option", "theirs", B], [B]), (["--into-name", "main", B], [B]),
    (["--mess", B], []), (["--fi", B], []), (["-qm", B], []), (["-qm", "msg", B], [B]),
    (["-nqF", "f", B], [B]), (["-mmsg", B], [B]), (["-Xours", B], [B]), (["-S", B], [B]),
    (["--gpg-sign", B], [B]), (["--no-ff", "--message=msg", B], [B]), (["--squash", B], [B]),
    ([B, "feat/t901-y"], [B, "feat/t901-y"]),
]


@pytest.mark.parametrize("args,names", MERGE_SOURCE_CASES)
def test_row3_merge_options_with_a_value_do_not_give_the_branch(args, names):
    assert [n for _, n in merge_gate._merge_sources(args, "/w")] == names


def test_row3_message_is_not_the_branch_with_a_real_repo_and_default_to_upstream(gate, tmp_path):
    """Git takes `--message <x>` as the message and, with `merge.defaultToUpstream`, merges the
    upstream (here `up`). The gate used to read `feat/t900-x` as the branch and check T900's row."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    git(fx.main, "checkout", "-q", "-b", "up")
    write(os.path.join(fx.main, "upstream.txt"), "unverified upstream work\n")
    git(fx.main, "add", "-A")
    git(fx.main, "commit", "-qm", "unverified upstream work")
    git(fx.main, "checkout", "-q", "main")
    git(fx.main, "branch", "--set-upstream-to=up", "main")
    git(fx.main, "config", "merge.defaultToUpstream", "true")
    command = MERGE + " --message " + B
    assert merge_gate.branch_target(command, fx.main) is None  # no branch is read
    text = reason(command, fx.main, session(tmp_path, fx, "do it [admin]"))
    assert text is not None and "names exactly one task branch" in text, text
    # the premise, run for real after the gate checks: git merges `up` and uses the value as message
    git(fx.main, "merge", "--no-ff", "--message", B)
    assert os.path.exists(os.path.join(fx.main, "upstream.txt"))
    assert git(fx.main, "log", "-1", "--format=%s") == B


def test_row3_a_plain_branch_is_still_the_target(gate):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    assert merge_gate.branch_target(MERGE + " " + B, fx.main)[:2] == ("T900", B)
    assert merge_gate.branch_target(MERGE + " -m msg " + B, fx.main)[:2] == ("T900", B)
    assert merge_gate.branch_target(MERGE + " --message msg " + B, fx.main)[:2] == ("T900", B)
    assert merge_gate.branch_target(MERGE + " --message " + B, fx.main) is None


# ── Row 5 — the trace gate reads a command the way the shell does ───────────────────────────
NOT_A_RUN = ["cd w && echo ok \\\npytest", "cd w && echo done\\; pytest",
             'cd w && echo "a\\" && pytest && echo \\"b"', "echo a\\|pytest", "echo \\& pytest"]
A_RUN = ["pytest", "cd w && pytest -q", "cd w && echo ok\npytest", "echo a;pytest", "echo a \\\\; pytest",
         'echo "x"; pytest', "echo 'it''s'; pytest", "pytest\\\n-q", "py\\\ntest", "echo a\\ b; pytest",
         "timeout 60 python3 -m pytest -q", "cd w && echo done \\\n && pytest"]


@pytest.mark.parametrize("command", NOT_A_RUN)
def test_row5_a_mention_after_a_backslash_is_not_a_test_run(command):
    assert not merge_gate.invokes_test_runner(command), command


@pytest.mark.parametrize("command", A_RUN)
def test_row5_real_runs_still_count(command):
    assert merge_gate.invokes_test_runner(command), command


# ── Row 6 (P3-3) — a branch push goes only to this repository's own remote ──────────────────
def _clone_with_origin(fx, url_of_origin=None):
    """A clone of the fixture's `origin` that holds `feat/t900-x` (with the hook-written verify row),
    its `origin` optionally set to another remote."""
    git(fx.wt, "push", "-q", "origin", B)
    clone = os.path.join(fx.root, "clone")
    git(fx.root, "clone", "-q", os.path.join(fx.root, "origin.git"), clone)
    git(clone, "checkout", "-q", B)
    if url_of_origin:
        git(clone, "remote", "set-url", "origin", url_of_origin)
    return clone


def test_row6_a_clone_with_the_same_origin_url_may_push_its_branch(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    clone = _clone_with_origin(fx)
    assert reason("cd " + clone + " && " + PUSH + " origin " + B, fx.wt, path) is None


def test_row6_a_clone_whose_origin_is_another_remote_is_refused(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    other = os.path.join(fx.root, "elsewhere.git")
    git(fx.root, "init", "-q", "--bare", other)
    clone = _clone_with_origin(fx, other)
    text = reason("cd " + clone + " && " + PUSH + " origin " + B, fx.wt, path)
    assert text is not None and "remote" in text and "origin" in text, text


def test_row6_the_repositorys_own_branch_push_is_unchanged(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    assert reason(PUSH + " origin " + B, fx.wt, path) is None
    assert reason(PUSH, fx.wt, path) is None


# ── Row 7 (P3-4) — the refusal names its reason; the doc names what the code does ────────────
@pytest.mark.parametrize("read,needle", [
    ("git log --output=/tmp/o", "--output"), ("git diff --output=/tmp/o", "--output"),
    ("git show --ext-diff HEAD", "--ext-diff")])
def test_row7_an_option_outside_the_read_only_allowlist_names_its_reason(gate, tmp_path, read, needle):
    fx, path = _verified(gate, tmp_path)
    text = reason(read + " && " + PUSH + " origin " + B, fx.wt, path)
    assert text is not None and needle in text, text
    assert "cannot tell which branch" not in text, text


def test_row7_rev_parse_in_an_admin_chain_is_refused_and_the_doc_says_so(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    text = reason("git rev-parse HEAD && " + PUSH + " origin " + B, fx.wt, path)
    assert text is not None and "rev-parse" in text, text
    item2 = re.search(r"2\. The command merges one task branch.*?\n3\. ", TRACKS.read_text(), re.S).group(0)
    flat = re.sub(r"\s+", " ", item2)
    assert "`rev-parse` and `cd <dir> &&` may stay" not in flat
    assert "`git status`, `log`, `diff` and `show`" in flat and "`rev-parse` is refused" in flat


def test_row7_the_known_limits_bullet_drops_what_is_fixed():
    flat = re.sub(r"\s+", " ", TRACKS.read_text(encoding="utf-8"))
    assert "Cheap hidden verbs" not in flat and "`git merge --message <branch>` are not caught" not in flat


def test_row7_the_auto_mode_hidden_verb_limit_states_the_new_rule():
    flat = re.sub(r"\s+", " ", TRACKS.read_text(encoding="utf-8"))
    assert "a git word or a git verb that is not a plain literal word" in flat
    assert "`git send-pack`" in flat and "`timeout`" in flat


# ── Row 8 — a corpus of the old gate's answers: all of them hold except the fixed shapes ─────
# Generated from the gate at `bc5ccc34` (before T296). `CHANGED` lists the only entries that differ.
OLD_HIDDEN = {
    "git status": False, "git log --oneline -5": False, "git diff --stat": False,
    "git add -A && git commit -m 'x'": False, 'git commit -m "git push later"': False,
    "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\"": False, "echo done": False,
    'grep -n "git push" notes.md': False, "python3 -m pytest -q": False,
    "pytest tests/test_x.py": False, "cd /tmp && ls": False, "ls -la | head": False,
    "git -C /tmp/x status": False, 'git -C "$d" status': False, 'git -C "$d" log -1': False,
    "git fetch origin": False, "git checkout -b fix/t900-x": False,
    "git branch -m fix/t900-y": False, "git stash": False, "git rebase main": False,
    "git push origin feat/t900-x": True, "git push": True, "git merge feat/t900-x": True,
    "git pull": True, "git merge-base HEAD main": False, "git remote -v": False,
    "git config user.name x": False, 'git "push" origin main': True, "git 'push' origin main": True,
    'git pu""sh origin main': True, "git p\\ush origin main": True, '"git" push origin main': True,
    "g''it push origin main": True, "git ${IFS}push origin main": True,
    "$(echo git) push origin main": True, "`echo git` push origin main": True,
    "eval git push origin main": True, 'git "merge" feat/t900-x': True, 'git "pull"': True,
    'command git "push" origin main': True, 'env git "push" x': True, 'sudo git "push" x': True,
    'nohup git "push" x': True, 'time git "push" x': True, 'exec git "push" x': True,
    'FOO=1 git "push" x': True, 'git -c core.x=y "push" x': True, 'git --no-pager "push" x': True,
    'echo hi; git "push" x': True, 'true && git "merge" b': True, 'true || git "pull"': True,
    "bash -c 'git status'": False, 'bash -c "echo hi"': False, "echo $(date)": False,
    "echo $HOME": False, "echo `date`": False, 'x="$(git rev-parse HEAD)"; echo $x': False,
    "VAR=$(git rev-parse HEAD) pytest": True, "git log --format='%H' | head -3": False,
    "git diff HEAD~1 | wc -l": False, "cat tasks/x.md": False, "gh pr create --title t": False,
    "docker run x": False, "make test": False, "npm test": False, "ls *.py": False,
    "echo {a,b}": False, 'git commit -m "$(date)"': False, "git commit --amend --no-edit": False,
    "git tag v1": False, "git reset --hard HEAD": False, "python3 -c 'print(1)'": False, "env": False,
    "env -i pytest": False, "timeout 20 pytest": False, "nice pytest": False,
    "timeout 20 git status": False, "nice git log": False, "env -i git status": False,
}
OLD_MERGE_SOURCES = [
    (["feat/t900-x"], ["feat/t900-x"]), (["--no-ff", "feat/t900-x"], ["feat/t900-x"]),
    (["-m", "msg", "feat/t900-x"], ["feat/t900-x"]),
    (["--no-ff", "-m", "T900 merge", "feat/t900-x"], ["feat/t900-x"]),
    (["-s", "ours", "feat/t900-x"], ["feat/t900-x"]), (["-X", "theirs", "feat/t900-x"], ["feat/t900-x"]),
    (["-Xours", "feat/t900-x"], ["feat/t900-x"]), (["--strategy", "ours", "feat/t900-x"], ["feat/t900-x"]),
    (["--strategy-option", "theirs", "feat/t900-x"], ["feat/t900-x"]),
    (["--strategy=ours", "feat/t900-x"], ["feat/t900-x"]), (["-F", "msgfile", "feat/t900-x"], ["feat/t900-x"]),
    (["--into-name", "main", "feat/t900-x"], ["feat/t900-x"]),
    (["--message", "feat/t900-x"], ["feat/t900-x"]), (["-m", "feat/t900-x"], []),
    (["--file", "feat/t900-x"], ["feat/t900-x"]), (["-F", "feat/t900-x"], []),
    (["--cleanup=strip", "feat/t900-x"], ["feat/t900-x"]),
    (["--cleanup", "strip", "feat/t900-x"], ["strip", "feat/t900-x"]),
    (["--squash", "feat/t900-x"], ["feat/t900-x"]), (["--no-commit", "feat/t900-x"], ["feat/t900-x"]),
    (["--edit", "feat/t900-x"], ["feat/t900-x"]), (["-S", "feat/t900-x"], ["feat/t900-x"]),
    (["feat/t900-x", "feat/t901-y"], ["feat/t900-x", "feat/t901-y"]), (["--abort"], []),
    (["--quiet", "-q", "feat/t900-x"], ["feat/t900-x"]), (["-qm", "feat/t900-x"], ["feat/t900-x"]),
    (["-qm", "msg", "feat/t900-x"], ["msg", "feat/t900-x"]),
    (["--mess", "feat/t900-x"], ["feat/t900-x"]), (["-mmsg", "feat/t900-x"], ["feat/t900-x"]),
    (["--log", "feat/t900-x"], ["feat/t900-x"]), (["--no-verify", "feat/t900-x"], ["feat/t900-x"]),
]
CHANGED_MERGE_SOURCES = {  # args -> the answer after T296 (rows 3)
    ("--message", "feat/t900-x"): [], ("--file", "feat/t900-x"): [],
    ("--cleanup", "strip", "feat/t900-x"): ["feat/t900-x"], ("-qm", "feat/t900-x"): [],
    ("-qm", "msg", "feat/t900-x"): ["feat/t900-x"], ("--mess", "feat/t900-x"): [],
}
OLD_RUNNER = {
    "pytest": True, "cd x && pytest": True, "python3 -m pytest -q": True, "timeout 60 pytest": True,
    "echo pytest": False, 'echo "pytest"': False, "grep pytest x": False,
    "python3 -B -m pytest -q": True, "python3 -c 'import pytest'": False,
    "cd w && echo ok\npytest": True, "echo a;pytest": True, "true || pytest": True, "(pytest)": True,
    "env pytest": True, "sudo pytest": True, "FOO=1 pytest": True, "npm test": True, "make test": False,
    "bash run_tests.sh": True, "cat <<EOF\npytest\nEOF": True, "echo 'it''s'; pytest": True,
    'echo "x"; pytest': True, "ls | pytest": True, "pytest &": True, "tox": True, "go test ./...": True,
    "cargo test": True, "jest": True, "./scripts/smoke.sh": True, "python3 -m unittest": True,
    "uv run pytest": True, "poetry run pytest": True, "pytest\\\n-q": True,
    "echo 'a' && pytest 'b'": True, 'echo "a b" pytest': False, "echo a\\ b; pytest": True,
    "echo a\\\\; pytest": True,
    # the shapes of row 5 (old answer True, a mention counted as a run) and a continuation (old False)
    "cd w && echo ok \\\npytest": True, "cd w && echo done\\; pytest": True,
    'cd w && echo "a\\" && pytest && echo \\"b"': True, "py\\\ntest": False,
}
CHANGED_RUNNER = {"cd w && echo ok \\\npytest": False, "cd w && echo done\\; pytest": False,
                  'cd w && echo "a\\" && pytest && echo \\"b"': False, "py\\\ntest": True}


@pytest.mark.parametrize("command", list(OLD_HIDDEN))
def test_row8_corpus_hidden_verb_answers_hold(command):
    assert bool(merge_gate.hidden_git_verb(command)) is OLD_HIDDEN[command], command


@pytest.mark.parametrize("args,old", OLD_MERGE_SOURCES)
def test_row8_corpus_merge_sources_hold_except_the_fixed_shapes(args, old):
    want = CHANGED_MERGE_SOURCES.get(tuple(args), old)
    assert [n for _, n in merge_gate._merge_sources(list(args), "/w")] == want, args


@pytest.mark.parametrize("command", list(OLD_RUNNER))
def test_row8_corpus_test_run_answers_hold_except_the_fixed_shapes(command):
    want = CHANGED_RUNNER.get(command, OLD_RUNNER[command])
    assert bool(merge_gate.invokes_test_runner(command)) is want, command


def test_row8_the_corpus_changes_only_what_the_rows_name():
    assert len(CHANGED_MERGE_SOURCES) == 6 and len(CHANGED_RUNNER) == 4


# ═══ Stage 4 fix round (two reviews, ~280 candidates run in real bash and zsh) ═══════════════════
# Rule behind these: EVERY word whose basename is `git` or `git-<verb>` is a git word; a verb that
# cannot be read is a doubt; a doubt is a refusal in auto mode (never the other way round).
EXEC = "/usr/lib/git-core"
HIDDEN_R2 = {
    # C1 — a redirect between git and its verb
    "c1-redirect-out": f"git >/dev/null push origin {B}",
    "c1-redirect-in": f"git </dev/null push origin {B}",
    "c1-redirect-both": f"git &>/dev/null push origin {B}",
    "c1-env-prefix": f"FOO=1 git >/dev/null push origin {B}",
    "c1-after-C": f"git -C . >/dev/null push origin {B}",
    "c1-merge-pager": f"git --no-pager >/dev/null merge {B}",
    "c1-force-main": "git >/dev/null push -f origin main",
    "c1-merge": f"git >/dev/null merge {B}",
    "c1-fd-redirect": f"git 2>/dev/null push origin {B}",
    # S1 — `--attr-source <tree>` takes a value
    "s1-push": f"git --attr-source HEAD push origin {B}",
    "s1-merge": f"git --attr-source HEAD merge {B}",
    "s1-pull": "git --attr-source HEAD pull",
    "s1-super-prefix": f"git --super-prefix x/ push origin {B}",
    # S2 — a rebase earlier in the command
    "s2-rebase-then-quoted-push": 'git rebase --abort 2>/dev/null; git "push" origin main',
    # S3 — the first word that looks like git is not the git word
    "s3-env-u": f'env -u git git "push" origin {B}',
    "s3-xargs-E": f'xargs -E git git "p""ush" origin {B}',
    # S4 — brace expansion in the command word, eval, a line continuation in the git word
    "s4a-brace-command-word": f"{{git,push}} origin {B}",
    "s4a-brace-in-word": f"g{{i,}}t push origin {B}",
    "s4c-eval-quoted": f"eval 'g\"\"it push origin {B}'",
    "s4c-eval-var": 'eval "$x push"',
    "s4c-eval-wrapped": f"env eval 'git push origin {B}'",
    "s4d-continuation": f"g\\\nit push origin {B}",
    "s4d-continuation-verb": f"git pu\\\nsh origin {B}",
    # C2 — env -S with an attached value
    "c2-attached": f"env -S'git \"push\" origin {B}'",
    "c2-long": f"env --split-string='git \"push\" origin {B}'",
    "c2-clustered": f"env -iS'git \"push\" origin {B}'",
    # C3 — dashed git commands
    "c3-send-pack": f"{EXEC}/git-send-pack ../origin.git {B}",
    "c3-push": f"{EXEC}/git-push origin {B}",
    "c3-exec-path-sub": f'"$(git --exec-path)/git-send-pack" ../origin.git {B}',
    "c3-path-prefix": f"PATH={EXEC}:$PATH git-push origin {B}",
    "c3-merge": f"git-merge {B}", "c3-pull": "git-pull", "c3-http-push": "git-http-push x",
    "c3-remote-ext": "git-remote-ext x", "c3-in-wrapper": f"timeout 5 git-push origin {B}",
    "c3-var-dashed": f"git-$v origin {B}",
    # C4 — an alias through the environment
    "c4-count": f"GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.x GIT_CONFIG_VALUE_0=push git x origin {B}",
    "c4-parameters": f"GIT_CONFIG_PARAMETERS=\"'alias.x=push'\" git x origin {B}",
    "c4-env": f"env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.x GIT_CONFIG_VALUE_0=push git x origin {B}",
    "c4-export": f"export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.x GIT_CONFIG_VALUE_0=push; git x origin {B}",
    "c4-exec-path": f"GIT_EXEC_PATH=/tmp/evil git status",
    "c4-config-global": "GIT_CONFIG_GLOBAL=/tmp/g git status",
    "c4-config-system": "GIT_CONFIG_SYSTEM=/tmp/g git status",
    # C5 — `xargs git` with the verb on stdin
    "c5-echo-pipe": f"echo push origin {B} | xargs git",
    "c5-herestring": f"xargs git <<< 'push origin {B}'",
    "c5-printf0": f"printf 'push\\0origin\\0{B}' | xargs -0 git",
    # C6 / S5 — a path-qualified git after an unknown head or a redirect
    "c6-flock": f'flock /tmp/l /usr/bin/git "push" origin {B}',
    "s5-redirect-head": f'>/dev/null /usr/bin/git "push" origin {B}',
    "c6-busybox": f'busybox /usr/bin/git "push" origin {B}',
    "c6-nonwrapper-git": f'strace -f git "push" origin {B}',
    # C8 — other verbs that publish or run a program
    "c8-subtree": f"git subtree push --prefix=a origin {B}",
    "c8-svn": "git svn dcommit", "c8-p4": "git p4 submit", "c8-cvs": "git cvsexportcommit HEAD",
    "c8-receive-pack": "git receive-pack ../origin.git", "c8-remote-ext": "git remote-ext x",
    # 9 — shell keywords start a command
    "k-if": "g=git; if true; then $g push x; fi", "k-for": "g=git; for i in 1; do $g push x; done",
    "k-not": "g=git; ! $g push x", "k-brace": "g=git; { $g push x; }",
    # 17 — a command word the shell builds from a glob or a brace
    "w-glob": "g[i]t push x", "w-brace": "{g,}it push x",
    # a variable the same command sets, used as the command word
    "taint-two-vars": f"g=git; v=push; $g $v origin {B}",
    "taint-wrapped": f"g=git; env $g status",
}


@pytest.mark.parametrize("name", list(HIDDEN_R2))
def test_r2_unit_each_reviewed_form_is_flagged(name):
    assert merge_gate.hidden_git_verb(HIDDEN_R2[name]), HIDDEN_R2[name]


@pytest.mark.parametrize("name", list(HIDDEN_R2))
@pytest.mark.parametrize("tag", ["[admin]", "[auto]"])
def test_r2_the_gate_blocks_each_reviewed_form(gate, tmp_path, name, tag):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    path = admin_session(tmp_path, fx, request="merge and push T900 " + tag)
    text = reason(HIDDEN_R2[name], fx.wt, path)
    assert text is not None and "cannot push/merge" in text, (name, text)


@pytest.mark.parametrize("name", list(HIDDEN_R2))
def test_r2_with_no_tag_the_reviewed_forms_change_nothing(gate, tmp_path, name):
    """Auto-mode rule only (the Supervisor's verdict on AC 1): no tag, no new block. The forms the
    plain patterns already read (`--attr-source` is now a known value option) are not in this check."""
    if name.startswith("s1-"):
        pytest.skip("`--attr-source <tree>` is now read by the plain patterns, as a push or merge")
    fx = gate(kanban(done=("T900",)))
    assert reason(HIDDEN_R2[name], fx.wt, None) is None
    assert reason(HIDDEN_R2[name], fx.wt, transcript(tmp_path, [human("thanks", AFTER)])) is None


def test_r2_attr_source_is_a_value_option_for_the_plain_patterns(gate):
    """With no tag a push with `--attr-source <tree>` is a push: the verb is `push`, not the tree."""
    fx = gate(kanban(in_progress=("T900",)))
    text = reason(f"git --attr-source HEAD push origin {B}", fx.wt, None)
    assert text is not None and "cannot push/merge" in text, text
    for option in ("--attr-source", "--super-prefix", "--git-dir", "--work-tree", "--namespace",
                   "--config-env", "-C", "-c"):
        assert option in merge_gate.GIT_OPTIONS_WITH_ARG and option in merge_gate.GIT_OPTION_ARGS


BENIGN_R2 = [
    "$PY -m pytest tests/test_*.py", '$PY -m pytest "$f"', "timeout $T $PY -m pytest $ARGS",
    "env $A $B pytest", 'for f in a b; do $TOOL "$f"; done', "cp $a pull", "cp $a push",
    "git --version", "git --help", "git -C . status", "git --no-pager -C . log -1",
    "git --attr-source HEAD status", "git status >/dev/null", "git status 2>&1 | head -3",
    "git log --oneline >/dev/null 2>&1", "git diff > /dev/null", "ls | xargs git status",
    "apt-get install git -y", "man git", "which git", "ln -s /usr/bin/git ~/bin/git",
    "git-lfs ls-files", "git-crypt status", "echo git-push", 'grep "git-push" notes.md',
    "git add a && git commit -m x", "git stash", "git tag v1",
    "if [ -f x ]; then echo hi; fi", "for i in 1 2; do echo $i; done", "{ echo a; echo b; }",
    '"$VENV/bin/pytest" -q', "${VENV}/bin/pytest -q", "FOO=1 pytest -q", "pytest -k 'a*' >/dev/null",
]


@pytest.mark.parametrize("command", BENIGN_R2)
def test_r2_unit_ordinary_commands_are_not_flagged(command):
    assert not merge_gate.hidden_git_verb(command), command


@pytest.mark.parametrize("command", ["git --version", "git status >/dev/null",
                                     "$PY -m pytest tests/test_*.py", "git -C . status"])
@pytest.mark.parametrize("tag", ["[admin]", "[auto]"])
def test_r2_ordinary_commands_stay_allowed_in_auto_mode(gate, tmp_path, command, tag):
    fx = gate(kanban(done=("T900",)))
    path = transcript(tmp_path, [human("go " + tag, AFTER)])
    assert reason(command, fx.main, path) is None, command


def test_r2_a_rebase_does_not_hide_the_rest_of_the_command_from_the_check(gate, tmp_path):
    """S2: the hidden-verb check ran only when no blocked pattern matched; `rebase` is blocked but
    not an auto-mode pattern, so a rebase earlier in the command skipped it."""
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    path = admin_session(tmp_path, fx)
    assert reason('git rebase --abort 2>/dev/null; git "push" origin main', fx.wt, path) is not None
    # nothing else changed: a plain rebase alone is not an auto-mode block
    assert reason("git rebase main", fx.wt, path) is None


def test_r2_x1_an_error_in_the_check_is_a_block_in_auto_mode_and_nothing_outside_it(gate, tmp_path,
                                                                                      monkeypatch):
    """An uncaught exception exits 1, which the harness reads as a non-blocking error."""
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)

    def boom(*_a, **_k):
        raise RuntimeError("boom")
    monkeypatch.setattr(merge_gate, "hidden_git_verb", boom)
    text = reason("echo hello", fx.wt, admin_session(tmp_path, fx))
    assert text is not None and "cannot push/merge" in text, text
    assert reason("echo hello", fx.wt, None) is None
    assert reason("echo hello", fx.wt, transcript(tmp_path, [human("thanks", AFTER)])) is None


# [admin]: a dashed or redirect-hidden git word never gets the plain verb's way through
@pytest.mark.parametrize("command", [
    f"{EXEC}/git-push origin {B}", f"git-push origin {B}", f"git >/dev/null push origin {B}",
    f"git push origin {B}; git >/dev/null push -f origin main",
    f"git push origin {B}; git-push -f origin main"])
def test_r2_admin_refuses_a_second_or_hidden_git_word(gate, tmp_path, command):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    assert reason(command, fx.wt, session(tmp_path, fx, "do it [admin]")) is not None


def test_r2_admin_verb_text_does_not_call_add_or_commit_read_only(gate, tmp_path):
    fx, path = _verified(gate, tmp_path)
    text = reason("git commit --no-gpg-sign -m x && " + PUSH + " origin " + B, fx.wt, path)
    assert text is not None and "read-only" not in text, text
    text = reason("git log --output=/tmp/o && " + PUSH + " origin " + B, fx.wt, path)
    assert text is not None and "read-only" in text, text


# ── real shells, no push: the premise (each shape reaches git with the verb `push`) ──────────
# Supervisor rule for this round: no agent runs a real `git push` or `git merge`, even into a throwaway
# remote. So `git` here is a stand-in script (first on PATH, or named by its path) that only records
# its own name and arguments; the shell, not the gate, decides what the stand-in is called with. The
# real-push witness for these shapes is a lab script the user runs (see the review file).
FAKE_GIT = """#!/bin/sh
printf '%s' "$(basename "$0")" >> "$CANARY_FILE"
for a in "$@"; do printf ' %s' "$a" >> "$CANARY_FILE"; done
printf '\\n' >> "$CANARY_FILE"
"""


def _have(shell):
    import shutil
    return shutil.which(shell) is not None


def _fake_bin(tmp_path):
    fake = tmp_path / "fakebin"
    fake.mkdir()
    for name in ("git", "git-push", "git-send-pack", "git-merge", "git-pull"):
        (fake / name).write_text(FAKE_GIT)
        (fake / name).chmod(0o755)
    return str(fake)


def _stand_in_shapes(fake):
    return {
        "c1-redirect": f"git >/dev/null push origin {B}",
        "c1-fd-and-env": f"FOO=1 git 2>/dev/null push origin {B}",
        "c1-after-C": f"git -C . >/dev/null push origin {B}",
        "s1-attr-source": f"git --attr-source HEAD push origin {B}",
        "s2-rebase-then-push": f'git rebase --abort 2>/dev/null; git "push" origin {B}',
        "s3-env-u": f'env -u git git "push" origin {B}',
        "s3-xargs": f'xargs -E git git "p""ush" origin {B}',
        "s4a-brace": f"{{git,push}} origin {B}",
        "s4c-eval": f'x=git; eval "$x push origin {B}"',
        "s4d-continuation": f"g\\\nit push origin {B}",
        "c2-env-S": f"env -S'git \"push\" origin {B}'",
        "c3-dashed-path": f"{fake}/git-push origin {B}",
        "c3-dashed-path-prefix": f"PATH={fake}:$PATH git-push origin {B}",
        "c3-send-pack": f"{fake}/git-send-pack ../origin.git {B}",
        "c5-xargs-stdin": f"echo push origin {B} | xargs git",
        "c6-redirect-head": f'>/dev/null {fake}/git "push" origin {B}',
        "c8-subtree-like": f"git subtree push --prefix=a origin {B}",
    }


SHAPES = list(_stand_in_shapes("/x"))


@pytest.mark.parametrize("shell", ["bash", "zsh"])
@pytest.mark.parametrize("shape", SHAPES)
def test_r2_premise_each_shape_reaches_git_with_the_verb_in_a_real_shell(tmp_path, shell, shape):
    """The control: in a real shell each shape calls git (a stand-in that only records its arguments)
    with the verb `push` (or the dashed command `git-push`). Without it the gate tests above could pass
    on shapes that are harmless. Nothing is pushed."""
    if not _have(shell):
        pytest.skip(f"{shell} is not installed")
    if shell == "zsh" and shape == "s4a-brace":
        pytest.skip("zsh reads `{git,push}` at the start of a command as a group, not a brace expansion")
    fake = _fake_bin(tmp_path)
    canary = tmp_path / "canary.txt"
    env = {**os.environ, "PATH": fake + os.pathsep + os.environ["PATH"], "CANARY_FILE": str(canary),
           "HOME": str(tmp_path)}
    subprocess.run([shell, "-c", _stand_in_shapes(fake)[shape]], cwd=tmp_path, env=env,
                   capture_output=True, text=True, stdin=subprocess.DEVNULL)
    text = canary.read_text() if canary.exists() else ""
    words = text.split()
    assert "push" in words or "git-push" in words or "git-send-pack" in words, (shape, shell, text)


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_r2_premise_an_alias_set_by_the_environment_runs(tmp_path, shell):
    """C4: `GIT_CONFIG_COUNT` and `GIT_CONFIG_PARAMETERS` define an alias for one command. The alias
    here is `!echo CANARY` (a shell alias that prints), so nothing is pushed."""
    if not _have(shell):
        pytest.skip(f"{shell} is not installed")
    env = {**os.environ, "HOME": str(tmp_path), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    for command in ("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.x GIT_CONFIG_VALUE_0='!echo CANARY' git x",
                    "GIT_CONFIG_PARAMETERS=\"'alias.x=!echo CANARY'\" git x"):
        done = subprocess.run([shell, "-c", command], cwd=tmp_path, env=env, capture_output=True, text=True)
        assert "CANARY" in done.stdout, (command, done.stdout, done.stderr)


def test_r2_premise_attr_source_takes_a_separate_value(tmp_path):
    """S1, on real git, with a read-only verb: `HEAD` is the option's value, `rev-parse` is the verb."""
    env = {**os.environ, "HOME": str(tmp_path), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", str(tmp_path / "r")], env=env, check=True)
    (tmp_path / "r" / "f").write_text("x\n")
    subprocess.run(["git", "-C", str(tmp_path / "r"), "add", "f"], env=env, check=True)
    subprocess.run(["git", "-C", str(tmp_path / "r"), "-c", "user.name=t", "-c", "user.email=t@e.invalid",
                    "commit", "-qm", "m"], env=env, check=True)
    done = subprocess.run(["git", "-C", str(tmp_path / "r"), "--attr-source", "HEAD", "rev-parse",
                           "--git-dir"], env=env, capture_output=True, text=True)
    assert done.returncode == 0 and done.stdout.strip() == ".git", done


# ── (11) the own-remote rule: ROOT / same common dir, and URLs compared after resolving ──────
def test_r2_a_clone_whose_origin_is_a_symlink_or_relative_path_to_the_same_bare_is_the_same_remote(
        gate, tmp_path):
    from test_gate_hidden_verbs import _clone_with_origin  # noqa: F401  (this module)
    fx, path = _verified(gate, tmp_path)
    clone = _clone_with_origin(fx)
    link = os.path.join(fx.root, "origin-link.git")
    os.symlink(os.path.join(fx.root, "origin.git"), link)
    git(clone, "remote", "set-url", "origin", link)
    assert reason("cd " + clone + " && " + PUSH + " origin " + B, fx.wt, path) is None
    git(clone, "remote", "set-url", "origin", os.path.join("..", "origin.git"))
    assert reason("cd " + clone + " && " + PUSH + " origin " + B, fx.wt, path) is None


def test_r2_the_own_remote_rule_accepts_the_project_root_and_a_same_common_dir(gate, tmp_path,
                                                                                monkeypatch):
    fx, path = _verified(gate, tmp_path)
    other = os.path.join(fx.root, "elsewhere.git")
    git(fx.root, "init", "-q", "--bare", other)
    clone = _clone_with_origin(fx, other)
    # the command starts somewhere unrelated; the clone's origin differs from that repo's: refused
    assert merge_gate._own_origin_refusal(clone, str(tmp_path)) is not None
    # ROOT is the project: a clone of the same repository (same common dir) is the project's own
    monkeypatch.setattr(merge_gate, "ROOT", fx.wt)
    assert merge_gate._own_origin_refusal(fx.wt, str(tmp_path)) is None  # same common dir as ROOT
    assert merge_gate._own_origin_refusal(clone, str(tmp_path)) is not None
    monkeypatch.setattr(merge_gate, "ROOT", clone)
    assert merge_gate._own_origin_refusal(clone, str(tmp_path)) is None  # `where` is ROOT itself


# ── (16) the corpus changes only what the rows name, derived from the data ──────────────────
def test_r2_corpus_overrides_name_only_keys_that_exist_in_the_corpus():
    assert all(list(args) in [list(a) for a, _ in OLD_MERGE_SOURCES] for args in CHANGED_MERGE_SOURCES)
    assert set(CHANGED_RUNNER) <= set(OLD_RUNNER)


def test_r2_limit_a_variable_set_outside_the_command_is_not_followed():
    """Documented limit (`docs/claude-md/tracks.md` Admin tag Known limits): `$g $v origin B` with both
    names set before the command is not flagged, because `$PY -m pytest "$f"` and `$TOOL "$f"` must
    stay allowed and the two look the same. The same command that sets the names is flagged."""
    assert not merge_gate.hidden_git_verb(f"$g $v origin {B}")
    assert merge_gate.hidden_git_verb(f"g=git; v=push; $g $v origin {B}")
