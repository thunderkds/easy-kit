# TASK_GUIDE — T354: the `[admin]`/`[ticket]` loop binds its task after the hook's close-out moved the row to Done
**Date**: 2026-11-25
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read this file completely
3. Read `agents/common-infrastructure.md`
4. Read `docs/claude-md/tracks.md` `### Auto close-out` and `### Session tags`

---

## Requirement (Pillar 1 — Adapt the requirement)

Found 2026-11-25 in the `[admin]` session loop: T347 passed its auto verify, the hook's close-out moved its `Mode: auto` row to Done, and the Supervisor's `git merge --no-ff fix/t347-readme-codex-list` was refused: "T347 is not the task of the `[admin]` request: … nor the task of this session's loop (its row in Ready for Review, …)". The loop binding (T317 R4) requires the row in Ready for Review, but the close-out (T189) moves every `Mode: auto` row to Done right after the pass, before the merge, and every loop ticket is `Mode: auto`. So the loop can never merge (`[admin]`) or push (`[ticket]`) its own task. User, 2026-11-25: "yes, let fix this, cause request users type the "merge A", "merge B" looks useless now".

**Restated intent**:
> The session loop binds its task for the merge (and the `[ticket]` task-branch push) when the row is in Ready for Review, as today, **or** when the row is in Done and carries the hook's own close-out note, `Done <date>: auto verify pass (session <id>, commit <sha>)`, for a commit whose hook pass record is this session's own run (the same `_pass_recorded_since` rule: written after this session's own `--start` call, held by the branch). Every other loop condition is unchanged. A Done row without that note, or whose note names another commit, still does not bind.

**Out of scope**:
- The request binding, the guide binding and the short-yes binding (T323).
- The close-out itself (`.claude/hooks/lib/auto_closeout.py`): it keeps moving the row at once.
- The `main` push rule (it already accepts a Done row).
- T321 (the push remote).

**Depends on**: None (T317, T189 merged)

**Requirement Refs**: None — kit maintenance; source is the refusal above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (signed auto (Supervisor) under `[admin]`; user: "yes, let fix this")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (merge gate, auto close-out, session tag)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: the loop binding in `admin_refusal` (`.claude/hooks/pre_bash_block_unsafe_merge.py`, the `R1`/`R4` block that calls `_ready_for_review`)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Loop `[admin]`: row in Done with the hook's close-out note naming the commit of this run's pass record → `git merge <task branch>` allowed | the loop merges its task |
| 2 | Loop `[ticket]`: the same Done row → `git push origin <task branch>` allowed | ticket too |
| 3 | A Done row with no close-out note (the T317 R4 test) → still refused, under both tags | Done alone never binds |
| 4 | A Done row whose note names a commit with no pass record of this run (another commit, or a record dated before this session's `--start` call) → refused | only this run's close-out |
| 5 | The note written by hand in a Todo row, or in a Ready for Review row of another task → binds nothing new | the note binds only in Done, only its own row |
| 6 | `docs/claude-md/tracks.md` `### Session tags` (gate binding bullet) and the refusal text say "Ready for Review, or Done by the hook's close-out of that same pass" | the user knows |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | loop `[admin]`, Done row + matching note | merge allowed | `test_t354_loop_closed_out_row.py` |
| 2 | loop `[ticket]`, Done row + matching note | push allowed | same file |
| 3 | Done row, no note | refused | same file + `test_t317_fix_round.py::test_r4_a_done_or_todo_row_does_not_bind_the_loop` unchanged |
| 4 | note names another commit / an older record | refused | same file |
| 5 | hand-written note in a Todo row | refused | same file |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t354_loop_closed_out_row.py .claude/hooks/tests/test_t317_fix_round.py .claude/hooks/tests/test_t317_loop_binding.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T354.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T354.md`.

---

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A: hook-only change.

---

## Approach

**Pattern reference**: `_ready_for_review`, `_pass_recorded_since` in `.claude/hooks/pre_bash_block_unsafe_merge.py`; the close-out note in `.claude/hooks/lib/auto_closeout.py:326` (`Done {day}: auto verify pass (session {session}, commit {head})`); fixtures in `.claude/hooks/tests/test_t317_fix_round.py` (`_loop`, `_gate_case`, `pass_written_at`).

**Vital slice**: one helper, `_closed_out_since(task_id, branch, where, when)`: the task's own row under `### Done`, its last close-out note's 40-character commit, and that commit's hook pass record passing the `_pass_recorded_since` rule (record for that sha, written at or after `when`, confirms pass, held by the branch). The loop binding reads `(main_push or _ready_for_review(task_id) or _closed_out_since(...))`.

**Cut list**: binding a Done row that another session's close-out wrote (the record must be after this session's own `--start`, which already covers it); changing the close-out's timing; a new board section.

## Edge Case Checklist

- [ ] The note's commit is the verified commit, not the branch tip (result-file-only commits follow it): the record lookup is by the note's sha, held by the branch
- [ ] Two notes in one row (a re-run): the last one counts
- [ ] A short or malformed sha in the note: no bind
- [ ] Board unreadable: no bind (fail closed)
- [ ] Pin-test pre-flight: `test_t317_fix_round.py` R4 Done test stays red-for-the-right-reason (no note in its row)
- [ ] `merge_gate_guard.py` `AUTHORISED_TASKS` gains T354 with the rule it owns

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_closed_out_since` helper; the loop binding and the refusal text read it |
| `.claude/hooks/tests/test_t354_loop_closed_out_row.py` | new test file (written first) |
| `.claude/hooks/tests/merge_gate_guard.py` | `AUTHORISED_TASKS` += T354 (Supervisor sign-off: the user's "yes, let fix this") |
| `docs/claude-md/tracks.md` | `### Session tags` gate bullet: Ready for Review, or Done by the hook's close-out |
| Pre-existing pin tests | grep the refusal text (`its row in Ready for Review`) in `.claude/hooks/tests` and `tests/` |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/auto_closeout.py` | the close-out timing stays |
| `.claude/settings.json` | no permission change |

---

## Test Plan

Test first (red: the Done-with-note cases refused), then the helper (green), then the gate test files in the Verification Command, then the full suite.

## Completion Checklist

- [ ] Implementation done
- [ ] Reviewer spawn: `code-review` and `security-review` (Risk High)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T354.md`
- [ ] Auto verify started
