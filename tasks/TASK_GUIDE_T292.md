# TASK_GUIDE — T292: One `parse_ts` for the hooks
**Date**: 2026-11-08
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read the review file or doc named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"push and start all as parallel"*, on the follow-up list. Evidence: two copies of the ISO timestamp parser exist: `.claude/hooks/stop_auto_mode_check.py:150` `parse_ts` and `.claude/hooks/lib/session_work.py:33` `parse_ts`. The T250 and T287 reviews both listed the duplicate. `session_work` imports `task_context`, which must never fail to import, so the shared copy must live where both can import it without a cycle.

**Restated intent**:
> The hooks have one `parse_ts` in a `lib/` module that both `stop_auto_mode_check.py` and `session_work.py` import. Its results for every input the two copies handle today stay the same.

**Out of scope** (what this task explicitly does NOT do):
- Changing what either copy returns for any input
- Touching other duplicated helpers (list them as a cut-list note)
- Any change to `.claude/settings.json` or the hook entry points

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/lib/` (a new or existing small module), imported by `stop_auto_mode_check.py` and `lib/session_work.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Before the change, a table test feeds both copies the same inputs (aware ISO, naive, `Z`, fractional seconds, empty, `None`, non-string, garbage) and records their outputs; the two agree or the differences are listed in the review file | Requirement |
| 2 | After the change there is exactly one `def parse_ts` under `.claude/hooks/` and both callers use it; the table test passes against it | Requirement |
| 3 | The fail-closed import guard of the hooks stays: a failed import of the shared module does not crash a hook that must fail closed (existing behaviour kept) | no regression |
| 4 | `grep -rn "def parse_ts" .claude/hooks` prints one line | Requirement |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Table of inputs through both old copies | Same outputs, or the differences listed | characterization test (written first) |
| 2 | Table through the one new copy | Same outputs as the old table | unit test |
| 3 | Mutation: the shared copy returns None for fractional seconds | the table test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "parse_ts or session_work or stop_auto"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
grep -rn "def parse_ts" .claude/hooks
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T292.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T292.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/lib/session_work.py` (it already holds small shared helpers) and how `stop_auto_mode_check.py` imports from `lib/`. Characterise first, then move.

**Vital slice**: the characterization table and the single copy
**Cut list**: no refactor of the surrounding code

---

## Edge Case Checklist

- [ ] `stop_auto_mode_check.py` runs `main()` at import: do not import it in tests; load only the function with `ast` or test through the new module
- [ ] The two copies may differ on naive timestamps: record it, then pick the stricter result and say so in the review file
- [ ] Pin-test pre-flight: grep tests for `parse_ts` before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/lib/session_work.py or a small new lib module | The one copy |
| .claude/hooks/stop_auto_mode_check.py | Import it, delete the copy |
| .claude/hooks/tests/test_parse_ts_single.py (new) | Table tests |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | Not in scope; do not change the gate |
| `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes; hook wiring is unchanged unless this guide says so |

---

## Test Plan

Write the tests for the Acceptance Criteria first and see them fail. Implement. Run the verification command and the full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` (bare `pytest` skips the hidden hook tests). Run each mutation control, paste the red output, restore, and paste the green output.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium/High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
