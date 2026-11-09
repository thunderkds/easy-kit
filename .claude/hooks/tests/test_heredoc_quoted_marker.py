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
    "after-ansi-c-escaped-quote": "echo $'\\'' > f <<EOF\n{push}\nEOF",
    # goes red when comment skipping is off: the `'` in the comment would leave a quote open
    "after-a-comment-with-a-quote": "echo ok # it's\ncat <<EOF\n{push}\nEOF",
    "in-substitution": "echo $(cat <<EOF\n{push}\nEOF\n)",
    "in-substitution-quoted-tag": "x=$(cat <<'EOF'\n{push}\nEOF\n); echo done",
    "in-backtick": "echo `cat <<EOF\n{push}\nEOF\n`",
    "in-substitution-in-double-quotes": 'echo "$(cat <<EOF\n{push}\nEOF\n)"',
    "commit-form": 'git commit -m "$(cat <<\'EOF\'\nT294: fix\n\n{push}\nEOF\n)"',
    "in-substitution-in-arithmetic": "echo $(( $(cat <<EOF\n{push}\nEOF\n) ))",
    "in-substitution-in-brace-default": "echo ${{x:-$(cat <<EOF\n{push}\nEOF\n)}}",
    "subshell-in-substitution": "echo $( (cat <<EOF\n{push}\nEOF\n) )",
    "quoted-tag-keeps-a-substitution-as-data": "cat <<'EOF'\n$(echo hi; {push})\nEOF",
    "nested-substitution": "echo $(echo $(cat <<EOF\n{push}\nEOF\n))",
    "substitution-after-quote-restart": 'echo "a $(cat <<EOF\n{push}\nEOF\n) b"',
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


@pytest.mark.parametrize("name", sorted(ALSO_HIDDEN))
def test_ac3_every_other_hidden_shape_is_stripped_by_the_old_function(name):
    """LR-0003: a test that the new scanner keeps the text can only go red if the old one stripped it."""
    command = shape(ALSO_HIDDEN[name], FORCE)
    assert old_strip(command) != command, name


def test_ac3_non_strings_and_heredoc_free_text_pass_through():
    assert strip_heredoc_bodies(None) is None
    assert strip_heredoc_bodies(7) == 7
    assert strip_heredoc_bodies("") == ""
    assert strip_heredoc_bodies(FORCE) == FORCE


# ── AC 4 — doubt keeps the text ──────────────────────────────────────────────────────────────────
DOUBT = {
    "unbalanced-double-quote": 'echo "oops <<EOF\n{push}\nEOF',
    "unbalanced-single-quote": "echo 'oops <<EOF\n{push}\nEOF",
    "heredoc-closed-on-its-header-line": "echo $(cat <<EOF)\n{push}\nEOF",
    "body-closes-the-context-early": "echo $(cat <<EOF\na ) b\n  EOF\n<<EOF\na ) b\nEOF)\n{push}\nEOF",
    "backtick-body-in-brace-default": "echo ${{x:-$(cat <<-EOF\n`\n{push}\n`\nEOF\n)}}\nEOF\n{push}",
    "header-line-opens-a-paren": "cat <<'EOF'(\n\n&&\\\n{push}\nEOF\n",
    "body-runs-past-the-context": "echo $(cat <<EOF\n)\n{push}\nEOF",
    "unquoted-tag-runs-a-substitution": "cat <<EOF\n$(echo hi; {push})\nEOF",
    "unquoted-tag-runs-a-backtick": "cat <<EOF\n`{push}`\nEOF",
    "unquoted-tag-runs-a-substitution-in-a-substitution": "echo $(cat <<EOF\n$({push})\nEOF\n)",
    "backtick-in-the-body-ends-the-backtick": "echo `cat <<'EOF'\n`{push}`\nEOF\n`",
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


# ── The kit's commit form: a heredoc inside `$(…)` is a real heredoc ─────────────────────────────
COMMIT_BODY = "T294: note\n\n" + FORCE
COMMIT_FORM = 'git commit -m "$(cat <<\'EOF\'\n' + COMMIT_BODY + '\nEOF\n)"'
COMMIT_PLAIN = 'git commit -m "' + COMMIT_BODY + '"'  # the same body outside any heredoc
# A quoted `<<` inside `$(…)` or a backtick: the shell does not read a heredoc, the lines after it run.
SUB_HIDDEN = {
    "dq-in-substitution": 'echo $(echo "<<EOF")\n{push}\nEOF',
    "sq-in-substitution": "echo $(echo '<<EOF')\n{push}\nEOF",
    "dq-in-backtick": 'echo `echo "<<EOF"`\n{push}\nEOF',
    "comment-in-substitution": "echo $(true # <<EOF\n)\n{push}\nEOF",
    "backslash-in-substitution": "echo $(echo \\<<EOF)\n{push}\nEOF",
    "quote-in-double-quoted-substitution": 'echo "$(echo \'<<EOF\')"\n{push}\nEOF',
    "arithmetic-in-substitution": "echo $(( 1<<n ))\n{push}\nn",
    "here-string-in-substitution": "echo $(cat <<<EOF)\n{push}\nEOF",
}


def test_commit_form_body_is_stripped_and_a_push_after_it_is_still_seen():
    stripped = strip_heredoc_bodies(COMMIT_FORM)
    assert "push" not in stripped and stripped.startswith('git commit -m "$(cat <<\'EOF\'')
    after = strip_heredoc_bodies(COMMIT_FORM + "\n" + FORCE)
    assert after.endswith(FORCE)


def test_commit_form_with_a_push_in_its_body_is_allowed_in_no_tag_mode(gate, tmp_path):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    assert reason(COMMIT_FORM, fx.main, path) is None


def test_commit_form_with_a_push_in_its_body_is_allowed_in_auto_mode(gate, tmp_path):
    fx = gate(kanban(done=("T900",)))
    assert reason(COMMIT_FORM, fx.main, transcript(tmp_path, [human("go [auto]", -60)])) is None


def test_commit_form_with_a_push_in_its_body_is_allowed_in_admin_mode(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    assert reason(COMMIT_FORM, fx.wt, session(tmp_path, fx, "do it [admin]")) is None


def test_commit_form_control_the_same_body_outside_a_heredoc_is_blocked(gate, tmp_path):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    assert reason(COMMIT_PLAIN, fx.main, path) is not None


def test_commit_form_followed_by_a_real_push_is_blocked(gate, tmp_path):
    fx = gate(kanban(in_progress=("T900",)))
    path = transcript(tmp_path, [human("thanks", -60)])
    assert reason(COMMIT_FORM + " && " + FORCE, fx.main, path) is not None


@pytest.mark.parametrize("name", sorted(SUB_HIDDEN))
def test_a_quoted_marker_inside_a_substitution_keeps_the_text(name):
    command = shape(SUB_HIDDEN[name], FORCE)
    assert strip_heredoc_bodies(command) == command, name


@pytest.mark.parametrize("name", ["dq-in-substitution", "sq-in-substitution", "dq-in-backtick",
                                  "quote-in-double-quoted-substitution"])
@pytest.mark.parametrize("mode", ["none", "auto", "admin"])
def test_a_quoted_marker_inside_a_substitution_is_blocked_by_the_gate(gate, tmp_path, name, mode):
    command = shape(SUB_HIDDEN[name], FORCE)
    if mode == "admin":
        fx = gate(kanban(ready=("T900",)))
        auto_verified(fx)
        text = reason(command, fx.wt, session(tmp_path, fx, "do it [admin]"))
    elif mode == "auto":
        fx = gate(kanban(done=("T900",)))
        text = reason(command, fx.main, transcript(tmp_path, [human("go [auto]", -60)]))
    else:
        fx = gate(kanban(in_progress=("T900",)))
        text = reason(command, fx.main, transcript(tmp_path, [human("thanks", -60)]))
    assert text is not None, f"{mode}, {name}: the gate ALLOWED the hidden force push"


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
@pytest.mark.parametrize("name", ["plain", "single-quoted-tag", "dash-tab-end", "after-ansi-c-escaped-quote",
                                  "in-substitution", "in-backtick", "commit-form",
                                  "in-substitution-in-double-quotes", "nested-substitution"])
def test_premise_the_shell_does_not_run_the_body_of_a_real_heredoc(tmp_path, shell, name):
    command = shape(REAL[name])
    assert not pushed_by(shell, command, tmp_path), f"{shell} ran the body of {name}"
    assert PUSH not in strip_heredoc_bodies(command)


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
@pytest.mark.parametrize("name", ["dq-in-substitution", "sq-in-substitution", "dq-in-backtick",
                                  "comment-in-substitution", "backslash-in-substitution"])
def test_premise_the_shell_runs_the_push_after_a_quoted_marker_in_a_substitution(tmp_path, shell, name):
    command = shape(SUB_HIDDEN[name])
    assert pushed_by(shell, command, tmp_path), f"{shell} did not run the push of {name}"
    assert PUSH in strip_heredoc_bodies(command)


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
@pytest.mark.parametrize("name", ["unquoted-tag-runs-a-substitution", "unquoted-tag-runs-a-backtick",
                                  "unquoted-tag-runs-a-substitution-in-a-substitution"])
def test_premise_the_shell_runs_what_an_unquoted_heredoc_body_holds(
        tmp_path, shell, name):
    """`cat <<EOF` expands `$(…)` and backticks in its body, so the push inside RUNS: that body is
    command text, not data. The scanner must keep it (found by the fuzz; true before T294 too)."""
    command = shape(DOUBT[name])
    assert pushed_by(shell, command, tmp_path), f"{shell} did not run the push of {name}"
    assert PUSH in strip_heredoc_bodies(command), f"{name}: the scanner hid a push {shell} runs"


CANARY = 'echo CAN""ARY'  # prints `CANARY`; the command text never holds that word


def canary_ran(shell, command, tmp_path):
    """True when `shell -c command`, run in an empty throwaway dir with no stdin, printed the canary."""
    done = subprocess.run([shell, "-c", command], cwd=str(tmp_path), env=ENV, capture_output=True,
                          text=True, timeout=10, stdin=subprocess.DEVNULL)
    return "CANARY" in done.stdout


# ── Fix round (Stage 4): shapes the first scanner still hid ──────────────────────────────────────
# Each runs `{push}` in a real shell and, before the fix round, lost it to the strip. The value says
# which shells run it (checked on bash 5.3.9 and zsh 5.9); a shell not listed may abort first.
BYPASS = {
    # R0: a heredoc inside `<(…)` / `>(…)`: its body holds a `)` and a `<<B` line, then the real `)`.
    "r0-process-substitution": ("true <(cat <<A\n)\ncat <<B\nA\n)\n{push}\nB", ("bash", "zsh")),
    "r0-output-process-substitution": ("true >(cat <<A\n)\ncat <<B\nA\n)\n{push}\nB", ("bash", "zsh")),
    # P0-1: the shell reads the whole word, quotes removed, as the tag.
    "tag-quoted-in-the-middle": ('cat <<E"O"F\nx\nEOF\n{push}\nE', ("bash", "zsh")),
    "tag-backslash-in-the-middle": ("cat <<E\\OF\nx\nEOF\n{push}\nE", ("bash", "zsh")),
    "tag-single-quoted-in-the-middle": ("cat <<E'O'F\nx\nEOF\n{push}\nE", ("bash", "zsh")),
    "tag-with-a-quoted-suffix": ('cat <<EOF"x"\nEOFx\n{push}\nEOF', ("bash", "zsh")),
    "tag-quoted-then-a-suffix": ('cat <<"EOF"x\nEOFx\n{push}\nEOF', ("bash", "zsh")),
    "tag-that-is-not-a-word": ("cat <<1\ncat <<B\n1\n{push}\nB", ("bash", "zsh")),
    # P0-2: the heredoc inside `$(…)` ends at a line that starts with the tag and closes the `$(`.
    "context-closes-on-the-tag-line": ("echo $(cat <<EOF\nx\nEOF) ; {push} ; (cat <<EOF\nx\nEOF\n)", ("bash",)),
    "context-closes-on-the-tag-line-with-a-word": (
        "echo $(cat <<EOF\nx\nEOF x) ; {push} ; (cat <<EOF\nx\nEOF\n)", ("bash",)),
    "context-closes-on-a-case-line": (
        "echo $(cat <<EOF\nx\nEOF2case x in x) ; {push} ; (cat <<EOF\nx\nEOF\n)", ("bash",)),
    "context-closes-on-a-tag-with-a-suffix": (
        "echo $(cat <<EOF\nx\nEOFx) ; {push} ; (cat <<EOF\nx\nEOF\n)", ("bash",)),
    # P0-3: `$[…]` and a subscript are arithmetic, so `<<` is a shift.
    "dollar-bracket-arithmetic": ("echo $[1<<n]\n{push}\nn", ("bash", "zsh")),
    "array-subscript-arithmetic": ("a[1<<n]=3\n{push}\nn", ("bash",)),
    # the same with a space after the tag, so that the tag check alone does not catch them
    "dollar-bracket-arithmetic-spaced": ("echo $[ 1<<n ]\n{push}\nn", ("bash", "zsh")),
    "array-subscript-arithmetic-spaced": ("a[ 1<<n ]=3\n{push}\nn", ("bash",)),
    # P0-4: an array literal is not a subshell: its `<<EOF` line is a syntax error in bash.
    "array-literal": ("x=(cat <<EOF\n{push}\nEOF\n)", ("bash",)),
    "array-literal-append": ("x+=(cat <<EOF\n{push}\nEOF\n)", ("bash",)),
}


@pytest.mark.parametrize("name", sorted(BYPASS))
def test_fix_round_the_scanner_keeps_the_push(name):
    command = shape(BYPASS[name][0], FORCE)
    assert FORCE in strip_heredoc_bodies(command), f"{name}: the scanner hid a push"


@pytest.mark.parametrize("name", sorted(BYPASS))
@pytest.mark.parametrize("mode", ["none", "auto", "admin"])
def test_fix_round_the_gate_blocks_the_force_push(gate, tmp_path, name, mode):
    command = shape(BYPASS[name][0], FORCE)
    if mode == "admin":
        fx = gate(kanban(ready=("T900",)))
        auto_verified(fx)
        text = reason(command, fx.wt, session(tmp_path, fx, "do it [admin]"))
    elif mode == "auto":
        fx = gate(kanban(done=("T900",)))
        text = reason(command, fx.main, transcript(tmp_path, [human("go [auto]", -60)]))
    else:
        fx = gate(kanban(in_progress=("T900",)))
        text = reason(command, fx.main, transcript(tmp_path, [human("thanks", -60)]))
    assert text is not None, f"{mode}, {name}: the gate ALLOWED the hidden force push"


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
@pytest.mark.parametrize("name", sorted(BYPASS))
def test_fix_round_premise_the_shell_runs_the_push_and_the_scanner_keeps_it(tmp_path, shell, name):
    """The push is an `echo` canary in a throwaway dir (never a real push): `echo CAN""ARY` prints
    `CANARY`, and the text of the command never holds that word."""
    template, runs_in = BYPASS[name]
    command = template.format(push=CANARY)
    ran = canary_ran(shell, command, tmp_path)
    if shell in runs_in:
        assert ran, f"{shell} did not run the canary of {name}"
    if ran:
        assert CANARY in strip_heredoc_bodies(command), f"{name}: the scanner hid a line {shell} runs"
