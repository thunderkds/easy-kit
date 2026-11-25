# TASK_REVIEW — T206: a bare or extra-arg `stop_auto_verify.py --start` exits 2 with a usage line

> Sibling of `tasks/TASK_GUIDE_T206.md`. Filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Ran T206, T253 and T254 in parallel, one implementer each in its own worktree — RULE: the user's request "start the task as parallel [admin]" (it sets aside `docs/claude-md/tracks.md` `### Session tags` "runs no two tickets at once" for the build); merges still need the task named, because the gate's loop binding (`_session_holds`) refuses while this session has another task open.
2. Track extended — RULE: docs/claude-md/tracks.md § Track rule (Risk Medium: a run that costs money).
3. One `common-infrastructure` implementer, `haiku`, effort `low` — RULE: AGENTS.md § Hard-Stop Gates (Gate 1: an implementer only for 2+ independent tasks at once); `PROJECT_SPEC.md` CLI Model Table (claude, C0: haiku).
4. The check sits at module level, before the project lookup, so a bare `--start` outside a project exits 2, not 1 — FACT: tasks/TASK_GUIDE_T206.md:31 "must never reach `stop_hook()`: it prints one usage line to stderr … and exits 2".
5. Reviewer P2-1 (the tests prove the exit code, not that `stop_hook()` is not called) accepted as a follow-up, not fixed: the exit is at module level before `main()`, so `stop_hook()` is unreachable, and a new test would need a second Reviewer round — SAFER OPTION: a stronger test that loads the module with the guard unset could start a paid run if written wrong ⚠ decided for you — please review
Checks: tests `python3 -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider` (the guide's Verification Command) — `4 passed` at 9bcfa01a (implementer and Reviewer); `-k auto_verify` over `.claude/hooks/tests/` — `232 passed, 5323 deselected`; reviews: Reviewer (fresh context, qa-expert, 9bcfa01a) PASS with findings, 1 P2 (accepted, decision 5), 3 P3; Supervisor `code-review` 0 P0/P1/P2, 2 P3; `security-review` (temporary `origin/HEAD`, removed after; branch diff read by hand) no findings; real run: `CLAUDE_AUTO_VERIFY_RUN=1 python3 .claude/hooks/stop_auto_verify.py --start T1 x` — printed `usage: stop_auto_verify.py --start <TASK_ID>`, rc 2 (implementer; auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); push (no push remote set: T321 waits on `/verify T321`); auto verify: ☑ pass (session 62b67884-b338-4b56-9bb2-681725edc01d, commit 1c97d42fd6748f05b21995b810634e564c85d385, log .claude/verify-runs/T206-1c97d42fd674.log)
Closed: row moved to Done 2026-11-25 — auto verify pass (session 62b67884-b338-4b56-9bb2-681725edc01d, commit 1c97d42fd6748f05b21995b810634e564c85d385); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t206_start_usage.py` (4): AC1 `test_bare_start_exits_2_with_usage`; AC2 `test_start_with_two_args_exits_2_with_usage`, `test_start_with_three_args_exits_2_with_usage`; AC3 `test_start_with_one_id_still_reaches_start_one` (reaches the child-guard answer). AC4 by the existing `-k auto_verify` tests (232 passed). |
| Verification command run | ☑ pass | `4 passed in 0.10s` (Reviewer, 9bcfa01a) |
| Negative cases hold | ☑ pass | Red run before the fix: Demonstration BEFORE (`3 failed, 1 passed`, `assert 0 == 2`). |
| verify | ☑ pass | auto-run by hook, session 62b67884-b338-4b56-9bb2-681725edc01d, commit 1c97d42fd6748f05b21995b810634e564c85d385, log .claude/verify-runs/T206-1c97d42fd674.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read: the module-level entry (`stop_auto_verify.py:90-112`), `main()`, the new test; `git diff --stat main...9bcfa01a`: 3 files. |
| Full smoke suite still green (no regression) | ☑ pass | `-k auto_verify` over `.claude/hooks/tests/`: `232 passed`; the change is 5 lines in one entry point that only `--start` reaches. |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: neither companion tool is installed for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | No UI. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☐ N/A | No UI. |

---

## Demonstration

**BEFORE**: (captured 2026-11-25 05:29:01–05:29:08 UTC, before the first implementation commit; the red test was committed before the hook fix)

```
$ date -u
Wed Nov 25 05:29:01 UTC 2026
$ /tmp/claude-1000/-home-thunderkds-workspace-pets-hungnguyen111-easy-kit/a074ce56-6c68-4a4f-b8ca-c467af91efc9/scratchpad/venv/bin/python3 -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider
FFF.                                                                     [100%]
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_bare_start_exits_2_with_usage
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_start_with_two_args_exits_2_with_usage
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_start_with_three_args_exits_2_with_usage
3 failed, 1 passed in 0.17s
$ date -u
Wed Nov 25 05:29:08 UTC 2026
```

Failing assertion: `assert 0 == 2` (bare `--start` and extra-arg forms return 0 with no usage line; they fall through to `stop_hook()` when the child guard is absent).

**AFTER**: (captured 2026-11-25 05:29:29 UTC, after the fix)

```
$ python3 -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider   (scratchpad venv)
....                                                                     [100%]
4 passed in 0.12s
$ CLAUDE_AUTO_VERIFY_RUN=1 python3 .claude/hooks/stop_auto_verify.py --start T1 x
usage: stop_auto_verify.py --start <TASK_ID>
rc=2
```

**DELTA**: A bare or extra-arg `stop_auto_verify.py --start` now prints one usage line and exits 2 without reaching `stop_hook()`, so it can no longer start a paid run for every due task.

**WITNESS**: the fresh-context Reviewer re-ran the Verification Command (`4 passed`); the auto verify run is the independent check.
