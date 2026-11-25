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
Checks: tests `python3 -m pytest` (the guide's Verification Command) — `321 passed` at 99978dad (round 2 reviewer); `test_t354_loop_closed_out_row.py` `26 passed`, mutations M0 and M4 each `2 failed, 24 passed`; full suite `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 1fdcee06: `58 failed, 7815 passed, 24 skipped`; 57 are the same list as clean `main` (`76b76bfc`, this session's environment); the 58th, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, ran while the Supervisor committed in this worktree and passes alone (`9 passed`); reviews: Reviewer round 1 (1fdcee06) PASS with findings, 1 P2 fixed in 99978dad; round 2 (99978dad) PASS, P3 only; Supervisor `code-review` 0 P0/P1/P2, 3 P3; `security-review` (temporary `origin/HEAD`, removed after) no findings; real run: the T347 refusal shape replayed by `test_a_done_row_with_this_runs_close_out_note_binds_the_loop` (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T354: the session loop binds its task after the close-out moved the row to Done
Not done: merge (admin: after the auto verify pass); push (the merge gate pushes to `origin` only and this repo's remote is `github`: T321); auto verify: not started
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report 3ffea37e141a]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t354_loop_closed_out_row.py` (22 tests, [admin]/[ticket]): AC1/2 `test_a_done_row_with_this_runs_close_out_note_binds_the_loop`, `test_the_last_close_out_note_of_the_row_counts`; AC3/4 `test_a_done_row_without_this_runs_note_does_not_bind` (no-note, other-commit, short-sha, record-before-start, other-session, note-not-at-row-end); AC5 `test_a_close_out_note_in_a_todo_row_does_not_bind`, `test_another_tasks_done_row_note_does_not_bind`, `test_two_done_rows_for_the_task_do_not_bind`. AC6 (docs/refusal text): no test, read in diff (`docs/claude-md/tracks.md`, refusal text). Edge-list gaps: see Review (round 1) P2-1. |
| Verification command run | ☑ pass | `PATH=<venv>/bin:$PATH python3 -m pytest .claude/hooks/tests/test_t354_loop_closed_out_row.py .claude/hooks/tests/test_t317_fix_round.py .claude/hooks/tests/test_t317_loop_binding.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider` -> `317 passed in 60.11s (0:01:00)` (at 1fdcee06) |
| Negative cases hold | ☑ pass | Mutations on a `git archive` copy of 1fdcee06 (not the worktree; `git diff --stat` each non-empty, 1 file, 1 line): M1 drop `$` anchor of CLOSE_OUT_NOTE -> `4 failed, 18 passed`; M2 `len(rows) == 1` -> `rows` -> `2 failed, 20 passed` (two-done-rows); M3 drop note-vs-record session check -> `2 failed, 20 passed` (other-session). SURVIVED: M0 drop helper's own mtime + `record_confirms_pass` check -> `22 passed`; M4 `return True` instead of the `merge-base --is-ancestor` check -> `22 passed` (see P2-1). Red run before the fix is in Demonstration BEFORE (4 failed, 12 passed). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read: loop-binding block in `admin_refusal`, `_closed_out_since`, `_pass_recorded_since`, `_ready_for_review`, `_session_holds`, `auto_mode.board_rows`, `verify_record.read_record`/`record_confirms_pass`, `lib/auto_closeout.py` `move_to_done` + note writer (line 326, unchanged), the 3 test files, `merge_gate_guard.py` allowlist, `docs/claude-md/tracks.md`. `git diff --stat main...HEAD`: 7 files, 387 insertions, 7 deletions; `lib/auto_closeout.py` and `.claude/settings.json` untouched. grep for the old refusal text outside `tasks/`: no other docs/pins. |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 1fdcee06: `58 failed, 7815 passed, 24 skipped`. 57 failures are the same list as clean `main` (`76b76bfc`) in this environment; the 58th (`test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`) ran while this worktree took a commit and passes alone, `9 passed`. No failure comes from the gate change. |
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

**AFTER**: `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t354_loop_closed_out_row.py` at 99978dad: `26 passed` (the 4 BEFORE failures pass; 22 refusal cases hold).

**DELTA**: under a session `[admin]` the loop merges its own task after the auto verify pass and close-out, with no `merge <ID> [admin]` typed; `[ticket]` pushes its task branch the same way.

**WITNESS**: Reviewer rounds 1 and 2 (fresh context) re-ran the Verification Command and the mutations; the auto verify run is the independent check (`memory/event-trace/T354.jsonl`).

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

---

## Review (round 2)

Reviewer: fresh context, commit 99978dad8d24a3c064df41f79ce2f888d5dc68c4, delta `1fdcee06..99978dad`, code-review + security-review (Risk High), read-only (mutations on `git archive` copies in the scratchpad, never the worktree).

### Delta read

Code under test is unchanged since round 1: the delta is one test (`test_the_notes_own_commit_must_pass_the_record_rule`, 2 cases x [admin]/[ticket] = 4 new tests, 26 in the file) plus the review-record fill-in of round 1 (Auto decisions 2, 4, 5 and the Evidence rows). No hook, gate, `settings.json` or `auto_closeout.py` change; the security conclusions of round 1 stand unchanged.

### Findings

- **P0 / P1 / P2: none.** Round 1's P2-1 is closed for two of the three record checks it named.
- **P2-1 closed.** Mutations on a copy of 99978dad (`git diff --stat` 1 file each, non-empty):
  - M0a drop `os.path.getmtime(path) < when.timestamp()` -> `2 failed, 24 passed` (the `note-record-before-start` cases, admin and ticket).
  - M4 `return held is not None and held.returncode == 0` -> `return True` -> `2 failed, 24 passed` (the `note-commit-off-branch` cases).
  - M0 (both dropped mtime + `record_confirms_pass`) -> `2 failed, 24 passed`.
  - The new cases are real: commit A holds a fresh held record so the outer `_pass_recorded_since` passes, and only the helper's own check on B refuses (round 1: these mutants passed 22/22).
- **P3-1 (residual survivor) `pre_bash_block_unsafe_merge.py:2482` `or not record_confirms_pass(where, record)` is still unpinned.** M0b (drop only that line) -> `26 passed`. Scenario: a Done row whose note names commit B with a fresh, held record whose verdict is not `pass` (e.g. `fail`) binds while commit A has a passing record. Low reach: the close-out writes the note only after a pass, so the row would have to be hand-written, and an agent that hand-writes a Done row still needs the A record. Suggested test: the same case with `write_record(..., "fail", ...)` for B, fresh and held; expect refusal.
- **P3-2 (carried from round 1, not in the delta):** the note's `session` is compared with the record's `session`, not with this session's id (the own `--start` plus the file time bind the run). No change asked.
- **P3-3 (carried, docs wording):** `tracks.md` bullet and refusal text do not say the note and the pass record name the same commit. Wording only.
- Test code quality: `_second_record` imports `time` inside the function (style only); the `assert other != verified_sha(fx)` guard in the first case makes the fixture self-checking; the second case commits to `fx.main` and passes through `git(fx.main, ...)` as the other fixtures do. No flakiness seen (two timing offsets, +10 s and +60 s, are relative to the fixed `TAG_AT`).

### Security review (merge gate)

Unchanged from round 1 (no code in the delta): fail closed on any exception or doubt; the loop branch only; the outer `_pass_recorded_since` and `_session_holds` stay ANDed; the `main` push rule, request/guide/short-yes bindings and `auto_closeout.py` untouched; no secrets or new shell execution. The delta strengthens the pin on two of the three record checks. The one unpinned check (P3-1) is defence in depth behind the outer pass rule.

### Test output

Verification Command, from the worktree, with the scratchpad venv first on `PATH`:

```
PATH=<scratchpad>/venv/bin:$PATH python3 -m pytest .claude/hooks/tests/test_t354_loop_closed_out_row.py .claude/hooks/tests/test_t317_fix_round.py .claude/hooks/tests/test_t317_loop_binding.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider
321 passed in 35.49s
```

(round 1: 317 passed at 1fdcee06; +4 = the new test.) The full smoke suite was not run in this review.

### Verdict

**PASS with findings** (no P0/P1/P2; round 1's P2-1 closed; three P3: one residual unpinned check, two carried wording/weakness notes). Merge is acceptable.

## Supervisor Stage 4 runs

- `code-review` (Supervisor, range `main...99978dad`): P0 none, P1 none, P2 none (round 1 P2-1 closed). P3: `normalize_task_id` computed twice in `_closed_out_since` (cosmetic); the `tracks.md` loop bullet is long; AC 6 is docs-only with no test. Lane: `lane: C2, 6 files, 377 lines, FITS; unpredicted: .claude/hooks/tests/test_merge_gate_guard.py, tasks/TASK_GUIDE_T354.md`. Stale-reference sweep: no other quote of the old refusal text outside `tasks/`.
- `security-review`: the first `Skill({ skill: "security-review" })` failed (`fatal: ambiguous argument 'origin/HEAD...'`: this repo's remote is `github`). Per `docs/claude-md/tracks.md` `### Known limits`, the Supervisor added a temporary `refs/remotes/origin/HEAD` (= `main`, `ac9704c0`), ran the skill, and deleted the ref right after (`git update-ref -d`, 0 `refs/remotes/origin` refs left). The skill's own diff was empty (the main checkout does not hold the branch), so its method ran on `git -C ../wt-t354 diff main...99978dad`: a scan sub-task found no finding at the >8/10 bar. Leads rejected: a forged close-out note (3/10: no new capability, the agent could already move the row to Ready for Review; the hook's run record, the hook-written verify row and the reviewer record stay required), the note's session not tied to this session, an older note commit, path traversal (40-hex sha), crafted board sections, the record file time, the T341 reviewer gate, the `[ticket]` and `main` push paths, errors (fail closed). Optional hardening (not a vulnerability): require the record's session to be this session's run. Also a by-hand pass by the rules of `skills/code-review/references/security-reviewer.md`: no findings.
- Accepted P3s (follow-ups, not fixed here): round 2 P3-1 (`record_confirms_pass` in the helper unpinned); the T323 short-yes path (`answered()`) keeps the Ready-for-Review-only rule.
