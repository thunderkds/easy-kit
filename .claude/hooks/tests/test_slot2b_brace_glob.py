#!/usr/bin/env python3
"""T296 — slot 2b (`task_context._leading_cd_dir`) no longer files a call whose brace or glob can
reach outside the worktree (`tasks/TASK_GUIDE_T296.md` rows 4, 5 and 6; findings P2-3, P3-1, P3-2
of `tasks/GATE_HUNT_2026-11-08.md`).

  * Row 4 — a `{`, a `}` or an unquoted `*`, `?`, `[` in the command: the call is not filed under
    the worktree's task. Quoted globs and the normal `cd <dir> && pytest tests/test_x.py` stay.
  * Row 5 — a backslash is read the way the shell reads it: `\\` + newline continues the line,
    `\\;` and `\\*` are literal. A mention of the runner after a backslash is no test run, in slot 2b
    or in the trace gate.
  * Row 6 — a call that renames or switches the worktree's branch is not filed by the branch it ends
    on (the hook runs after the command).

Each call goes through the real `post_tool_trace.py`, as in `test_stop_attribution_t287.py`.
Run with: python3 -m pytest .claude/hooks/tests/test_slot2b_brace_glob.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_stop_attribution_t287 import (  # noqa: E402
    Session, _git, gate_sees_test_run, t120_project, trace)

WT = "cd @WT@ && "


def _expand(command, tmp_path, project):
    return command.replace("@WT@", str(tmp_path / "wt-t120")).replace("@MAIN@", str(project))


def _file(tmp_path, command, setup=None):
    """Send `command` as a Bash call (the session pointer names T250); return (project, tasks that got it)."""
    project = t120_project(tmp_path)
    (tmp_path / "wt-t120" / "tests").mkdir(exist_ok=True)
    os.symlink(project, tmp_path / "wt-t120" / "mtests")  # `mt*` expands to a link that points to main
    if setup:
        setup(tmp_path, project)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(command, tmp_path, project)})
    return project, {t: len(trace(project, t)) for t in ("T120", "T250")}


# ── Row 4 — brace expansion and globs ────────────────────────────────────────────────────────
NOT_FILED = {
    "brace-redirect-dotdot": WT + "echo hi > {.,..}/f",
    "brace-redirect-abs": WT + "echo hi > {/tmp/out,x}",
    "brace-option-value": WT + "git diff --output={.,..}/d",
    "brace-log-output": WT + "git log -1 --output={.,..}/d",
    "brace-pytest-path": WT + "python3 -m pytest {..,.}/main/tests",
    "brace-sequence": WT + "echo {1..3}",
    "brace-closing-only": WT + "echo a}",
    "glob-symlink-to-main": WT + "python3 -m pytest -q mt*",
    "glob-question": WT + "python3 -m pytest -q mtest?",
    "glob-bracket": WT + "python3 -m pytest -q mtest[s]",
    "glob-ls": WT + "ls *.py",
    "glob-after-a-quote": WT + "echo 'a' *",
}


@pytest.mark.parametrize("name", list(NOT_FILED))
def test_row4_a_call_with_a_brace_or_unquoted_glob_is_not_filed_under_the_task(tmp_path, name):
    project, got = _file(tmp_path, NOT_FILED[name])
    assert got == {"T120": 0, "T250": 1}, (name, got)
    assert not gate_sees_test_run(project, tmp_path, "T120")


FILED = {
    "quoted-glob-in-k": WT + 'python3 -m pytest -q -k "a*"',
    "single-quoted-glob": WT + "grep 'a*' setup.sh",
    "quoted-question": WT + 'grep "a?" setup.sh',
    "escaped-star": WT + "echo \\*",
    "escaped-bracket": WT + "echo \\[x",
    "plain-test-path": WT + "python3 -m pytest tests/test_x.py",
    "plain-run": WT + "python3 -m pytest -q",
    "git-reading": WT + "git log -1 && ls && python3 -m pytest -q",
}


@pytest.mark.parametrize("name", list(FILED))
def test_row4_quoted_and_escaped_globs_and_plain_runs_stay_filed(tmp_path, name):
    _, got = _file(tmp_path, FILED[name])
    assert got == {"T120": 1, "T250": 0}, (name, got)


# ── Row 5 — a backslash is read the way the shell reads it ───────────────────────────────────
BACKSLASH_MENTIONS = {
    "line-continuation": WT + "echo ok \\\npython3 -m pytest -q",
    "escaped-semicolon": WT + "echo done\\; python3 -m pytest -q",
    "escaped-quote-in-a-string": WT + 'echo "a\\" && python3 -m pytest -q && echo \\"b"',
}


@pytest.mark.parametrize("name", list(BACKSLASH_MENTIONS))
def test_row5_a_mention_after_a_backslash_is_no_test_run(tmp_path, name):
    project, got = _file(tmp_path, BACKSLASH_MENTIONS[name])
    # `echo` takes everything as its arguments: slot 2b files it like any honest echo, and the
    # trace gate counts no test run for T120 or for the pointer's task.
    assert got == {"T120": 1, "T250": 0}, (name, got)
    assert not gate_sees_test_run(project, tmp_path, "T120")
    assert not gate_sees_test_run(project, tmp_path, "T250")


def test_row5_a_real_second_command_after_a_continuation_line_still_counts(tmp_path):
    project, got = _file(tmp_path, WT + "echo ok \\\n&& python3 -m pytest -q")
    assert got == {"T120": 1, "T250": 0}
    assert gate_sees_test_run(project, tmp_path, "T120")


def test_row5_a_continuation_inside_a_word_joins_it_as_the_shell_does(tmp_path):
    """`pyt\\` + newline + `est` is one word for the shell, `pytest`: it is a runner, not a stray word."""
    project, got = _file(tmp_path, WT + "pyt\\\nest -q")
    assert got == {"T120": 1, "T250": 0}
    assert gate_sees_test_run(project, tmp_path, "T120")


def test_row5_a_continuation_cannot_glue_a_path_out_of_the_worktree(tmp_path):
    """The shell reads `.` + backslash-newline + `./main` as `../main`: slot 2b must see it too."""
    project, got = _file(tmp_path, WT + "python3 -m pytest -q .\\\n./main")
    assert got == {"T120": 0, "T250": 1}, got


# ── Row 6 (P3-2) — a call that moves the worktree's branch is not filed by the branch it ends on ──
def _rename_to(tmp_path, project, *args):
    _git(tmp_path / "wt-t120", *args)


MOVES = {
    "branch-m": (WT + "git branch -m fix/t900-x && python3 -m pytest -q", ("branch", "-m", "fix/t900-x")),
    "branch-M": (WT + "git branch -M fix/t900-x && python3 -m pytest -q", ("branch", "-M", "fix/t900-x")),
    "checkout-b": (WT + "git checkout -b fix/t900-x && python3 -m pytest -q",
                   ("checkout", "-q", "-b", "fix/t900-x")),
    "switch-c": (WT + "git switch -c fix/t900-x && python3 -m pytest -q",
                 ("switch", "-q", "-c", "fix/t900-x")),
    "checkout-existing": (WT + "git checkout fix/t900-x && python3 -m pytest -q",
                          ("checkout", "-q", "-b", "fix/t900-x")),
    "symbolic-ref": (WT + "git symbolic-ref HEAD refs/heads/fix/t900-x && python3 -m pytest -q",
                     ("checkout", "-q", "-b", "fix/t900-x")),
}


@pytest.mark.parametrize("name", list(MOVES))
def test_row6_a_call_that_moves_the_branch_is_not_filed_by_the_branch_it_ends_on(tmp_path, name):
    command, git_args = MOVES[name]
    project = t120_project(tmp_path)
    _rename_to(tmp_path, project, *git_args)  # the hook runs AFTER the command: the branch has moved
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(command, tmp_path, project)})
    assert trace(project, "T900") == [], name
    assert len(trace(project, "T250")) == 1, name


def test_row6_reading_git_commands_and_a_branch_listing_stay_filed(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(WT + "git status --short && git branch --show-current "
                                       "&& git log -1 && python3 -m pytest -q", tmp_path, project)})
    assert len(trace(project, "T120")) == 1 and trace(project, "T250") == []


# ── Stage 4 fix round — SL6 and SL7 ──────────────────────────────────────────────────────────
def test_sl6_an_even_run_of_backslashes_before_a_newline_is_not_a_continuation(tmp_path):
    """`echo ok\\\\` + newline: the two backslashes are one escaped backslash, the newline ends the
    command, and `git branch -m ...` is a second command (the hook must not read one command)."""
    project, got = _file(tmp_path, WT + "echo ok\\\\\ngit branch -m fix/t999-forged")
    assert got == {"T120": 0, "T250": 1}, got


@pytest.mark.parametrize("command", [
    WT + "echo ok\\\\\\\\\ngit branch -m fix/t999-forged",          # four backslashes: still even
    WT + "echo 'a\\'\ngit branch -m fix/t999-forged",                # single quotes have no escapes
])
def test_sl6_other_even_or_quoted_backslashes_before_a_newline(tmp_path, command):
    _, got = _file(tmp_path, command)
    assert got == {"T120": 0, "T250": 1}, got


def test_sl6_an_odd_run_is_still_a_continuation(tmp_path):
    """One backslash + newline joins the lines: this stays one `echo` command and stays filed."""
    _, got = _file(tmp_path, WT + "echo ok \\\nand more")
    assert got == {"T120": 1, "T250": 0}, got


@pytest.mark.parametrize("command", [
    WT + "git --namespace log checkout -b fix/t999-x",      # `--namespace` takes `log` as its value
    WT + "git --git-dir log checkout -b fix/t999-x",
    WT + "git --attr-source log checkout -b fix/t999-x",
    WT + "git --super-prefix log checkout -b fix/t999-x",
    WT + "git --config-env log checkout -b fix/t999-x",
    WT + "git -c x=y log -1",
    WT + "git --unknown-option log -1",
])
def test_sl7_a_global_option_before_the_verb_is_not_filed_unless_it_takes_no_value(tmp_path, command):
    _, got = _file(tmp_path, command)
    assert got == {"T120": 0, "T250": 1}, got


@pytest.mark.parametrize("command", [
    WT + "git --no-pager log -1", WT + "git -P status", WT + "git --no-pager -P diff --stat",
    WT + "git --no-optional-locks status",
])
def test_sl7_the_no_value_global_options_stay_filed(tmp_path, command):
    _, got = _file(tmp_path, command)
    assert got == {"T120": 1, "T250": 0}, got
