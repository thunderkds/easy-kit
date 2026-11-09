# TASK_REVIEW — T294: A quoted heredoc marker no longer hides later lines from the merge gate

> Sibling of `tasks/TASK_GUIDE_T294.md`. Everything here is **filled by the reviewer at Stage
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
1. Accepted the implementer's wider scanner (it tracks `$(…)`, backtick and subshell context and keeps unquoted bodies that hold `$(`), although the guide's cut list says "no parser for `$(...)`" — DEBATED: accept as is, then amend the guide and run both reviews (Advocate 1: accept, amend the guide wording, run code-review and security-review; Advocate 2: accept with three conditions: both reviews, guide amended, docstring checked; Advocate 3: accept as the smallest safe thing, record the departure in this file, flag `EXPANSION_IN_BODY` as beyond the brief). Superseded by decision 3: the scanner is replaced by an allowlist, so the `$(…)` and backtick parsing is removed ⚠ decided for you — please review
2. The security review found a gate bypass the rewrite adds, so the task is not ready and goes back for one fix round — RULE: `.claude/skills/code-review/SKILL.md` § Severity Scale "P0 | Correctness bug, data loss, security hole | Yes — hard block". Supervisor check on 2026-11-09: `cat <(cat <<A` / `)` / `cat <<B` / `A` / `)` / a push line / `B` — `strip_heredoc_bodies` on `bc5ccc34` keeps the push line (visible to the gate); on this branch it strips it
3. After two independent review rounds found 12 gate bypasses (5 in round 1, 7 in round 2: `${x- #'`, a carriage return after `<<`, a zsh same-line `$(`, a `case` pattern `)`, a backslash-newline before `<<`, `x=( (cat <<A`, `${x:-(cat <<A`) while the author's seeded fuzz reported 0 hidden lines each time, the stateful scanner is replaced by an allowlist: a heredoc body is stripped only when everything before and on the header line is plain (words, balanced simple quoted atoms with no `$`, backtick or backslash inside, space or tab only as whitespace, one `<<` or `<<-` and a plain-word tag), plus exactly one nested form `<plain prefix> "$(cat <<'TAG'` … `TAG` followed at once by `)"`; any other `<<` ends all stripping in that command; a header that feeds a shell or interpreter (`bash`, `sh`, `zsh`, `source`, `eval`, `ssh`) keeps its text — DEBATED: allowlist (Advocate 1: allowlist, strip only a plain prefix and the commit form, one `break` for everything else, keep the fuzz as a keep-text oracle; Advocate 2: allowlist with four tightenings: a clean test over all text before the header, a character whitelist on the header line, one commit-form shape for any command word, no stripping when a shell consumes the body; Advocate 3: allowlist as the smallest safe thing, strip only balanced simple quoted atoms so `echo "writing notes" > n.md <<'EOF'` (pinned at `.claude/hooks/tests/test_quoted_spans_t099.py:294`) stays stripped, and generalise the commit form to any plain prefix). The cost is more over-blocking of unusual heredoc headers, which is recoverable; a bypass is not. ⚠ decided for you — please review
Checks: tests (implementer) `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — 4712 passed at `d936374c`, before the redesign; reviews security-review — 1 P0 confirmed and fixed, code-review — 4 P0 fixed, round-2 adversarial review — 7 more bypasses, redesign open; real run — pending the redesign (auto-checked, not /verify)
Memory: nothing new yet — the pass runs after the redesign
Not done: the redesign (allowlist), then a third independent review; merge (yours); auto verify: not started
Paused: auto-mode check failed — Risk High: decision 1 (`DEBATED`) is a choice — it names 2 Advocates, not exactly 3 — so it must be `DEBATED` with exactly 3 Advocates named; Risk High, but no decision was DEBATED with 3 Advocates [report 9f397879cf19]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_heredoc_quoted_marker.py` (608 tests) and `.claude/hooks/tests/test_heredoc_fuzz.py` (4 tests). AC 1: gate tests in three modes (no tag, `[auto]`, `[admin]`) for the four hidden shapes and more, with a marker-less control per mode. AC 2: real-heredoc forms (`REAL`, unit and gate), plus `OVERBLOCK` (real heredocs the allowlist does not read: the text stays, a recoverable over-block; round 3 added `$` and a backslash inside double quotes before the header). AC 3: a corpus against a frozen copy of the old function; `test_ac3_the_result_is_the_old_result_or_the_whole_command` pins that the result is never looser than the old one. AC 4: `DOUBT` shapes keep the text (round 3 added two that pin the closer of the commit form). Round 2 shapes (`BYPASS`, 18) and round 3 shapes (`ROUND3`, 35: B1-B7 and extras), each as a unit test, a gate test in three modes, and a premise test in real bash 5.3.9 and zsh 5.9 (an `echo` canary in a throwaway dir). Seeded differential fuzz. At `6e30dc83`, 2026-11-09T04:08Z: `python3 -m pytest .claude/hooks/tests/test_heredoc_quoted_marker.py -q -p no:cacheprovider` -> `608 passed in 11.58s`; `python3 -m pytest .claude/hooks/tests/test_heredoc_fuzz.py -q -p no:cacheprovider` -> `4 passed in 12.26s` |
| Verification command run | ☑ pass | at `b3561fe1` (the scanner code of the final commit; `6e30dc83` only adds tests), 2026-11-09, in the background: `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4980 passed, 25 subtests passed in 473.02s (0:07:53)` |
| Negative cases hold | ☑ pass | Red against the prior content: the new test file on `bc5ccc34` failed 58 tests in round 1 (see BEFORE). Round 3 (the allowlist): the B1-B7 shapes, red on the context-stack scanner at `bd9f1c4b`, green now (below). Seven mutation controls, one per allowlist rule, each one line of `shell_data.py` (`git diff --stat` = `1 file changed, 1 insertion(+), 1 deletion(-)`), run over both test files with `python3 -B -m pytest <both files> -q`, restored by `git checkout -- .claude/hooks/lib/shell_data.py` (`git status` clean of `shell_data.py` afterwards): R1 prefix check off (`not _is_plain(prefix)` -> `False`) -> 146 red; R2 header-line whitelist -> `[^\n]*` -> 5 red; R3 `[ \t]*` -> `\s*` -> 98 red; R4 nested-form closer check off -> 0 red at first (`610 passed`), so two `DOUBT` tests were added (`commit-form-with-a-command-after-the-terminator`, `commit-form-without-the-closing-quote`) and R4 is now 2 red (`2 failed, 610 passed`); R5 unquoted-body expansion check off -> 14 red; R6 `_feeds_a_shell` -> False -> 32 red; R7 quote atoms removed in two passes, singles first, instead of one alternation -> 4 red (the new `double-quoted-single-then-single-quoted-double` shape in `REAL`, unit and gate). Output of the run (R4 as first run, before the two tests):

```
=== R1 prefix check off
 1 file changed, 1 insertion(+), 1 deletion(-)
146 failed, 464 passed in 56.68s
=== R2 header-line whitelist -> [^\n]*
 1 file changed, 1 insertion(+), 1 deletion(-)
5 failed, 605 passed in 49.48s
=== R3 [ \t]* -> \s*
 1 file changed, 1 insertion(+), 1 deletion(-)
98 failed, 512 passed in 28.35s
=== R4 nested closer check off
 1 file changed, 1 insertion(+), 1 deletion(-)
610 passed in 24.14s
=== R5 unquoted-body expansion check off
 1 file changed, 1 insertion(+), 1 deletion(-)
14 failed, 596 passed in 31.82s
=== R6 _feeds_a_shell -> False
 1 file changed, 1 insertion(+), 1 deletion(-)
32 failed, 578 passed in 44.22s
=== R7 quote atoms in two passes (singles first)
 1 file changed, 1 insertion(+), 1 deletion(-)
4 failed, 606 passed in 39.45s
```

Mutation controls of rounds 1 and 2 (M1-M18, `Ma`-`Mf`) belonged to the replaced context-stack scanner and are in the history of this file at `4dfdc76d`. Fuzz (`.claude/hooks/tests/test_heredoc_fuzz.py`; `FUZZ_RUNS` and `FUZZ_SEED` set the size and seed; the suite runs 1500 per shell at seed 20261109): power check, the scanner of `bd9f1c4b` hid a line the shell ran in 118 of 6000 bash and 91 of 6000 zsh commands at seed 5 (the B vocabulary generator). Final scanner: 0 hidden lines at seeds 4001, 4002 and 4003, 20000 commands per shell each (bash and zsh; `2 passed` per seed, 153 s, 144 s, 139 s; output `/tmp/claude-1000/t294w/hunt3.txt`). `test_fuzz_control_the_oracle_finds_a_line_a_broken_scanner_hides` shows the oracle goes red on a scanner that strips after every `<<EOF`. `shell_data.py` size: 300 lines at `bc5ccc34`, 449 at `bd9f1c4b`, 393 at `b013651d`, 396 now (the docstring grew by 3). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `strip_heredoc_bodies` and its 7 call sites (listed below), the heredoc tests of 9 suites run in the full suite, `docs/claude-md/tracks.md`. Not reviewed: the merge gate's own logic (`pre_bash_block_unsafe_merge.py` is unchanged, so `merge_gate_guard.AUTHORISED_TASKS` is unchanged), `strip_quoted_spans`, `task_context.py` (own allowlist, does not call the function). `code-review` and `security-review` skills not run by this agent: left to the Supervisor's Stage 4 |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` at `b3561fe1` -> `4980 passed, 25 subtests passed in 473.02s (0:07:53)` |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08 15:24 UTC on `bc5ccc34`, before any implementation commit; a driver
that sends each hidden shape, `<marker line>` / `git push --force origin main` / `EOF`, through the
merge gate's real `main()` with the repo's `gate` fixture; the board has T901 In Progress and T900 Ready
for Review; admin mode has T900 auto-verified and an `[admin]` request):

```
$ python3 -m pytest scratchpad/t294/test_driver.py -q -s -k test_table      # 2026-11-08T15:24:16Z
DRIVER double-quoted      no-tag=ALLOWED [auto]=ALLOWED.
DRIVER single-quoted      no-tag=ALLOWED [auto]=ALLOWED.
DRIVER after-comment      no-tag=ALLOWED [auto]=ALLOWED.
DRIVER after-backslash    no-tag=ALLOWED [auto]=ALLOWED.
DRIVER no-marker-control  no-tag=BLOCKED [auto]=BLOCKED.
$ python3 -m pytest scratchpad/t294/test_driver.py -q -s -k test_admin      # 2026-11-08T15:24:23Z
DRIVER-ADMIN double-quoted      [admin]=ALLOWED.
DRIVER-ADMIN single-quoted      [admin]=ALLOWED.
DRIVER-ADMIN after-comment      [admin]=ALLOWED.
DRIVER-ADMIN after-backslash    [admin]=ALLOWED.
DRIVER-ADMIN no-marker-control  [admin]=BLOCKED.
```

The new tests against the old code, same commit (`python3 -m pytest .claude/hooks/tests/test_heredoc_quoted_marker.py -q`,
2026-11-08T15:23:51Z): `58 failed, 70 passed` (before the three control tests were split; every AC 1 test fails with
"the gate ALLOWED the hidden force push", and the premise tests show bash and zsh both run the push).

**AFTER** (round 3, 2026-11-09, scanner code of `b3561fe1`, scratchpad driver `/tmp/claude-1000/t294w/drive3.py`): the real hook `.claude/hooks/pre_bash_block_unsafe_merge.py` as a subprocess, stdin JSON, in a throwaway `git init` directory. The driver passes only the command text to the hook and runs no command. The push line is built in halves. 4 controls, then every shape of round 1 (8), round 2 (18) and round 3 (35) with a push-named line in place of a canary:

```
control: plain push line                             exit-ok BLOCKED  want=BLOCKED  OK
echo "<<EOF" + push line + EOF                       exit-ok BLOCKED  want=BLOCKED  OK
plain cat <<EOF with push-named body                 exit-ok allowed  want=allowed  OK
commit form with push in its body                    exit-ok allowed  want=allowed  OK
round1 after-backslash                               exit-ok BLOCKED  want=BLOCKED  OK
round1 after-comment                                 exit-ok BLOCKED  want=BLOCKED  OK
round1 ansi-c-quote                                  exit-ok BLOCKED  want=BLOCKED  OK
round1 brace-default                                 exit-ok BLOCKED  want=BLOCKED  OK
round1 double-quoted                                 exit-ok BLOCKED  want=BLOCKED  OK
round1 here-string                                   exit-ok BLOCKED  want=BLOCKED  OK
round1 quote-after-escaped-quote                     exit-ok BLOCKED  want=BLOCKED  OK
round1 single-quoted                                 exit-ok BLOCKED  want=BLOCKED  OK
round2 array-literal                                 exit-ok BLOCKED  want=BLOCKED  OK
round2 array-literal-append                          exit-ok BLOCKED  want=BLOCKED  OK
round2 array-subscript-arithmetic                    exit-ok BLOCKED  want=BLOCKED  OK
round2 array-subscript-arithmetic-spaced             exit-ok BLOCKED  want=BLOCKED  OK
round2 context-closes-on-a-case-line                 exit-ok BLOCKED  want=BLOCKED  OK
round2 context-closes-on-a-tag-with-a-suffix         exit-ok BLOCKED  want=BLOCKED  OK
round2 context-closes-on-the-tag-line                exit-ok BLOCKED  want=BLOCKED  OK
round2 context-closes-on-the-tag-line-with-a-word    exit-ok BLOCKED  want=BLOCKED  OK
round2 dollar-bracket-arithmetic                     exit-ok BLOCKED  want=BLOCKED  OK
round2 dollar-bracket-arithmetic-spaced              exit-ok BLOCKED  want=BLOCKED  OK
round2 r0-output-process-substitution                exit-ok BLOCKED  want=BLOCKED  OK
round2 r0-process-substitution                       exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-backslash-in-the-middle                   exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-quoted-in-the-middle                      exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-quoted-then-a-suffix                      exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-single-quoted-in-the-middle               exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-that-is-not-a-word                        exit-ok BLOCKED  want=BLOCKED  OK
round2 tag-with-a-quoted-suffix                      exit-ok BLOCKED  want=BLOCKED  OK
round3 b1-hash-in-brace-default                      exit-ok BLOCKED  want=BLOCKED  OK
round3 b1-hash-in-brace-default-echo                 exit-ok BLOCKED  want=BLOCKED  OK
round3 b1-hash-in-brace-default-split-dollar         exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-carriage-return-after-the-dash-marker      exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-carriage-return-after-the-marker           exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-em-space-after-the-dash-marker             exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-em-space-after-the-marker                  exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-file-separator-after-the-dash-marker       exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-file-separator-after-the-marker            exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-form-feed-after-the-dash-marker            exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-form-feed-after-the-marker                 exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-ideographic-space-after-the-dash-marker    exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-ideographic-space-after-the-marker         exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-next-line-after-the-dash-marker            exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-next-line-after-the-marker                 exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-no-break-space-after-the-dash-marker       exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-no-break-space-after-the-marker            exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-vertical-tab-after-the-dash-marker         exit-ok BLOCKED  want=BLOCKED  OK
round3 b2-vertical-tab-after-the-marker              exit-ok BLOCKED  want=BLOCKED  OK
round3 b3-header-then-a-new-substitution             exit-ok BLOCKED  want=BLOCKED  OK
round3 b3-header-then-a-new-substitution-echo        exit-ok BLOCKED  want=BLOCKED  OK
round3 b4-case-pattern-in-process-substitution       exit-ok BLOCKED  want=BLOCKED  OK
round3 b4-case-pattern-in-substitution               exit-ok BLOCKED  want=BLOCKED  OK
round3 b5-backslash-newline-before-the-marker        exit-ok BLOCKED  want=BLOCKED  OK
round3 b5-backslash-newline-colon                    exit-ok BLOCKED  want=BLOCKED  OK
round3 b5-backslash-newline-no-space                 exit-ok BLOCKED  want=BLOCKED  OK
round3 b6-array-with-a-subshell                      exit-ok BLOCKED  want=BLOCKED  OK
round3 b7-subshell-in-brace-default                  exit-ok BLOCKED  want=BLOCKED  OK
round3 commit-form-feeding-bash-c                    exit-ok BLOCKED  want=BLOCKED  OK
round3 piped-into-bash                               exit-ok BLOCKED  want=BLOCKED  OK
round3 piped-into-bash-on-the-next-line              exit-ok BLOCKED  want=BLOCKED  OK
round3 stdin-of-bash                                 exit-ok BLOCKED  want=BLOCKED  OK
round3 stdin-of-sh-dash-form                         exit-ok BLOCKED  want=BLOCKED  OK
round3 stdin-of-source                               exit-ok BLOCKED  want=BLOCKED  OK
round3 unquoted-body-joins-the-terminator            exit-ok BLOCKED  want=BLOCKED  OK
shapes checked: 61 (+4 controls); mismatches: 0
```

`echo "<<EOF"` + a push-named line + `EOF` is blocked; a plain `cat <<EOF` with a push-named body is allowed; the commit form with a push in its body is allowed; all 61 bypass shapes are blocked.

The B1-B7 shapes of round 3, each run against the scanner of `bd9f1c4b` (red: it hid the push) and against the allowlist (green: the push is kept): B1 3 shapes, B2 16 (the Unicode and control whitespace after `<<` and `<<-`), B3 2, B4 2, B5 3, B6 1, B7 1; extras: an unquoted body whose line join hides a line (1) and 6 shell-consumer shapes (`bash <<`, `| bash`, `source`, `eval`, `ssh`, the commit form feeding `bash -c`). Premise tests run each shape in real bash and zsh and show the shell runs the push.

Earlier captures (rounds 1 and 2, at `6756099a`, `bbc5665e`, `d936374c`) showed the same hook blocking the shapes of those rounds; they stay valid because the allowlist keeps every text that the earlier scanners kept (the `ROUND3`, `BYPASS` and `ALL_HIDDEN` unit tests above).


**DELTA**: A `<<WORD` inside quotes, after `#` or after a backslash no longer makes the hook drop the lines after it, so a
force push written after such a marker is blocked in every mode; a real heredoc body is still treated as data.

**WITNESS**: [left for the Supervisor: derive from `memory/event-trace/T294.jsonl`. This agent ran the BEFORE capture at
2026-11-08T15:24Z and the AFTER capture at 15:30Z]

## Callers of `strip_heredoc_bodies` (AC 5)

The function strips a body only when it can prove it is data (the allowlist). For the commands of the earlier suites its result is the old result or the whole command, never less text than before: `test_ac3_the_result_is_the_old_result_or_the_whole_command` pins that over the corpus. So all 7 callers get equal or more text, and none gets looser for text the shell runs. The shell-consumer rule and the fuzz against bash and zsh back the claim for commands outside the corpus. The cost: some real heredocs (a variable or `$(…)` before the header, a subshell) keep their body text, so a push named there is blocked (the recoverable side; the `OVERBLOCK` tests pin the list). The direction per caller:

| Caller | Use | Effect |
|---|---|---|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` `main()` (about line 1765) | `BLOCKED_PATTERNS` and `AUTO_MODE_PATTERNS` run on `strip_quoted_spans(strip_heredoc_bodies(command))` | Safer: the P1-1 fix. The kit's commit form `"$(cat <<'EOF' … EOF)"` keeps its body as data (heredoc directly inside `$(…)` is still a heredoc), so a commit message that names a push is not over-blocked |
| same file, `_command_segments` (about line 1001) | Splits a push into segments for scope and branch resolution | Safer: more text to parse; text it cannot tokenize returns `None`, which the callers treat as "cannot tell" |
| same file, `hidden_git_verb` (about line 1450) | Auto-mode block on a hidden `git` verb | Safer: a hidden verb in a formerly stripped line is now seen |
| `.claude/hooks/post_bash_memory_update.py` (line 89) | Asks for a memory pass after a push or merge | Safer in its own direction: more prompts, no lost prompt. Commit form still stripped (no extra prompt) |
| `.claude/hooks/pre_tool_sensitive_path.py` `command_tokens` (line 227) | Sensitive-path tokens | Safer: tokens in a formerly stripped line are now checked, so more asks, none fewer. The commit form stays stripped as before |
| `.claude/hooks/lib/session_work.py` `_segments` and `_bash_works` (lines 264, 312) | Whether this session worked on a task (In Progress block, T250/T293) | Safer for the block: more segments can only add "worked". Small side effect on `work_start` (T293 Debate window): a call that hides a task path behind a quoted marker now counts, so the window can start earlier |
| `scripts/token_meter.py` `bash_writes_file` (line 177), outside `.claude/hooks` | Meter heuristic for "this call wrote a file" | Same direction (more text seen, more "writes"); a metering heuristic, not a gate |
| `.claude/hooks/tests/test_quoted_spans_t099.py`, `test_merge_gate_t095.py` | Test callers | Unchanged results (in the full run) |

Round 3 changed no caller and the function keeps its signature. The allowlist keeps more text than the round 1 and 2 scanners did, so the caller list above holds.

