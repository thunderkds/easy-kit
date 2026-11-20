#!/usr/bin/env python3
"""
SubagentStop hook — writes a `ReviewerDone` trace record when a reviewer sub-agent ends (T341, AC 11).

The merge gate (`pre_bash_block_unsafe_merge.py` `trace_shows_review`) refuses the merge of an
extended-track task branch until the trace holds this record for the task and the commit being
merged. The `Agent` spawn record cannot prove it: `post_tool_trace.py` writes that record when the
call returns, and in this harness every spawn returns at launch (`spawn.status: async_launched`),
before the review has run.

A sub-agent is a reviewer when its spawn prompt's first three lines are `REVIEWER_PROMPT_PREFIX`,
`Task ID: <ID>` and `Commit: <40-hex>` (`docs/claude-md/pipeline-stages.md`, Stage 4 step 0). The
prompt is the first line of the sub-agent's own transcript, read as `task_context._spawn_prompt`
reads it: `<dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl`. The event's
own fields are never trusted for the task or the commit.

The record (`tool_name` `ReviewerDone`, `task_id`, `commit`, `agent_id`) goes to
`memory/event-trace/<ID>.jsonl`, hash-chained and anchored as `post_tool_trace.py` appends.

Spike (Claude Code 2.1.329, 2026-11-20; a real event captured with a capture-only hook): the event
carries `session_id`, `transcript_path`, `cwd`, `prompt_id`, `permission_mode`, `agent_id`,
`agent_type`, `effort`, `hook_event_name`, `stop_hook_active`, `agent_transcript_path`,
`background_tasks`, `session_crons`, and `last_assistant_message` when the last message has text. No
field says how the sub-agent ended. A sub-agent that ends on an API error (a rate limit) fires
`StopFailure` instead, with `error`, and no `SubagentStop`, so this hook never sees it. A run that is
aborted or throws can still reach `SubagentStop` from the harness's teardown, which looks the same:
that limit is stated in `docs/claude-md/tracks.md` `### Known limits`.

Never raises, always exits 0, prints nothing (a `SubagentStop` decision could keep the sub-agent
running), and writes nothing for any other sub-agent or event.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
try:
    from project_root import exit_outside_kit_project, project_root
except Exception:  # T232: no helper, no known project to write the trace in
    sys.exit(0)
exit_outside_kit_project()
ROOT = project_root()
TRACE_DIR = os.path.join(ROOT, "memory", "event-trace")
try:
    from task_context import _safe_key, _spawn_prompt, normalize_task_id
    from trace_chain import GENESIS, anchor_path, chain_hash, safe_name
except Exception:  # no attribution or chain code: write nothing rather than an unchained record
    sys.exit(0)
try:
    import fcntl
except Exception:  # not POSIX: appends go unlocked and say so
    fcntl = None

# Copied from `pre_bash_block_unsafe_merge.py`, which runs `main()` at import;
# `tests/test_t341_reviewer_done.py` pins the two equal.
REVIEWER_PROMPT_PREFIX = "Review alone, from the repo only:"
TASK_LINE = re.compile(r"Task ID: (\S+)")
COMMIT_LINE = re.compile(r"Commit: ([0-9a-f]{40})")


def reviewer_target(prompt):
    """`(task_id, commit)` that a reviewer spawn prompt names in its first three lines, or None. The
    ID must already be in its canonical, file-safe form (`normalize_task_id` leaves it unchanged)."""
    if not isinstance(prompt, str):
        return None
    lines = prompt.split("\n")
    if len(lines) < 3 or lines[0] != REVIEWER_PROMPT_PREFIX:
        return None
    task, commit = TASK_LINE.fullmatch(lines[1]), COMMIT_LINE.fullmatch(lines[2])
    if not task or not commit or normalize_task_id(task.group(1)) != task.group(1):
        return None
    return task.group(1), commit.group(1)


# --- The append, as `post_tool_trace.py` does it (copied: that module runs `main()` at import) ---

def _lock(f):
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        return True
    except Exception:
        return False


def _last_hash(lines):
    """`hash` of the last chained line, or genesis. A crash-truncated last line is skipped here; the
    verifier reports it as the break."""
    for raw in reversed(lines):
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("hash"), str):
            return rec["hash"]
    return GENESIS


def _write_anchor(task_id, line_no, digest):
    try:
        path = anchor_path(ROOT, task_id)
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        with open(path, "a") as f:
            f.write("%s %d %s\n" % (safe_name(task_id, "_untagged"), line_no, digest))
        return True
    except Exception:
        return False


def append_record(trace_path, task_id, record):
    """Append one chained, anchored line under the trace's lock. A failed anchor is marked
    `"anchor": "failed"` (the gate does not count it), as in `post_tool_trace.py`."""
    with open(trace_path, "a+b") as f:
        if not _lock(f):
            record["lock"] = "failed"
        f.seek(0)
        data = f.read()
        if data and not data.endswith(b"\n"):
            f.write(b"\n")  # end a crash-truncated line; ours starts clean
            data += b"\n"
        lines = data.split(b"\n")[:-1]
        record["prev"] = _last_hash(lines)
        record["hash"] = chain_hash(record)
        if not _write_anchor(task_id, len(lines) + 1, record["hash"]):
            del record["hash"]
            record["anchor"] = "failed"
            record["hash"] = chain_hash(record)
        f.write((json.dumps(record) + "\n").encode("utf-8"))


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or event.get("hook_event_name") != "SubagentStop":
            return
        session_id, agent_id = _safe_key(event.get("session_id")), _safe_key(event.get("agent_id"))
        if not session_id or not agent_id:
            return
        target = reviewer_target(_spawn_prompt(event.get("transcript_path"), session_id, agent_id))
        if target is None:
            return
        task_id, commit = target
        record = {"timestamp": datetime.now(timezone.utc).isoformat(), "tool_name": "ReviewerDone",
                  "task_id": task_id, "commit": commit, "agent_id": agent_id}
        os.makedirs(TRACE_DIR, exist_ok=True)
        append_record(os.path.join(TRACE_DIR, f"{task_id}.jsonl"), task_id, record)
    except Exception:
        return


main()
