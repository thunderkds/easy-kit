# TASK_REVIEW — T374: The T363 folder rule reads past wrapper option values, names its xargs limit, and pins its walk budget

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t374_folder_rule_followups.py` covers AC 1, 2, 3 (AC 1 lacks the `--signal KILL` separate-word form, F3) |
| Verification command run | ☑ pass | `python3 -m pytest -q -p no:cacheprovider <the 5 guide files>` -> `79 passed, 105 subtests passed in 7.90s` (commit 524f0070, reviewer run) |
| Negative cases hold | ☑ pass | 16 mutations of a scratch copy (worktree untouched): 15 turn the file red (empty table or step-1 loop: 6 failed; one failed each for the sudo/nice/env entry, timeout `-k`, `--kill-after`, `-s`, sudo `-u`, env `-u`, nice `-n`; budget per folder; folders not counted; header xargs; header `-exec sh -c`). Survivor: dropping `--signal` stays green (F3). Real hook as subprocess, project with `config/.env`: `timeout -s KILL 5 rm -rf config` old silent, new ask; `timeout -s KILL 5 ls config` and `... rm -rf build` silent |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 524f0070 range only: `_segment_command` and its one caller `folder_hits`, the new table, the header. Not reviewed: T363 code, `lib/shell_data.py` (untouched) |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | Not run by this reviewer (a full run was already in progress); the five guide suites above are green |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI (a PreToolUse hook). |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |

---

## Demonstration

Not filled by this reviewer (the Supervisor owns BEFORE/AFTER). Reviewer observation, real hook as a subprocess, 2026-11-25: `timeout -s KILL 5 rm -rf config` (config/.env present): T363 hook silent, T374 hook ask.

---

## Review findings (code-review rules + hooks rules of `skills/code-review/references/security-reviewer.md`)

Verdict: **PASS with one P2 to fix before merge** (F1). Confidence >= 75 for every finding.

| ID | Sev | Where | Finding | One-line fix |
|----|-----|-------|---------|--------------|
| F1 | P2 | `.claude/hooks/pre_tool_sensitive_path.py` `PREFIX_VALUE_OPTIONS["env"]` (`-S`, `--split-string`) | NEW silence. Unquoted `env -S rm -rf config` runs `rm -rf config` (`-S` takes `rm`, the rest are its arguments). The T363 hook asked; the T374 hook is silent: the table steps over the word that IS the command. Seen with the real hook as a subprocess: old `ask`, new `silent`. Quoted `env -S "rm -rf config"` is silent either way (quoted spans are stripped first), so the entry gains nothing. | Remove `-S`/`--split-string` from the `env` set. |
| F2 | P3 | same table, `sudo` `-h`/`--host` | NEW silence for `sudo -h rm -rf config` (ask before, silent now). Bare `-h` is help in sudo; only `-h host` with `-l` takes a value, so the entry is wrong for the common form. | Drop `-h`/`--host` from `sudo`. |
| F3 | P3 | `.claude/hooks/tests/test_t374_folder_rule_followups.py:50-53` | Mutation survivor: removing `--signal` (separate-word `timeout --signal KILL 5 rm -rf config`) stays green; only `--signal=KILL` is tested. Other entries (sudo `-g/-D/-C/--user`, env `-C/--unset`, nice `--adjustment`) are also untested. | Add `timeout --signal KILL 5 rm -rf config` to the AC 1 tuple. |
| F4 | P3 | same table | Old silences left open, inconsistent with the siblings the table lists: `sudo -R/--chroot DIR`, `sudo -T/--command-timeout N`, `env -P DIR`, `env -a NAME`, `time -o FILE`/`-f FMT`, `exec -a NAME` (the value is read as the command; `sudo -R /x rm -rf config` silent, old and new). Not new, not in an AC. | Add the entries or name them in the header limits; not a blocker. |

Checked, no finding:
- NEW ask on an ordinary command: none. `timeout -s KILL 5 rm -rf build` and `ls config` stay silent; the change only moves the judged word to the real command.
- Exception path: `i += 2` past the end just ends the loop; `words[i]` is guarded by `i < len(words)`; `timeout -s` alone returns `(None, [])`; `.get(wrapper, ())` is safe for `command/nohup/time/exec`. The hook's existing fail-closed `ask` on an internal error is unchanged.
- Hooks rules: the hook still only reads the command string and runs nothing from it; the new step is a dict lookup, with no fetch, install or write. The one security-relevant regression is F1.

### Test-to-mutation map (scratch copy only)

| Test | Change that turns it red |
|------|--------------------------|
| `test_n1_timeout_with_an_option_value_still_asks` | empty table or a step-1-only loop; removing `-s`, `-k` or `--kill-after` (timeout), `-u` (sudo, env), `-n` (nice), or a whole wrapper set. Not `--signal` (F3) |
| `test_n1_timeout_on_a_reading_command_stays_silent` | none of my table mutations (it is green in all). It would go red only if a reading command began to ask, e.g. a loop that stepped 0 words for `-s` |
| `test_n1_header_names_xargs_and_find_exec_sh` | deleting `xargs` or `find -exec sh -c` from the header's Recorded limitations |
| `test_n2_the_budget_is_shared_by_every_folder_of_the_call` | a fresh budget per folder (`[_walk_cap()]` at the `held_sensitive_path` call) |
| `test_n2_folders_count_against_the_budget` | `budget[0] -= len(files)` (folders not counted) |

---

## Round 2 (Reviewer: T374, commit 1bbbf065)

Verdict: **PASS with one P2 to fix** (G1). Round-1 F1-F4 are fixed. Confidence >= 75 for G1.

### Round-1 findings, checked with the real hook as a subprocess

Scratch kit project (`config/.env`, `cd/.env`, `build/`), the T363-branch hook against the 1bbbf065 hook, 718 commands: every `PREFIX_VALUE_OPTIONS` wrapper and option (and `env -S/--split-string`, `command`, `nohup`) with a value, with the command right after the option, `--opt=VAL`, and unknown `-x`, each over `rm -rf config`, `rm -rf cd`, `ls config`, `rm -rf build`, `cat config/.env`.

| Round-1 | Result |
|---|---|
| F1 `env -S rm -rf config` / `--split-string` | fixed: asks (old asked too) |
| F2 `sudo -h rm -rf config` | fixed: asks |
| F3 `timeout --signal KILL 5 rm -rf config` | fixed: asks, now in the test tuple |
| F4 `sudo -R/-T`, `env -P/-a`, `time -o/-f`, `exec -a` | fixed: ask with a value and with the command right after the option |
| New ask on an ordinary command | none: `ls config`, `rm -rf build` stay silent for every form; the only new asks are the `OPT VALUE rm -rf config` forms the task wants |
| Old ask, now silent | **38 commands, all one cause (G1)** |

### Findings

| ID | Sev | Where | Finding | One-line fix |
|----|-----|-------|---------|--------------|
| G1 | P2 | `.claude/hooks/pre_tool_sensitive_path.py` `folder_hits`: the `if verb in DIR_CHANGE_COMMANDS: ... continue` runs on the skipping reading only, before the plain reading is built | The "no command the T363 hook asked on is now silent" claim is false for `cd`/`pushd`. When the skipping reading lands on `cd`, the segment is taken as a directory change and the plain reading is never judged. (a) `sudo -u rm -rf cd`, and the same for every table option of sudo/env/nice/time/exec (`env -C rm -rf cd`, `nice -n rm -rf cd`, ...): old ask, now silent, for a folder named `cd` or `pushd` that holds a sensitive path. (b) `nice -n 5 cd x && rm -rf config` and `sudo -u root cd cd; rm -rf config`: old ask, now silent, because the later segment is resolved against a moved `where` (`cd` under a wrapper does not change the shell's folder). Contrived (a folder named `cd`; `cd` behind a wrapper) but a fail-open in a High-risk hook, and the round-1 fix exists to rule it out. No test covers it. | Build `readings` first and apply the `cd` shift only when the plain reading is also a `cd` (else judge both readings and leave `where` alone); add `sudo -u rm -rf cd` and `nice -n 5 cd x && rm -rf config` to `test_r1_...` |
| G2 | P3 | `test_t374_folder_rule_followups.py` `test_r1_...` | Weak pin: dropping the plain reading turns only the `sudo -h rm -rf config` subtest red (every other row is also caught by the table). Putting `-S` back in the `env` table stays green (the plain reading catches it), so the `-S` removal itself is not pinned. Fine as a safety net. | Add one row whose option is in no table (`sudo --nonsense-opt rm -rf config`) |

Checked, no finding: the exception path and `i += 2` past the end (loop just ends); both readings share one walk budget and one folder list (`dict.fromkeys`), so a wrapper form never spends the budget twice; the hook still only reads the string and runs nothing from it; the header names `xargs`, `find -exec sh -c`, `env -S "..."`.

### Test-to-mutation map for `test_r1_a_wrong_or_missing_table_entry_never_hides_the_command` (scratch copy only, worktree untouched)

| Change | Result |
|---|---|
| Delete the `if plain != (verb, args): readings.append(plain)` lines (the second reading) | RED: 1 subtest, `sudo -h rm -rf config` (the other 8 rows are caught by the table) |
| Read every segment without the skips (`skip_values=False` on the first read) | RED: 12 failed in the file |
| Start `readings` empty (plain reading only) | RED: 19 failed |
| `-S` back into the `env` table, second reading kept | green (the second reading covers it; not pinned) |

### Evidence

Verification Command in the worktree (the five guide files, no full suite):

```
$ python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
80 passed, 114 subtests passed in 8.17s
```
