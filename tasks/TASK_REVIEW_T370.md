# TASK_REVIEW — T370: The default branch is the setting EASY_KIT_DEFAULT_BRANCH

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Auto decisions

Mode: auto
1. Took T370 after T372's merge, one ticket at a time — RULE: `docs/claude-md/tracks.md` `### Session tags` (loop step 1: "Take the highest Priority first"); the user's answer "Take T372 and T370" (2026-11-25, session 43b43f7e)
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High, C2 rows)
3. The Supervisor wrote the code test first; one fresh `Reviewer: T370` spawn, two rounds — RULE: `docs/claude-md/pipeline-stages.md:198` "on the extended track the Supervisor writes the code itself, in the task's worktree, test first"
4. The default branch comes from the setting `EASY_KIT_DEFAULT_BRANCH` (default `main`), never from a git ref; the reader in `auto_mode.py` — DEBATED: the setting (Advocate 1: the setting, a reader in a new `lib/default_branch.py`; Advocate 2: the setting, a new `lib/default_branch.py`, None never formatted into a ref; Advocate 3: the setting, the reader in `auto_mode.py`). All three agreed on the setting and rejected `git symbolic-ref`/local refs/`ls-remote --symref` (agent-writable). `auto_mode.py` over a new module by Decide rule 2 (`skills/resolve-question/SKILL.md:138` "it is the smaller change": all three callers already import it). The board row's example (`git symbolic-ref`) is not used ⚠ decided for you — please review
5. Added T370 to `AUTHORISED_TASKS` (`.claude/hooks/tests/merge_gate_guard.py`, its pin in `test_merge_gate_guard.py`, the guide's Files to Change row) — RULE: `.claude/hooks/tests/merge_gate_guard.py:22` "A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off"; the user's answer "T370" to the gate sign-off question (2026-11-25, session 43b43f7e)
6. Fixed reviewer P2-1 (no test drove a bad setting through `verify_record._base()`) with one test, then spawned the reviewer again on the new commit — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires"
7. Left the three P3 notes (`review_in_scope` untested on `master`; stale `main` in docstrings; names git rejects but the check accepts, which fail as a missing ref) without a change — RULE: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |"
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t370_default_branch.py tests/test_t370_cleanup_default_branch.py` — red first `27 failed, 4 passed` at 2026-11-25T11:45:57Z (before the change; the 4 are the controls and the merge that already ran), then `32 passed` with the P2-1 test; guide Verification Command `678 passed` + 2 timing flakes in `tests/test_auto_verify.py` that pass alone (`253 passed in 96.13s` for the whole file), Reviewer `680 passed in 120.08s`; full suite: see the Evidence row; reviews: fresh `Reviewer: T370` round 1 PASS (P2-1 fixed, three P3 left), round 2 PASS on `52a59aab` (P2-1 closed: its mutant now fails `1 failed, 28 passed`; `681 passed` for the Verification Command; one new P3-4, left); `code-review` skill in the Supervisor session (range `c37b386b...146e0800`) — P0 0 / P1 0 / P2 0 / P3 6, no fix needed; `security-review` skill in the Supervisor session (started with a temporary `refs/remotes/origin/HEAD` at the base `c37b386b`, removed right after with `git update-ref -d`; its precomputed diff was the main checkout's, so its sub-task read the branch range `c37b386b...36a1a807`) — no findings at confidence 8 or above; real run: a `master` fixture repo with `EASY_KIT_DEFAULT_BRANCH=master` merges the task branch and pushes `master` through the real gate `main()` (`test_ac2_a_master_repo_with_the_setting_may_push_master_after_its_merge`, a constructed repo) (auto-checked, not /verify)
Memory: memory/decisions.md — T370: the default branch is `EASY_KIT_DEFAULT_BRANCH` (default `main`), never a git ref (commit `c6c2e677`)
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass (session 2c5f336b-72e1-4fff-b182-360d7e9b58dd, commit 146e08007dc0bfde3552838cede51c4b0a8b3c59, log .claude/verify-runs/T370-146e08007dc0.log); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`, a settings change that stays yours); follow-ups not registered: the `[admin]` merge never checks its target branch (a merge into any checked-out branch runs; only pushes are limited), and `.claude/settings.json` is not in its own deny list (Advocate 2; the same for `EASY_KIT_ADMIN_REMOTE`)
Closed: row moved to Done 2026-11-25 — auto verify pass (session 2c5f336b-72e1-4fff-b182-360d7e9b58dd, commit 146e08007dc0bfde3552838cede51c4b0a8b3c59); Gates 5 and 6 checked

## Demonstration

**BEFORE** (2026-11-25T11:45:57Z, the new tests on the unchanged code): `27 failed, 4 passed`. On a `master` repo the push of `master` after the `[admin]` merge was refused ("cannot read the remote's real `main`: `git ls-remote origin refs/heads/main` …"), `verify_record` and `scripts/cleanup_task.py` judged against a `main` that does not exist (cleanup: "branch feat/t900-demo is not merged into main"), and no setting existed.

**AFTER** (branch head): the same files `32 passed`. With `EASY_KIT_DEFAULT_BRANCH=master` the merge and the push of `master` are allowed, an agent-made `main` is not pushable, cleanup removes the merged worktree and branch; a bad value refuses every `[admin]` merge and push and names the setting; unset, everything is `main` as before.

**DELTA**: a repo whose default branch is `master` works under `[admin]` after one settings line; nothing an agent can write in git decides which branch that is.

**WITNESS**: Supervisor session 43b43f7e, 2026-11-25 (BEFORE red run, full-suite comparison); `Reviewer: T370` (fresh qa-expert, commits `36a1a807` and `52a59aab`, mutations on a scratch copy).

## Review verdict

**Verdict: PASS with findings (no P0/P1). Commit 36a1a8073b6e10a81a593975965a9a92c2d7092d, reviewed alone, from the repo only.** Risk High: code-review and the security-reviewer hooks checks applied.

### Findings

| ID | Sev | Conf | Finding | Where |
|----|-----|------|---------|-------|
| P2-1 | P2 | 0.9 | Test gap, proven by a surviving mutant: no test drives a bad setting through `verify_record._base()`. Replacing its `raise OSError` with `return "refs/heads/main"` leaves all 31 new tests green, so the guide's AC 4 "None for a bad value: no docs-only pass" and the edge-case line "`_base()` raises inside its `try`" are pinned only at `base_ref()`, not at `docs_only_change`, `shell_suites_changed` or `record_confirms_pass`. Today the gate refuses first (`_default_branch_refusal`), so no bypass is reachable by the `[admin]` path; the fail-closed layer is unguarded against a later edit. Add one test: bad setting, `docs_only_change(...)` is None and `record_confirms_pass(...)` is False. | `.claude/hooks/lib/verify_record.py` `_base` |
| P3-1 | P3 | 0.9 | Surviving mutant 2: `review_in_scope` with `name = "main"` passes every test; the "bad setting reads the whole history (fail closed)" and the `master` base are untested there. | `.claude/hooks/pre_bash_block_unsafe_merge.py` `review_in_scope` |
| P3-2 | P3 | 0.8 | Stale `main` in docstrings after the change: `verify_record.docs_only_change` ("merge-base of `refs/heads/main`"), `shell_suites_changed` ("left `main`"), `_remote_main`, `_main_push_refusal`, the `main..tip` comments. Refusal texts that say `main` on a `master` repo (`cannot resolve \`main\``, `\`main\` does not hold ...`) are declared out of scope in the guide; only the docstrings are drift. | same files |
| P3-3 | P3 | 0.6 | `default_branch()` accepts a few names git itself rejects (`a/b.lock/c`, `MAIN` on a case-insensitive filesystem) and `refs/heads/x`-style values. All are the user's own setting and fail as a missing ref, never as a wrong ref; fail-closed holds. No change needed. | `.claude/hooks/lib/auto_mode.py` `default_branch` |
| Note | info | 1.0 | Residual exposure, already declared in the guide: the setting sits in `.claude/settings.json`, which an agent can write (same as `EASY_KIT_ADMIN_REMOTE`), and `cleanup_task.py` reads the agent's shell environment. The design is no worse than T321 and better than any git-derived source. Not re-opened here. | guide Cut list |

### Checks done

- Security (hooks): a bad value never reaches a ref or an argv: probed 19 values with the real `default_branch()` (`a\nb`, `feat@{1}`, `-x`, `HEAD`, `a b`, `a~1`, `a^`, `..`, `@`, `a/`, `a.`, `x.lock`, non-ASCII: None; `main`, `master`, `a/b`, `release/1.0`: themselves). No option injection into `git ls-remote` / `merge-base`, which also get `refs/heads/` prefixed.
- Fail closed: `_default_branch_refusal` is the first check in `admin_refusal`, covering `[admin]` and `[ticket]`, merge and push; its message names the setting and the shown value, never `None`.
- A `main` repo with the setting unset: same refs and argv as before; the older suites pass unchanged (680 passed).
- The allowlist change (`AUTHORISED_TASKS` plus its pin test) matches the guide's recorded user sign-off.
- Reader read at call time (not import time), so a session-start setting is honoured.

### Negative cases

| Case | Result |
|------|--------|
| Bad setting (`a..b`, option, `HEAD`, space) refuses merge and push, names the setting | held (mutant `if False:` killed, 4 failed) |
| `master` repo, setting unset: push of `master` refused | held (control test) |
| `master` setting, push of an agent-made `main` refused | held (mutant `branch == "main"` killed, 3 failed) |
| Cleanup on a bad setting removes nothing | held (mutant killed, 1 failed) |
| `verify_record._base` bad value raises | NOT pinned (P2-1) |
| `review_in_scope` on `master` | NOT pinned (P3-1) |

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t370_default_branch.py` (AC 1-4), `tests/test_t370_cleanup_default_branch.py` (AC 5); AC 6 by the older suites. Two paths are not pinned, see P2-1 and P3-1 |
| Verification command run | ☑ pass | the guide's command, run in `/home/thunderkds/workspace/pets/hungnguyen111/wt-t370` at 36a1a807: `680 passed in 120.08s (0:02:00)` |
| Negative cases hold | ☑ pass | 11 mutants on a `git archive` scratch copy (scratchpad `m/`, the worktree untouched), the 2 new test files only: 9 killed (`4 failed`, `5 failed`, `2 failed`, `4 failed`, `1 failed`, `3 failed`, `2 failed`, `2 failed`, `1 failed`); 2 SURVIVED: `verify_record._base` raise replaced by `return "refs/heads/main"` (31 passed) and `review_in_scope` `name = "main"` (31 passed). Pre-change red run: the guide records `27 failed, 4 passed` on `main` |
| verify | ☑ pass | auto-run by hook, session 2c5f336b-72e1-4fff-b182-360d7e9b58dd, commit 146e08007dc0bfde3552838cede51c4b0a8b3c59, log .claude/verify-runs/T370-146e08007dc0.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read the whole diff (10 files). Grepped `.claude/hooks`, `.claude/hooks/lib`, `scripts` for any left `main` ref: none remains as code (`auto_mode.DEFAULT_BRANCH` only); the rest are docstrings and the declared-out-of-scope refusal texts. Skipped: `scripts/agent_ws.py` (uses HEAD, not `main`), site, installer |
| Full smoke suite still green (no regression) | ☑ pass | The 9 files of the Verification Command (680 passed) cover every suite that touches the gate, verify record and cleanup. The whole repo suite was not run by this review. Supervisor, whole repo (`python3 -m pytest -q -p no:cacheprovider tests/ .claude/hooks/tests/`, commit `36a1a807`): `61 failed, 8014 passed, 24 skipped` against `main` `60 failed, 7958 passed, 24 skipped` (same day). The one extra failure, `tests/test_auto_verify.py::test_ac4_blocked_row_never_says_pass[pass-and-fail]`, passes when rerun (`9 passed in 13.24s`), and the whole file passes alone (`253 passed`): a timing flake of the detached runs. No failure on `main` is missing on the branch. |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: no companion tool was asked for this review |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI: hook code, a script and doctrine text |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI: no component, token or style changed |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI: nothing renders at a viewport |


## Round 2

**Verdict: PASS (no P0/P1/P2 open). Commit 52a59aab729b2a8e166c7b5004b74ee101d00efe, reviewed alone, from the repo only.** Risk High.

### Findings

| ID | Sev | Conf | Finding | Where |
|----|-----|------|---------|-------|
| P2-1 | closed | 0.95 | Closed. The same mutant (`_base` `raise OSError(...)` replaced by `return "refs/heads/main"`), on a `git archive` scratch copy of `52a59aab` (worktree untouched), is now killed: `1 failed, 28 passed`, the failure `test_ac4_a_bad_setting_fails_the_docs_only_verify_closed` at line 157 (`docs_only_change` not None). Unmutated copy: `29 passed`. The test uses a real repo (docs-only branch), asserts the unset case passes first (control), then `docs_only_change` is None and `record_confirms_pass` is False under `a..b`. | `.claude/hooks/tests/test_t370_default_branch.py` |
| P3-1 | P3 | 0.9 | Still open, accepted by the Supervisor: `review_in_scope` on `master` / bad setting is untested (round 1 mutant `name = "main"` still survives; not re-run). | `.claude/hooks/pre_bash_block_unsafe_merge.py` |
| P3-2 | P3 | 0.8 | Still open, accepted: stale `main` in docstrings. | `verify_record.py`, the gate |
| P3-3 | P3 | 0.6 | Still open, accepted: names git rejects but the check accepts fail as a missing ref. | `auto_mode.default_branch` |
| P3-4 | P3 | 0.5 | Minor: the last assertion of the new test (`shell_suites_changed(...) == []`) holds for any doubt, so it does not tell a fail-closed `[]` from an empty change; harmless, the branch changes no `.sh` file. | same test file |

### Whole-diff re-check

The new commit changes only that test file (+29 lines) and the review file; no production code changed since `36a1a807`, so round 1's security and negative-case results stand. Test helper `docs_only_repo` builds its repo under `tmp_path`, no shared state.

### Evidence (round 2)

| Check | Result | Output |
|-------|--------|--------|
| Verification Command, in the worktree at `52a59aab` | pass | `681 passed in 118.66s (0:01:58)` (680 + the new test) |
| P2-1 mutation, scratch copy | killed | `1 failed, 28 passed` (unmutated: `29 passed`) |
