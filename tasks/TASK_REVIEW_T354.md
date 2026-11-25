# TASK_REVIEW — T354: the `[admin]`/`[ticket]` loop binds its task after the hook's close-out moved the row to Done

> Sibling of `tasks/TASK_GUIDE_T354.md`. Evidence is filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Registered T354 and ran it before T321 — RULE: the user's request "yes, let fix this" (`tasks/TASK_GUIDE_T354.md § Requirement`), answering the Supervisor's offer to run it next.
2. Track extended — RULE: docs/claude-md/tracks.md § Track rule (Risk High: the merge gate; C2: gate, new test, guard, tracks.md).
3. The Supervisor writes the code itself, test first, in `../wt-t354`; no implementer spawn — RULE: `AGENTS.md § Hard-Stop Gates` (Gate 1: "the Supervisor writes the code itself, in the task's worktree, test first").
4. Fix shape: the loop also binds the task's one Done row that ends with the close-out note, whose commit has the hook's pass record from that session, written after this session's own `--start` and held by the branch — DEBATED: option (a) (Advocate 1: (a), the note must match the transcript's session — not taken, the note names the headless verify run's session, `.claude/hooks/stop_auto_verify.py:367`; Advocate 2: (a), the note's session must match the record's, exactly one Done row; Advocate 3: (a), the note anchored at the row end, the session must match the record's). All three rejected (b) delay the close-out (breaks `[ticket]`, `scripts/cleanup_task.py:152` needs Done) and (c) drop R4 (breaks the locked `test_t317_fix_round.py::test_r4_a_done_or_todo_row_does_not_bind_the_loop`). ⚠ decided for you — please review
5. `merge_gate_guard.py` `AUTHORISED_TASKS` gains T354 with the Supervisor's sign-off — RULE: .claude/hooks/tests/merge_gate_guard.py:22 ("A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off").
Checks: PENDING
Memory: PENDING
Not done: merge (admin: after the auto verify pass); push (the merge gate pushes to `origin` only and this repo's remote is `github`: T321); auto verify: not started

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t354_loop_closed_out_row.py` (22 tests, [admin]/[ticket]): AC1/2 `test_a_done_row_with_this_runs_close_out_note_binds_the_loop`, `test_the_last_close_out_note_of_the_row_counts`; AC3/4 `test_a_done_row_without_this_runs_note_does_not_bind` (no-note, other-commit, short-sha, record-before-start, other-session, note-not-at-row-end); AC5 `test_a_close_out_note_in_a_todo_row_does_not_bind`, `test_another_tasks_done_row_note_does_not_bind`, `test_two_done_rows_for_the_task_do_not_bind`. AC6 (docs/refusal text): no test, read in diff (`docs/claude-md/tracks.md`, refusal text). Edge-list gaps: see Review (round 1) P2-1. |
| Verification command run | ☑ pass | `PATH=<venv>/bin:$PATH python3 -m pytest .claude/hooks/tests/test_t354_loop_closed_out_row.py .claude/hooks/tests/test_t317_fix_round.py .claude/hooks/tests/test_t317_loop_binding.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider` -> `317 passed in 60.11s (0:01:00)` (at 1fdcee06) |
| Negative cases hold | ☑ pass | Mutations on a `git archive` copy of 1fdcee06 (not the worktree; `git diff --stat` each non-empty, 1 file, 1 line): M1 drop `$` anchor of CLOSE_OUT_NOTE -> `4 failed, 18 passed`; M2 `len(rows) == 1` -> `rows` -> `2 failed, 20 passed` (two-done-rows); M3 drop note-vs-record session check -> `2 failed, 20 passed` (other-session). SURVIVED: M0 drop helper's own mtime + `record_confirms_pass` check -> `22 passed`; M4 `return True` instead of the `merge-base --is-ancestor` check -> `22 passed` (see P2-1). Red run before the fix is in Demonstration BEFORE (4 failed, 12 passed). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read: loop-binding block in `admin_refusal`, `_closed_out_since`, `_pass_recorded_since`, `_ready_for_review`, `_session_holds`, `auto_mode.board_rows`, `verify_record.read_record`/`record_confirms_pass`, `lib/auto_closeout.py` `move_to_done` + note writer (line 326, unchanged), the 3 test files, `merge_gate_guard.py` allowlist, `docs/claude-md/tracks.md`. `git diff --stat main...HEAD`: 7 files, 387 insertions, 7 deletions; `lib/auto_closeout.py` and `.claude/settings.json` untouched. grep for the old refusal text outside `tasks/`: no other docs/pins. |
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

---

## Review (round 1)

Reviewer: fresh context, commit 1fdcee06f76e28e29710237ff0330a500f405ab7, code-review + security-review (Risk High), read-only.

### Findings

- **P0 / P1: none.**
- **P2-1 (test gap) `.claude/hooks/tests/test_t354_loop_closed_out_row.py` (no case) vs `pre_bash_block_unsafe_merge.py:~2480-2486`.** The helper's own record checks (file time at or after `--start`, `record_confirms_pass`, branch holds the note's commit) are not pinned: they are shadowed by the outer `_pass_recorded_since`, which accepts any passing record. Failure scenario: a later edit drops the held/mtime checks and the suite stays green (mutants M0 and M4 survived, 22 passed). Then a Done row whose note names a commit with a stale or off-branch record binds as long as some other commit of the task has a fresh held record. The code as written is correct; the guide edge case "the note's commit is the verified commit" is covered only by the positive test. Suggested test: two records for T900, a fresh held one for commit A, and a note naming commit B whose record is dated before `--start` (and one on another branch); expect refusal.
- **P3-1 `pre_bash_block_unsafe_merge.py` `_closed_out_since`: the note's `session` is compared to the record's `session`, not to this session's id.** Same weakness as `_pass_recorded_since` (the own `--start` plus the file time bind the run). Not a new bypass; noted only because the guide says "this session's own run". No change asked.
- **P3-2 docs:** `tracks.md` bullet is now one long sentence chain, and "Done by the hook's close-out of that same pass" never says the note and the pass record must name the same commit in the refusal text. Wording only.

### Security review (merge gate)

- Fail closed: any exception, unreadable board, zero or two Done rows, unmatched note, missing/other-session record, record file older than `--start`, failed `record_confirms_pass`, or commit not an ancestor of the task branch returns False. Note regex is anchored at row end, 40 lowercase hex, so short sha, uppercase and trailing text do not bind.
- No new bypass: an agent that hand-writes a Done row and note still needs a hook-written run record newer than its own `--start` and held by the branch, the same bar the loop already needed (the outer `_pass_recorded_since` and `_session_holds` are unchanged and still ANDed). Before this change an agent could equally hand-move a row to Ready for Review. Move to Done adds no capability; Todo-row and another-task-row notes are tested as non-binding.
- Scope: only the loop (`started is not None`) branch changed; the request/guide/short-yes bindings, the `main` push rule and `auto_closeout.py` are untouched. `[ticket]` still cannot merge (unchanged code path; tested through `_gate_case` push).
- `merge_gate_guard.py` allowlist + its pin test updated consistently with T354 owning the rule.
- No secrets, no new shell execution, no path built from the note except through `record_path` with a 40-hex sha.

### Test output

`317 passed in 60.11s (0:01:00)` for the Verification Command (pasted in the Evidence rows above).

### Verdict

**PASS with findings** (no P0/P1; one P2 test-gap, two P3). Merge is acceptable; adding the P2-1 test is recommended before or right after merge.
