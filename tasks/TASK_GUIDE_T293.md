# TASK_GUIDE — T293: A Debate counts for its task only inside that task's work window
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: Medium
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

User, 2026-11-08: *"push and start all as parallel"*. Evidence: `tasks/TASK_REVIEW_T287.md` item `P3 session window`: "Debates of the whole session count, not only recent ones ... Today a Debate counts for its named task for the whole session." The Stop check (`.claude/hooks/stop_auto_mode_check.py` `_debate_counts`, `_debate_task`) credits any Advocates run after a `resolve-question` Skill call with `task=<ID>` to that task, with no time limit, so an old Debate for the task name can satisfy the High-risk check for work done much later.

**Restated intent**:
> A Debate counts for task `<ID>` only when the `resolve-question` Skill call with `task=<ID>` and its Advocates fall inside the window in which the task's files changed in this session (the same window `session_work.py` uses to decide this session worked on the task). A Debate older than that window does not count.

**Out of scope** (what this task explicitly does NOT do):
- Changing how many Advocates a risk level needs
- Changing the report format or the other Stop checks
- Counting Debates from other sessions (T250 session ownership stays)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/stop_auto_mode_check.py` (`_debate_counts`, `_debate_task`) using `.claude/hooks/lib/session_work.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A Debate whose Skill call and Advocates are dated inside the task's work window counts (today's behaviour) | Requirement |
| 2 | Negative: a Debate for `task=T242` dated before the task's first change in this session does not count for T242; the check still pauses with today's message | Requirement |
| 3 | Negative: a Debate with a missing or unparsable timestamp does not count (fail closed) | fail closed |
| 4 | A task with no recorded change window in this session keeps today's rule (whole session) and the review file states it | no surprise pauses |
| 5 | `docs/claude-md/tracks.md` Known limits and the `P3 session window` line are updated; no stale text (LR-0005) | stale-text rule |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Debate inside the window | counted | unit test over a fixture transcript |
| 2 | Debate before the window | not counted, same pause text | unit test |
| 3 | Debate with bad timestamp | not counted | unit test |
| 4 | Mutation: window check always True | the before-window test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "debate or stop_auto or session_work"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T293.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T293.md`.

---

## Approach

**Pattern reference**: `_debate_counts` and `_own_session_files` in `.claude/hooks/stop_auto_mode_check.py` (T287) and how `session_work.py` finds a task's change window. Reuse that window; do not write a second one.

**Vital slice**: the window check on top of the existing session-file reader
**Cut list**: no new setting; no change to the 6-hour `_untagged.jsonl` fallback in this task

---

## Edge Case Checklist

- [ ] A Debate that starts just before the first change of the task (planning) while the work follows: decide the boundary and write it in the review file (prefer: count a Debate from the task's guide creation commit, if the window logic exposes it)
- [ ] Clock skew between transcript and git times
- [ ] Pin-test pre-flight: T287's `test_stop_attribution_t287.py` Debate tests are run before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/stop_auto_mode_check.py | Window check in `_debate_counts` |
| .claude/hooks/tests/test_debate_window.py (new) | Tests |
| docs/claude-md/tracks.md | Known limits line |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | Not in scope |
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
