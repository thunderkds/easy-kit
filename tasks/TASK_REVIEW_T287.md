# TASK_REVIEW — T287: Auto-mode Stop check files a task's test, review and Advocate calls under the task they serve

> Sibling of `tasks/TASK_GUIDE_T287.md`. Everything here is **filled by the reviewer at Stage
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

## Root causes (AC 1)

Reproduced from the real traces in the main checkout's `memory/event-trace/` (read only) and the
`Paused:` lines on `main`. The spike's 6 stops have three causes, not one. Each has its own AC row
in the guide (AC 1a, 1b, 1c). Line numbers are at the branch base `a4e0221b`.

| Stop | Cause | Evidence (real records) | Root cause, file:line |
|------|-------|-------------------------|-----------------------|
| T219 (code-review, security-review) | **A — real stop: the work had not run yet** | Pause line added in the implementer's commit `d9dfeb22` (2026-10-30 12:31:55Z). The Supervisor's `code-review` Skill call is at 12:32:31Z and `security-review` at 12:32:52Z, both in `T219.jsonl`. | Nothing misfiled. The Stop hook fires when the main session ends a turn (`.claude/settings.json` `Stop`); the Supervisor ended its turn while the background implementer ran, before Stage 4. `.claude/hooks/stop_auto_mode_check.py:409-413` was right at that moment. **Row dropped** (guide: "If a case turns out to be a real stop, say so and drop that row"). |
| T226 (tests, code-review, security-review) | **A — real stop: the work had not run yet** | Pause line added in `89117f17` (2026-11-01 05:06:03Z). The Supervisor's last call before it is the background spawn at 05:00:57Z; its next call is 05:09:00Z. First test run 05:04:53Z, `code-review` 05:09:00Z, `security-review` 05:09:23Z, all in `T226.jsonl`. | As T219: the check ran right after the spawn; `T226.jsonl` held no test and no review then. `.claude/hooks/stop_auto_mode_check.py:370`, `:409-413` were right. **Row dropped.** |
| T120 ×2 (`Paused: done not moved — Gate 5` by the auto close-out; `Paused: auto-mode check failed — no test run` by check (7)) | **B — tests run in the task's worktree, filed under the session pointer's task** | The Supervisor (main session) wrote the pointer `T120` at 10:38:47Z. A `printf … "T250" > …/active_task.d/$CLAUDE_CODE_SESSION_ID` at 10:40:16Z (filed in `T250.jsonl`) and `T119` at 10:53:57Z re-pointed it. T120's test runs `cd …/wt-t120 && python3 -m pytest …` at 10:44:56Z, 10:53:20Z, 10:53:26Z are in `T250.jsonl`; 10:58:46Z is in `T119.jsonl`. `wt-t120` is on branch `fix/t120-reinstall-summary`. | `.claude/hooks/lib/task_context.py:384`: a main-session call (no `agent_id`) is filed by the one per-session pointer before any signal of the call itself; the pointer is shared by the session and every sub-agent of it (`:62-64`, "Residual"). `.claude/hooks/post_tool_trace.py:158` files the record by it. Both T120 readers then read only `T120.jsonl`: check (7) `.claude/hooks/stop_auto_mode_check.py:370` and the close-out's Gate 5 `.claude/hooks/lib/auto_closeout.py:168`, both through the gate's `trace_shows_verification` (`.claude/hooks/pre_bash_block_unsafe_merge.py:280`). |
| T242 ×2 (the Supervisor's `Paused: trace mismatch` line; check (3) `the trace has 0`) | **C — a Debate for the task, filed under the stale pointer's task** | Pointer `T241` written 2026-11-03 11:46:09Z (`T241.jsonl`). `Skill resolve-question` with args `task=T242 risk=Medium` at 11:58:59Z, then `Advocate 1: how to shrink plugin install?` / `Advocate 2: …` at 11:59:21Z / 11:59:22Z, all in `T241.jsonl`. The pointer named T242 only from 12:02:51Z. | `.claude/hooks/lib/task_context.py:384` again (stale pointer), and an Advocate prompt carries no task ID by design (T221, `skills/resolve-question/references/advocate.md`), so no signal of the call outranks it. `.claude/hooks/stop_auto_mode_check.py:194` reads only `T242.jsonl` and `_untagged.jsonl`, so `:392` counts 0 Advocates. |

Causes B and C share the root: the main session's calls are filed by one pointer that names one
task, while the Supervisor works on several. They need two remedies, because only B leaves a
signal on the call itself (the directory it runs in). C leaves one on an earlier call of the same
session (`resolve-question` `task=T242`, its documented `Args:`).

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_stop_attribution_t287.py` (19 tests, written first; 6 red against the unchanged hooks at `a4e0221b`, see BEFORE). AC 1b/2: `test_ac2_t120_*` (2); AC 1c/2: `test_ac2_t242_advocates_of_its_own_debate_are_found`; AC 3: `test_ac3_*` (5); AC 4: `test_ac4_*` (7); AC 5: `test_ac5_*` (3); AC 6: `test_ac6_tracks_md_states_the_new_attribution`. After `86a91d88`: `19 passed in 3.01s` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q` → `19 passed in 3.01s` (head `86a91d88`) |
| Negative cases hold | ☑ pass | AC 3/AC 4 negatives pass before and after the change (9 of the BEFORE run's passes). Six byte-changing mutation controls, each `git diff --stat` non-empty, red then restored (`git checkout`) green: M1 `stop_auto_mode_check.py \| 2 +-` (credit every trace file to every task) → `test_ac4_another_sessions_debate_is_not_credited` `1 failed` / `1 passed`; M2 `task_context.py \| 8 ++++----` (slot 2b after the pointer) → `test_ac2_t120_tests_run_in_its_worktree_are_found` `1 failed` / `1 passed`; M3 `task_context.py \| 2 +-` (any worktree counts) → `test_ac4_a_test_run_in_another_tasks_worktree_is_not_credited_to_the_pointer` `1 failed` / `1 passed`; M4 `stop_auto_mode_check.py \| 2 +-` (a Debate counts for every task) → `test_ac4_advocates_of_a_debate_for_another_task_are_not_credited` `1 failed` / `1 passed`; M5 `task_context.py \| 2 +-` (`per_call=True` by default, reaches the safety hook and step limit) → `test_ac5_the_safety_hook_and_the_step_limit_still_resolve_by_the_pointer` `1 failed` / `1 passed`; M6 `stop_auto_mode_check.py \| 2 +-` (sum, not max) → `test_ac3_an_advocate_filed_right_is_not_counted_twice` `1 failed` / `1 passed` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q` at head `86a91d88` (2026-11-08T00:35:07Z–00:38:31Z): `1 failed, 3562 passed, 25 subtests passed in 203.28s`. The 1 failure is `tests/test_spike_report_t283.py::test_the_real_report_is_valid` — `tasks/SPIKE_REPORT_T283.md is not written yet`: that file is only on `feat/t283-karpathy-spikes`, the test came in with `faa5180f`, and T287 touches neither (no regression from this change) |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | pure hook code and doctrine text: no UI component, no `site/` change |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | pure hook code and doctrine text: no UI component, no `site/` change |
| **UI: Responsiveness at target viewports** | ☑ N/A | pure hook code and doctrine text: no UI component, no `site/` change |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured before any implementation commit; the reproduction fixtures against the unchanged
hooks — the Stop check pauses T120 and T242 although the work ran):

```
2026-11-08T00:25:00Z
HEAD a4e0221b docs(T287): guide from main (no implementation commit yet; hooks unchanged)
$ python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q -rf
E       AssertionError: [hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `## Auto mode`):
E       assert "[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `#...ctive_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop" is None
E       AssertionError: [hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `## Auto mode`):
E       assert "[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `#...ctive_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop" is None
E       AssertionError: ('[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `...Agent` calls (description `Advocate <n>:` and a prompt starting `Using the repo, answer alone:`); the trace has 0', '')
E       assert '[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `#...ate `Agent` calls (description `Advocate <n>:` and a prompt starting `Using the repo, answer alone:`); the trace has 0' is None
E       AssertionError: [hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `## Auto mode`):
E       assert ('[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `#...ate `Agent` calls (description `Advocate <n>:` and a prompt starting `Using the repo, answer alone:`); the trace has 0' and 'the trace has 1' in '[hook:stop_auto_mode_check] Auto-mode final report check failed — fix it before you stop (docs/claude-md/tracks.md `#...ate `Agent` calls (description `Advocate <n>:` and a prompt starting `Using the repo, answer alone:`); the trace has 0')
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac2_t120_tests_run_in_its_worktree_are_found
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac2_t120_relative_cd_and_a_later_segment_are_found
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac4_a_test_run_in_another_tasks_worktree_is_not_credited_to_the_pointer
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac2_t242_advocates_of_its_own_debate_are_found
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac3_t242_one_advocate_is_still_too_few
FAILED .claude/hooks/tests/test_stop_attribution_t287.py::test_ac5_the_safety_hook_and_the_step_limit_still_resolve_by_the_pointer
6 failed, 9 passed in 3.67s
```

The T120 fixtures pause on check (7) (`no test run in memory/event-trace/T120.jsonl`); the T242
fixture pauses on check (3) (`the trace has 0`). The 9 that pass before the change are the
negatives (AC 3, AC 4) and the stops that stay (AC 5): they must hold before and after.

**AFTER** (same command, head `86a91d88`):

```
$ python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q
...................                                                      [100%]
19 passed in 3.01s
```

Against the real repo (`CLAUDE_PROJECT_DIR` = the main checkout), slot 2b files
`cd /home/hungnguyenhuu/workspace/pets/wt-t287 && python3 -m pytest -q` under `T287` (branch
`feat/t287-stop-attribution`), and `ls -la` / `cd <main checkout> && git status` under nothing new
(0.1 ms and 0.2 ms: no tokenizer, no `git`).

**DELTA**: An auto-mode task whose tests ran in its own worktree, or whose Debate's `resolve-question` call named it, is no longer paused for that work when the session's active-task file named another task; a task with no such work is still paused with the same message.

**WITNESS**: [to be filled by the reviewer from `memory/event-trace/T287.jsonl` and the auto verify run — the implementing agent (common-infrastructure, 2026-11-08) ran BEFORE at 00:25:00Z and AFTER at head `86a91d88`, and is not a witness alone]
