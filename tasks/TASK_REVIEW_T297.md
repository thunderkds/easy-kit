# TASK_REVIEW — T297: A `## CLI Effort Table` beside the CLI Model Table

> Sibling of `tasks/TASK_GUIDE_T297.md`. Everything here is **filled by the reviewer at Stage
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
1. Effort goes in its own `## CLI Effort Table` after the model table, not as a new column of the model table — SAFER OPTION: a new column changes the header that `tests/test_cli_model_table.py` AC1 pins and makes an empty cell mean two different things; a second table leaves the model table byte-identical. The plan doc says "column". ⚠ decided for you — please review
2. No model cell changes (haiku → strong model waits for T300, not started) — RULE: `tasks/TASK_GUIDE_T297.md` § Requirement "Out of scope" (the plan doc says "Keep the proposed table only if cost is lower and no pass is lost", so the change follows the measurement)
3. Default `claude` row is `low, low, medium, high`; other rows are empty — SAFER OPTION: the claude values are the plan doc's proposal, and the kit never guesses another CLI's values (T136). ⚠ decided for you — please review
4. An empty effort cell passes no effort and is not a STOP (an empty model cell still is) — SAFER OPTION: a missing effort must not block a spawn. ⚠ decided for you — please review
5. The three guides T297-T299 were committed on local `main` (not pushed) as one `plan:` commit — RULE: precedent `git show bc5ccc34` ("plan: T294 … guides, board"), `tasks/` guides must exist before a spawn (`AGENTS.md` Hard-Stop Gate 1)
6. Stage 4: code review no P0/P1/P2; P3s handled in a fix round (mutation controls for two Stage 1 guards, stale output-form lines in the template and `PROJECT_SPEC.md`); the review prompt had no memory slice, because a reviewer reads the diff and the guide — RULE: `docs/claude-md/pipeline-stages.md` Stage 4 item 1
Paused: disk full — `/tmp/claude-1000` volume returned ENOSPC, so no Bash command starts (the T299 agent and this session both hit it). The T297 fix-round check, the full test run and the auto verify run have not run. Free space (or restart with `CLAUDE_CODE_TMPDIR` on another volume), then run `python3 .claude/hooks/stop_auto_verify.py --start T297`.
Checks: tests `python3 -m pytest tests/test_cli_effort_table.py tests/test_cli_model_table.py -q -p no:cacheprovider` — 19 passed on the final commit `abc719ad` (fix round: two more mutation controls, a re-wrap with no word change, the intro-note output form); `python3 -m pytest tests -q -p no:cacheprovider -k "cli_effort or cli_model or auto_mode or stage"` — 193 passed at `d337a116`; full suite `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — 4390 passed before the fix round, NOT re-run on `abc719ad` (a rerun died with ENOSPC and a pytest process from it may still be running: stop it before the next run); reviews code-review — no P0/P1/P2 (read-only reviewer, `Verdict: no P0/P1/P2`), the P3s fixed in `abc719ad` except the tracks.md row 6 note, which T299 carries; real run — not run (disk full)
Memory: nothing new (the cause of the disk-full stop is not checked yet)
Not done: merge (yours); auto verify: not started (disk full)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
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

**BEFORE**: Verbatim prior content (docs and template change, no executable code; captured 2026-11-09 before any implementation commit). `grep -c "CLI Effort Table"` on `templates/PROJECT_SPEC_template.md`, `PROJECT_SPEC.md` and `docs/claude-md/pipeline-stages.md` = 0 in each.

`docs/claude-md/pipeline-stages.md` Stage 1 item 2 (lines 79-88):

```
2. **Multi-CLI Authentication**
   Please list every agentic CLI you have authenticated, the exact command to run it, and which
   model it should spawn at each Complexity level (C0–C3). Record this as the `## CLI Model Table`
   in `PROJECT_SPEC.md` (from `templates/PROJECT_SPEC_template.md`): one row per CLI, one column
   per level. Example: "Claude: claude — C0 haiku, C1 sonnet, C2 sonnet/opus, C3 opus | Codex: codex
   — [ask the user; never guess a Codex/Gemini model name]". A CLI with no row, or an empty cell for
   a level, means `craft-spawn-prompt` will STOP and ask rather than pick a model for it. In auto mode
   the Supervisor reads the table instead of asking; with no row or an empty cell it spawns on the CLI that
   runs this session, with the model this session runs as, logged `SAFER OPTION` with the review flag, and
   never invents another CLI's model name.
```

`templates/PROJECT_SPEC_template.md` `## CLI Model Table` section (lines 77-89), followed directly by `## Tasks`:

```
## CLI Model Table

> Filled at Stage 1. One row per authenticated CLI, one column per Complexity level. At spawn
> time, `craft-spawn-prompt` looks the task's Complexity Level up in the row for the CLI that will
> run it and reports `<cli> · <Cn> → <model>`. No row for the CLI, or an empty cell → STOP and ask
> the user; never fall back to another CLI's model, never invent one.

| CLI | Run command | C0 | C1 | C2 | C3 |
|---|---|---|---|---|---|
| claude | `claude` | haiku | sonnet | sonnet or opus | opus |
| [cli] | [run command] | [model] | [model] | [model] | [model] |

---

## Tasks
```

`PROJECT_SPEC.md` `## CLI Model Table` section (lines 137-149) has the same intro and a `| claude | ... | haiku | sonnet | sonnet or opus | opus |` row and an empty `| codex | `codex` | | | | |` row, followed directly by `## Tasks`. No effort table exists anywhere.

**AFTER**: Verbatim new content (2026-11-09). `grep -n "CLI Effort Table"` now hits `templates/PROJECT_SPEC_template.md:91`, `PROJECT_SPEC.md:151` and `docs/claude-md/pipeline-stages.md:87`. The new section, directly after the model table's closing `---` and before `## Tasks`, in `PROJECT_SPEC.md`:

```
## CLI Effort Table

> Filled at Stage 1. Same shape as the CLI Model Table: one row per CLI, one column per Complexity
> level. A cell is `low`, `medium`, `high`, `xhigh` or `max`. `craft-spawn-prompt` passes it as the
> spawn's effort. An empty cell means: pass no effort. It is not a STOP.

| CLI | Run command | C0 | C1 | C2 | C3 |
|---|---|---|---|---|---|
| claude | `claude` | low | low | medium | high |
| codex | `codex` | | | | |
```

The template has the same section with a `| [cli] | [run command] | | | | |` row. Stage 1 item 2 gained: "Also ask for the effort at each level (`low`, `medium`, `high`, `xhigh` or `max`) and record it as the `## CLI Effort Table`, same shape, beside the model table. An empty effort cell means no effort is passed; it is not a STOP." and its auto-mode sentence now reads "reads both tables ... no row or an empty model cell". The model table headers and cells are untouched; only the intro note's report format changed to `<cli> · <Cn> → <model> · effort <level|none>` (Supervisor request, matches T298's output).

**DELTA**: A project can record the effort per Complexity level for each CLI in `PROJECT_SPEC.md`, and the Stage 1 question asks for it, with an empty cell meaning no effort is passed.

**WITNESS**: Run by the common-infrastructure agent in the T297 worktree on 2026-11-09, to be confirmed by the reviewer from `memory/event-trace/T297.jsonl`: `python3 -m pytest tests/test_cli_effort_table.py tests/test_cli_model_table.py -q -p no:cacheprovider` -> `19 passed`; five byte-changing mutation controls (one per guard: bad value, empty claude cell, heading, effort per level, not a STOP) each turned the new tests red (non-empty `git diff --stat` shown first), restored -> `10 passed`.
