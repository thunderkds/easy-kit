# TASK_GUIDE — T289: Docs-only and tests-only tasks get a real pass verdict from the auto verify run (so [admin] needs no manual /verify)
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
6. Read `tasks/SPIKE_REPORT_T283.md`, the section named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"with admin tag, you should run the verify also"*, after T283 and T286 (a report and a size test) both ended `blocked (no single verdict line)` from the headless auto verify run, so the user had to type `/verify T283` and `/verify T286` before `[admin]` could merge them. The verify skill answers SKIP for a diff with no runtime surface (docs, types, tests). The hook records a SKIP as `blocked` (`docs/claude-md/tracks.md` `### Auto verify (Stop hook)`: "a SKIP or BLOCKED verdict, no verdict line ... is `blocked`"). Evidence: `tasks/TASK_REVIEW_T283.md` and `tasks/TASK_REVIEW_T286.md` verify rows (`blocked (no single verdict line)`), the T283 report note "a docs-only task answers skip (seen on T246 and T283)".

**Restated intent**:
> When every file a task's branch changes lies in a short, fixed list of paths that have no runtime surface, and the headless run answers SKIP, the hook writes a pass row that says `skip (no runtime surface)`. The hook, not the model, decides from `git diff --name-only <base>...<tip>` that the paths are all in the list. One path outside the list, or any other verdict, keeps today's result.

**Out of scope** (what this task explicitly does NOT do):
- Any change to what the headless run asks the model, to its budget or to its timeout
- Letting the model's SKIP alone make a pass: the hook must compute the path check itself
- Prompt-config paths as docs-only: `skills/**`, `agents/**`, `templates/**`, `AGENTS.md`, `CLAUDE.md`, `docs/claude-md/**` are runtime surface for an agent and stay out of the list
- UI paths (`site/**`) and anything under `.claude/hooks/*.py`, `scripts/**`
- The user's own `/verify` line (T250 G1) and the hand-typed pass rule: unchanged

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/stop_auto_verify.py` (the headless run's result writer) and `.claude/hooks/pre_bash_block_unsafe_merge.py` (`auto_row_confirmed`, the run record read)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A branch whose changed paths are all in the docs-only list and whose headless run answers SKIP gets a `verify` row `☑ pass`, notes `auto-run by hook ... skip (no runtime surface: <paths>)`, and a run record that says `skip-pass`. The merge gate accepts it like any hook-written pass (`auto_row_confirmed`) | Requirement |
| 2 | The path list is computed by the hook from git, never read from the model's answer, and covers `tasks/**`, `memory/**`, `docs/**` except `docs/claude-md/**`, `tests/**`, `.claude/hooks/tests/**`, and root `*.md` except `AGENTS.md` and `CLAUDE.md` | Requirement; fail closed |
| 3 | Negative: one changed path outside the list (for example `skills/x/SKILL.md`, `site/index.html`, `.claude/hooks/foo.py`, `AGENTS.md`) and a SKIP answer: the row stays `blocked`, exactly as today | every gate stays |
| 4 | Negative: a PASS or FAIL answer is handled as today; a FAIL is never turned into a pass; no verdict line stays `blocked` | verify rule |
| 5 | Negative: an empty diff, an unreadable git range, a missing base ref or a rename that moves a file out of the list: not a skip-pass (`blocked`) | fail closed |
| 6 | Under `[admin]`, a docs-only task with a skip-pass row can be merged and pushed by the existing gate rules with no typed `/verify`; under `[auto]` alone it still cannot | user 2026-11-08 |
| 7 | `docs/claude-md/tracks.md` (`### Auto verify (Stop hook)`, `### Auto close-out`, `### Admin tag`), `AGENTS.md` if it restates the SKIP rule, and the site/docs lines that say a docs-only task needs the user's `/verify` name the new rule and no old fact (LR-0005) | stale-text rule |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Branch changes only `tasks/TASK_REVIEW_T9.md`, headless answer `**Verdict:** SKIP` | Row `☑ pass`, notes carry `skip (no runtime surface`, run record `skip-pass`, `auto_row_confirmed` True | hook unit test |
| 2 | Same, plus one changed `skills/x/SKILL.md` | Row `☐ blocked` | hook unit test |
| 3 | Same as row 1 but the answer is `**Verdict:** FAIL` | Row `☐ fail`/`blocked` as today, never pass | hook unit test |
| 4 | Git range unreadable or empty diff | Row `☐ blocked` | hook unit test |
| 5 | Mutation: the path check always returns True | Row 2 test turns red | mutation control that changes bytes |
| 6 | Mutation: SKIP accepted without the path check at the merge gate | the gate negative test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -B -m pytest .claude/hooks/tests -q -k "verify or admin or merge"
python3 -B -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T289.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T289.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/stop_auto_verify.py` and how it writes the `auto-run by hook` row with its run record; `.claude/hooks/pre_bash_block_unsafe_merge.py` `auto_row_confirmed`. Imitate the existing record format and add one more outcome, `skip-pass`. Do not write a second parser of the model's answer.

Design rules: (1) the model's text only says SKIP; the hook decides pass from git. (2) Fail closed on any doubt. (3) The path list is a literal tuple in one place, covered by a test that lists every entry. (4) This is a High-risk change to a merge gate: Stage 4 runs `code-review` and `security-review`, and the Supervisor runs an independent re-check of the path rule (renames, symlinks, a file whose path looks like docs but is imported by a hook).

**Vital slice**: the path rule plus the one new row outcome (AC 1, 2, 3, 5)
**Cut list**: no change to the headless prompt; no new setting; no automatic pass for `skills/**` or `agents/**` even when the text looks like prose

---

## Edge Case Checklist

- [ ] A file under `docs/` that a hook or test reads at runtime (`docs/claude-md/**` is out; check `docs/` for other loaded files before listing it)
- [ ] A branch that renames a runtime file into `tasks/` or `docs/` (rename detection must not hide the old path)
- [ ] A symlink under `tasks/` or `docs/` that points into `.claude/` or `skills/`
- [ ] The record of a skip-pass must name the paths so a reviewer can see what was judged
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/stop_auto_verify.py | Compute the path list; write the skip-pass row and record |
| .claude/hooks/pre_bash_block_unsafe_merge.py | Read a skip-pass run record in `auto_row_confirmed` (only if needed) |
| docs/claude-md/tracks.md, AGENTS.md, site/docs.html, README.md | State the rule (AC 7) |
| .claude/hooks/tests/test_auto_verify_skip_pass.py (new) | Tests for AC 1-6 |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | The hook wiring is unchanged |
| The user's `/verify` line rule (`USER_LINE`, `verify_typed`) | A security boundary; unchanged |
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
