#!/usr/bin/env python3
"""T247 locked oracle: an interrupt entry or a slash-command entry does not close the Stop
check's `[auto]` span (`stop_auto_mode_check.py` `auto_windows`).

Before T247 the Stop check read `[Request interrupted by user]` and `<command-name>/compact…`
as untagged requests, so each one closed the `[auto]` span (T229 verify step 6). The merge
gate's own reading (`lib/auto_mode.py` `request_text`) stays as it is (AC 5).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t247_auto_span_entries.py -q -p no:cacheprovider
"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOOKS / "lib"))
sys.path.insert(0, str(HOOKS))
import auto_mode  # noqa: E402

_spec = importlib.util.spec_from_file_location("stop_auto_mode_check_t247",
                                               HOOKS / "stop_auto_mode_check.py")
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

T0, T1, T2 = ("2026-11-25T01:00:00Z", "2026-11-25T01:05:00Z", "2026-11-25T01:10:00Z")


def ts(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def user(content, when):
    return {"type": "user", "timestamp": when, "message": {"role": "user", "content": content}}


def text_blocks(text):
    return [{"type": "text", "text": text}]


def transcript(tmp_path, *entries):
    path = tmp_path / "t.jsonl"
    path.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    return str(path)


INTERRUPT = "[Request interrupted by user]"
INTERRUPT_TOOL = "[Request interrupted by user for tool use]"
COMPACT_NAME_FIRST = ("<command-name>/compact</command-name>\n"
                      "<command-message>compact</command-message>\n<command-args></command-args>")
COMPACT_MESSAGE_FIRST = ("<command-message>compact</command-message>\n"
                         "<command-name>/compact</command-name>\n<command-args></command-args>")

NOT_REQUESTS = [
    pytest.param(INTERRUPT, id="ac1-interrupt-string"),
    pytest.param(text_blocks(INTERRUPT), id="ac1-interrupt-list"),
    pytest.param(text_blocks(INTERRUPT_TOOL), id="ac2-interrupt-for-tool-use-list"),
    pytest.param(INTERRUPT_TOOL, id="ac2-interrupt-for-tool-use-string"),
    pytest.param(COMPACT_NAME_FIRST, id="ac3-command-name-first-string"),
    pytest.param(text_blocks(COMPACT_MESSAGE_FIRST), id="ac3-command-message-first-list"),
    pytest.param("  " + COMPACT_NAME_FIRST, id="ac3-leading-space"),
]


@pytest.mark.parametrize("content", NOT_REQUESTS)
def test_entry_does_not_close_the_auto_span(tmp_path, content):
    path = transcript(tmp_path, user("do the work [auto]", T0), user(content, T1))
    assert hook.auto_windows(path) == [(ts(T0), None)]


@pytest.mark.parametrize("content", NOT_REQUESTS)
def test_entry_does_not_open_an_auto_span(tmp_path, content):
    path = transcript(tmp_path, user(content, T0))
    assert hook.auto_windows(path) == []


def test_ac4_an_ordinary_untagged_request_still_closes_the_span(tmp_path):
    path = transcript(tmp_path, user("do the work [auto]", T0), user(INTERRUPT, T1),
                      user("now something else", T2))
    assert hook.auto_windows(path) == [(ts(T0), ts(T2))]


def test_ac4_a_request_that_quotes_the_interrupt_text_is_still_a_request(tmp_path):
    path = transcript(tmp_path, user("do the work [auto]", T0),
                      user(f"why did I see {INTERRUPT} there?", T1))
    assert hook.auto_windows(path) == [(ts(T0), ts(T1))]


@pytest.mark.parametrize("content", [INTERRUPT, text_blocks(INTERRUPT_TOOL), COMPACT_NAME_FIRST,
                                     text_blocks(COMPACT_MESSAGE_FIRST)])
def test_ac5_the_gate_reading_is_unchanged(content):
    entry = user(content, T0)
    expected = content if isinstance(content, str) else content[0]["text"]
    assert auto_mode.request_text(entry) == expected
