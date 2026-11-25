# TASK_GUIDE — T206: a bare or extra-arg `stop_auto_verify.py --start` exits 2 with a usage line
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Medium
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`
**Track**: extended

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

User, 2026-11-25: "start the task as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: `stop_auto_verify.py --start` with no task ID falls through to `stop_hook()` and starts a paid run for every due task; make a bare or extra-arg `--start` exit 2 with a usage line.

**Restated intent**:
> `python3 .claude/hooks/stop_auto_verify.py --start` with no task ID, or with more than one argument after it, must never reach `stop_hook()`: it prints one usage line to stderr (`usage: stop_auto_verify.py --start <TASK_ID>`) and exits 2, starting no run. `--start <ID>` (exactly one argument) and every other entry (`--run …`, the plain Stop hook call) are unchanged.

**Out of scope**: the `--run` argument count; what `start_one` does with a valid ID; any other hook.

**Depends on**: None (T203 is Done)

**Requirement Refs**: None — kit maintenance; source is the board row above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: None (T203 is Done)

**Entry point**: `main()` in `.claude/hooks/stop_auto_verify.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `--start` alone → exit 2, usage line on stderr, `stop_hook()` not called, no run record or child process | bare `--start` |
| 2 | `--start T1 T2` (and `--start T1 extra`) → exit 2, same usage line, no run | extra-arg |
| 3 | `--start T900` → `start_one("T900")` called as before | unchanged |
| 4 | no args (the Stop hook) and `--run …` behave as before | unchanged |

## UI / Design Acceptance Criteria

Not applicable — no UI.

---

## Evaluation & Acceptance

**Locked oracle**: the new test named under Files to Change, written first (red), then the fix.

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/TASK_REVIEW_T206.md` (extended) or `tasks/MINIMAL_LOG.md` (minimal).

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T206.md` (extended) or the `tasks/MINIMAL_LOG.md` record (minimal).

---

## Approach

In `main()`, add a branch before the `stop_hook()` fallback: `elif len(sys.argv) >= 2 and sys.argv[1] == "--start":` print the usage line to stderr and `sys.exit(2)`. Test by running the script as a subprocess with `CLAUDE_AUTO_VERIFY` unset and a patched/absent claude binary, or by loading the module and monkeypatching `stop_hook`/`start_one` to record calls (see existing tests of this file: `grep -ln stop_auto_verify .claude/hooks/tests/`).

## Files to Change (Predicted)

- `.claude/hooks/stop_auto_verify.py`
- `.claude/hooks/tests/test_t206_start_usage.py` (new)

## Files must NOT touch

- `PROJECT_KANBAN.md` (the Supervisor moves rows), `.claude/settings.json`, `.claude/hooks/pre_bash_block_unsafe_merge.py`
