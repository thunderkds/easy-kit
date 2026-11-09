# TASK_REVIEW — T296: Merge gate: hidden git verbs, `merge --message`, and slot 2b brace and glob escapes

> Sibling of `tasks/TASK_GUIDE_T296.md`. Everything here is **filled by the reviewer at Stage
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
1. The hidden-verb refusal applies only under `[auto]` and `[admin]`; with no tag the 11 forms stay allowed as before, and a no-tag refusal is a separate task with its own corpus of ordinary commands. The guide's AC row 1 (line 58) and test row 1 (line 77) say "still blocked with no tag", but requirement (a) (line 28) says "Under `[auto]` and `[admin]`" — DEBATED: auto-mode only, amend AC row 1 and test row 1 (Advocate 1: keep auto-only, because a no-tag refusal blocks ordinary `$(…)` and `$var` git commands in every session; Advocate 2: keep auto-only, correct the two guide rows, open a follow-up task with a false-positive corpus if a no-tag refusal is wanted; Advocate 3: keep auto-only as the smallest safe thing, because the hook comment says "Outside auto mode nothing changes" and `docs/claude-md/tracks.md:642` says "Outside auto mode these forms behave as before") ⚠ decided for you — please review
2. The code review and the security review of this branch must report before the task is marked ready — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4 ("Skill({ skill: "code-review" }) always; security-review for Medium/High risk")
3. Two independent reviews (a code review that drove about 280 commands through the real hook, and a static security review) blocked the branch: a hidden `git` word or verb still passed in about 12 shapes (a redirect between `git` and the verb, `--attr-source`, an earlier `git rebase`, `env -u git git "push"`, `{git,push}`, `eval`, `env -S'…'`, dashed `git-push`, an alias set through `GIT_CONFIG_*`, `xargs git`, a path-qualified `git` after an unknown head, `git subtree push`) and slot 2b mis-filed two shapes; the fix round rewrote the scan as one structural rule (every word whose basename is `git` or `git-<verb>` is read, a git word whose verb cannot be read is a doubt, an unknown option before the verb is a doubt) and fixed slot 2b — RULE: `.claude/skills/code-review/SKILL.md` § Severity Scale "P0 | Correctness bug, data loss, security hole | Yes — hard block"
4. No agent ran a real push from this session after the no-push rule; the real push witness for the fix-round shapes is a lab script that you run yourself — RULE: `docs/claude-md/tracks.md` `### Stops that stay` ("a safety-hook block")
5. A second-round adversarial review (45300 fuzz candidates against a stand-in `git`) confirmed 11 more bypass classes and 3 new false positives. Round 3 fixes the plain shapes (`>|` read as a pipe, an empty-string argument that swallows the verb, `xargs` behind a wrapper), the 3 false positives that would block normal `[auto]` work (`man git-push`, `$DOCKER push registry/img`, `GIT_CONFIG_GLOBAL=/dev/null git status`), and one cheap rule for `$'…'` and `$"…"` quoting next to a git word; it documents the deliberate-obfuscation classes as limits (an unknown wrapper before a hidden word, exotic `env -S`, a shell alias, the trace-gate quote desync that already existed at `bc5ccc34`) — RULE: `docs/claude-md/tracks.md:632` "`[admin]` as a guard against accidents, not against a hostile repo or a hostile agent."
6. No third review round after round 3: with the reviewer's own fuzz (`lib/fuzz.py`, 5 seeds of 7000 commands) the allowed publishes in `[auto]` fell from 2848 to 147, and 133 of those 147 sit behind an unknown wrapper, which is a documented limit; the shapes left are deliberate obfuscation — RULE: `docs/claude-md/tracks.md:632` "`[admin]` as a guard against accidents, not against a hostile repo or a hostile agent."
Checks: tests (implementer) `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — 5627 passed, 5 skipped, 25 subtests passed (after round 3; 845 tracks, review and admin-tag tests re-run after the last docs edit); 47 mutation controls red (28 in the fix round, 19 in round 3); 67 forms blocked in `[auto]` and `[admin]` after the fix round, unchanged with no tag; round 3: 38 of 38 plain shapes blocked (36 were allowed before), 0 of 29 ordinary commands blocked (14 were before); reviews code-review — block, fixed; security-review — block, fixed; adversarial review round 2 — 11 classes, round 3 fixed A, E, G, 3 false positives and the `$'…'` rule (auto-checked, not /verify)
Memory: memory/learnings.md — "A text gate over shell input: allowlist the plain shapes; the author's fuzz proves little; stop at documented limits (T294, T296)" (written once for T294 and T296); memory/MEMORY.md — one index line under Patterns & Gotchas
Not done: real push witness for the fix-round shapes: run by the user outside an `[auto]` session (`!bash /tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/lab_t296_push.sh`); documented limits (an unknown wrapper before a hidden word, exotic `env -S`, a shell alias, a heredoc or pipe into a shell, `$(echo 'git push …')`, `su -c`, `busybox sh -c`, `GIT_CONFIG_*` set in the profile, the own-remote rule's trust in the starting directory); merge (yours); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_gate_hidden_verbs.py` (rows 1, 2, 3, 5, 6, 7, 8) and `.claude/hooks/tests/test_slot2b_brace_glob.py` (rows 4, 5, 6); `merge_gate_guard.py` and `test_merge_gate_guard.py` (row 8, `T296` in `AUTHORISED_TASKS`). Run against the unchanged hooks they gave 114 failed (see Demonstration); now `414 passed in 5.76s`. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or slot or task_context or hidden"` -> `1147 passed, 1690 deselected in 28.33s`. `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4797 passed, 25 subtests passed in 332.50s (0:05:32)` (2026-11-09, HEAD `7503935d`). Fix round (2026-11-09, HEAD after `c5c18be6`): `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `5175 passed, 5 skipped, 25 subtests passed in 518.42s (0:08:38)`. Fix round 3 (2026-11-09, HEAD `2cd59933` plus the docs edit): `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `5627 passed, 5 skipped, 25 subtests passed in 443.21s (0:07:23)`. |
| Negative cases hold | ☑ pass | Red run against the prior content: 114 failed, 268 passed (Demonstration). Mutation controls (19), each one byte change in `pre_bash_block_unsafe_merge.py` or `lib/task_context.py` (`git diff --stat` non-empty), run on the two new test files (414 tests), restored after each; every one turned tests red. The three the guide names: M1 `hidden_git_verb` returns False: `103 failed, 311 passed`; M2 `--message` out of `MERGE_OPTIONS_WITH_ARG`: `6 failed, 408 passed`; M3 brace refusal out of slot 2b: `7 failed, 407 passed`. Diffs and the rest are under the table. Fix round: tests-first commit `1638a47d` red (153 failed for the unit and gate checks, 175 with slot 2b and admin tests); 28 new mutation controls N1-N28 all red (see the Fix round section); `hidden_git_verb` returns False: `296 failed, 496 passed, 5 skipped`. Fix round 3: 19 mutation controls, all red (see the Fix round 3 section); new test file run against the hook of `664c2f00`: `191 failed, 1005 passed, 5 skipped`. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the two hook files and the five test files named in the guide, `docs/claude-md/tracks.md` (`### Admin tag`, Known limits, slot 2b rules). Dependents of `invokes_test_runner` and slot 2b ran in the full suite. Stale-text grep (LR-0005) for `quote inside the word`, `Cheap hidden verbs`, `merge --message <branch>`, `find -exec git`, `cannot tell which branch` over the repo: only history (`TASK_REVIEW_T284`, the hunt, guides) and the new tests remain. Not reviewed: the heredoc scanner (T294) and the repo config and hook allowlist (T295), out of scope. Not run by this agent: `code-review` and `security-review` skills (Stage 4, the Supervisor). |
| Full smoke suite still green (no regression) | ☑ pass | `4797 passed, 25 subtests passed in 332.50s (0:05:32)`. The pin tests the guide names ran in it: `test_admin_tag.py` (T284), `test_stop_attribution_t287.py`, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, the tracks.md text pins, `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Fix round: `5175 passed, 5 skipped, 25 subtests passed in 518.42s (0:08:38)` (includes the pin-test pre-flight: `test_auto_mode.py`, `test_stop_auto_mode_check.py`, `test_admin_tag.py`, `test_stop_attribution_t287.py`, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, the tracks.md pins). |
| **Companion score (easy-verifier)** | ☑ N/A | Neither companion tool was run for this task; the guide does not require it. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Hook code and docs only; no UI component. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Hook code and docs only; no UI component. |
| **UI: Responsiveness at target viewports** | ☑ N/A | Hook code and docs only; no UI component. |

**Mutation controls** (each applied to the worktree, tests run, file restored with the original bytes; run 2026-11-09):

```
M1  .claude/hooks/pre_bash_block_unsafe_merge.py  | 1 +
+    return False     (first line of the body of hidden_git_verb, before `text = strip_heredoc_bodies(command)`)
    -> 103 failed, 311 passed
M2  .claude/hooks/pre_bash_block_unsafe_merge.py  | 2 +-
-MERGE_OPTIONS_WITH_ARG = frozenset({"-m", "--message", "-F", "--file", ...
+MERGE_OPTIONS_WITH_ARG = frozenset({"-m", "-F", "--file", ...
    -> 6 failed, 408 passed
M3  .claude/hooks/lib/task_context.py  | 2 +-
-    if "{" in command or "}" in command or _unquoted_glob(command):
+    if _unquoted_glob(command):
    -> 7 failed, 407 passed
M4  glob refusal out (`or _unquoted_glob(command)` removed)            -> 5 failed, 409 passed
M5  `send-pack` out of PUBLISH_VERBS                                    -> 5 failed, 409 passed
M6  `_own_origin_refusal` returns None at once                          -> 1 failed, 413 passed
M7  slot 2b `_git_verb_allowed` check removed                           -> 5 failed, 409 passed
M8  backslash + newline joined with a space again                       -> 2 failed, 412 passed
M9  `invokes_test_runner` back to QUOTED_SPAN_PATTERN                   -> 14 failed, 400 passed
M10 `--cleanup` out of MERGE_OPTIONS_WITH_ARG                           -> 2 failed, 412 passed
M11 `--file` out of MERGE_OPTIONS_WITH_ARG                              -> 3 failed, 411 passed
M12 `timeout` out of SHELL_WRAPPERS                                     -> 1 failed, 413 passed
M13 the verb refusal reason back to "cannot tell which branch"         -> 3 failed, 411 passed
M14 abbreviated long option (`--mess`) rule off                         -> 3 failed, 411 passed
M15 short-option run rule (`-qm <x>`) off                               -> 18 failed, 396 passed
M16 nonliteral command word (`$g push`) rule off                        -> 10 failed, 404 passed
M17 `bash -c '...'` recursion off                                       -> 5 failed, 409 passed
M18 depth limit off                                                     -> 1 failed, 413 passed
M19 PLAIN_VERB check off                                                -> 26 failed, 388 passed
```
The first agent run also reached a wrapper-assignment mutation (its M23, pinned by commit `4faf490a`).
Mutation script (outside the repo): `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/mutate.py`.

**Follow-ups and notes** (cut list, not built): `-S`/`--gpg-sign` and `--log` take an optional attached value only, so they never take the next word (git's own rule; pinned by `(["-S", B], [B])`). `git submodule foreach` and `git rebase --exec` stay unseen and are named in Known limits. The stray root file `corpus_old.json` (a capture artifact, referenced by no test) was removed.

**Fix round (Stage 4: code review and security review blocked the branch).** Work after commit `2d3a931c`, test first
(tests-first commit `1638a47d`, red) then the fixes. Rule that replaced the one-off patterns: every word whose
basename is `git` or `git-<verb>` is a git word and all of them are read (no early return); a git word whose verb
cannot be read is a doubt; a doubt is a block in auto mode; the check also runs when the command holds a `rebase`;
an error in the check is a block. The `[admin]` path cross-checks the same scan against its old segment loop.

| Item | Fix | Test (goes red on `1638a47d`) |
|------|-----|------|
| C1 redirect between git and verb | redirects are skipped, then the verb is read (`git >/dev/null push` is a push) | `c1-*` in `HIDDEN_R2`, gate [auto]/[admin] |
| S1 `--attr-source`, `--super-prefix` | added to `GIT_OPTIONS_WITH_ARG` and `GIT_OPTION_ARGS` (now one tuple) | `s1-*`, `test_r2_attr_source_is_a_value_option_for_the_plain_patterns` |
| S2 `rebase` skips the check | the check runs when no auto-mode pattern matches | `test_r2_a_rebase_does_not_hide_...` |
| S3 first git-looking word returns | all candidates examined | `s3-*` |
| S4a/c/d brace command word, `eval`, continuation | `BRACE_EXPANSION`, `eval` is a doubt, `join_line_continuations` before tokenising | `s4a-*`, `s4c-*`, `s4d-*` |
| C2 `env -S` attached | `-S<v>`, `-iS<v>`, `--split-string=<v>` | `c2-*` |
| C3 dashed git commands | basename `git-<verb>` is a git word; `git-send-pack`, `git-push`, ... are publishing; `[admin]` refuses any dashed command | `c3-*`, admin test |
| C4 alias through the environment | `GIT_CONFIG_COUNT`/`PARAMETERS`/`KEY_*`/`VALUE_*`, `GIT_EXEC_PATH`, `GIT_CONFIG_GLOBAL`/`SYSTEM` with a git word in the command | `c4-*` |
| C5 `xargs git` | no verb after `xargs` is a doubt | `c5-*` |
| C6/S5 path-qualified git after unknown head or redirect | rule (i): no `word == "git"` condition | `c6-*`, `s5-*` |
| C8 other publishing verbs | `receive-pack`, `remote-ext`, `subtree`, `svn`, `p4`, `cvsexportcommit` (each justified in a comment) | `c8-*` |
| SL6 even backslashes before newline | `join_line_continuations` (left to right) in `lib/task_context.py` | `test_sl6_*` |
| SL7 value option read as flag | slot 2b allows only the no-value global options | `test_sl7_*` |
| X1 exception in the check | `try/except` in `main()`: a block in auto mode | `test_r2_x1_*` |
| 9 SHELL_KEYWORDS untested | `if`, `for`, `!`, `{` cases | `k-*` |
| 10 false positives | a nonliteral command word is a doubt only with a brace expansion, a variable this command sets, or a later publishing verb or `-c` | `BENIGN_R2` |
| 11, 17 surviving mutations | benign `cp $a pull`; `g[i]t`, `{g,}it`; own-remote ROOT and same-common-dir tests | `w-*`, own-remote tests |
| 13 dead clause | `"=" not in arg` removed (mutation N29 is an equivalent mutant: the clause never changed an answer) | existing option tests |
| 14 "Four more limits" | now "Nine more limits" | docs |
| 15 refusal wording | the `read-only` text only for `ADMIN_READ_ONLY_GIT` verbs | `test_r2_admin_verb_text_...` |
| 16 hard counts | replaced by a data-derived check | `test_r2_corpus_overrides_...` |
| own remote | URL of a local path is resolved before comparing; the rule still trusts the starting directory (a Known limit) | symlink and relative path test |

Reproduced then fixed: 64 forms of the fix-round table at the tests-first commit `1638a47d` through the hook's real
`main()` (gate only, nothing run): 51 ALLOWED in both `[auto]` and `[admin]`. Now (`HEAD`) all 67 forms of the table are
BLOCKED in both (no tag: unchanged, ALLOWED). At `1638a47d` the new unit and gate tests failed 153 times (the unit and gate
checks of the forms), 175 with the slot 2b and admin tests. The shapes were first shown to push in a real shell with the first
run's script (before the Supervisor's no-push rule); the repo's premise tests now use a stand-in `git` that only records its
arguments, so the suite pushes nothing.

Gate verdicts after the fix (HEAD, 2026-11-09T03:51Z; `[auto]=BLOCKED [admin]=BLOCKED none=ALLOWED` for each of: c1 redirect
out/in/both/env-prefix/after-C/merge-pager/force-main/merge/fd; s1 push/merge/pull/super-prefix; s2 rebase-then-push; s3 env-u,
xargs-E; s4a brace command word and in-word; s4c eval quoted/var/wrapped; s4d continuation (git word and verb); c2 attached/long/
clustered; c3 send-pack/push/exec-path-substitution/path-prefix/merge/pull/http-push/remote-ext/in-wrapper/var-dashed; c4
count/parameters/env/export/exec-path/config-global/config-system; c5 echo-pipe/herestring/printf0; c6 flock/busybox/non-wrapper;
s5 redirect head; c8 subtree/svn/p4/cvs/receive-pack/remote-ext; keywords if/for/!/{; w-glob, w-brace; taint two-vars, wrapped,
shell-c, env-S; unknown option before the verb): `blocked in both auto and admin: 67 of 67`.

Mutation controls for the new rules (script `.../scratchpad/mutate2.py`, each a one-line change, restored after; run on the two
new test files with `-x`): N1 redirect handling off, N2 `--attr-source` out, N3 check only without a blocked pattern, N4 return at
the first git word, N5 brace command word off, N6 `eval` off, N7 continuation not joined, N8 `env -S<v>` off, N9 dashed off, N10 env
alias risk off, N11 `xargs git` off, N12 `subtree` out, N13 unknown option not a doubt, N14 `SHELL_KEYWORDS` empty, N15 error not a
block, N16 admin scan doubt off, N17 admin dashed off, N18 admin write-count cross-check off, N19 tainted command word off, N20 URL
not resolved, N21 SL6 back to `replace`, N22 SL7 any option allowed, N23 nonliteral word then publish verb off, N24 `bash -c`
recursion off, N25 admin wording branch, N26 `DATA_HEADS` off, N27 own-remote ROOT base off, N28 same-common-dir off: all RED
(N13, N16, N17, N18 and N28 first survived, then got the tests `iii-unknown-option`, the admin cross-check tests and the
no-origin test and turned red). `hidden_git_verb` returning False: `296 failed, 496 passed, 5 skipped`. The first run's M2 to M15
that still apply (`--message`, brace, glob, `send-pack`, own-origin, slot 2b verb allowlist, `invokes_test_runner`, `--cleanup`,
`--file`, `timeout`, abbreviation, short run) are RED again; the rest (M1, M8, M13, M16-M19) target code that was rewritten and are
covered by N-set.

**Not done** (fix round): real push witness for the fix-round shapes: run by the user outside an [auto] session (!bash
/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/lab_t296_push.sh).
The script was written, syntax-checked with `bash -n`, and not run. Left as documented limits in `docs/claude-md/tracks.md`
(Admin tag, Known limits), with examples, as follow-up work: a shell fed by a heredoc, here-string or pipe (`bash <<'E'`,
`echo 'git push origin b' | sh`; overlaps T294); `$(echo 'git push …')` and backtick command substitution that builds git
from data (S4b); `su -c`, `script -c`, `busybox sh -c`; `g=git\ push; $g origin x` word splitting (bash only); `$g $v origin b`
with the variables set outside the command; `GIT_CONFIG_*` set in the profile; the own-remote rule's trust in the starting
directory.

**Fix round 3 (second adversarial review: 45300 fuzz candidates against a stand-in `git`, 11 classes).** Decision (Supervisor,
logged): the gate guards against an accident, not against a hostile repo or a hostile agent (`docs/claude-md/tracks.md`), so the
plain shapes and the false positives are fixed and the deliberate obfuscation classes are documented limits. Test first: the new
shapes (`R3_BLOCKED`, `R3_BENIGN`, premise shapes in `test_gate_hidden_verbs.py`) run against the hook of `664c2f00`:
`191 failed, 1005 passed, 5 skipped`; the first red capture (before the fuzz-driven shapes were added) was `164 failed`.

| Item | Cause in the code | Fix | Red on `664c2f00` | Green now |
|------|-------------------|-----|-------------------|-----------|
| A `>|` read as a pipe | `shlex` returns `>|` as one token; it was neither a redirect nor a separator that kept the verb | one operator at a time out of a punctuation run (`OPERATOR_PIECE`); anything with `<` or `>` is a redirect | `git >|/dev/null push origin b`, `merge`, `>| /dev/null`, `git log | git >|…`, admin `other`, `>>|`: allowed in `[auto]` and `[admin]` (6 of 11 `a-*` shapes; `<>`, `>&`, `<&`, `&>>`, `2>|` were already read) | 38 of 38 spec shapes blocked in both |
| E empty string vanishes | `''` is the empty set, a subset of the punctuation set, so it ended the simple command | `token and set(token) <= SHELL_PUNCTUATION`; an empty token is a word | `git -C '' "push"` and 13 more (`'push'`, `pu\sh`, `"merge"`, `"p"ush`, `$'push'`, `-c`, `--namespace`, `--work-tree`, `--git-dir`, `--super-prefix`, `--attr-source`, `env git -C ''`): allowed | blocked |
| G `xargs` not first | the doubt needed `words[0] == "xargs"` | the doubt needs an `xargs` word before a git word with no verb | `| env xargs git` and 11 more wrappers (`nice sudo time command nohup timeout exec stdbuf setsid flock busybox`): allowed | blocked |
| FP `man git-push` | a dashed name counted as a git word in any position | a dashed name counts only in a command position (first word, after a wrapper, after `find -exec`) | 6 of 6 blocked (`man git-push`, `-merge`, `-pull`, `git help git-push`, `which git-push`, `ls /usr/lib/git-core/git-push`) | allowed |
| FP `$DOCKER push img` | a variable head plus a publishing word was a doubt | a variable head is a doubt only when the command sets the name, the head says git (`$GIT`, `${G:-git}`, `g${E}it`), the head globs to git (`gi?`), a brace expansion, or `-c` follows; a glob or backtick head with a publishing word stays a doubt | 5 of 5 blocked (`$DOCKER push`, `"$DOCKER" pull`, `$PY tool.py merge a b`, `$PY -m pip push`, `$SCRIPT merge-reports`) | allowed; `g=git; $g push origin b` still blocked |
| FP `GIT_CONFIG_GLOBAL=/dev/null git status` | an env-risk name plus a git word was always a doubt | a doubt when `GIT_CONFIG_COUNT` or `GIT_CONFIG_PARAMETERS` has a value, or any git verb is not `status log diff show rev-parse`; the existing alias shapes stay blocked | 3 of 3 blocked (`GIT_CONFIG_GLOBAL`, `GIT_EXEC_PATH`, `GIT_CONFIG_PARAMETERS=`) | allowed |
| Cheap rule `$'…'` | `shlex` reads `$'git'` as `$git` and `\'` in `$'…'` as the end of the quote | `_mark_ansi_quotes` marks a `$'…'` or `$"…"` the shell reads (not one inside another quote); in a simple command it is a doubt next to a publishing verb, a brace expansion, a hex or octal escape or a git verb outside `add commit status log diff show`, and always in a `-c` string; an ANSI-C span with `\'` is a doubt | 6 of 6 (`$'git' $'push'`, `$'git-push'`, `$'git-pu\x73h'`, `echo $'\'' ; git "push" …`, `bash -c $'git pu\\sh …'`, `sh -c $'git \x70ush …'`): allowed | blocked; the benign corpus has no false positive (`git commit -m $'title\n\nbody'`, `cut -d $'\t'`, `tr -d $'\r'`, `git commit -m "costs 5$"`) |
| Added after the fuzz run | `function f { git push; }`, a backtick span with an odd number of quotes (`echo \`echo '\` ; git push`), hex-escaped ANSI heads, `gi?` heads | `function` body skip, odd-quote backtick doubt, `ANSI_ESCAPE`, `fnmatch("git", head)`, dashed verb with odd characters is a doubt | `z-*` shapes (15) in `R3_BLOCKED` | blocked |

Gate verdicts at HEAD (2026-11-09, the repo's `gate` fixture through the real `main()`, nothing run): the 38 shapes of the
Supervisor's list for A, E, G and the cheap rule, plus the alias and `g=git` controls: `blocked in [auto]: 38 of 38, in
[admin]: 38 of 38, with no tag: 0 of 38`. At `664c2f00`: `2 of 38` (the two controls). The 29 benign commands of the false-positive
and earlier-corpus lists: `0 of 29` blocked now; `14 of 29` at `664c2f00`.

Real shell premise (stand-in `git` that only records its arguments, bash and zsh, nothing pushed): 11 new shapes in
`_stand_in_shapes` (`r3-*`: `>|`, `2>|`, `-C ''`, `-c ''`, `env`, `nice` and `time xargs git`, `$'git' $'push'`,
`$'git-pu\x73h'`, `echo $'\'' ; git "push" …`, `bash -c $'git pu\\sh …'`) reach git with the verb in both shells.

Fuzz (the reviewer's `lib/fuzz.py`, seeds 21 22 31 32 33, 7000 candidates each, oracle = the same command in bash and zsh against the
stand-in; scratchpad `rev296b/`). Publishes the gate allowed in `[auto]` (oracle saw a publishing verb), HEAD `664c2f00` then now:
seed 21: 564 -> 29; 22: 559 -> 30; 31: 570 -> 24; 32: 570 -> 32; 33: 585 -> 32; total 2848 -> 147. Candidates allowed in `[auto]`:
6507 -> 2268. `[admin]`: 2 per seed before and after (the legitimate admin branch pushes the generator contains). Of the 147, 133
stand behind an unknown wrapper (`strace`, `busybox`, `flock`, `setsid`, `builtin`), 8 are a `\$` or a backslash line break inside a
double-quoted `-c` string, 6 are other deliberate shapes; all are documented limits. The first intermediate run showed the variable-head
change opening `$'\x67it' push` (hex heads) and `${G:-git}`; the `ANSI_ESCAPE` and head-says-git rules closed them.

Mutation controls (each a one-pattern change in `pre_bash_block_unsafe_merge.py`, `git diff --stat -- <file>` non-empty, run on
`test_gate_hidden_verbs.py` selection `r3 or premise or r2_limit or row1_unit or r2_unit`, restored with `git checkout --`; script
`.../scratchpad/mutate3.py`): A `>|` out of `OPERATOR_PIECE`: 21 failed; E empty token is punctuation: 39; G xargs rule off: 39; D dashed
in an argument counts: 18; V variable head + publish is a doubt again: 17; N command-set variable not a doubt: 14; R env read-only
exemption off: 15; Y `GIT_CONFIG_COUNT=<value>` not an alias: 6; Q2 hex escape off: 3; Q3 unbalanced ANSI-C off: 6; Q4 odd-quote
backtick off: 6; Q6 ANSI mark not set: 6; F function body off: 3; X `find -exec` off: 3; H head-says-git off: 6. Four survived at first
(Q1 ANSI next to a non-safe git verb, Q5 ANSI `-c` string, H2 glob head, S dashed verb with odd characters) and got the tests
`z-ansi-alias-verb`, `z-ansi-c-string`, `z-glob-head-alias`, `z-dashed-odd-chars`: Q1 3 failed, Q5 3, H2 3, S 3, all red.

Tests that had to change (the Supervisor's decision moves them): the three `$g …` shapes of `HIDDEN_MORE` use `$GIT` (an unset `$g` is
data); `c4-exec-path`, `c4-config-global`, `c4-config-system` use a write verb (`git x`) because `GIT_EXEC_PATH=… git status` is
allowed again; `test_r2_limit_a_variable_set_outside_the_command_is_not_followed` also pins `$g push origin b` as allowed.

Documented limits added to `docs/claude-md/tracks.md` (Admin tag, What it does not see): an unknown wrapper before a hidden word
(`flock /tmp/l $'git' push origin b`, `strace -f {git,} push origin`, `taskset 1 bash -c 'git "push" origin b'`, `find . -exec
$'git' push origin b \;`, `busybox env $'git' push`, `flock /tmp/l git-push origin b`), `g=git; flock /tmp/l $g push origin b`,
exotic `env -S` (`env -S'git' push origin b`, `env -S "git\_push\_origin\_b"`, `env -vS 'git "push" b'`), a shell alias, `${G:-git}`,
`g${E}it` and a glob after an unknown wrapper, a `\$` inside a double-quoted `-c` string; and, in the trace-gate list (now "Ten
more limits", it held ten), the `invokes_test_runner` quote desync `echo $'\' ; pytest ; \''` (older than `bc5ccc34`). `v=push; $'git'
"$v"`, `g${E}it $'push' origin b` and `${G:-git} ${V:-push} origin b` are closed by the new rules and are no longer limits.

**Not done** (fix round 3): follow-up: second-round review found 11 classes; round 3 fixed A, E, G and 3 false positives; the rest are
documented limits. Still open: the real push witness for the shapes of rounds 2 and 3 (run by the user outside an `[auto]` session).

**Disclosure.** Before the no-push rule reached this run, the premise tests of the tests-first commit (and one `-k` selection
that ran them again in a throwaway `git worktree` of that commit) ran real `git push` commands into throwaway bare remotes under
pytest's temporary directories, from `pytest` and not from a Bash call that names push. No real remote was touched. They were
replaced by stand-in tests in commit `49dfedd4`; no later run pushes.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08 at HEAD `bc5ccc34`, before any implementation commit; the unchanged
gate, the repo's own `gate` fixture with a passed auto verify of T900, driven through `main()` with no
tag, a typed `[auto]` request and a typed `[admin]` request; then the same command line run for real
in `bash -c` and `zsh -c` inside a throwaway clone with a throwaway bare remote under pytest's tmp dir,
`HOME` isolated). Script: the Supervisor-scratchpad file `capture_t296.py` (not in the repo). A
`real push landed` of True means `refs/heads/feat/t900-x` exists on the bare remote afterwards. The
last line is the `send-pack` form, run with the bare remote at `../origin.git`:

```
2026-11-08T15:25:31Z  'v=push; git $v origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'g=git; $g push origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'v=pu; git ${v}sh origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'git {p..p}ush origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  "git $'push' origin feat/t900-x"
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  "$'git' push origin feat/t900-x"
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'env -i git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'timeout 20 git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'nice git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'bash -c \'git "push" origin feat/t900-x\''
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'git send-pack ../origin.git feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
```
All 11 forms: ALLOWED by the gate in all three modes, and the push landed in both shells.

Tests written first, run against the unchanged hooks (2026-11-08T15:30:30Z, HEAD `bc5ccc34` plus the
two new test files, no implementation commit):

```
$ python3 -m pytest .claude/hooks/tests/test_gate_hidden_verbs.py .claude/hooks/tests/test_slot2b_brace_glob.py -q -p no:cacheprovider
114 failed, 268 passed
  failed by test (count): hidden form flagged (unit) 34, gate blocks each hidden form in [auto]/[admin] 22,
  block names its reason 3, merge options with a value 8, real repo + merge.defaultToUpstream 1,
  plain branch still the target (--message) 1, slot 2b brace/glob not filed 12, backslash mention
  not a test run (trace gate) 5, backslash mention (slot 2b + gate) 3, continuation joins a word 1,
  continuation cannot glue a path 1, real runs still count (py\<nl>test) 1, branch move not filed 5,
  clone with another origin refused 1, --output/--ext-diff reason 3, rev-parse doc 1, known-limits
  text 2, hidden-verb limit text 1, corpus merge sources 6, corpus test-run answers 4
  passed (the guards that must hold before and after): ordinary [auto]/[admin] commands, [admin]
  push/merge forms, no-tag behaviour, quoted globs and plain runs still filed, the old corpus answers
```

**BEFORE note (resume)**: the capture above was taken by the first agent run on 2026-11-08 against
base commit `bc5ccc34`, before any implementation commit; it is kept as it is. The Supervisor
scratchpad script `capture_t296.py` is gone, so the AFTER run below uses a scratch script of the same
shape (the repo's `gate` fixture, the real `main()`, a throwaway repo with a bare remote `../origin.git`,
`HOME` and git config isolated), kept outside the repo.

**AFTER** (2026-11-09, HEAD `7503935d`; same 11 forms, gate verdict per mode, then the same command
line run for real in `bash -c` and `zsh -c` in the throwaway worktree: first with no gate (control),
then only if the `[admin]` gate allowed it; "landed" means `refs/heads/feat/t900-x` exists on the bare
remote afterwards):

```
2026-11-09T02:28:34Z  'v=push; git $v origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'g=git; $g push origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'v=pu; git ${v}sh origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'git {p..p}ush origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  "git $'push' origin feat/t900-x"
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  "$'git' push origin feat/t900-x"
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'env -i git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'timeout 20 git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'nice git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'bash -c \'git "push" origin feat/t900-x\''
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'git send-pack ../origin.git feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
```

Tests that were red now pass (2026-11-09): `python3 -m pytest .claude/hooks/tests/test_gate_hidden_verbs.py .claude/hooks/tests/test_slot2b_brace_glob.py -q -p no:cacheprovider` -> `414 passed in 5.76s`.
With no tag the 11 forms stay ALLOWED on purpose: the hidden-verb check is an auto-mode rule
(`hidden_git_verb`, requirement (a) says "under `[auto]` and `[admin]`"). The guide's AC 1 phrase "still
blocked with no tag" does not match that requirement text or the gate's design; the tests pin "no tag, no
change" (`test_row1_with_no_tag_the_hidden_forms_behave_as_before`). The Supervisor may decide otherwise.

**DELTA**: Under `[auto]` and `[admin]` the gate now refuses all 11 hidden-verb forms that used to push for real, a `git merge` option value is no longer read as the branch, and slot 2b no longer files a call whose brace or glob reaches outside the worktree.

**WITNESS**: `memory/event-trace/T296.jsonl` (hash-chained, written by the trace hook, not by the agent): the first run's spawn at 2026-11-08T15:19:03Z, this resume's Bash calls on 2026-11-09 (the 19 mutation runs, the full suite and the AFTER capture, last record 2026-11-09T02:28:36Z). The Supervisor confirms it from that file at Stage 4.
