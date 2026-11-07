# TASK_GUIDE — T283: Karpathy autoresearch loop — seven spikes with evidence, then a decision
**Date**: 2026-11-08
**Complexity Level**: C3
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
5. Read `memory/codebase-map.md` (C3: hooks, skills and gates are blast-radius hotspots)
6. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md` and `LR-0004-pin-tests-hit-later-tasks.md`
7. Read `docs/claude-md/tracks.md` sections `## Auto mode` and `### Never in auto mode`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08, after the Supervisor read Karpathy's *autoresearch loop* technical note (one editable file, a five-minute budget, a locked judge, keep-or-revert on one number): *"all of them should be experimented with good evidence, after that, let decide and create task guide for that."*

**Restated intent** (Supervisor's interpretation):
> Test each of the 7 ideas taken from the autoresearch loop on a throwaway spike branch, measure it against real past work of this kit, and write one evidence report. The user then decides which ideas become real tasks. This task writes no kit change to `main`.

The 7 ideas (names are fixed; use them as written):
1. **Locked judge** — the agent that writes the code cannot edit the test that grades it.
2. **Keep-or-revert ratchet** — one number per task; a change that does not improve it is reverted by rule.
3. **Simplicity rule** — a small gain that costs many lines is dropped; the same result with less code is kept.
4. **Time budget** — a wall-clock limit per sub-agent run, with a kill.
5. **Attempt log** — an append-only log of every attempt, failures included.
6. **No check-ins** — the agent never stops to ask for permission mid-run.
7. **Steering file** — the human steers through one small file that the agent rereads before each idea.

**Out of scope** (what this task does NOT do):
- Any change to `main`: hooks, skills, `AGENTS.md`, docs or the board. Only the report lands (on the task branch, merged by the user).
- Writing the adoption TASK_GUIDEs. Those wait for the user's decision, in a later step.
- The `[admin]` tag (task T284).

**Requirement Refs**: None — kit-internal; follow-up to the user's request of 2026-11-08.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user chose "Spike branch per idea" on 2026-11-08)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

> An agent must NOT start implementing until this gate is checked. If anything here is unclear,
> STOP and ask the Supervisor (Karpathy: Think Before Coding).

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: Standalone — N/A: a research task; its output is `tasks/SPIKE_REPORT_T283.md`, read by the user.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | One spike branch exists per idea, named `spike/t283-<idea>` (7 branches). `git branch --merged main` lists none of them | "experimented" / seven ideas |
| 2 | `tasks/SPIKE_REPORT_T283.md` has exactly one row per idea. Each row holds: hypothesis, baseline measure, spike measure, the exact command to reproduce, pasted output, and a verdict (`adopt`, `adapt` or `drop`) with one reason | "good evidence" |
| 3 | Each baseline is measured on real past kit work (a named task ID, commit or review file), never on a toy example | "good evidence" |
| 4 | Each spike has at least one automated test that can fail: a mutation control that changes bytes and turns the test red (LR-0003) | "good evidence" |
| 5 | An idea that cannot be measured gets the verdict `no evidence` with the reason. No row holds a guess | "good evidence" |
| 6 | The report ends with a ranked recommendation and a list of the adoption tasks it proposes (titles only, no guides) | "let decide" |
| 7 | Negative: no file under `.claude/`, `skills/`, `agents/`, `docs/`, `AGENTS.md` or `PROJECT_KANBAN.md` differs from `main` on the task branch | Out of scope |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The oracle is written first by the Supervisor (`tests/test_spike_report_t283.py`, below). The implementing agent must not weaken it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The finished report | 7 rows, one per idea name above; every row has all 6 fields and a verdict in `adopt`/`adapt`/`drop`/`no evidence` | `tests/test_spike_report_t283.py` |
| 2 | A report copy with one field blanked | The test fails (mutation control) | same test file |
| 3 | The task branch diff against `main` | Touches only `tasks/SPIKE_REPORT_T283.md`, `tests/test_spike_report_t283.py` and the task's own review/log files | `git diff --name-only main` |
| 4 | Each spike branch | Contains its own test, and that test fails after its guard is mutated | command in the report row |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_spike_report_t283.py -q
git diff --name-only main...HEAD
for i in locked-judge ratchet simplicity time-budget attempt-log no-check-ins steering-file; do git rev-parse --verify "spike/t283-$i" >/dev/null && echo "ok $i"; done
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T283.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T283.md`.

---

## Approach

**Pattern reference**: `skills/optimize/SKILL.md` — baseline, hypothesis, experiment, converge. Imitate its baseline-first order. Also `.claude/hooks/pre_agent_step_limit.py` — the kit already limits steps; spike 4 starts from it, not from zero.

**Vital slice**: the three spikes whose evidence changes a gate: 1 (locked judge), 2 (ratchet), 3 (simplicity rule). Do them first.
**Cut list**: no production-quality code in any spike; no spike is wired into `settings.json`; no docs or site text.

Group the work in three agent runs, each in its own worktree, to bound the cost:
- **Run A** — spikes 1, 2 (measure on tests and verify results of past tasks).
- **Run B** — spikes 3, 5 (measure on merged diffs and on past review and blocked records).
- **Run C** — spikes 4, 6, 7 (measure on `memory/event-trace/`, auto-mode final reports and the size of `AGENTS.md`).

How each idea gets its evidence:
1. **Locked judge**: prototype a PreToolUse check that denies the implementer an edit to a file listed as `Locked oracle` in the guide, and allows `qa-expert`. Baseline: count review findings in `tasks/TASK_REVIEW_*.md` and `memory/learnings.md` that say a test could not fail or was weakened by its own author (LR-0003 incidents).
2. **Ratchet**: prototype a script that runs a metric command (suite pass count and runtime) before and after a change and prints `keep` or `revert`. Replay it on at least 3 past commits whose outcome is known.
3. **Simplicity rule**: prototype a script that reads a diff's added lines and the task's Acceptance Criteria count. Run it on the last 15 merged tasks. Compare its flags with the Stage 4 findings that named over-building.
4. **Time budget**: from `memory/event-trace/*.jsonl`, compute the run durations of past sub-agents. Report how many exceed a candidate limit, and what `pre_agent_step_limit.py` already caught.
5. **Attempt log**: prototype an append-only `tasks/attempts.tsv` row per spawn and per blocked or failed attempt. Baseline: for past blocked attempts, say how many can be found in existing records today and how many would be new.
6. **No check-ins**: from the auto-mode final reports (`## Auto decisions`, `Paused:` lines), count the stops and sort them as avoidable or required. `[auto]` mode already exists; the question is what it still stops for.
7. **Steering file**: measure the size of `AGENTS.md` and what each session loads. List which of its rules a hook enforces and which are only text. `AGENTS.md` is already the one steering file, so this spike asks what to cut or lock, not whether to add one.

---

## Edge Case Checklist

- [ ] A spike that works on a toy example only is a fail of AC 3: re-measure on real work
- [ ] A spike test that cannot fail (an `x <= x` assertion, a `sed` that changes no bytes) is a fail of AC 4 (LR-0003)
- [ ] Spike 1 must not break the existing rule that the Supervisor, not the implementer, signs off the oracle
- [ ] Spike 6 must not suggest dropping a stop that `### Stops that stay` keeps (safety-hook block, data deletion, secrets)
- [ ] Spike branches must not be merged and must not be pushed
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: the report names no fact (count, path, ID) it did not read in this task

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `tasks/SPIKE_REPORT_T283.md` | New: the evidence report, 7 rows and the ranked recommendation |
| `tests/test_spike_report_t283.py` | New: the oracle for the report structure (written first by the Supervisor) |
| `spike/t283-*` branches | New: throwaway prototypes and their tests, never merged |
| Pre-existing pin tests | None expected: no file on `main` is edited. Confirm by grepping `tests/` for `tasks/SPIKE_REPORT` |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/**`, `skills/**`, `agents/**`, `AGENTS.md`, `docs/**` | Doctrine and gates; a spike prototype lives only on its spike branch |
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |
| `.claude/settings.json` | A spike must never be wired into the live hooks |

---

## Test Plan

Run the verification command above. For each spike, run the command in its report row and paste the output. Mutate each spike's guard once and show the test turn red.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: not required (Medium risk, no data, no gate change on `main`)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
