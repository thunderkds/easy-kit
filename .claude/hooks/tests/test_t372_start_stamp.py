#!/usr/bin/env python3
"""T372 — the `[admin]` loop binds on the run record's own start stamp, and a repeated tag keeps
the window.

AC 1 — a loop `--start` the transcript reader cannot parse (`… > run.log`, a script) binds when the
       run record carries `started_by` = this session and `started_at` at or after the tag onset.
AC 2 — a stamp from another session, before the onset, or for a commit the branch does not hold
       binds nothing.
AC 3 — a later request that only repeats the tag does not move the loop window; a different tag in
       between does.
AC 4 (unit half) — `write_record` stores the stamp keys only when given; `session_onset`.

Run with: python3 -m pytest .claude/hooks/tests/test_t372_start_stamp.py -q -p no:cacheprovider
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, git, kanban, merge_gate  # noqa: E402
from test_admin_tag import (  # noqa: E402
    SID, auto_verified, bash, human, reason, transcript, _ts)
from test_t317_loop_binding import BRANCH, TAG_AT, spawn, start  # noqa: E402

import auto_mode  # noqa: E402
import verify_record  # noqa: E402

assert gate  # the fixture, imported for pytest

OTHER_SID = "bbbbbbbb-1111-2222-3333-444444444444"
UNPARSED = "python3 .claude/hooks/stop_auto_verify.py --start T900 > run.log"  # `>` to a file


def verified_sha(fx):
    return git(fx.wt, "log", "-1", "--format=%H", "--", "tasks/TASK_GUIDE_T900.md")


def stamp(fx, started_by=SID, start_s=TAG_AT + 20, written_s=TAG_AT + 60, sha=None):
    """Rewrite T900's pass record with a start stamp, dated `written_s` from now."""
    sha = sha or verified_sha(fx)
    path = verify_record.write_record(merge_gate.ROOT, "T900", sha, "pass", "s-1", "log.txt",
                                      started_by=started_by, started_at=_ts(start_s))
    when = time.time() + written_s
    os.utime(path, (when, when))
    return sha


def unparsed_loop(tmp_path, tag="admin", extra=()):
    return transcript(tmp_path, [human(f"run the board [{tag}]", TAG_AT), spawn("T900", TAG_AT + 10),
                                 bash(UNPARSED, "/", TAG_AT + 20)] + list(extra))


# ── AC 1 ──────────────────────────────────────────────────────────────────────────────────
def test_ac1_the_transcript_reader_misses_the_unparsed_start():
    assert merge_gate._command_segments(UNPARSED) is None  # the reason the stamp is needed


def test_ac1_a_stamp_from_this_session_binds_the_admin_merge(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx)
    assert reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path)) is None


def test_ac1_a_stamp_from_this_session_binds_the_ticket_push(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx)
    assert reason(PUSH + " origin " + BRANCH, fx.wt, unparsed_loop(tmp_path, "ticket")) is None


def test_ac1_a_script_start_with_no_start_text_binds(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx)
    path = transcript(tmp_path, [human("run the board [admin]", TAG_AT), spawn("T900", TAG_AT + 10),
                                 bash("bash scripts/run_verify.sh", "/", TAG_AT + 20)])
    assert reason(MERGE + " " + BRANCH, fx.main, path) is None


def test_ac1_control_no_stamp_and_no_parsed_start_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    sha = verified_sha(fx)
    path = verify_record.record_path(merge_gate.ROOT, "T900", sha)
    when = time.time() + TAG_AT + 60
    os.utime(path, (when, when))  # a fresh pass record, but no stamp
    text = reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path))
    assert text is not None and "not the task" in text, text


# ── AC 2 ──────────────────────────────────────────────────────────────────────────────────
def test_ac2_a_stamp_from_another_session_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx, started_by=OTHER_SID)
    text = reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path))
    assert text is not None and "not the task" in text, text


def test_ac2_a_stamp_before_the_tag_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx, start_s=TAG_AT - 10)
    text = reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path))
    assert text is not None and "not the task" in text, text


def test_ac2_a_stamp_in_the_future_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx, start_s=TAG_AT + 3600)
    text = reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path))
    assert text is not None and "not the task" in text, text


def test_ac2_a_stamp_for_a_commit_the_branch_does_not_hold_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    sha = verified_sha(fx)
    path = verify_record.record_path(merge_gate.ROOT, "T900", sha)
    when = time.time() + TAG_AT + 60
    os.utime(path, (when, when))  # the held pass record: fresh, unstamped
    stamp(fx, sha="b" * 40)  # the stamp names a commit no branch holds
    text = reason(MERGE + " " + BRANCH, fx.main, unparsed_loop(tmp_path))
    assert text is not None and "not the task" in text, text


# ── AC 3 ──────────────────────────────────────────────────────────────────────────────────
def test_ac3_a_repeated_admin_tag_after_the_pass_keeps_the_binding(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    sha = verified_sha(fx)
    path = verify_record.record_path(merge_gate.ROOT, "T900", sha)
    when = time.time() + TAG_AT + 60
    os.utime(path, (when, when))
    transcript_path = transcript(tmp_path, [
        human("run the board [admin]", TAG_AT), spawn("T900", TAG_AT + 10), start("T900", TAG_AT + 20),
        human("final flow with [admin] tag is to merge to main", TAG_AT + 90)])
    assert reason(MERGE + " " + BRANCH, fx.main, transcript_path) is None


def test_ac3_a_repeated_tag_keeps_the_stamp_binding_too(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx)
    path = unparsed_loop(tmp_path, extra=[human("go on [admin]", TAG_AT + 90)])
    assert reason(MERGE + " " + BRANCH, fx.main, path) is None


def test_ac3_a_different_tag_in_between_resets_the_window(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    stamp(fx)
    path = unparsed_loop(tmp_path, extra=[human("push only [ticket]", TAG_AT + 80),
                                          human("back to merging [admin]", TAG_AT + 90)])
    text = reason(MERGE + " " + BRANCH, fx.main, path)
    assert text is not None and "not the task" in text, text


# ── AC 4 (unit) and the onset reader ──────────────────────────────────────────────────────
def test_ac4_write_record_without_a_stamp_writes_the_same_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", str(tmp_path / "anchors"))
    verify_record.write_record(str(tmp_path), "T900", "a" * 40, "pass", "s-1", "log.txt")
    assert set(verify_record.read_record(str(tmp_path), "T900", "a" * 40)) == {
        "task", "commit", "verdict", "session", "log"}


def test_ac4_write_record_with_a_stamp_stores_both_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", str(tmp_path / "anchors"))
    verify_record.write_record(str(tmp_path), "T900", "a" * 40, "pass", "s-1", "log.txt",
                               started_by=SID, started_at="2026-11-25T10:00:00+00:00")
    record = verify_record.read_record(str(tmp_path), "T900", "a" * 40)
    assert record["started_by"] == SID and record["started_at"] == "2026-11-25T10:00:00+00:00"


def test_session_onset_keeps_the_first_request_of_the_same_tag(tmp_path):
    path = transcript(tmp_path, [human("a [admin]", -300), human("plain", -200),
                                 human("b [admin]", -100)])
    tag, onset = auto_mode.session_onset(path)
    assert tag == "admin" and abs((onset - auto_mode.parse_ts(_ts(-300))).total_seconds()) < 5


def test_session_onset_resets_on_stop_and_on_another_tag(tmp_path):
    path = transcript(tmp_path, [human("a [admin]", -300), human("[stop]", -200),
                                 human("b [admin]", -100)])
    _, onset = auto_mode.session_onset(path)
    assert abs((onset - auto_mode.parse_ts(_ts(-100))).total_seconds()) < 5
    path = transcript(tmp_path, [human("a [admin]", -300), human("b [ticket]", -100)])
    tag, onset = auto_mode.session_onset(path)
    assert tag == "ticket" and abs((onset - auto_mode.parse_ts(_ts(-100))).total_seconds()) < 5


def test_session_onset_is_none_with_no_session_tag(tmp_path):
    assert auto_mode.session_onset(transcript(tmp_path, [human("plain")])) is None


def test_session_request_still_returns_the_latest_tag_request(tmp_path):
    path = transcript(tmp_path, [human("a [admin]", -300), human("merge T900 [admin]", -100)])
    tag, _, text = auto_mode.session_request(path)
    assert tag == "admin" and text == "merge T900 [admin]"
