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
        _git(checkout, "init", "-q")
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
