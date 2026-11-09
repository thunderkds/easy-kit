# TASK_REVIEW — T295: `[admin]` merge and push refuse repo config and hooks that can run code (allowlist)

> Sibling of `tasks/TASK_GUIDE_T295.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` or `[admin]` tag; with `[admin]`, the `Not done:` line names `merge (admin: after the auto verify pass)`,
`docs/claude-md/tracks.md` `## Auto mode`). To use it, copy the block below out of this comment, to this
place, and replace every <...>. Keep `Mode: auto` as its first line, exactly as written: T182's hook reads
it. Write it to this file before the run ends; the chat message is a copy, not the report. The same
block is the Supervisor's final chat message. It is not the `delivery-report` page and not
Evidence. A taste decision (what the user wants) also ends with the flag. Write `DEBATED` only when ≥2
Advocate `Agent` calls ran for that question, naming each Advocate's option. A decision with no Advocates is
labelled `RULE`, `FACT` or `SAFER OPTION`, never `DEBATED`. A decision flagged `⚠ decided for you` is a choice, and is never labelled `FACT`. A
safety action a rule requires (for example the backup before a delete) is `RULE` without the flag.
At Risk Medium or High, a `RULE:` counts only when it names a written rule (`path:line`,
`path § <heading>`, or `docs/claude-md/tracks.md` `### <section>`), and a `FACT:` needs a Citation
(`path:line "quoted text"`); without one it is a choice and must be `DEBATED`. Good: `2. backed up the CSV
— RULE: `docs/claude-md/tracks.md` `### Stops that stay``. Bad: `1. kept recurring.csv — RULE: Surgical Changes`.
`Memory:` records the diff-driven memory pass you run before you stop: each entry written, or `nothing new`.
After an auto verify pass the hook, never you, adds `Closed: row moved to Done <date> — …` and moves the row,
or adds `Paused: done not moved — <reason>`. It moves the row only when this block holds `Mode: auto`, a
numbered decision, `Checks:`, `Memory:`, the `Not done:` auto verify slot with its result, and `Not done:`
naming the merge — no `<...>` left (`docs/claude-md/tracks.md` `### Auto close-out`).

-->

## Auto decisions

Mode: auto
1. The allowlist stays wider than the guide's start list: `remote.<name>.url` and `.fetch` for any remote name, `core.symlinks`, `branch.<b>.vscode-merge-base`, `pull.rebase` (true or false), `push.default` (simple or current), `extensions.worktreeConfig`; and the `ADMIN_HOOKS` name list is replaced by a refusal that names the executable hook file found — DEBATED: keep the widenings and add the small checks the Advocates named: a boolean value check for `core.symlinks` and `extensions.worktreeConfig`, a test that fails when the origin-only push rule (`.claude/hooks/pre_bash_block_unsafe_merge.py:1393` `if positionals[0] != ADMIN_REMOTE:`) goes, and a real check of a push with several `remote.origin.url` entries (Advocate 1: keep all, because the guide allows an added key with a reason and a test (`tasks/TASK_GUIDE_T295.md:59`) and a narrower list refuses real two-remote repos; Advocate 2: keep all and add a boolean value check on `core.symlinks` and `extensions.worktreeConfig`; Advocate 3: keep all as the smallest safe thing, add a test on a repo shaped like this one, escape the hook file name in refusal text, and check several `remote.origin.url` entries) ⚠ decided for you — please review
2. The code review and the security review must report before the task is marked ready — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4 ("Skill({ skill: "code-review" }) always; security-review for Medium/High risk")
Paused: none. The disk filled on 2026-11-09 and was freed; the full suite then ran green (4744 passed at `c02693c0`).
3. Second independent review (read-only, fresh agent): no P0, no hang. One P1 fixed: a second `remote.<n>.url` set in user-global or system config was not counted (new test `test_f2a_a_global_url_for_the_same_remote_blocks`, red on the old code, 364 passed in the T295 file). P2 false refusals (built-in `diff=`/`merge=` drivers, ignored-directory `.gitattributes`, ordinary local keys, `file://localhost/`, `%` in a path, any executable hook) are fail-closed and kept; now written under the Admin tag limits in `docs/claude-md/tracks.md`. Test gaps the reviewer named (the `%` refusal, the `@-` helper branch, a dangling `.gitattributes` symlink, the `.git` suffix candidates, a hooks subdirectory, the `.git` prune) are not added: they cover refusal paths that already fail closed — decided for you — please review
Checks: tests (implementer) `python3 -m pytest .claude/hooks/tests/test_admin_repo_allowlist.py` — 363 passed at `66facc10` (29 failed and 16 passed on the old code); verification command `-k "admin or merge_gate or t284 or t210"` — 1036 passed, 1 failed before the commit (the test that counts an uncommitted gate change as unauthorised; it passes after the commit); pin pre-flight 677 passed; 29 mutation controls red; full suite — 4744 passed, 25 subtests at `c02693c0` (before the review-P1 fix; the changed gate files re-run below); reviews code-review — block, fixed; security-review — 3 items fixed; second independent review — one P1 fixed (decision 3); real push witness — not run (auto-checked, not /verify)
Memory: nothing new for T295 — the learning for T294 and T296 already covers this
Not done: the P2 test gaps listed in Auto decision 3 (refusal paths that already fail closed); real push witness for the fix-round shapes (multi-url, local path with an executable hook, `updateInstead`): run by the user outside an `[auto]` session; merge (yours); auto verify: ☐ not run yet; do not merge T295 without T296 (`--attr-source`)
Paused: done not moved — Gate 5: the tests row is not `☑ pass` with pasted output; report incomplete: auto verify slot

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | New: `.claude/hooks/tests/test_admin_repo_allowlist.py` (319 tests: AC 1 allowlist constant + 21 allowed keys × merge/push + value checks for `remote.NAME.url`, `push.default`, `pull.rebase`; AC 2 64 planted keys × merge/push incl. every T284 key, mixed case, key set twice, newline in a value, per-worktree config, global config unread, unreadable config; AC 3 all 28 git hook names + 3 other names, non-executable/`.sample`, symlinked file and directory, `core.hooksPath`, unreadable dir; AC 4 8 bad lines × worktree/subdir/info, 9 harmless lines, unreadable file; AC 5 10 chained reads × 3 shapes, `cd` and lone merge/push allowed; AC 6 driver scenario through the gate and through `_main_push_refusal`; AC 7 tracks.md text; SC 4/5 regression and real bash/zsh run). Repointed: `.claude/hooks/tests/test_admin_tag.py` (2 parametrize lists, commented), `.claude/hooks/tests/test_merge_gate_guard.py` (AC 8 tuple). **Red against the prior content** (new test file + new `test_merge_gate_guard.py` copied into a throwaway worktree at `bc5ccc34`): `199 failed, 140 passed in 28.86s` — red in every AC group (`test_ac1_the_allowlist_is_one_constant…` 1, `test_ac2_a_planted_key…` 92, `test_ac3_any_executable_hook_file_blocks` 22, `test_ac4_an_attributes_line…` 24, `test_ac5_a_read_only_git_command…` 30, `test_ac6_…` 2, `test_ac7_…` 3, `test_sc5_with_the_gate…` 2, `test_the_allowlist_names_the_tasks…` 1); the 140 that pass at base are the allowed-key controls and the keys/hooks T284 already refused. At HEAD `74ec6995`: `319 passed`. **Fix round (Stage 4, 2026-11-09)**: 44 more tests in the same file (363 now): F2a second `url` (origin, upstream; push and merge); F2b local push target with an executable `post-receive`/`pre-receive`/`update`/`push-to-checkout`, a `file://` URL, the target's `core.hooksPath`, a relative URL from a subdirectory (resolved from the worktree top), `updateInstead`, `.git/remotes/` and `.git/branches/`, and 3 network-URL controls; F3 12 attributes forms, each first read by git itself with `git check-attr merge filter diff` (read-only) and then asked of the gate, plus the `[attr]` macro rule; F4 a FIFO `.gitattributes` (worktree, `info/attributes`, behind a symlink) under a 10 s alarm that raises a `BaseException`, and the walk deadline; F5 the unreadable-config test now stubs only `git config --list` (3 cases: no answer, returncode 128, odd field count), an attributes file over 1 MB, an unreadable directory in the walk, an attributes file that cannot be opened; F6a boolean values (gate refusal plus a direct `_config_value_ok` call: git itself dies on a bad boolean first); F6b a push to a configured `upstream` and a bare push with `branch.B.remote=upstream`; F6c a repo shaped like the project's (`remote.github` + `remote.origin`, `branch.main.remote=github`, `pull.rebase=true`, `vscode-merge-base` twice) keeps its push and merge; F6d a hook name, a config key and an attributes path are escaped and cut to 120 characters. **Red on the code before the fix** (`03eaa260`, the same code as `a272e6b5`), `-k "f2 or f3 or f4 or f5 or f6 or unreadable_config"`: `29 failed, 16 passed, 318 deselected in 44.07s`; the FIFO case failed by hanging (`test_admin_repo_allowlist.Hang: the gate hung on the FIFO`, raised in `_admin_attributes_refusal` at the `open()`, line 1529). The 16 that pass at the old code are coverage and no-false-positive controls (unreadable config ×3, network URL ×3, the harmless attributes forms ×4, the macro test, F5 ×3, F6b, F6c); each is proved able to fail by a mutation control below. Green at `66facc10`: `363 passed in 99.72s`; after the second review's P1 fix: `python3 -m pytest .claude/hooks/tests/test_admin_repo_allowlist.py -q -p no:cacheprovider` → `364 passed in 73.38s`; the new test `test_f2a_a_global_url_for_the_same_remote_blocks` fails on the old code (`1 failed`) |
| Verification command run | ☑ pass / ☐ fail | **Fix round**: `-k "admin or merge_gate or t284 or t210"` → `1 failed, 1036 passed, 1747 deselected in 147.20s`; the one failure was `test_stop_auto_mode_check.py::test_merge_gate_is_untouched`, which counts an uncommitted gate change as unauthorised (it passed at HEAD before the change); after commit `66facc10`: `1 passed`. Pin-test pre-flight rerun after the tracks.md edit (the 11 files below) → `677 passed, 361 deselected in 43.05s`. Earlier, at HEAD `74ec6995`: `python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or t284 or t210"` → `993 passed, 1747 deselected in 44.26s`. Pin-test pre-flight (`test_admin_tag.py`, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, `test_agent_guide_dedup.py`, `test_vital_slice.py`, `test_memory_channel_and_budget.py`, `tests/test_tracks.py`, `tests/test_site_content.py`, `tests/test_site_story.py`, `tests/test_site_visual_first.py`) → `675 passed in 15.70s`. Pin hits handled: `test_admin_tag.py::test_r3_n1_read_only_segments_stay_allowed` narrowed to `cd` (status/log now refused, AC 5); `test_r3_n4_harmless_values_of_those_keys_stay_allowed` repointed to allowlisted keys (`core.fsmonitor=false`, `credential.helper=store`, `alias.st` now refused, AC 2); `test_merge_gate_guard.py` tuple gains `T295` (AC 8, Supervisor sign-off). No test pins `ADMIN_DENY_CONFIG`, `ADMIN_HOOKS` or the old message text (`git grep`) |
| Negative cases hold | ☑ pass / ☐ fail | **Fix round** (script `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/mutate_fix_round.py`, output `mutate_fix_round.out` in the same folder; each control changes bytes in `.claude/hooks/pre_bash_block_unsafe_merge.py`, prints `git diff --stat`, runs, restores with `git checkout --`; worktree clean after: `?? tasks/HANDOFF_T295_fix_round.md` only). Every stat is `1 file changed, 1 insertion(+), 1 deletion(-)` unless named. **N1 F2a** `> 1` → `> 99` → `2 failed`. **N2 F2b target hooks** `refusal = None` → `7 failed`. **N3 updateInstead** `if False:` → `1 failed`. **N4 relative URL** joined to `where` (the cwd) instead of the worktree top → `1 failed`. **N5 legacy remotes/branches** `if False:` → `2 failed`. **N6 F3 quote** `[ \t\r"]` → `[ \t\r]` → `4 failed, 8 passed`. **N7 F3 lstrip** → `decode().strip()` → `2 failed, 10 passed`. **N8 F3 split** `\x0b` made a line end → `3 failed, 9 passed`. **N9 F3 `[attr]` macro** → `False` → `1 failed` (a first try whose comment hid a `)` gave `1 error` and does not count; redone). **N10 F4** lstat and fstat checks both `if False:` (`2 insertions(+), 2 deletions(-)`) → `3 failed` (one alone is covered by the other). **N11 walk deadline** → `1 failed`. **N12 F6a boolean** `return True` → `2 failed`. **N13 F6b origin-only rule** removed (`1 insertion(+), 2 deletions(-)`) → `1 failed`. **N14 F6d escape** `safe = text` → `3 failed`. **N15 F6d cut** `return safe` → `2 failed`. F5 `return "cannot read…"` branches: **C1** config read failed → `return None` → `2 failed, 1 passed`; **C2** odd field count → `1 failed, 2 passed`; **C3** hooks directory → `1 failed`; **C4** walk error → `1 failed`; **C5** file open error → `return b""` → `1 failed`; **C6** over 1 MB `if False:` → `1 failed`. Rerun of the first round's controls on the new code: **M1** `128 failed`; **M2** (`1 insertion(+)`) `-k "test_ac1_the_allowlist or test_ac6"` → `3 failed, 1 passed`; **M3** `33 failed, 6 passed`; **M4** `22 failed, 13 passed` (3 `[attr]` lines now also caught by the macro rule); **M5 repointed at `if git_commands != 1:`** → `< 1` → `31 failed, 5 passed`; **M6** (`1 insertion(+), 4 deletions(-)`) `1 failed, 1 passed`; **M7** `4 failed`. All restored. First round: Mutation controls (script `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/mutate.sh`, run at `adb9d524`; each changes bytes in `.claude/hooks/pre_bash_block_unsafe_merge.py`, prints the diff, runs, restores with `git checkout`; worktree clean after). **M1 (SC 6)** `-        if shape not in ADMIN_ALLOWED_CONFIG:` / `+        if not True:  # MUTATION` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac2_a_planted_key`: `128 failed`. **M2 (SC 7)** `+    ("merge", True, "driver"): "MUTATION",` — `1 file changed, 1 insertion(+)` → `7 failed, 3 passed` (allowlist-constant test, `merge.evil.driver` merge/push, AC 6 ×2, SC 5 gated ×2). **M3 hook rule** `+ and os.access(entry.path, os.X_OK) and False):` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac3`: `33 failed, 6 passed`. **M4 attributes** `+ADMIN_ATTRIBUTE_PATTERN = re.compile(r"(?!)")` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac4`: `25 failed, 10 passed`. **M5 chain** `+ADMIN_READ_ONLY_GIT = frozenset({"status", "log", "diff", "show", "rev-parse"})` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac5`: `31 failed, 5 passed`. **M6 main push** removed `repo_refusal = _admin_repo_refusal(where)` / `if repo_refusal:` / `return repo_refusal` from `_main_push_refusal` — `1 file changed, 1 insertion(+), 4 deletions(-)` → `-k test_ac6_main_push_refusal`: `1 failed, 1 passed`. **M7 URL value** `+        return True  # MUTATION` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac1_a_remote_url`: `4 failed`. All restored; `319 passed` after |
| verify | ☑ pass | auto-run by hook, session 5b5d79af-2ec1-4b7b-a1f9-ed5ae9ab23c6, commit 739c4d1933d51006849aaf8f6d656be1b108aab8, log .claude/verify-runs/T295-739c4d1933d5.log — pass; done not moved: Gate 5: the tests row is not `☑ pass` with pasted output |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass / ☐ fail | Affected set: the `[admin]` branch of `.claude/hooks/pre_bash_block_unsafe_merge.py` (`ADMIN_ALLOWED_CONFIG`, `_config_key_shape`, `_config_value_ok`, `_admin_config_refusal`, `_admin_hooks_refusal`, `_admin_attributes_refusal`, `_admin_repo_refusal`, `_main_push_refusal`, `ADMIN_READ_ONLY_GIT`, the chain message), only reached when the request carries `[admin]`; its tests (`-k "admin or merge_gate or t284 or t210"`); the doc `docs/claude-md/tracks.md` `### Admin tag`. Stale-text grep (LR-0005): `ADMIN_DENY_CONFIG`, `ADMIN_HOOKS`, "deny lists in item 2", "rev-parse` and `cd", "post-index-change", "other git write" over the repo — the only hits left are history (`tasks/TASK_REVIEW_T284.md`, the gate's round-3 comment, `tasks/GATE_HUNT_2026-11-08.md`); the chain comment and message were fixed in `74ec6995`. `AGENTS.md`, `README.md`, `site/docs.html` name `[admin]` only at the level of "merge and push after a passed verify", which stays true. Not re-reviewed: the non-admin merge gate paths (unchanged lines). `code-review` and `security-review` skills: not run by the implementing agent (no `Skill` tool in this spawn) — the Supervisor's Stage 4 step. **Fix round** affected set: `_shown`, `_config_value_ok`, `_admin_config_refusal`, `_admin_hooks_refusal(hooks, whose)`, `_attributes_bytes`, `_sets_a_driver`, `_admin_attributes_refusal`, `_admin_repo_refusal`, `_local_push_path`, `_admin_push_target_refusal`, the push branch and the `git_commands` count of `admin_refusal`, the comment of `_main_push_refusal`, the module docstring; `docs/claude-md/tracks.md` item 2 and Known limits. Stale-text grep (LR-0005) for `ADMIN_READ_ONLY_GIT`, "this hook does not read git config", "checked below for helper and option forms", "repository's hooks directory": no hit left outside this file's history. The tracks.md line "checks that its push URL equals its fetch URL" is still true. Not touched: `GIT_OPTIONS_WITH_ARG` / `GIT_OPTION_ARGS` (T296) |
| Full smoke suite still green (no regression) | ☑ pass / ☐ fail | **Fix round** at `c02693c0`: `4744 passed, 25 subtests passed in 696.77s (0:11:36)` (2026-11-09; a first run with `-x` stopped at one `test_auto_verify_skip_pass.py` case that passes alone, 222 passed, and passed in this unstopped run). Earlier: `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` at `adb9d524`: `4700 passed, 25 subtests passed in 318.81s (0:05:18)`; re-run at `81a01ca0` (after the message fix and this file): `4700 passed, 25 subtests passed in 348.08s (0:05:48)` |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☑ N/A | Not run: neither companion tool was run for this task by the implementing agent |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☑ N/A | No UI component: the task changes a Python hook, its tests and one doctrine doc |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☑ N/A | No UI component: no page, style or site file changes |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☑ N/A | No UI component: nothing renders at a viewport |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T15:21Z at HEAD `bc5ccc34`, before any implementation commit; throwaway repo and `[admin]` request driven through the gate's real `main()`, then the command run for real; repro script `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/9e7b73f3-3c09-4250-86c1-dac31ab338c5/scratchpad/t295/repro_driver.py`; plant: `git config merge.evil.driver <script>` plus `.git/info/attributes` `* merge=evil`, command `git merge feat/t900-x`):

```
[2026-11-08T15:21:14Z] bash gated=False GATE: ALLOWED
[2026-11-08T15:21:14Z] ran in bash: rc=0
[2026-11-08T15:21:14Z] marker exists=True merge driver ran as code
[2026-11-08T15:21:15Z] zsh gated=False GATE: ALLOWED
[2026-11-08T15:21:15Z] ran in zsh: rc=0
[2026-11-08T15:21:15Z] marker exists=True merge driver ran as code
[2026-11-08T15:21:15Z] bash gated=True GATE: ALLOWED
[2026-11-08T15:21:15Z] ran in bash: rc=0
[2026-11-08T15:21:15Z] marker exists=True merge driver ran as code
[2026-11-08T15:21:15Z] zsh gated=True GATE: ALLOWED
[2026-11-08T15:21:15Z] ran in zsh: rc=0
[2026-11-08T15:21:15Z] marker exists=True merge driver ran as code
```

The gate says ALLOWED, so the merge runs and the planted driver writes its marker file.

Re-capture on resume (the first repro script was lost with its scratchpad). The pre-change gate ran from a
throwaway `git worktree add --detach <scratchpad>/base bc5ccc34` (removed after; `main` not touched).
The same plant and command, through the gate's real `main()` via the `gate` fixture. The repro script is
`/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/repro/repro_t295.py`,
run as `GATE_TESTS=<checkout>/.claude/hooks/tests python3 -m pytest repro_t295.py -s -q -p no:cacheprovider`.
`gated=False` is the control: it runs the command whatever the gate says.

```
[2026-11-09T02:15:35Z] bash gated=False GATE: ALLOWED
[2026-11-09T02:15:35Z] ran in bash: rc=0
[2026-11-09T02:15:35Z] marker exists=True merge driver ran as code
[2026-11-09T02:15:35Z] zsh gated=False GATE: ALLOWED
[2026-11-09T02:15:35Z] ran in zsh: rc=0
[2026-11-09T02:15:35Z] marker exists=True merge driver ran as code
[2026-11-09T02:15:35Z] bash gated=True GATE: ALLOWED
[2026-11-09T02:15:35Z] ran in bash: rc=0
[2026-11-09T02:15:35Z] marker exists=True merge driver ran as code
[2026-11-09T02:15:35Z] zsh gated=True GATE: ALLOWED
[2026-11-09T02:15:35Z] ran in zsh: rc=0
[2026-11-09T02:15:35Z] marker exists=True merge driver ran as code
4 passed in 0.35s
```

**AFTER** (captured 2026-11-09T02:22:55Z at HEAD `74ec6995`, the same script and plant against the
T295 gate; the refusal's newlines are shown as ` | `):

```
[2026-11-09T02:22:55Z] bash gated=False GATE: BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: |   • `[admin]` does not allow this command: repo config `merge.evil.driver` is not on the `[admin]` allowlist: it can run a command or send git elsewhere, so `[admin]` refuses | With `[auto]`, merge and push stay the user's. `[admin]` allows only a merge or a plain push of the request's own task branch (or of `main` after that merge), after its auto verify passed (docs/claude-md/tracks.md `### Admin tag`).
[2026-11-09T02:22:55Z] ran in bash: rc=0
[2026-11-09T02:22:55Z] marker exists=True merge driver ran as code
[2026-11-09T02:22:55Z] zsh gated=False GATE: BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: |   • `[admin]` does not allow this command: repo config `merge.evil.driver` is not on the `[admin]` allowlist: it can run a command or send git elsewhere, so `[admin]` refuses | With `[auto]`, merge and push stay the user's. `[admin]` allows only a merge or a plain push of the request's own task branch (or of `main` after that merge), after its auto verify passed (docs/claude-md/tracks.md `### Admin tag`).
[2026-11-09T02:22:55Z] ran in zsh: rc=0
[2026-11-09T02:22:55Z] marker exists=True merge driver ran as code
[2026-11-09T02:22:55Z] bash gated=True GATE: BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: |   • `[admin]` does not allow this command: repo config `merge.evil.driver` is not on the `[admin]` allowlist: it can run a command or send git elsewhere, so `[admin]` refuses | With `[auto]`, merge and push stay the user's. `[admin]` allows only a merge or a plain push of the request's own task branch (or of `main` after that merge), after its auto verify passed (docs/claude-md/tracks.md `### Admin tag`).
[2026-11-09T02:22:55Z] not run in bash: the gate refused
[2026-11-09T02:22:55Z] marker exists=False driver did not run
[2026-11-09T02:22:55Z] zsh gated=True GATE: BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: |   • `[admin]` does not allow this command: repo config `merge.evil.driver` is not on the `[admin]` allowlist: it can run a command or send git elsewhere, so `[admin]` refuses | With `[auto]`, merge and push stay the user's. `[admin]` allows only a merge or a plain push of the request's own task branch (or of `main` after that merge), after its auto verify passed (docs/claude-md/tracks.md `### Admin tag`).
[2026-11-09T02:22:55Z] not run in zsh: the gate refused
[2026-11-09T02:22:55Z] marker exists=False driver did not run
4 passed in 0.25s
```

The control still runs the driver (the plant works). With the gate, the merge is refused by name and the
driver's marker file is absent, in bash and in zsh.

**AFTER, fix round** (captured 2026-11-09T05:48:14Z at `c02693c0`; the gate is only asked, through the `gate`
fixture's `reason()`, which passes the command text to the hook and runs nothing; script
`/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/after/after_fixround.py`, run as
`GATE_TESTS=<worktree>/.claude/hooks/tests python3 -m pytest after_fixround.py -s -q -p no:cacheprovider`; the fixture
path is shown as `<fx>`):

```
[2026-11-09T05:48:14Z] multi-url (control, before the plant): ALLOWED
[2026-11-09T05:48:14Z] local-hook (control, before the plant): ALLOWED
[2026-11-09T05:48:14Z] updateInstead (control, before the plant): ALLOWED
[2026-11-09T05:48:14Z] quoted-pattern (control, before the plant): ALLOWED
[2026-11-09T05:48:14Z] nbsp (control, before the plant): ALLOWED
[2026-11-09T05:48:14Z] fifo (control, before the plant): ALLOWED
[2026-11-09T05:48:03Z] multi-url: BLOCKED: • `[admin]` does not allow this command: repo config `remote.origin.url` is set more than once: a push to that remote would go to every URL
[2026-11-09T05:48:03Z] local-hook: BLOCKED: • `[admin]` does not allow this command: the push target of origin has an executable `post-receive` hook, which this merge or push could run
[2026-11-09T05:48:04Z] updateInstead: BLOCKED: • `[admin]` does not allow this command: the push target of origin sets `receive.denyCurrentBranch=updateInstead`: the push would check out files there, with that repository's own filters
[2026-11-09T05:48:04Z] quoted-pattern: BLOCKED: • `[admin]` does not allow this command: the attributes file <fx>/main/.gitattributes sets `merge=`, `filter=` or `diff=`, which can run a driver or filter during this merge or push
[2026-11-09T05:48:04Z] nbsp: BLOCKED: • `[admin]` does not allow this command: the attributes file <fx>/main/.gitattributes sets `merge=`, `filter=` or `diff=`, which can run a driver or filter during this merge or push
[2026-11-09T05:48:04Z] fifo: BLOCKED: • `[admin]` does not allow this command: the attributes file <fx>/main/.gitattributes is not a regular file
6 passed in 0.91s
```

The blocked lines are from the first run (05:48:03Z); the control lines are from a second run of the same script
(05:48:14Z), because pytest's progress dot hid five of them in the first one. Before the fix, the same six shapes were
allowed or hung (the red run in Evidence). No real push or merge was run for this capture.

**DELTA**: An `[admin]` merge or push in a repository with a planted merge driver, filter, textconv,
external diff, editor, credential helper, proxy or executable hook is now refused before git runs it,
instead of being allowed while the planted program runs.

**WITNESS**: Implementing agent (common-infrastructure, T295 resume), recorded in
`memory/event-trace/T295.jsonl` of the main checkout: BEFORE re-capture at line 82
(`2026-11-09T02:15:36Z`), AFTER at line 96 (`2026-11-09T02:22:56Z`); `scripts/verify_trace.py T295` →
`INTACT: lines 1-97 chained and anchored`. The independent witness is the hook's auto verify run
(pending: the Supervisor starts it with `python3 .claude/hooks/stop_auto_verify.py --start T295`).

---

## Fix round (Stage 4, 2026-11-09)

Supervisor decision for this round: code and gate-only tests; no real `git push`, `git merge` or `git pull` by an agent,
and no lab script of real pushes. Every new shape is proved by the gate's verdict and by read-only git facts
(`git check-attr`, `git config`, `git rev-parse --git-path hooks`, `os.mkfifo`/`os.lstat`).

Not done: the P2 test gaps listed in Auto decision 3 (refusal paths that already fail closed); real push witness for the fix-round shapes (multi-url, local path with an executable hook, `updateInstead`): run by the user outside an `[auto]` session; merge (yours); auto verify: ☐ not run yet; do not merge T295 without T296 (`--attr-source`)

Documented limits (in `docs/claude-md/tracks.md` `### Admin tag`, Known limits): the incoming branch's `.gitattributes`
is not scanned; a local-path `origin` can still run work the gate does not stop (its own `git gc --auto`); a network
`origin` is not read; `git --attr-source <tree> merge …` skips the gate until T296 lands (do not merge T295 alone).
Seen and left alone (outside this task): from a subdirectory of a worktree, the gate's guide lookup
(`_guides_added_since`, `git log -- tasks/`) is relative to the cwd and finds no guide, so a request that does not name
its task is refused there.
