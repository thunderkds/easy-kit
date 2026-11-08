# TASK_REVIEW — T293: A Debate counts for its task only inside that task's work window

> Sibling of `tasks/TASK_GUIDE_T293.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_debate_window.py`, 21 tests in round 1 (35 after round 3; 32 after round 2: +4 trace-record, +1 no-window trace, +3 hint, +2 fallback, +1 doc pin extended), written first: `16 failed, 5 passed` on the unchanged hooks at `eb85573c` (the 5 passing are today's behaviour: AC 1 x3, AC 4 x2). AC 1: `test_ac1_*` (3). AC 2: `test_ac2_*` (5 incl. 2 parametrized). AC 3: `test_ac3_*` (6 parametrized). AC 4: `test_ac4_*` (2, with a control). AC 5: `test_ac5_*`. Window reader: `test_work_*` (4). Round 2 red run on the round-1 code: `7 failed, 25 passed`. After round 2: `32 passed in 5.65s`. After round 3: `35 passed in 7.20s` (plain `python3 -m pytest`). |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_debate_window.py -q -p no:cacheprovider` -> `35 passed in 7.20s`; `python3 -m pytest .claude/hooks/tests -q -k "debate or stop_auto or session_work"` covered by the full run below. |
| Negative cases hold | ☑ pass | Nine mutation controls (table below), each with a non-empty `git diff --stat` before its verdict; every one turns at least one test red, and the restored tree is `21 passed`. |
| verify | ☑ pass | auto-run by hook, session b8dee3fe-6b63-464d-aa8b-1bc3c631ce8e, commit a1981b74635cb7f9ac0098a0e8aed302e26525d2, log .claude/verify-runs/T293-a1981b74635c.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `session_work.py` (callers `load_work`, `worked_on`: `pre_bash_block_unsafe_merge.py`, `stop_auto_mode_check.py`, T250/T252 tests), `stop_auto_mode_check.py` (`check_task`, `main`), `tracks.md`. Skipped: the other Stop checks, the report format, the 6-hour `_untagged.jsonl` fallback (cut list). Independent Stage 4 code and security review (read-only): round 1 found no P0 or P1 and 3 P2 (trace count unwindowed, planted transcript revives an old Debate, workaround wording) and P3-1 fallback tests; round 2 re-review of `git diff 7d2372aa..ed7b6a08` found no P0, P1 or P2 and 3 test gaps, closed in 8e0dd4ae (mutants R1-R3 red). The planted-transcript limit (P2-2) is documented, not fixed. |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests tests -p no:cacheprovider` after round 3 (clean tree, no edits during the run) -> `4197 passed in 283.13s (0:04:43)` (round 2: `4194 passed`). (One earlier run showed 1 failure, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, because this review file was edited while the suite ran; it passes alone and in the clean rerun.) |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: Medium-risk change to one hook; two independent Stage 4 reviews (round 1 and round 2 re-review) cover it |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T08:49:38Z at `eb85573c`, before any implementation commit; the fixture is the T287 `t242_reviewed` session plus a Debate dated 5 hours before T242's first change; the script drives the real Stop hook):

```
now                 : 2026-11-08T08:49:38.138031+00:00
T242 first change   : 2026-11-08T08:49:38.026606+00:00
Debate (Skill call) : 2026-11-08T03:49:38.026606+00:00 task=T242, 2 Advocates
Stop check          : NOT paused: the old Debate was counted
```

Red tests run at 2026-11-08T08:49:20Z on the unchanged hooks: `16 failed, 5 passed` in `.claude/hooks/tests/test_debate_window.py` (the 5 that pass are today's behaviour: AC 1 x3, AC 4 x2). Example: `test_ac2_a_debate_dated_before_the_window_does_not_count` -> `AssertionError: None` (no pause).

**AFTER** (2026-11-08T08:56:07Z at `116c3b32`, the same script):

```
now                 : 2026-11-08T08:56:08.083657+00:00
T242 first change   : 2026-11-08T08:56:07.967693+00:00
Debate (Skill call) : 2026-11-08T03:56:07.967693+00:00 task=T242, 2 Advocates
Stop check          : paused: [hook:stop_auto_mode_check] Auto-mode final report check failed ... T242: 1 `DEBATED` line(s) need >=2 Advocate `Agent` calls ... the trace has 0
```

**DELTA**: A Debate that is older than a task's first change in the session no longer satisfies the Stop check for that task, so an old Debate cannot cover work done much later.

**WITNESS**: the implementing agent ran both captures; the Supervisor's independent reviewer reran the suites and the repros (reports in `memory/event-trace/T293.jsonl`); the reviewer reruns `python3 -m pytest .claude/hooks/tests/test_debate_window.py -q`. The trace `memory/event-trace/T293.jsonl` holds the counted test runs.

---

## Decisions (implementer)

- **Window.** The start is the earliest transcript time of a call that `session_work` counts as work on the task (`work_start`, the same test as `worked_on`, so the two cannot disagree). The Skill call and each Advocate must be dated at or after it. Both the work and the Debate are dated from the transcript, so clock skew with git or file times does not arise.
- **Boundary.** `>=`: a Debate at exactly the start counts. A Debate that ran before any file of the task changed does NOT count (AC 2, strict). The guide preferred counting from the guide's creation commit "if the window logic exposes it"; it does not, and adding git times would add a second clock, so it was not built. Consequence: write the task's guide or review file first, then debate (stated in `tracks.md`). The T287 fixture `t242_run` had the Debate before the review file; it now writes the file first (LR-0004 repoint, one pin-test edit).
- **No upper bound.** A Debate after the task's last change still counts: the check runs at the Stop, so a Debate cannot be newer than the check, and the T287 finding was about an old Debate covering later work.
- **No window keeps today's rule (AC 4).** For a task with no recorded change window in this session the whole session counts, as before T293. That happens when: no dated change call names the task (a marked minimal-track record whose work is in the main checkout, `T293 test_ac4_*`); the transcript cannot be read; or `session_work` raises (one stderr line, `Debate window unknown`). `tracks.md` Known limits says so.
- **Fail closed on dates.** With a window, a Skill call or Advocate call with a missing or unparsable timestamp does not count (AC 3).
- **Read cost.** The window is read lazily: only for a task that has a counted Advocate. That is one more pass over the transcript in that case only. `session_owner` still uses `load_work`, so the T250/T252 tests that break `load_work` still pin the ownership path.
- **Cut list kept:** no new setting; the 6-hour `_untagged.jsonl` fallback is unchanged.

## Mutation controls

Each: change bytes, `git diff --stat` non-empty, run `python3 -B -m pytest .claude/hooks/tests/test_debate_window.py` (pycache cleared first), restore with `git checkout`.

| # | Mutation | diff --stat | Red result |
|---|----------|-------------|------------|
| M1 | window check always true (`if False:`) | 1 file, 1 insertion, 2 deletions | 11 failed, 10 passed (`test_ac2_a_debate_dated_before_the_window_does_not_count` and 10 more) |
| M2 | only the Advocate date checked | 1 file, 1+/1- | 1 failed (`test_ac2_the_skill_call_and_the_advocates_must_both_be_inside[old-skill-call-new-advocates]`) |
| M3 | only the Skill date checked | 1 file, 1+/1- | 2 failed (`[new-skill-call-old-advocates]`, `test_ac2_one_old_and_one_new_advocate_leave_one_too_few`) |
| M4 | a missing or unparsable date counts (fail open) | 1 file, 1+/2- | 6 failed (`test_ac3_*`) |
| M5 | boundary `<=` instead of `<` (exact start does not count) | 1 file, 1+/1- | 1 failed (`test_ac1_a_debate_at_the_exact_start_of_the_window_counts`) |
| M6 | no window counts nothing (fail closed instead of whole session) | 1 file, 1+/1- | 1 failed (`test_ac4_a_task_with_no_change_window_keeps_the_whole_session_rule`) |
| M7 | window starts at the last change (`max`) | 1 file, 1+/1- | 2 failed (`test_ac1_the_window_starts_at_the_first_change_not_the_last`, `test_work_start_is_the_earliest_dated_call_that_worked_on_the_task`) |
| M8 | `work_start` counts any dated call, not only work | 1 file, 1+/1- | 5 failed (`test_ac2_a_debate_one_second_before_the_window_does_not_count`, ...) |
| M9 | window not passed to the count | 1 file, 1+/1- | 11 failed, 10 passed |

Restored tree: `21 passed`. Script: `scratchpad/mutate.py` (not committed).

## Stage 4 self-review (implementing agent; Medium risk)

- **P0/P1:** none found.
- **P2 (accepted, documented):** the window start is read from the session's own transcript files via `session_work._session_files`, which (T250) does not skip symlinks or filter `sessionId`, unlike `_own_session_files` for Debates. A planted or linked sub-agent file with an early forged work call for the task moves the start earlier, so an old Debate counts again. That equals today's rule (it fails open to T287), and writing the transcript folder is already the T251 trust root. Not changed here (Surgical Changes; `session_work` is shared with the merge gate).
- **P2 (behaviour):** a Debate before the task's first change no longer counts. A planning Debate with no earlier edit to a task file pauses at Stop. Stated in `tracks.md` ("write the task's guide or review file first").
- **P3:** `session_window` and `session_owner` now share `_task_worktrees` (one place for the worktree list). `_debate_counts` changed shape (`calls`, `window_start`), no other caller. Stale-text grep (LR-0005) for `_debate_counts`, `debates(task_id`, `load_work`, `session window`, `named with task=`: the hits are the changed code, `tracks.md` (updated) and `TASK_REVIEW_T287.md` (the `P3 session window` row, updated to "Fixed in T293"). No hit in `README.md`, `site/`, `agents/`, `docs/main-flow.md`.
- **Pin tests (LR-0004):** `test_stop_attribution_t287.py` (3 tests red after the change: the Debate came before the review file; fixed in `t242_run`), `test_t250_session_ownership.py`, `test_t252_marked_ownership.py` (still pass: they break `load_work`, which `session_owner` still uses), `test_agent_guide_dedup.py`, `test_vital_slice.py`, memory budget tests: part of the full run, green.

## Stage 4 round 2 (coordinator review: three P2, one P3)

| Finding | Handling |
|---------|----------|
| **P2-1** the window applied only to the transcript count; old Advocate records in `<ID>.jsonl` (no time limit) and `_untagged.jsonl` (6 h) still counted | **Fixed.** `advocate_records_in_window(records, start)`: with a window, a trace Advocate record counts only when its `timestamp` is at or after the start (`>=`); a missing or unparsable one does not count. No window = every record counts (AC 4). The window is read only when the trace holds an Advocate record. Tests (`test_p2_1_*`): old record in `T242.jsonl` (3 days), old record in `_untagged.jsonl` (2 h), bad timestamp, record inside the window counts (both files), and a no-window task still counts a 3-day-old record. Red first on the round-1 code: `7 failed, 25 passed` (the 7: 3 of P2-1, 1 hint, 2 P3-1, 1 doc pin). |
| **P2-2** `session_work._session_files` skips no symlink and filters no `sessionId` | **Not changed in code** (shared with the merge gate). New Known limits bullet in `tracks.md`: a planted transcript file can move the window start earlier (same trust root as T251). |
| **P2-3** wording, and no reason for the pause | **Done.** `tracks.md` now says: make the first change to a task file (the guide, the review file or the failing test in its worktree) before the Debate. The pause reasons (the `DEBATED` count reason and the Risk High reason) end with `(a Debate was found before the task's first change in this session; rerun it after the first change)` when the transcript held Advocate calls of this task's Debates dated before the window. Tests `test_p2_3_*`: hint present; absent with no Debate; absent for a Debate of another task. Trace records alone do not add the hint (as asked). |
| **P3-1** the two `session_window` fallbacks had no test | **Done.** `test_p3_1_a_transcript_that_cannot_be_read_*` (`work_entries` returns None) and `test_p3_1_a_window_reader_that_raises_*` (the `except` branch: `work_start` is made to raise in the project's copy of the lib; stderr names `Debate window unknown (RuntimeError)`). Both use a 3-day-old trace record, so they fail if the fallback fails closed. |

Pin tests repointed (LR-0004): `test_stop_attribution_t287.py::test_ac3_an_advocate_filed_right_is_not_counted_twice` wrote the review file after the Debate; with the trace side windowed it now writes it first (one move of one line).

Docs matched to the code: hook docstring (trace records, hint), `tracks.md` Auto-mode check paragraph and Known limits (trace records, wording, symlink limit).

Mutation controls, round 2 (`python3 -B`, `git diff --stat` 1 file, 1+/1- each; restored tree `32 passed`):

| # | Mutation | Red result |
|---|----------|------------|
| N1 | trace window filter always true | 4 failed (`test_p2_1_*` x3, `test_p3_1_a_transcript_that_cannot_be_read_*`) |
| N2 | trace record with a bad date counts | 1 failed (`test_p2_1_a_trace_record_with_a_bad_timestamp_does_not_count`) |
| N3 | window not passed to the trace count | 5 failed |
| N4 | hint never added | 1 failed (`test_p2_3_the_pause_names_a_debate_found_before_the_window`) |
| N5 | hint always added | 2 failed (`test_p2_3_the_pause_has_no_hint_*`) |
| N6 | unreadable transcript fails closed (`datetime.max`) | 1 failed (`test_p3_1_a_transcript_that_cannot_be_read_*`) |
| N7 | raising window reader fails closed | 1 failed (`test_p3_1_a_window_reader_that_raises_*`) |

## Stage 4 round 3 (re-review: three surviving mutants, two doc fixes)

The three new tests pass on the round-2 code on purpose: they pin behaviour that was already right but not covered. Each is proven by a mutation (`python3 -B`, `git diff --stat` 1 file, 1+/1-; restored tree `35 passed`).

| # | Mutation | Test that turns red |
|---|----------|---------------------|
| R1 | trace boundary `>=` -> `>` in `advocate_records_in_window` | 1 failed: `test_r3_a_trace_record_at_the_exact_start_of_the_window_counts` (both trace records dated exactly at the window start) |
| R2 | `dropped` = `len(mine)` instead of `len(mine) - counted` (false hint) | 1 failed: `test_r3_one_advocate_inside_the_window_is_too_few_and_gives_no_hint` |
| R3 | hint removed from the Risk High (D10) reason | 1 failed: `test_r3_the_risk_high_reason_carries_the_hint` (a High task with 3 Advocates dated before the window; asserts the exact `Risk High, but no decision was DEBATED with 3 Advocates (<hint>)`) |

Docs: `tracks.md` Known limits has a new bullet (a session that resumes a task and writes the report must rerun the Debate, because the Advocate records of an earlier session fall before the window), and the sentence "Times come from the transcript for both the work and the Debate" is reworded so it no longer contradicts the trace-record sentence ("Times of the work and of the Debate come from the transcript, and the trace's Advocate records follow the same rule with the trace hook's own timestamp. No time comes from git or file times"). `test_ac5_tracks_md_states_the_window_rule` pins both.
