"""T292: the hooks have one `parse_ts`, in `lib/auto_mode.py`.

TABLE holds the answers both copies gave before T292 (characterized first, see
tasks/TASK_REVIEW_T292.md). The tests check that the one copy still gives them and that no second
copy exists. `stop_auto_mode_check.py` runs `main()` at import, so it is read with `ast`, never imported.
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


DEF = "def " + "parse_ts"   # built here so this file never holds the literal itself


def read_tree(path):
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def same(a, b):
    return a == b and repr(a) == repr(b)


@pytest.mark.parametrize("value,expected", TABLE, ids=IDS)
def test_ac2_the_one_copy_gives_the_table_answer(value, expected):
    import auto_mode
    assert same(auto_mode.parse_ts(value), expected)


@pytest.mark.parametrize("value,expected", TABLE, ids=IDS)
def test_ac2_session_work_gives_the_table_answer_through_the_one_copy(value, expected):
    import session_work
    assert same(session_work.parse_ts(value), expected)


def test_ac2_session_work_uses_the_one_copy_not_its_own():
    import auto_mode
    import session_work
    assert session_work.parse_ts is auto_mode.parse_ts


def test_ac2_stop_auto_mode_check_binds_the_one_copy():
    """`parse_ts = am.parse_ts` at module level, and no def of its own."""
    body = read_tree(STOP).body
    assert not [n for n in body if isinstance(n, ast.FunctionDef) and n.name == "parse_ts"]
    binds = [n for n in body if isinstance(n, ast.Assign)
             and [t.id for t in n.targets if isinstance(t, ast.Name)] == ["parse_ts"]
             and ast.unparse(n.value) == "am.parse_ts"]
    assert len(binds) == 1


def test_ac2_ac4_exactly_one_parse_ts_def_under_the_hooks():
    hits = []
    for root, _dirs, files in os.walk(HOOKS):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    hits += [(path, n) for n, line in enumerate(f, 1) if line.lstrip().startswith(DEF)]
    assert [os.path.relpath(p, HOOKS) for p, _ in hits] == [os.path.join("lib", "auto_mode.py")]
