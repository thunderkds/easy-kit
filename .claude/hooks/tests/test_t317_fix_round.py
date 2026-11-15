#!/usr/bin/env python3
"""T317 — Stage 4 fix-round locked oracle (qa-expert, written before the fix).

Spec: `tasks/TASK_GUIDE_T317.md` `## Supervisor decisions during Stage 3`, decision 3 (R1–R6).
The implementer may not edit this file.

  * R1 — the loop binding of a session tag needs this session's own Bash call
    `python3 .claude/hooks/stop_auto_verify.py --start <ID>`, dated after the tag request, plus a
    hook pass record for that run. A record's file time alone never binds (the T284 P1 shape:
    `touch <guide>` and a fresh record). The bound task's own row must be In Progress or Ready for
    Review (R4): a Done or Todo row does not bind, under `[ticket]` and under a loop `[admin]`.
  * R2 — the resume mark lives under the anchors base (`$CLAUDE_TRACE_ANCHOR_DIR`, else
    `~/.claude/harness-anchors`), in the run records' `<base>/<repo slug>/` folder, which the
    settings deny rules already cover. Deleting the old `.claude/hooks/.state/resume_at.d/<sid>` path
    does not revive the tag. `### Session tags` has a Known limits line: an install whose settings
    lack the `SessionStart` entry keeps tags across a resume.
  * R3 — `### Admin tag` merge rule 1 points at `### Session tags`; no unqualified "A later request
    without the tag ends it". `AUTO_MODE_LIMIT`'s `[admin]` sentence and the
    `stop_auto_mode_check.py` docstring mention the session tag.
  * R5 — `[admin]` and `[stop]` in one request: the per-request `[admin]` allowance does not apply.
  * R6 — a ready ticket is "not claimed by another live session"; no sentence calls a Todo row
    "In Progress".

Every board, guide, transcript and git repo here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t317_fix_round.py -q -p no:cacheprovider
"""
import ast
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, kanban, merge_gate  # noqa: E402
from test_admin_tag import SID, auto_verified, bash, human, reason, transcript  # noqa: E402
from test_t317_loop_binding import BRANCH, TAG_AT, pass_written_at, spawn  # noqa: E402

import auto_mode as am  # noqa: E402
from trace_chain import repo_slug  # noqa: E402

assert gate  # the fixture, imported for pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HOOKS_DIR = os.path.join(ROOT, ".claude", "hooks")
TRACKS = os.path.join(ROOT, "docs", "claude-md", "tracks.md")
RESUME_HOOK = os.path.join(HOOKS_DIR, "session_start_resume_mark.py")
STOP_CHECK = os.path.join(HOOKS_DIR, "stop_auto_mode_check.py")
START = "python3 .claude/hooks/stop_auto_verify.py --start {tid}"
OLD_MARK = os.path.join(".claude", "hooks", ".state", "resume_at.d")
ROW = "- [ ] **{tid}** — fixture {tid} | agent | C1 | Risk: Low | P1\n"


def _section(heading):
    with open(TRACKS, encoding="utf-8") as f:
        text = f.read()
    start = text.index("\n" + heading + "\n")
    end = text.find("\n### ", start + len(heading) + 2)
    return text[start:end if end != -1 else len(text)]


def _sentences(text):
    return [s for s in re.split(r"(?<=[.:])\s+", re.sub(r"\s+", " ", text)) if s]


def _gate_case(fx, tag):
    """(command, cwd) of the session tag's own gated action: a merge for admin, a push for ticket."""
    return (MERGE + " " + BRANCH, fx.main) if tag == "admin" else (PUSH + " origin " + BRANCH, fx.wt)


# ══ R1 — a record's file time alone never binds; this session's own `--start` call does ═════════
AFTER = 60  # the tag request: after every fixture commit, so the request binding cannot hold


def _p1(tmp_path, fx, tag, extra=()):
    """The T284 P1 transcript: an untargeted tag request, then `touch <guide>`."""
    guide = os.path.join(fx.main, "tasks", "TASK_GUIDE_T900.md")
    return transcript(tmp_path, [human(f"fix the typo in README [{tag}]", AFTER),
                                 bash("touch " + guide, fx.main, AFTER + 30)] + list(extra))


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_r1_touch_guide_and_a_fresh_pass_record_do_not_bind(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, AFTER + 60)  # written after the request, but no `--start` call of ours
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _p1(tmp_path, fx, tag))
    assert text is not None, f"[{tag}] bound T900 by a record's file time alone"
    assert f"[{tag}]" in text, text


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_r1_own_start_call_after_the_request_plus_its_pass_record_binds(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, AFTER + 60)
    path = _p1(tmp_path, fx, tag, extra=[bash(START.format(tid="T900"), fx.main, AFTER + 40)])
    command, cwd = _gate_case(fx, tag)
    assert reason(command, cwd, path) is None


@pytest.mark.parametrize("case", ["start-before-request", "start-for-another-task",
                                  "start-only-echoed", "start-in-agent-prompt",
                                  "record-before-start"])
def test_r1_a_start_call_that_is_not_this_runs_own_does_not_bind(gate, tmp_path, case):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    record_at, start_at, command = AFTER + 60, AFTER + 40, START.format(tid="T900")
    if case == "start-before-request":
        start_at = AFTER - 30
    elif case == "start-for-another-task":
        command = START.format(tid="T901")
    elif case == "start-only-echoed":
        command = "echo '" + command + "'"
    elif case == "record-before-start":
        record_at = AFTER + 10  # after the request, before the run started: not that run's record
    pass_written_at(fx, record_at)
    if case == "start-in-agent-prompt":
        call = {"type": "assistant", "timestamp": (bash("x", fx.main, start_at))["timestamp"],
                "sessionId": SID, "message": {"role": "assistant", "content": [{
                    "type": "tool_use", "id": "a2", "name": "Agent",
                    "input": {"prompt": "Task ID: T900\nrun " + command}}]}}
    else:
        call = bash(command, fx.main, start_at)
    text = reason(MERGE + " " + BRANCH, fx.main, _p1(tmp_path, fx, "admin", extra=[call]))
    assert text is not None and "[admin]" in text, (case, text)


def _todo(tid):
    return kanban().replace("### Todo\n\n", "### Todo\n" + ROW.format(tid=tid) + "\n")


def _loop(tmp_path, tag):
    return transcript(tmp_path, [human(f"run the board [{tag}]", TAG_AT), spawn("T900", TAG_AT + 10),
                                 bash(START.format(tid="T900"), "/", TAG_AT + 20)])


@pytest.mark.parametrize("tag", ["admin", "ticket"])
def test_r4_control_a_ready_row_with_its_own_run_binds(gate, tmp_path, tag):
    """The control for the Done / Todo rows below (an In Progress row is blocked by the pipeline gate
    before any tag rule, so Ready for Review is the open row the gate can allow)."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    command, cwd = _gate_case(fx, tag)
    assert reason(command, cwd, _loop(tmp_path, tag)) is None


@pytest.mark.parametrize("tag", ["admin", "ticket"])
@pytest.mark.parametrize("row", ["done", "todo"])
def test_r4_a_done_or_todo_row_does_not_bind_the_loop(gate, tmp_path, tag, row):
    fx = gate(kanban(done=("T900",)) if row == "done" else _todo("T900"))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    command, cwd = _gate_case(fx, tag)
    text = reason(command, cwd, _loop(tmp_path, tag))
    assert text is not None and f"[{tag}]" in text, (row, text)


# ══ R2 — the resume mark lives under the anchors base ═══════════════════════════════════════════
@pytest.fixture
def project(tmp_path, monkeypatch):
    proj = tmp_path / "proj"
    (proj / "tasks").mkdir(parents=True)
    (proj / "PROJECT_KANBAN.md").write_text(kanban(), encoding="utf-8")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(proj))
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", str(tmp_path / "anchors"))
    return str(proj)


def test_r2_the_mark_path_is_in_the_run_records_folder_of_the_anchor_base(project, tmp_path):
    path = am.resume_mark_path(SID)
    assert path is not None
    base = os.path.join(str(tmp_path / "anchors"), repo_slug(project)) + os.sep
    assert path.startswith(base), path
    assert SID in os.path.basename(path), path
    assert not os.path.abspath(path).startswith(project + os.sep), path


def test_r2_with_no_override_the_mark_is_under_the_denied_anchor_base(project, monkeypatch):
    monkeypatch.delenv("CLAUDE_TRACE_ANCHOR_DIR")
    path = am.resume_mark_path(SID)
    assert path is not None
    assert path.startswith(os.path.expanduser(os.path.join("~", ".claude", "harness-anchors"))
                           + os.sep), path
    with open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8") as f:
        deny = json.load(f)["permissions"]["deny"]
    assert "Edit(~/.claude/harness-anchors/**)" in deny and "Bash(*harness-anchors*)" in deny


def test_r2_deleting_the_old_state_path_does_not_revive_the_tag(project, tmp_path):
    path = transcript(tmp_path, [human("run the board [admin]", -600)])
    assert am.session_tag(path) == "admin"
    done = subprocess.run([sys.executable, RESUME_HOOK], input=json.dumps(
        {"hook_event_name": "SessionStart", "source": "resume", "session_id": SID}),
        capture_output=True, text=True, timeout=30, env=os.environ.copy())
    assert done.returncode == 0, done.stderr
    assert am.session_tag(path) == "none"
    mark = am.resume_mark_path(SID)
    assert mark is not None and os.path.isfile(mark), mark
    old = os.path.join(project, OLD_MARK, SID)
    if os.path.exists(old):
        os.remove(old)  # an agent removes the path the deny rules never covered
    assert am.session_tag(path) == "none", "deleting the old resume-mark path revived [admin]"


def test_r2_docs_and_hook_no_longer_name_the_old_state_path():
    assert ".state/resume_at.d" not in _section("### Session tags")
    with open(RESUME_HOOK, encoding="utf-8") as f:
        doc = ast.get_docstring(ast.parse(f.read()))
    assert ".state/resume_at.d" not in doc


def test_r2_session_tags_known_limits_names_a_missing_session_start_entry():
    section = _section("### Session tags")
    at = section.lower().find("known limit")
    assert at != -1, "`### Session tags` has no Known limits line"
    hits = [s for s in _sentences(section[at:]) if "SessionStart" in s
            and re.search(r"\b(lack|lacks|missing|without|no)\b", s) and "resume" in s.lower()]
    assert hits, "no Known limits sentence: settings without the `SessionStart` entry keep a tag"


# ══ R3 — the `[admin]` rule texts point at `### Session tags` ═══════════════════════════════════
def test_r3_admin_tag_merge_rule_1_points_at_session_tags():
    section = _section("### Admin tag")
    merge = section[section.index("**Merge and push.**"):]
    rule1 = merge[merge.index("\n1. "):merge.index("\n2. ")]
    assert "### Session tags" in rule1, rule1


def test_r3_no_unqualified_later_request_ends_it_sentence_in_admin_tag():
    section = _section("### Admin tag")
    for item in re.split(r"\n(?=\d+\. )|\n\n", section):
        if re.search(r"later request without the tag ends it", item, re.I):
            assert "### Session tags" in item, item


def test_r3_auto_mode_limit_admin_sentence_mentions_the_session_tag():
    admin = [s for s in _sentences(merge_gate.AUTO_MODE_LIMIT) if s.startswith("`[admin]`")]
    assert admin, merge_gate.AUTO_MODE_LIMIT
    assert any(re.search(r"session tag", s, re.I) for s in admin), admin


def test_r3_stop_check_docstring_mentions_the_session_tag():
    with open(STOP_CHECK, encoding="utf-8") as f:
        doc = ast.get_docstring(ast.parse(f.read()))
    assert re.search(r"session[ _]tag", doc, re.I), "stop_auto_mode_check.py docstring"


# ══ R5 — `[stop]` in the same request turns the per-request `[admin]` off ═══════════════════════
@pytest.mark.parametrize("text", ["merge T900 [admin] [stop]", "merge T900 [stop] [admin]"])
def test_r5_admin_and_stop_in_one_request_blocks_the_merge(gate, tmp_path, text):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    path = transcript(tmp_path, [human(text, AFTER)])
    assert am.session_tag(path) == "none"
    reply = reason(MERGE + " " + BRANCH, fx.main, path)
    assert reply is not None, f"{text!r} still merges under the per-request [admin]"


# ══ R6 — "ready" wording ════════════════════════════════════════════════════════════════════════
def test_r6_ready_ticket_is_not_claimed_by_another_live_session():
    sentences = _sentences(_section("### Session tags"))
    ready = [s for s in sentences if "ready when" in s]
    assert ready and all("not claimed by another live session" in s for s in ready), ready


def test_r6_no_sentence_calls_a_todo_row_in_progress():
    bad = [s for s in _sentences(_section("### Session tags")) if "Todo" in s and "In Progress" in s]
    assert not bad, bad
