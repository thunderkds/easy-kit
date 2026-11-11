# TASK_REVIEW — T306: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T306.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | New: `tests/test_t306_admin_retry_blocked.py` (locked oracle, drafted by the implementer, signed off and committed by the Supervisor in `e2a7f75`; 33 tests: AC 1–6 17 needles in `### Admin tag` + numbered steps; AC 6 retry words outside the section only in `[admin]` pointers, `Not done:` item keeps `/verify (yours)`; AC 7 both templates' slot; AC 8 5 pointer phrases + AGENTS.md agreement). Red at `e2a7f75` (prior content): `33 failed in 0.14s`. Green at `e661366`: `python3 -m pytest tests/test_t306_admin_retry_blocked.py -q -p no:cacheprovider` → `33 passed in 0.11s`. Repointed: `tests/test_stage_names.py` row 18 (T306 branch beside T284/T299, commit `e661366`) |
| Verification command run | ☑ pass / ☐ fail | Oracle: `33 passed in 0.11s`. Pin tests (`test_admin_tag.py`, `test_auto_verify_skip_pass.py`, `test_agent_guide_dedup.py`, `test_stop_auto_mode_check.py`, `test_vital_slice.py`, `test_memory_channel_and_budget.py`, `tests/test_auto_verify.py`, `tests/test_auto_mode.py`, `tests/test_tracks.py`, `tests/test_stage_names.py`, `tests/test_site_content.py`), first run after the edit: `2 failed, 1265 passed in 141.10s` — `test_admin_tag.py::test_ac10_mutation_control_dropping_a_statement_is_caught[`python3 .claude/hooks/stop_auto_verify.py --start <ID>`]` (the full command was now twice in `### Admin tag`; the first paragraph now says `--start <ID>` and points to step 4) and `test_stage_names.py::test_ac4_each_auto_mode_row_keeps_its_rule_and_its_log_label` (row 18 pinned to base; repointed). After: oracle + `test_admin_tag.py` + `test_stage_names.py` → `280 passed in 14.34s` |
| Negative cases hold | ☑ pass / ☐ fail | Red run against the prior content: `33 failed` at `e2a7f75`. Mutation controls inside the oracle (17 needle drops + SC 3 "once" cut and `fail`-sentence cut + 2 template-slot cuts) pass, i.e. each mutation goes red. Repoint control for `test_stage_names.py` row 18: `sed` appended `, changed` to row 18 → `git diff --stat docs/claude-md/tracks.md` `1 file changed, 38 insertions(+), 9 deletions(-)` (uncommitted edit + mutation) → `1 failed, 15 deselected`; restored → `1 passed, 15 deselected` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass / ☐ fail | Affected set: `docs/claude-md/tracks.md` (`### Admin tag` + pointers at the Merge paragraph, the `Not done:` item, `### Auto verify (Stop hook)` last line, row 18, `### The Supervisor never`), `docs/claude-md/pipeline-stages.md` Stage 5 item 1, the `Not done:` slot of `templates/TASK_REVIEW_template.md` and `templates/MINIMAL_LOG_template.md`, `tests/test_stage_names.py` row 18. No `.claude/hooks/**` file changed (`git diff --stat 0bc6bcd HEAD -- .claude/hooks` is empty). Not edited: `AGENTS.md` (hash-pinned hub, `test_agent_guide_dedup.py`; its "on `blocked` or `fail` merges nothing" stays true), `site/docs.html` (states no rule for what follows `blocked`). Stale-text grep for "merges nothing and reports why", "falls back to you", "when the run is blocked, you must", `/verify (yours)` outside tests/tasks: every hit is an updated line. `code-review` / `security-review`: not run by the implementer (no `Skill` tool in this spawn) — the Supervisor's Stage 4 step |
| Full smoke suite still green (no regression) | ☑ pass / ☐ fail | `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` (scratchpad venv, pytest 9.2.0) at `e661366`: `2 failed, 7000 passed, 6 skipped, 25 subtests passed in 426.36s (0:07:06)`. The 2 failures are environment-only: `test_heredoc_quoted_marker.py::test_round4_premise_the_shell_runs_the_push_and_the_scanner_keeps_it[d-busybox-ash-bash]` and `[d-busybox-ash-zsh]` — `AssertionError: bash did not run the canary of d-busybox-ash`; `which busybox` → `busybox not found`. The test runs a real busybox; this branch changes no hook file |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: verbatim prior content (docs/templates only), quoted 2026-11-11T11:41Z at `0bc6bcd1d5df`, before the first implementation commit.

`docs/claude-md/tracks.md:617-622` (`### Admin tag`):

> With `[admin]`, the Supervisor starts the run itself: as soon as the task is at Ready for Review, it runs
> `python3 .claude/hooks/stop_auto_verify.py --start <ID>` and waits for the verdict. It never runs `/verify` in
> its own session. Only on a pass does it go on to merge and push, without asking. On `blocked` or
> `fail` it merges nothing and reports why. A task that changes only files with no runtime surface (docs, task
> files, memory, tests: `### Auto verify (Stop hook)`) gets a pass when the run answers `skip`, so it needs no
> typed `/verify`. A `skip` for any other task is `blocked`: its `/verify` then falls back to you.

`templates/TASK_REVIEW_template.md:42`:

> `Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours)>`

`templates/MINIMAL_LOG_template.md:59`:

> `**Not done:** merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours)>`

No retry exists: one `blocked` run sends `/verify` to the user.

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
