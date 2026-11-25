#!/usr/bin/env python3
"""T354 — the session loop binds its task after the hook's close-out moved the row to Done.

After a passed auto verify, the close-out (`.claude/hooks/lib/auto_closeout.py`) moves a `Mode: auto`
row to `### Done` at once and appends `Done <date>: auto verify pass (session <id>, commit <sha>)`.
Every loop ticket is `Mode: auto`, so the T317 R4 rule (the row must be in Ready for Review) refused
every loop merge and `[ticket]` push. The loop now also binds a Done row whose last close-out note
names a commit that has this run's own hook pass record (written after this session's own `--start`
call, held by the branch). A Done row with no note, or with a note for other code, binds nothing
(`tasks/TASK_GUIDE_T354.md`, AC 1-5).

Every board, guide, transcript and git repo here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t354_loop_closed_out_row.py -q -p no:cacheprovider
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import gate, git, kanban, merge_gate  # noqa: E402
from test_admin_tag import auto_verified, reason  # noqa: E402
from test_t317_loop_binding import TAG_AT, pass_written_at  # noqa: E402
from test_t317_fix_round import _gate_case, _loop  # noqa: E402

import verify_record  # noqa: E402

assert gate  # the fixture, imported for pytest

SESSION = "s-1"  # the session `auto_verified` writes into the run record


def verified_sha(fx):
    """The commit the hook's run record names (the commit that added T900's guide)."""
    return git(fx.wt, "log", "-1", "--format=%H", "--", "tasks/TASK_GUIDE_T900.md")


def note(sha, day="2026-11-25", session=SESSION):
    return f"Done {day}: auto verify pass (session {session}, commit {sha})"


ROW = "- [ ] **T900** — fixture T900 | agent | C1 | Risk: Low | P1"


def board_with(fx, done_row_extra=None, todo_row_extra=None):
    """Rewrite the fixture board: T900 in Done (with `done_row_extra` after the row, if any), or in
    Todo with `todo_row_extra`."""
    if todo_row_extra is not None:
        text = kanban().replace("### Todo\n\n", f"### Todo\n{ROW} | {todo_row_extra}\n")
    else:
        text = kanban().replace("### Done\n", f"### Done\n{ROW}"
                                + ("" if done_row_extra is None else " | " + done_row_extra) + "\n")
    with open(fx.kanban, "w", encoding="utf-8") as f:
        f.write(text)


# ── AC 1, 2: a Done row with this run's close-out note binds ────────────────────────────────────
@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_a_done_row_with_this_runs_close_out_note_binds_the_loop(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    board_with(fx, done_row_extra=note(verified_sha(fx)))
    command, cwd = _gate_case(fx, tag)
    assert reason(command, cwd, _loop(tmp_path, tag)) is None


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_the_last_close_out_note_of_the_row_counts(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    board_with(fx, done_row_extra=note("0" * 40, "2026-11-24") + " | " + note(verified_sha(fx)))
    command, cwd = _gate_case(fx, tag)
    assert reason(command, cwd, _loop(tmp_path, tag)) is None


# ── AC 3, 4: a Done row without this run's note binds nothing ────────────────────────────────────
@pytest.mark.parametrize("tag", ["admin", "ticket"])
@pytest.mark.parametrize("case", ["no-note", "other-commit", "short-sha", "record-before-start",
                                  "other-session", "note-not-at-row-end"])
def test_a_done_row_without_this_runs_note_does_not_bind(gate, tmp_path, tag, case):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    sha = verified_sha(fx)
    pass_written_at(fx, TAG_AT + 10 if case == "record-before-start" else TAG_AT + 60)
    extra = {"no-note": None, "other-commit": note("1" * 40), "short-sha": note(sha[:12]),
             "record-before-start": note(sha), "other-session": note(sha, session="s-2"),
             "note-not-at-row-end": note(sha) + " | moved by hand"}[case]
    board_with(fx, done_row_extra=extra)
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _loop(tmp_path, tag))
    assert text is not None and f"[{tag}]" in text, (case, text)


# ── AC 5: the note binds only in the task's own row under Done ───────────────────────────────────
@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_a_close_out_note_in_a_todo_row_does_not_bind(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    board_with(fx, todo_row_extra=note(verified_sha(fx)))
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _loop(tmp_path, tag))
    assert text is not None and f"[{tag}]" in text, text


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_another_tasks_done_row_note_does_not_bind(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    text = kanban(done=("T901",)).replace("| Risk: Low | P1\n", "| Risk: Low | P1 | "
                                          + note(verified_sha(fx)) + " T900\n", 1)
    with open(fx.kanban, "w", encoding="utf-8") as f:
        f.write(text)  # T900 has no row at all; T901's row carries T900's commit
    command, cwd = _gate_case(fx, tag)
    result = reason(command, cwd, _loop(tmp_path, tag))
    assert result is not None and f"[{tag}]" in result, result


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_two_done_rows_for_the_task_do_not_bind(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    line = f"{ROW} | {note(verified_sha(fx))}\n"
    with open(fx.kanban, "w", encoding="utf-8") as f:
        f.write(kanban().replace("### Done\n", "### Done\n" + line + line))
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _loop(tmp_path, tag))
    assert text is not None and f"[{tag}]" in text, text


# ── Stage 4 P2-1: the helper's own record checks, not shadowed by `_pass_recorded_since` ────────
def _second_record(fx, sha, offset_s):
    """A hook pass record for `sha` from session `s-1`, dated `offset_s` from now."""
    import time
    verify_record.write_record(merge_gate.ROOT, "T900", sha, "pass", SESSION, "log2.txt")
    path = verify_record.record_path(merge_gate.ROOT, "T900", sha)
    when = time.time() + offset_s
    os.utime(path, (when, when))


@pytest.mark.parametrize("tag", ["admin", "ticket"])
@pytest.mark.parametrize("case", ["note-record-before-start", "note-commit-off-branch"])
def test_the_notes_own_commit_must_pass_the_record_rule(gate, tmp_path, tag, case):
    """Commit A (the guide commit) has a fresh record held by the branch, so `_pass_recorded_since`
    holds. The note names commit B: its record is older than this session's `--start`, or B is not
    on the task branch. The Done row must not bind through B."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    if case == "note-record-before-start":
        other = git(fx.wt, "rev-parse", "HEAD")  # the review-file commit after A, on the branch
        assert other != verified_sha(fx)
        _second_record(fx, other, TAG_AT + 10)
    else:
        git(fx.main, "commit", "-q", "--allow-empty", "-m", "on main only")
        other = git(fx.main, "rev-parse", "HEAD")
        _second_record(fx, other, TAG_AT + 60)
    board_with(fx, done_row_extra=note(other))
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _loop(tmp_path, tag))
    assert text is not None and f"[{tag}]" in text, (case, text)
