# TASK_REVIEW — T368: `[admin]` auto verify loops back on a fail (2 fix rounds) and runs a changed shell suite instead of skipping it

> Sibling of `tasks/TASK_GUIDE_T368.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Sign the Requirement Fidelity Gate myself — RULE: docs/claude-md/tracks.md:257 "| 13 | Stage 2/3: the Requirement Fidelity Gate (\"Restated intent confirmed\") | Signed `auto (Supervisor)`, not by the user. | `RULE` |"
2. Ask `/verify` to run each changed shell suite (A), not widen the docs-only list (B) or run the suites in the hook (C) — DEBATED: Advocate 1: A (only on otherwise docs-only branches); Advocate 2: A (a SKIP on named suites stays blocked); Advocate 3: A (smallest safe change); settled by rule 1 — RULE: docs/claude-md/tracks.md:491 "`conftest.py`, a `.sh` file, `tests/lib/` or `merge_gate_guard.py`;" rules out B; log `reports/question_T368_20261125T165656.html`
3. A `fail` loops back at most 2 fix rounds, each with a fresh reviewer on the new commit — RULE: tasks/TASK_GUIDE_T368.md § Requirement (Pillar 1 — Adapt the requirement) ("(b) **A fail loops back.** … at most 2 fix rounds, then it stops and says why", from the user's "yes, I think." to that proposal)
4. `[admin]` on a `master` repo is split out as T370, not done here: `main` is hard-coded in the merge gate — FACT: .claude/hooks/pre_bash_block_unsafe_merge.py:1472 "ADMIN_MAIN_BRANCH = \"main\"  # AC 8: the one branch `[admin]` may push besides the task branch"
5. Add `merge-base` to the read-only git verbs `tests/test_auto_verify.py::test_t189_ac6_the_run_issues_no_git_command_that_writes` allows: it reads, it does not write — FACT: .claude/hooks/lib/verify_record.py:159 "def _git(checkout, *args):" (the same read helper `docs_only_change` already calls `merge-base --all` through)
Checks: tests `tests/test_auto_verify_shell_suites_t368.py` — 9 passed (red first: `7 failed, 1 passed`, only SC2's plain request passed); guide Verification Command `483 passed` (Reviewer re-run; one run had a `test_auto_verify.py` flake that also fails on `main`); `tests/test_t306_admin_retry_blocked.py` + T368 `43 passed`; full suite `tests/ .claude/hooks/tests/` at `0eb171a0`: `77 failed` vs base `8cc88130` `58 failed` — the 19 new were all `tests/test_t306_admin_retry_blocked.py` pinning the replaced sentence, repinned in `1420c388` (43 passed), none else new; code-review 0 P0/P1, 2 P2 fixed (`7afeb933`: stale verify-request descriptions in `tracks.md:425` and the hook docstring), 1 P3 left (`call_claude`'s unused `head=None` default); security-review run with a temporary `refs/remotes/origin/HEAD` at `8cc88130`, removed after (`docs/claude-md/tracks.md:1001`), no findings; Debate 3/3 for (A) (`reports/question_T368_20261125T165656.html`, local); Reviewer: T368 round 1 (`0eb171a0`) PASS, 0 P0/P1, P2 flake note (`tests/test_auto_verify.py:217`, also on `main`), 2 P3 left (`SHA_PATTERN` `$` accepts a trailing newline: harmless, git rejects it; no cap on named suites: a failed launch is `blocked`); round 2 (`1420c388`: the T306 repin and the memory entry) PASS, 0 P0–P2, 1 P3 left (`tasks/TASK_GUIDE_T306.md:30` still quotes the replaced sentence: a dated record, no test reads it), `43 passed`; auto-checked, not /verify
Memory: `memory/decisions.md` — 2026-11-25 T368: fix rounds under `[admin]`; changed shell suites named in the `/verify` request
Not done: merge (admin: after the auto verify pass); push (yours until `EASY_KIT_ADMIN_REMOTE=github` is in `.claude/settings.local.json` `"env"`: the auto-mode classifier refused Claude's edit); auto verify: running (T182); T367's fix round after the merge (the first live run of the shell-suite request); T370 (`[admin]` on a `master` repo)
Paused: auto-mode check failed — Risk High, but no decision was DEBATED with 3 Advocates [report 45bc26592e14]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_auto_verify_shell_suites_t368.py` (SC1 a changed `tests/test_x.sh` / `.claude/hooks/tests/test_y.sh` is named, via the real Stop hook and a fake `claude`; SC2 plain `/verify <ID>`; SC3 `tests/lib/`, non-`test_*.sh`, symlink, unsafe name, added-then-deleted; SC4 bad sha, no checkout, no `main`; SC5 the docs) |
| Verification command run | ☑ pass | guide `### Verification Command`: `483 passed` (Reviewer round 1 re-run) |
| Negative cases hold | ☑ pass | the new test red first (`7 failed, 1 passed`); SC3/SC4 name nothing on every doubt; `tests/test_t306_admin_retry_blocked.py` mutation controls go red when the fix-round sentence or the cap is cut |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff 8cc88130...HEAD`: `verify_record.py` (one new function), `stop_auto_verify.py` (`verify_request`), `tracks.md`, 3 test files, records; lane `C2, 6 files, 196 lines, FITS` at round 1 |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression: base `58 failed`; the branch's 19 extra were one pinned sentence, repinned and passing at `1420c388` |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI |

---

## Demonstration

**BEFORE** (2026-11-25, captured before the implementation commit `67a8a823`): T367's auto verify log `.claude/verify-runs/T367-48a724ab6514.log` (its retry) — `$ claude -p '/verify T367' --max-budget-usd 2 --output-format json`, the run's answer "**Verdict:** SKIP — no runtime surface: tests-only.", and the hook's `verdict: blocked (SKIP, and git does not show a change of docs-only files)`; the branch changed only `tests/test_pack_catalog.sh` plus records. The new test before the change: `7 failed, 1 passed` (only SC2, the plain request, passed).

**AFTER** (2026-11-25, `1420c388`): `tests/test_auto_verify_shell_suites_t368.py::test_sc1_a_changed_shell_suite_is_named_with_a_pass_or_fail_ask` — the real Stop hook sends `-p "/verify T951 — this branch changes the shell test suite(s) .claude/hooks/tests/test_y.sh, tests/test_x.sh: they are its runtime surface. Run each with `bash <path>` from the repository root and answer PASS or FAIL by its exit code; SKIP is not an answer for them."`; a branch with no changed suite still sends `/verify T951`.

**DELTA**: a shell-test-only change now asks the verify session for a real run (PASS or FAIL) instead of ending `blocked` on SKIP, and under `[admin]` a `fail` loops back for up to 2 fix rounds instead of stopping.

**WITNESS**: Supervisor session 7b4187fe, 2026-11-25 (BEFORE from T367's verify log, red run, full-suite comparison); `Reviewer: T368` round 1 (`0eb171a0`, `483 passed`) and round 2 (`1420c388`).
