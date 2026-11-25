# TASK_REVIEW — T372: The `[admin]` loop binds on the run record's own start stamp, and a repeated tag keeps the window

> Sibling of `tasks/TASK_GUIDE_T372.md`. Reviewer: fresh-context qa-expert, commit `5d4ebc21e8a52a75b4c13bf4c5431b87ef19ef78`, diff `main...5d4ebc21`. Risk High (merge-gate hook).

## Verdict: PASS (no P0/P1/P2). Two P3 notes.

## Findings

| # | Sev | Conf | Finding |
|---|-----|------|---------|
| 1 | P3 | 90% | Mutation M6 (drop `onset[0] == tag` in the gate) survives. `tag` and `onset[0]` come from the same `_session_scan` pass, so they cannot differ today; the check is defence in depth, not an observable behaviour. No action needed. |
| 2 | P3 | 85% | Mutation M7 (`started_by and started_at` -> `or`) survives: no test passes one stamp key alone to `write_record`. Gate side is safe (`_stamped_start_since` needs both: `parse_ts(None)` -> skipped, and `started_by` must equal the session). Optional one-line test. |
| 3 | info | 80% | Stamp is as forgeable as the pass record itself (any Bash can write `.claude/verify-runs/*.json`, or set `CLAUDE_CODE_SESSION_ID`). Same trust level as the existing `_pass_recorded_since` / `_closed_out_since` bindings; it adds no new capability. It still needs a pass record written at/after `started_at`, a commit the branch holds, and `_session_holds` on the window. |

Security-reviewer (hooks) checks: fails closed on every path (bare `except` -> None; unset or malformed session id -> no stamp; unparsable `started_at` -> skipped; wrong session, stamp before onset, commit not an ancestor of `refs/heads/<branch>` -> binds nothing). The window widens only inside the loop branch, only to the onset of the same tag (`onset[0]==tag`, `onset[1]<=when`), and `_session_holds` only gets stricter with a wider window (it refuses on any other In Progress / Ready for Review task worked on). `session_request`, the name, guide, short-yes bindings and `_session_admin_merges` are unchanged. `stop_hook` path passes no stamp; `main()` accepts argv 8, 9 or 11 (10 is rejected, fine). `AUTHORISED_TASKS` change matches the guide's recorded user sign-off, and the pin test is updated in step. Docs (`tracks.md` `### Session tags`) state both rules (AC 6).

Scope: reviewed the 5 hook files, both guard files, the 2 new tests and the doc hunk; blast radius = callers of `admin_refusal` loop branch, `write_record`, `run()`/`start()`. Not reviewed: unrelated gate branches, T370 `ADMIN_MAIN_BRANCH` (out of scope).

## Negative cases (mutations, on a `git archive` scratch copy, never the worktree)

| Mutation | Result |
|---|---|
| M1 drop `started_by == session` | killed (`test_ac2_a_stamp_from_another_session_does_not_bind`) |
| M2 drop `at < when` (onset) | killed (`test_ac2_a_stamp_before_the_tag_does_not_bind`) |
| M3 drop branch-holds check | killed (`test_ac2_..._commit_the_branch_does_not_hold...`) |
| M4 window = latest request (`since = when`) | killed (`test_ac3_a_repeated_admin_tag_after_the_pass_keeps_the_binding`) |
| M5 onset moves on a repeated tag | killed (same AC 3 test) |
| M6 drop `onset[0] == tag` | survived (equivalent today, P3 #1) |
| M7 `and` -> `or` in `write_record` | survived (P3 #2) |

Baseline on the scratch copy: 18 passed.

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t372_start_stamp.py` (18 tests, AC 1-4 + `session_onset`), `tests/test_t372_start_stamp_run.py` (3 tests, AC 4 end to end) |
| Verification command run | ☑ pass | Guide's command, in the worktree: `853 passed in 129.62s (0:02:09)` |
| Negative cases hold | ☑ pass | 5 of 7 mutations killed; the 2 survivors are P3 (table above) |
| verify | ☐ pass / ☐ fail / ☐ N/A | left for the auto verify hook |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | the 10 changed files plus `_session_holds`, `_pass_recorded_since` readers; see Scope above |
| Full smoke suite still green (no regression) | ☑ pass | Reviewer: the 11 suites in the Verification Command pass unchanged. Supervisor, whole repo (`python3 -m pytest -q -p no:cacheprovider tests/ .claude/hooks/tests/`): branch `63 failed, 7980 passed, 24 skipped` against `main` `60 failed, 7958 passed, 24 skipped` (same day). The 3 extra failures all pass when rerun alone (`8 passed in 13.01s`): `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository` and `test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged` ran while the Supervisor committed in the repo (the first also failed on the T365 branch the same way); `test_t372_start_stamp_run.py::…[not a session id!]` failed once under full-suite load with a concurrent reviewer run, then passed 5 of 5 alone (`6 passed` each). No failure on `main` is missing on the branch. |
| **Companion score (easy-verifier)** | ☑ N/A | not run |
| **UI rows** | ☑ N/A | no UI |

## Auto decisions

Mode: auto
1. Took T372 first, then T370, and left T365 to the other live session (acceb8c1), which had committed in `../wt-t365` at 17:57 — RULE: `docs/claude-md/tracks.md` `### Session tags` (loop step 1: "it is not claimed by another live session … the highest Priority first"); the user's answer "Take T372 and T370" (2026-11-25, session 43b43f7e)
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High, C2 rows)
3. The Supervisor wrote the code test first; one fresh `Reviewer: T372` spawn — RULE: `docs/claude-md/pipeline-stages.md:198` "on the extended track the Supervisor writes the code itself, in the task's worktree, test first"
4. The binding design: stamp `started_by`/`started_at` into the run record from `--start`, and read the loop window from the tag's onset (`auto_mode.session_onset`), loop branch only — DEBATED: A + C (Advocate 1: stamp `requester`/`started` in the record and keep the first tag time in `session_request`; Advocate 2: a separate `<task>-<sha>.start.json` stamp file plus `session_onset`; Advocate 3: stamp in the record plus `session_since`, loop branch only). All three agreed on A + C. The record over a separate file, and the loop-branch-only window, by the safer option (the smaller change; `session_request` unchanged keeps `_session_admin_merges` as it is) ⚠ decided for you — please review
5. Kept the transcript reading of `--start` (`_own_start_since`) beside the stamp, though all three Advocates proposed replacing it — RULE: `skills/resolve-question/SKILL.md:138` "the **safer option**: it can be undone > it keeps all data > it is the smaller change" (nothing that binds today stops binding; a run started before this change has no stamp and still binds) ⚠ decided for you — please review
6. Added T372 to `AUTHORISED_TASKS` (`.claude/hooks/tests/merge_gate_guard.py`, its pin in `test_merge_gate_guard.py`, the guide's Files to Change row) — RULE: `.claude/hooks/tests/merge_gate_guard.py:22` "A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off"; the user's answer "T372" to the gate sign-off question (2026-11-25, session 43b43f7e)
7. Dropped the planned "not in the future" check on `started_at`: the test fixtures date the tag 60 s ahead, and `_pass_recorded_since` already refuses a pass record older than the start — RULE: `docs/claude-md/tracks.md` `### Session tags` "The hook wrote its auto verify pass after that call"
8. Left both reviewer P3 notes (M6: `onset[0] == tag` cannot differ today; M7: one stamp key alone is not tested) without a code change, so the reviewed commit stays the merged code — RULE: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |"
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t372_start_stamp.py tests/test_t372_start_stamp_run.py` — red first `16 failed, 8 passed` at 2026-11-25T11:13:31Z (before the change), then `24 passed`; guide Verification Command `853 passed in 129.58s` (Supervisor) and `853 passed in 129.62s` (Reviewer); full suite: see the Evidence row; reviews: fresh `Reviewer: T372` PASS (P3 only), `security-review` skill in the Supervisor session (started with a temporary `refs/remotes/origin/HEAD` at the base `81bdae3a`, removed right after with `git update-ref -d`; its precomputed diff was the main checkout's, so its sub-task read the branch range `81bdae3a...5d4ebc21`) — no findings at confidence 8 or above; real run: `stop_auto_verify.py --start T951` with a stubbed `claude` writes `started_by`/`started_at` into the run record (`test_ac4_start_stamps_the_starting_session_and_time`, a constructed project) (auto-checked, not /verify)
Memory: memory/learnings.md — two live `[admin]` sessions on one board: check the worktree's latest commit and `.claude/hooks/.state/active_task.d/` before resuming a paused task (T365, 2026-11-25)
Not done: merge (admin: after the auto verify pass); auto verify: running (T182); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`, a settings change that stays yours); follow-up not registered yet: a long loop's `main` push sees every merge since the tag request (Advocate 1)

## Demonstration

**BEFORE** (2026-11-25T11:13:31Z, the new tests on the unchanged hooks): `16 failed, 8 passed`. A loop whose `--start` ran as `python3 .claude/hooks/stop_auto_verify.py --start T900 > run.log` (or from a script) was refused: "T900 is not the task of the `[admin]` request … nor the task of this session's loop". A later "final flow with [admin] tag is to merge to main" also refused a loop that had already passed.

**AFTER** (branch head `5d4ebc21`): the same files `24 passed`. The run record carries `started_by` and `started_at`; the merge is allowed for this session's stamp, refused for another session's stamp, a stamp before the tag, or a stamp for a commit the branch does not hold; a repeated `[admin]` keeps the window, and a `[ticket]` in between resets it.

**DELTA**: under `[admin]` the Supervisor's own auto verify start binds its loop task whatever shell form ran it, and a reply that only mentions `[admin]` no longer blocks the merge. No other binding changed.

**WITNESS**: Supervisor session 43b43f7e, 2026-11-25 (BEFORE red run, full-suite comparison); `Reviewer: T372` (fresh qa-expert, commit `5d4ebc21`, mutations on a scratch copy).
