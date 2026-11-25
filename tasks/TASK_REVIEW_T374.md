# TASK_REVIEW — T374: The T363 folder rule reads past wrapper option values, names its xargs limit, and pins its walk budget

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
1. Took T374, then T371, stacked on T363's branch (same hook functions; T363 is Done, not merged) — RULE: the user's request "continue [admin] 371 and 374"
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High row)
3. The Supervisor wrote the code, one fresh `Reviewer: T374` spawn per round (five rounds) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. The value-option table covers `timeout`, `sudo`, `env`, `nice`, `time` and `exec`, and every segment is read both with and without the value skips — DEBATED: Advocate 1: keep the table for all four wrappers (one bug class); Advocate 2: narrow it to `timeout` as the row says (a wrong entry hides the command); Advocate 3: keep all four but drop `env -S` (its value is the command). Settled by a written rule: `.claude/hooks/pre_tool_sensitive_path.py:18` "Fail toward the human, never a silent allow (AC5)" — reading both ways means a wrong or missing entry can only add an ask; `env -S` dropped as Advocate 3 showed
5. Fixed every finding of rounds 1–4 (F1 P2 `env -S`, F2–F4; G1 P2 a reading landing on `cd`; H1 P2 `command cd`/`VAR= cd`/`\cd`/`time cd`; J1 P2 the folder-set cap) and spawned the reviewer again after each — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires"
6. Round 5's K1 (seven or more distinct `cd` targets in one command ask) left as it is — RULE: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |" (it fails toward the human)
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py` — 8 passed (red first: `4 failed, 4 passed` at 2026-11-25T11:44:04Z; each round's new tests red before its fix: 11:50:20Z `8 failed`, 12:47:42Z `4 failed`, 12:52:28Z `5 failed`, 12:57:17Z `5 failed`); the 9 sensitive-path suites `150 passed`; full suite at `6c0a3836` `60 failed, 7979 passed`, the same 60 as `main`; reviews `Reviewer: T374` rounds 1–4 PASS with one P2 each (all fixed), round 5 PASS (P3 only); `security-review` skill in the Supervisor session (temporary `refs/remotes/origin/HEAD` at `221fd720`, removed right after) — one finding, `env -S` (confidence 9/10), fixed; real run: the reviewers' harness (`cmp3.py`, 733 commands, the real hook as a subprocess against the T363 hook) — 0 old asks now silent, 0 new asks on ordinary commands (auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass, and after T363's merge); auto verify: running (T182); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t374_folder_rule_followups.py` covers AC 1, 2, 3 (AC 1 lacks the `--signal KILL` separate-word form, F3) |
| Verification command run | ☑ pass | `python3 -m pytest -q -p no:cacheprovider <the 5 guide files>` -> `79 passed, 105 subtests passed in 7.90s` (commit 524f0070, reviewer run) |
| Negative cases hold | ☑ pass | 16 mutations of a scratch copy (worktree untouched): 15 turn the file red (empty table or step-1 loop: 6 failed; one failed each for the sudo/nice/env entry, timeout `-k`, `--kill-after`, `-s`, sudo `-u`, env `-u`, nice `-n`; budget per folder; folders not counted; header xargs; header `-exec sh -c`). Survivor: dropping `--signal` stays green (F3). Real hook as subprocess, project with `config/.env`: `timeout -s KILL 5 rm -rf config` old silent, new ask; `timeout -s KILL 5 ls config` and `... rm -rf build` silent |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 524f0070 range only: `_segment_command` and its one caller `folder_hits`, the new table, the header. Not reviewed: T363 code, `lib/shell_data.py` (untouched) |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression (Supervisor, at `6c0a3836`): `60 failed, 7979 passed, 24 skipped` — the same 60 failures as the clean `main` worktree (`60 failed, 7943 passed, 24 skipped`). Earlier rounds each had one extra timing test under load (`test_memory_usage_report`, `test_t203_ac3_off_still_runs_a_marked_task[start]`, `test_ac4_any_other_answer_on_a_docs_only_branch_stays_blocked[none]`), each passing alone |
| **Companion score (easy-verifier)** | ☑ N/A | Not run in this review. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI (a PreToolUse hook). |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |

---

## Demonstration

**BEFORE** (2026-11-25T11:44:04Z, the new test file against the T363 branch's hook, before the first implementation commit): `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py` printed `4 failed, 4 passed`: `timeout -s KILL 5 rm -rf config`, `timeout -k 5 10 rm -rf config` and `timeout --kill-after 3 5 rm -rf config` got no ask (the option value was read as the command), and the header named neither `xargs` nor `find -exec sh -c`.

**AFTER** (branch head `6c0a3836`): the same file printed `8 passed, 33 subtests passed`. Every wrapper form asks, `env -S rm -rf config` asks, every `cd` form (`command cd`, `FOO=1 cd`, `\cd`, `time cd`, `builtin cd`) moves the folder, and a long `cd` chain asks. The reviewers' harness (733 commands, the real hook run as a subprocess against the T363 hook) shows 0 old asks gone silent and 0 new asks on ordinary commands.

**DELTA**: a destructive command behind a wrapper with an option value (`timeout -s KILL`, `sudo -u root`, `nice -n 5`) is judged like the bare command, and a wrong or missing table entry can no longer hide one.

**WITNESS**: Supervisor session acceb8c1, 2026-11-25 (BEFORE red run, the per-round red runs, full-suite comparison); `Reviewer: T374`, fresh qa-expert spawns in five rounds (`524f0070`, `1bbbf065`, `0337bfde`, `25ab79dd`, `6c0a3836`), each comparing the real hooks as subprocesses.

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

---

## Round 3 (Reviewer: T374, commit 0337bfde)

Verdict: **PASS on G1 and G2 (both fixed); one NEW P2 (H1) to fix before merge.** The round-2 fix narrowed the `cd` test to `words[0]`, and that turns off the folder move for `cd` forms a real shell still obeys. Confidence >= 75.

### Round-2 findings

| Round-2 | Result |
|---|---|
| G1(a) `sudo -u rm -rf cd`, `env -C rm -rf cd`, `nice -n 5 rm -rf cd` | fixed: ask (both readings are judged; a reading on `cd` no longer hides the other) |
| G1(b) `nice -n 5 cd x && rm -rf config`, `sudo -u root cd cd; rm -rf config` | fixed: ask (a wrapped `cd` no longer moves `where`) |
| G2 pin for an option in no table | fixed: `sudo --nonsense-opt rm -rf config` is in `test_r2_...` |

### Comparison, real hook as a subprocess (T363-branch hook vs 0337bfde hook; scratch project with `config/.env`, `cd/.env`, `build/`)

Harness: round 2's `cmp.py`, copied to `<scratchpad>/cmp3.py` (same command generator over every wrapper, option, with value / bare / `=VAL` / no duration, five targets) plus 15 `cd`-form commands. 733 distinct commands.

| Count | Result |
|---|---|
| Old ask, new silent | **0** in the generated set (round 2 had 38) |
| Old silent, new ask | 80, all `WRAPPER OPT VAL rm -rf config|cd` (a table option with its value before the command), the asks the task wants |
| New ask on an ordinary command (`ls config`, `rm -rf build`, `cat config/.env`) | **0** |

Second probe (`<scratchpad>/cd3.py`), `cd` forms followed by a command that depends on the folder (old / new):

| Command | old | new |
|---|---|---|
| `cd build && rm -rf ../config` | ask | ask |
| `command cd build && rm -rf ../config` | ask | **silent** |
| `FOO=1 cd build && rm -rf ../config` | ask | **silent** |
| `\cd build && rm -rf ../config` | ask | **silent** |
| `time cd build && rm -rf ../config` | ask | **silent** |
| `FOO=1 cd build; rm -rf ../cd` | ask | **silent** |
| `sudo cd build && ...`, `/usr/bin/cd build && ...` | ask | silent (correct: a child process; over-ask removed) |

### Findings

| ID | Sev | Where | Finding | One-line fix |
|----|-----|-------|---------|--------------|
| H1 | P2 | `.claude/hooks/pre_tool_sensitive_path.py:618` `if words and words[0] in DIR_CHANGE_COMMANDS` | NEW silence vs T363 (fail-open in a High-risk hook). The test now looks at the first word only, so `command cd build`, `VAR=x cd build`, `\cd build`, `time cd build` no longer move `where`. A real shell DOES change folder for these (builtin `cd` with an assignment, `command cd`, `\cd`, `time cd`). The next segment is then resolved against the wrong folder: `FOO=1 cd build && rm -rf ../config` (with `config/.env`): T363 hook ask, this hook silent. The same shape as G1(b), the other way round. Not covered by the tests. | Find the verb with `_segment_command` past only `VAR=`, `\`, `command`, `time` (not the value-skip table, not `sudo/env/nice/exec/timeout/nohup`), and move `where` when that verb is `cd`/`pushd`; add `FOO=1 cd build && rm -rf ../config`, `command cd build && rm -rf ../config`, `\cd build && rm -rf ../config` to `test_r2_...` |
| H2 | P3 | `.claude/hooks/tests/test_t374_folder_rule_followups.py` `test_r2_...` | Pin gap: no row has a moving `cd` form other than a bare `cd`; H1 passes the whole suite. | The rows from H1 |

Checked, no finding: `i += 2` past the end and an empty `words` (the `words and` guard; `_segment_command([])` returns `(None, [])`); `dict.fromkeys` keeps both readings on one walk budget and one folder list; `target` read from `words[1:]` still skips `-` options; the hook still only reads the string and runs nothing from it; header names `xargs`, `find -exec sh -c`, `env -S "..."`, `git -C ... restore`.

### Evidence

Verification Command in the worktree (five guide files, no full suite; `git status` clean before my edit of this file):

```
$ python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
81 passed, 119 subtests passed in 8.47s
```

---

## Round 4 (Reviewer: T374, commit 25ab79dd)

Verdict: **H1 and H2 fixed; one NEW P2 (J1) to fix before merge.** The folder set doubles on every `cd`, so the cap of 16 is reached after 4 `cd` segments, and the 5th drops the real folder. Confidence >= 75 (reproduced with the real hook).

### Round-3 findings

| Round-3 | Result |
|---|---|
| H1 `command cd`, `FOO=1 cd`, `\cd`, `time cd` | fixed: ask (old ask, new ask) |
| H2 pin | fixed: `test_r2_...` has the six forms (also `builtin cd`) |

### Comparison (T363-branch hook vs 25ab79dd hook, real hook as a subprocess; harnesses `cmp3.py`, `cd3.py`)

| Count | Result |
|---|---|
| cmp3.py, 733 commands: old ask, new silent | **0** |
| old silent, new ask | 80, all `WRAPPER OPT VAL rm -rf config|cd` (the asks the task wants) |
| New ask on an ordinary command (`ls config`, `rm -rf build`, `cat config/.env`) | **0** |
| cd3.py, 12 `cd` forms: old ask, new silent | **0** (`builtin cd build && rm -rf ../config`: old silent, new ask) |

### Findings

| ID | Sev | Where | Finding | One-line fix |
|----|-----|-------|---------|--------------|
| J1 | P2 | `.claude/hooks/pre_tool_sensitive_path.py` `folder_hits`: `wheres = list(dict.fromkeys(wheres + moved))[:MAX_CD_FOLDERS]` | The set holds every old folder plus every old folder moved, so it doubles per `cd` (1, 2, 4, 8, 16) and is truncated at the 5th `cd`; the truncation keeps the oldest entries and drops the newest, which is the folder a real shell is in. Repro (project with `a/b/c/d/e/f/.env`): `cd a && cd b && cd c && cd d && cd e && rm -rf f`: old **ask**, new **silent** (4 `cd` still ask). `cd a && cd b && cd . && cd . && cd . && cd c && cd d && cd e && rm -rf f` and `cd . && cd . && cd . && cd a && ... && cd e && rm -rf f`: old ask, new silent (a `cd .` doubles the set to no purpose; dedup only removes exact repeats). `cd a/b && cd ../.. && ...` x4 then the chain: old ask, new silent. Fail-open past the cap in a High-risk hook, and a regression vs T363 for a plain 5-step `cd` chain. Not pinned: no test has more than one `cd`. | Do not double: keep one chain (`chain = join(chain, target)`) and put `cd` of a wrapped form into the set only as a fork; or, when the cap is reached, ask (fail toward the human) instead of dropping. Add `cd a && cd b && cd c && cd d && cd e && rm -rf f` and the `cd .` x3 form to the tests |
| J2 | P3 | `test_t374_folder_rule_followups.py` | No test for the cap or for a chain of `cd`; J1 passes the whole suite. | The rows from J1 |

Checked, no finding: a `cd` with no target leaves the set alone; `walked` skips a folder seen before (its hit was already recorded, and the budget is not spent twice); both readings and all folders share one budget; the hook only reads the string and runs nothing from it; `builtin` in `COMMAND_PREFIXES` is a prefix only (asks more, never less).

### Evidence

Verification Command in the worktree (five guide files, no full suite):

```
$ python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
81 passed, 125 subtests passed in 8.60s
```

Cap probe harness: `<scratchpad>/cap5.py` (`python3 -I cap5.py <scratchpad>`): the first row `cd a && cd b && cd c && cd d && cd e && rm -rf f` prints `ask silent`.

---

## Round 5 (Reviewer: T374, commit 6c0a3836)

Verdict: **PASS. J1 and J2 are fixed; no P0-P2 finding; one P3 note.** Confidence >= 75 (real hook as a subprocess).

### Round-4 findings

| Round-4 | Result |
|---|---|
| J1 `cd a && cd b && cd c && cd d && cd e && rm -rf f`, `cd .` x3 forms, `cd a/b && cd ../.. ` forms | fixed: ask (old ask, new ask). Past `MAX_CD_FOLDERS` (64) the code raises `ValueError`, which `main()` turns into an ask; no folder is dropped |
| J2 pin | fixed: `test_r4_a_long_cd_chain_never_drops_the_shell_folder` (four chains plus an 8-`cd` chain over the cap) |

### Comparison (T363-branch hook vs 6c0a3836 hook; harnesses `cmp3.py`, `cd3.py`, `cap5.py`, new `multi5.py`)

| Harness | Count |
|---|---|
| cmp3.py, 733 commands: old ask, new silent | **0** |
| cmp3.py: old silent, new ask | 84 listed lines: the wrapper option-value `rm -rf config|cd` asks the task wants (round 4 counted 80; the extra lines are `env -u cd rm -rf config`-type rows, same shape) |
| cmp3.py: new ask on an ordinary command (`ls config`, `rm -rf build`, `cat config/.env`) | **0** |
| cd3.py, 12 `cd` forms: old ask, new silent | **0** (`builtin cd build && rm -rf ../config`: old silent, new ask) |
| cap5.py, 20 chains: old ask, new silent | **0** (7 ask/ask; 13 old silent, new ask: chains with `cd x` into folders that do not exist, kept as forks, an over-ask toward the human) |
| multi5.py, 8 ordinary multi-cd commands | 7 silent/silent, including `cd build && git status && cd ..`, `cd build && ls && cd .. && cd build && ls`, 4-`cd` chains, 5 x `cd build && ls && cd ..` then `rm -rf build`. 1 silent/ask: 8 distinct `cd xN` then `rm -rf build` (see K1) |

### Findings

| ID | Sev | Where | Finding | One-line fix |
|----|-----|-------|---------|--------------|
| K1 | P3 | `.claude/hooks/pre_tool_sensitive_path.py:633-636` (`MAX_CD_FOLDERS` raise in the `cd` branch) | The set doubles per distinct `cd`, so 7 distinct `cd` targets in one command ask even when no folder verb follows (the test's own `cd x0 ... cd x7 && ls` asks). Fail-safe, not a hole; a kit session with 7+ different `cd` hops in one command is rare, and `cd ..` / repeated `cd` back to a folder do not grow the set. | Optional: raise only when a folder verb is later seen, or raise the cap; no change needed to merge |

Checked, no finding: `ValueError` reaches the ask path in `main()`; dedup keeps `cd .` and `cd x && cd ..` from growing the set; `walked` and the `(arg, folder)` dedup keep one walk budget across readings and folders; the hook still only reads the string and runs nothing from it; `builtin` stays a prefix only.

### Evidence

Verification Command in the worktree (five guide files, no full suite; `git status` clean before my edit of this file):

```
$ python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
82 passed, 129 subtests passed in 8.90s
```
