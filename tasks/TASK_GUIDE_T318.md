# TASK_GUIDE — T318: `stop_auto_mode_check.py` does not read its own `Paused:` line as a decision
**Date**: 2026-11-25
**Complexity Level**: C1
**Risk Level**: Medium
**Priority**: P2
**Assigned agent**: common-infrastructure (the Supervisor writes the code, DDR-0011)
**Agent guide**: `agents/common-infrastructure.md`

> Read relevant files from `docs/legacy/` before making any code changes. (This repo has no `docs/legacy/`: `PROJECT_SPEC.md` and `docs/claude-md/` are the source of truth.)

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in the spawn prompt, if any; read `memory/MEMORY.md` only if the work reaches what it misses
3. Read this file completely
4. Read `agents/common-infrastructure.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "continue your work by picking tasks [admin]". The task is the board row registered 2026-11-15 from the T314/T317 run.

**Problem**: `stop_auto_mode_check.py` writes `Paused: auto-mode check failed — <reasons> [report <stamp>]` into the report. The reasons quote earlier report text that holds `⚠`. On the next fire the check reads that `Paused:` line as a decision. At Risk Medium or High it reports "`Paused: auto-mode check failed — Risk Hi` (`⚠`) is a choice … must be DEBATED". The hook then blocks on its own output.

**Restated intent**: lines the hook itself writes (`STAMP_SKIPS`: `Paused:`, `Closed:`, `Not done:`, `**Not done:**`, `- verify:`) are not decisions. `STAMP_SKIPS` already says these are "lines no check reads". The decision checks (per-line choice check and the `DEBATED` count) skip them too. No real decision stops being checked.

**Out of scope**: the stamp logic, the Advocate trace count, the merge gate.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row — auto (Supervisor), `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: none
**Entry point**: `.claude/hooks/stop_auto_mode_check.py` (Stop hook), `check_task`.

---

## Acceptance Criteria

1. At Risk High, a correct report that holds a `Paused:` line quoting `⚠` passes the check (no block).
2. A `Closed:`, `**Not done:**` or `- verify:` line quoting `⚠` is not read as a decision either.
3. A real flagged decision still blocks when a `Paused:` line sits beside it, and the reason names that decision.
4. Every test in `test_stop_auto_mode_check.py` passes unchanged.

## Evaluation & Acceptance

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | good report + `Paused:` line with `⚠`, Risk High | no block | automated (`test_t318_paused_line_not_a_decision.py` AC 1) |
| 2 | each other skipped prefix with `⚠` | no block | automated (same file, AC 2) |
| 3 | real flagged FACT + `Paused:` line | block names decision 3 | automated (same file, AC 3) |
| 4 | existing suite | all pass | automated (`test_stop_auto_mode_check.py`) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t318_paused_line_not_a_decision.py .claude/hooks/tests/test_stop_auto_mode_check.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T318.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T318.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: Stop hook logic.

---

## Approach

**Vital slice**: one change in `check_task`: build `lines` without lines that start with `STAMP_SKIPS`. Both readers of `lines` (the per-line choice check, the `DEBATED` list) are decision readers, so both are fixed at the source.

| Option | Invasiveness | Regression risk | Chosen |
|---|---|---|---|
| A. Filter `lines` once where it is built | Low: one line | a decision line that starts with a skipped prefix stops being read; none is a decision by T186's definition | **yes** |
| B. Skip the prefixes inside `choice_reason` only | Low | the `DEBATED:` count still reads a `Paused:` line that quotes `DEBATED:` | no |

**Cut list**: none.

---

## Edge Case Checklist

- [x] A numbered decision never starts with a skipped prefix (`1. …`), so none is dropped
- [x] Pin-test pre-flight: no other test reads `check_task` text or line counts (grep of `stop_auto_mode_check` in tests)
- [x] Stale text: the module docstring already says the stamp skips these lines; no doc change needed

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/stop_auto_mode_check.py` | `lines` skips `STAMP_SKIPS` lines (1 line + 1 comment) |
| `.claude/hooks/tests/test_t318_paused_line_not_a_decision.py` (new) | AC 1–3 |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | the merge gate has its own owner list |
| `.claude/settings.json` | no wiring change |

---

## Test Plan

Test first: the new file fails on `main` (AC 1 and AC 2 fail, AC 3 passes). Then the change, then the Verification Command.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` not required (Medium risk, no auth or input surface; run if the reviewer asks)
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T318.md` Evidence
- [ ] Auto verify pass
- [ ] Board current

---

## Questions Log

None.
