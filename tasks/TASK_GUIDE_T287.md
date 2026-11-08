# TASK_GUIDE — T287: Auto-mode Stop check files a task's test, review and Advocate calls under the task they serve
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
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

From the T283 spike report, section `### 6. No check-ins` and `## Recommendation` item 3. The user approved it on 2026-11-08: *"let do as your recommend"*. Evidence: of 11 real `Paused:` stops in the kit's records, 10 were avoidable and 0 came from `### Stops that stay`. 4 were the marker check firing on tasks with no `Mode: auto` (fixed by T229). 6 were one cause: the work ran and the report shows it, but `stop_auto_mode_check.py` read the wrong trace file (T219, T226, T242 twice, T120 twice: tests, `code-review`, `security-review` and Advocate calls filed under another task).

**Restated intent**:
> When a task's tests, reviews or Advocate calls ran, the Stop check finds them in the trace of that task, so it does not pause the task for work that was done. Every stop that stays still stops.

**Out of scope** (what this task explicitly does NOT do):
- Dropping or loosening any stop, including the T218 Gate 6 stop and everything in `### Stops that stay`
- Changing the `verify` row rule or the merge gate
- Changing the auto verify run
- Any change to `[admin]` handling (T284 owns it)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: T284 — it moves `request_text` into `lib/auto_mode.py` and changes `stop_auto_mode_check.py`; start after T284 is merged

**Entry point**: `.claude/hooks/stop_auto_mode_check.py` (Stop hook; its trace reader) and `.claude/hooks/lib/task_context.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Reproduce first: for each of T219, T226, T242 and T120, write a test fixture (a trace file plus a report) that shows the Stop check pausing although the work ran. The root cause of each is written in `tasks/TASK_REVIEW_T287.md` with a file:line. If the 6 stops have more than one cause, each cause gets its own AC row before any fix | Requirement |
| 2 | After the fix, a task whose tests, `code-review`, `security-review` and Advocate calls are in its own trace (or in a trace the session ownership rules attribute to it) is not paused for missing evidence | Requirement |
| 3 | Negative: a task with no such calls in any attributed trace is still paused, with the same message as today | every stop stays |
| 4 | Negative: a call made by another session for another task is not credited to this task (T250 session ownership still holds) | T250 rule |
| 5 | Negative: no stop in `### Stops that stay` changes: a safety-hook block, a delete with no backup, the 4th Debate, a paid action, a missing secret, the same agent at the step limit twice each still pause | ### Stops that stay |
| 6 | `docs/claude-md/tracks.md` `### Known limits` and any text that names this attribution gap state the new behaviour | stale-text rule (LR-0005) |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Fixture of T219/T226/T242/T120-shaped traces | The Stop check finds the work; no pause | `.claude/hooks/tests/test_stop_attribution_t287.py` |
| 2 | Same fixture with the work removed | Pause as today | same file |
| 3 | A trace of another session and task | Not credited | same file |
| 4 | Each Stops-that-stay case | Still pauses | same file |
| 5 | Mutation: credit every trace file to every task | The not-credited test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T287.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T287.md`.

---

## Approach

**Pattern reference**: T250's session-ownership change and its tests (`.claude/hooks/tests/test_t250_session_ownership.py`, `test_t252_marked_ownership.py`): imitate how they attribute by session and event trace and how they build trace fixtures. Read `stop_auto_mode_check.py` `check_task` and `lib/task_context.py`.

Start with the reproduction (AC 1): the spike report counts the symptom, not the cause, so do not fix anything before each of the 6 cases has a failing fixture and a named cause. If a case turns out to be a real stop (the work did not run), say so in the review file and drop that row; do not force a pass.

**Vital slice**: the reproduction of the 6 cases and the one fix for the cause they share
**Cut list**: a rewrite of the trace format; any new Stop hook

---

## Edge Case Checklist

- [ ] Parallel sessions: two sessions work on two tasks at once (the case that caused the first mis-filings)
- [ ] A sub-agent's calls carry its own `agent_id` and transcript; check which file the hook reads for them
- [ ] A task renamed or re-registered mid-run
- [ ] Fail closed: an unreadable trace still pauses the task, as today
- [ ] Do not edit trace files by hand to make a fixture pass
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/stop_auto_mode_check.py | Attribution of evidence to a task |
| .claude/hooks/lib/task_context.py | Only if the cause is there (read first; change the minimum) |
| .claude/hooks/tests/test_stop_attribution_t287.py (new) | Tests for AC 1–5 |
| docs/claude-md/tracks.md `### Known limits` | AC 6 |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| .claude/hooks/pre_bash_block_unsafe_merge.py | Merge gate; not part of this change |
| .claude/hooks/stop_auto_verify.py | Auto verify run; not part of this change |
| memory/event-trace/** | Trace files are data; never edited |
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
