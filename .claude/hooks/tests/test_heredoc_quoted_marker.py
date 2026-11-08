#!/usr/bin/env python3
"""T294 — a `<<WORD` the shell does not read as a heredoc no longer hides the lines after it from the
merge gate (`tasks/TASK_GUIDE_T294.md`, AC 1-5; finding P1-1 of `tasks/GATE_HUNT_2026-11-08.md`).

  * AC 1: the four hidden shapes (`echo "<<EOF"`, `echo '<<EOF'`, `true # <<EOF`, `echo \\<<EOF`),
    each followed by a force push and an `EOF` line, are BLOCKED in no-tag, `[auto]` and `[admin]` mode.
  * AC 2: a real heredoc keeps its behaviour: the body is data and is stripped.
  * AC 3: every command that earlier suites send through `strip_heredoc_bodies` keeps its result
    (a frozen copy of the old function is the oracle), except the hidden shapes.
  * AC 4: a `<<` whose quote state the scanner cannot settle keeps the text.
  * Premise: a real bash (and zsh, when installed) runs the hidden shapes' push and does not run a
    real heredoc's body, so the scanner is compared with the shell, not with an opinion.

Every board, guide, transcript and git repo here is constructed (throwaway dirs under pytest's tmp_path).
Spelled in halves (`G + "push"`) so this file's own text never reads as a command to the live gate.
Run with: python3 -m pytest .claude/hooks/tests/test_heredoc_quoted_marker.py -v
"""
import os
import re
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import G, PUSH, gate, git, kanban  # noqa: E402
from test_admin_tag import auto_verified, human, reason, session, transcript  # noqa: E402

from shell_data import strip_heredoc_bodies  # noqa: E402  (on sys.path: the hook put its lib/ there)

assert gate  # the fixture, imported for pytest

FORCE = PUSH + " --force origin main"

# The four shapes of the finding. `{push}` is the line the shell runs as a command.
HIDDEN = {
    "double-quoted": 'echo "<<EOF"\n{push}\nEOF',
    "single-quoted": "echo '<<EOF'\n{push}\nEOF",
    "after-comment": "true # <<EOF\n{push}\nEOF",
    "after-backslash": "echo \\<<EOF\n{push}\nEOF",
}
# Shapes beyond the four that the same scanner must keep (found while writing it).
ALSO_HIDDEN = {
    "here-string": "cat <<<EOF\n{push}\nEOF",
    "ansi-c-quote": "echo $'<<EOF'\n{push}\nEOF",
    "brace-default": "echo ${{x:-<<EOF}}\n{push}\nEOF",
    "quote-after-escaped-quote": 'echo "a\\"" "<<EOF"\n{push}\nEOF',
    "comment-after-space-then-quote": "echo ok # it's\n{push}\n# <<EOF\nEOF",
}
ALL_HIDDEN = {**HIDDEN, **ALSO_HIDDEN}

# Real heredocs: the body is data and is stripped (AC 2).
REAL = {
    "plain": "cat <<EOF\n{push}\nEOF",
    "dash-tab-end": "cat <<-EOF\n{push}\n\tEOF",
    "single-quoted-tag": "cat <<'EOF'\n{push}\nEOF",
    "double-quoted-tag": 'cat <<"EOF"\n{push}\nEOF',
    "space-before-tag": "cat << EOF\n{push}\nEOF",
    "after-closed-quotes": 'echo "a b" \'c d\' > f <<EOF\n{push}\nEOF',
    "after-closed-substitution": "echo $(pwd) > f <<EOF\n{push}\nEOF",
    "after-escaped-quote": "echo \\\" > f <<EOF\n{push}\nEOF",
    "comment-on-previous-line": "# note <<X\ncat <<EOF\n{push}\nEOF",
    "hash-inside-word": "echo a#b <<EOF\n{push}\nEOF",
    "subshell": "(cat <<EOF\n{push}\nEOF\n)",
}


def shape(template, push=PUSH + " origin main"):
    return template.format(push=push)


# ── AC 1 — the gate blocks the lines after a marker the shell does not read as a heredoc ────────
@pytest.mark.parametrize("name", sorted(ALL_HIDDEN))
def test_ac1_no_tag_mode_blocks_the_force_push_after_a_hidden_marker(gate, tmp_path, name):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    text = reason(shape(ALL_HIDDEN[name], FORCE), fx.main, path)
    assert text is not None, f"no tag, {name}: the gate ALLOWED the hidden force push"
    assert "Tasks still In Progress: T900" in text


@pytest.mark.parametrize("name", sorted(ALL_HIDDEN))
def test_ac1_auto_mode_blocks_the_force_push_after_a_hidden_marker(gate, tmp_path, name):
    fx = gate(kanban(done=("T900",)))
    path = transcript(tmp_path, [human("go [auto]", -60)])
    text = reason(shape(ALL_HIDDEN[name], FORCE), fx.main, path)
    assert text is not None, f"[auto], {name}: the gate ALLOWED the hidden force push"
    assert "Auto-mode gate" in text


@pytest.mark.parametrize("name", sorted(ALL_HIDDEN))
def test_ac1_admin_mode_blocks_the_force_push_after_a_hidden_marker(gate, tmp_path, name):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    path = session(tmp_path, fx, "do it [admin]")
    text = reason(shape(ALL_HIDDEN[name], FORCE), fx.wt, path)
    assert text is not None, f"[admin], {name}: the gate ALLOWED the hidden force push"


def test_ac1_control_the_same_push_without_a_marker_is_blocked_in_no_tag_mode(gate, tmp_path):
    """Control: the shape is blocked because of the push line; the marker only hid it."""
    fx = gate(kanban(in_progress=("T900",)))
    assert reason(FORCE, fx.main, transcript(tmp_path, [human("thanks", -60)])) is not None


def test_ac1_control_the_same_push_without_a_marker_is_blocked_in_auto_mode(gate, tmp_path):
    fx = gate(kanban(done=("T900",)))
    assert reason(FORCE, fx.main, transcript(tmp_path, [human("go [auto]", -60)])) is not None


def test_ac1_control_the_same_push_without_a_marker_is_blocked_in_admin_mode(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    assert reason(FORCE, fx.wt, session(tmp_path, fx, "do it [admin]")) is not None


# ── AC 2 — a real heredoc is still data ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("name", sorted(REAL))
def test_ac2_a_real_heredoc_body_is_stripped(name):
    command = shape(REAL[name], FORCE)
    stripped = strip_heredoc_bodies(command)
    assert "push" not in stripped, f"{name}: the body of a real heredoc must be data\n{stripped!r}"


@pytest.mark.parametrize("name", sorted(REAL))
def test_ac2_the_gate_allows_a_real_heredoc_that_only_mentions_a_push(gate, tmp_path, name):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    assert reason(shape(REAL[name], FORCE), fx.main, path) is None, name


@pytest.mark.parametrize("tag", ["[auto]", "[admin]"])
def test_ac2_auto_and_admin_mode_allow_a_real_heredoc_that_only_mentions_a_push(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    path = session(tmp_path, fx, "do it " + tag)
    assert reason(shape(REAL["plain"], FORCE), fx.wt, path) is None


def test_ac2_a_push_after_the_terminator_of_a_real_heredoc_is_still_seen():
    stripped = strip_heredoc_bodies("cat <<EOF\nbody\nEOF\n" + FORCE)
    assert FORCE in stripped and "body" not in stripped


# ── AC 3 — the corpus: the old function is the oracle ────────────────────────────────────────────
OLD_HEADER = re.compile(
    r"<<(?!<)(?P<dash>-?)\s*(?P<quote>['\"]?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)(?P=quote)")


def old_strip(command):
    """The function as it was before T294, frozen here as the oracle for the corpus."""
    if not isinstance(command, str) or "<<" not in command:
        return command
    pieces, pos = [], 0
    while True:
        header = OLD_HEADER.search(command, pos)
        if not header:
            break
        body_start = command.find("\n", header.end())
        if body_start == -1:
            break
        lead = "[\t]*" if header.group("dash") else ""
        terminator = re.compile(rf"^{lead}{re.escape(header.group('tag'))}[ \t]*$",
                                re.MULTILINE).search(command, body_start + 1)
        if not terminator:
            break
        pieces.append(command[pos:body_start + 1])
        pieces.append(" ")
        pos = terminator.end()
    if not pieces:
        return command
    pieces.append(command[pos:])
    return "".join(pieces)


# Commands that earlier suites pass through `strip_heredoc_bodies` (test_merge_gate_t095,
# test_merge_gate_push_scope, test_merge_gate_t211, test_merge_gate_companion_rows,
# test_quoted_spans_t099, test_memory_hook_heredoc_data, test_pre_tool_sensitive_path,
# test_t250_session_ownership, test_token_meter, test_admin_tag), plus the shapes of Edge Case Checklist.
CORPUS = [
    "cat <<'E'\nbody\nE\npush",
    "cat > f <<-EOF\n" + G + "push\n\tEOF\ntrue",
    "cat > f <<EOF\nprose\n\tEOF\nmore prose\nEOF\ntrue",
    "cat > a <<'E1'\n" + G + "push\nE1\ncat > b <<'E2'\n" + G + "merge\nE2\ntrue",
    "grep x <<< 'data'\n" + G + "push",
    "cat > notes.md <<'EOF'\n" + G + "push origin main\n",
    "cat > notes.md <<'EOF'\n" + PUSH + " origin feat/t900-x\nEOF\n" + PUSH + " origin main",
    "cat > notes.md <<'EOF'\n" + PUSH + " origin feat/t900-x\nEOF\n",
    "cat > notes.md <<EOF\nThe Supervisor will " + G + "merge this branch.\nEOF\n",
    "cat > notes.md <<EOF\nRun " + G + "pull before starting.\nEOF\n",
    PUSH + " && cat > notes.md <<'EOF'\nplain prose\nEOF\n",
    PUSH + " origin fix/t900 && cat > n <<EOF\nx\nEOF",
    "cat > notes.md <<'EOF'\n" + G + "-C x push\n" + G + "-c alias.p=push p\nEOF",
    "cat > f <<'EOF'\nbody\nEOF\n" + G + "-C x push",
    'echo "writing notes" > n.md <<\'EOF\'\nhello\nEOF\n' + PUSH + " origin main",
    "cat <<EOF > notes.md\nremember .env\nEOF",
    "cat > tasks/TASK_REVIEW_T900.md <<'EOF'\nhello\nEOF",
    "python3 - <<'EOF'\np='tasks/TASK_REVIEW_T901.md'\n# quotes tasks/TASK_REVIEW_T900.md\nEOF",
    "cat > x.py <<'EOF'\nprint(1)\nEOF",
    "cat <<EOF\npython3 -m pytest -q\nEOF",
    "cd /w && cat <<EOF\npython3 -m pytest -q\nEOF",
    "cat <<A <<B\na\nA\nb\nB",                       # two headers on one line: only the first is read
    "cat <<A; cat <<B\na\nA\nb\nB",
    "cat <<A\na\nA\ncat <<B\nb\nB",                   # sequential
    "echo hi",
    "cat <<EOF",                                      # header with no body
    "cat <<EOF\nnever ended",                         # unterminated
    "git commit -m 'one' && cat <<EOF\nx\nEOF",
    "echo a # trailing note\ncat <<EOF\nx\nEOF",
]


@pytest.mark.parametrize("command", CORPUS, ids=lambda c: repr(c)[:50])
def test_ac3_the_corpus_keeps_its_old_result(command):
    assert strip_heredoc_bodies(command) == old_strip(command)


@pytest.mark.parametrize("name", sorted(HIDDEN))
def test_ac3_the_corpus_differs_only_on_the_hidden_shapes(name):
    command = shape(HIDDEN[name], FORCE)
    assert old_strip(command) != command, "the oracle must show the old bug"
    assert strip_heredoc_bodies(command) == command


def test_ac3_non_strings_and_heredoc_free_text_pass_through():
    assert strip_heredoc_bodies(None) is None
    assert strip_heredoc_bodies(7) == 7
    assert strip_heredoc_bodies("") == ""
    assert strip_heredoc_bodies(FORCE) == FORCE


# ── AC 4 — doubt keeps the text ──────────────────────────────────────────────────────────────────
DOUBT = {
    "unbalanced-double-quote": 'echo "oops <<EOF\n{push}\nEOF',
    "unbalanced-single-quote": "echo 'oops <<EOF\n{push}\nEOF",
    "open-command-substitution": "echo $(cat <<EOF\n{push}\nEOF\n)",
    "open-backtick": "echo `cat <<EOF\n{push}\nEOF\n`",
    "arithmetic-shift": "echo $((1<<n))\n{push}\nn",
    "arithmetic-command": "(( x = 1<<n ))\n{push}\nn",
    "process-substitution": "diff <(cat <<EOF\n{push}\nEOF\n) f",
    "quote-opens-inside-substitution": 'echo $(echo "<<EOF"\n{push}\nEOF',
}


@pytest.mark.parametrize("name", sorted(DOUBT))
def test_ac4_a_marker_the_scanner_cannot_settle_keeps_the_text(name):
    command = shape(DOUBT[name], FORCE)
    assert strip_heredoc_bodies(command) == command, name


def test_ac4_a_real_heredoc_before_an_unbalanced_quote_is_still_stripped():
    command = "cat <<EOF\nbody\nEOF\necho 'oops"
    assert "body" not in strip_heredoc_bodies(command)
    assert strip_heredoc_bodies(command).endswith("echo 'oops")


def test_ac4_the_gate_blocks_the_force_push_after_an_unbalanced_quote(gate, tmp_path):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    assert reason(shape(DOUBT["unbalanced-double-quote"], FORCE), fx.main, path) is not None


def test_ac4_a_header_line_that_leaves_a_quote_open_keeps_the_text():
    """A quote that never closes puts the body start where the scanner cannot place it."""
    command = 'cat <<EOF "a\n' + FORCE + "\nEOF"
    assert strip_heredoc_bodies(command) == command


def test_ac4_a_header_line_that_leaves_a_substitution_open_keeps_the_text():
    """The newline is inside `$(`: the scanner cannot say where the body starts."""
    command = "cat <<EOF $(echo\nx)\n" + FORCE + "\nEOF"
    assert strip_heredoc_bodies(command) == command


def test_ac4_a_quote_that_spans_the_header_line_closes_and_the_body_follows_it():
    """Checked against bash and zsh: the body of `cat <<EOF "a<newline>b"` starts after `b"`."""
    command = 'cat <<EOF "a\nb"\nbody\nEOF\ntrue'
    assert "body" not in strip_heredoc_bodies(command)


# ── Edge cases from the checklist ────────────────────────────────────────────────────────────────
def test_edge_several_headers_on_one_line_keep_the_old_result():
    command = "cat <<A <<B\na\nA\nb\nB\n" + FORCE
    assert strip_heredoc_bodies(command) == old_strip(command)
    assert FORCE in strip_heredoc_bodies(command)


def test_edge_a_heredoc_marker_after_a_closed_quote_pair_is_real():
    command = 'echo "x" \'y\' <<EOF\n' + FORCE + "\nEOF"
    assert "push" not in strip_heredoc_bodies(command)


def test_edge_a_hash_inside_a_word_is_not_a_comment():
    command = "echo a#b <<EOF\n" + FORCE + "\nEOF"
    assert "push" not in strip_heredoc_bodies(command)


def test_edge_an_escaped_backslash_does_not_hide_the_marker():
    command = "echo \\\\<<EOF\n" + FORCE + "\nEOF"  # `\\` is a literal backslash, `<<EOF` is real
    assert "push" not in strip_heredoc_bodies(command)


def test_edge_a_comment_ends_at_the_newline():
    command = "true # <<EOF\ncat <<EOF\nbody\nEOF\n" + FORCE
    stripped = strip_heredoc_bodies(command)
    assert "body" not in stripped and FORCE in stripped


def test_edge_a_quoted_marker_does_not_swallow_a_later_real_heredoc():
    command = 'echo "<<A"\ncat <<B\nbody\nB\n' + FORCE
    stripped = strip_heredoc_bodies(command)
    assert "body" not in stripped and FORCE in stripped


# ── The shell is the ground truth ────────────────────────────────────────────────────────────────
SHELLS = [s for s in ("bash", "zsh") if shutil.which(s)]
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_TERMINAL_PROMPT": "0"}


def pushed_by(shell, command, tmp_path):
    """Run `command` in `shell` inside a throwaway clone of a throwaway bare remote; True when the
    remote's `main` moved (the shell ran the push)."""
    remote, clone = tmp_path / "origin.git", tmp_path / "clone"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    git(tmp_path, "clone", "-q", str(remote), str(clone))
    git(clone, "checkout", "-q", "-B", "main")
    (clone / "f.txt").write_text("one\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "one")
    git(clone, "push", "-q", "origin", "main")
    before = git(remote, "rev-parse", "main")
    (clone / "f.txt").write_text("two\n")
    git(clone, "commit", "-qam", "two")
    subprocess.run([shell, "-c", command], cwd=str(clone), env=ENV, capture_output=True,
                   text=True, timeout=60)
    return git(remote, "rev-parse", "main") != before


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
@pytest.mark.parametrize("name", sorted(ALL_HIDDEN))
def test_premise_the_shell_runs_the_push_after_a_hidden_marker(tmp_path, shell, name):
    command = shape(ALL_HIDDEN[name])
    assert pushed_by(shell, command, tmp_path), f"{shell} did not run the push of {name}"
    assert PUSH in strip_heredoc_bodies(command), f"{name}: the scanner hid a push {shell} runs"


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
@pytest.mark.parametrize("name", ["plain", "single-quoted-tag", "dash-tab-end"])
def test_premise_the_shell_does_not_run_the_body_of_a_real_heredoc(tmp_path, shell, name):
    command = shape(REAL[name])
    assert not pushed_by(shell, command, tmp_path), f"{shell} ran the body of {name}"
    assert PUSH not in strip_heredoc_bodies(command)
