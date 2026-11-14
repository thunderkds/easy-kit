# TASK_REVIEW — T310: `[admin]` stops when a Debate does not settle a choice

> Sibling of `tasks/TASK_GUIDE_T310.md`. Everything here is **filled by the reviewer at Stage
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
With `/verify (yours)`, your pass goes in the `verify` row below: Result `☑ pass`, Notes `/verify by the user, session <id>, commit <sha>`.

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t310_admin_unsure_stop.py` (18 tests, written first by `qa-expert`, red 9 failed / 9 passed at `dbe20e67`, green 18 passed after `ac208553`, `107d831f`, `c89e25f3`). AC 1–4, 6, 7 are doc-text tests; AC 5 and the `RULE` label run `stop_auto_mode_check.py` as a subprocess at Risk Medium and High. Three existing pins repointed with T310 comments: `tests/test_t307_admin_end_to_end.py`, `tests/test_auto_verify.py`, `.claude/hooks/tests/test_stop_attribution_t287.py`; one stale pin fixed: `.claude/hooks/tests/test_verify_row_fill_detection.py` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_t310_admin_unsure_stop.py -q -p no:cacheprovider` -> `18 passed in 1.46s` (Supervisor, at `c89e25f3`). Targeted run of the oracle plus the 3 repointed pins and the stale-pin file (`test_verify_row_fill_detection.py`, `tests/test_t307_admin_end_to_end.py`, `tests/test_auto_verify.py`) -> `371 passed in 105.64s` (at `107d831f`) |
| Negative cases hold | ☑ pass | Red run against the prior content (`qa-expert`, commit `dbe20e67`): `9 failed, 9 passed` — the 9 failures are the missing doc text (AC 1, 2, 3, 4, 6, 7). Negative cases in the oracle: a `[auto]`-only report and a Debate settled by a written rule are not a stop (AC 1, 7); a `DEBATED` line under `[admin]` is judged as before; at Risk High a `Paused:` line alone is still blocked by rule D10. `git diff main..HEAD --stat`: 9 files, 506 insertions before the review fixes (non-empty) |
| verify | ☑ pass | auto-run by hook, session 71fc08ae-2c84-4296-80a8-2781b8ea0977, commit d64ff62181434ba169d5eec72a3d6b9029ee882f, log .claude/verify-runs/T310-d64ff6218143.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 9 files of `main..feat/t310-admin-unsure-stop`: `docs/claude-md/tracks.md`, `skills/resolve-question/SKILL.md`, the oracle, 4 pin tests, the guide and this file. Direct readers found by grep: `.claude/hooks/stop_auto_mode_check.py` (unchanged; proved by the oracle's subprocess tests) and the pins named in the guide's `Pre-existing pin tests` row. Skipped: the ~90 files of T294–T309 that the `security-review` prompt listed — they are not in this branch. `code-review` 2026-11-14: P0 0, P1 0, P2 2, P3 2 (P2 x2 and one P3 fixed in `c89e25f3`; one P3 left: the `PushNotification` rule is in `tracks.md` only, the skill file has 2 spare bytes). `lane_check`: `lane: C2, 8 files, 445 lines, FITS`. `security-review`: no findings. Reports: `reports/code-review_feat-t310-admin-unsure-stop_20261114T033757.html`, `reports/security-review_feat-t310-admin-unsure-stop_20261114T033757.html` (git-ignored) |
| Full smoke suite still green (no regression) | ☑ pass | Implementer, clean run at `c89e25f3`: `7191 passed, 5 skipped, 25 subtests passed in 399.64s`. Supervisor run at `c89e25f3`: `1 failed, 7190 passed, 5 skipped, 25 subtests passed in 370.62s`. The one failure, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, compares `git status` before and after; the Supervisor edited this review file during the run. Alone: `9 passed in 0.22s`. The auto verify run re-runs the suite |
| **Companion score (easy-verifier)** | ☑ N/A | not run: the optional companion score was skipped for a change to docs, skill text and tests. The merge gate blocks on `☑ fail` only, never on an N/A row |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component: docs, skill text and tests only |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-14T02:44:05Z by qa-expert, before any implementation commit; docs and skill text, so the verbatim prior content):

`docs/claude-md/tracks.md` `### Stops that stay`:

```
Even in auto mode, the Supervisor pauses the task, with one message that says why, for:

- a safety-hook block;
- an action that deletes or overwrites data with no backup;
- the 4th Debate in a task (the `resolve-question` cap);
- a paid action outside the task's own work;
- a login or secret the Supervisor does not have;
- the same sub-agent hitting the step limit twice.

The pause also goes in the final report, on its `Paused:` line.
```

`skills/resolve-question/SKILL.md` size: 8191 bytes (`wc -c`; cap 8192).

Oracle, red: `python3 -m pytest .claude/hooks/tests/test_t310_admin_unsure_stop.py -q -p no:cacheprovider` -> `9 failed, 9 passed` (the 9 failures are the doc-text tests; the 9 passes are the hook tests, as the hook stays unchanged).

**AFTER** (implementer, 2026-11-14, docs and skill text; the oracle run is the real run):

```
$ python3 -m pytest .claude/hooks/tests/test_t310_admin_unsure_stop.py -q -p no:cacheprovider
..................                                                       [100%]
18 passed in 1.13s
$ wc -c skills/resolve-question/SKILL.md
8190 skills/resolve-question/SKILL.md
```

New bullet in `### Stops that stay`: "with `[admin]` only, an unsettled Debate: the Advocates disagree and no written rule or Citation picks one. `[auto]` alone is unchanged: it decides by its rules and logs `⚠ decided for you`." 

**DELTA**: A task run with `[admin]` now stops and asks you, with one `Paused: unsure — <question>; options: <A> / <B>` line and one push notification, when its Debate does not settle a choice. Before, the Supervisor picked the safer option itself and logged it.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
