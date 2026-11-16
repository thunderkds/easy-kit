# TASK_GUIDE — T324: a test run in a task's worktree is not work on the task (Stop check false positive)
**Date**: 2026-11-16
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

## Bug Fix Task Guide — T324

### Mental Model (confirmed: auto (Supervisor), `[admin]` session 2026-11-16 — `docs/claude-md/tracks.md` `### Every user stop and its auto rule` row 13)
- Observed: session `ebb01feb` had no `[auto]`/`[admin]` tag. It only ran T321's locked oracle read-only (`cd /home/hungnguyenhuu/workspace/pets/wt-t321 && timeout 300 python3 -m pytest .claude/hooks/tests/test_t321_admin_remote.py -q --no-header -p no:cacheprovider -rf 2>&1 | tail -40`). At its stop, `.claude/hooks/stop_auto_mode_check.py` blocked with three T321 reasons (`Risk High, but no decision was DEBATED with 3 Advocates`; `the trace has 0`; `no security-review Skill call`). On the second fire it appended `Paused: auto-mode check failed — …` to `../wt-t321/tasks/TASK_REVIEW_T321.md`, a task another session owns.
- Expected: a session that only reads a task and runs its tests does not own it. The T252 ownership skip applies: the Stop check skips the task (one stderr note) and writes nothing to its report.
- Likely divergence point: `.claude/hooks/lib/session_work.py` `_bash_works` → `_read_only(tokens)`. `timeout` and `python3 -m pytest` are not in `READ_ONLY_COMMANDS`, so a test run whose directory is inside the task's worktree returns True, `worked_on()` is True, and the T252 skip does not fire. Repro (Supervisor, 2026-11-16): `worked_on([("Bash", {"command": "cd <wt-t321> && timeout 300 python3 -m pytest x.py -q"}, main)], "T321", [<wt-t321>])` → `True`; the same with `grep … tasks/TASK_REVIEW_T321.md` → `False`.
- Recent context: T250 (ownership rule, `session_work.py`), T252 (the rule also for a report already marked `Mode: auto`), T287 (a test run in a worktree is filed under the task in the event trace, for item 7 and the close-out), T293 (a task's change window starts at its first `worked_on` call). `session_work.py` is also read by `.claude/hooks/pre_bash_block_unsafe_merge.py` (T250 G2: an In Progress task blocks a merge only when this session worked on it; the `[admin]` loop binding "This session changed it since the tag request"), `lib/task_context.py` and `lib/auto_mode.py`.

### Intake
- Trigger: in a session with no auto tag, run a task's tests inside its worktree, where the task's review file carries `Mode: auto`, Risk Medium/High, and its Debates/reviews are not yet in the trace; then stop.
- Severity: P1 (blocks every stop of a session that checks another session's auto task; writes a false `Paused:` line into that task's report).
- Affected area: `.claude/hooks/lib/session_work.py` (and/or `.claude/hooks/stop_auto_mode_check.py`, per the Design decision below).

### Complexity & Risk
- Complexity: C2 (a design choice in a shared ownership library read by the Stop check and the merge gate)
- Risk: High (it changes which tasks a gate checks; the same library decides merge-gate ownership)

## Design decision

Debated (3 Advocates, 2026-11-16; `tasks/TASK_REVIEW_T324.md` `## Auto decisions` decision 1). Option D:

- `.claude/hooks/lib/session_work.py`: `worked_on(calls, task_id, worktrees, *, test_runs_count=True)` and `work_start(entries, task_id, worktrees, *, test_runs_count=True)`, passed through `_works` and `_bash_works`. With `test_runs_count=False`, one simple command that is a **test run** is not work. A test run is: `pytest` / `py.test`, or `python` / `python3` [flags from `task_context.PYTHON_FLAGS`] `-m pytest|unittest`, optionally behind exactly one `timeout <n>` prefix (`\d+[smhd]?`), with no output redirect to a real file (the existing redirect guard of `_read_only` runs first). Reuse or mirror `lib/task_context.py` `_allowed_command` (lines 454-480); do not write a looser third parser.
- The default stays `True`: `.claude/hooks/pre_bash_block_unsafe_merge.py` (T250 G2 at line 1374, T317 `_session_holds` at line 2282), `lib/auto_mode.py`, `lib/task_context.py` and every T250/T252/T293 test keep today's meaning. `pre_bash_block_unsafe_merge.py` is **not** changed (it is guarded by `.claude/hooks/tests/merge_gate_guard.py`).
- `.claude/hooks/stop_auto_mode_check.py`: `session_owner` and `session_window` both pass `test_runs_count=False`, so ownership and the Debate window keep one test (`session_work.py:362` "Same test as `worked_on`, so the two never disagree").
- Rejected: (A) the exemption for every caller — it changes the user-approved T250 G2 merge-gate meaning (`pre_bash_block_unsafe_merge.py:1290` "an edit, a writing `Bash` command or a spawn") and flips the pinned `test_t250_session_ownership.py:141`, `:146`; (B) skip by session tag — breaks T252 (a marked task is checked by ownership, not by tag; `stop_auto_mode_check.py:31`) and fails open on an unreadable transcript.

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | With `test_runs_count=False`, `worked_on` is False for a test run inside the task's worktree: the incident command `cd <wt> && timeout 300 python3 -m pytest <file> -q --no-header -p no:cacheprovider -rf 2>&1 \| tail -40`, plus `python3 -m pytest -q` with cwd in the worktree, `pytest -q`, `py.test`, `python3 -B -m unittest`, `timeout 60 python -m pytest` | Expected |
| 2 | With `test_runs_count=False`, these stay work (True): `timeout 300 rm -rf x` in the worktree; `python3 -m pytest -q > <wt>/out`; `python3 tool.py` in the worktree; `pytest -q && rm x` in the worktree; `timeout 5 timeout 5 python3 -m pytest`; a test run plus an `Edit` of the task's review file; every write/commit/spawn case of `test_t250_session_ownership.py` | no fail-open |
| 3 | Without the keyword (default `True`), every case above returns exactly what it returns today (a test run in the worktree is work); `pre_bash_block_unsafe_merge.py` is byte-identical to `main` | merge gate unchanged |
| 4 | `work_start(..., test_runs_count=False)` returns the time of the first call that `worked_on(..., test_runs_count=False)` counts (a test run before the first edit does not start the window); with the default it is unchanged | one test for both |
| 5 | Stop hook end to end: a session transcript with no tag whose only call on a marked `Mode: auto`, Risk High task (in its own worktree, Debates/reviews missing) is the incident test run → the stop is not blocked, stderr names the task as "not checked", and the task's review file is byte-identical after a first and a second (`stop_hook_active`) fire. The same transcript plus an `Edit` of that review file → blocked as today | the incident |
| 6 | `session_owner` and `session_window` in `stop_auto_mode_check.py` both pass `test_runs_count=False` | one test for both |

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A: hook-only change.

### Diagnosis Gates (Pillar 1 — must pass before any fix)
- [x] Phase 1 feedback loop built and running (the `worked_on` repro above)
- [x] Bug reproduces deterministically on the loop
- [ ] 3–5 ranked falsifiable hypotheses listed (consistent with confirmed mental model)
- [ ] Correct hypothesis identified via Phase 4 instrumentation

### Attempts Log (filled live during diagnosis — required if >1 hypothesis tested)
| # | Hypothesis | Predicted signal | Actual result | Verdict |
|---|---|---|---|---|

### Fix Gates (Pillar 2)
- [ ] Regression test written before the fix (or no-seam documented)
- [ ] Fix applied; regression test passes
- [ ] Phase 1 loop no longer reproduces the bug
- [ ] Fix matches the "correct behaviour" definition from the mental model

### Cleanup Checklist (Pillar 3)
- [ ] All [DEBUG-...] instrumentation removed (grep verified)
- [ ] Throwaway prototypes deleted
- [ ] Correct hypothesis stated in commit message
- [ ] Post-mortem: what would have prevented this?

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T324.md`.

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T324.md`.

## Files to Change (Predicted)

- `.claude/hooks/lib/session_work.py`
- `.claude/hooks/stop_auto_mode_check.py`
- `.claude/hooks/tests/test_t324_test_run_not_work.py` (new, qa-expert, locked)

## Evaluation & Acceptance

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t324_test_run_not_work.py`. The implementer may not edit it.

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

## Approach

**Pattern reference**: `_read_only` / `_bash_works` in `lib/session_work.py`; `_allowed_command` in `lib/task_context.py`; `session_owner` / `session_window` in `stop_auto_mode_check.py`; fixtures in `test_t250_session_ownership.py` and `test_t252_marked_ownership.py`.
**Vital slice**: one `_test_run(tokens)` predicate and one keyword threaded through `_works` → `_bash_works`, used by the two Stop-hook readers.
**Cut list**: removing the false `Paused:` line already written to `../wt-t321/tasks/TASK_REVIEW_T321.md` (another session's file; reported to the user); `sh -c`/`eval` test runs (stay work); conftest/plugin writes made by a test run (known limit, as `python3 -c`).

## Questions Log
- 2026-11-16 DEBATE how should the fix stop a read-only test run from making a session own another session's auto task? → D: a `test_runs_count` keyword in `session_work`, off only in the Stop hook (Advocate 1: D, flag for `worked_on` and `work_start`; Advocate 2: D, flag for `worked_on` only; Advocate 3: A, test runs are not work for every caller) ⚠ decided for you — please review
