# TASK_GUIDE — T253: the Update summary says what was and was not replaced when a backup fails
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`
**Track**: minimal

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

> Read relevant files from `docs/legacy/` before making any code changes (this repo has none: skip when absent).

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-25: "start the task as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: Update `[o]verwrite`: a failed backup does not stop the run (`lib/harness-update.sh` records `backup_failed` and goes on), so later paths are installed too; the T119 abort text says only that paths before it were installed — make the Update summary say what was and was not replaced.

**Restated intent**:
> After an Update where a backup failed, the user reads, in the summary, which paths were replaced and which were kept because their backup failed; no message claims that only paths before the failure were installed. First confirm the defect still exists on current `main`: T174 added an update log/summary that prints `kept (backup failed: …)` (`lib/harness-update.sh` ~line 864). If the summary and every abort/failure text already say this truthfully, change no code: report the evidence (the exact lines and a test that shows it) and stop.

**Out of scope**: the backup mechanism itself; stopping the run on a failed backup.

**Depends on**: None (T119, T174 Done)

**Requirement Refs**: None — kit maintenance; source is the board row above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: None (T119, T174 Done)

**Entry point**: `lib/harness-update.sh` update summary (`backup_failed` outcome)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A run where one backup fails and a later file is overwritten: the summary lists the failed path as kept (backup failed) and the later path as overwrote/refreshed | what was / was not replaced |
| 2 | No output text claims the paths after a failed backup were not installed (or only those before it were) | the misleading text |

## UI / Design Acceptance Criteria

Not applicable — no UI.

---

## Evaluation & Acceptance

**Locked oracle**: the new test named under Files to Change, written first (red), then the fix.

### Verification Command (exact, runnable)

```bash
bash tests/test_update.sh
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/TASK_REVIEW_T253.md` (extended) or `tasks/MINIMAL_LOG.md` (minimal).

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T253.md` (extended) or the `tasks/MINIMAL_LOG.md` record (minimal).

---

## Approach

Read `process_one_file`, `record_outcome`, the summary printer (~line 850-871) and every text that mentions a backup failure or T119. Find the T119 text (grep `T119`, `backup`, `before it` in `lib/` and `tests/`). Add or extend a case in the update test that forces a backup failure (an existing test may already do so: grep `backup_failed` in `tests/`).

## Files to Change (Predicted)

- `lib/harness-update.sh` (only if the defect is still there)
- `tests/test_update.sh` or the existing test that covers `backup_failed`

## Files must NOT touch

- `PROJECT_KANBAN.md` (the Supervisor moves rows), `.claude/settings.json`, `.claude/hooks/pre_bash_block_unsafe_merge.py`
