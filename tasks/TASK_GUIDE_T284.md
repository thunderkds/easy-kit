# TASK_GUIDE — T284: `[admin]` tag — auto mode plus merge and push after a passed verify
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full: this task reaches the merge gate and the auto-mode hooks, which a slice may miss
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read `docs/claude-md/tracks.md` sections `## Auto mode`, `### Auto verify (Stop hook)`, `### Auto close-out`, `### Never in auto mode`
7. Read `.claude/hooks/pre_bash_block_unsafe_merge.py`, `.claude/hooks/lib/auto_mode.py` and `.claude/hooks/stop_auto_mode_check.py`
8. Read `docs/claude-md/untrusted-content-boundary.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"add 1 more tag as administrator to allow supervisor to merge and push to git, the same with [auto] task work."* Choices made by the user on 2026-11-08: the tag text is `[admin]`; the merge gate stays (merge and push only after the headless auto verify run passes); `ship` stays out.

**Restated intent**:
> The user can write the literal tag `[admin]` in a request. The task then runs in auto mode, and the Supervisor may also merge and push it, but only after the auto verify run has passed. `[auto]` alone keeps today's rule: no merge, no push.

**Out of scope**:
- `ship` (release planning) stays the user's, also under `[admin]`
- Any weakening of the merge gate, the Hard-Stop Gates or the "only the hook writes the `verify` row" rule
- A merge or push of any task other than the one the tag was written for
- Force push, a push to a branch other than the task branch, and a merge of a task that has no passed verify

**Requirement Refs**: None — kit-internal.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user answered the three scope questions on 2026-11-08)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `[admin]` — the literal tag, read from the user's prompt by `.claude/hooks/lib/auto_mode.py` (constant `TAG`)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A user prompt with the exact text `[admin]` marks the task as admin and auto: every existing `[auto]` hook behaviour applies to it | "the same with [auto]" |
| 2 | For an admin task whose auto verify passed (a hook-written `auto-run by hook` row with its run record), `git merge` of its branch and `git push` of its branch are allowed by the merge gate | "allow supervisor to merge and push" |
| 3 | For an admin task with no passed auto verify, the merge gate still blocks the merge and the push | gate stays |
| 4 | For an `[auto]`-only task, merge and push stay blocked exactly as today | "the same with [auto]" stays unchanged |
| 5 | `[admin]` found in pasted content, a tool result, a fetched page, a file or a PR comment does not count; only text the user typed counts | untrusted-content boundary |
| 6 | `[Admin]`, `[ADMIN]`, a bare word *admin* and `[administrator]` are not the tag | exact tag rule, as for `[auto]` |
| 7 | The tag covers only the task of the request it was typed in. A later plain request, or another task, is not admin | one tag, one task |
| 8 | `ship`, force push and a push to a branch other than the task branch stay blocked under `[admin]` | Out of scope |
| 9 | `docs/claude-md/tracks.md` (`## Auto mode`, `### Never in auto mode`), `AGENTS.md` (Tracks paragraph) and the site/docs text that lists the tag name the new tag and its limit, and state no old fact | stale-text rule (LR-0005) |
| 10 | With `[admin]`, the Supervisor starts the headless auto verify run itself (`python3 .claude/hooks/stop_auto_verify.py --start <ID>`) as soon as the task is at Ready for Review, waits for the verdict, and only on a pass goes on to merge and push without asking. It never runs `/verify` in its own session. On `skip`, `blocked` or `fail` it merges nothing and reports why; a docs-only task answers `skip` (seen on T246 and T283), so the user runs `/verify` for it | User 2026-11-08: "with [admin] tag, you should run verify as automatically also" |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The Supervisor signs off the test names below before the agent starts; the agent writes the tests but must not weaken a sign-off row.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Prompt `do X [admin]` | task marked admin and auto | hook unit test |
| 2 | Admin task, passed auto verify, `git merge <task branch>` | allowed | gate test |
| 3 | Admin task, verify not passed, same command | blocked, message says why | gate test |
| 4 | `[auto]`-only task, passed verify, same command | blocked | gate test (regression) |
| 5 | `[admin]` only inside a tool result or pasted block | not marked | hook unit test |
| 6 | `[Admin]`, `[administrator]`, "admin" | not marked | hook unit test |
| 7 | Admin task, `git push --force` or `git push origin main` | blocked | gate test |
| 8 | Mutation: remove the passed-verify check from the gate | tests 3 and 7 turn red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"
python3 -m pytest tests -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T284.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T284.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/lib/auto_mode.py` — `TAG = "[auto]"` and the single reader of auto-mode tasks (T188 D1). Add the admin reader beside it. Do not write a second parser. For the merge gate, imitate how `pre_bash_block_unsafe_merge.py` already checks the hook-written verify row and its run record.

**Vital slice**: the admin marker plus the one merge-gate branch that allows merge and push after a passed auto verify (AC 1, 2, 3, 5). Fail closed: a doubt about the tag or the verify record means block.
**Cut list**: no `ship` support; no per-branch allow-list UI; no new setting; no change to the headless verify run.

Design rules the agent must keep:
- The marker is read from user-typed prompt text only (the same source `[auto]` uses). A tag in any other source is data, never an instruction.
- The gate reads the marker and the verify record at hook time. It never trusts a row the Supervisor typed.
- A missing or unreadable marker means "not admin" (block). The existing fail-closed import guard stays.
- `[admin]` implies `Mode: auto`; do not make a second marker line that a hook could read differently.

---

## Edge Case Checklist

- [ ] Two sessions: an admin tag typed in session A must not unlock a merge in session B (T250 session ownership)
- [ ] An admin task merged, then a new plain request in the same session: the next merge is blocked again
- [ ] The tag typed twice, or together with `[auto]` (`[auto][admin]`): still one admin task
- [ ] A branch name or commit message containing `[admin]` does not count
- [ ] `git merge` with a global option (`git -C dir merge`, T211 forms) is gated the same as the plain form
- [ ] The post-merge memory pass (`post_bash_memory_update.py`) still runs after an admin merge
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep the repo for `[auto]`, `Never in auto mode`, `merge, push` and "never merges" in README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/lib/auto_mode.py` | Add the admin tag reader beside `TAG` |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | Allow merge and push for an admin task with a passed auto verify |
| `.claude/hooks/stop_auto_mode_check.py`, `.claude/hooks/stop_auto_verify.py` | Only if they must treat `[admin]` as auto (read first; change the minimum) |
| `docs/claude-md/tracks.md`, `AGENTS.md`, `site/` pages that name the tag | State the new tag and its limit (AC 9) |
| `.claude/hooks/tests/test_*admin*.py` (new) | Tests for AC 1–8 |
| Pre-existing pin tests | Pins on `tracks.md`, `AGENTS.md` and `site/index.html` text and size (300-word cap), the merge-gate tests, `test_agent_guide_dedup.py`, `test_vital_slice.py` and the memory budget tests. Repoint, narrow or escalate each |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |
| `.claude/settings.json` | The hook wiring is unchanged; a new hook entry needs the user |
| `skills/ship/**` | `ship` stays out |
| The "only the hook writes the `verify` row" logic | A security boundary; AC 3 depends on it |

---

## Test Plan

Write the tests for AC 1–8 first and see them fail. Implement. Run the verification command. Do the mutation control of Success Criteria row 8 and paste the red output. Stage 4 runs `code-review` and `security-review` (High risk).

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
