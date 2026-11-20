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


# --- T341: a reviewer spawn's trace record, the way `post_tool_trace.py` writes it -------------
#
# Since T341 the merge gate refuses the merge of an extended-track task branch until the trace holds
# a `Reviewer: <ID>` `Agent` record that names the reviewed commit, with its chain hash and its
# anchor intact. A test whose point is something else gives its fixture that record here.

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
    """The trace record a finished foreground reviewer spawn leaves (`spawn.status: completed`)."""
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


def prove_review(trace_dir, root, task_id, commit, stem=None, anchor_dir=None, **overrides):
    """Give `task_id` a valid reviewer record for `commit`, filed under `stem` (the task's own trace
    file by default). `anchor_dir` sets `CLAUDE_TRACE_ANCHOR_DIR` for the write only, as in
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
                            reviewer_record(task_id, commit, **overrides))
    finally:
        if anchor_dir is not None:
            if saved is None:
                os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
            else:
                os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved
