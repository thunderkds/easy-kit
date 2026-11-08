# TASK_REVIEW — T285: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T285.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_step_limit_agent_scope.py` (new, 7 tests, AC1-AC5; AC6 is text, checked by grep below). Run 2026-11-08T00:17:13Z: `python3 -m pytest .claude/hooks/tests/test_step_limit_agent_scope.py .claude/hooks/tests/test_step_limit_session_scope.py .claude/hooks/tests/test_step_limit_self_clearing.py -q` -> `28 passed in 23.67s` |
| Verification command run | ☑ pass | Command 1 (above): `28 passed in 23.67s`. Command 2 `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` (2026-11-08T00:22Z): `1 failed, 3448 passed, 25 subtests passed in 248.61s`. The 1 failure is `tests/test_spike_report_t283.py::test_the_real_report_is_valid` (`tasks/SPIKE_REPORT_T283.md is not written yet`): that file exists only on branch `feat/t283-karpathy-spikes`, so it fails on base `4c076b6c` too and does not touch this change. |
| Negative cases hold | ☑ pass | RED against the prior hook content: see BEFORE (`4 failed, 24 passed`). Mutation controls, each a byte change to `.claude/hooks/pre_agent_step_limit.py` (diff of good vs mutated shown), restored after each run:
M1 `counter_name = f"step_count_{session}_{agent}_{task_id}.txt"` -> `f"step_count_{session}_{task_id}.txt"` (drop agent fragment): `4 failed, 3 passed` (ac1, ac3, ac4, ac5-unsafe red).
M2 `cleaned = _SESSION_SANITIZE_PATTERN.sub("", agent_id)[:_AGENT_MAX_LEN]` -> `cleaned = agent_id` (drop sanitiser): `2 failed, 5 passed` (ac5-unsafe, ac5-fallback red).
M3 `if not isinstance(agent_id, str):` -> `if agent_id is None:` (non-string accepted): `2 failed, 5 passed` (ac5-fallback, ac5-still-limited red).
M4 insert `if "agent_id" in event and not agent: sys.exit(0)` (bad agent_id means no limit): `2 failed, 5 passed` (ac5-fallback, ac5-still-limited red).
Restored: `diff` against the saved good copy empty, `7 passed in 17.84s`. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | Not filled by the implementer: the Supervisor runs Stage 4. Changed: `.claude/hooks/pre_agent_step_limit.py`, new `.claude/hooks/tests/test_step_limit_agent_scope.py`, one sentence in `skills/resolve-question/SKILL.md`. Pin-test grep for `step_count`/`pre_agent_step_limit` in `.claude/hooks/tests/` and `tests/` found only main-thread-key pins (no `agent_id` in their events); all pass. |
| Full smoke suite still green (no regression) | ☑ pass | `1 failed, 3448 passed` with the one failure unrelated and present on base (see Verification command row). |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

2026-11-08 note: Not covered by tests: the real `agent_id` to `resolve_task_id` path; a harness that omits `agent_id` falls back to today's behaviour (limit still in force).

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T00:13:41Z by common-infrastructure on base `4c076b6c`, with the new test file present and no change to `.claude/hooks/pre_agent_step_limit.py`; `git status --short` showed only the two untracked files `.claude/hooks/tests/test_step_limit_agent_scope.py` and `tasks/TASK_REVIEW_T285.md`):
```
$ python3 -m pytest .claude/hooks/tests/test_step_limit_agent_scope.py .claude/hooks/tests/test_step_limit_session_scope.py .claude/hooks/tests/test_step_limit_self_clearing.py -q
FAILED .claude/hooks/tests/test_step_limit_agent_scope.py::test_ac1_two_agents_of_one_task_have_two_counters_and_no_shared_block
FAILED .claude/hooks/tests/test_step_limit_agent_scope.py::test_ac3_one_agents_91st_call_is_blocked_and_another_agent_is_allowed
FAILED .claude/hooks/tests/test_step_limit_agent_scope.py::test_ac4_a_single_looping_agent_is_still_blocked_resets_and_escalates
FAILED .claude/hooks/tests/test_step_limit_agent_scope.py::test_ac5_unsafe_agent_id_is_reduced_to_a_safe_file_name_fragment
4 failed, 24 passed in 27.08s
```
The cause shown by the first run: with `agent_id` present the hook still writes one file, `['step_count_S_T925.txt']`, where `step_count_S_x_T925.txt` is expected. Agent B's first call is the 91st call on the shared counter and is blocked.

**AFTER** (2026-11-08T00:17:13Z, same command, hook changed):
```
$ python3 -m pytest .claude/hooks/tests/test_step_limit_agent_scope.py .claude/hooks/tests/test_step_limit_session_scope.py .claude/hooks/tests/test_step_limit_self_clearing.py -q
............................                                             [100%]
28 passed in 23.67s
```
Counter names now: main thread `step_count_S_T921.txt`; sub-agent `step_count_S_agentA_T921.txt` and `step_count_S_agentB_T921.txt`.

**DELTA**: Two parallel sub-agents of one task each get their own 90-call budget, so one run's calls no longer stop the other, while a single looping run is still blocked at call 91.

**WITNESS**: Run by the common-infrastructure agent (implementer) on 2026-11-08 between 00:13Z and 00:26Z; the calls are in `memory/event-trace/T285.jsonl` (written by `post_tool_trace.py`). The Supervisor's Stage 4 re-run and the auto verify run are the independent witness; the implementer alone is not.
