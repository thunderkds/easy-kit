# TASK_REVIEW — T311: a generator writes the kit data into site/docs.html, and a test fails when it goes stale

> Sibling of `tasks/TASK_GUIDE_T311.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_kit_explorer_data.py` (18 tests, written first by `qa-expert`; red `9 failed, 9 errors` at `cb4ffbdc`, green `18 passed` after `591cf07a`). AC 1–5 are tested directly (markers, one JSON block, idempotence, every skill and agent once, built-ins, stage mapping, no `/home/`, timestamp or raw `</`, hostile text, `--check` exit codes, missing marker exits 2, `--check` never writes). AC 6 is held by the existing site suites (`test_site_content.py`, `test_site_story.py`, `test_site_visual_first.py`: 213 passed). Two pins repointed past the generated block, each with a T311 comment: `tests/test_site_content.py` (`_page_text()` cuts the block) and `tests/test_stage_names.py` (`OWN_PHASE_LINES` gains one `site/docs.html` line) |
| Verification command run | ☑ pass | Supervisor at `08693dfd`: `python3 -m pytest tests/test_kit_explorer_data.py -q -p no:cacheprovider` -> `18 passed in 0.78s`; `python3 scripts/gen_kit_explorer.py --check; echo "exit $?"` -> printed nothing, `exit 0`. Data: 37 skills (34 steps, 3 sections), 4 agents, 5 built-ins |
| Negative cases hold | ☑ pass | Red run before any implementation (`qa-expert`, `cb4ffbdc`, 2026-11-14T04:35:38Z): `scripts/gen_kit_explorer.py` did not exist (exit 2), `grep -c kit-explorer-data site/docs.html` printed 0, oracle `9 failed, 9 errors`. Oracle mutations in a temp copy of the repo: a changed skill description gives `stale:` naming it (exit 1); a new and a removed skill exit 1; a changed stage index exits 1; a deleted marker exits 2 and writes nothing; text holding `</script><b>x</b>` and `-->` stays text and the block closes once. `git diff main..HEAD --stat`: 7 files, non-empty |
| verify | ☑ pass | auto-run by hook, session 26e36c9c-0e70-4ce6-aac8-097556b59301, commit b31a0094abf20f78671cab39402e717c50e18989, log .claude/verify-runs/T311-b31a0094abf2.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 7 files of `main..feat/t311-kit-explorer-data`: `scripts/gen_kit_explorer.py`, the generated block in `site/docs.html`, the oracle, two repointed pins, the guide and this file. Callers by grep: the existing site tests that read `docs.html` (all run; 213 passed). Skipped: the ~90 files of T294–T310 that the `security-review` prompt listed (not in this branch). `code-review` 2026-11-14: P0 0, P1 0, P2 2 (guide said "every string from a kit file" but the built-ins are hand-written; guide said step headings stay inside the Workflow section but the code reads on past it — both fixed in `08693dfd`), P3 3 (page weight +77 KB, kept indented for readable diffs; a change to a built-in line is invisible to `--check`, written into the guide as a known limit; `lane_check` `EXCEEDS (lines 2217 > 500)`, almost all of it the generated block, warn-only). A scan of the block for emails, home paths, task IDs and key patterns found none. For T312: the block holds `KANBAN` (5) and `In Progress` (2), recorded in the T312 guide. `security-review`: no findings. Reports: `reports/code-review_feat-t311-kit-explorer-data_20261114T045913.html`, `reports/security-review_feat-t311-kit-explorer-data_20261114T045913.html` (git-ignored) |
| Full smoke suite still green (no regression) | ☑ pass | Implementer, clean run (no edits during it, `git status` clean before) at `08693dfd`: `python3 -m pytest .claude/hooks/tests/ tests/ -q` -> `7209 passed, 5 skipped, 25 subtests passed in 339.66s (0:05:39)`. The auto verify run re-runs the suite |
| **Companion score (easy-verifier)** | ☑ N/A | not run: the optional companion score was skipped; the merge gate blocks on `☑ fail` only, never on an N/A row |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no visible change: this task adds a data block and a script; the visible section is T312 |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no visible change; `test_site_visual_first.py` (no hex outside tokens, no third-party asset) passes with the block in the page |
| **UI: Responsiveness at target viewports** | ☑ N/A | no visible change |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-14T04:35:38Z, before any implementation commit):
```
$ python3 scripts/gen_kit_explorer.py --check; echo "exit $?"
python3: can't open file '/home/hungnguyenhuu/workspace/pets/wt-t311/scripts/gen_kit_explorer.py': [Errno 2] No such file or directory
exit 2
$ grep -c 'kit-explorer-data' site/docs.html
0
$ python3 -m pytest tests/test_kit_explorer_data.py -q -p no:cacheprovider
9 failed, 9 errors in 0.37s   (script and markers absent)
```

**AFTER** (captured 2026-11-14, after the implementation):
```
$ python3 scripts/gen_kit_explorer.py --check; echo "exit $?"
exit 0
$ grep -c 'kit-explorer-data' site/docs.html
4
$ python3 -m pytest tests/test_kit_explorer_data.py -q -p no:cacheprovider
18 passed in 0.86s
$ git diff --stat site/docs.html
 site/docs.html | 1539 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 1539 insertions(+)   (0 deletions)
```
Page weight: `site/docs.html` 163,864 -> 241,348 bytes; the block is 77,453 bytes (compact JSON would save 8 KB, so the indented form is kept for readable diffs).

**DELTA**: A maintainer can run `python3 scripts/gen_kit_explorer.py` to put every agent's and skill's data into `site/docs.html`, and `--check` (and the test) fails the moment the kit and the page disagree. No reader sees a change yet; T312 draws the explorer from this block.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
