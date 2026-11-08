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

## Stage 4 fix round (2026-11-08)

Security review: one P0, one P1, three P2 and two P3 findings, all confirmed by the reviewer's experiments E1-E9. Each experiment is now a red test in `.claude/hooks/tests/test_stop_attribution_t287.py`. The tests were committed red in `c687279e` (`14 failed, 20 passed`; the `pushd` case was already blocked); the fix is in `deac1d5d`.

| Finding | What I did |
|---------|------------|
| **P0** slot 2b filed a test run that did not run in X's worktree, or did not run at all (E1 comment, E2 main checkout then `cd`, E3 `/tmp` then `cd`, E4 subshell `cd`) | **Fixed.** `.claude/hooks/lib/task_context.py` `_run_dirs` / `_task_id_from_worktree`: a call is filed under X only when EVERY simple command runs in X's worktree. A command in the main checkout, in a directory that is no worktree, in an unknown directory or in another task's worktree gives None, so the session pointer decides. None also for any `#` comment token, `(` / `)`, `$(` or backticks, a background `&` (including a trailing one), a pipe after `cd`, and `pushd` / `popd`. Tests: `test_p0_*` (10 cases). The positive T120 cases (`cd <wt-t120> && python3 -m pytest …`) stay green. |
| **P1** `_debate_counts` counted an Advocate `tool_use` that a hook or the user denied (E7) | **Fixed.** `.claude/hooks/stop_auto_mode_check.py`: an Advocate `tool_use` counts only when a `tool_result` for its id, in the same file, is not an error. The max(trace, session) rule is kept. Tests: `test_p1_*` (no result; an error result). The fixture `Session.call` now writes real `tool_result` entries with unique ids. |
| **P2a** a raising slot 2b (no `git`, timeout, OSError) dropped the whole resolution to `_untagged` (E5) | **Fixed.** `resolve_task_id` wraps slot 2b in its own `try`, so slots 3-5 still run. Test: `test_p2_slot_2b_failing_falls_through_to_the_pointer` (`PATH=/nonexistent`, filed under T250). |
| **P2b** forged `subagents/agent-*.jsonl` or a symlink to another session's transcript was read (E6, E8) | **Fixed in the T287 code path only.** `session_work.py` was last changed by T284 (`f654ee3c`), so I left it alone and added `_own_session_files` in `stop_auto_mode_check.py`: it skips symlinks, and `_debate_counts` reads only entries whose `sessionId` equals this session's id. The docstring and `tracks.md` now say what is enforced. A file planted in this session's folder with this session's id is still read; only the `.claude/settings.json` deny rules (T251) protect that folder. Tests: `test_p2_a_forged_sub_agent_transcript_is_not_read`, `test_p2_a_symlink_to_another_sessions_transcript_is_not_read`. |
| **P2c** docs said "all run in live worktrees" while the code also filed when some ran elsewhere | **Fixed.** `docs/claude-md/tracks.md` `### Auto-mode check (Stop hook)` and `### Known limits`, and the `task_context.py` slot 2b docstring, now state the every-command rule, the forms that block it, and that a main-checkout command blocks the filing. `test_ac6_*` pins the new sentences. |
| **P3** `DEBATE_TASK` took the first `task=` anywhere, including quoted question text (E9) | **Fixed.** `_debate_task` splits `args` with `shlex` and takes the last whole top-level `task=<ID>` token. Test: `test_p3_*`, run as a subprocess Stop check (so no in-process `main()` waits on stdin). |
| **P3** `git worktree list --porcelain` without `-z` | **Fixed.** `-z`, fields split on NUL. |
| **P3** session window (Debates of the whole session count, not only recent ones) | **Skipped, follow-up.** Not part of this round, as the coordinator asked. Today a Debate counts for its named task for the whole session. |

Mutation controls for the new guards (each `git diff --stat` = `1 file changed, 1 insertion(+), 1 deletion(-)`, restored with `git checkout`, then green). Run at `4d5a73ed`:

```
N1  return None -> continue for a non-worktree dir  task_context.py | 2 +-  RED 1 failed  / GREEN 1 passed  (e3-tmp-then-cd)
N3  drop the `#` comment guard                     task_context.py | 2 +-  RED 1 failed  / GREEN 1 passed  (e1-comment-after-cd)
N4  follow `(` `)`                                 task_context.py | 2 +-  RED 1 failed  / GREEN 1 passed  (e4-subshell)
N5  narrow the slot 2b try to KeyError             task_context.py | 2 +-  RED 1 failed  / GREEN 1 passed  (p2 falls through)
N6  count a tool_use without a non-error result    stop_auto_mode_check.py | 2 +-  RED 2 failed / GREEN 2 passed (p1 x2)
N7  read symlinked sub-agent files                 stop_auto_mode_check.py | 2 +-  RED 1 failed  / GREEN 1 passed  (p2 symlink)
N8  drop the sessionId check                       stop_auto_mode_check.py | 2 +-  RED 1 failed  / GREEN 1 passed  (p2 forged)
N9  first task= token, not the last                stop_auto_mode_check.py | 2 +-  RED 1 failed  / GREEN 1 passed  (p3)
N10 porcelain without -z                           task_context.py | 2 +-  RED 1 failed  / GREEN 1 passed  (ac2 t120)
N2  `any(d == root)` -> `all(...)`                 task_context.py | 2 +-  stays green (1 passed)
```

N2 stays green by design. The main checkout is never in the worktree list, so N1's rule already blocks a main-checkout command. The `any(d == root)` line only skips the `git` call; it is not a separate guard. Two tests were adjusted so that one guard does not hide another: `e1-comment-after-cd` (the comment comes after the `cd`), and the forged and symlinked transcripts now carry non-error results (`4d5a73ed`). My earlier positive case `cd <main>; printf …; cd ../wt-t120 && pytest` now correctly says nothing (it has a main-checkout command), so it became `cd ../wt-t120 && python3 -m pytest -q 2>&1 | tail -3` from the main checkout.

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_stop_attribution_t287.py`, 35 tests. First round: 19 tests, written first, 6 red on the unchanged hooks at `a4e0221b` (see BEFORE). AC 1b/2: `test_ac2_t120_*` (2); AC 1c/2: `test_ac2_t242_*`; AC 3: `test_ac3_*`; AC 4: `test_ac4_*`; AC 5: `test_ac5_*`; AC 6: `test_ac6_*`. Stage 4 round: 16 more (`test_p0_*` 10, `test_p1_*` 2, `test_p2_*` 3, `test_p3_*` 1), committed red in `c687279e` (`14 failed, 20 passed`). At `4d5a73ed`: `35 passed in 5.43s` |
| Verification command run | ☑ pass | `python3 -B -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q` → `35 passed in 5.43s` (head `4d5a73ed`) |
| Negative cases hold | ☑ pass | First round: M1-M6, each `git diff --stat` non-empty, red then green after `git checkout`: M1 credit every trace file to every task → `test_ac4_another_sessions_debate_is_not_credited`; M2 slot 2b after the pointer → `test_ac2_t120_tests_run_in_its_worktree_are_found`; M3 any worktree counts → `test_ac4_a_test_run_in_another_tasks_worktree_is_not_credited_to_the_pointer`; M4 a Debate counts for every task → `test_ac4_advocates_of_a_debate_for_another_task_are_not_credited`; M5 `per_call=True` by default → `test_ac5_the_safety_hook_and_the_step_limit_still_resolve_by_the_pointer`; M6 sum, not max → `test_ac3_an_advocate_filed_right_is_not_counted_twice`; each `1 failed` / `1 passed`. Stage 4 round: N1, N3-N10 red then green, N2 green by design (see § Stage 4 fix round) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -B -m pytest .claude/hooks/tests/ tests/ -q` at head `4d5a73ed` (2026-11-08T00:51:37Z–00:54:58Z): `1 failed, 3578 passed, 25 subtests passed in 201.30s`. The 1 failure is `tests/test_spike_report_t283.py::test_the_real_report_is_valid` — `tasks/SPIKE_REPORT_T283.md is not written yet`: that file is only on `feat/t283-karpathy-spikes`, and T287 touches neither (no regression from this change) |
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
negatives (AC 3, AC 4) and the AC 5 tests that drive the step limit and the sensitive-path hook: they must hold before and after. (`test_ac5_the_text_of_the_stops_that_stay_is_unchanged` pins the bullets of `### Stops that stay` only; it does not run a stop.)

**AFTER** (same command; first round at head `86a91d88`, Stage 4 round at `4d5a73ed`):

```
$ python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q
...................                                                      [100%]
19 passed in 3.01s
$ python3 -B -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q   # 4d5a73ed
35 passed in 5.43s
```

Against the real repo (`CLAUDE_PROJECT_DIR` = the main checkout), slot 2b files
`cd /home/hungnguyenhuu/workspace/pets/wt-t287 && python3 -m pytest -q` under `T287` (branch
`feat/t287-stop-attribution`), and `ls -la` / `cd <main checkout> && git status` under nothing new
(0.1 ms and 0.2 ms: no tokenizer, no `git`).

**DELTA**: An auto-mode task whose tests ran in its own worktree, or whose Debate's `resolve-question` call named it, is no longer paused for that work when the session's active-task file named another task; a task with no such work is still paused with the same message.

**WITNESS**: [to be filled by the reviewer from `memory/event-trace/T287.jsonl` and the auto verify run — the implementing agent (common-infrastructure, 2026-11-08) ran BEFORE at 00:25:00Z and AFTER at head `86a91d88`, and is not a witness alone]

## Fix round 2 (2026-11-08)

An independent security re-check found a P0 in slot 2b (15 shapes in which `pytest` ran in the main checkout while the call was filed under T120, and the merge gate's `trace_shows_verification('T120')` accepted T120). A code-review and a 3-Advocate Debate followed. All were folded into this round.

**What changed.** `.claude/hooks/lib/task_context.py`: the blocklist `_run_dirs` is gone. `_leading_cd_dir` is an ALLOWLIST. A `Bash` call is filed under a worktree's task only when the whole command is `cd <dir> && cmd [&& cmd]...` and:
- `<dir>` is absolute or resolves (against the event `cwd`) to an existing, searchable directory (`os.path.isdir` + `os.access X_OK`) whose logical and physical paths agree; no `-`, `~`, `$`, backtick, glob, or `CDPATH` (for a bare name).
- `&&` is the only joiner after the `cd`: never `;`, `||`, newline, `&`, `|&`, `(`, `)`; a pipe only after a later command.
- no second `cd`, and no `builtin command eval exec source pushd popd` anywhere; no shell keyword (`if while until for case select function coproc time ! { }`, `.` as the first word of a command); no leading `VAR=` before a word; no `<<`, `$`, backtick or `#`.
- no argument that names `..`, `~`, or an absolute path outside the worktree (`--rootdir <main>`); no inline-code flag (`-c`, `-e`, `-lc`, `--eval`) and no argument with a quote or paren next to a `/` (Debate residual: `python3 -c "import os;os.chdir('/home')"`).
Anything else falls through to the pointer task (today's behaviour). A call with no `cd` is never filed by the event `cwd`. `stop_auto_mode_check.py` and the docs: only comments and text. Docs: `docs/claude-md/tracks.md` (`### Auto-mode check (Stop hook)` and `### Known limits`: the exact form, the forms that fall through, C9, the older `invokes_test_runner` weakness, what the filing does not prove) and the `task_context.py` docstring slot 2b.

**Review findings.** P1 (`cd <wt> && git status; cd - && pytest`): rejected by the allowlist (`;`), test `review-P1-cd-dash-after-a-semicolon`. P2 tests added: `test_review_p2_a_debate_in_a_sub_agent_transcript_is_credited` (mutation M9), `test_review_p2_a_resolve_question_call_with_no_task_does_not_keep_the_earlier_task` (M10), the `popd`/`pushd` shapes (M3), the subdirectory honest shape for the `startswith(p + os.sep)` guard (M11), and the bare-relative / `./` shapes with an event `cwd` unlike the hook's cwd (M12). `test_ac5_the_stops_that_stay_are_unchanged` is renamed `test_ac5_the_text_of_the_stops_that_stay_is_unchanged` (it pins text only). P3: the dead `last_head` code went with `_run_dirs`; "keep in step with session_work" comments added at the lexer setup and at `_own_session_files`.

**Not changed.** The fourth P1 case in the coordinator's note (event `cwd` after the command ran) is pinned: `test_round2_a_trailing_cd_is_not_filed_when_the_event_cwd_is_the_directory_after_it` (2 cases) and `test_round2_a_command_with_no_cd_is_not_filed_by_the_event_cwd`. `;` and newline after the `cd` are not kept (no existing honest test used them), so they fall to the pointer.

**Red then green.** Tests committed red first (`5b767a87`: `29 failed, 55 passed`). After the later review and Debate tests were added, the same tests against the round-1 `task_context.py` (`git stash` of that file only):

```
$ python3 -B -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q -p no:cacheprovider    # round-1 task_context.py
41 failed, 60 passed in 11.18s     (B03 B04 B05 B28 B06 B07 B08 B09 B10 B11 B12 B13 B24 B27 B14 B16 B18 B19, C3 x2, trailing cd x2, no-cd, CDPATH env, dotdot via symlink, -c/-e x6, ...)
$ python3 -B -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q -p no:cacheprovider    # allowlist
101 passed in 12.57s
```

Mutation controls (one `str.replace` each, restored by writing the original back, `-k` on the group shown):

```
M1  remove the existence check (isdir + access)          3 failed, 61 passed (nonexistent-dir-and-and, target-is-a-file-and-and, C3 pruned)
M1b remove ONLY the isdir clause                         55 passed  (stays green BY DESIGN: os.access(X_OK) also fails on a missing path)
M2  `||` treated as a joiner                             1 failed (B18)
M3  ANYWHERE_WORDS never matches                         1+ failed (B03 cd-dash and the builtin/eval/popd shapes)
M4  HEAD_WORDS / VAR= check removed                      1 failed (env-assignment-before-the-runner)
M5  _escapes always False                                2 failed (B16, relative-dotdot-argument)
M6  `$` and backtick guard removed                       2 failed (variable-argument, backtick-argument)
M7  `;` allowed after the cd                             1 failed (semicolon-after-cd)
M8  CDPATH rule removed                                  1 failed (cdpath env)
M9  sub-agent files not read (stop_auto_mode_check)      1 failed (sub-agent transcript credited)
M10 task-less resolve-question keeps the earlier task    1 failed
M11 `real.startswith(p + os.sep)` -> `real == p`         1 failed (subdirectory-target)
M12 relative cd joins the hook's cwd                     2 failed (bare-relative-name, C13 dot-slash)
M13 logical == physical check removed                    1 failed (dotdot through a symlink)
M14 inline-code flag rule removed                        5 failed (-c/-e shapes)
M15 quote/paren + slash rule removed                     1 failed (debate-quote-and-slash-without-c)
```

The `<<` rule has three guards (the explicit `<<` test, the newline rule, the punctuation token check), so removing one leaves B14/B19 red-proof intact; no single-byte mutation of only that line can turn them red. That is intended.

**Suite.** `python3 -B -m pytest .claude/hooks/tests tests -q -p no:cacheprovider`: `1 failed, 3644 passed, 25 subtests passed in 202.55s`. The 1 failure is the pre-existing `tests/test_spike_report_t283.py::test_the_real_report_is_valid` (`tasks/SPIKE_REPORT_T283.md` exists only on `feat/t283-karpathy-spikes`); T287 touches neither.

**Accepted limits** (`### Known limits`): a script file in the worktree that does its own `cd`; a symlink in the worktree that points to main; any worktree of this repo on a branch whose name holds the task ID (C9); the gate's older `invokes_test_runner` counting a heredoc body or the far side of `||` as a run (not changed here).
