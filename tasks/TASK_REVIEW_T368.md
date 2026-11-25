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
Checks: _pending_
Memory: _pending_
Not done: _pending_
Paused: auto-mode check failed — Risk High, but no decision was DEBATED with 3 Advocates [report 45bc26592e14]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ | |
| Verification command run | ☐ | |
| Negative cases hold | ☐ | |
| verify | ☐ pass / ☐ fail / ☐ N/A | [hook-written: auto-run by hook, session <id>, commit <sha>, log <file> — <verdict>] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ | |
| Full smoke suite still green (no regression) | ☐ | |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI |

---

## Demonstration

**BEFORE** (2026-11-25, captured before the implementation commit `67a8a823`): T367's auto verify log `.claude/verify-runs/T367-48a724ab6514.log` (its retry) — `$ claude -p '/verify T367' --max-budget-usd 2 --output-format json`, the run's answer "**Verdict:** SKIP — no runtime surface: tests-only.", and the hook's `verdict: blocked (SKIP, and git does not show a change of docs-only files)`; the branch changed only `tests/test_pack_catalog.sh` plus records. The new test before the change: `7 failed, 1 passed` (only SC2, the plain request, passed).

**AFTER**: _pending_

**DELTA**: _pending_

**WITNESS**: _pending_
