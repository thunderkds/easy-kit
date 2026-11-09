# TASK_REVIEW — T300: Measure the effort table on 6 replayed C0/C1 tasks

> Sibling of `tasks/TASK_GUIDE_T300.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_t300_effort_measurement.py` (9 tests: AC1 data file, AC2/AC4 table and totals, AC3 verdict, AC5 limits and unchanged tables; 3 mutation controls). Written first: 9 failed before the data and DDR existed, 9 passed after (implementer report, commit b9de8eb9). Pass |
| Verification command run | ☑ pass | `python3 -m pytest tests/test_t300_effort_measurement.py -q -p no:cacheprovider` → `9 passed in 0.02s`. Full suite, run by the Supervisor on the branch with TMPDIR under `.eff-tmp`: `.claude/hooks/tests tests` → `6911 passed, 5 skipped, 25 subtests passed in 405.17s`. Pass |
| Negative cases hold | ☑ pass | Mutation 1: JSON cost 0.012755 → 0.012756 gives `FAILED test_ddr_table_matches_json`, `1 failed, 8 passed`. Mutation 2: DDR `**Verdict**: do not keep` → `keep` gives `FAILED test_ddr_verdict_equals_the_rule` and `FAILED test_mutation_flipped_verdict_turns_verdict_red`, `2 failed, 7 passed`. Both restored, `9 passed`. Mutation 3 is in the test: arm B cost 0 still gives `do not keep` while T292 is lost, and clearing the T292 failure gives `keep` (the rule can say both). Pass |
| verify | ☐ blocked | auto-run by hook, session 6baae659-0efc-4617-9c65-92207b5947a0, commit 20e1f52d6c4496772889627a8dadf7d70b68cf19, log .claude/verify-runs/T300-20e1f52d6c44.log — blocked (SKIP, and git does not show a change of docs-only files) |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `code-review`: scope is the 3 new files (DDR, JSON data, test) and the guide and review file; no code file changed. No P0, P1 code or P2 finding. `lane_check`: `C2, 4 files, 663 lines, EXCEEDS (lines 663 > 500); unpredicted: the DDR, the JSON, the guide, the test` (warn-only; 254 lines are the pretty-printed JSON). JSON equals the Supervisor's `results.json` record for record (checked). Stale-reference sweep: the one stale line is `memory/MEMORY.md:28` ("T300 unmeasured"), a Supervisor-only write, updated after the review. Startup-reads check: the implementer's line omits `agents/common-infrastructure.md`, `memory/codebase-map.md` and LR-0003/4/5, a P1 process finding; waived by the Supervisor because the role guide arrives as the agent's system prompt (AGENTS.md, Skills vs Agents), and the work needed no code or LR rule it skipped (mutation controls were run). `security-review` (Medium risk): nothing to report. The new files hold no secrets, paths, emails or executable code. Pass |
| Full smoke suite still green (no regression) | ☑ pass | `6911 passed, 5 skipped, 25 subtests passed in 405.17s (0:06:45)` on the branch, run alone. The implementer's own earlier run showed 2 `test_auto_verify*` failures that moved on each rerun (known load flake, while its own background work still ran); the clean rerun has none. Pass |
| **Companion score (easy-verifier)** | ☑ N/A | not run: the change is a record (docs, data, a test) with no code to score |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Verbatim prior state (2026-11-09, before any implementation commit; this task adds a DDR, a data file and a test, no executable code). `ls docs/ddr/` printed:
```
0001-measure-first-token-refactor.md
0002-retire-measure-first-token-instrument.md
0003-demonstration-block-and-delivery-report.md
0004-uphold-hard-stop-gate-1-over-spawn-elimination.md
0005-vital-slice-extends-simplicity-first.md
0006-provider-adapters-inline-non-negotiables.md
0007-canonical-skills-and-agents-at-plain-root.md
0008-saved-tool-output-lives-inside-the-repo.md
0009-measure-token-work-from-transcripts-and-aim-at-focus.md
```
`docs/ddr/data/` and `tests/test_t300_effort_measurement.py` do not exist yet.

**AFTER**: `ls docs/ddr/` now also prints `0010-effort-table-measured-on-replayed-tasks.md` and `data`. The DDR's verdict line reads `**Verdict**: do not keep`. Totals row: `| All | $0.7806 | $3.1994 | 4.10 |`.

**DELTA**: The project owner can see, with numbers, that running C0 and C1 tasks on `opus` at `low` effort cost 4.10 times the current table and lost one pass, so the effort-table proposal stops here.

**WITNESS**: Supervisor session, 2026-11-09: the 12 trials, `finalize.py` (oracle and meter) and the full suite run; the implementer's tool calls are traced under T300 in `memory/event-trace/T300.jsonl` by the spawn binding.
