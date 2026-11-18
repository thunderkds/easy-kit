# TASK_GUIDE — T327: Clean up a task's resources after it is merged and Done
**Date**: 2026-11-18
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in `agents/common-infrastructure.md`
6. Read `memory/codebase-map.md` (multi-file task)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-18: "we have progress to clean the resource, and related build for testing after done" →
Supervisor found no doc, skill or hook that removes a task's worktree or branch, deletes its build/test
output, or stops its test processes after Done. User: "yes, register both tasks, and execute 2 of them parallel [admin]".

**Restated intent**:
> After a task is Done and its branch is merged into `main`, one command cleans up what the task left:
> its linked worktree (with the build and test output inside it), its merged task branch, and processes
> still running from inside that worktree. The Supervisor runs it at Stage 5 after the merge, in every mode
> (under `[admin]` and the session loop, automatically). It never deletes unmerged or uncommitted work.

**Out of scope**:
- Cleaning the main checkout's ignored files (`__pycache__/`, `memory/event-trace/`) — they are shared, not the task's.
- Deleting remote branches.
- Tasks not Done or branches not merged — the command refuses them.

**Requirement Refs**: none in `PRD.md`; doctrine `docs/claude-md/pipeline-stages.md` Stage 5, `docs/claude-md/tracks.md` (minimal 7 steps, `### Admin tag`, `### Session tags` loop step 4).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, [admin] 2026-11-18, RULE + SAFER OPTION: never delete unmerged/dirty work)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: doctrine sections named above

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `scripts/cleanup_task.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `python3 scripts/cleanup_task.py <ID>` on a Done task whose branch is merged into local `main`: removes the task's linked worktree (and so its build/test output), deletes the branch with `git branch -d`, prints one line per action | "clean the resource ... after done" |
| 2 | Refuses (exit non-zero, nothing removed) when the board row is not in Done, or the branch is not merged into `main` | never delete unmerged work |
| 3 | Refuses to remove a worktree with uncommitted or untracked (non-ignored) files; never uses `--force`, `branch -D` or `git clean` | never delete uncommitted work |
| 4 | No signal is sent to any process. Every process whose symlink-resolved cwd is inside the task's worktree (the script's own process and its ancestors excluded) is printed, one line with PID and command, and while any runs the command refuses: exit non-zero, nothing removed, so the user stops them and runs again (a worktree may hold another live session, `skills/wake/SKILL.md:69`). An unreadable `/proc` entry is skipped and counted in a printed line; other OS: prints that the process check was skipped | "related build for testing" (test servers, watchers) |
| 5 | Run from a linked worktree, or with no worktree/branch left: prints what is already clean and exits 0 (idempotent) | safe re-run |
| 6 | Doctrine: Stage 5 in `docs/claude-md/pipeline-stages.md`, the minimal track steps and `### Admin tag` / `### Session tags` loop in `docs/claude-md/tracks.md` name the command as the step after merge; under `[admin]`/session loop the Supervisor runs it itself | "we have progress to clean" |
| 7 | Never touches the main checkout or another task's worktree/branch | surgical |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Fixture repo: board row Done, branch merged, worktree with ignored build dir, a `sleep` started with cwd in it | worktree gone, branch gone, sleep terminated | automated test |
| 2 | Row Ready for Review / branch unmerged / dirty worktree | exit non-zero, everything still present | automated test |
| 3 | Second run | exit 0, "already clean" | automated test |

### Verification Command (exact, runnable)

```bash
uv run --with pytest python -m pytest -q tests/test_cleanup_task.py
uv run --with pytest python -m pytest -q .claude/hooks/tests tests
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled in `tasks/TASK_REVIEW_T327.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T327.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/stop_auto_verify.py` — how it finds a task's worktree from the board row's branch (`auto_mode.find_for_task`, "the one worktree whose branch names the task"), and its main-checkout-only rule; reuse that lookup instead of writing a new one.

**Vital slice**: the script with the Done + merged + clean preconditions, worktree remove, `branch -d`, process stop, plus the doctrine lines.
**Cut list**: no hook auto-trigger (doctrine step only); no remote branch delete; no cleanup of main-checkout caches.

Supervisor decision (SAFER OPTION): use only `git worktree remove <path>` (no `--force`) and `git branch -d` (merged-only); git itself refuses dirty or unmerged. Check that the merge gate (`.claude/hooks/pre_bash_block_unsafe_merge.py`) does not block these commands; do NOT change the merge gate — if it blocks, stop and report `Status: blocked` with a `Question:` line.

---

## Edge Case Checklist

- [ ] Board row names no branch → use the one worktree whose branch names the task; none or several → refuse
- [ ] Worktree folder already deleted by hand → `git worktree prune` for that entry only? No: use `git worktree remove` semantics; report and exit 0 if git no longer lists it
- [ ] Process running in the worktree: list it, send no signal, do not remove the worktree or branch, exit non-zero
- [ ] Task ID shape validated (`T\d+`); no shell interpolation (subprocess list args)
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for "Stage 5" step lists in README, `site/`, `docs/claude-md/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `scripts/cleanup_task.py` | new |
| `tests/test_cleanup_task.py` | new |
| `docs/claude-md/pipeline-stages.md` | Stage 5 step after merge |
| `docs/claude-md/tracks.md` | minimal steps, `### Admin tag`, `### Session tags` loop step 4 |
| Pre-existing pin tests | Checked before editing (grep of `pipeline-stages.md`, `tracks.md`, `MANIFEST` in `tests/` and `.claude/hooks/tests/`: 47 files): `tests/test_tracks.py`, `test_stage_names.py`, `test_claude_md_slim.py`, `test_t307_admin_end_to_end.py`, `test_t306_admin_retry_blocked.py`, `test_auto_verify.py`, `test_plugin_names.py` (scripts vs MANIFEST), `test_memory_slice.py`, `.claude/hooks/tests/test_agent_guide_dedup.py`, `test_memory_channel_and_budget.py`. All of them passed in the full run after the edit |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | merge gate; T326's area, needs sign-off |
| `.claude/hooks/tests/merge_gate_guard.py` | T326 |

---

## Test Plan

TDD with temp git repos (main + linked worktree + fake board), a real child process with cwd inside the worktree; red, then implement; full suites.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T327.md`
- [ ] `Skill({ skill: "verify" })` run (headless auto verify)
- [ ] Supervisor notified: task ready for Stage 4 review
