#!/usr/bin/env python3
"""T309 oracle — the ordinary merge gate stops accepting a hand-typed `☑ pass` verify row.

Written by qa-expert before the change (Pillar 3); the implementer may not edit it.

  AC 1 — an extended-track Evidence `verify` row typed by hand (`☑ pass`, the word "pass" in
         Notes, no `auto-run by hook` tag, not a proven `USER_LINE`) makes the gate block, on the
         working-tree read (`git merge` of another task's branch) and on the own-branch committed
         read (`git merge` of the task's own branch), in the review file and in the guide's inline
         Evidence.
  AC 2 — unchanged: a hook-written pass with its run record passes; the T308 user line with its
         transcript proof passes; the template's unwritten row and a hook-shaped row with no record
         block; the minimal-track `verify:` line keeps its results; `[admin]` (`hook_only`) keeps
         its results.
  AC 3 — the Supervisor's own real-run row (`auto-checked`) never counts.
  Mutation control — a copy of the gate (inside the temp repo only) with the old "any row with
         pass in Notes" branch put back lets the hand-typed row through, so the AC 1 cases are
         proven to depend on the change.

Every case runs `pre_bash_block_unsafe_merge.py` as a subprocess in a temp repo (fixtures from
`test_t250_session_ownership.py` and the shapes of `test_t308_user_verify_extended.py`), never an
import of `verify_row_passes`.

Run with: python3 -m pytest .claude/hooks/tests/test_t309_hand_typed_pass_row.py -q -p no:cacheprovider
"""
import json
import os
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_record  # noqa: E402
from test_t250_session_ownership import (  # noqa: E402
    GATE, SID, _git, commit_at, gate_env, gate_project, human, min_project,
    run_gate, slash_verify, user_line, verify_session,
)

TASK = "T900"
RFR_EXT_ROW = ("- [ ] **T900** — Fix the gate | common-infrastructure | C2 | Risk: High | P1 "
               "| Guide: `tasks/TASK_GUIDE_T900.md`")
CODE_AT = "2026-11-04T06:00:00+00:00"
ROW_AT = "2026-11-04T06:10:00+00:00"
IN_WINDOW = "2026-11-04T06:05:12.960Z"
ADMIN_AT = "2026-11-04T06:20:00Z"
UNFILLED = "☐ pass / ☐ fail / ☐ N/A | [what was observed]"
MERGE_OTHER = "git merge --no-ff fix/t901-x"   # the working-tree read (`has_filled_verify_row`)
MERGE_OWN = "git merge --no-ff fix/t900-x"     # the committed read (`committed_verify_row`)
COMMANDS = [MERGE_OTHER, MERGE_OWN]
COMMAND_IDS = ["working-tree-read", "own-branch"]
NO_ROW = "T900 (no evidence row)"
REVIEW_REL = "tasks/TASK_REVIEW_T900.md"
GUIDE_REL = "tasks/TASK_GUIDE_T900.md"
POINTER_GUIDE = "# T900\n\n## Evidence\n\n> **Moved.** `tasks/TASK_REVIEW_T900.md`.\n"
LOG = ".claude/verify-runs/T900-{short}.log"


def user_notes(sha, sid=SID):
    return f"/verify by the user, session {sid}, commit {sha}"


def hook_cells(sha):
    """The cells `verify_record.row_cells` writes for a pass (asserted equal in `_write_record`)."""
    return (f"☑ pass | {verify_record.AUTO_ROW_TAG}, session hook-sess-1, commit {sha}, "
            f"log {LOG.format(short=sha[:12])} — pass")


# Rows an agent can type with no `/verify` run at all. Each holds "pass" in Notes, so today's
# `VERIFY_ROW_PATTERN` branch accepts it.
HAND_TYPED = [
    lambda sha: "☑ pass | ran /verify myself — pass",
    lambda sha: "☑ pass | feature confirmed working — pass",
    # The `USER_LINE` shape, but the session id holds "pass" and no transcript entry backs it.
    lambda sha: f"☑ pass | {user_notes(sha, 'pass-1')}",
    lambda sha: "☑ pass / ☐ N/A | checked by hand, all pass",
]
HAND_TYPED_IDS = ["ran-verify-myself", "confirmed-working", "user-shape-sid-pass-1",
                  "pass-slash-na"]


def evidence(rows):
    body = "".join(f"| verify | {cells} |\n" for cells in rows)
    return ("## Evidence\n\n| Check | Result | Notes / output snippet |\n|-------|--------|----|\n"
            "| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | tests/x.py |\n"
            f"{body}"
            "| Full smoke suite still green (no regression) | ☑ pass | 12 passed |\n")


def review(rows):
    return f"# TASK_REVIEW — T900: Fix the gate\n\n{evidence(rows)}\n## Demonstration\n\nx\n"


def ext_project(tmp_path, rows_for, inline=False, worktree=False):
    """T900 on the extended track at Ready for Review (T308's fixture). The code is committed at
    06:00 (`sha`); the Evidence rows `rows_for(sha)` (a list of `Result | Notes` cells) are
    committed at 06:10 in `tasks/TASK_REVIEW_T900.md`, or (inline=True) in the guide's own Evidence.
    The event trace holds a test-runner call, so only the verify row decides. Returns
    (project, sha)."""
    project = gate_project(tmp_path, in_progress=(), ready=(RFR_EXT_ROW,),
                           files={"src/app.py": "print('v1')\n", GUIDE_REL: POINTER_GUIDE})
    trace = project / "memory" / "event-trace"
    trace.mkdir(parents=True)
    (trace / "T900.jsonl").write_text(json.dumps({"tool_name": "Bash", "is_error": False,
                                      "summary": json.dumps({"command": "python3 -m pytest -q"})})
                                      + "\n", encoding="utf-8")
    sha = commit_at(project, CODE_AT, "T900: fix")
    checkout = project
    if worktree:
        checkout = tmp_path / "wt-t900"
        _git(project, "worktree", "add", "-q", "-b", "fix/t900-x", str(checkout))
    rows = rows_for(sha)
    if inline:
        (checkout / GUIDE_REL).write_text(f"# T900\n\n{evidence(rows)}", encoding="utf-8")
    else:
        (checkout / REVIEW_REL).write_text(review(rows), encoding="utf-8")
    commit_at(checkout, ROW_AT, "T900: verify row")
    if not worktree:
        _git(project, "branch", "fix/t900-x")
    return project, sha


def one(cells_for):
    return lambda sha: [cells_for(sha)]


def gate(tmp_path, project, command, transcript=None):
    reason, _ = run_gate(project, command, transcript,
                         env=gate_env(project, CLAUDE_TRACE_ANCHOR_DIR=str(tmp_path / "anchors")))
    return reason


def _write_record(tmp_path, project, sha, verdict="pass"):
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(tmp_path / "anchors")
    try:
        verify_record.write_record(str(project), TASK, sha, verdict, "hook-sess-1",
                                   LOG.format(short=sha[:12]))
    finally:
        if saved is None:
            os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
        else:
            os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved
    result, notes = verify_record.row_cells(sha, verdict, "hook-sess-1", LOG.format(short=sha[:12]))
    assert f"{result} | {notes}" == hook_cells(sha), "the fixture's hook row drifted from row_cells"


def blocked(reason):
    return bool(reason) and NO_ROW in reason


# ── AC 1 — a hand-typed pass row blocks, in both merge forms ──────────────────────────────────
@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
@pytest.mark.parametrize("cells_for", HAND_TYPED, ids=HAND_TYPED_IDS)
def test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks(tmp_path, command, cells_for):
    project, _ = ext_project(tmp_path, one(cells_for))
    current = verify_session(tmp_path, project, [human("merge it", IN_WINDOW)])
    reason = gate(tmp_path, project, command, current)
    assert blocked(reason), reason


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac1_a_hand_typed_pass_row_without_a_transcript_blocks(tmp_path, command):
    project, _ = ext_project(tmp_path, one(HAND_TYPED[0]))
    reason = gate(tmp_path, project, command)
    assert blocked(reason), reason


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
@pytest.mark.parametrize("cells_for", HAND_TYPED[:2], ids=HAND_TYPED_IDS[:2])
def test_ac1_a_hand_typed_pass_row_in_the_guides_inline_evidence_blocks(tmp_path, command,
                                                                        cells_for):
    project, _ = ext_project(tmp_path, one(cells_for), inline=True)
    reason = gate(tmp_path, project, command)
    assert blocked(reason), reason


def test_ac1_a_hand_typed_row_committed_only_in_the_tasks_worktree_blocks(tmp_path):
    project, _ = ext_project(tmp_path, one(HAND_TYPED[0]), worktree=True)
    reason = gate(tmp_path, project, MERGE_OWN)
    assert blocked(reason), reason


def test_ac1_a_user_shaped_row_with_a_transcript_for_another_session_blocks(tmp_path):
    """`session pass-1` names a file that is not there; the current session's own transcript holds a
    real `/verify T900` — it still does not prove a row that names another session."""
    project, _ = ext_project(tmp_path, one(HAND_TYPED[2]))
    current = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, current)
    assert blocked(reason), reason


# ── AC 2 — unchanged results ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_a_hook_written_pass_with_its_record_still_passes(tmp_path, command):
    project, sha = ext_project(tmp_path, lambda sha: [hook_cells(sha)])
    _write_record(tmp_path, project, sha)
    assert gate(tmp_path, project, command) is None


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_the_t308_user_line_with_its_proof_still_passes(tmp_path, command):
    project, _ = ext_project(tmp_path, lambda sha: [f"☑ pass | {user_notes(sha)}"])
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, command, t) is None


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_a_hand_typed_row_beside_a_proven_row_does_not_stop_the_pass(tmp_path, command):
    """Edge case: the proven row counts; an extra hand-typed row neither adds nor removes."""
    project, sha = ext_project(tmp_path, lambda sha: [HAND_TYPED[0](sha), hook_cells(sha)])
    _write_record(tmp_path, project, sha)
    assert gate(tmp_path, project, command) is None


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_a_hook_row_with_no_record_and_a_proven_user_row_passes(tmp_path, command):
    """Edge case: a hook row and a user line in one table — either counts, as in T308."""
    project, _ = ext_project(tmp_path, lambda sha: [hook_cells(sha),
                                                    f"☑ pass | {user_notes(sha)}"])
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, command, t) is None


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_the_templates_unwritten_row_still_blocks(tmp_path, command):
    project, _ = ext_project(tmp_path, one(lambda sha: UNFILLED))
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, command, t)
    assert blocked(reason), reason


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_a_hook_shaped_row_with_no_record_still_blocks(tmp_path, command):
    project, _ = ext_project(tmp_path, lambda sha: [hook_cells(sha)])
    reason = gate(tmp_path, project, command)
    assert blocked(reason), reason


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_ac2_a_hook_row_whose_record_says_fail_still_blocks(tmp_path, command):
    project, sha = ext_project(tmp_path, lambda sha: [hook_cells(sha)])
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(tmp_path / "anchors")
    try:
        verify_record.write_record(str(project), TASK, sha, "fail", "hook-sess-1",
                                   LOG.format(short=sha[:12]))
    finally:
        if saved is None:
            os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
        else:
            os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved
    reason = gate(tmp_path, project, command)
    assert blocked(reason), reason


# The minimal track: unchanged (T250 G1 / T188 D5).
def test_ac2_the_minimal_track_user_line_with_its_proof_still_passes(tmp_path):
    project, _ = min_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, MERGE_OTHER, t) is None


def test_ac2_the_minimal_track_user_line_without_a_transcript_still_blocks(tmp_path):
    project, _ = min_project(tmp_path)
    reason = gate(tmp_path, project, MERGE_OTHER)
    assert blocked(reason), reason


def test_ac2_the_minimal_track_hand_typed_line_still_blocks(tmp_path):
    project, _ = min_project(tmp_path, line_for=lambda sha: [
        "- verify: ☑ pass — ran /verify myself, pass"])
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert blocked(reason), reason


# `[admin]` (`hook_only`): the request is the latest human entry and names T900; the merge is of
# the task's own branch. Driven through the subprocess like every case above.
def admin_session(tmp_path, project, entries=()):
    return verify_session(tmp_path, project,
                          list(entries) + [human("merge T900 [admin]", ADMIN_AT)])


def test_ac2_admin_with_a_hook_written_pass_still_merges(tmp_path):
    project, sha = ext_project(tmp_path, lambda sha: [hook_cells(sha)])
    _write_record(tmp_path, project, sha)
    assert gate(tmp_path, project, MERGE_OWN, admin_session(tmp_path, project)) is None


@pytest.mark.parametrize("rows_for, entries", [
    (one(HAND_TYPED[0]), ()),
    (one(lambda sha: f"☑ pass | {user_notes(sha)}"), (slash_verify(TASK, IN_WINDOW),)),
    (lambda sha: [hook_cells(sha)], ()),
], ids=["hand-typed", "t308-user-line-with-proof", "hook-row-no-record"])
def test_ac2_admin_without_a_hook_written_pass_still_blocks(tmp_path, rows_for, entries):
    project, _ = ext_project(tmp_path, rows_for)
    reason = gate(tmp_path, project, MERGE_OWN, admin_session(tmp_path, project, entries))
    assert reason and "[admin]" in reason and "auto verify" in reason, reason


# ── AC 3 — the Supervisor's own real-run row never counts ─────────────────────────────────────
@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
@pytest.mark.parametrize("notes", [
    f"{verify_record.AUTO_CHECKED_TAG}: ran the app, all pass",
    f"{verify_record.AUTO_CHECKED_TAG} — pass",
], ids=["auto-checked-prose", "auto-checked-short"])
def test_ac3_an_auto_checked_row_never_counts(tmp_path, command, notes):
    project, _ = ext_project(tmp_path, one(lambda sha: f"☑ pass | {notes}"))
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, command, t)
    assert blocked(reason), reason


# ── Mutation control — the old "any row with pass in Notes" branch, put back in a copy ────────
OLD_BRANCH = '''

# T309 mutation control: the pre-T309 rule, put back. Any `verify` row with "pass" in Notes, a
# Result with no unchecked `☐ pass`, and neither tag counts on the ordinary gate.
_t309_strict_verify_row_passes = verify_row_passes


def verify_row_passes(section, confirm, hook_only=False, confirm_user=None):
    if section and not hook_only:
        for _m in re.finditer(r"verify\\s*\\|([^|\\n]*)\\|([^|\\n]*pass[^|\\n]*)", section, re.I):
            _notes = _m.group(2).lower()
            if (re.search(r"☐\\s*pass\\b", _m.group(1), re.I) or AUTO_CHECKED_TAG in _notes
                    or AUTO_ROW_TAG in _notes):
                continue
            return True
    return _t309_strict_verify_row_passes(section, confirm, hook_only, confirm_user)

'''


def _mutate(project):
    path = project / ".claude" / "hooks" / GATE
    assert path.resolve() != (HOOKS / GATE).resolve(), "never patch the real hook"
    source = path.read_text(encoding="utf-8")
    head, marker, tail = source.rpartition("\nmain()")
    assert marker and not tail.strip(), "the gate no longer ends with main()"
    path.write_text(head + OLD_BRANCH + marker + tail, encoding="utf-8")


@pytest.mark.parametrize("command", COMMANDS, ids=COMMAND_IDS)
def test_mutation_the_old_any_pass_branch_lets_a_hand_typed_row_through(tmp_path, command):
    """The real gate blocks the hand-typed row; the copy with the old branch put back allows it,
    so the AC 1 tests turn red on a gate that still accepts "pass" in Notes."""
    project, _ = ext_project(tmp_path, one(HAND_TYPED[0]))
    reason = gate(tmp_path, project, command)
    assert blocked(reason), f"the real gate must block a hand-typed row: {reason}"
    _mutate(project)
    assert gate(tmp_path, project, command) is None, \
        "the mutated copy still blocks: the AC 1 cases do not depend on the old branch being gone"
