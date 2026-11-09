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

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours)>

-->

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass / ☐ fail | New: `.claude/hooks/tests/test_admin_repo_allowlist.py` (319 tests: AC 1 allowlist constant + 21 allowed keys × merge/push + value checks for `remote.<name>.url`, `push.default`, `pull.rebase`; AC 2 64 planted keys × merge/push incl. every T284 key, mixed case, key set twice, newline in a value, per-worktree config, global config unread, unreadable config; AC 3 all 28 git hook names + 3 other names, non-executable/`.sample`, symlinked file and directory, `core.hooksPath`, unreadable dir; AC 4 8 bad lines × worktree/subdir/info, 9 harmless lines, unreadable file; AC 5 10 chained reads × 3 shapes, `cd` and lone merge/push allowed; AC 6 driver scenario through the gate and through `_main_push_refusal`; AC 7 tracks.md text; SC 4/5 regression and real bash/zsh run). Repointed: `.claude/hooks/tests/test_admin_tag.py` (2 parametrize lists, commented), `.claude/hooks/tests/test_merge_gate_guard.py` (AC 8 tuple). **Red against the prior content** (new test file + new `test_merge_gate_guard.py` copied into a throwaway worktree at `bc5ccc34`): `199 failed, 140 passed in 28.86s` — red in every AC group (`test_ac1_the_allowlist_is_one_constant…` 1, `test_ac2_a_planted_key…` 92, `test_ac3_any_executable_hook_file_blocks` 22, `test_ac4_an_attributes_line…` 24, `test_ac5_a_read_only_git_command…` 30, `test_ac6_…` 2, `test_ac7_…` 3, `test_sc5_with_the_gate…` 2, `test_the_allowlist_names_the_tasks…` 1); the 140 that pass at base are the allowed-key controls and the keys/hooks T284 already refused. At HEAD `74ec6995`: `319 passed` |
| Verification command run | ☑ pass / ☐ fail | HEAD `74ec6995`. `python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or t284 or t210"` → `993 passed, 1747 deselected in 44.26s`. Pin-test pre-flight (`test_admin_tag.py`, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, `test_agent_guide_dedup.py`, `test_vital_slice.py`, `test_memory_channel_and_budget.py`, `tests/test_tracks.py`, `tests/test_site_content.py`, `tests/test_site_story.py`, `tests/test_site_visual_first.py`) → `675 passed in 15.70s`. Pin hits handled: `test_admin_tag.py::test_r3_n1_read_only_segments_stay_allowed` narrowed to `cd` (status/log now refused, AC 5); `test_r3_n4_harmless_values_of_those_keys_stay_allowed` repointed to allowlisted keys (`core.fsmonitor=false`, `credential.helper=store`, `alias.st` now refused, AC 2); `test_merge_gate_guard.py` tuple gains `T295` (AC 8, Supervisor sign-off). No test pins `ADMIN_DENY_CONFIG`, `ADMIN_HOOKS` or the old message text (`git grep`) |
| Negative cases hold | ☑ pass / ☐ fail | Mutation controls (script `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/mutate.sh`, run at `adb9d524`; each changes bytes in `.claude/hooks/pre_bash_block_unsafe_merge.py`, prints the diff, runs, restores with `git checkout`; worktree clean after). **M1 (SC 6)** `-        if shape not in ADMIN_ALLOWED_CONFIG:` / `+        if not True:  # MUTATION` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac2_a_planted_key`: `128 failed`. **M2 (SC 7)** `+    ("merge", True, "driver"): "MUTATION",` — `1 file changed, 1 insertion(+)` → `7 failed, 3 passed` (allowlist-constant test, `merge.evil.driver` merge/push, AC 6 ×2, SC 5 gated ×2). **M3 hook rule** `+ and os.access(entry.path, os.X_OK) and False):` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac3`: `33 failed, 6 passed`. **M4 attributes** `+ADMIN_ATTRIBUTE_PATTERN = re.compile(r"(?!)")` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac4`: `25 failed, 10 passed`. **M5 chain** `+ADMIN_READ_ONLY_GIT = frozenset({"status", "log", "diff", "show", "rev-parse"})` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac5`: `31 failed, 5 passed`. **M6 main push** removed `repo_refusal = _admin_repo_refusal(where)` / `if repo_refusal:` / `return repo_refusal` from `_main_push_refusal` — `1 file changed, 1 insertion(+), 4 deletions(-)` → `-k test_ac6_main_push_refusal`: `1 failed, 1 passed`. **M7 URL value** `+        return True  # MUTATION` — `1 file changed, 1 insertion(+), 1 deletion(-)` → `-k test_ac1_a_remote_url`: `4 failed`. All restored; `319 passed` after |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass / ☐ fail | Affected set: the `[admin]` branch of `.claude/hooks/pre_bash_block_unsafe_merge.py` (`ADMIN_ALLOWED_CONFIG`, `_config_key_shape`, `_config_value_ok`, `_admin_config_refusal`, `_admin_hooks_refusal`, `_admin_attributes_refusal`, `_admin_repo_refusal`, `_main_push_refusal`, `ADMIN_READ_ONLY_GIT`, the chain message), only reached when the request carries `[admin]`; its tests (`-k "admin or merge_gate or t284 or t210"`); the doc `docs/claude-md/tracks.md` `### Admin tag`. Stale-text grep (LR-0005): `ADMIN_DENY_CONFIG`, `ADMIN_HOOKS`, "deny lists in item 2", "rev-parse` and `cd", "post-index-change", "other git write" over the repo — the only hits left are history (`tasks/TASK_REVIEW_T284.md`, the gate's round-3 comment, `tasks/GATE_HUNT_2026-11-08.md`); the chain comment and message were fixed in `74ec6995`. `AGENTS.md`, `README.md`, `site/docs.html` name `[admin]` only at the level of "merge and push after a passed verify", which stays true. Not re-reviewed: the non-admin merge gate paths (unchanged lines). `code-review` and `security-review` skills: not run by the implementing agent (no `Skill` tool in this spawn) — the Supervisor's Stage 4 step |
| Full smoke suite still green (no regression) | ☑ pass / ☐ fail | `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` at `adb9d524`: `4700 passed, 25 subtests passed in 318.81s (0:05:18)`; re-run at the final HEAD: FULL_SUITE_FINAL |
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

**DELTA**: An `[admin]` merge or push in a repository with a planted merge driver, filter, textconv,
external diff, editor, credential helper, proxy or executable hook is now refused before git runs it,
instead of being allowed while the planted program runs.

**WITNESS**: Implementing agent (common-infrastructure, T295 resume), recorded in
`memory/event-trace/T295.jsonl` of the main checkout: BEFORE re-capture at line 82
(`2026-11-09T02:15:36Z`), AFTER at line 96 (`2026-11-09T02:22:56Z`); `scripts/verify_trace.py T295` →
`INTACT: lines 1-97 chained and anchored`. The independent witness is the hook's auto verify run
(pending: the Supervisor starts it with `python3 .claude/hooks/stop_auto_verify.py --start T295`).
