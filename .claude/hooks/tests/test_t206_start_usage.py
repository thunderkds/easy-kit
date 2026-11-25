#!/usr/bin/env python3
"""T206 — a bare or extra-arg `stop_auto_verify.py --start` exits 2 with one usage line.

`--start` with no task ID, or with more than one argument after it, must never reach `stop_hook()`:
it prints `usage: stop_auto_verify.py --start <TASK_ID>` to stderr and exits 2, starting no run.
`--start <ID>` (exactly one argument) still goes to `start_one()`.

Safety: every subprocess sets CLAUDE_AUTO_VERIFY_RUN=1 (the child guard). With that guard set the
script never calls `stop_hook()` or starts a run, so no real `claude` is launched by these tests.
Run with: python3 -B -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = Path(HERE).resolve().parents[2]
HOOK = str(REPO / ".claude" / "hooks" / "stop_auto_verify.py")
CHILD_ENV = "CLAUDE_AUTO_VERIFY_RUN"
USAGE = "usage: stop_auto_verify.py --start <TASK_ID>"


def run_hook(*args):
    env = dict(os.environ)
    env[CHILD_ENV] = "1"  # stub: no run can start from this subprocess
    env.pop("CLAUDE_PROJECT_DIR", None)
    return subprocess.run([sys.executable, "-B", HOOK, *args], cwd=str(REPO), env=env,
                          capture_output=True, text=True, timeout=60)


def test_bare_start_exits_2_with_usage():
    result = run_hook("--start")
    assert result.returncode == 2
    assert result.stderr.strip() == USAGE
    assert result.stdout == ""


def test_start_with_two_args_exits_2_with_usage():
    result = run_hook("--start", "T001", "extra")
    assert result.returncode == 2
    assert result.stderr.strip() == USAGE
    assert result.stdout == ""


def test_start_with_three_args_exits_2_with_usage():
    result = run_hook("--start", "T001", "extra", "more")
    assert result.returncode == 2
    assert result.stderr.strip() == USAGE
    assert result.stdout == ""


def test_start_with_one_id_still_reaches_start_one():
    # With the child guard set, start_one() answers before any run; the exit code is 1, not 2.
    result = run_hook("--start", "T001")
    assert result.returncode == 1
    assert "inside an auto verify run" in result.stdout
    assert "usage:" not in result.stderr
