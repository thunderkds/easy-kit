# TASK_GUIDE — T254: hook tests drop `CLAUDE_AUTO_VERIFY_RUN` from the env they pass to `stop_auto_mode_check.py`
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

User, 2026-11-25: "start the task as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: Hook tests clear `CLAUDE_AUTO_VERIFY_RUN`: `stop_auto_mode_check.py` `main()` exits at once when it is set (true inside every headless auto verify run), and the test env helpers (`gate_env` in `.claude/hooks/tests/test_t250_session_ownership.py`, `_run` in `test_stop_auto_mode_check.py`, `test_t252_marked_ownership.py`) pass it through, so the block tests fail for an unrelated reason when the suite runs inside a verify session; drop it from the test env.

**Restated intent**:
> The tests that run `stop_auto_mode_check.py` as a subprocess build their env without `CLAUDE_AUTO_VERIFY_RUN`, so they give the same result inside a headless auto verify run as outside. Test code only; the hook is unchanged.

**Out of scope**: `stop_auto_mode_check.py` itself; other hooks' tests unless they run this hook the same way.

**Depends on**: None

**Requirement Refs**: None — kit maintenance; source is the board row above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: the env helpers in the three named test files

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | With `CLAUDE_AUTO_VERIFY_RUN=1` exported, `python3 -m pytest .claude/hooks/tests/test_t250_session_ownership.py .claude/hooks/tests/test_stop_auto_mode_check.py .claude/hooks/tests/test_t252_marked_ownership.py -q` gives the same pass/fail list as without it | same result in a verify run |
| 2 | No hook source file changes | test only |

## UI / Design Acceptance Criteria

Not applicable — no UI.

---

## Evaluation & Acceptance

**Locked oracle**: the new test named under Files to Change, written first (red), then the fix.

### Verification Command (exact, runnable)

```bash
CLAUDE_AUTO_VERIFY_RUN=1 python3 -m pytest .claude/hooks/tests/test_t250_session_ownership.py .claude/hooks/tests/test_stop_auto_mode_check.py .claude/hooks/tests/test_t252_marked_ownership.py -q -p no:cacheprovider
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/TASK_REVIEW_T254.md` (extended) or `tasks/MINIMAL_LOG.md` (minimal).

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T254.md` (extended) or the `tasks/MINIMAL_LOG.md` record (minimal).

---

## Approach

In each helper that builds the subprocess env (`{**os.environ, ...}`), drop `CLAUDE_AUTO_VERIFY_RUN` (e.g. `env.pop("CLAUDE_AUTO_VERIFY_RUN", None)`). grep for other helpers that run this hook the same way and treat them alike. BEFORE: run the Verification Command before the change and paste its result.

## Files to Change (Predicted)

- `.claude/hooks/tests/test_t250_session_ownership.py`
- `.claude/hooks/tests/test_stop_auto_mode_check.py`
- `.claude/hooks/tests/test_t252_marked_ownership.py`

## Files must NOT touch

- `PROJECT_KANBAN.md` (the Supervisor moves rows), `.claude/settings.json`, `.claude/hooks/pre_bash_block_unsafe_merge.py`
