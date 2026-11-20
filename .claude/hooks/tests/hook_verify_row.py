"""T309: the one shared way for a test to give a task a `verify` Evidence row the merge gate counts.

Since T309 the gate counts no `verify` row an agent typed by hand, even with "pass" in Notes: only
a hook-written row (`auto-run by hook`, T182 D5) with its run record, or the user's own `/verify`
line with its transcript proof (T308). A test whose point is something else (worktree evidence,
push narrowing, octopus merges, companion rows, guide sections) uses this module to swap its
fixture row for a real hook-written pass: the row text `verify_record.row_cells` writes, plus the
run record `verify_record.write_record` writes, for the checkout's head commit.

Modelled on `_hook_row` in `test_t308_user_verify_extended.py` / `test_t309_hand_typed_pass_row.py`.

**A fixed code commit.** Many fixtures build a plain directory (no git) as their checkout and keep
their review file as a module-level string. `code_commit(checkout)` turns such a directory into a
git repository whose only commit is an empty root commit with fixed author, committer, dates and
message, so its hash is the same on every machine: `CODE_SHA`. A module constant can then hold the
row (`HOOK_PASS_ROW`), and the fixture only calls `prove(root, checkout)` to make it true.

Not a test module (no `test_` prefix), so pytest collects nothing here.
"""
import os
import subprocess
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

import verify_record  # noqa: E402

TASK = "T900"
SESSION = "hook-sess-1"
FIXED = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.com",
         "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.com",
         "GIT_AUTHOR_DATE": "2026-11-11T00:00:00+00:00",
         "GIT_COMMITTER_DATE": "2026-11-11T00:00:00+00:00",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def _git(checkout, *args):
    done = subprocess.run(["git", "-C", str(checkout), *args], capture_output=True, text=True,
                          timeout=30, env={**os.environ, **FIXED})
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {checkout}: {done.stderr.strip()}")
    return done.stdout.strip()


def _is_own_repo(checkout):
    """True when `checkout` is the top level of its own git repository (never an enclosing one)."""
    done = subprocess.run(["git", "-C", str(checkout), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, timeout=30,
                          env={**os.environ, **FIXED})
    return (done.returncode == 0
            and os.path.realpath(done.stdout.strip()) == os.path.realpath(str(checkout)))


def code_commit(checkout):
    """The head commit of `checkout`. A directory that is not its own git repository becomes one,
    with the fixed empty root commit (`CODE_SHA`). Files already in it stay untracked."""
    os.makedirs(str(checkout), exist_ok=True)
    if not _is_own_repo(checkout):
        _git(checkout, "init", "-q", "--template=")  # no sample hooks: /tmp is a small tmpfs
        _git(checkout, "commit", "-q", "--allow-empty", "--no-verify", "-m", "fixture: code")
    return _git(checkout, "rev-parse", "HEAD")


def log_path(sha, task_id=TASK):
    return f".claude/verify-runs/{task_id}-{sha[:12]}.log"


def hook_cells(sha, task_id=TASK, result=None):
    """`Result | Notes` exactly as the hook writes them for a pass of `sha`. `result` replaces the
    Result cell only (a row-shape variant, e.g. `☑ pass / ☐ N/A`); the Notes stay the hook's."""
    cell, notes = verify_record.row_cells(sha, "pass", SESSION, log_path(sha, task_id))
    return f"{cell if result is None else result} | {notes}"


def hook_row(sha, task_id=TASK, result=None):
    """The whole `| verify | <Result> | <Notes> |` line, with no newline."""
    return f"| verify | {hook_cells(sha, task_id, result)} |"


def write_pass_record(root, sha, task_id=TASK, anchor_dir=None):
    """The hook's run record for a pass of `sha`, under the record directory of `root` (the gate's
    `ROOT`). `anchor_dir` sets `CLAUDE_TRACE_ANCHOR_DIR` for the write only; None keeps the
    environment's (the conftest's temp directory, which a subprocess gate inherits)."""
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    if anchor_dir is not None:
        os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(anchor_dir)
    try:
        return verify_record.write_record(str(root), task_id, sha, "pass", SESSION,
                                          log_path(sha, task_id))
    finally:
        if anchor_dir is not None:
            if saved is None:
                os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
            else:
                os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved


def prove(root, checkout, task_id=TASK, anchor_dir=None):
    """Make a hook row for `checkout`'s head commit true: commit the code (`code_commit`) and write
    the pass record. Returns the commit hash."""
    sha = code_commit(checkout)
    write_pass_record(root, sha, task_id, anchor_dir)
    return sha


def _fixed_code_sha():
    scratch = tempfile.mkdtemp(prefix="t309_code_sha_")
    try:
        return code_commit(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


CODE_SHA = _fixed_code_sha()
HOOK_PASS_ROW = hook_row(CODE_SHA)


# --- T341: the reviewer's `ReviewerDone` trace record ----------------------------------------
#
# Since T341 the merge gate refuses the merge of an extended-track task branch until the trace holds
# a `ReviewerDone` record for the task that names the reviewed commit, with its chain hash and its
# anchor intact. The `SubagentStop` hook `subagent_stop_reviewer_done.py` writes it when a reviewer
# sub-agent ends (option B, AC 11-12); the `Agent` spawn record alone no longer counts. A test whose
# point is something else gives its fixture that record here (`prove_review`), and
# `run_reviewer_done_hook` runs the real hook on a real-shaped `SubagentStop` event.

import json  # noqa: E402

from trace_chain import GENESIS, anchor_path, chain_hash, safe_name  # noqa: E402

REVIEWER_PREFIX = "Review alone, from the repo only:"


def reviewer_summary(task_id, commit, description=None, prefix=REVIEWER_PREFIX, task_line=None,
                     lead=None):
    """`json.dumps(tool_input)[:300]` of the documented reviewer spawn (`post_tool_trace.summarize`).
    `lead` puts extra keys before the documented ones (they then use up the 300 characters)."""
    tool_input = dict(lead or {})
    tool_input.update({
        "subagent_type": "easy-kit:qa-expert",
        "description": f"Reviewer: {task_id}" if description is None else description,
        "prompt": (f"{prefix}\n{task_line or f'Task ID: {task_id}'}\nCommit: {commit}\n"
                   f"Diff: main...{commit}\nGuide: tasks/TASK_GUIDE_{task_id}.md\n"
                   + "Run code-review and security-review; write tasks/TASK_REVIEW_<ID>.md. " * 5),
    })
    return json.dumps(tool_input)[:300]


def reviewer_record(task_id, commit, **overrides):
    """The `Agent` spawn record `post_tool_trace.py` leaves for a reviewer spawn. Since option B it
    is not proof on its own, whatever its `spawn.status`: the negative tests use it."""
    summary_args = {k: overrides.pop(k) for k in ("description", "prefix", "task_line", "lead")
                    if k in overrides}
    record = {"timestamp": "2026-11-20T00:00:00+00:00", "tool_name": "Agent",
              "summary": reviewer_summary(task_id, commit, **summary_args), "is_error": False,
              "spawn": {"resolved_model": "claude-opus-5-5", "status": "completed"}}
    record.update(overrides)
    return record


def append_trace(trace_dir, root, stem, record, anchor=True):
    """Append `record` to `<trace_dir>/<stem>.jsonl` hash-chained, and (with `anchor`) its anchor
    line under `CLAUDE_TRACE_ANCHOR_DIR`, as `post_tool_trace.append_record` does for the gate's
    `ROOT` (`root`). Returns the line number."""
    os.makedirs(str(trace_dir), exist_ok=True)
    path = os.path.join(str(trace_dir), f"{stem}.jsonl")
    lines = open(path, "rb").read().split(b"\n")[:-1] if os.path.exists(path) else []
    prev = GENESIS
    for raw in reversed(lines):
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("hash"), str):
            prev = rec["hash"]
            break
    record = dict(record, prev=prev)
    record["hash"] = chain_hash(record)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    if anchor:
        target = anchor_path(str(root), stem)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "a", encoding="utf-8") as f:
            f.write("%s %d %s\n" % (safe_name(stem, "_untagged"), len(lines) + 1, record["hash"]))
    return len(lines) + 1


REAL_TRACE_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               "..", "..", "..", "memory", "event-trace"))


REVIEWER_AGENT_ID = "a0f1c7d2e3d4b5c6d"


def reviewer_done_record(task_id, commit, **overrides):
    """The `ReviewerDone` record `subagent_stop_reviewer_done.py` writes (before `prev`/`hash`)."""
    record = {"timestamp": "2026-11-20T00:00:00+00:00", "tool_name": "ReviewerDone",
              "task_id": task_id, "commit": commit, "agent_id": REVIEWER_AGENT_ID}
    record.update(overrides)
    return record


def prove_review(trace_dir, root, task_id, commit, stem=None, anchor_dir=None, **overrides):
    """Give `task_id` a valid `ReviewerDone` record for `commit`, filed under `stem` (the task's own
    trace file by default). `anchor_dir` sets `CLAUDE_TRACE_ANCHOR_DIR` for the write only, as in
    `write_pass_record` (a subprocess gate with its own anchor directory). Refuses the real repo's
    `memory/event-trace/`: a fixture passes its own trace directory, never a gate's `TRACE_DIR`
    before the test patched it."""
    if os.path.realpath(str(trace_dir)) == REAL_TRACE_DIR:
        raise RuntimeError(f"refusing to write a fixture reviewer record into {REAL_TRACE_DIR}")
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    if anchor_dir is not None:
        os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(anchor_dir)
    try:
        return append_trace(trace_dir, root, stem or task_id,
                            reviewer_done_record(task_id, commit, **overrides))
    finally:
        if anchor_dir is not None:
            if saved is None:
                os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
            else:
                os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved


# --- T341 option B: the real `SubagentStop` hook on a real-shaped event -------------------------
#
# Field names from a real event captured on Claude Code 2.1.329 (2026-11-20, T341 spike): a
# `general-purpose` sub-agent spawned by `claude -p` with a capture-only `SubagentStop` hook. The
# sub-agent's spawn prompt is the first line of
# `<dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl` (= `agent_transcript_path`),
# a `user` message whose `content` is the prompt string.

SUBAGENT_STOP_HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "subagent_stop_reviewer_done.py")
SPAWN_SESSION = "70f8b176-ebb2-43c4-bfa9-872c2581e11f"


def reviewer_prompt(task_id, commit):
    """The documented reviewer spawn prompt (`docs/claude-md/pipeline-stages.md`, Stage 4 step 0)."""
    return (f"{REVIEWER_PREFIX}\nTask ID: {task_id}\nCommit: {commit}\nDiff: main...{commit}\n"
            f"Guide: tasks/TASK_GUIDE_{task_id}.md\nRun code-review; write tasks/TASK_REVIEW_{task_id}.md.")


def spawn_transcript(base, prompt, agent_id=REVIEWER_AGENT_ID, session_id=SPAWN_SESSION):
    """Write the main transcript and the sub-agent's own transcript under `base`, the sub-agent's
    first line holding `prompt` as the harness writes it. Returns the main `transcript_path`."""
    projects = os.path.join(str(base), "projects", "-fixture")
    agent_dir = os.path.join(projects, session_id, "subagents")
    os.makedirs(agent_dir, exist_ok=True)
    transcript = os.path.join(projects, f"{session_id}.jsonl")
    with open(transcript, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "go"}}) + "\n")
    first = {"parentUuid": None, "isSidechain": True, "agentId": agent_id, "type": "user",
             "message": {"role": "user", "content": prompt}, "sessionId": session_id}
    with open(os.path.join(agent_dir, f"agent-{agent_id}.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(first) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                                                             "content": [{"type": "text", "text": "ok"}]}})
                + "\n")
    return transcript


def subagent_stop_event(transcript, cwd, agent_id=REVIEWER_AGENT_ID, session_id=SPAWN_SESSION,
                        **overrides):
    """A `SubagentStop` hook input with the captured event's exact keys."""
    event = {
        "session_id": session_id, "transcript_path": transcript, "cwd": str(cwd),
        "prompt_id": "d0262379-ea67-404d-ba5f-67fd5cacaf13", "permission_mode": "auto",
        "agent_id": agent_id, "agent_type": "qa-expert", "effort": {"level": "medium"},
        "hook_event_name": "SubagentStop", "stop_hook_active": False,
        "agent_transcript_path": os.path.join(os.path.dirname(transcript), session_id, "subagents",
                                              f"agent-{agent_id}.jsonl"),
        "background_tasks": [], "session_crons": [],
    }
    event.update(overrides)
    return event


def run_reviewer_done_hook(project, event, anchor_dir, raw=None):
    """Run the real hook as the harness does: `event` (or `raw` text) on stdin, the project in
    `CLAUDE_PROJECT_DIR`. Refuses the real repo's trace. Returns the finished process."""
    if os.path.realpath(os.path.join(str(project), "memory", "event-trace")) == REAL_TRACE_DIR:
        raise RuntimeError(f"refusing to run the reviewer hook against {REAL_TRACE_DIR}")
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_ACTIVE_TASK")}
    env.update({"CLAUDE_PROJECT_DIR": str(project), "CLAUDE_TRACE_ANCHOR_DIR": str(anchor_dir)})
    return subprocess.run([sys.executable, SUBAGENT_STOP_HOOK], input=json.dumps(event) if raw is None
                          else raw, capture_output=True, text=True, timeout=30, env=env)
