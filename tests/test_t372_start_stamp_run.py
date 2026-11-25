"""T372 AC 4 — `stop_auto_verify.py --start <ID>` stamps the run record with the session that
started it (`started_by`, from `CLAUDE_CODE_SESSION_ID`) and when (`started_at`); a Stop-hook run
and a `--start` with no usable session id write no stamp.

Every test stubs `claude` (`tests/test_auto_verify.py` fixtures); the real binary is never run.
Run with: python3 -m pytest tests/test_t372_start_stamp_run.py -q -p no:cacheprovider
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_auto_verify import (  # noqa: E402
    HOOK, TASK, _env, _git, _lib, _project, _stop, _stub, _wait_row)

SID = "aaaaaaaa-1111-2222-3333-444444444444"


def _start(project, env):
    return subprocess.run([sys.executable, str(project / ".claude" / "hooks" / HOOK), "--start", TASK],
                          capture_output=True, text=True, cwd=project, env=env, timeout=30)


def _record(project, env):
    head = _git(project, "rev-parse", "HEAD")
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = env["CLAUDE_TRACE_ANCHOR_DIR"]
    try:
        return _lib().read_record(str(project), TASK, head)
    finally:
        if saved is None:
            del os.environ["CLAUDE_TRACE_ANCHOR_DIR"]
        else:
            os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved


def test_ac4_start_stamps_the_starting_session_and_time(tmp_path):
    project, checkout = _project(tmp_path)
    stub_dir, _ = _stub(tmp_path)
    env = _env(tmp_path, project, stub_dir, CLAUDE_CODE_SESSION_ID=SID)
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    result = _start(project, env)
    assert result.returncode == 0, result
    _wait_row(checkout)
    record = _record(project, env)
    assert record["verdict"] == "pass" and record["started_by"] == SID
    started = datetime.fromisoformat(record["started_at"])
    assert before <= started <= datetime.now(timezone.utc)


@pytest.mark.parametrize("value", [None, "", "not a session id!", "a/../b"])
def test_ac4_start_with_no_usable_session_id_writes_no_stamp(tmp_path, value):
    project, checkout = _project(tmp_path)
    stub_dir, _ = _stub(tmp_path)
    extra = {} if value is None else {"CLAUDE_CODE_SESSION_ID": value}
    env = _env(tmp_path, project, stub_dir, **extra)
    assert _start(project, env).returncode == 0
    _wait_row(checkout)
    record = _record(project, env)
    assert record["verdict"] == "pass"
    assert "started_by" not in record and "started_at" not in record


def test_ac4_a_stop_hook_run_writes_no_stamp(tmp_path):
    project, checkout = _project(tmp_path)
    stub_dir, _ = _stub(tmp_path)
    env = _env(tmp_path, project, stub_dir, CLAUDE_CODE_SESSION_ID=SID)
    _stop(project, env)
    _wait_row(checkout)
    record = _record(project, env)
    assert record["verdict"] == "pass"
    assert "started_by" not in record and "started_at" not in record
