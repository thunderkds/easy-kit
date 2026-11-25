# TASK_REVIEW — T318: `stop_auto_mode_check.py` does not read its own `Paused:` line as a decision

> Sibling of `tasks/TASK_GUIDE_T318.md`. Stage 4 review by a fresh-context reviewer (not the author). Round 1: commit `c843e9582a293560069b4612bda6245733807f66`. Round 2: commit `8fdc3b75575645096ad3dd361c7da9512531815f`. Diff `48a73f81..8fdc3b75`.

## Auto decisions

Mode: auto
1. Took T318 because T346, T375 and T328 already had a worktree from a parallel session; T318 edits a file none of them touch — RULE: `AGENTS.md:142` (the extended track runs on, one task at a time; the user's request "continue your work by picking tasks [admin]")
2. Track extended — RULE: `AGENTS.md:142` ("Risk Medium or High" puts a task on the extended track; the board row says Risk Medium)
3. The Supervisor wrote the code, one fresh `Reviewer: T318` spawn per round (two rounds) — RULE: `AGENTS.md:171` ("the Supervisor writes the code itself, in the task's worktree, test first")
4. Narrowed the filter from every `STAMP_SKIPS` prefix to the `PAUSE` text only, after round 1 P2-1 (a flagged choice could hide behind `Not done:`, `Closed:` or `- verify:`); a new reviewer round on the new commit — RULE: `skills/code-review/SKILL.md` § Finding Classification (P2 is recommended; the fix is one expression, and the merge gate wants the reviewer to see the merged code)
5. Kept the guide on `main` and on the branch identical, so the merge has no add/add conflict, and put the review file on `main` where the stop check reads it — RULE: `AGENTS.md:171` (the merge gate reads a reviewer record for the code being merged)
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t318_paused_line_not_a_decision.py .claude/hooks/tests/test_stop_auto_mode_check.py` — 90 passed at `8fdc3b75`; the new file is red on the base hook first (`1 failed, 2 passed`, AC 1 fails); related suites (`test_t250_session_ownership`, `test_t317_fix_round`, `test_t247_auto_span_entries`, `test_t310_admin_unsure_stop`, `test_admin_tag`, `tests/test_hooks_from_plugin.py`, `tests/test_plugin_init.py`) 551 passed at `c843e958`; code-review (Supervisor, no P0 to P3 on the one-line change; `lane_check`: C1, 3 files, FITS) and security-review (Supervisor, no finding at confidence 8 or higher)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); auto verify (starts now that round 2 passed); push (`EASY_KIT_ADMIN_REMOTE` decides the remote)
Paused: done not moved — the verify result is not confirmed by its run record (the merge gate's rule); report incomplete: auto verify slot

## Review verdict

Round 1 (`c843e958`): PASS, no P0 or P1; one P2 (P2-1: skipping every `STAMP_SKIPS` prefix lets a flagged decision hide behind a prefix the agent writes itself, confidence 85) and two P3 (no test pins the hole; guide checkboxes unticked). Round 1 verified AC 1 and AC 2 red on the base hook, AC 3 green on both.

Fixed in `8fdc3b75`: the filter uses the `PAUSE` prefix only, AC 2 now pins that `Closed:`, `Not done:`, `**Not done:**`, `- verify:` and a hand-written `Paused: choose B ...` line still block. The guide says so and records the accepted limit (an agent that writes the exact pause text by hand hides that one line).

Round 2 (`8fdc3b75`): PASS, no P0, P1 or P2; one P3.
- Verification Command: `90 passed` (3 T318 tests and 87 in `test_stop_auto_mode_check.py`).
- AC by hook version: base `48a73f81` AC 1 fails (`1 failed, 2 passed`); round 1 `c843e958` AC 2 fails (`1 failed, 2 passed`, so the test pins P2-1); now `8fdc3b75` `3 passed`.
- P2-1 closed: a flagged line behind `Not done:`, `Closed:`, `- verify:`, `**Not done:**` or `Paused: choose B` each blocks. A hook-written pause line does not block a good report, on a normal fire or a second fire.
- `report_stamp` and `last_pause` are unchanged (no hunk touches them).
- P3 (accepted, confidence about 60): a hand-written line that starts with the full `PAUSE` text (`Paused: auto-mode check failed — pick B ...`) is skipped. It needs the agent to imitate the hook's exact prefix, and `PAUSE_LINE` and `last_pause` already trust that prefix. The guide's wording "hand-written `Paused: ...` line still blocks" holds for any text that is not the exact `PAUSE` string; the guide's Cut list already records the accepted limit. Left as is: a guide edit after the reviewed commit would make the merge gate read the review as stale.

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t318_paused_line_not_a_decision.py` (AC 1 to 3; AC 4 is `.claude/hooks/tests/test_stop_auto_mode_check.py`, unchanged) — `3 passed`; on the base hook `1 failed, 2 passed` (AC 1) |
| Verification command run | ☑ pass | the guide's command printed `90 passed` at `8fdc3b75` |
| Negative cases hold | ☑ pass | round 1: AC 1 and AC 2 red on the reverted hook (scratch copy); round 2 probes a flagged line behind each other prefix (blocks) |
| verify | ☑ pass | auto-run by hook, session 2e91ec2d-259b-48ab-bb76-0f2ca0b2157e, commit 4de436e22598544a8287bd6434a16d97eda567cf, log .claude/verify-runs/T318-4de436e22598.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `lines` has two readers in `check_task` (`choice_reason` loop, `DEBATED` list); `report_stamp` and `last_pause` do not read it |
| Full smoke suite still green (no regression) | ☑ pass | round 1 hook suite: `5 failed, 5763 passed`; the 5 are the `MEMORY.md` hot-tier budget (44,683 of 42,000 characters, from `main`'s last memory commit), none touch this change |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI |

---

## Demonstration

**BEFORE** (2026-11-25T15:50:42Z, the final new test file on the base hook `48a73f81`, in a scratch copy): `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t318_paused_line_not_a_decision.py` — `1 failed, 2 passed`. AC 1 fails: a correct Risk High report that holds the hook's own `Paused: auto-mode check failed — Risk High: decision 1 (`⚠`) is a choice ...` line is blocked with "`Paused: auto-mode check failed — Risk Hi` (`⚠`) is a choice ... must be `DEBATED` with exactly 3 Advocates named".

**AFTER** (branch head `8fdc3b75`): the same file — `3 passed`; with `test_stop_auto_mode_check.py`, `90 passed`.

**DELTA**: after a pause, the Stop check no longer blocks a correct report on its own pause line, so the next fire does not report a choice the Supervisor never made. A flagged choice hidden behind `Not done:`, `Closed:`, `- verify:` or a hand-written `Paused:` line still blocks.

**WITNESS**: Supervisor session 8847ad33, 2026-11-25 (BEFORE red run, tests); `Reviewer: T318` (fresh qa-expert, round 1 on `c843e958`, round 2 on `8fdc3b75`, probes on a scratch copy).
