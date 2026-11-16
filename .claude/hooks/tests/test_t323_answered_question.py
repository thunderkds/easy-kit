#!/usr/bin/env python3
"""T323 — LOCKED ORACLE (written first by qa-expert; the implementer may not edit it).

A short "yes [admin]" that answers the Supervisor's immediately preceding visible question, when
that question names exactly one task, binds that task for the merge gate (`tasks/TASK_GUIDE_T323.md`,
AC 1-6, AC 8, Success Criteria 1-2).

Every case drives the gate's real entry: the hook's `main()` through `test_admin_tag.reason` (a
session `[admin]` / `[ticket]` tag, which any typed `[admin]` request sets), or `admin_refusal`
directly with `tag=None` (the per-request `[admin]` path). The request is dated after the guide's
commit (`ASK_AT`), and the transcript holds no `--start` call, so the request binding and the
loop binding cannot hold: only the answered question can bind. The tests assert behaviour only
(allowed vs refused, the task named, the AC 6 hint); they do not pin a helper name.

Run with: python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q -p no:cacheprovider
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import (  # noqa: E402
    GUIDE_VACATED, MERGE, PUSH, gate, git, kanban, merge_gate)
from test_admin_tag import (  # noqa: E402
    SID, auto_verified, human, publish, reason, transcript, _ts)

import auto_mode as am  # noqa: E402

assert gate  # the fixture, imported for pytest

ASK_AT = +60  # the question and the yes: after every fixture commit (no guide added after them)
BRANCH = "feat/t900-x"
T322_QUESTION = "Do you want me to merge `feat/t900-x` into `main`?"
HINT = ("a bare yes binds only when the Supervisor's last message asked about exactly one task; "
        "else reply with the task ID and `[admin]`")


# ── transcript entries (shapes as in test_admin_tag.py; invented content) ───────────────────
def said(*blocks, offset_s=ASK_AT - 10, **extra):
    """An assistant transcript entry holding `blocks` (a str is one `text` block)."""
    content = [{"type": "text", "text": b} if isinstance(b, str) else b for b in blocks]
    entry = {"type": "assistant", "timestamp": _ts(offset_s), "sessionId": SID,
             "isSidechain": False, "message": {"role": "assistant", "content": content}}
    entry.update(extra)
    return entry


def thinking(text):
    return {"type": "thinking", "thinking": text, "signature": "x"}


def tool_use(command):
    return {"type": "tool_use", "id": "q1", "name": "Bash", "input": {"command": command}}


def answer(text="yes [admin]", offset_s=ASK_AT):
    return human(text, offset_s)


def asked(tmp_path, question=T322_QUESTION, reply="yes [admin]", between=()):
    """The T322 shape: the Supervisor's question, then the user's short reply."""
    q = said(question) if isinstance(question, str) else question
    return transcript(tmp_path, [q] + list(between) + [answer(reply)])


def _flat(text):
    return re.sub(r"\s+", " ", text or "")


def refused_unbound(text, task="T900"):
    """The binding refusal: present, names the task, carries the AC 6 hint."""
    assert text is not None, "allowed, but the task must not bind"
    assert task in text and "not the task" in text, text
    assert HINT in _flat(text), text


@pytest.fixture
def verified(gate):
    """T900 in Ready for Review, a committed hook-written pass row and its run record, `origin`."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    return fx


def direct(fx, path, command=MERGE + " " + BRANCH, cwd=None, tag=None):
    """The gate's `admin_refusal` with the per-request `[admin]` (or `tag`) read from `path`."""
    if tag is None:
        request = am.admin_request(path)  # `(timestamp, text)`, as `auto_mode_blocker` passes it
    else:
        found = am.session_request(path)
        request = found[1:] if found is not None and found[0] == tag else None
    assert request is not None, "the fixture's request must carry the tag"
    return merge_gate.admin_refusal(command, cwd or fx.main, path, request, tag=tag)


# ── AC 1 / Success Criterion 1 — the T322 transcript shape binds ────────────────────────────
def test_sc1_the_t322_shape_binds_the_merge_under_the_admin_tag(verified, tmp_path):
    assert reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path)) is None


def test_sc1_the_t322_shape_binds_on_the_per_request_admin_path(verified, tmp_path):
    assert direct(verified, asked(tmp_path)) is None


def test_ac1_the_answered_question_binds_the_task_branch_push(verified, tmp_path):
    path = asked(tmp_path, question="Shall I push `feat/t900-x` to `origin`?")
    assert reason(PUSH + " origin " + BRANCH, verified.wt, path) is None


@pytest.mark.parametrize("question", [
    "Merge T900 into `main`?",
    "T900 passed its auto verify.\n\nDo you want me to merge `feat/t900-x` into `main`?\n\n",
], ids=["by-id", "preamble-and-trailing-blank-lines"])
def test_ac4_a_question_naming_the_task_by_id_or_branch_binds(verified, tmp_path, question):
    assert reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)) is None


@pytest.mark.parametrize("reply", ["yes [admin]", "Yes. [admin]", "yes! [admin]", "[admin] yes",
                                   "OK [admin]", "okay [admin]", "sure [admin]", "go ahead [admin]",
                                   "do it [admin]", "merge it [admin]", "y [admin]"])
def test_ac2_each_short_yes_binds(verified, tmp_path, reply):
    assert reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, reply=reply)) is None


def test_edge_split_entries_the_newest_text_entry_is_the_question(verified, tmp_path):
    """One assistant entry per content block: a later tool-only entry is not the question."""
    path = asked(tmp_path, between=[said(tool_use("git status"), offset_s=ASK_AT - 5)])
    assert reason(MERGE + " " + BRANCH, verified.main, path) is None


# ── AC 2 — only a bare yes ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("reply", [
    "yes and push it too [admin]",
    "yes please, merge it now [admin]",
    "yes. Then run the release. [admin]",
    "no [admin]",
    "not yet [admin]",
    "don't [admin]",
    "yes T901 [admin]",
    "`yes` [admin]",
    "> yes\n[admin]",
    "yes" + "!" * 45 + " [admin]",
], ids=["extra-words", "extra-words-comma", "second-sentence", "no", "not-yet", "dont", "other-id",
        "code-span", "quoted-line", "over-40-chars"])
def test_ac2_a_reply_that_is_not_only_a_short_yes_does_not_bind(verified, tmp_path, reply):
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, reply=reply)))


def test_ac2_extra_words_do_not_bind_on_the_per_request_path(verified, tmp_path):
    text = direct(verified, asked(tmp_path, reply="yes and push it too [admin]"))
    refused_unbound(text)


# ── AC 4 — the question names exactly one task, and asks ────────────────────────────────────
def test_ac4_two_ids_in_the_question_do_not_bind(verified, tmp_path):
    path = asked(tmp_path, "Do you want me to merge `feat/t900-x` and then T901 into `main`?")
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


def test_ac4_a_negated_id_does_not_count_as_named(verified, tmp_path):
    path = asked(tmp_path, "T900 is not ready to merge yet, so shall I wait?")
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


@pytest.mark.parametrize("question", [
    "I will merge `feat/t900-x` into `main`.",
    "Merge `feat/t900-x` into `main`? I will wait for your reply.",
    "Shall I merge `feat/t900-x` into `main`?\n\nI will wait for your reply.",
], ids=["statement", "question-then-statement", "question-then-statement-line"])
def test_ac4_a_question_not_ending_in_a_question_mark_does_not_bind(verified, tmp_path, question):
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)))


def test_ac4_a_question_naming_t901_does_not_bind_the_merge_of_t900(verified, tmp_path):
    path = asked(tmp_path, "Do you want me to merge `feat/t901-y` into `main`?")
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


def test_ac4_a_question_naming_no_task_does_not_bind(verified, tmp_path):
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, "Shall I merge it?")))


# ── AC 3 — only what the user saw, in the message directly before the reply ────────────────
def test_ac3_an_id_only_in_thinking_does_not_bind(verified, tmp_path):
    question = said(thinking("I should merge feat/t900-x (T900) next."), "Shall I go ahead?")
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)))


def test_ac3_an_id_only_in_tool_use_input_does_not_bind(verified, tmp_path):
    question = said(tool_use("git log feat/t900-x -1"), "Shall I go ahead?")
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)))


def test_ac3_an_id_only_in_a_tool_result_does_not_bind(verified, tmp_path):
    result = {"type": "user", "timestamp": _ts(ASK_AT - 5), "sessionId": SID,
              "origin": {"kind": "human"},
              "message": {"role": "user", "content": [
                  {"type": "tool_result", "tool_use_id": "q1", "content": "feat/t900-x T900"}]}}
    path = asked(tmp_path, said("Shall I go ahead?", offset_s=ASK_AT - 10), between=[result])
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


def test_ac3_a_sidechain_assistant_entry_is_not_the_question(verified, tmp_path):
    question = said(T322_QUESTION, isSidechain=True)
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)))


def test_ac3_a_human_request_between_question_and_yes_does_not_bind(verified, tmp_path):
    path = asked(tmp_path, between=[human("hmm, what changed in it?", ASK_AT - 5)])
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


def test_ac3_an_older_assistant_message_is_not_read(verified, tmp_path):
    path = asked(tmp_path, between=[said("All checks are done.", offset_s=ASK_AT - 5)])
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


def test_edge_a_compact_summary_between_question_and_yes_does_not_bind(verified, tmp_path):
    summary = {"type": "user", "isCompactSummary": True, "timestamp": _ts(ASK_AT - 5),
               "sessionId": SID, "message": {"role": "user", "content":
                                             "This session is being continued. Merge T900?"}}
    path = asked(tmp_path, between=[summary])
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


# ── AC 5 — nothing else loosened ────────────────────────────────────────────────────────────
def test_ac5_a_session_tag_needs_the_row_in_ready_for_review(gate, tmp_path):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    refused_unbound(reason(MERGE + " " + BRANCH, fx.main, asked(tmp_path)))


def test_ac5_the_answered_task_still_needs_its_committed_auto_verify(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    fx.task_file("TASK_GUIDE_T900.md", GUIDE_VACATED.format(tid="T900"), commit=True)
    publish(fx)
    text = reason(MERGE + " " + BRANCH, fx.main, asked(tmp_path))
    # The binding holds (no "not the task"); the verify-row check refuses.
    assert text is not None and "not the task" not in text, text
    assert "T900 has no passed auto verify committed" in text, text


def test_ac5_one_task_per_command_still_holds(verified, tmp_path):
    git(verified.main, "branch", "feat/t901-y")
    text = reason(MERGE + " " + BRANCH + " feat/t901-y", verified.main, asked(tmp_path))
    assert text is not None, "an octopus merge must stay refused"


def test_ac5_force_push_stays_refused(verified, tmp_path):
    path = asked(tmp_path, question="Shall I push `feat/t900-x` to `origin`?")
    assert reason(PUSH + " --force origin " + BRANCH, verified.wt, path) is not None


# ── AC 1 — `[ticket]` never binds by the answered question ──────────────────────────────────
def test_ac1_ticket_does_not_bind_by_the_answered_question(verified, tmp_path):
    path = asked(tmp_path, question="Shall I push `feat/t900-x` to `origin`?", reply="yes [ticket]")
    text = reason(PUSH + " origin " + BRANCH, verified.wt, path)
    assert text is not None and "T900" in text and "[ticket]" in text, text


def test_ac1_ticket_does_not_bind_on_the_direct_path(verified, tmp_path):
    path = asked(tmp_path, question="Shall I push `feat/t900-x` to `origin`?", reply="yes [ticket]")
    text = direct(verified, path, PUSH + " origin " + BRANCH, verified.wt, tag="ticket")
    assert text is not None and "T900" in text, text


# ── AC 6 — fail closed ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("question", [
    {"type": "assistant", "timestamp": _ts(ASK_AT - 10), "sessionId": SID, "message": None},
    {"type": "assistant", "timestamp": _ts(ASK_AT - 10), "sessionId": SID,
     "message": {"role": "assistant", "content": {"type": "text", "text": T322_QUESTION}}},
    {"type": "assistant", "timestamp": _ts(ASK_AT - 10), "sessionId": SID,
     "message": {"role": "assistant", "content": [{"type": "text", "text": 900}]}},
    {"type": "assistant", "timestamp": _ts(ASK_AT - 10), "sessionId": SID,
     "message": {"role": "assistant", "content": [{"type": "text"}]}},
], ids=["message-null", "content-dict", "text-not-str", "text-missing"])
def test_ac6_a_malformed_question_entry_is_refused(verified, tmp_path, question):
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, asked(tmp_path, question)))


def test_ac6_a_question_line_that_is_not_json_is_refused(verified, tmp_path):
    path = asked(tmp_path, said("placeholder"))
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    lines[0] = '{"type": "assistant", "message": {"content": [{"type": "text", "text": "' \
               + T322_QUESTION + '"}\n'  # truncated JSON
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))


@pytest.mark.parametrize("bad", [None, "", "relative.jsonl", "/nonexistent/t323.jsonl"])
def test_ac6_an_unreadable_transcript_is_refused_on_the_direct_path(verified, tmp_path, bad):
    request = (am.parse_ts(_ts(ASK_AT)), "yes [admin]")
    text = merge_gate.admin_refusal(MERGE + " " + BRANCH, verified.main, bad, request, tag=None)
    assert text is not None and "T900" in text, text


# ── regression: the existing request binding is unchanged ───────────────────────────────────
def test_regression_a_request_naming_the_id_still_binds(verified, tmp_path):
    path = transcript(tmp_path, [answer("merge T900 [admin]")])
    assert reason(MERGE + " " + BRANCH, verified.main, path) is None


def test_regression_ticket_naming_the_id_still_does_not_bind(verified, tmp_path):
    path = transcript(tmp_path, [answer("push T900 [ticket]")])
    text = reason(PUSH + " origin " + BRANCH, verified.wt, path)
    assert text is not None and "T900" in text, text


def test_regression_a_plain_yes_with_no_question_does_not_bind(verified, tmp_path):
    path = transcript(tmp_path, [answer("yes [admin]")])
    refused_unbound(reason(MERGE + " " + BRANCH, verified.main, path))
