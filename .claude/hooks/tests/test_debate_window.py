#!/usr/bin/env python3
"""T293 — a Debate counts for its task only from the first change of the task's files in this session.

T287 credits the Advocates run after a `resolve-question` Skill call with `task=<ID>` to that task
for the whole session. In a long session an old Debate for the task name then satisfied the check
for work done much later (`tasks/TASK_REVIEW_T287.md`, `P3 session window`). Now the Skill call and
each Advocate must be dated at or after the window start: the earliest call of this session (or a
sub-agent) that worked on the task (`lib/session_work.py`, the reader T250 uses). Boundary: a call
at exactly the start counts; there is no upper bound (the check runs at the Stop, so a Debate cannot
be newer than the check). A task with no recorded change window keeps the whole-session rule.

  AC 1 — a Debate dated inside the window counts.
  AC 2 — a Debate dated before the window does not count; the pause text is today's.
  AC 3 — a missing or unparsable timestamp does not count.
  AC 4 — a task with no change window in this session keeps the whole-session rule.
  AC 5 — `docs/claude-md/tracks.md` states the rule.

Every fixture drives the real hooks, as `test_stop_attribution_t287.py` does.

Run with: python3 -m pytest .claude/hooks/tests/test_debate_window.py -q
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import session_work as sw  # noqa: E402
from test_stop_attribution_t287 import (  # noqa: E402
    ROOT, SID, T120_ROW, T242_PAUSE, T242_REPORT, T242_ROW, Session, _tracks_section,
    advocate_input, kit_project, t242_project, t242_reviewed, trace)

HOUR = timedelta(hours=1)
SECOND = timedelta(seconds=1)


def _work_start(s):
    """The transcript time of the session's first `Write` (the start of T242's window)."""
    for line in s.transcript.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") == "assistant" and isinstance(content, list) and any(
                b.get("type") == "tool_use" and b.get("name") == "Write" for b in content):
            return datetime.fromisoformat(entry["timestamp"])
    raise AssertionError("no Write in the transcript")


def _add_call(s, use_id, name, tool_input, at):
    """A call with its non-error result in the transcript. `at` is a datetime, a string, or None
    for an entry with no timestamp key at all."""
    stamp = {} if at is None else {"timestamp": at.isoformat() if isinstance(at, datetime) else at}
    s._entry({"type": "assistant", **stamp, "cwd": str(s.project), "sessionId": s.sid,
              "message": {"role": "assistant", "content": [
                  {"type": "tool_use", "id": use_id, "name": name, "input": tool_input}]}})
    s._entry({"type": "user", "timestamp": datetime.now(timezone.utc).isoformat(),
              "sessionId": s.sid, "message": {"role": "user", "content": [
                  {"type": "tool_result", "tool_use_id": use_id, "content": "done",
                   "is_error": False}]}})


def _debate(s, skill_at, advocate_at, args="task=T242 risk=Medium", tag="d"):
    """A Debate in the transcript only (no trace records): the Skill call at `skill_at`, then two
    Advocates at `advocate_at` (one value for both, or a pair)."""
    pair = advocate_at if isinstance(advocate_at, tuple) else (advocate_at, advocate_at)  # any length
    _add_call(s, f"toolu_{tag}0", "Skill", {"skill": "resolve-question", "args": args}, skill_at)
    for n, at in enumerate(pair, 1):
        _add_call(s, f"toolu_{tag}{n}", "Agent", advocate_input(n), at)


def _stop(tmp_path, build):
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    build(s, _work_start(s))
    return s.stop()


# -- AC 1 ----------------------------------------------------------------------------------------
def test_ac1_a_debate_dated_inside_the_window_counts(tmp_path):
    reason, stderr = _stop(tmp_path, lambda s, start: _debate(s, start + SECOND, start + 2 * SECOND))
    assert reason is None, (reason, stderr)


def test_ac1_a_debate_at_the_exact_start_of_the_window_counts(tmp_path):
    """The boundary: `>=`, not `>`."""
    reason, stderr = _stop(tmp_path, lambda s, start: _debate(s, start, start))
    assert reason is None, (reason, stderr)


def test_ac1_the_window_starts_at_the_first_change_not_the_last(tmp_path):
    """T242's guide was first written 3 hours ago; a Debate 2 hours ago is inside the window."""
    def build(s, start):
        _add_call(s, "toolu_early", "Write", {"file_path": str(s.project / "tasks" /
                                                               "TASK_GUIDE_T242.md"),
                                              "content": "x"}, start - 3 * HOUR)
        _debate(s, start - 2 * HOUR, start - 2 * HOUR + SECOND)
    reason, stderr = _stop(tmp_path, build)
    assert reason is None, (reason, stderr)


# -- AC 2 ----------------------------------------------------------------------------------------
def test_ac2_a_debate_dated_before_the_window_does_not_count(tmp_path):
    reason, _ = _stop(tmp_path, lambda s, start: _debate(s, start - 5 * HOUR,
                                                         start - 5 * HOUR + SECOND))
    assert reason and T242_PAUSE in reason, reason


def test_ac2_a_debate_one_second_before_the_window_does_not_count(tmp_path):
    reason, _ = _stop(tmp_path, lambda s, start: _debate(s, start - SECOND, start - SECOND))
    assert reason and T242_PAUSE in reason, reason


@pytest.mark.parametrize("skill_back,advocate_back", [(5, 0), (0, 5)],
                         ids=["old-skill-call-new-advocates", "new-skill-call-old-advocates"])
def test_ac2_the_skill_call_and_the_advocates_must_both_be_inside(tmp_path, skill_back,
                                                                 advocate_back):
    def build(s, start):
        _debate(s, start + SECOND - skill_back * HOUR, start + 2 * SECOND - advocate_back * HOUR)
    reason, _ = _stop(tmp_path, build)
    assert reason and "the trace has 0" in reason, reason


def test_ac2_one_old_and_one_new_advocate_leave_one_too_few(tmp_path):
    def build(s, start):
        _debate(s, start + SECOND, (start - 5 * HOUR, start + 2 * SECOND))
    reason, _ = _stop(tmp_path, build)
    assert reason and "the trace has 1" in reason, reason


# -- AC 3 ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [None, "", "not a date", 12345],
                         ids=["no-key", "empty", "garbage", "number"])
def test_ac3_a_skill_call_with_a_bad_timestamp_does_not_count(tmp_path, bad):
    def build(s, start):
        _debate(s, bad, start + SECOND)
    reason, _ = _stop(tmp_path, build)
    assert reason and T242_PAUSE in reason, reason


@pytest.mark.parametrize("bad", [None, "not a date"], ids=["no-key", "garbage"])
def test_ac3_an_advocate_call_with_a_bad_timestamp_does_not_count(tmp_path, bad):
    def build(s, start):
        _debate(s, start + SECOND, (bad, start + 2 * SECOND))
    reason, _ = _stop(tmp_path, build)
    assert reason and "the trace has 1" in reason, reason


# -- AC 4 ----------------------------------------------------------------------------------------
T300_ROW = T120_ROW.replace("T120", "T300").replace("Risk: Low", "Risk: Medium")
T300_RECORD = """# Minimal-track Decision records

## T300 — A choice with a Debate · minimal
Mode: auto
Risk: Medium
**Asked:** "start it [auto]"
**Decisions:**
1. Pick A — DEBATED: A (Advocate 1: a; Advocate 2: b) ⚠ decided for you — please review
**Checked:**
- Suite: `python3 -m pytest -q` — 3 passed
**Files:** `setup.sh`
**Memory:** nothing new
**Not done:** merge (yours); auto verify: running (T182)
"""


def _t300(tmp_path, debate):
    """A marked minimal-track record: its work leaves nothing the transcript can name (the main
    checkout), so the task has no change window in this session."""
    project = kit_project(tmp_path, [T300_ROW], {"tasks/MINIMAL_LOG.md": T300_RECORD,
                                                  "setup.sh": "echo v1\n"})
    s = Session(project, tmp_path)
    s.request("start it [auto]")
    s.point_at("T300")
    s.call("Bash", {"command": "python3 -m pytest -q"})
    if debate:
        now = datetime.now(timezone.utc)
        _debate(s, now - 5 * HOUR, now - 5 * HOUR + SECOND, args="task=T300 risk=Medium")
    return s.stop()


def test_ac4_a_task_with_no_change_window_keeps_the_whole_session_rule(tmp_path):
    reason, stderr = _t300(tmp_path, debate=True)
    assert reason is None, (reason, stderr)


def test_ac4_control_the_same_task_without_the_debate_still_pauses(tmp_path):
    reason, _ = _t300(tmp_path / "b", debate=False)
    assert reason and "T300: 1 `DEBATED` line(s) need ≥2" in reason and "the trace has 0" in reason


# -- P2-1: the trace records obey the window too --------------------------------------------------
HINT = "a Debate was found before the task's first change in this session; rerun it after the first change"


def _advocates_to_trace(s, file_name, age):
    """Two Advocate `Agent` calls through the real trace hook, filed in `memory/event-trace/
    <file_name>.jsonl` (`T242` through the pointer, `_untagged` with the pointer removed); then their
    records are dated `age` ago, as if an earlier Debate had run."""
    state = s.project / ".claude" / "hooks" / ".state" / "active_task.d" / s.sid
    if file_name == "_untagged":
        state.unlink()
    for n in (1, 2):
        s.call("Agent", advocate_input(n))
    path = s.project / "memory" / "event-trace" / f"{file_name}.jsonl"
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("tool_name") == "Agent":
            record["timestamp"] = (datetime.now(timezone.utc) - age).isoformat()
        lines.append(json.dumps(record))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _trace_run(tmp_path, file_name, age):
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    _advocates_to_trace(s, file_name, age)
    assert [r["tool_name"] for r in trace(project, file_name)].count("Agent") == 2
    return s


@pytest.mark.parametrize("file_name,age", [("T242", 3 * 24 * HOUR), ("_untagged", 2 * HOUR)],
                         ids=["old-record-in-the-task-file", "old-record-in-untagged"])
def test_p2_1_an_advocate_trace_record_before_the_window_does_not_count(tmp_path, file_name, age):
    reason, _ = _trace_run(tmp_path, file_name, age).stop()
    assert reason and T242_PAUSE in reason, reason


@pytest.mark.parametrize("file_name", ["T242", "_untagged"])
def test_p2_1_an_advocate_trace_record_inside_the_window_counts(tmp_path, file_name):
    reason, stderr = _trace_run(tmp_path, file_name, timedelta(0)).stop()
    assert reason is None, (reason, stderr)


def test_p2_1_a_trace_record_with_a_bad_timestamp_does_not_count(tmp_path):
    s = _trace_run(tmp_path, "T242", timedelta(0))
    path = s.project / "memory" / "event-trace" / "T242.jsonl"
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("tool_name") == "Agent":
            record["timestamp"] = "not a date"
        lines.append(json.dumps(record))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    reason, _ = s.stop()
    assert reason and T242_PAUSE in reason, reason


def test_p2_1_a_task_with_no_window_counts_old_trace_records(tmp_path):
    """AC 4 for the trace side: the minimal record has no window, so a 3-day-old record counts."""
    project = kit_project(tmp_path, [T300_ROW], {"tasks/MINIMAL_LOG.md": T300_RECORD,
                                                  "setup.sh": "echo v1\n"})
    s = Session(project, tmp_path)
    s.request("start it [auto]")
    s.point_at("T300")
    s.call("Bash", {"command": "python3 -m pytest -q"})
    _advocates_to_trace(s, "T300", 3 * 24 * HOUR)
    reason, stderr = s.stop()
    assert reason is None, (reason, stderr)


# -- P2-3: the pause says why ---------------------------------------------------------------------
def test_p2_3_the_pause_names_a_debate_found_before_the_window(tmp_path):
    reason, _ = _stop(tmp_path, lambda s, start: _debate(s, start - 5 * HOUR,
                                                         start - 5 * HOUR + SECOND))
    assert reason and T242_PAUSE in reason and HINT in reason, reason


def test_p2_3_the_pause_has_no_hint_when_no_debate_was_found(tmp_path):
    reason, _ = _stop(tmp_path, lambda s, start: None)
    assert reason and T242_PAUSE in reason and "a Debate was found" not in reason, reason


def test_p2_3_the_pause_has_no_hint_for_a_debate_of_another_task(tmp_path):
    reason, _ = _stop(tmp_path, lambda s, start: _debate(s, start - 5 * HOUR, start - 5 * HOUR,
                                                         args="task=T241 risk=Medium"))
    assert reason and "a Debate was found" not in reason, reason


# -- P3-1: the "no window" fallbacks of session_window --------------------------------------------
def _old_trace_session(tmp_path):
    return _trace_run(tmp_path, "T242", 3 * 24 * HOUR)


def test_p3_1_a_transcript_that_cannot_be_read_keeps_the_whole_session_rule(tmp_path):
    """`work_entries` returns None: no window, so the 3-day-old record counts as before T293."""
    s = _old_trace_session(tmp_path)
    reason, _ = s.stop()
    assert reason and T242_PAUSE in reason  # control: with the window, the record is too old
    saved = s.transcript.read_text(encoding="utf-8")
    s.transcript.unlink()
    try:
        reason, stderr = s.stop()
    finally:
        s.transcript.write_text(saved, encoding="utf-8")
    assert reason is None, (reason, stderr)


def test_p3_1_a_window_reader_that_raises_keeps_the_whole_session_rule(tmp_path):
    s = _old_trace_session(tmp_path)
    lib = s.project / ".claude" / "hooks" / "lib" / "session_work.py"
    lib.write_text(lib.read_text(encoding="utf-8") + "\n\ndef work_start(_entries, _task_id, _worktrees):\n"
                   "    raise RuntimeError('window reader broke')\n", encoding="utf-8")
    reason, stderr = s.stop()
    assert reason is None, (reason, stderr)
    assert "Debate window unknown (RuntimeError)" in stderr, stderr


# -- round 3: boundary of the trace side, the hint's false cases, the Risk High reason ------------
def test_r3_a_trace_record_at_the_exact_start_of_the_window_counts(tmp_path):
    """The boundary of the trace side: `>=`, not `>` (as the transcript side's test)."""
    s = _trace_run(tmp_path, "T242", timedelta(0))
    start = _work_start(s)
    path = s.project / "memory" / "event-trace" / "T242.jsonl"
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("tool_name") == "Agent":
            record["timestamp"] = start.isoformat()
        lines.append(json.dumps(record))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    reason, stderr = s.stop()
    assert reason is None, (reason, stderr)


def test_r3_one_advocate_inside_the_window_is_too_few_and_gives_no_hint(tmp_path):
    """Nothing fell before the window, so nothing is dropped and no hint is given."""
    def build(s, start):
        _debate(s, start + SECOND, (start + 2 * SECOND,))
    reason, _ = _stop(tmp_path, build)
    assert reason and "the trace has 1" in reason, reason
    assert "a Debate was found" not in reason, reason


T243_ROW = T242_ROW.replace("T242", "T243").replace("Risk: Medium", "Risk: High")
T243_REPORT = (T242_REPORT.replace("T242", "T243").replace(
    "(Advocate 1: symlink the kit dirs; Advocate 2: copy at release)",
    "(Advocate 1: symlink the kit dirs; Advocate 2: copy at release; Advocate 3: ship nothing)"))
D10_TEXT = "Risk High, but no decision was DEBATED with 3 Advocates"


def test_r3_the_risk_high_reason_carries_the_hint(tmp_path):
    project = kit_project(tmp_path, [T243_ROW], {
        "tasks/TASK_GUIDE_T243.md": "# TASK_GUIDE — T243\n**Complexity Level**: C2\n"
                                    "**Risk Level**: High\n",
        "tasks/TASK_REVIEW_T243.md": T243_REPORT})
    s = Session(project, tmp_path)
    s.request("run T243 [auto]", seconds_ago=900)
    s.point_at("T243")
    s.call("Write", {"file_path": str(project / "tasks" / "TASK_REVIEW_T243.md"), "content": "x"})
    s.call("Bash", {"command": "python3 -m pytest -q"})
    s.call("Skill", {"skill": "code-review", "args": "task=T243"})
    s.call("Skill", {"skill": "security-review"})
    start = _work_start(s)
    _debate(s, start - 5 * HOUR, (start - 5 * HOUR,) * 3, args="task=T243 risk=High")
    reason, _ = s.stop()
    assert reason and f"{D10_TEXT} ({HINT})" in reason, reason


# -- the window reader ---------------------------------------------------------------------------
def _call(name, tool_input, at, cwd="/nowhere"):
    return (at, name, tool_input, cwd)


GUIDE = {"file_path": "/repo/tasks/TASK_GUIDE_T242.md", "content": "x"}
T0 = datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc)


def test_work_start_is_the_earliest_dated_call_that_worked_on_the_task():
    entries = [_call("Write", GUIDE, T0 + 2 * HOUR), _call("Edit", GUIDE, T0 + HOUR),
               _call("Write", GUIDE, T0 + 3 * HOUR)]
    assert sw.work_start(entries, "T242", []) == T0 + HOUR


def test_work_start_ignores_reads_other_tasks_and_calls_with_no_date():
    other = {"file_path": "/repo/tasks/TASK_GUIDE_T241.md", "content": "x"}
    entries = [_call("Write", GUIDE, None), _call("Write", other, T0),
               _call("Bash", {"command": "cat tasks/TASK_GUIDE_T242.md"}, T0),
               _call("Write", GUIDE, T0 + HOUR)]
    assert sw.work_start(entries, "T242", []) == T0 + HOUR


def test_work_start_is_none_when_the_task_has_no_dated_change():
    assert sw.work_start([], "T242", []) is None
    assert sw.work_start([_call("Write", GUIDE, None)], "T242", []) is None


def test_work_entries_carry_the_call_time_and_load_work_is_unchanged(tmp_path):
    t = tmp_path / "s.jsonl"
    stamp = T0.isoformat()
    t.write_text(json.dumps({"type": "assistant", "timestamp": stamp, "cwd": "/w", "message": {
        "content": [{"type": "tool_use", "id": "a", "name": "Write", "input": GUIDE}]}}) + "\n"
                 + json.dumps({"type": "assistant", "message": {"content": [
                     {"type": "tool_use", "id": "b", "name": "Edit", "input": GUIDE}]}}) + "\n",
                 encoding="utf-8")
    assert sw.work_entries(str(t)) == [(T0, "Write", GUIDE, "/w"), (None, "Edit", GUIDE, None)]
    assert sw.load_work(str(t)) == [("Write", GUIDE, "/w"), ("Edit", GUIDE, None)]
    assert sw.work_entries(str(tmp_path / "missing.jsonl")) is None


# -- AC 5 ----------------------------------------------------------------------------------------
def test_ac5_tracks_md_states_the_window_rule():
    check = _tracks_section("Auto-mode check (Stop hook)")
    assert ("The Skill call and each Advocate must be dated at or after the first change of the "
            "task's files in this session") in check, check
    assert "a missing or unparsable timestamp does not count" in check, check
    assert "A task with no recorded change window keeps the whole-session rule" in check, check
    limits = _tracks_section("Known limits")
    assert "A Debate counts only from the task's first change in this session (T293)." in limits
    assert ("make the first change to a task file (the guide, the review file or the failing test in "
            "its worktree) before the Debate") in check, check
    assert "Advocate trace records obey the same window" in check, check
    assert "does not skip symlinks and does not filter `sessionId`" in limits, limits
    assert "must rerun the Debate" in limits and "earlier session" in limits, limits
    assert "Times of the work and of the Debate come from the transcript" in limits, limits
    assert "Times come from the transcript for both" not in limits, limits
    review = (ROOT / "tasks" / "TASK_REVIEW_T287.md").read_text(encoding="utf-8")
    line = next(l for l in review.splitlines() if "**P3** session window" in l)
    assert "Fixed in T293" in line and "Skipped, follow-up" not in line, line
