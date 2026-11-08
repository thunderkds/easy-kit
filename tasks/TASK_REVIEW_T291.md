# TASK_REVIEW — T291: Merge gate counts a test run that has interpreter flags (`python3 -B -m pytest`)

> Sibling of `tasks/TASK_GUIDE_T291.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_invokes_test_runner_flags.py` (AC 1: 15 positives + trace test; AC 2: 32 negatives, 46 single-letter flags, 3 trace tests; AC 3: 26 old positives, 17 old negatives, non-string). Red on `eb85573c` code: `17 failed, 72 passed` (2026-11-08T15:51:35+07:00). Green after the Stage 4 round: `141 passed`. AC 4: `test_merge_gate_guard.py::test_the_allowlist_names_the_tasks_that_own_rules_in_the_gate` repointed to include T291. |
| Verification command run | ☑ pass | `cd wt-t291 && python3 -m pytest .claude/hooks/tests/test_invokes_test_runner_flags.py -q -p no:cacheprovider` -> `135 passed in 0.09s` (2026-11-08T15:52:32+07:00). Full suite `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4298 passed, 25 subtests passed in 269.96s (0:04:29)`. |
| Negative cases hold | ☑ pass | Mutation controls, each with a non-empty `git diff --stat` (`pre_bash_block_unsafe_merge.py | 2 +-`), run with `python3 -B`, restored by `git checkout` after: M1 `INTERPRETER_FLAGS = r""` (flag group removed) -> `17 failed, 72 passed`; M2 group `-\w+(?:\s+\w+)?` (any `-X dev` token) -> `10 failed, 79 passed` (incl. `python3 -B -c 'x' -m pytest`, the mention trace test); M3 `(?-i:` dropped (IGNORECASE widens to `-b -S -i`) -> `4 failed, 85 passed`; M4 letter `X` added to the class -> first run `89 passed` (SURVIVED), test `test_ac2_no_other_single_letter_flag_is_on_the_list` added, rerun -> `1 failed, 134 passed` (`[X]`); M5 letter `m` added -> `1 failed, 134 passed` (`[m]`). Working tree clean after the last restore. Stage 4 round (3 P3 test gaps, 6 negatives added: `python3 -B-m pytest`, `python3-m pytest`, `python3-B -m pytest`, `python3 -B-B -m pytest`, `/usr/bin/python3 -B -m pytest`, `python3.12 -B -m pytest`; all False on the code before the test change): M6 `\s+` -> `\s*` before `-m` -> `2 failed, 139 passed` (`[python3 -B-m pytest]`, `[python3-m pytest]`); M7 `\s+` -> `\s*` before each flag -> `2 failed, 139 passed` (`[python3-B -m pytest]`, `[python3 -B-B -m pytest]`); M8 head `python3?` -> `\S*python[\d.]*` -> `2 failed, 139 passed` (`[/usr/bin/python3 -B -m pytest]`, `[python3.12 -B -m pytest]`). Each had a non-empty `git diff --stat` (`pre_bash_block_unsafe_merge.py | 2 +-`), ran with `python3 -B`, and was restored by `git checkout`. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Independent Stage 4 code and security review (read-only, 2026-11-08): no P0, P1 or P2; 3 P3 test gaps (closed in 19e06549, mutants M6-M8 red); 3 theoretical P3 notes (NBSP and CR whitespace, pipe and heredoc forms, `unittest.mock`) that exist on main for the unflagged form. Checked: differential against main on about 100 hand-made and 400,000 random commands (0 regressions, 5 widenings, all intended), ReDoS timings under 10 ms on 150,000-char inputs, `-O` does not pass vacuously. Reviewed: `pre_bash_block_unsafe_merge.py`, the new test file, `merge_gate_guard.py` and its pin test. Skipped: unrelated hooks |
| Full smoke suite still green (no regression) | ☑ pass | `4298 passed, 25 subtests passed in 269.96s` |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: 8-line regex change; the independent review and the 400,000-command differential cover it |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T15:50:39+07:00, before any implementation commit, on `eb85573c`; the hook is loaded with its bare `main()` call stripped, as `test_merge_gate_t210.py` does):

```
$ python3 before.py   # calls m.invokes_test_runner(c) for each command
2026-11-08T15:50:39.611214+07:00
'python3 -B -m pytest x.py' -> False
'python3 -m pytest x.py' -> True
'python3 -u -B -m unittest' -> False
'python -I -m pytest' -> False
'py -B -m pytest' -> False
```

**AFTER** (same loader and commands, commit `99ccb29e` + test commit; 2026-11-08T15:52):

```
$ python3 -m pytest .claude/hooks/tests/test_invokes_test_runner_flags.py -q -p no:cacheprovider
135 passed in 0.09s
```
Per-command results on the new code, from the test corpus: `python3 -B -m pytest x.py`, `python3 -u -B -m unittest`, `python -I -m pytest`, `py -B -m pytest` -> counted; `python3 -X dev -m pytest`, `python3 -B script.py`, `python3 -B -m json.tool`, `echo "python3 -B -m pytest"` -> not counted.

**DELTA**: A task whose tests ran as `python3 -B -m pytest` now passes the merge gate's test-run check without one extra run without `-B`.

**WITNESS**: `memory/event-trace/T291.jsonl` holds the implementer's calls and the Stage 4 reviewer's hand-back. Last targeted run in `wt-t291`: `161 passed` (2026-11-08T17:06+07:00); full suite `4298 passed` before the last 6 test strings. The hook-written verify row follows from the auto verify run.

---

## Stage 4 self-review (implementer; the Supervisor runs the independent reviews)

- Change: one new constant `INTERPRETER_FLAGS` and one concatenation in `TEST_INVOCATION_PATTERN`; the other alternatives are untouched (diff is 7 added lines, 1 changed).
- Fail closed: the list is `-B -u -O -s -E -I`, alone or in a run (`-uB`); it is case exact through `(?-i:...)` because the pattern is IGNORECASE (M3 shows the widening). A flag with an argument (`-X dev`, `-W error`) or `-c`, `-m` of another module, a path, a quoted or `echo`ed mention all stay uncounted. `-Bx`, `-mpytest`, `--` and `-` do not match.
- ReDoS: 20000 repeated `-B ` tokens, 5000 `-BBBBBBBB ` tokens and one 100000-letter token each returned in under 6 ms.
- Consistency: `lib/task_context.py` `PYTHON_FLAGS` already holds the same six flags (`frozenset({"-B", "-u", "-O", "-s", "-E", "-I"})`), so the attribution hook and the gate now agree on the list.
- Stale text (LR-0005): the only repo text that says `-B` runs do not count is `memory/learnings.md:3067-3068` (the 2026-11-08 entry). It is under `memory/**`, which this task must not edit; the Supervisor should mark it fixed by T291. No doc under `docs/`, `skills/`, `agents/`, `templates/`, `site/` or `README.md` says it.
- Pin tests (LR-0004): `test_merge_gate_t210.py`, `test_quoted_spans_t099.py`, `test_stop_attribution_t287.py` pass unchanged; `test_merge_gate_guard.py` pins the `AUTHORISED_TASKS` tuple and required the T291 repoint.
- Tripwire: `T291` is added to `AUTHORISED_TASKS` with its rule comment in `.claude/hooks/tests/merge_gate_guard.py`. **The Supervisor must sign this line off at Stage 4.**

- Stage 4 round: three P3 test gaps closed (M6-M8 in the Negative cases row). Final run, plain `python3 -m pytest` on the new file and `test_merge_gate_guard.py`: `161 passed in 0.37s` (141 + 20 guard tests, 2026-11-08T17:06:15+07:00); `merge_gate_guard.py` not touched in this round.
