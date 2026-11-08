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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_heredoc_quoted_marker.py` (136 tests): AC 1 gate tests x3 modes (no tag, `[auto]`, `[admin]`) for the four hidden shapes plus five more, with a marker-less control per mode; AC 2 real-heredoc forms (unit and gate); AC 3 corpus of 29 commands against a frozen copy of the old function; AC 4 doubt cases; premise tests that run bash and zsh in throwaway repos. `python3 -m pytest .claude/hooks/tests/test_heredoc_quoted_marker.py -q` -> `136 passed in 1.62s` |
| Verification command run | ☑ pass | at `6756099a`, 2026-11-08T15:30Z, tree clean: `python3 -m pytest .claude/hooks/tests -q -k "heredoc or shell_data or merge"` -> `675 passed, 1883 deselected in 13.76s`; `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4518 passed, 25 subtests passed in 270.87s` |
| Negative cases hold | ☑ pass | Red against the prior content: the new file on `bc5ccc34` gave `58 failed, 70 passed` (see BEFORE). 13 mutation controls on `shell_data.py`, each with `git diff --stat` = 1 file changed (M13: 14 insertions), each restored by `git checkout`, run as `python3 -B -m pytest <file>`: M1 double-quote tracking off -> 15 red; M2 single-quote skip off -> 7 red; M3 comment skip off -> 8 red; M4 backslash skip off -> 8 red; M5 context stack ignored at `<<` -> 7 red; M6 ANSI-C quote branch off -> 4 red; M7 `((` frame off -> 1 red; M8 pending kept across a newline in a substitution -> 1 red; M9 `$(` and `${` frames off -> 7 red; M10 backtick frame off -> 1 red; M11 `<(` frame off -> 1 red; M12 closers never pop -> 2 red; M13 scanner strips every `<<` (the old regex search put back) -> 58 red, including all 24 AC 1 gate tests. Differential fuzz against real shells (scratchpad `t294/fuzz.py`, 6000 random commands x bash and zsh per seed): old function hid a line the shell ran in 72 of 6000 runs (seed 1); new function 0 in 6 x 6000 (seeds 1-6) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `strip_heredoc_bodies` and its 7 call sites (listed below), the heredoc tests of 9 suites run in the full suite, `docs/claude-md/tracks.md`. Not reviewed: the merge gate's own logic (`pre_bash_block_unsafe_merge.py` is unchanged, so `merge_gate_guard.AUTHORISED_TASKS` is unchanged), `strip_quoted_spans`, `task_context.py` (own allowlist, does not call the function). `code-review` and `security-review` skills not run by this agent: left to the Supervisor's Stage 4 |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` on a clean tree at `6756099a` -> `4518 passed, 25 subtests passed in 270.87s (0:04:30)` |
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

**AFTER** (2026-11-08T15:30:47Z on `6756099a`, the same driver, nothing else changed):

```
DRIVER double-quoted      no-tag=BLOCKED [auto]=BLOCKED.
DRIVER single-quoted      no-tag=BLOCKED [auto]=BLOCKED.
DRIVER after-comment      no-tag=BLOCKED [auto]=BLOCKED.
DRIVER after-backslash    no-tag=BLOCKED [auto]=BLOCKED.
DRIVER no-marker-control  no-tag=BLOCKED [auto]=BLOCKED.
DRIVER-ADMIN double-quoted      [admin]=BLOCKED.
DRIVER-ADMIN single-quoted      [admin]=BLOCKED.
DRIVER-ADMIN after-comment      [admin]=BLOCKED.
DRIVER-ADMIN after-backslash    [admin]=BLOCKED.
DRIVER-ADMIN no-marker-control  [admin]=BLOCKED.
```

The real hook as a subprocess in this worktree (stdin JSON, no test fixture):
`echo "<<EOF"` / `git push --force origin main` / `EOF` -> `BLOCK: [hook:pre_bash] Pipeline gate failed — cannot push/merge:`;
`cat <<EOF` / `git push --force origin main` / `EOF` -> allowed (no output).

**DELTA**: A `<<WORD` inside quotes, after `#` or after a backslash no longer makes the hook drop the lines after it, so a
force push written after such a marker is blocked in every mode; a real heredoc body is still treated as data.

**WITNESS**: [left for the Supervisor: derive from `memory/event-trace/T294.jsonl`. This agent ran the BEFORE capture at
2026-11-08T15:24Z and the AFTER capture at 15:30Z]

## Callers of `strip_heredoc_bodies` (AC 5)

The function now returns the input unchanged, or with fewer spans removed, for every command where it differed before; it never removes
more. So every caller sees equal or more text. None gets looser; the direction per caller:

| Caller | Use | Effect |
|---|---|---|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` `main()` (about line 1765) | `BLOCKED_PATTERNS` and `AUTO_MODE_PATTERNS` run on `strip_quoted_spans(strip_heredoc_bodies(command))` | Safer: the P1-1 fix. Also over-blocks a commit message `"$(cat <<'EOF' … git push … EOF)"` (open risk 1) |
| same file, `_command_segments` (about line 1001) | Splits a push into segments for scope and branch resolution | Safer: more text to parse; text it cannot tokenize returns `None`, which the callers treat as "cannot tell" |
| same file, `hidden_git_verb` (about line 1450) | Auto-mode block on a hidden `git` verb | Safer: a hidden verb in a formerly stripped line is now seen |
| `.claude/hooks/post_bash_memory_update.py` (line 89) | Asks for a memory pass after a push or merge | Safer in its own direction: more prompts, no lost prompt. Same open risk 1 (a prompt for a commit whose message names a push) |
| `.claude/hooks/pre_tool_sensitive_path.py` `command_tokens` (line 227) | Sensitive-path tokens | Safer: tokens in a formerly stripped line are now checked, so more asks, none fewer. A commit message body that names `.env` inside `$(cat <<EOF` now asks |
| `.claude/hooks/lib/session_work.py` `_segments` and `_bash_works` (lines 264, 312) | Whether this session worked on a task (In Progress block, T250/T293) | Safer for the block: more segments can only add "worked". Small side effect on `work_start` (T293 Debate window): a call that hides a task path behind a quoted marker now counts, so the window can start earlier |
| `scripts/token_meter.py` `bash_writes_file` (line 177), outside `.claude/hooks` | Meter heuristic for "this call wrote a file" | Same direction (more text seen, more "writes"); a metering heuristic, not a gate |
| `.claude/hooks/tests/test_quoted_spans_t099.py`, `test_merge_gate_t095.py` | Test callers | Unchanged results (in the full run) |

