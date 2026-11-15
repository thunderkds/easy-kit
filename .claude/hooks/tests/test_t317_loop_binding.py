#!/usr/bin/env python3
"""T317 G1 — the merge gate binds a session tag's task by the loop, not by the request.

In a `[admin]` / `[ticket]` loop the Supervisor picks each ticket itself, so the tag request names
none of them and their guides were written before it. The gate then binds the branch's task when
its row is in Ready for Review, this session changed it since the tag request, holds no other task
In Progress or Ready for Review, ran its own `python3 .claude/hooks/stop_auto_verify.py --start
<ID>` Bash call after the request (R1), and the hook wrote the task's auto verify pass after that
call (`_session_holds`, `_own_start_since`, `_pass_recorded_since`). The locked oracle's fixtures
satisfy the older request binding, so this file drives the loop binding alone: every request here is
dated after the guide's commit.

Run with: python3 -m pytest .claude/hooks/tests/test_t317_loop_binding.py -q -p no:cacheprovider
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, git, kanban, merge_gate  # noqa: E402
from test_admin_tag import (  # noqa: E402
    SID, auto_verified, bash, human, reason, transcript, wrote, _ts)

import verify_record  # noqa: E402

assert gate  # the fixture, imported for pytest

TAG_AT = +60  # the tag request: after every fixture commit, so the request binding cannot hold
BRANCH = "feat/t900-x"


def spawn(task_id, offset_s):
    return {"type": "assistant", "timestamp": _ts(offset_s), "sessionId": SID,
            "message": {"role": "assistant", "content": [{
                "type": "tool_use", "id": "a1", "name": "Agent",
                "input": {"prompt": f"Task ID: {task_id}\nGuide: tasks/TASK_GUIDE_{task_id}.md"}}]}}


def pass_written_at(fx, offset_s):
    """Date the hook's run record for T900's verified commit `offset_s` from now."""
    sha = git(fx.wt, "log", "-1", "--format=%H", "--", "tasks/TASK_GUIDE_T900.md")
    path = verify_record.record_path(merge_gate.ROOT, "T900", sha)
    assert os.path.isfile(path), path
    when = time.time() + offset_s
    os.utime(path, (when, when))


def start(task_id, offset_s):
    """This session's own `--start` Bash call for `task_id` (R1)."""
    return bash(f"python3 .claude/hooks/stop_auto_verify.py --start {task_id}", "/", offset_s)


def loop(tmp_path, tag, extra=()):
    return transcript(tmp_path, [human(f"run the board [{tag}]", TAG_AT), spawn("T900", TAG_AT + 10),
                                 start("T900", TAG_AT + 20)] + list(extra))


def test_admin_loop_binds_the_task_it_ran_and_verified_after_the_tag(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    assert reason(MERGE + " " + BRANCH, fx.main, loop(tmp_path, "admin")) is None


def test_ticket_loop_binds_the_task_it_ran_and_verified_after_the_tag(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    assert reason(PUSH + " origin " + BRANCH, fx.wt, loop(tmp_path, "ticket")) is None


def test_a_pass_recorded_before_the_tag_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)  # the record is dated now, before the tag request
    for tag, command, cwd in (("admin", MERGE + " " + BRANCH, fx.main),
                              ("ticket", PUSH + " origin " + BRANCH, fx.wt)):
        text = reason(command, cwd, loop(tmp_path, tag))
        assert text is not None and "not the task" in text and f"[{tag}]" in text, (tag, text)


def test_work_before_the_tag_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    path = transcript(tmp_path, [spawn("T900", TAG_AT - 30), human("run the board [admin]", TAG_AT),
                                 start("T900", TAG_AT + 20)])
    text = reason(MERGE + " " + BRANCH, fx.main, path)
    assert text is not None and "not the task" in text, text


def test_a_second_open_task_of_the_session_does_not_bind(gate, tmp_path):
    fx = gate(kanban(ready=("T900", "T901")))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    other = wrote(os.path.join(fx.main, "tasks", "TASK_REVIEW_T901.md"), TAG_AT + 20)
    text = reason(MERGE + " " + BRANCH, fx.main, loop(tmp_path, "admin", extra=[other]))
    assert text is not None and "not the task" in text, text
