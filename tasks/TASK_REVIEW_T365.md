# TASK_REVIEW — T365: The merge gate's T321 refusal texts name the remote, never `None`

> Sibling of `tasks/TASK_GUIDE_T365.md`. Stage 4 review by a fresh-context reviewer (not the author), commit `f364bdedc22dbe0eb10eddfd0bab6bd2827f8c1d`, diff `main...f364bded`.

## Auto decisions

Mode: auto
1. Took T365 after T366 and T364, one task at a time — RULE: `docs/claude-md/tracks.md` `### Admin tag` (one request runs each task Stage 0–5); the user's request "continue your work on the pending tasks, [admin]"
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High row)
3. The Supervisor wrote the code, one fresh `Reviewer: T365` spawn (two rounds) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. Item 2 (the run-record slug) split out to T369, not fixed here — DEBATED: Advocate 1: fix it in T365 (`repo_slug` reads `remote.<admin remote>.url`; it conceded the slug would then depend on a setting only Claude Code sessions get, so `scripts/verify_trace.py` from a plain terminal reads the wrong folder); Advocate 2: split it (every anchor, record and resume mark lives under the slug: `.claude/hooks/lib/trace_chain.py:79`, `verify_record.py:125`, `auto_mode.py:197`); Advocate 3: split it and add a temporary pin test of today's slug (the smallest safe thing). Settled by a written rule: `docs/claude-md/tracks.md:35` "The change deletes, moves, renames or converts user data or its storage format … | extended" (moving the record folders is its own extended task). Advocate 3's pin test not added: `memory/learning-records/LR-0004-pin-tests-hit-later-tasks.md` (pin tests break later tasks), and the T369 row tracks the bug
5. Fixed both reviewer P3 findings (an assert the appended `AUTO_MODE_LIMIT` always satisfied; no test that another git failure is not "no remote") and spawned the reviewer again on the new commit — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires"
6. Added T365 to `AUTHORISED_TASKS` (`.claude/hooks/tests/merge_gate_guard.py`, its pin in `test_merge_gate_guard.py`, and the guide's Files to Change row) after the user signed it off, then spawned `Reviewer: T365` again on that commit — RULE: `.claude/hooks/tests/merge_gate_guard.py:22` "A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off"; the user's answer "T365 (paused, ready)" to the gate sign-off question (2026-11-25, session 43b43f7e)
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t365_admin_remote_texts.py` — 23 passed after the P3 fixes (red first: `18 failed, 1 passed` at 2026-11-25T09:15:30Z, before the change); guide Verification Command — Reviewer `350 passed`; full suite `61 failed, 7966 passed` vs `main` `60 failed` (the 1 extra passes alone; the 3 merge-gate pins fixed by the `AUTHORISED_TASKS` entry, user sign-off "approve"); guard `.claude/hooks/tests/test_merge_gate_guard.py` 32 passed; reviews `Reviewer: T365` PASS in two rounds (P3 only), `code-review` rules in the Supervisor session no P0–P2; `security-review` skill in the Supervisor session (started with a temporary `refs/remotes/origin/HEAD` at the base `480227da`, removed right after with `git update-ref -d`; its precomputed diff was the main checkout's, so its sub-task read the branch range `main...979783b3`) — no vulnerabilities; real run: the gate refuses `git push github <branch>` with "this repository has no remote `github`" (`test_ac1_a_missing_set_remote_is_named`, a constructed repo) (auto-checked, not /verify); how AC 2 shows in a real run: every push under a bad setting is refused first by `_admin_remote_refusal` ("is a b, not a plain remote name", no `None`: verify run 1, step 4), so the `[ticket]` merge text and `_main_push_refusal` are reached only behind a bound loop with a passed verify; those two are covered by `test_ac2_the_ticket_merge_refusal_never_prints_none` and `test_ac2_main_push_refusal_names_the_setting_not_none` (red before the change)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); auto verify: ☐ blocked (session 60e6963e-d4cf-4c74-8511-c91b2dabfd78, commit cb67efc794bbbb7e42c04654e47dfa4dc380d505, log .claude/verify-runs/T365-cb67efc794bb.log); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`); T369 (the slug) registered, not started; numbered T369 because a parallel session registered T368 on `main` the same minute
Paused: 2026-11-25 for the user's `AUTHORISED_TASKS` sign-off (the auto-mode classifier refused the Supervisor's own edit of the gate pin list); resumed in session 43b43f7e after the sign-off

## Review verdict: PASS (no P0/P1/P2 finding; two P3 notes)

Scope: `_admin_remote_text`, `_missing_remote_refusal`, their three call sites (`admin_refusal` `[ticket]` merge text, `admin_refusal` push path, `_main_push_refusal`), the `_own_origin_refusal` and `_remote_main` docstrings, and the T321 tests.

### Allow/refusal analysis (the guide's claim: texts change only)

- Push path: `_missing_remote_refusal` fires only when `git remote get-url <remote>` exits non-zero with "no such remote" on stderr. Before the change, the same case reached `_admin_push_target_refusal` (get-url failure returns None there) and then `_admin_push_branch`, which returns None when `get-url` fails, so the push was refused with the generic text. The new check adds a refusal only where one already happened. No allow became a refusal. Any other failure (no git, a timeout, a localised git message, not a repository) returns None and falls to the old checks, so nothing becomes an allow.
- `_main_push_refusal`: the new early return runs only when `_admin_remote()` is None. Before, `_remote_main` returned None for that case and the function refused with "cannot read the remote's real `main`". Refusal to refusal, text only.
- `[ticket]` merge: still returns a refusal string. Only the interpolated value changed.
- The remote name put in the new text passes `REMOTE_NAME_PATTERN` (`[A-Za-z0-9._-]+`), and `_admin_remote_text` prints only the setting's name, so no repository-chosen text reaches the message unbounded. A hostile repo can shape the git stderr only toward a refusal, never an allow.

### Findings

| # | Severity | Confidence | File:line | Finding | One-line fix |
|---|----------|-----------|-----------|---------|--------------|
| 1 | P3 | 90 | `.claude/hooks/tests/test_t365_admin_remote_texts.py:41` | `ENV in text` is vacuous. `reason()` returns the refusal with `AUTO_MODE_LIMIT` appended, and that constant holds `EASY_KIT_ADMIN_REMOTE`. Mutation: removing `ADMIN_REMOTE_HINT` from the new text leaves all 19 tests green. AC 1 ("and the setting's name") is not pinned. | Assert the name against the helper's own text: `merge_gate._missing_remote_refusal(fx.wt)` contains `ENV`, or strip `AUTO_MODE_LIMIT` before the check. |
| 2 | P3 | 80 | `.claude/hooks/tests/test_t365_admin_remote_texts.py` (no test) | Edge case 1 of the guide ("`get-url` failing for another reason is not 'no remote'") has no test. Mutation: dropping the `"no such remote"` stderr match (any failure reads "no remote") leaves 19 + 70 T321 tests green. | Add a test that makes `_git` return a failure with other stderr and asserts `_missing_remote_refusal(...) is None`. |

Not findings: `_admin_push_target_refusal`'s docstring and `AUTO_MODE_LIMIT` still say `origin` (pre-existing, `AUTO_MODE_LIMIT` is explicitly out of scope). The extra `git remote get-url` call adds latency only.

### security-reviewer.md (hooks section) checks

- Input the hook did not write: the env value and git stderr are the inputs. The env value is validated before use; the stderr is only matched, never echoed.
- No new subprocess form: `_git` runs argv with no shell and a 5 s timeout, the same call `_admin_push_target_refusal` already makes.
- No new fetch, install step or CI change. No gate bypass found.

### Negative cases: mutation of a scratch copy (worktree untouched)

| Mutation | Result | Tests that turn red |
|---|---|---|
| M1 drop the `_missing_remote_refusal` call in the push path | 3 failed | `test_ac1_a_missing_set_remote_is_named[named]`, `[bare]`, `test_ac1_the_ticket_push_names_the_missing_remote_too` |
| M2 drop the `_admin_remote() is None` guard in `_main_push_refusal` | 7 failed | `test_ac2_main_push_refusal_names_the_setting_not_none[*]` (all 7 `BAD`) |
| M3 `[ticket]` merge text back to `` `{_admin_remote()}` `` | 7 failed | `test_ac2_the_ticket_merge_refusal_never_prints_none[*]` (all 7) |
| M4a `_own_origin_refusal` docstring back to `origin` only | 1 failed | `test_ac3_docstrings_name_the_admin_remote` |
| M4b `_remote_main` docstring back to `ls-remote origin` | 1 failed | `test_ac3_docstrings_name_the_admin_remote` |
| M5 stderr match never true | 3 failed | the three AC 1 tests |
| M8 text drops the remote name | 3 failed | the three AC 1 tests |
| M7 text drops the setting name (hint) | 19 passed (survives) | none: finding 1 |
| M6b any `get-url` failure reads "no remote" | 19 + 70 passed (survives) | none: finding 2 |
| `test_ac1_control_the_remote_exists_and_the_push_runs` | no mutation run | guards a change that refuses when the remote exists; would go red if the helper returned text on rc 0 |

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t365_admin_remote_texts.py` (AC 1 to 3; AC 4 is `.claude/hooks/tests/test_t321_admin_remote.py`, unchanged). Two P3 gaps: findings 1 and 2 |
| Verification command run | ☑ pass | `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t365_admin_remote_texts.py .claude/hooks/tests/test_t321_admin_remote.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_t210.py` printed `350 passed in 32.17s` |
| Negative cases hold | ☑ pass | Mutations M1 to M5 and M8 turn the matching tests red (table above); the mutated copy was `git archive HEAD` extracted to the session scratchpad, never the worktree. M6b and M7 survive (P3) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the two helpers, three call sites, two docstrings, the T321 and T365 tests, plus the callers `_admin_push_target_refusal`, `_admin_push_branch`, `_own_origin_refusal`. Skipped: the rest of the gate and the full suite, as instructed |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression (Supervisor, at `18a8fce2`): `61 failed, 7966 passed, 24 skipped` vs clean `main` worktree `60 failed, 7943 passed, 24 skipped`; the 1 extra, `.claude/hooks/tests/test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, passes alone (`9 passed`) and reads no changed file. The first run (at `979783b3`) had 3 more: the merge-gate pins, fixed by the `AUTHORISED_TASKS` entry (user sign-off "approve") |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI |

---

## Demonstration

**BEFORE** (2026-11-25T09:15:30Z, the new test file on `main`'s hook, before the implementation commit): `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t365_admin_remote_texts.py` — `18 failed, 1 passed`: a push to a set remote that does not exist got the generic "`[admin]` allows only a plain push of the task branch …" text; under a bad value the `[ticket]` merge refusal read "… to `None`" and `_main_push_refusal` read "`git ls-remote None refs/heads/main` failed"; both docstrings said `origin`.

**AFTER** (branch head): the same file — `23 passed` (4 more cases after the P3 fixes); the push is refused with "this repository has no remote `github`: `[admin]` and `[ticket]` push only to it (the one remote is `EASY_KIT_ADMIN_REMOTE` …); add it with `git remote add github <url>` or change the setting"; no refusal prints `None`.

**DELTA**: a user who sets `EASY_KIT_ADMIN_REMOTE` to a remote they have not added is told exactly that, and a bad setting is named in every refusal instead of `None`; no command is allowed or refused differently.

**WITNESS**: Supervisor session acceb8c1, 2026-11-25 (BEFORE red run, full-suite comparison); `Reviewer: T365` (fresh qa-expert, commit `f364bded`, mutations on a scratch copy; round 2 on the fix commit).

## Round 2 (Reviewer: T365, commit 18a8fce2)

Verdict: PASS (no P0, P1, P2 or P3 finding). Scope: the whole diff `main...18a8fce2`, bounded to the gate's T321 texts, the two new tests, and the `AUTHORISED_TASKS` pin.

### Round 1 findings

| # | Status | Evidence |
|---|---|---|
| 1 (setting name vacuous) | Fixed | `test_ac1_a_missing_set_remote_is_named` now asserts `ENV` and `` `github` `` on `merge_gate._missing_remote_refusal(fx.wt)` itself. Mutation on a scratch copy (`git archive`, hint replaced by `()`): `2 failed, 21 passed` (`[named]`, `[bare]`) |
| 2 (other git failure is not "no remote") | Fixed | New `test_ac1_only_git_no_such_remote_counts_as_missing` (4 cases plus `_git` returning None). Mutation (the `"no such remote"` stderr match removed): `2 failed, 21 passed` (`[not-a-repo]`, `[other-error]`) |

### `AUTHORISED_TASKS` entry

`.claude/hooks/tests/merge_gate_guard.py`: one comment block and the tuple gain only `"T365"` (last). The block follows the others' format (ID, dash, the rule it owns, the guide and AC, who authorised, date) and names the rule: the T321 refusal texts (`_missing_remote_refusal`, `_admin_remote_text`, `_main_push_refusal`), texts only. `.claude/hooks/tests/test_merge_gate_guard.py`: one comment and the pinned tuple gain only `"T365"`. No other ID changed or moved. The hook's diff is texts and docstrings; no allow or refusal changed (as round 1 analysed; unchanged since).

### security-reviewer.md (hooks section)

Env value is validated before use; git stderr is matched, never echoed; `_git` is argv with a timeout, no shell; no fetch, installer or CI change; `.claude/settings.json` untouched. Nothing found.

### Findings

None.

### Commands run (worktree)

- `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t365_admin_remote_texts.py .claude/hooks/tests/test_t321_admin_remote.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_t210.py` printed `354 passed in 20.68s`
- `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_merge_gate_guard.py` printed `32 passed in 0.89s`
- Full suite not run (one was running).
