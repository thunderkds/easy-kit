# TASK_REVIEW — T288: Attempts log derived from the event trace

> Sibling of `tasks/TASK_GUIDE_T288.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` tag,
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_attempt_log.py` (26 tests after the Stage 4 fix round, AC 1-5; AC 6 is the doc line). Written first: before `scripts/attempt_log.py` existed, `python3 -m pytest tests/test_attempt_log.py -q` ended `ERROR tests/test_attempt_log.py - FileNotFoundError: ... scripts/attempt_log.py` / `1 error`. After the first round: `22 passed in 0.38s`; after the fix round: `26 passed`. |
| Verification command run | ☑ pass | `python3 -B -m pytest tests/test_attempt_log.py -q` -> `26 passed` (fix round). `python3 scripts/attempt_log.py derive /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/memory/event-trace/*.jsonl` -> 15 rows, exit 0 (T148 T170 T173 T190 T189 T223 T236 T236 T249 T250 T255 T267 T268 T283 T284). `python3 -B -m pytest .claude/hooks/tests/ tests/ -q` on commit 44d2e025 (after the Stage 4 fix round; the only later commit changes this review file) -> `1 failed, 3467 passed, 25 subtests passed in 226.61s`; the one failure is `tests/test_spike_report_t283.py::test_the_real_report_is_valid`: it needs `tasks/SPIKE_REPORT_T283.md`, which is on branch `feat/t283-karpathy-spikes` and is not in this worktree (`git ls-tree HEAD tasks/SPIKE_REPORT_T283.md` is empty), so it is not caused by T288. |
| Negative cases hold | ☑ pass | 8 mutations of `scripts/attempt_log.py` against commit b56bfc26, each with a non-empty `git diff --stat` (`scripts/attempt_log.py | 2 +-`, `1 file changed, 1 insertion(+), 1 deletion(-)`), each restored with `git checkout` and green again (`22 passed`). M1 step-limit regex `r"step_limit_never"`: `3 failed, 19 passed` (`test_ac1_blocked_and_step_limit_rows_only`, `test_ac1_step_limit_in_a_done_status_is_a_stopped_row`, `test_ac4_a_done_status_that_says_the_step_limit_did_not_stop_it_is_not_a_row`). M2 `BLOCKED` anywhere in the line (the spike false positive): `7 failed, 15 passed`, includes `test_ac4_ready_for_review_that_only_says_blocked_is_not_a_row`. M3 negation guard never matches: `1 failed, 21 passed`. M4 `append` without the dedupe: `2 failed, 20 passed` (`test_ac2_append_adds_only_missing_rows_and_twice_adds_nothing`, `test_ac2_cli_append_twice_leaves_the_file_unchanged`). M5 cut marker removed: `2 failed, 20 passed`. M6 `derive` dedupe removed: `1 failed, 21 passed`. M7 header not written: `1 failed, 21 passed`. M8 malformed count removed: `1 failed, 21 passed`. |
| verify | ☐ pass / ☐ fail / ☐ N/A | Not run by the implementer; the Supervisor starts the auto verify run. [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | Not reviewed by the implementer (the Supervisor runs Stage 4). Blast radius: 3 files, `scripts/attempt_log.py` (new, no importer), `tests/test_attempt_log.py` (new), one added bullet in `docs/claude-md/memory-write-protocol.md` (its two pin tests, `tests/test_memory_slice.py` and `.claude/hooks/tests/test_memory_channel_and_budget.py`, pass). No hook, no `.claude/settings.json`. |
| Full smoke suite still green (no regression) | ☑ pass | Same run as above, after the fix round: `1 failed, 3467 passed`; the failure is the T283 report test, not a regression (file absent in this worktree). |
| **Companion score (easy-verifier)** | ☑ N/A | Not run by the implementer. [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: a Python script and its tests. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T00:13:09Z in `/home/hungnguyenhuu/workspace/pets/wt-t288`, HEAD `4c076b6c`, before any implementation commit):

```
$ ls tasks/attempts.tsv scripts/attempt_log.py
ls: cannot access 'tasks/attempts.tsv': No such file or directory
ls: cannot access 'scripts/attempt_log.py': No such file or directory
exit=2
```

Real trace, read only (`/home/hungnguyenhuu/workspace/pets/personal-agentic-claude/memory/event-trace/*.jsonl`), counted with a throwaway one-off inline regex, not the new script: 295 `SubagentHandback` records; 16 have a status line that starts with `blocked` or names the step limit. They are in T148:31, T170:42, T173:94, T188:71, T189:100, T223:90, T223:92, T236:26, T236:91, T249:90, T250:88, T255:90, T267:91, T268:90, T283:95, T284:92. None of them is in a committed, derived record: there is no `tasks/attempts.tsv`.

**AFTER** (captured 2026-11-08T00:20:05Z in `/home/hungnguyenhuu/workspace/pets/wt-t288`, branch `feat/t288-attempts-tsv`, commit b56bfc26; the real trace, read only):

```
$ ls tasks/attempts.tsv scripts/attempt_log.py
ls: cannot access 'tasks/attempts.tsv': No such file or directory
scripts/attempt_log.py
$ python3 scripts/attempt_log.py derive /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/memory/event-trace/*.jsonl | wc -l
15
$ python3 scripts/attempt_log.py derive .../memory/event-trace | head -3 | cut -c1-140
2026-10-17T05:17:49.319743+00:00	T148	blocked	blocked (on AC3 only; everything else is ready for review)
2026-10-20T11:20:52.089830+00:00	T170	blocked	blocked
2026-10-26T03:18:51.215974+00:00	T173	stopped	ready-for-review, with 3 gaps listed below. The `pre_agent_step_limit` hook stopped me at its 
```

`tasks/attempts.tsv` is deliberately still absent: the Supervisor runs the first `append`. The 15 rows are the 16 of BEFORE minus T223's second handback ("The step-limit hook did not stop me this time", a negated mention, now not a row), and T188's ready-for-review "Nothing is blocked" handback is not a row (the spike's false positive). T219's "ready-for-review, with AC 3b blocked" is also not a row: the status does not start with `blocked`, and T219 is already named in `tasks/TASK_REVIEW_T219.md:87`. T190's block (found in the T188 trace) is now attributed to T190, the `Task:` line of the handback.

**DELTA**: The Supervisor can run `python3 scripts/attempt_log.py append tasks/attempts.tsv memory/event-trace` and get a committed, readable, append-only file of every blocked or stopped sub-agent run, including the step-limit stops that no committed record names today.

**WITNESS**: Derived from `/home/hungnguyenhuu/workspace/pets/personal-agentic-claude/memory/event-trace/T288.jsonl` (the common-infrastructure sub-agent's tool calls, bound by the spawn prompt's `Task ID: T288`); BEFORE was captured before commit b56bfc26. The Supervisor re-runs the Verification Command at Stage 4; the implementing agent alone is not the witness.

---

## Known limit

A handback with no `Status:` line is never a row, because AC 1 limits rows to the status line. Example: a reviewer handback that the step limit (`pre_agent_step_limit`) stopped, T266, trace `memory/event-trace/T266.jsonl` line 90. The same limit is in the docstring of `scripts/attempt_log.py`. Not fixed on purpose: a free-text search of the whole handback is what produced the spike's false positive (the word "blocked" in a done handback).

## Stage 4 fix round (2026-11-08)

Findings of the Stage 4 `code-review`: no P0, no P1, three P2, two P3. Method: each test written first and seen red (`python3 -B -m pytest tests/test_attempt_log.py -q`), then the fix. Fix commit `0ac64982`. Each mutation changes bytes of `scripts/attempt_log.py` (non-empty `git diff --stat`), is restored with `git checkout`, and the file is green again (`26 passed`).

| # | Finding | What I did | Red before the fix | Mutation control (red) |
|---|---------|------------|--------------------|------------------------|
| 1 | P2: `append` not idempotent for a status holding a character that `str.splitlines()` splits on (VT, FF, FS, GS, RS, NEL, LS, PS) | New `LINE_BREAKS` class and `_flat()`: every such character, and tab, CR, LF, becomes a space in each cell. `have` is read with `text.split("\n")`. New test `test_ac2_a_status_with_a_splitlines_separator_appends_once` (8 separators: append twice, second run `appended 0 rows`, file bytes unchanged, one row) | `FAILED test_ac2_a_status_with_a_splitlines_separator_appends_once`, `2 failed, 24 passed` | N4: `LINE_BREAKS` cut to `[\t\n\r]`: `1 failed, 25 passed` (`test_ac2_a_status_with_a_splitlines_separator_appends_once`). N3: `have = set(text.splitlines())` alone: `26 passed`. It cannot be seen by itself, because the cells are already flat; N4 is the guard that bites. `split("\n")` stays as defence in depth for a file edited by hand. |
| 2 | P2: a lone surrogate (a cut between the halves of an emoji pair, `\ud83d`) crashes `derive` with `UnicodeEncodeError` | `_flat()` repairs lone surrogates: `text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")`. New test `test_ac5_a_cut_between_the_halves_of_an_emoji_pair_does_not_crash` runs the real command (derive and two appends): exit 0, a row ending in `(cut at 300)`, no traceback | `FAILED test_ac5_a_cut_between_the_halves_of_an_emoji_pair_does_not_crash` | N2: the `encode("utf-16", "surrogatepass")` line removed: `1 failed, 25 passed` (same test) |
| 3 | P2: `test_ac3_a_cut_in_the_middle_of_an_escape_does_not_crash` cannot fail for `PARTIAL_ESCAPE` | Added `assert cell.startswith("blocked \u2014 y")` (em dash decoded) and `"\\u20" not in cell` | n/a (test strengthened; the guard was already in place) | N1: loop `for text in (raw, PARTIAL_ESCAPE.sub("", raw))` replaced by `for text in (raw,)`: `FAILED test_ac3_a_cut_in_the_middle_of_an_escape_does_not_crash`, `1 failed, 25 passed` |
| 4 | P3: the tab/newline test does not exercise `\r` | New `test_a_carriage_return_inside_the_status_line_becomes_a_space` (`blocked\rabc` gives `blocked abc`, no `\r` in the row). `\n` stays in the class: the escape `\n` ends the status line, but `\u000a` decodes to a real newline; new test `test_a_newline_escaped_as_unicode_inside_the_status_line_becomes_a_space` | both pass at once (the old code already replaced `\r` and `\n`); the mutations show they can fail | N5: `\r` removed from the class: `FAILED test_a_carriage_return_inside_the_status_line_becomes_a_space`, `1 failed, 25 passed`. N6: `\n` removed from the class: `FAILED test_a_newline_escaped_as_unicode_inside_the_status_line_becomes_a_space`, `1 failed, 25 passed` |
| 5 | P3: a reviewer handback with no `Status:` line, stopped by the step limit (T266), is not logged | Documentation only: section `## Known limit` above and the docstring of the script. No code change | n/a | n/a |
| 6 | Title line | Filled: `# TASK_REVIEW — T288: Attempts log derived from the event trace` | n/a | n/a |

The `verify` row and the companion-score row are unchanged.

