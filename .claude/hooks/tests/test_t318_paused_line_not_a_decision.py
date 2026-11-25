#!/usr/bin/env python3
"""T318 — `stop_auto_mode_check.py` does not read its own `Paused: auto-mode check failed — …` line
as a decision (`tasks/TASK_GUIDE_T318.md`, AC 1-3). Every project here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t318_paused_line_not_a_decision.py -v
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_stop_auto_mode_check import (EXT_ROW, FLAG, _blocked, _good_decisions, _project,  # noqa: E402
                                       _report, _run, _trace)

PAUSED = ("Paused: auto-mode check failed — Risk High: decision 1 (`⚠`) is a choice — it is flagged "
          f"⚠ — so it must be `DEBATED` with exactly 3 Advocates named [report 000000000000]")


def _with_line(extra):
    return _report(_good_decisions(3)).replace("Memory: nothing new", f"{extra}\nMemory: nothing new")


def test_ac1_a_paused_line_quoting_a_flag_is_not_a_decision(tmp_path):
    project = _project(tmp_path, [EXT_ROW], review=_with_line(PAUSED), untagged=_trace(3))
    result, out = _run(project)
    assert result.returncode == 0 and out == {}, (out, result.stderr)


def test_ac2_other_skipped_prefixes_and_a_hand_written_paused_line_still_block(tmp_path):
    """Review P2-1: a flagged choice hidden behind a prefix the agent writes itself is still a choice."""
    lines = [f"Closed: {FLAG}", f"**Not done:** merge {FLAG}", f"Not done: pick B {FLAG}",
             f"- verify: {FLAG}", f"Paused: choose B {FLAG}"]
    for i, line in enumerate(lines):
        project = _project(tmp_path / f"case{i}", [EXT_ROW], review=_with_line(line), untagged=_trace(3))
        _, out = _run(project)
        assert _blocked(out) and "is a choice" in out["reason"], (line, out)


def test_ac3_a_real_flagged_decision_still_blocks_beside_a_paused_line(tmp_path):
    decisions = _good_decisions(3) + [f"3. kept recurring.csv — FACT: data/recurring.csv:1 \"rent\" {FLAG}"]
    review = _report(decisions).replace("Memory: nothing new", f"{PAUSED}\nMemory: nothing new")
    project = _project(tmp_path, [EXT_ROW], review=review, untagged=_trace(3))
    _, out = _run(project)
    assert _blocked(out) and "decision 3" in out["reason"], out
