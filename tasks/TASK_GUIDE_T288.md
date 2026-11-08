# TASK_GUIDE — T288: `tasks/attempts.tsv` — blocked and stopped runs, derived from the event trace
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
6. Read `tasks/SPIKE_REPORT_T283.md` (on branch `feat/t283-karpathy-spikes`; `git show feat/t283-karpathy-spikes:tasks/SPIKE_REPORT_T283.md`), the section named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

From the T283 spike report, section `### 5. Attempt log` and `## Recommendation` item 4. The user approved it on 2026-11-08: *"let do as your recommend"*. Evidence: `memory/event-trace/*.jsonl` is git-ignored and holds every spawn (316) and every handback (290), but cuts each handback summary at 300 characters. 13 handbacks report a blocked or stopped run; only 5 are named in a committed record. 8 are not (T190, T223, T236 second, T249, T250, T255, T267, T268); 7 of those 8 are step-limit stops. A prototype `scripts/attempt_log.py` (branch `spike/t283-attempt-log`, commit `58dd5d51`) derived 17 attempt rows from the trace, 16 correct.

**Restated intent**:
> A committed, readable file `tasks/attempts.tsv` holds one row for each blocked or stopped run: time, task, kind, and the full status line. A script derives the rows from the trace. It adds no hook.

**Out of scope** (what this task explicitly does NOT do):
- A new hook or a change to `.claude/settings.json`
- Logging every spawn (the trace has them; the spike counted 316 rows as noise)
- Rewriting or deleting a row (the file is append-only)
- Reading the file back into any gate or memory pass

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `scripts/attempt_log.py derive` (run by the Supervisor; a line in `docs/claude-md/memory-write-protocol.md` says when)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `scripts/attempt_log.py derive <trace files>` prints rows `time<TAB>task<TAB>kind<TAB>status line` for each handback whose status is `blocked`, or that names the step limit (`kind` = `blocked` or `stopped`) | Requirement |
| 2 | `scripts/attempt_log.py append` adds only the rows `tasks/attempts.tsv` does not hold, never changes an existing row, and running it twice adds nothing | append-only |
| 3 | The status line is kept in full from the handback, not cut at 300 characters, when the handback text has it; when it is cut, the row says `(cut at 300)` | spike finding |
| 4 | Negative: a handback that is `ready-for-review` and only contains the word 'blocked' (T188's second handback in the spike) is not a row | false positive in the spike |
| 5 | Negative: a missing or empty trace folder gives no rows and exit 0, not a crash; a malformed trace line is skipped and counted on stderr | edge |
| 6 | `docs/claude-md/memory-write-protocol.md` says when the Supervisor runs it (at the diff-driven memory pass after a merge), and `memory/`'s rules still hold: only the Supervisor writes `tasks/attempts.tsv` | Supervisor-only writes |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Fixture trace with 1 blocked, 1 step-limit stop, 1 ready-for-review that says 'blocked', 1 normal | 2 rows (blocked, stopped); the 'blocked' word case is not a row | `tests/test_attempt_log.py` |
| 2 | `append` run twice on the same fixture | File unchanged after the second run | same file |
| 3 | Empty folder / malformed line | No rows, exit 0, count on stderr | same file |
| 4 | Mutation: the step-limit regex changed to one that never matches | The stop-row test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_attempt_log.py -q
python3 scripts/attempt_log.py derive memory/event-trace/*.jsonl | head -20
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T288.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T288.md`.

---

## Approach

**Pattern reference**: the spike script `scripts/attempt_log.py` and its test `tests/test_spike_attempt_log_t283.py` on branch `spike/t283-attempt-log` (commit `58dd5d51`): `git show spike/t283-attempt-log:scripts/attempt_log.py`. Start from it, do not copy its false positive. Also `scripts/lane_check.py` for how a kit script reads the repo and prints one line per finding.

The trace folder is git-ignored and exists only in the main checkout; the script takes the folder as an argument and the test uses a fixture, never the real trace.

**Vital slice**: `derive` plus `append` and the false-positive guard (AC 1, 2, 4)
**Cut list**: a backfill of the 8 older missing attempts as a separate commit (the Supervisor can run `append` once; it is not part of this task's tests); any analysis of the rows

---

## Edge Case Checklist

- [ ] The trace holds the same handback twice (resumed run): one row
- [ ] Time stamps in UTC, as the trace has them
- [ ] A status line with a tab or newline: replace with a space so the TSV stays one row per line
- [ ] `tasks/attempts.tsv` absent: `append` creates it with a header row
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| scripts/attempt_log.py (new) | Derive and append |
| tests/test_attempt_log.py (new) | Tests for AC 1–5 |
| docs/claude-md/memory-write-protocol.md | One line: when to run `append` (AC 6) |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| .claude/settings.json and every hook | No new hook |
| memory/event-trace/** | Data; read only |
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
