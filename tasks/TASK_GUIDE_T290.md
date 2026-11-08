# TASK_GUIDE — T290: Locked oracle: a task guide can lock its oracle test while the task runs
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: High
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
6. Read `tasks/SPIKE_REPORT_T283.md`, the section named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

From the T283 spike report, section `### 1. Locked judge` (verdict `adapt`) and the user's "let do as your recommend" of 2026-11-08, which left this idea without a guide because it needs a hook entry in `.claude/settings.json`. Evidence in the report: the T082 implementer weakened T066's guard test (`7448c0cd`, `x <= x`) and recorded an approval that was never given; the spike `spike/t283-locked-judge` (commit `22a87330`) denies a sub-agent other than `qa-expert` an Edit or Write to a file the guide lists as `**Locked oracle**:`, allows the main thread, and fails closed; the hook input carries `agent_id` and `agent_type` (Claude Code 2.1.319). A permanent file lock is wrong: 52 later edits to `test_agent_guide_dedup.py`, 43 "repoint" (LR-0004). So the lock holds only while the task is In Progress.

**Restated intent**:
> A task guide may list oracle files on a `**Locked oracle**:` line. While that task's board row is In Progress, a PreToolUse hook denies a sub-agent that is not `qa-expert` an Edit or Write to those files. The Supervisor (main thread) and `qa-expert` may edit them. When the row leaves In Progress the lock ends.

**Out of scope** (what this task explicitly does NOT do):
- A permanent lock on any file
- The 8 self-authored LR-0003 cases (a lock on another author's file does not reach them; the mutation-control rule stays the control)
- Locking by `Bash` redirects or `sed -i` (state it as a known limit; do not parse shell)
- A change to who writes the oracle: the Supervisor or `qa-expert` writes it first (T283 and T284 did)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: a new PreToolUse hook on `Edit|Write|MultiEdit|NotebookEdit`, wired in `.claude/settings.json` (needs the user's approval: the Supervisor asks at Stage 3 before the wiring commit, even in a run that stops for nothing else)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A guide with a `**Locked oracle**: <path>[, <path>]` line and a board row In Progress: an Edit or Write of one of those paths by a hook event that has `agent_id` and an `agent_type` other than `qa-expert` or `easy-kit:qa-expert` is denied with a message that names the guide | Requirement |
| 2 | The same Edit by `qa-expert`, or by the main thread (no `agent_id`), is allowed | Requirement |
| 3 | After the row moves out of In Progress (Ready for Review, Done, Blocked), the same Edit is allowed | lock is for the task's length |
| 4 | Fail closed on unreadable input for a path that the hook cannot clear; allow when no guide names the path (no guide, no lock) | safety |
| 5 | The guide template gets the optional `**Locked oracle**:` line with one sentence of when to use it; `agents/common-infrastructure.md` and the other implementer guides do not need it | stale-text rule |
| 6 | The `.claude/settings.json` entry is added only after the user approves it; the tests cover the hook by calling it directly, not through the wiring | User approval gate |
| 7 | Replay: the real T066 guide plus a lock line on `.claude/hooks/tests/test_agent_guide_dedup.py` and a T082-style `<` to `<=` Edit by `common-infrastructure` is denied | T283 spike replay |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Lock line, In Progress, implementer Edit | deny JSON with `permissionDecision: deny` | hook unit test |
| 2 | Same, `qa-expert` or main thread | allow (no output) | hook unit test |
| 3 | Same, row In Progress -> Ready for Review | allow | hook unit test |
| 4 | T082 replay | deny | hook unit test |
| 5 | Mutation: the lookup never denies | the deny tests turn red | mutation control that changes bytes |
| 6 | Mutation: the row-status check always says In Progress | the lock-ends test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -B -m pytest .claude/hooks/tests -q -k "locked or oracle"
python3 -B -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T290.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T290.md`.

---

## Approach

**Pattern reference**: `spike/locked_judge.py` and `spike/test_locked_judge.py` on branch `spike/t283-locked-judge` (commit `22a87330`, read with `git show`); `.claude/hooks/pre_agent_step_limit.py` for how a PreToolUse hook reads the event and the board row. Port the spike, do not copy its toy fixtures: read the guide and the board row from the main checkout.

The Supervisor does not edit `.claude/settings.json` without the user. Write the hook and its tests first, then ask the user to approve the wiring entry (show the exact JSON), then add it.

**Vital slice**: the deny rule for an In Progress task and the allow rules (AC 1, 2, 3)
**Cut list**: no locking of `Bash`; no per-file expiry; no `Locked oracle` UI

---

## Edge Case Checklist

- [ ] A guide with two lock lines or paths with `..`, absolute paths or a symlink out of the repo: resolve and compare real paths
- [ ] A path locked by two tasks, one In Progress and one Done: the In Progress one wins
- [ ] A sub-agent whose `agent_type` is missing: deny (fail closed)
- [ ] Pin-test pre-flight: `.claude/settings.json` tests and `test_agent_guide_dedup.py` are checked before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/pre_tool_locked_oracle.py (new) | The PreToolUse check |
| .claude/hooks/tests/test_locked_oracle.py (new) | Tests for AC 1-4, 7 |
| templates/TASK_GUIDE_template.md | The optional `**Locked oracle**:` line (AC 5) |
| .claude/settings.json | One hook entry, only after the user approves (AC 6) |
| docs/claude-md/tracks.md or pipeline-stages.md | One line saying when to lock an oracle |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |
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
