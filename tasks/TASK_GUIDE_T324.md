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

Set by the Debate in `tasks/TASK_REVIEW_T324.md` `## Auto decisions` (filled before the oracle is written).

## Acceptance Criteria

Filled after the Debate; each traces to the Mental Model above.

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
- `.claude/hooks/tests/test_t324_test_run_not_work.py` (new, qa-expert, locked)
