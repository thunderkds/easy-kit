# TASK_GUIDE — T299: A task that moves up or fails `verify` gets one more effort step first
**Date**: 2026-11-09
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
6. Read `tasks/TASK_GUIDE_T297.md` (the table contract)
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-09: *"yes, let create plan and start parallel [auto]"*, on the plan doc `easy-kit — update plan (base)`: "`tracks.md` near line 59: when a task moves up or `verify` fails, raise effort one step before any other change." The talk's rule is "start low, dial up". Evidence: `docs/claude-md/tracks.md:58-59` says a task moves up (minimal to extended) and never down; it says nothing about effort.

**Restated intent**:
> `docs/claude-md/tracks.md` says: when a task moves up a track, or its `verify` fails, the Supervisor raises the effort of the next spawn by one step on the ladder `low`, `medium`, `high`, `xhigh`, `max` before it changes the model, splits the task or moves any other lever. At `max` the rule changes nothing and the other levers apply. The Supervisor never lowers effort on its own.

**Contract shared with T297 and T298**: the effort levels are `low`, `medium`, `high`, `xhigh`, `max`; they come from the `## CLI Effort Table` cell of the task's Complexity (T297); `craft-spawn-prompt` passes them (T298).

**Out of scope** (what this task explicitly does NOT do):
- Any code or hook that raises effort (the rule is doctrine text the Supervisor follows)
- The effort table (T297) and the spawn text (T298)
- `AGENTS.md` (size ratchet, T286): the rule lives in `tracks.md` only
- The `### Admin tag` section of `tracks.md` (T295 edits it in another worktree); touch only the lines near the "moves up" bullet

**Requirement Refs**: None — kit-internal.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (auto (Supervisor), 2026-11-09, from the plan doc and the user's go-ahead)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None (the contract above is fixed; the text names the table, not its contents)

**Entry point**: the "moves a task **up**" bullet in `docs/claude-md/tracks.md` (near line 58)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `tracks.md` states the rule in at most 4 short sentences, in the same section as the "never moves a task down" rule, and it names both triggers: a move up, and a failed `verify` | Restated intent |
| 2 | The text names the ladder `low`, `medium`, `high`, `xhigh`, `max` and says "before" any other change | Restated intent |
| 3 | The text says the Supervisor never lowers effort on its own, and that at `max` the other levers apply | Restated intent |
| 4 | The text points at `## CLI Effort Table` as the place the starting level comes from | Contract |
| 5 | The existing rule sentences (move up only, never down; a task grows when ...) stay word for word | Out of scope |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `tracks.md` after the change | The rule is present with both triggers, the ladder, "before", "never lowers", `max` and the table name | new test in `tests/test_tracks.py` |
| 2 | The existing `tests/test_tracks.py` | Pass unchanged | existing tests |
| 3 | Mutation: delete "failed `verify`" from the rule | The trigger test turns red | mutation control that changes bytes |
| 4 | Mutation: delete the ladder | The ladder test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_tracks.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
grep -n "effort" docs/claude-md/tracks.md
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T299.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T299.md`.

---

## Approach

**Pattern reference**: the "moves up" bullet at `docs/claude-md/tracks.md:58-62` and how `tests/test_tracks.py` reads a section of that file.

**Vital slice**: the rule text and its test.
**Cut list**: no effort ladder in the `bugfix` skill or `verify` skill (follow-up if a `verify` failure shows the Supervisor forgets the rule); no table of effort per attempt.

---

## Edge Case Checklist

- [ ] Write for a reader who has not followed the project: plain words, short sentences, one idea each (AGENTS.md Writing Principles)
- [ ] `tracks.md` is long and other pin tests read it by line count or section text: grep `tests/` and `.claude/hooks/tests/` for `tracks.md` before editing
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep the repo for the "moves up, never down" wording elsewhere (site, README, `AGENTS.md`) and say whether it needs the new rule too (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| docs/claude-md/tracks.md | The rule near the "moves up" bullet |
| tests/test_tracks.py | New tests for AC 1-4 and the mutation controls |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `docs/claude-md/tracks.md` `### Admin tag` | T295 is editing it in another worktree |
| `skills/craft-spawn-prompt/**`, `templates/PROJECT_SPEC_template.md`, `PROJECT_SPEC.md`, `docs/claude-md/pipeline-stages.md` | T297 and T298 own them |
| `AGENTS.md`, `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes or size ratchet |

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
