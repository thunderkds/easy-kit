# TASK_GUIDE — T308: the merge gate accepts the user's own `/verify <ID>` for an extended-track task
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

Found while verifying T306 (2026-11-11). T306 is an extended-track task. Its auto verify run ended `blocked`: the verifier said SKIP, and the hook counts `docs/claude-md/` and `templates/` as having a runtime surface. The user then ran `/verify T306` twice. The merge gate did not accept it.

Cause, `.claude/hooks/pre_bash_block_unsafe_merge.py` `has_filled_verify_row`: an Evidence `verify` row counts only through `auto_row_confirmed` (a hook-written pass with a run record). The user's own line (`/verify by the user, session <sid>, commit <sha>`, T250 G1, `user_line_confirmed`) is read only from the `verify:` lines of `tasks/MINIMAL_LOG.md`, a minimal-track task. So an extended-track task whose auto run is `blocked` has no accepted path to a merge. User, 2026-11-11: "yes, do both" (register T308 and prepare the T306 merge).

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> For an extended-track task, the merge gate accepts an Evidence `verify` row that holds the user's own `/verify` line, with the same proof as the minimal track: the transcript of the named session holds the user's typed `/verify <ID>`, dated after the commit and before the row was committed. A hook-written pass stays accepted as before.

**Out of scope** (what this task explicitly does NOT do):
- The `[admin]` rule (item 4 of `### Admin tag`): "a hand-typed pass row does not count" stays. T308 changes the ordinary merge gate only. Report any conflict between the two and stop.
- The no-runtime-surface path list in `verify_record.py`.
- A new proof of the verdict: the gate shows only that the user ran `/verify <ID>`, not what it said. `### Known limits` already says so for the minimal track; the same sentence covers this.
- Any change to `user_line_confirmed`'s time and session rules, except the file path it searches (below).

**Depends on**: T306 (merge it first: both edit `docs/claude-md/tracks.md`; T308 edits lines 437-448 and `### Known limits`, T307 edits `### Admin tag`). Start T308 from `main` after those merges.

**Requirement Refs**: None — kit maintenance; source is the user request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; the user approved registering T308 on 2026-11-11: "yes, do both")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Entry point**: `has_filled_verify_row` in `.claude/hooks/pre_bash_block_unsafe_merge.py` (called by the merge gate for every `git merge` and `git push`)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | An extended-track task whose Evidence `verify` row is `☑ pass` with Notes `/verify by the user, session <sid>, commit <sha>` passes `has_filled_verify_row` when `user_line_confirmed`'s proof holds: the transcript of `<sid>` has a human `/verify <ID>` entry dated after `<sha>` was committed and before the row was committed; `<sha>` is the same code as the head (only the report file may differ) | the blocked T306 case |
| 2 | The time bound reads the commit that added the row to `tasks/TASK_REVIEW_<ID>.md` (or the guide's inline Evidence). Today `user_line_confirmed` searches only `MINIMAL_LOG_REL`; the path becomes a parameter, and the minimal-track call keeps its path | AC 1 |
| 3 | Every proof rule stays: a missing transcript, a short hash, a `<sha>` of other code, an entry dated before `<sha>` or after the row's commit, an entry typed for another task ID, an entry with no human origin, and a row whose Notes do not match the `USER_LINE` shape each return False (fail closed) | gate stays strict |
| 4 | A hook-written pass still passes; the template's unwritten row and a hand-typed pass with no proof still fail; the minimal-track path is unchanged | no regression |
| 5 | The `### Known limits` and lines 437-448 of `docs/claude-md/tracks.md` say the extended track accepts the user's line too, in the same shape, and keep the sentence that the gate does not show the verdict | docs agree |
| 6 | The `/verify (yours)` fallback text (`tracks.md` `### Final report`, both templates) names where the user's pass goes on the extended track: the `verify` row, Result `☑ pass`, Notes in the `USER_LINE` shape. No other text change in the templates | users can follow it |

---

## Evaluation & Acceptance

**Locked oracle**: `.claude/hooks/tests/test_t308_user_verify_extended.py` (written first by `qa-expert`, commit `c2c1252`, red: 9 failed, 27 passed). The implementer may not edit it. Two assertions expect the block text `T900 (no evidence row)`: keep that message.

**Known older hole (out of scope, found by `qa-expert`)**: `VERIFY_ROW_PATTERN` needs the word "pass" in Notes, and `verify_row_passes` accepts any non-hook row that has it (no proof) unless `hook_only` (`[admin]`). So a hand-typed `☑ pass` row with "pass" in Notes already passes the ordinary gate, and `### Known limits` says it does not. `test_verify_row_fill_detection.py` `FILLED_CHECKED_BOX_ROW` and `test_merge_gate_t095.py:83` pin it. T308 does not change this. The `USER_LINE` Notes have no "pass", so the new path needs its own row match. The security review restates the hole; a separate task decides code or docs.

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | A temp repo with an extended-track task at Ready for Review, a transcript holding the user's `/verify <ID>`, and the `USER_LINE` row | the gate lets `git merge <branch>` through | automated test that runs the hook as a subprocess (`pre_bash_block_unsafe_merge.py`), not an import |
| 2 | The same, with one proof rule broken at a time (AC 3, seven cases) | the gate blocks each time | automated test, one case per rule |
| 3 | A hook-written pass; an unwritten row; a minimal-track record | unchanged results | automated test |
| 4 | A mutation: make the new path ignore the time bound | a test goes red | mutation control |
| 5 | The full suites | no regression, in particular `test_merge_gate*.py`, `test_auto_verify.py`, `test_admin_tag.py` | `python3 -m pytest .claude/hooks/tests/ tests/ -q` (the Supervisor's venv: see the spawn prompt) |

### Verification Command

```bash
python3 -m pytest .claude/hooks/tests/test_t308_user_verify_extended.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence

> **Moved.** `tasks/TASK_REVIEW_T308.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T308.md`.

---

## Approach

**Pattern reference**: `user_line_confirmed` and `minimal_line_passes` in `.claude/hooks/pre_bash_block_unsafe_merge.py` (T250 G1), and their tests.
**Vital slice**: pass the report file's path into `user_line_confirmed`, and let `verify_row_passes` call it for the `USER_LINE` shape.
**Cut list**:
- No change to the verdict proof (a known limit).
- No change to `[admin]` item 4.
- No new row shape: the minimal track's shape is reused.

Risk: the gate is the one place where a wrong answer is silent and repo-wide (its own docstring). Fail closed on any doubt. Security review is mandatory, and the transcript-forgery limit already in `### Known limits` must be restated, not widened.

---

## Edge Case Checklist

- [ ] A row committed with a `<sha>` that is a branch commit not yet merged: `head` is the branch tip, as on the minimal track.
- [ ] The report file is read from a worktree: the search directories are the same ones `evidence_search_dirs` returns.
- [ ] A row with both a hook-written pass and a user line: either counts; neither edits the other.
- [ ] Pin-test pre-flight: fill `Pre-existing pin tests` before work starts
- [ ] Stale references: grep for "hand-typed", "counts for nothing", `user_line_confirmed`, `USER_LINE`, "minimal-track `verify:` line" in `docs/claude-md/`, `site/`, `README`, `agents/`, `skills/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `user_line_confirmed` takes the report path; `verify_row_passes` accepts the `USER_LINE` shape |
| `.claude/hooks/tests/test_t308_user_verify_extended.py` | new, written by `qa-expert` |
| `docs/claude-md/tracks.md` | lines 437-448, `### Known limits`, `### Final report` `Not done:` item |
| `templates/TASK_REVIEW_template.md` | one clause on where the user's pass goes (AC 6), only if the slot needs it |
| Pre-existing pin tests | grep `.claude/hooks/tests/` and `tests/` for `user_line_confirmed`, `USER_LINE`, `has_filled_verify_row`, `verify_row_passes`, `MINIMAL_LOG_REL` and each edited doc string; always `test_agent_guide_dedup.py`, `test_vital_slice.py`, the memory budget tests. **Found (pre-flight, 2026-11-11, before the change):** code — `test_admin_tag.py:765` (`user_line_confirmed` patched with `lambda *a, **k`), `test_merge_gate_t095.py`, `test_merge_gate_t210.py`, `test_verify_row_fill_detection.py`, `test_guide_sections.py`, `test_t250_session_ownership.py`, `tests/test_auto_mode.py`; the gate-owner allowlist `merge_gate_guard.py` `AUTHORISED_TASKS` (read by `test_stop_auto_mode_check.py::test_merge_gate_is_untouched` and `tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged`: T308 must be added, the file's documented record); docs — `tests/test_auto_mode.py:861-862` (`### Known limits`: "hand-typed `☑ pass`[^.]*ends the check", "merge gate still blocks a hand-typed row at merge"), `tests/test_t306_admin_retry_blocked.py:120-140` (`### Final report` `Not done:` item, 2 lines; template `Not done:` slot), `test_t250_session_ownership.py:646` (the minimal `verify:` line shape in `### Auto verify (Stop hook)`), `tests/test_stage_names.py:210` (row 18) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/verify_record.py` | the path list stays |
| `### Admin tag` text of `docs/claude-md/tracks.md` | T306 and T307 own it |
| `.claude/settings.json` | permissions |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

`qa-expert` writes the oracle first (red). The implementer then changes the gate and the docs until it is green, then runs the full suites. The Supervisor runs code review and security review at High risk.

---

## Completion Checklist

- [ ] Oracle written by `qa-expert`, red
- [ ] Implementation done
- [ ] `code-review` run
- [ ] `security-review` run (High risk; it changes a merge gate)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T308.md` (Hard-Stop Gate 5)
- [ ] The user types `/verify T308` (the auto run may block the same way T306 did)
- [ ] `memory/MEMORY.md` updated (Supervisor)
- [ ] Supervisor notified: ready for Stage 4
