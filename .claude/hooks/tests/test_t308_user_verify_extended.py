#!/usr/bin/env python3
"""T308 oracle — the merge gate accepts the user's own `/verify <ID>` for an extended-track task.

Written by qa-expert before the change (Pillar 3); the implementer may not edit it.

  AC 1 — an extended-track task at Ready for Review whose Evidence `verify` row is
         `| verify | ☑ pass | /verify by the user, session <sid>, commit <sha> |` lets a merge
         through when the transcript of `<sid>` holds a human `/verify <ID>` entry dated after
         `<sha>` was committed and before the row was committed, and `<sha>` is the head's code
         (only the file that holds the row may differ).
  AC 2 — the upper time bound is the commit that added the row to `tasks/TASK_REVIEW_<ID>.md`
         (or to the guide's inline Evidence), not `tasks/MINIMAL_LOG.md`.
  AC 3 — every proof rule fails closed, one rule broken at a time.
  AC 4 — unchanged: a hook-written pass passes; the template's unwritten row and a hand-typed pass
         with no proof fail; the minimal-track user line keeps its T250 G1 results.
  Mutation control — a copy of the hooks whose `/verify` lookup ignores the time bound must let an
         out-of-window entry through, so the AC 3 time cases are proven to depend on the bound.

Every case runs `pre_bash_block_unsafe_merge.py` as a subprocess in a temp repo (fixtures from
`test_t250_session_ownership.py`), never an import of `has_filled_verify_row`.

Run with: python3 -m pytest .claude/hooks/tests/test_t308_user_verify_extended.py -q -p no:cacheprovider
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
    OTHER_SID, SID, _git, commit_at, gate_env, gate_project, human, min_project, run_gate,
    slash_verify, user_line, verify_session,
)

TASK = "T900"
RFR_EXT_ROW = ("- [ ] **T900** — Fix the gate | common-infrastructure | C2 | Risk: High | P1 "
               "| Guide: `tasks/TASK_GUIDE_T900.md`")
CODE_AT = "2026-11-04T06:00:00+00:00"
ROW_AT = "2026-11-04T06:10:00+00:00"
IN_WINDOW = "2026-11-04T06:05:12.960Z"
BEFORE_CODE = "2026-11-04T05:59:00Z"
AFTER_ROW = "2026-11-04T06:11:00Z"
UNFILLED = "☐ pass / ☐ fail / ☐ N/A | [what was observed]"
MERGE_OTHER = "git merge --no-ff fix/t901-x"   # the working-tree read (`has_filled_verify_row`)
MERGE_OWN = "git merge --no-ff fix/t900-x"     # the committed read (`committed_verify_row`)
NO_ROW = "T900 (no evidence row)"
REVIEW_REL = "tasks/TASK_REVIEW_T900.md"
GUIDE_REL = "tasks/TASK_GUIDE_T900.md"
POINTER_GUIDE = "# T900\n\n## Evidence\n\n> **Moved.** `tasks/TASK_REVIEW_T900.md`.\n"


def user_notes(sha, sid=SID):
    return f"/verify by the user, session {sid}, commit {sha}"


def evidence(cells):
    return ("## Evidence\n\n| Check | Result | Notes / output snippet |\n|-------|--------|----|\n"
            "| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | tests/x.py |\n"
            f"| verify | {cells} |\n"
            "| Full smoke suite still green (no regression) | ☑ pass | 12 passed |\n")


def review(cells):
    return f"# TASK_REVIEW — T900: Fix the gate\n\n{evidence(cells)}\n## Demonstration\n\nx\n"


def ext_project(tmp_path, cells_for=lambda sha: f"☑ pass | {user_notes(sha)}", inline=False,
                code_change_after=False, worktree=False):
    """T900 on the extended track at Ready for Review. The code is committed at 06:00 (`sha`); the
    Evidence row `cells_for(sha)` is committed at 06:10 — in `tasks/TASK_REVIEW_T900.md`, or
    (inline=True) in the guide's own Evidence section. With worktree=True the row commit lives only
    on branch `fix/t900-x`, checked out in `../wt-t900`. Returns (project, checkout, sha)."""
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
    if inline:
        (checkout / GUIDE_REL).write_text(f"# T900\n\n{evidence(cells_for(sha))}", encoding="utf-8")
    else:
        (checkout / REVIEW_REL).write_text(review(cells_for(sha)), encoding="utf-8")
    commit_at(checkout, ROW_AT, "T900: verify row")
    if code_change_after:
        (checkout / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        commit_at(checkout, ROW_AT, "T900: more code")
    if not worktree:
        _git(project, "branch", "fix/t900-x")
    return project, checkout, sha


def env_for(tmp_path, project):
    return gate_env(project, CLAUDE_TRACE_ANCHOR_DIR=str(tmp_path / "anchors"))


def gate(tmp_path, project, command, transcript=None):
    reason, _ = run_gate(project, command, transcript, env=env_for(tmp_path, project))
    return reason


# ── AC 1, AC 2 — the user's line on the extended track passes with its proof ──────────────────
@pytest.mark.parametrize("command", [MERGE_OTHER, MERGE_OWN], ids=["working-tree-read", "own-branch"])
def test_ac1_the_users_verify_row_with_the_transcript_entry_passes(tmp_path, command):
    project, _, _ = ext_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, command, t) is None


@pytest.mark.parametrize("command", [MERGE_OTHER, MERGE_OWN], ids=["working-tree-read", "own-branch"])
def test_ac2_a_row_in_the_guides_inline_evidence_passes(tmp_path, command):
    project, _, _ = ext_project(tmp_path, inline=True)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, command, t) is None


def test_ac1_a_row_committed_only_in_the_tasks_worktree_passes(tmp_path):
    project, _, _ = ext_project(tmp_path, worktree=True)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    assert gate(tmp_path, project, MERGE_OWN, t) is None


def test_ac1_the_named_session_may_be_another_file_in_the_same_folder(tmp_path):
    project, _, _ = ext_project(tmp_path, cells_for=lambda sha: f"☑ pass | {user_notes(sha, OTHER_SID)}")
    verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)], sid=OTHER_SID)
    current = verify_session(tmp_path, project, [human("merge it", IN_WINDOW)])
    assert gate(tmp_path, project, MERGE_OTHER, current) is None


# ── AC 3 — each proof rule, broken alone, blocks ──────────────────────────────────────────────
def test_ac3_no_transcript_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path)
    reason = gate(tmp_path, project, MERGE_OTHER)            # the event has no transcript_path
    assert reason and NO_ROW in reason
    current = verify_session(tmp_path, project, [human("merge it", IN_WINDOW)], sid=OTHER_SID)
    reason = gate(tmp_path, project, MERGE_OTHER, current)   # `<sid>.jsonl` does not exist
    assert reason and NO_ROW in reason


def test_ac3_a_short_hash_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path, cells_for=lambda sha: f"☑ pass | {user_notes(sha[:12])}")
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


def test_ac3_a_commit_of_other_code_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path, code_change_after=True)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


@pytest.mark.parametrize("command", [MERGE_OTHER, MERGE_OWN], ids=["working-tree-read", "own-branch"])
def test_ac3_an_entry_dated_before_the_code_commit_blocks(tmp_path, command):
    project, _, _ = ext_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify(TASK, BEFORE_CODE)])
    reason = gate(tmp_path, project, command, t)
    assert reason and NO_ROW in reason


@pytest.mark.parametrize("command", [MERGE_OTHER, MERGE_OWN], ids=["working-tree-read", "own-branch"])
@pytest.mark.parametrize("inline", [False, True], ids=["review-file", "inline-guide"])
def test_ac2_ac3_an_entry_dated_after_the_rows_commit_blocks(tmp_path, command, inline):
    """The AC 2 case: the upper bound must come from the file holding the row. Searching only
    `tasks/MINIMAL_LOG.md` finds no commit, which leaves the window open on the working-tree read."""
    project, _, _ = ext_project(tmp_path, inline=inline)
    t = verify_session(tmp_path, project, [slash_verify(TASK, AFTER_ROW)])
    reason = gate(tmp_path, project, command, t)
    assert reason and NO_ROW in reason


def test_ac3_an_entry_for_another_task_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify("T901", IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


def test_ac3_an_entry_with_no_human_origin_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW, origin=None)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


@pytest.mark.parametrize("cells_for", [
    lambda sha: f"☑ pass | user ran /verify T900, session {SID}, commit {sha}",
    lambda sha: f"☑ pass | {user_notes(sha)} (looked fine)",
    # Not `../../etc/passwd`: Notes holding the word "pass" are a plain hand-typed pass row, which
    # the gate accepts today outside the T308 path (reported to the Supervisor, out of scope here).
    lambda sha: f"☑ pass | {user_notes(sha, '../../etc/hosts')}",
    lambda sha: f"☐ pass / ☐ fail | {user_notes(sha)}",
], ids=["other-wording", "trailing-text", "bad-session-id", "unchecked-result"])
def test_ac3_notes_not_in_the_user_line_shape_block(tmp_path, cells_for):
    project, _, _ = ext_project(tmp_path, cells_for=cells_for)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


# ── AC 4 — unchanged results ──────────────────────────────────────────────────────────────────
def _hook_row(tmp_path, project, sha, verdict="pass"):
    saved = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(tmp_path / "anchors")
    try:
        verify_record.write_record(str(project), TASK, sha, verdict, "hook-sess-1",
                                   f".claude/verify-runs/{TASK}-{sha[:12]}.log")
    finally:
        if saved is None:
            os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR", None)
        else:
            os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = saved
    result, notes = verify_record.row_cells(sha, verdict, "hook-sess-1",
                                            f".claude/verify-runs/{TASK}-{sha[:12]}.log")
    return f"{result} | {notes}"


@pytest.mark.parametrize("command", [MERGE_OTHER, MERGE_OWN], ids=["working-tree-read", "own-branch"])
def test_ac4_a_hook_written_pass_still_passes(tmp_path, command):
    holder = {}
    project, _, _ = ext_project(tmp_path, cells_for=lambda sha: holder.setdefault("cells", (
        f"☑ pass | {verify_record.AUTO_ROW_TAG}, session hook-sess-1, commit {sha}, "
        f"log .claude/verify-runs/{TASK}-{sha[:12]}.log — pass")))
    sha = _git(project, "rev-parse", "HEAD~1")
    assert _hook_row(tmp_path, project, sha) == holder["cells"]
    assert gate(tmp_path, project, command) is None


def test_ac4_a_hook_written_row_with_no_record_still_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path, cells_for=lambda sha: (
        f"☑ pass | {verify_record.AUTO_ROW_TAG}, session hook-sess-1, commit {sha}, "
        f"log .claude/verify-runs/{TASK}-{sha[:12]}.log — pass"))
    reason = gate(tmp_path, project, MERGE_OTHER)
    assert reason and NO_ROW in reason


def test_ac4_the_templates_unwritten_row_still_blocks(tmp_path):
    project, _, _ = ext_project(tmp_path, cells_for=lambda sha: UNFILLED)
    t = verify_session(tmp_path, project, [slash_verify(TASK, IN_WINDOW)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


@pytest.mark.parametrize("with_transcript", [False, True], ids=["no-transcript", "with-transcript"])
def test_ac4_a_hand_typed_user_shaped_pass_with_no_proof_blocks(tmp_path, with_transcript):
    """The user's shape, but no matching entry: the text of the row is never the proof."""
    project, _, _ = ext_project(tmp_path)
    t = (verify_session(tmp_path, project, [human("please mark T900 as verified", IN_WINDOW)])
         if with_transcript else None)
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    assert reason and NO_ROW in reason


# The minimal track: the T250 G1 expectations, copied (test_t250_session_ownership.py AC 1/2).
@pytest.mark.parametrize("entry_at, line_for, code_change_after, allowed", [
    (IN_WINDOW, lambda sha: [user_line(sha)], False, True),
    (BEFORE_CODE, lambda sha: [user_line(sha)], False, False),
    ("2026-11-04T06:11:00Z", lambda sha: [user_line(sha)], False, False),
    (IN_WINDOW, lambda sha: [user_line(sha[:12])], False, False),
    (IN_WINDOW, lambda sha: [user_line(sha)], True, False),
], ids=["in-window-passes", "before-the-code", "after-the-line", "short-sha", "other-code"])
def test_ac4_the_minimal_track_user_line_is_unchanged(tmp_path, entry_at, line_for,
                                                      code_change_after, allowed):
    project, _ = min_project(tmp_path, line_for=line_for, code_change_after=code_change_after)
    t = verify_session(tmp_path, project, [slash_verify(TASK, entry_at)])
    reason = gate(tmp_path, project, MERGE_OTHER, t)
    if allowed:
        assert reason is None, reason
    else:
        assert reason and NO_ROW in reason


def test_ac4_the_minimal_track_without_a_transcript_still_blocks(tmp_path):
    project, _ = min_project(tmp_path)
    reason = gate(tmp_path, project, MERGE_OTHER)
    assert reason and NO_ROW in reason


# ── Mutation control — the time bound is load-bearing on the extended path ────────────────────
TIME_BLIND = '''

# T308 mutation control: the `/verify` lookup ignores its time bound.
_t308_bounded_verify_typed = verify_typed


def verify_typed(transcript_path, task_id, after=None, before=None):
    return _t308_bounded_verify_typed(transcript_path, task_id)
'''


@pytest.mark.parametrize("entry_at, command", [
    (BEFORE_CODE, MERGE_OTHER), (AFTER_ROW, MERGE_OTHER), (BEFORE_CODE, MERGE_OWN),
], ids=["before-code-working-tree", "after-row-working-tree", "before-code-own-branch"])
def test_mutation_a_time_blind_copy_lets_an_out_of_window_entry_through(tmp_path, entry_at, command):
    """Run the AC 3 time case against a patched copy of the hooks (inside the temp repo only). The
    real gate blocks it; the time-blind copy must allow it, so the AC 3 time tests above turn red
    on a gate whose extended-track path does not apply the bound. Today the copy still blocks
    (the extended path does not exist), so this test is red until the path is built."""
    project, _, _ = ext_project(tmp_path)
    t = verify_session(tmp_path, project, [slash_verify(TASK, entry_at)])
    assert gate(tmp_path, project, command, t), "the real gate must block an out-of-window entry"
    lib = project / ".claude" / "hooks" / "lib" / "session_work.py"
    assert lib.resolve() != (HOOKS / "lib" / "session_work.py").resolve()
    lib.write_text(lib.read_text(encoding="utf-8") + TIME_BLIND, encoding="utf-8")
    assert gate(tmp_path, project, command, t) is None, \
        "the time-blind copy still blocks: the extended path does not depend on the time bound"
