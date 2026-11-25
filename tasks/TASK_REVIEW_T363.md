# TASK_REVIEW — T363: The sensitive-path hook asks when a destructive command targets a folder that holds a sensitive path

> Sibling of `tasks/TASK_GUIDE_T363.md`. Filled by the independent reviewer (qa-expert), Stage 4.
> Commit reviewed: `ccc8d91e8215a4e066f25af1960e743b87c0fc95` (diff `main...ccc8d91e`).

## Review verdict

**FAIL (two P2 fail-open holes in the hook, plus over-asks).** AC 1 to 5 hold as the guide words them, and the Verification Command is green. But the change adds two ways for the hook to stay silent or hang where it must ask (unchecked walk error at the end of a walk; brace-expansion blow-up that times out), and it adds new asks on ordinary read-only commands.

Findings (confidence >= 75; every one was reproduced with the real hook in a scratch project, none edited in the worktree):

| # | Sev | File:line | Finding | One-line fix |
|---|-----|-----------|---------|--------------|
| 1 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:327` | Fail-open by timeout. `expand_braces` is exponential and now runs on every Bash token: `ls {a,b}` x16 takes 3.7 s, x20 takes 59.7 s, x22 and x24 hit the 60 s timeout (no ask came back). A hook that times out lets the call run. A command that never gets the ask is the failure mode (c). | Cap the expansion (for example 1000 results, via a counting generator or a product-size pre-check); on exceeding it, return a hit or raise so `main` asks. |
| 2 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:501-513` | Fail-open on an unreadable folder. `if errors:` runs only after a yielded folder's files, so an unreadable folder that is the last (or only) one `os.walk` reaches never triggers it: `rm -rf ro` with `ro/sub` at mode 000 printed silent, and the guide says "cannot list a folder counts as a hit". Mutant "walk errors ignored" stays green, so no test pins it. | Move the check after the `for` loop too: `if errors: return (folder, "a folder that could not be read")`, and add a test with a `chmod 000` subfolder. |
| 3 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:539` | New ask on a read-only command (b). Any `find` with `-exec`/`-ok` asks when the start folder holds a sensitive path, whatever the command it runs: `find . -name '*.py' -exec grep -l x {} +` and `find . -type f -exec wc -l {} +` both ask in a kit root (`.` holds `.claude/sensitive-paths.txt`). The guide's AC 2 lists `find . -name '*.py'` only. | Ask for `-exec*`/`-ok*` only when the word after it is a destructive verb (`rm`, `mv`, `shred`, ...); keep `-delete` as is. |
| 4 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:551-553` | New ask on a non-destructive command (b). `git restore --staged .` (only the index) and `git checkout .` at a kit root ask. The first changes no file. | Skip when `--staged`/`-S` is present without `--worktree`/`-W`. `git checkout .` is a real discard: keep. |
| 5 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:564` | Silent cases the guide's header does not record (a). Verified silent for a holding `config`: a glob folder (`rm -rf conf*`, `rm -rf ./conf*`, `rm -rf *`, `rm -rf .cl*`), `bash -c "rm -rf config"`, `sh -c 'rm -rf config'` (quoted code is dropped by `strip_quoted_spans` here, while `command_tokens` keeps it), `rm -rf config>/dev/null` (the glued redirect makes one word), `timeout 5 rm -rf config`, `\rm -rf config`, `rm -rf $PWD/config`, `git -C . restore .`. Guide AC 1/2 do not name them, but "Recorded limitations" names only variables, `eval`, `python -c` and the verb list. | Add to the header limit list: globs in the folder argument, `bash -c`/`sh -c` bodies, glued redirects, `timeout`/`xargs`/`\`-prefixed verbs, `git -C`. (Or expand globs with the token rule's `glob.iglob`.) |
| 6 | P3 | `.claude/hooks/pre_tool_sensitive_path.py:546` | `mv a.txt .` asks (the destination `.` is the project root, which holds the list). Moving a file into a folder does not touch what the folder holds; `mv x.txt docs/` stays silent, so the rule is inconsistent. | For `mv`, walk the source arguments only (all but the last). |
| 7 | P3 | `.claude/hooks/pre_tool_sensitive_path.py:496-513` | Cost of the walk: capped by files (20000), not folders or arguments. Measured: 19000 files 1.12 s; 25000 files 1.19 s (asks); 5 arguments of 19000 files 5.47 s (about 1 s per argument and per segment); 60000 empty folders 0.76 s and silent. `rm -rf node_modules` over 20000 files asks by design. Bounded enough for one call; a many-argument command is not. | Share one `seen` counter across all arguments of the call, and count folders as well as files. |

No P0/P1. Also checked, no finding: symlink loops (not followed, silent 0.04 s), a file with an undecodable name (silent, no exception), `cwd` inside a subfolder (`rm -rf ../config` from `src` asks), a folder outside both roots (silent), any exception in the new code (inside `main`'s `try`, so it asks, not fails open), `git checkout main` and `git checkout -b feat` (silent).

### Security rules (`skills/code-review/references/security-reviewer.md`, hooks section)

- Input the hook did not write: the command string, `cwd` and folder names. Findings 1 and 2 are the two places where that input makes the hook skip its ask. Lower-trust actor: the model or injected text driving a Bash call; boundary: the PreToolUse hook; resource: a sensitive file; result: the call runs with no ask. Verdict: finding 1 `confirmed`, Medium (needs a contrived command, and `$VAR` names are an already recorded bypass, so it is hardening, not a new class); finding 2 `confirmed`, Low to Medium (needs an unreadable subfolder).
- Walk safety: `os.walk` does not follow symlinks, `.git` is pruned, the target is bounded to the two roots, no command runs from the folder's content. No TOCTOU effect beyond the ask itself.
- The guide's `Recorded limitations` stay honest only after finding 5 is written down.

### Mutation check of each new test (scratch copy at the scratchpad `mut/`, worktree untouched)

| Test | Code change that turns it red (verified) |
|------|------------------------------------------|
| `test_ac1_destructive_commands_on_a_holding_folder_ask` (subtests) | `folder_hits` call removed; `rm` flag test returning `[]`; `mv` branch emptied (`mv .claude old`); `find` default `["."]` dropped (`find -delete`); `GIT_FOLDER_SUBCOMMANDS` emptied (`git restore .`); `COMMAND_PREFIXES` emptied (`env rm -rf config`); `VAR=` skip removed and `os.path.basename` dropped (`FOO=1 /bin/rm -rf .claude`); `DIR_CHANGE_COMMANDS` branch off (`cd src; rm -rf ..`) |
| `test_ac1_the_ask_names_the_folder` | `folder_hits` call removed or `rm` flag test returning `[]` |
| `test_ac1_a_predicting_guide_does_not_cover_the_folder` | the same two |
| `test_ac2_reads_and_other_targets_stay_silent` | `find` no longer requires an action flag (`find . -name '*.py'` asks) |
| `test_ac2_a_folder_outside_both_roots_is_skipped` | the outside-roots `continue` removed |
| `test_ac3_a_brace_token_naming_a_sensitive_path_asks` | the `expand_braces` extension in `command_tokens` removed |
| `test_ac3_a_harmless_brace_token_stays_silent` | none of my mutants (it is a control; only an over-expansion would redden it, not mutated) |
| `test_ac4_the_walk_cap_fails_toward_asking` | `if seen > cap` made `False`; the walk returning a hit when nothing is found (control line); `folder_hits` removed |

Mutants that left the whole file green (a test gap, each is a behaviour the guide states): `rm` without the `-r` requirement (`rm config` would walk); `git` `paths[1:]` replaced by `paths`; the `os.path.isdir` check dropped; the `.git` skip dropped; walk errors ignored (finding 2); `strip_quoted_spans` dropped; the hit's `forms` taken from a wrong path. Suggested: add `rm config` (no `-r`) silent, a `chmod 000` folder asks, and a `.git`-only secret silent.

## Auto decisions

Mode: auto
1. Took T363 with option C — RULE: the user's request "T363 go with C [admin]" (the T363 Debate did not settle: `docs/claude-md/tracks.md` `### Stops that stay`)
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High row)
3. The Supervisor wrote the code, one fresh `Reviewer: T363` spawn (two rounds) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. Direction: ask only when a destructive verb targets a folder that holds a sensitive path, expand braces, write the rest down (option C) — RULE: the user's request "T363 go with C [admin]", after the T363 Debate of the previous request did not settle (Advocate 1: ask on any folder or unresolved name; Advocate 2: destructive verbs, braces, `python -c` checked; Advocate 3: option C)
5. Fixed every round-1 finding (5 P2, 2 P3) or named it in the hook header's limits, and spawned the reviewer again on the new commit — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires"
6. The round-2 P3s (N1: `timeout -s KILL` and `xargs` unnamed in the header limits; N2: no test pins the per-call budget or the folder count) go to follow-up task T374, and T363 merges as reviewed — DEBATED: Advocate 1: fix both now, then a third review round and a new auto verify (AC 5 asks the header to name the open cases; N2 is the LR-0003 pattern); Advocate 2: a follow-up task (P3 is optional, and any code change after the review needs a new reviewer spawn); Advocate 3: a follow-up task, and no edit of the hook at all, not even its header (nothing is worse than before T363). Settled by written rules: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |" and `docs/claude-md/pipeline-stages.md:225` "A later code fix needs a new reviewer spawn on the new commit"
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py` — 13 passed (red first: `22 failed, 5 passed` at 2026-11-25T11:19:19Z before the change; the round-1 tests `12 failed, 3 passed` at 2026-11-25T11:29:15Z before their fixes); every sensitive-path suite (8 files) `142 passed`; full suite `61 failed, 7970 passed` vs `main` `60 failed` (the 1 extra passes alone); reviews `Reviewer: T363` round 1 FAIL (5 P2, 2 P3, all fixed), round 2 PASS (2 P3, recorded below); `security-review` skill in the Supervisor session (temporary `refs/remotes/origin/HEAD` at the base `2b15b38e`, removed right after; its sub-task read the branch range) — no finding at confidence 8 or more; its one lead (brace expansion with no cap, 7/10) fixed; real run: the hook asks on `rm -rf .claude` in a constructed kit project and stays silent on `ls .claude` (`test_ac1_destructive_commands_on_a_holding_folder_ask`, `test_ac2_reads_and_other_targets_stay_silent`) (auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass (session 80a69ee1-22ef-4be9-a1c2-d56576671a88, commit 464e61b5350b70a8151395df72ad020a3d3fbcc3, log .claude/verify-runs/T363-464e61b5350b.log); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`); T371 (read-only commands that name a protected folder) stays its own task; round-2 P3 follow-ups registered as T374 (decision 6)
Closed: row moved to Done 2026-11-25 — auto verify pass (session 80a69ee1-22ef-4be9-a1c2-d56576671a88, commit 464e61b5350b70a8151395df72ad020a3d3fbcc3); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t363_folder_level.py` (AC 1 to 4); AC 5 by the three existing test files. Gaps listed above (mutants that stay green). |
| Verification command run | ☑ pass | `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py` -> `69 passed, 81 subtests passed in 6.80s` |
| Negative cases hold | ☑ pass | Mutation table above: 14 mutants made a T363 test red (SUBFAILED or FAILED); 7 mutants stayed green (listed). Findings 1 to 5 are cases that must ask and stay silent or hang: reproduced with `probe.py` (hook run as a subprocess, kit project in a temp dir). |
| verify | ☑ pass | auto-run by hook, session 80a69ee1-22ef-4be9-a1c2-d56576671a88, commit 464e61b5350b70a8151395df72ad020a3d3fbcc3, log .claude/verify-runs/T363-464e61b5350b.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `folder_hits`, `_segment_command`, `_folder_arguments`, `held_sensitive_path`, brace expansion in `command_tokens`, `sensitive_hits`, `main`'s exception path, and the hook's 3 other test files (run). Skipped: the full suite (one already runs in the worktree), `lib/shell_data.py` and the merge gate (not touched by the diff). |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression (Supervisor, at `8ce93206`): `61 failed, 7970 passed, 24 skipped` vs clean `main` worktree `60 failed, 7943 passed, 24 skipped`; the 1 extra, `.claude/hooks/tests/test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, passes alone (`9 passed`) and reads no changed file. At `ccc8d91e` (round 1): `60 failed`, the same set as `main` |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |

## Round 2 (Reviewer: T363, commit 8ce93206)

**Verdict: PASS.** All five round-1 P2 findings are fixed or named in the header's "Recorded limitations", and both P3 findings are fixed. No P0, P1 or P2 remains. Two new P3 findings (header gaps) and one P3 test gap are listed below; none blocks the merge. The real hook was run as a subprocess in a scratch kit project (scratchpad `p363r2`, probe `r2.py`/`r2b.py`); the worktree was not edited.

### Round-1 findings re-checked

| R1 # | Result | Evidence (hook subprocess, scratch kit project) |
|------|--------|-----------------------------------------------|
| 1 P2 brace blow-up timeout | fixed | `ls {a,b}` x24: ASK in 0.04 s (was timeout); `{a,b}` x500, 5000 `{`, a 3000-item group, nested groups: ASK or silent in 0.04 s; `ls {a,b}` x5 and `echo {{a,b},{c,d}}{e,f}` silent. `capped_brace_expansion` raises, `main`'s `try` turns it into an ask |
| 2 P2 unreadable last folder | fixed | `rm -rf ro` and `rm -rf ro/sub` (`ro/sub` mode 000): ASK |
| 3 P2 `find -exec` reads ask | fixed | `find . -name '*.py' -exec grep -l x {} +` and `find . -type f -exec wc -l {} +`: silent; `find . -name x -exec rm {} +`, `find . -exec rm {} \;`, `find config -execdir rm {} ;`, `find . -delete`: ASK |
| 4 P2 `git restore --staged` | fixed | `git restore --staged .`, `-S .`: silent; `--staged --worktree .`, `--staged -W .`, `git restore .`, `git checkout .`: ASK; `git checkout main`, `git restore src/app.py`: silent |
| 5 P2 unrecorded silent forms | fixed or named | Fixed (now ASK): `rm -rf conf*`, `./conf*`, `*`, `.cl*`, `config>/dev/null`, `config 2>&1`, `timeout 5 rm -rf config`, `\rm -rf config`. Named in the header: `bash -c`/`sh -c` bodies, `$PWD/config`, `git -C <dir> restore` (all still silent, as recorded). One residue: see N1 |
| 6 P3 `mv a.txt .` | fixed | `mv a.txt .`, `mv notes.txt src/`, `mv notes.txt config`: silent; `mv config old`, `mv .claude old`: ASK |
| 7 P3 walk cost | fixed | One budget per call, counting folders and files: `rm -rf big0..big4` (5 x 19000 files) ASK in 1.11 s (was 5.47 s); `rm -rf *` 1.17 s; three segments of `rm -rf big*` 1.21 s; 30000 empty folders ASK in 0.05 s (was silent) |

### New findings (confidence >= 75, each reproduced)

| # | Sev | File:line | Finding | One-line fix |
|---|-----|-----------|---------|--------------|
| N1 | P3 | `.claude/hooks/pre_tool_sensitive_path.py:552-555` (`_segment_command`) | `timeout -s KILL 5 rm -rf config` stays silent: the option's value `KILL` is taken as the duration, so `5` becomes the command. Likewise `xargs rm -rf config` and `find . -exec sh -c 'rm {}' \;` are silent. Only the `sh -c`/`bash -c` part is named in the header; `timeout` with an option value and `xargs` are not. | Add `timeout` options with a value, `xargs` and `find -exec sh -c` to the header's limit list (or skip `-s`/`-k` values) |
| N2 | P3 | `.claude/hooks/tests/test_t363_folder_level.py` | Test gaps (mutants that stay green): one budget shared across arguments (`budget` per argument instead of per call), and folders counted as well as files (`len(files)` only). The in-loop `if errors:` is redundant with the new post-loop check (equivalent mutant, not a gap). | Add a test with the cap set to 3 and two folders of 2 files each (ask), and one with only empty subfolders over the cap (ask) |

### Checks for the three things asked

- Fail-open: no timeout path left (brace cap, one walk budget, glob matches capped by `MAX_GLOB_MATCHES`); every exception in `folder_hits`, `command_tokens` and the walk is inside `main`'s `try` and becomes an ask (the brace `ValueError` was run: ASK). A walk error or a spent budget returns a hit, not None.
- New ask on an ordinary command: none found. Silent: `ls .claude`, `python3 -m pytest .`, `grep -rn x .claude`, `rm config`, `rm -rf build`, `rm -rf ../elsewhere`, `rm -rf repo` (secret only under `.git`), `git checkout main`, `git restore src/app.py`. Only a token that expands to over 1000 paths asks (by design).
- Guide AC 1 commands (`rm -rf .claude`, `rm -r`, `find .claude -delete`, `find . -name x -exec rm {} +`, `mv .claude old`, `git restore .`, `rm -rf secrets`/`config`) all ask; none stays silent.

### Security rules (`skills/code-review/references/security-reviewer.md`, hooks section)

Untrusted input is the command string, `cwd` and folder names. Both round-1 places where that input skipped the ask (timeout, unreadable folder) are closed. No file or command from the walked folder is executed; `os.walk` does not follow symlinks and prunes `.git`; the target stays bounded to the two roots. N1 is the same class as the recorded `bash -c`/variable limits: hardening, Low.

### Mutation check of the round-1 tests (scratch copy `mut2/`, worktree untouched)

| Test | Code change that turns it red (verified) |
|------|------------------------------------------|
| `test_r1_brace_bomb_asks_fast` | `capped_brace_expansion(...)` replaced by `expand_braces(...)` in `command_tokens` (red after 22 s) |
| `test_r1_an_unreadable_folder_asks` | the post-loop `if errors:` removed |
| `test_r1_read_only_finds_and_index_only_restores_stay_silent` | `FIND_DESTRUCTIVE_EXEC` check reverted to `FIND_ACTION_FLAGS`; the `--staged`/`-S` skip removed; `mv` returning all paths; `rm` without the `-r` requirement |
| `test_r1_destructive_forms_the_first_round_missed_ask` | glob folder expansion off; `timeout` removed from `COMMAND_PREFIXES`; the `timeout` duration skip off; the `lstrip("\\")` off; the redirect split off |
| `test_r1_a_secret_only_under_git_stays_silent` | the `.git` prune removed |
| `test_ac4_the_walk_cap_fails_toward_asking` | per-call budget replaced by 10**9; `if budget[0] < 0` made False |
| (no test) | per-argument budget, `len(files)` only: green (N2) |

### Evidence (round 2)

| Check | Result | Output |
|-------|--------|--------|
| Verification command, run in the worktree | pass | `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py` -> `74 passed, 96 subtests passed in 7.37s` |
| Full suite | not run | a full run is in progress in the worktree |
| `git status --short` after the review (code files) | clean | only this file changed |

## Demonstration

**BEFORE** (2026-11-25T11:19:19Z, the new test file against `main`'s hook, before the first implementation commit): `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py` printed `22 failed, 5 passed`: `rm -rf .claude`, `find .claude -delete`, `git restore .`, `mv .claude old` and `rm -rf config` (holding `config/.env`) got no ask, and `cp x .claude/{sensitive-paths.txt,y}` was silent.

**AFTER** (branch head `8ce93206`): the same file printed `13 passed, 48 subtests passed`. Every AC 1 command asks, naming the folder. `ls .claude`, `python3 -m pytest .`, `find . -exec grep …`, `git restore --staged .` and `rm -rf build` stay silent, and a brace token over 1000 paths asks in 0.04 s.

**DELTA**: an agent can no longer delete, move or restore a whole folder that holds the pattern list, the approval state or a listed secret without the human seeing an ask, and ordinary read commands cost no new prompt.

**WITNESS**: Supervisor session acceb8c1, 2026-11-25 (the BEFORE red run, full-suite comparison); `Reviewer: T363`, a fresh qa-expert (round 1 at `ccc8d91e`, round 2 at `8ce93206`, both with the real hook run as a subprocess in a scratch kit project).
