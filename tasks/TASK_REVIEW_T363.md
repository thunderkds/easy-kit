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

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t363_folder_level.py` (AC 1 to 4); AC 5 by the three existing test files. Gaps listed above (mutants that stay green). |
| Verification command run | ☑ pass | `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py` -> `69 passed, 81 subtests passed in 6.80s` |
| Negative cases hold | ☑ pass | Mutation table above: 14 mutants made a T363 test red (SUBFAILED or FAILED); 7 mutants stayed green (listed). Findings 1 to 5 are cases that must ask and stay silent or hang: reproduced with `probe.py` (hook run as a subprocess, kit project in a temp dir). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `folder_hits`, `_segment_command`, `_folder_arguments`, `held_sensitive_path`, brace expansion in `command_tokens`, `sensitive_hits`, `main`'s exception path, and the hook's 3 other test files (run). Skipped: the full suite (one already runs in the worktree), `lib/shell_data.py` and the merge gate (not touched by the diff). |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | Not run by the reviewer (a full run is in progress in the worktree); the four hook test files are green. |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |
