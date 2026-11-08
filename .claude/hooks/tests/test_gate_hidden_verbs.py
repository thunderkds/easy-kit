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
    f"$g -C /x push origin {B}", f"$g $v origin {B}", f"timeout 20 $g push origin {B}",
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
    assert merge_gate._hidden_in_command(["ls"], merge_gate.HIDDEN_DEPTH_LIMIT + 1)  # nested too deep: doubt


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
