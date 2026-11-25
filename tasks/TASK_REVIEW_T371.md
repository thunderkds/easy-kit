# TASK_REVIEW — T371: Under `[admin]` the sensitive-path hook approves and logs instead of asking

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
1. Took T371 after T374, stacked on T374's branch (the same hook; T363 and T374 are Done, not merged) — RULE: `docs/claude-md/tracks.md` `### Admin tag` (one `[admin]` request runs each task from Stage 0 to Stage 5; the user's request "continue [admin] 371 and 374"), and `tasks/TASK_GUIDE_T371.md` § Dependencies & Reachability ("Depends on: T363, T374")
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High row)
3. The Supervisor wrote the code, one fresh `Reviewer: T371` spawn per round (three rounds) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. The guard's own files (`PROTECTED_PATTERNS`) still ask under `[admin]`, a read included; the log lives in the anchors folder — DEBATED: Advocate 1: let the protected patterns pass too, log in the anchors folder; Advocate 2: the protected patterns still ask, log in the anchors folder (agents are denied writes there); Advocate 3: protected writes ask and reads pass, log in the anchors folder opened `O_APPEND|O_NOFOLLOW`, an unknown command is a write, a failed log line asks. Settled by a written rule: `.claude/hooks/pre_tool_sensitive_path.py:37` "Always sensitive and never approvable" (Advocate 1 named this line as the main risk of its own proposal); reads of them ask too after the security review (V1)
5. "Approve" means no decision (the normal permission flow), never `allow` — RULE: `.claude/hooks/pre_tool_sensitive_path.py:14` "Deliberately NOT `allow`"
6. Fixed every finding of rounds 1–2 (F1 P1 a pre-resume tag; F2, F6 P2 code runners and shell-built words read as reads; F3 test gaps; F4, F5 P3) and of the Supervisor's `security-review` (V1 the guard's files through a read form; V2 in-word quotes), and spawned the reviewer again after each — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires"
7. Round 2's F8 (the token check does not dequote, outside `[admin]` too) registered as T375 — RULE: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |"
8. Round 3's F9/F10 (P3 test gaps) and the Supervisor `code-review`'s P2 (the header of `.claude/sensitive-paths.txt` still says a match "asks the human first") go to T375, tests first, and T371 merges as reviewed — DEBATED: Advocate 1: fix F9/F10 now, then a fourth round and a new auto verify (LR-0003; round 3 lost the `-exec` pin round 2 had); Advocate 2: merge as reviewed, register a follow-up (P3 is optional; a later code fix needs a new reviewer); Advocate 3: merge as reviewed and add the tests to T375's line, which edits the same hook and depends on T371, written first in its red step. Settled by written rules: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |" and `docs/claude-md/pipeline-stages.md:225` "A later code fix needs a new reviewer spawn on the new commit"
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t371_admin_approval.py` — 22 passed (red first: `18 failed, 6 passed` at 2026-11-25T13:13:29Z before the change; round 1's tests `7 failed` at 13:21:16Z; round 2's test failed at 14:13:08Z, before their fixes); the 11 sensitive-path and `tracks.md` suites `260 passed`; full suite at `10469631` `60 failed, 8001 passed`, the same 60 as `main`; reviews `Reviewer: T371` round 1 FAIL (1 P1, 2 P2, 2 P3, all fixed), round 2 FAIL (1 P2, fixed), round 3 PASS (P3 only); `security-review` skill in the Supervisor session (temporary `refs/remotes/origin/HEAD` at `107969fe`, removed right after) — two findings (V1 9/10, V2 8–9/10), both fixed; `code-review` skill in the Supervisor session on `…10469631` — no P0/P1, one P2 (the list header's stale "asks the human first"), two P3, all to T375 (decision 8); real run: the reviewers' probes ran the real hook as a subprocess under a constructed `[admin]` transcript (auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass, and after T363 and T374); auto verify: ☑ pass (session 31488f0f-2295-4526-8c14-b4aaf6b545b1, commit 48503097769e7c29b7a5da22a015421f2ece959e, log .claude/verify-runs/T371-48503097769e.log); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`); T375 (the token check's dequoting, plus decision 8's tests and the list header) registered, not started
Closed: row moved to Done 2026-11-25 — auto verify pass (session 31488f0f-2295-4526-8c14-b4aaf6b545b1, commit 48503097769e7c29b7a5da22a015421f2ece959e); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t371_admin_approval.py` (11 tests, 23 subtests) |
| Verification command run | ☑ pass | 181 passed, 152 subtests passed in 22.23s (the guide's Verification Command, run in the worktree at 3b41a1d1) |
| Negative cases hold | ☑ pass (with gaps) | Mutations on a scratch copy (no repo edit): 18 of 25 turn a test red; survivors: drop `[stop]` check (M3), `[ticket]` as admin (M4), no session-tag read (M23), `git push` in READ_ONLY_GIT (M20), dir/file mode (M21/M22), origin check in lib (M18, double-guarded). See Findings F1, F3. |
| verify | ☑ pass | auto-run by hook, session 31488f0f-2295-4526-8c14-b4aaf6b545b1, commit 48503097769e7c29b7a5da22a015421f2ece959e, log .claude/verify-runs/T371-48503097769e.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Range fix/t374-folder-rule-followups...3b41a1d1: hook, test, tracks.md; read lib/auto_mode.py tag readers and the merge gate's reading (pre_bash_block_unsafe_merge.py:2754-2785). Skipped: unrelated hooks. |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression (Supervisor, at `10469631`): `60 failed, 8001 passed, 24 skipped` — the same 60 failures as the clean `main` worktree (`60 failed, 7943 passed, 24 skipped`). The round-1 run at `97a3678d` had one extra timing test (`test_auto_verify_skip_pass.py::test_ac3_one_path_outside_the_list_and_a_skip_answer_stays_blocked[docs/claude-md/tracks.md]`), passing alone (`19 passed`) |
| **Companion score (easy-verifier)** | ☑ N/A | Not run. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |


## Review findings (code-review, P0-P3, confidence >= 75)

Verdict: **FAIL** (one P1).

| # | Sev | Conf | Where | Finding | One-line fix |
|---|-----|------|-------|---------|--------------|
| F1 | P1 | 90 | `.claude/hooks/pre_tool_sensitive_path.py` `admin_in_force` (the fallback after `session_request`) | A stale `[admin]` holds after a resume. `session_request` returns None when the tag was typed before the resume mark (or the mark is unreadable: "trust no tag"), but the fallback `latest_request`/`admin_request` has no resume check, so the old request still counts. Probed with the real hook: a resume mark written after the tag, then a Write of `.env` -> `[admin] approved ... logged`; a mark holding `garbage` -> same. Every request that carries `[admin]` is already a session tag, so the fallback only ever adds the resume / unreadable-mark cases. | Drop the fallback: `s = auto_mode.session_request(t); return s is not None and s[0] == "admin"`; add a resume-mark test. |
| F2 | P2 | 85 | same file, `only_reads` | A call that runs code is read as a read (no log line): `GIT_EXTERNAL_DIFF=rm git diff --ext-diff config/.env` asks outside `[admin]` and passes silent under it; `git diff/log --ext-diff|--textconv` and `rg --pre CMD` likewise. `_segment_command` skips `VAR=` prefixes, so the verb is `git`. | In `only_reads`: a segment whose first word is `VAR=...` is a write; add `--ext-diff`, `--textconv`, `--pre`, `--pre-glob` to the write flags. |
| F3 | P2 | 80 | `test_t371_admin_approval.py` | Gaps (mutations that stay green): `[ticket]` as admin (M4), `[stop]` in the same request as `[admin]` (M3), the tag held over a later plain request (M23), `git push` counted as a read (M20), resume (F1), folder/file modes (M21/M22). | Add one test each (the `[ticket]`, `[stop]` + `[admin]` in one request, resume mark, `git push config/.env`, mode 0700/0600). |
| F4 | P3 | 78 | `log_admin_approval` | `os.makedirs(mode=0o700)` sets the leaf only and leaves an existing folder as is; `O_NOFOLLOW` covers the final component only, so a symlinked slug folder is followed. Agents are denied writes there only by string rules in `.claude/settings.json:162-163` (`Bash(*harness-anchors*)`), which a glob or a variable evades; the log is append-only by convention, not tamper-evident. | `os.lstat` the folder (owner = us, mode & 0o077 == 0, not a symlink) before the open; say in tracks.md that the log is advisory. |
| F5 | P3 | 75 | hook / tracks.md | "No decision" keeps the normal permission flow, so the user may still be prompted or deny; the log line says "approved" and is written before that. | Word it "not asked by the hook" or log the PostToolUse result. |

Checked and held (no finding): the hook never emits `allow` (grep: only comments; M16 turns a test red); no change outside `[admin]` (the new branch sits behind `admin_in_force`; the earlier suites pass); a tag in a tool result, a sub-agent (sidechain) prompt, a code span or a `>` quoted line asks (probed: code span, quoted line, `[ticket]`, `[auto]` after `[admin]`, `[stop]`); a write to `PROTECTED_PATTERNS` asks (M11 red, 4 tests); log failure asks (M15 red); log lines cannot be forged by a command: `json.dumps` escapes newlines, target is cut at 2000; `cat "$(rm -rf config)"`, backtick and `$()` forms, `;`, `&&`, `||`, newline, `&`, subshell and heredoc forms are all logged, not read.

## Test-by-test: the change that turns it red (scratch copy, real hook as a subprocess)

| Test | Turns red when |
|------|----------------|
| OutsideAdmin.test_ac1 | `admin_in_force` returns True (M1) |
| OutsideAdmin.test_ac6_a_later_stop | M1 (not the removal of the `[stop]` check: M3 stays green, F3) |
| UnderAdmin.test_ac2_a_write_passes_and_is_logged | `admin_in_force` False (M2); no log write (M12); `allow` emitted (M16); note without the log path (M17); `session` field dropped (M19); only_reads true for Edit/Write (M10) |
| UnderAdmin.test_ac2_destructive_bash | M2, M5 (only_reads always True), M12, M14 (O_TRUNC) |
| UnderAdmin.test_ac3_a_read_passes_with_no_log | `only_reads` always False (M6); the read check removed (M24); a read of a protected file asks (M25) |
| UnderAdmin.test_ac3_a_read_with_a_write_in_it | redirect/tee check dropped (M7); find flags (M8); `git --output` (M9); M5; M2; M12 |
| UnderAdmin.test_ac4_guards_own_files | PROTECTED check removed (M11, 4 failed) |
| UnderAdmin.test_ac5_a_log_that_cannot_be_written | log error swallowed (M15) |
| UnderAdmin.test_ac5_a_symlinked_log | `O_NOFOLLOW` dropped (M13); M15; M2; M12; M16 |
| UnderAdmin.test_ac7_the_log_only_grows | `O_APPEND` -> `O_TRUNC` (M14); M2; M5; M12; M16 |
| AdminInAToolResult.test_ac6_an_untyped_tag | M1 (the lib origin check alone, M18, stays green: `latest_request` also requires "human") |

Commands: `python3 -I /tmp/claude-1000/.../scratchpad/mut.py` (mutations), `probe.py`, `probe2.py`, `probe3.py` (read classes, resume, tags); all on scratch copies.

---

## Demonstration

**BEFORE** (2026-11-25T13:13:29Z, the new test file against T374's hook, before the first implementation commit): `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t371_admin_approval.py` printed `18 failed, 6 passed`. Under a typed `[admin]`, a Write of `.env`, `rm -rf config` (holding `.env`) and `cat config/.env` each asked, the same as outside it, and nothing was logged.

**AFTER** (branch head `10469631`): the same file printed `22 passed, 51 subtests passed`.
- Under `[admin]`, a read of a listed secret passes with no output and no log line.
- A write, delete or move passes with no decision, after one JSON line in `sensitive-admin-<session>.jsonl` (mode 0600, in a private folder) and a note asking for the report line.
- A read or a write of the guard's own files asks.
- A pre-resume tag, `[stop]`, `[ticket]` or an untyped tag approves nothing.
- A log that cannot be written asks.
- Outside `[admin]` every call asks, as before.

**DELTA**: an `[admin]` run no longer stops on a sensitive-path prompt for the user's listed files. Every write it makes there leaves a log line, and the guard's own files still stop it.

**WITNESS**: Supervisor session acceb8c1, 2026-11-25 (BEFORE red run, the per-round red runs, full-suite comparison); `Reviewer: T371`, fresh qa-expert spawns in three rounds (`3b41a1d1`, `97a3678d`, `10469631`), each running the real hook as a subprocess under constructed transcripts, with mutation runs.


---

## Round 2 (Reviewer: T371, commit 97a3678d)

Verdict: **FAIL** (one P2: a write that deletes a protected file is still read as a read, a V2 class the dequoting did not close). Round-1 F1, F2 (as probed), F4 and F5 and V1 are fixed.

Verification Command (worktree, commit 97a3678d): `191 passed, 170 subtests passed in 12.26s`. The full suite was not run.

### Round-1 findings and V1/V2, re-probed with the real hook (scratchpad probe.py, probe2.py, probe3.py, probe4-6.py)

| Item | Result |
|------|--------|
| F1 stale tag after a resume | Fixed. A resume mark after the tag, and a mark holding `garbage`: both ask. `[ticket]`, `[auto]` after `[admin]`, a code span, a quoted line: ask. A plain request after `[admin]` keeps the session tag (by design). |
| F2 code runners read as reads | Fixed for the round-1 probes: `GIT_EXTERNAL_DIFF=rm git diff ...`, `git diff --ext-diff`, `git ...`, `file -C`, `env rm -rf config`, `xargs rm`, `sh` are logged; `rg`, `file`, `git` are off the read list (M31-M33 red). `rg --pre` and `git log --output` on a non-sensitive path give no decision outside `[admin]` too (not a hit). |
| F3 test gaps | Closed for `[ticket]`/`[auto]`, the held session tag, resume, folder/file modes, symlinked folder (M4, M3, M21, M22, M26, M27 red). Still open: see survivors. |
| F4 log folder checks | Fixed: `os.lstat` of the folder (link, mode, owner). Owner check has no test (M28 survives). tracks.md now says the log is by convention. |
| F5 wording | Fixed: "not asked by the hook", `decision` field in the line. |
| V1 guard files read form | Fixed: `cat/ls/grep/head` of `.claude/sensitive-paths.txt` and `.claude/state/**`, also in a `;` chain, ask (M11 red, 7 failures). |
| V2 in-word quotes | Fixed for `-de''lete`, `-de'le'te`, `-d"elete"`, `-ex''ec`, `-o''k`, `-fpr''int`, `r''m`, `t''ee`, `\r\m`, `>''x`, `-de\lete`: all logged. NOT fixed for `$'...'`, `${x}` and `{e,}`: see F6. |
| Folder rule dequoting adds no ask on an ordinary command | Checked: 22 commands run through the round-1 hook (3b41a1d1) and this one, `rm`/`mv`/`cp`/`git rm`/`echo >`/`ls` on `build`, `node_modules`, quoted, escaped, `(build)`, globs: identical. The only differences are `rm -rf con''fig`, `con""fig`, `\config`, `conf\ig` (now ask: they are the folder `config`, correct) and `rm -rf config\ x` (asks, though the true target is the file `config x`: over-ask toward the human, rare). |

Checked and held: the hook never emits `allow` (M16 red); no change outside `[admin]` (the branch sits behind `admin_in_force`; the T374/T363/T314/T316 suites pass); log failure asks (M15 red); a log line cannot be forged by a command (`json.dumps`, target cut at 2000); a tag in a tool result, a sub-agent prompt or a quote does not count.

### Findings

| # | Sev | Conf | Where | Finding | One-line fix |
|---|-----|------|-------|---------|--------------|
| F6 | P2 | 85 | `.claude/hooks/pre_tool_sensitive_path.py` `only_reads` (the dequote at the word loop, ~line 705) | A `find` whose write flag is built by the shell is read as a read: under `[admin]` it passes silent, with no log, and deletes or writes a protected-by-pattern file. Probed (all ASK outside `[admin]`, SILENT-NO-LOG under it): `find config/.env -d$'elete'`, `-$'delete'`, `-d$"elete"`, `-$'exec' rm {} ;`, `-de${x}lete`, `-d{e,}lete` (brace expands to `-delete -dlete`), `-$'\x64elete'`. The dequote strips the quote but keeps the `$`, so the word is `-d$elete`. | In `only_reads`: a `find` (or any read verb) word that contains `$`, a backtick, `{` or `\` after the quote strip makes the call a write; or drop `find` from `READ_ONLY_COMMANDS`; add the probes above to `test_v2_f2_...`. |
| F7 | P3 | 80 | `test_t371_admin_approval.py` | Mutation survivors (test gaps, no wrong behaviour seen): M28 folder owner check dropped; M35/M36/M37 `-fprint`, `-ok`, `-fls` prefixes dropped (only `-delete`, `-exec` are tested; `-fprint`/`-ok` via prefix cover `-fprintf`, `-okdir`); M38 `return seen` -> True (empty command counts as a read); M39 the `skip_values=False` reading dropped; M41 default anchors base; M43 the note's "final report" line. | One test per survivor (a `find -fprint config/.env`, `-ok`, `-fls` call; a `chown`-ed folder is hard, so assert the check by a mock-free uid compare or accept M28). |
| F8 | P3 | 75 | `pre_tool_sensitive_path.py` hit detection (pre-existing, not this range) | `cat .claude/sens''itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt` and `find config -d$'elete'` are not a hit at all, so they pass outside `[admin]` as well. V1's "any PROTECTED_PATTERNS hit asks" cannot cover a call the hit detection misses. | Out of scope for T371; note it in the cut list / a follow-up (dequote the words in `sensitive_hits`). |

### Mutation survivors (scratch copy, 37 mutations, real hook as a subprocess; mut3.py)

Red: 29 of 37 (M1-M3, M4, M5-M17, M19, M21, M22, M26, M27, M29-M34, M40, M42). Survivors: M28, M35, M36, M37, M38, M39, M41, M43 (all F7). Mutations that undo a round-2 fix are all red: M3 (fallback back), M9 (env prefix), M11 (V1), M29 (dequote in `only_reads`), M30 (folder-rule dequote), M31-M33 (rg/file/git back on the list).
(The script prints `GREEN` for M3, M4 and M11 because its FAILED-line regex finds no names; their summary lines show failures, so they are red.)

Commands: `python3 -m pytest -q -p no:cacheprovider <the guide's seven files>` -> `191 passed, 170 subtests passed in 12.26s`; `python3 -I .../scratchpad/mut3.py`, `probe.py`, `probe2.py`, `probe3.py`, `probe4.py`, `probe5.py`, `probe6.py`, `cmp5.py` (round-1 hook against this one).


---

## Round 3 (Reviewer: T371, commit 10469631)

Verdict: **PASS** (no P0-P2). Round-2 F6 is fixed; F7 is partly closed (see survivors); F8 is T375, out of scope. Two P3 test gaps remain.

Verification Command (worktree, commit 10469631): `192 passed, 180 subtests passed in 14.60s`. The full suite was not run.

### Round-2 items re-probed with the real hook (scratchpad probe4.py, probe5.py, probe6.py, probe7.py; mut4.py)

| Item | Result |
|------|--------|
| F6 shell-built find flag | Fixed. `find config/.env -d$'elete'`, `-$'delete'`, `-d$"elete"`, `-$'exec' rm {} ;`, `-de${x}lete`, `-d{e,}lete`, `-d$(echo)elete`, `` -d`echo`elete ``, `-$'\x64elete'`, `find config/.env "$X"`, `"${A:--delete}"`, `-d"$e"lete`: all LOGGED (a write), none silent. The change is in `only_reads` only: any word with `$`, a backtick or `{` (after the quote strip) makes the segment a write. Over-reach (a read with `$HOME` or `{a,b}` now logs instead of passing) goes toward a log line, not an ask, and only under `[admin]`. |
| F7 survivors | `-fprint`, `-fls` (M35, M37) and the `-ok` / `-exec` prefixes are now red or double-guarded; survivors listed below. |
| Any write read as a read | None found. Still silent under `[admin]`, all because the hit detection misses the call outside `[admin]` too (the F8 class, T375): `find config/.env$IFS-delete`, `find config/.env!-delete`, `cat .claude/sens''itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt`. Probed outside `[admin]`: `find config/.env$IFS-delete` is silent there as well, so no `[admin]` regression. |
| `[admin]` counting when the user did not type it | None. `admin_in_force` is `auto_mode.session_request` only; the earlier probes (tool result, sidechain, `[ticket]`, `[auto]`, code span, quote, resume mark, `garbage` mark) and tests `AdminInAToolResult`, `test_f3_*` still pass. Round 3 did not touch it. |
| Guard-file call that passes | None: `cat/ls/grep/head` of `.claude/sensitive-paths.txt`, `.claude/state/*`, and a `;` chain all ASK (probe4). The in-word-quote forms are not a hit at all (F8/T375). |
| New ask outside `[admin]` | None. The range 97a3678d..10469631 changes `only_reads` (called only after `admin_in_force`) plus a docstring and 12 test lines; `folder_hits` and `sensitive_hits` are byte-identical to round 2, whose round-1 comparison (cmp5.py) showed no new ask on ordinary commands. |

### Findings

| # | Sev | Conf | Where | Finding | One-line fix |
|---|-----|------|-------|---------|--------------|
| F9 | P3 | 80 | `test_t371_admin_approval.py` `test_r2_shell_built_words_...` | Every `-exec`/`-ok` probe also carries `{}`, which the new brace check catches, so the `-exec` and `-ok` prefixes in `FIND_WRITE_FLAG_PREFIXES` are no longer pinned (M34, M36 survive): `find config/.env -exec rm -rf config ;` (no braces) would still be read as a read if a prefix were dropped. Current code is right; the pin is gone. | Add `find config/.env -exec rm x ;` and `find config/.env -ok rm x ;` (no `{}`) to the test. |
| F10 | P3 | 75 | same file | Carry-over survivors with no wrong behaviour: M28 (folder owner check), M38 (`return seen` -> True, an empty command counts as a read), M39 (second `_segment_command` reading), M41 (default anchors base), M43 (the note's "final report" line), M52 (backtick in the build check: double-guarded, a backtick splits the segment first). | One test each where cheap (an empty/whitespace Bash command is not a read; the note contains "final report"); accept M28, M52. |

### Mutation survivors (scratch copy, 41 mutations: mut3.py's 37 plus 4 for the new `$`/backtick/`{` check)

Red: M1-M3, M4-M17, M19, M21, M22, M26, M27, M29-M33, M35, M37, M40, M42, M50 (check dropped), M51 (`$` dropped), M53 (`{` dropped). Survivors: M28, M34, M36, M38, M39, M41, M43, M52 (F9, F10). (The script prints `GREEN` for M3, M4 and M11 because its FAILED-line regex finds no names; their summary lines show failures, so they are red.)

Commands: `python3 -m pytest -q -p no:cacheprovider <the guide's seven files>` -> `192 passed, 180 subtests passed in 14.60s`; `python3 -I .../scratchpad/probe4.py`, `probe5.py`, `probe6.py`, `probe7.py`, `mut4.py`.
