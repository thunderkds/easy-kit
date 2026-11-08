# TASK_GUIDE — T285: Step limit counts per sub-agent run (agent_id), not per session and task
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: Medium
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

From the T283 spike report, section `### 4. Time budget` and `## Recommendation` item 1. The user approved it on 2026-11-08: *"let do as your recommend"*. Evidence: `.claude/hooks/pre_agent_step_limit.py` keys its counter on session and task (`step_count_<session>_<task>.txt`), so parallel sub-agents of one task share one budget of 90 tool calls. It stopped 6 real runs (T173, T249, T250, T255, T266, T267), some after 3.4 min (T267) or after 8 of a reviewer's own calls (T266), and it stopped Run B of T283.

**Restated intent**:
> A sub-agent run has its own step budget. One run that hits 90 calls is stopped alone. Two parallel runs with one Task ID never share a count. A runaway loop is still stopped.

**Out of scope** (what this task explicitly does NOT do):
- A wall-clock limit (the T283 spike dropped it: 0 runaways in 127 runs)
- Raising `CLAUDE_STEP_LIMIT` or changing the self-clearing block (T057) or the escalation wording
- A cap on the total calls of one task across all runs (listed in the cut list)
- `.claude/settings.json` wiring

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/pre_agent_step_limit.py` (PreToolUse, all matchers; counter file name built from the event)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A hook event from a sub-agent (it carries `agent_id`) is counted in a counter keyed on session, agent and task. Two agents with the same session and Task ID have two counters | Requirement |
| 2 | An event with no `agent_id` (the main thread) keeps the counter key it has today, so the Supervisor's budget is unchanged | Requirement |
| 3 | One agent's 90th call is blocked; the next call of another agent of the same task is allowed | Requirement |
| 4 | Negative: a single agent that loops past `CLAUDE_STEP_LIMIT` is still blocked, and the T057 self-clearing reset and `block_count` escalation still work | a runaway is still stopped |
| 5 | Negative: an `agent_id` with unsafe characters is reduced to a safe file-name fragment, as `session_id` is; a non-string `agent_id` falls back to the main-thread key (fail safe, never unlimited) | untrusted input |
| 6 | The hook's docstring and `docs/claude-md/` text that describe the counter key name the new key and state no old fact | stale-text rule (LR-0005) |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Events of agents A and B, same session and task, 60 calls each | No block; two counter files | `.claude/hooks/tests/test_step_limit_agent_scope.py` |
| 2 | Events of agent A only, 91 calls | Call 91 blocked; counter reset; next call allowed | same test file (regression of T057) |
| 3 | Event with no `agent_id`, 91 calls | Blocked under today's key | same test file |
| 4 | `agent_id` = `../../x` or 12345 | Safe file name, or main-thread key; no path outside `.state/` | same test file |
| 5 | Mutation: drop the agent fragment from the key | The A-and-B test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_step_limit_agent_scope.py .claude/hooks/tests/test_step_limit_session_scope.py .claude/hooks/tests/test_step_limit_self_clearing.py -q
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T285.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T285.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/tests/test_step_limit_session_scope.py` and the T056 change that added the session to the key: imitate how it sanitises `session_id` (`_sanitize_session_id`) and add the same for `agent_id`. Read how `lib/task_context.py` reads `agent_id` for the spawn binding (T196).

The counter name becomes `step_count_<session>_<agent>_<task>.txt` when `agent_id` is present. Old counter files age out by the 6 h TTL; do not migrate them.

**Vital slice**: the key change plus its sanitiser (AC 1, 3, 5)
**Cut list**: a cap on a task's total calls across runs (more runs now mean more total calls; record it as a follow-up if the data asks for it); a migration of old counter files

---

## Edge Case Checklist

- [ ] Existing runs mid-flight when the hook is updated keep an old counter file: it ages out, never read twice
- [ ] Two agents with the same `agent_id` (a resumed run via `SendMessage`) share one counter: that is intended, one run
- [ ] `agent_id` is absent on every event in a harness that does not send it: behaviour equals today's, never looser
- [ ] The fail-open import guard of this hook stays as it is
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/pre_agent_step_limit.py | Counter key and docstring |
| .claude/hooks/tests/test_step_limit_agent_scope.py (new) | Tests for AC 1–5 |
| `docs/claude-md/` or `AGENTS.md` text naming the counter key, if any | State the new key (AC 6) |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| .claude/hooks/lib/task_context.py | Task resolution is not part of this change |
| .claude/hooks/tests/test_step_limit_session_scope.py, test_step_limit_self_clearing.py | Existing tests are the regression oracle; do not weaken them |
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
