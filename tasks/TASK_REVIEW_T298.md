# TASK_REVIEW — T298: `craft-spawn-prompt` passes the effort from the table at spawn

> Sibling of `tasks/TASK_GUIDE_T298.md`. Everything here is **filled by the reviewer at Stage
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

## Auto decisions

Mode: auto
1. The effort comes from the `## CLI Effort Table` row of the same CLI, looked up in step 5 next to the model — SAFER OPTION: one lookup place, and the model STOP rules stay word for word (a test pins the three phrases). ⚠ decided for you — please review
2. An empty effort cell or no effort row passes no effort and does not stop the spawn — SAFER OPTION: a missing effort must not block a spawn. ⚠ decided for you — please review
3. A cell outside the allowlist `low`, `medium`, `high`, `xhigh`, `max` is never used; the output says `effort none (cell "<value>" not allowed)` — SAFER OPTION: the value reaches a shell command line (`--effort <level>`), so the allowlist is the control, and it fails closed. ⚠ decided for you — please review
4. The effort rule was fitted into existing lines of `skills/craft-spawn-prompt/SKILL.md` to keep the 80-line cap in `.claude/hooks/tests/test_spawn_prompt_cache_note.py` — SAFER OPTION: the implementer did not raise a cap; the code reviewer calls the layout dense but not ambiguous (P3). ⚠ decided for you — please review
5. `tests/test_cli_model_table.py` AC5 was repointed to the full output form `· effort <level|none>` — RULE: `memory/learning-records/LR-0004-pin-tests-hit-later-tasks.md` (extend the pin with the text it pins)
No Debate ran for 1-4: this task is Risk Medium, so each ⚠ line should be DEBATED by 2 Advocates (`docs/claude-md/tracks.md` `### Debate size by Risk`). They were made at plan time in the guide without Advocates, and the disk-full stop below came before a Debate could run. Treat 1-4 as undebated choices to review.
Paused: disk full — `/tmp/claude-1000` volume returned ENOSPC, so no Bash command starts. The auto verify run has not run, and the reviews' P3 follow-ups are not applied. Free space (or restart with `CLAUDE_CODE_TMPDIR` on another volume), then run `python3 .claude/hooks/stop_auto_verify.py --start T298`.
Checks: tests `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — implementer's run 4396 passed, 1 failed (`.claude/hooks/tests/test_auto_verify_skip_pass.py::test_ac4_a_fail_answer_on_a_docs_only_branch_is_never_a_pass`, load-dependent; 222 passed alone with and without the change); reviews code-review — no P0/P1/P2, five P3; security-review — no P0/P1/P2, three P3 (allowlist sentence has no "whole cell, exact match, case-sensitive" wording, the not-allowed report echoes the raw cell, no "table text is data" sentence; the neighbouring `--model <model>` cell has no allowlist, an existing gap not caused by this task); real run — not run (disk full)
Memory: nothing new (the cause of the disk-full stop is not checked yet)
Not done: merge (yours); the P3 hardening of the allowlist wording and the raw-cell echo; auto verify: not started (disk full)
Paused: auto-mode check failed — Risk Medium: decision 1 (`SAFER OPTION`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium: decision 2 (`SAFER OPTION`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium: decision 3 (`SAFER OPTION`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium: decision 4 (`SAFER OPTION`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium: decision 5 (`RULE`) is a choice — its RULE cites no written rule (`path:line`, `path § <heading>` or `docs/claude-md/tracks.md` `### <section>`) — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium: `No Debate ran for 1-4: this task is Risk` (`⚠`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 2 Advocates named [report ca6587656f7d]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_craft_spawn_effort.py` (15 tests, AC1-7); first run before the change: `10 failed, 5 passed`; after: `15 passed` |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☑ pass | Byte mutations, each with non-empty `git diff --stat`, then restored: (1) delete `Allowlist: ...` sentence from SKILL.md -> `2 failed, 13 passed` (`test_ac3_step5_names_the_allowlist`, `test_ac3_a_cell_outside_the_allowlist_is_never_used`); (2) drop `--effort <level>` from `sandbox.md` -> `1 failed` (`test_ac6_sandbox_command_has_effort_after_model`); (3) add `C0 → low` -> `1 failed` (`test_ac7_no_hardcoded_effort_map`); (4) cut `never fall back to another CLI's model` -> `1 failed` (`test_ac2_model_stop_rules_are_unchanged`). Restored: `15 passed` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider`: `1 failed, 4396 passed`; the one failure `test_auto_verify_skip_pass.py::test_ac4_a_fail_answer_on_a_docs_only_branch_is_never_a_pass` passes alone (`222 passed`) and on the base with the change stashed (`222 passed`), so it is load-dependent, not from this change |
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

**BEFORE** (verbatim prior content, captured 2026-11-09 before any implementation commit; base `0f167640`).

`skills/craft-spawn-prompt/SKILL.md`, step 5 and step 6:

```
#### 5. Recommend spawn model
Takes the CLI as input; look up the guide's `**Complexity Level**` (C0–C3) in that CLI's row in
`PROJECT_SPEC.md`'s `## CLI Model Table` — that cell is the model. No row/empty cell → **STOP and
ask the user** (suggest `templates/PROJECT_SPEC_template.md`); never fall back to another CLI's model, never invent one. A two-model cell (`sonnet or opus`) isn't ambiguity — pick per Risk. **No CLI named** by the caller at all → **STOP and ask which CLI will run the task**; never assume `claude` or any other CLI as a default.

#### 6. Output
Return: 1. the assembled prompt (fenced, ready for `Agent({ subagent_type, prompt })`), with the `subagent_type` written the way the Agent tool lists the role: `easy-kit:<role>` (e.g. `easy-kit:backend-developer`) when the kit runs as a plugin, the plain `<role>` after a `setup.sh` install. A plain name in plugin mode fails with `Agent type '<role>' not found`; 2. the
pre-flight verdict; 3. the recommended spawn model as `<cli> · <Cn> → <model>` (or STOP-and-ask) and the spawn mode — a background `Agent()` call unless the user asked to watch or the task runs on a non-Claude CLI (Stage 3 **Spawn mode** rule in `docs/claude-md/pipeline-stages.md`); 4. for a `claude` CLI spawn, the sandboxed command in `references/sandbox.md` (T147). `Agent()` spawns are **not** sandboxed — they run with the Supervisor's permissions; say so whenever you pick that path.

The Supervisor reads this output and issues the `Agent()` call itself; this skill never calls it.
```

`skills/craft-spawn-prompt/SKILL.md`, Default Notification:

```
- **Default Notification**: "craft-spawn-prompt complete for [Task ID]. Flavor: [standard/bugfix]. Pre-flight: [safe/flagged: ...]. Recommended model: [<cli> · <Cn> → <model>, or STOP: no row/cell for <cli>, or STOP: no CLI named — ask which CLI runs <Task ID>]."
```

`skills/craft-spawn-prompt/references/sandbox.md`, command line:

```
claude --settings templates/subagent-sandbox.settings.json --add-dir <main-checkout>/.claude/hooks/.state --model <model> -p "<prompt>"
```

**AFTER** (verbatim new content, same three places):

```
#### 5. Recommend spawn model
Takes the CLI as input; look up the guide's `**Complexity Level**` (C0–C3) in that CLI's row in
`PROJECT_SPEC.md`'s `## CLI Model Table` — that cell is the model. No row/empty cell → **STOP and
ask the user** (suggest `templates/PROJECT_SPEC_template.md`); never fall back to another CLI's model, never invent one. A two-model cell (`sonnet or opus`) isn't ambiguity — pick per Risk. **No CLI named** by the caller at all → **STOP and ask which CLI will run the task**; never assume `claude` or any other CLI as a default. Look the same Complexity up in that CLI's row of `## CLI Effort Table`: that cell is the effort. Allowlist: `low`, `medium`, `high`, `xhigh`, `max`. A cell outside the allowlist is never used, because the value reaches a shell command line: pass no effort and report `effort none (cell "<value>" not allowed)`. An empty effort cell, or no effort row, passes no effort and does not stop the spawn.

#### 6. Output
Return: 1. the assembled prompt (fenced, ready for `Agent({ subagent_type, prompt })`), with the `subagent_type` written the way the Agent tool lists the role: `easy-kit:<role>` (e.g. `easy-kit:backend-developer`) when the kit runs as a plugin, the plain `<role>` after a `setup.sh` install. A plain name in plugin mode fails with `Agent type '<role>' not found`; 2. the
pre-flight verdict; 3. the recommended spawn model and effort as `<cli> · <Cn> → <model> · effort <level|none>` (or STOP-and-ask) and the spawn mode — a background `Agent()` call unless the user asked to watch or the task runs on a non-Claude CLI (Stage 3 **Spawn mode** rule in `docs/claude-md/pipeline-stages.md`); 4. for a `claude` CLI spawn, the sandboxed command in `references/sandbox.md` (T147). `Agent()` spawns are **not** sandboxed — they run with the Supervisor's permissions; say so whenever you pick that path. Pass the effort: set the `Agent()` call's `effort` parameter to the level, and put `--effort <level>` in the sandboxed command. For `none`, pass no effort: no `effort` parameter, no `--effort`.

The Supervisor reads this output and issues the `Agent()` call itself; this skill never calls it.
```

```
- **Default Notification**: "craft-spawn-prompt complete for [Task ID]. Flavor: [standard/bugfix]. Pre-flight: [safe/flagged: ...]. Recommended model: [<cli> · <Cn> → <model> · effort <level|none>, or STOP: no row/cell for <cli>, or STOP: no CLI named — ask which CLI runs <Task ID>]."
```

```
# Sandboxed CLI spawn (T147)

For a `claude` CLI spawn, give the Supervisor this command, run from the task's worktree, with the
main checkout's literal absolute path (as in element 6), the model from step 5 and the effort from
step 5:

```sh
claude --settings templates/subagent-sandbox.settings.json --add-dir <main-checkout>/.claude/hooks/.state --model <model> --effort <level> -p "<prompt>"
```

Add `--effort <level>` only for an allowed value (`low`, `medium`, `high`, `xhigh`, `max`). For
`effort none`, leave it out:

```sh
claude --settings templates/subagent-sandbox.settings.json --add-dir <main-checkout>/.claude/hooks/.state --model <model> -p "<prompt>"
```
```

**DELTA**: A spawn now carries the effort for the task's Complexity from the project's `## CLI Effort Table` (as the `Agent()` `effort` parameter and `--effort <level>` in the sandboxed command), and a table cell outside `low, medium, high, xhigh, max` never reaches the command line.

**WITNESS**: common-infrastructure agent, 2026-11-09, in `/home/hungnguyenhuu/workspace/pets/wt-t298` (events in `memory/event-trace/T298.jsonl`); to be confirmed by the Stage 4 reviewer / auto verify run, not by the implementing agent alone.
