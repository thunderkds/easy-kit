"""T292: the hooks have one `parse_ts`, in `lib/auto_mode.py`.

Stage 1 (characterization): both old copies give the same answer for every input of TABLE.
`stop_auto_mode_check.py` runs `main()` at import, so its copy is loaded with `ast`, never imported.
"""
import ast
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

HOOKS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(HOOKS, "lib"))
STOP = os.path.join(HOOKS, "stop_auto_mode_check.py")

UTC = timezone.utc
# (input, expected) — the outputs of the two copies before T292 (see tasks/TASK_REVIEW_T292.md).
TABLE = [
    ("2026-11-04T06:05:12+00:00", datetime(2026, 11, 4, 6, 5, 12, tzinfo=UTC)),
    ("2026-11-04T06:05:12+07:00", datetime(2026, 11, 4, 6, 5, 12, tzinfo=timezone(timedelta(hours=7)))),
    ("2026-11-04T06:05:12", datetime(2026, 11, 4, 6, 5, 12, tzinfo=UTC)),          # naive -> UTC
    ("2026-11-04T06:05:12Z", datetime(2026, 11, 4, 6, 5, 12, tzinfo=UTC)),
    ("2026-11-04T06:05:12.123456Z", datetime(2026, 11, 4, 6, 5, 12, 123456, tzinfo=UTC)),
    ("2026-11-04T06:05:12.5", datetime(2026, 11, 4, 6, 5, 12, 500000, tzinfo=UTC)),
    ("2026-11-04", datetime(2026, 11, 4, tzinfo=UTC)),
    ("2026-11-04T06:05:12z", None),
    (" 2026-11-04T06:05:12Z", None),
    ("", None),
    (None, None),
    (0, None),
    (1.5, None),
    ([], None),
    ({}, None),
    (b"2026-11-04T06:05:12Z", None),
    ("not a time", None),
    ("2026-13-45T00:00:00Z", None),
    (datetime(2026, 11, 4, 6, 5, 12), datetime(2026, 11, 4, 6, 5, 12, tzinfo=UTC)),  # str() of a naive datetime
    (datetime(2026, 11, 4, tzinfo=UTC), datetime(2026, 11, 4, tzinfo=UTC)),
]
IDS = [repr(v) for v, _ in TABLE]


def stop_copy():
    """The `parse_ts` def of `stop_auto_mode_check.py`, run in its own namespace."""
    with open(STOP, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "parse_ts")
    ns = {"datetime": datetime, "timezone": timezone}
    exec(compile(ast.Module([fn], []), STOP, "exec"), ns)
    return ns["parse_ts"]


def same(a, b):
    return a == b and repr(a) == repr(b)


@pytest.mark.parametrize("value,expected", TABLE, ids=IDS)
def test_ac1_old_stop_copy_gives_the_table_answer(value, expected):
    assert same(stop_copy()(value), expected)


@pytest.mark.parametrize("value,expected", TABLE, ids=IDS)
def test_ac1_old_session_work_copy_gives_the_table_answer(value, expected):
    import session_work
    assert same(session_work.parse_ts(value), expected)
