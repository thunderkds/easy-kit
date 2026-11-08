# TASK_GUIDE — T291: Merge gate counts a test run that has interpreter flags (`python3 -B -m pytest`)
**Date**: 2026-11-08
**Complexity Level**: C1
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
6. Read the review file or doc named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"push and start all as parallel"*, on the follow-up list. Evidence: on 2026-11-08 the merge gate blocked the merges of T289 and T290 with `evidence row present but no verified tool call in memory/event-trace/T289.jsonl` because every test run in those traces was `python3 -B -m pytest ...`. `invokes_test_runner` in `.claude/hooks/pre_bash_block_unsafe_merge.py` (`TEST_INVOCATION_PATTERN`) matches `python3 -m pytest` but not `python3 -B -m pytest`, although the kit tells agents to run mutation controls with `python3 -B` (`memory/learnings.md`, "stale `.pyc`"). The workaround was one extra run without `-B`. See `memory/learnings.md` entry "The merge gate does not count `python3 -B -m pytest` as a test run".

**Restated intent**:
> The gate counts `python3 [flags] -m pytest|unittest` as a test run, where flags are a short fixed list of harmless interpreter flags (`-B`, `-u`, `-O`, `-s`, `-E`, `-I`, `-X <opt>` is not in the list). Nothing else about what counts changes: a command that only mentions a runner still does not count.

**Out of scope** (what this task explicitly does NOT do):
- Counting any other command as a test run
- Letting `-c`, `-m` of another module, a path to a script or a shell wrapper count
- Changing `trace_shows_verification`, the verify row rules or `AUTHORISED_TASKS` beyond adding T291 (the merge-gate tripwire in `merge_gate_guard.py` needs the Supervisor's sign-off)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` (`TEST_INVOCATION_PATTERN`, read by `invokes_test_runner`)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `python3 -B -m pytest x.py`, `python3 -u -B -m unittest`, `python -I -m pytest`, `py -B -m pytest` count as test runs in `invokes_test_runner` | Requirement |
| 2 | Negative: `python3 -c "import pytest"`, `python3 -B script.py`, `python3 -B -m json.tool`, `python3 -X dev -m pytest` (not in the flag list), `python3 -B -m pytest` inside quotes or after `echo` do not count | only real runs count |
| 3 | The existing positive and negative cases of `invokes_test_runner` keep their results (a corpus test over the old cases) | no regression |
| 4 | `merge_gate_guard.AUTHORISED_TASKS` gains `T291` (Supervisor sign-off) and `docs/claude-md/tracks.md` or the learning that says `-B` runs do not count is updated (LR-0005) | tripwire; stale-text rule |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `python3 -B -m pytest a.py -q` in a trace record | `invokes_test_runner` True | unit test |
| 2 | `python3 -c "import pytest"` / `python3 -B script.py` | False | unit test |
| 3 | Mutation: the flag group accepts any `-X` token | the negative test turns red | mutation control that changes bytes |
| 4 | Mutation: the flag group removed | the positive test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "merge or runner or invokes"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T291.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T291.md`.

---

## Approach

**Pattern reference**: the existing `TEST_INVOCATION_PATTERN` alternatives in `.claude/hooks/pre_bash_block_unsafe_merge.py`; extend only the `python` alternative with an optional flag group. Do not touch the other alternatives. The run that proves the work must itself be a plain `python3 -m pytest ...` (no `-B`) so the trace records it (this task is the reason).

**Vital slice**: the optional flag group and its positive and negative tests
**Cut list**: no change to wrapper handling, `uv run`, `poetry run` or other runners

---

## Edge Case Checklist

- [ ] A flag with an argument (`-W error`, `-X dev`) must not make the next word look like the module
- [ ] `-m` twice or `-m` before a flag
- [ ] Pin-test pre-flight: the existing runner corpus tests are found and run before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/pre_bash_block_unsafe_merge.py | The flag group |
| .claude/hooks/tests/test_invokes_test_runner_flags.py (new) | Tests |
| .claude/hooks/tests/merge_gate_guard.py | Add T291 to AUTHORISED_TASKS |
| memory pointers or docs that say `-B` runs do not count | Only if a doc in the repo says so |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | No wiring change |
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
