# TASK_REVIEW — T354: the `[admin]`/`[ticket]` loop binds its task after the hook's close-out moved the row to Done

> Sibling of `tasks/TASK_GUIDE_T354.md`. Evidence is filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Registered T354 and ran it before T321 — RULE: the user's request "yes, let fix this" (`tasks/TASK_GUIDE_T354.md § Requirement`), answering the Supervisor's offer to run it next.
2. Track extended — RULE: `docs/claude-md/tracks.md` `## Track rule` (Risk High: the merge gate; C2: gate, new test, guard, tracks.md).
3. The Supervisor writes the code itself, test first, in `../wt-t354`; no implementer spawn — RULE: `AGENTS.md § Hard-Stop Gates` (Gate 1: "the Supervisor writes the code itself, in the task's worktree, test first").
4. Fix shape — DEBATED: PENDING
5. `merge_gate_guard.py` `AUTHORISED_TASKS` gains T354 with the Supervisor's sign-off — RULE: `.claude/hooks/tests/merge_gate_guard.py` module docstring ("A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off").
Checks: PENDING
Memory: PENDING
Not done: merge (admin: after the auto verify pass); push (the merge gate pushes to `origin` only and this repo's remote is `github`: T321); auto verify: not started

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: neither companion tool is installed for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | No UI: hook-only change. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | No UI: hook-only change. |
| **UI: Responsiveness at target viewports** | ☐ N/A | No UI: hook-only change. |

---

## Demonstration

**BEFORE**: captured 2026-11-25T04:49:12Z on `da038f57` (before any implementation commit), `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t354_loop_closed_out_row.py`:
```
FAILED .claude/hooks/tests/test_t354_loop_closed_out_row.py::test_a_done_row_with_this_runs_close_out_note_binds_the_loop[admin]
FAILED .claude/hooks/tests/test_t354_loop_closed_out_row.py::test_a_done_row_with_this_runs_close_out_note_binds_the_loop[ticket]
FAILED .claude/hooks/tests/test_t354_loop_closed_out_row.py::test_the_last_close_out_note_of_the_row_counts[admin]
FAILED .claude/hooks/tests/test_t354_loop_closed_out_row.py::test_the_last_close_out_note_of_the_row_counts[ticket]
4 failed, 12 passed in 2.38s
```
The live case the day it was found: `git merge --no-ff fix/t347-readme-codex-list` under the session `[admin]` → "T347 is not the task of the `[admin]` request: … nor the task of this session's loop (its row in Ready for Review, …)".

**AFTER**: PENDING

**DELTA**: PENDING

**WITNESS**: PENDING
