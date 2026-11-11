# TASK_GUIDE — T309: the ordinary merge gate stops accepting a hand-typed `☑ pass` verify row with no proof
**Date**: 2026-11-11
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

Found by `qa-expert` while writing the T308 oracle (2026-11-11), reported to the user the same day. User, 2026-11-11: "register it" (the Supervisor had recommended: close the hole in code and repoint the two pin tests; the alternative was to change the docs).

The hole, in `.claude/hooks/pre_bash_block_unsafe_merge.py`: `VERIFY_ROW_PATTERN` needs the word "pass" in the Notes cell, and `verify_row_passes` returns True for any `verify` row that has it, unless the row carries the `auto-run by hook` tag (then it needs its run record) or the caller sets `hook_only` (`[admin]`). So on the ordinary gate, an extended-track row `| verify | ☑ pass | ran /verify myself — pass |`, typed by an agent with no `/verify` run at all, lets `git merge` and `git push` through (the gate then only asks for a test-runner call in the event trace). `docs/claude-md/tracks.md` `### Known limits` says the opposite: "The merge gate still blocks a hand-typed row at merge: it accepts only a row with an `auto-run by hook` run record." Two tests pin the current behaviour: `.claude/hooks/tests/test_verify_row_fill_detection.py` (`FILLED_CHECKED_BOX_ROW`) and `.claude/hooks/tests/test_merge_gate_t095.py` (`REVIEW_WITH_FILLED_VERIFY_ROW`, line ~83).

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> On the ordinary merge gate, an Evidence `verify` row counts only as a hook-written pass with its run record, or as the user's own `/verify` line with its transcript proof (T308). A row an agent typed by hand does not count, even with the word "pass" in Notes. The code then matches `### Known limits`.

**Out of scope** (what this task explicitly does NOT do):
- The `[admin]` path (`hook_only`): it already counts only a hook-written row.
- The minimal-track gate (`minimal_line_passes`): already strict.
- The T308 user-line path itself: T308 adds it; T309 only keeps it working.
- The no-runtime-surface path list in `verify_record.py`, the event-trace check, the Stop hook.

**Depends on**: T308 — the same function (`verify_row_passes`) and the `USER_LINE` row. Start T309 from `main` after T308 is merged.

**Requirement Refs**: None — kit maintenance; source is the report above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; the user said "register it" on 2026-11-11 after the recommendation)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Entry point**: `verify_row_passes` in `.claude/hooks/pre_bash_block_unsafe_merge.py` (called through `has_filled_verify_row` and `committed_verify_row` by the merge gate for every `git merge` and `git push`)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | An extended-track `verify` row typed by hand (`☑ pass`, "pass" in Notes, no `auto-run by hook` tag, not the `USER_LINE` shape) makes the gate block, in both merge forms (working-tree read and own-branch committed read) | the hole |
| 2 | A hook-written pass with its run record passes; the T308 user line with its proof passes; the template's unwritten row blocks; the minimal-track path and `[admin]` (`hook_only`) give the same results as before | no regression |
| 3 | The Supervisor's own real-run row (`AUTO_CHECKED_TAG`) still never counts | unchanged rule |
| 4 | `### Known limits` and the lines about the merge gate in `docs/claude-md/tracks.md` stay true as written; fix any other doc text that says a hand-typed pass row is accepted (grep first) | docs agree |
| 5 | The two pin tests (`test_verify_row_fill_detection.py`, `test_merge_gate_t095.py`) and any other test that expects a hand-typed pass row to pass are changed to expect a block, each with a one-line comment naming T309. The gate tests that guard the row shape (unchecked box, `☑ pass / ☐ N/A`, "pass" only in Result) keep their meaning | pins |

---

## Evaluation & Acceptance

**Locked oracle**: `.claude/hooks/tests/test_t309_hand_typed_pass_row.py` (written first by `qa-expert`, commit `eb85f72`, red: 18 failed, 25 passed). The implementer may not edit it. Keep the block text `T900 (no evidence row)`.

**Fixture fallout found by `qa-expert` (the real size of AC 5)**: with the one-line prototype fix (`if hook_only and AUTO_ROW_TAG not in notes:` becomes `if AUTO_ROW_TAG not in notes:`), these existing tests fail because their base fixture is a hand-typed pass row: `test_merge_gate_t095.py` (4 tests, `REVIEW_WITH_FILLED_VERIFY_ROW`), `test_verify_row_fill_detection.py` (`FILLED_CHECKED_BOX_ROW`; `test_ac3_all_four_real_filled_shapes_are_filled`, `test_ac3_trap_checked_pass_with_unchecked_na_shape`, `test_ac6_old_vs_new_pattern_over_real_corpus_differs_only_on_placeholders`: these are row-shape tests and keep their meaning, so they need a hook-row variant, not a flip), `test_merge_gate_t210.py` (`MANUAL_PASS`, 12 tests), `test_merge_gate_t211.py` (imports `MANUAL_PASS`, 10 tests), `test_merge_gate_companion_rows.py` (`REVIEW_HEADER` and lines ~621, ~660; about 34 tests), `test_guide_sections.py` (`FILLED_EVIDENCE_TABLE` and rows ~625, ~837, ~852; 5 tests), `test_admin_tag.py` (`test_sc3_a_hand_typed_pass_row_is_not_an_auto_verify`: its control line ~275 asserts the normal gate allows `MANUAL_PASS`), `tests/test_auto_mode.py` (`test_ac4_control_a_real_verify_row_passes`). Rule for the repoint: a test whose point is something other than the row (worktree evidence, push narrowing, octopus, companion rows, guide sections) keeps its meaning by swapping its fixture row for a hook-written pass with a real run record (a shared helper, modelled on `_hook_row` in `test_t308_user_verify_extended.py` / `test_t309_hand_typed_pass_row.py`); a test whose point IS that a hand-typed row counts flips to expect a block and names T309 in a comment. Never delete a test, never loosen an assertion, never edit the gate to spare a fixture.

**Gate-owner allowlist**: `tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged` needs `T309` in `AUTHORISED_TASKS` in `.claude/hooks/tests/merge_gate_guard.py` (with its rule line) and the pin in `test_merge_gate_guard.py`, as T308 did. The Supervisor signs this line off (this guide; user: "register it", 2026-11-11), and tells the user at merge.

**Rows that would now fail** (qa-expert's scan): none of the Ready for Review tasks; 128 task files hold a hand-typed pass row (121 Done, 7 not on the board: T083, T084, T087, T135, T183, T185, T187), and the gate reads none of them (`main()` reads only `### Ready for Review` IDs; the one Done read, `[admin]`'s `committed_verify_row(..., hook_only=True)`, already ignores hand-typed rows).

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | A temp repo, an extended-track task at Ready for Review, and a hand-typed `☑ pass` row with "pass" in Notes | the gate blocks `git merge <branch>` (both forms) | automated test that runs the hook as a subprocess |
| 2 | A hook-written pass; the T308 user line; the unwritten row; a minimal-track record; `[admin]` | unchanged results | automated test |
| 3 | A mutation: restore the old "any row with pass" branch | a test goes red | mutation control |
| 4 | The full suites | no regression other than the repointed pins | `python3 -m pytest .claude/hooks/tests/ tests/ -q` (the Supervisor's venv: see the spawn prompt) |

### Verification Command

```bash
python3 -m pytest .claude/hooks/tests/test_t309_hand_typed_pass_row.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence

> **Moved.** `tasks/TASK_REVIEW_T309.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T309.md`.

---

## Approach

**Pattern reference**: `verify_row_passes`, `minimal_line_passes` and T308's `USER_LINE` branch in `.claude/hooks/pre_bash_block_unsafe_merge.py`; T308's oracle `.claude/hooks/tests/test_t308_user_verify_extended.py` for the subprocess fixtures.
**Vital slice**: in `verify_row_passes`, a row with no `auto-run by hook` tag and not the `USER_LINE` shape returns "not a pass".
**Cut list**: no new row shape, no new message text unless a test needs one, no change to the event-trace check.

Risk: this tightens a merge gate that real tasks pass through today. Before the change, list every task on the board at Ready for Review and every guide or review file in `tasks/` whose `verify` row would now fail, and report the list (a Done task is not read by the gate; confirm that). Fail closed on any doubt. Security review is mandatory.

---

## Edge Case Checklist

- [ ] A row with both a hook tag and a user line: either counts, as in T308.
- [ ] `☑ pass / ☐ N/A` (filled, "pass" in Result only) keeps the same answer as today for the shape checks.
- [ ] A review file that still carries an old hand-typed row on a task already in Done: not read by the gate; confirm.
- [ ] Pin-test pre-flight: fill `Pre-existing pin tests` before work starts
- [ ] Stale references: grep for "hand-typed", "typed by hand", "FILLED_CHECKED_BOX_ROW", "REVIEW_WITH_FILLED_VERIFY_ROW", "verify skill run" in `docs/claude-md/`, `site/`, `README`, `agents/`, `skills/`, `templates/`, `.claude/hooks/tests/`, `tests/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `verify_row_passes`: a hand-typed row is not a pass |
| `.claude/hooks/tests/test_t309_hand_typed_pass_row.py` | new, written by `qa-expert` |
| the tests listed under "Fixture fallout" above, `.claude/hooks/tests/merge_gate_guard.py`, `.claude/hooks/tests/test_merge_gate_guard.py` | repoint the fixtures and pins (AC 5); `AUTHORISED_TASKS` gains `T309` |
| `docs/claude-md/tracks.md`, other docs | only where a grep hit says a hand-typed pass row is accepted (AC 4) |
| `PROJECT_SPEC.md:102` (glossary "Auto verify"), `templates/TASK_REVIEW_template.md` (`verify` row placeholder: Notes "must literally state pass") | found at T308 Stage 4: the glossary is stale since T250; the placeholder reads as a conflict with the user-row shape. Fix both here, with the gate change |
| Pre-existing pin tests | grep `.claude/hooks/tests/` and `tests/` for `verify_row_passes`, `has_filled_verify_row`, `committed_verify_row`, `VERIFY_ROW_PATTERN` and each edited doc string; always `test_agent_guide_dedup.py`, `test_vital_slice.py`, the memory budget tests |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/verify_record.py` | the path list stays |
| `.claude/hooks/tests/test_t308_user_verify_extended.py` | T308's locked oracle |
| `### Admin tag` text of `docs/claude-md/tracks.md` | T306 and T307 own it |
| `.claude/settings.json` | permissions |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

`qa-expert` writes the oracle first (red). The implementer changes the gate and repoints the pins until green, then runs the full suites. The Supervisor runs code review and security review at High risk.

---

## Completion Checklist

- [ ] Oracle written by `qa-expert`, red
- [ ] List of rows that would now fail, reported
- [ ] Implementation done
- [ ] `code-review` run
- [ ] `security-review` run (High risk; it changes a merge gate)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T309.md` (Hard-Stop Gate 5)
- [ ] The user types `/verify T309` if the auto run ends `blocked`
- [ ] `memory/MEMORY.md` updated (Supervisor)
- [ ] Supervisor notified: ready for Stage 4
