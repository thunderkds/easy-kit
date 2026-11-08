"""T285 — the step limit counts per sub-agent run (agent_id), not per session and task.

Covers AC1-AC5 of tasks/TASK_GUIDE_T285.md. Drives the real hook as a
subprocess, as the harness does. The task is resolved from CLAUDE_ACTIVE_TASK
so these tests do not depend on a transcript file; the counter key is what
is under test.
"""
import glob
import json
import os
import subprocess
import sys

HOOK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(HOOK_DIR, "pre_agent_step_limit.py")
STATE_DIR = os.path.join(HOOK_DIR, ".state")
LIMIT = 90

_NO_AGENT = object()


def _cleanup(task_id):
    for f in glob.glob(os.path.join(STATE_DIR, f"step_count_*{task_id}*.txt")):
        os.remove(f)


def _counters(task_id):
    return sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(STATE_DIR, f"step_count_*{task_id}*.txt"))
    )


def _run(task_id, session="S", agent=_NO_AGENT):
    event = {"tool_name": "Bash", "tool_input": {"command": "true"}, "session_id": session}
    if agent is not _NO_AGENT:
        event["agent_id"] = agent
    env = dict(os.environ)
    env["CLAUDE_ACTIVE_TASK"] = task_id
    env["CLAUDE_STEP_LIMIT"] = str(LIMIT)
    return subprocess.run(
        [sys.executable, HOOK], input=json.dumps(event), capture_output=True, text=True, env=env
    )


def _is_block(proc):
    return bool(proc.stdout.strip()) and json.loads(proc.stdout)["decision"] == "block"


def test_ac1_two_agents_of_one_task_have_two_counters_and_no_shared_block():
    task = "T921"
    _cleanup(task)
    try:
        for _ in range(60):
            assert not _is_block(_run(task, agent="agentA"))
            assert not _is_block(_run(task, agent="agentB"))
        assert _counters(task) == [
            f"step_count_S_agentA_{task}.txt",
            f"step_count_S_agentB_{task}.txt",
        ]
        with open(os.path.join(STATE_DIR, f"step_count_S_agentA_{task}.txt")) as f:
            assert f.read().splitlines()[0] == "60"
    finally:
        _cleanup(task)


def test_ac3_one_agents_91st_call_is_blocked_and_another_agent_is_allowed():
    task = "T922"
    _cleanup(task)
    try:
        for _ in range(LIMIT):
            assert not _is_block(_run(task, agent="agentA"))
        # Agent B's first call comes while A sits on 90: with one shared counter it
        # would be call 91 and blocked. With a counter per agent it is call 1.
        other = _run(task, agent="agentB")
        assert not _is_block(other), f"agent B must not be blocked by agent A: {other.stdout}"
        assert _is_block(_run(task, agent="agentA")), "call 91 of agent A must be blocked"
    finally:
        _cleanup(task)


def test_ac4_a_single_looping_agent_is_still_blocked_resets_and_escalates():
    task = "T923"
    _cleanup(task)
    try:
        blocks = 0
        for _ in range(3 * (LIMIT + 1)):
            proc = _run(task, agent="agentA")
            if _is_block(proc):
                blocks += 1
                last = json.loads(proc.stdout)["reason"]
        assert blocks == 3, f"a looping agent is interrupted every {LIMIT + 1} calls, got {blocks}"
        assert "interrupted 3 times" in last, "T057 escalation wording must still appear"
        with open(os.path.join(STATE_DIR, f"step_count_S_agentA_{task}.txt")) as f:
            assert f.read().splitlines() == ["0", "3"]
        assert not _is_block(_run(task, agent="agentA")), "T057 self-clearing: next call allowed"
    finally:
        _cleanup(task)


def test_ac2_an_event_without_agent_id_keeps_todays_key_and_limit():
    task = "T924"
    _cleanup(task)
    try:
        for _ in range(LIMIT):
            assert not _is_block(_run(task))
        assert _is_block(_run(task)), "the main thread is still blocked at call 91"
        assert _counters(task) == [f"step_count_S_{task}.txt"]
    finally:
        _cleanup(task)


def test_ac5_unsafe_agent_id_is_reduced_to_a_safe_file_name_fragment():
    task = "T925"
    _cleanup(task)
    try:
        assert not _is_block(_run(task, agent="../../x"))
        assert not _is_block(_run(task, agent="a/b\\c\x00d e"))
        assert _counters(task) == [
            f"step_count_S_abcde_{task}.txt",
            f"step_count_S_x_{task}.txt",
        ]
        outside = glob.glob(os.path.join(HOOK_DIR, f"*{task}*")) + glob.glob(
            os.path.join(os.path.dirname(HOOK_DIR), f"*{task}*")
        )
        assert outside == [], f"nothing may be written outside .state/: {outside}"
    finally:
        _cleanup(task)


def test_ac5_a_non_string_or_empty_agent_id_falls_back_to_the_main_thread_key():
    task = "T926"
    _cleanup(task)
    try:
        for bad in (12345, None, ["a"], {"k": "v"}, "", "../..", "///"):
            proc = _run(task, agent=bad)
            assert not _is_block(proc)
        # every call counted on the one main-thread counter: never unlimited
        assert _counters(task) == [f"step_count_S_{task}.txt"]
        with open(os.path.join(STATE_DIR, f"step_count_S_{task}.txt")) as f:
            assert f.read().splitlines()[0] == "7"
    finally:
        _cleanup(task)


def test_ac5_a_non_string_agent_id_is_still_limited():
    task = "T927"
    _cleanup(task)
    try:
        for _ in range(LIMIT):
            assert not _is_block(_run(task, agent=12345))
        assert _is_block(_run(task, agent=12345)), "a bad agent_id must never mean no limit"
    finally:
        _cleanup(task)
