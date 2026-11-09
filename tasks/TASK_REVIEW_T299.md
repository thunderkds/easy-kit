# TASK_REVIEW — T299: A task that moves up or fails `verify` gets one more effort step first

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
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
1. With an empty or missing effort cell the raise-effort rule changes nothing and the other levers apply (like at `max`) — SAFER OPTION: counting from `low` could lower the effort the CLI uses by default, which breaks "never lowers". The reviewer found this gap (P2). ⚠ decided for you — please review
2. Repeated raises add up: the count starts from the effort of the task's last spawn (the table cell for the first raise), up to `max` — SAFER OPTION: a fixed base would make the second failure change nothing; the plan doc's "start low, dial up" adds up. The reviewer found this gap (P2). ⚠ decided for you — please review
3. Only a `fail` verdict counts, not `blocked` — RULE: `docs/claude-md/tracks.md` `### Auto verify (Stop hook)` lists the verdicts pass, fail and blocked; a blocked run is not a code failure (reviewer P3)
4. Row 6 of the `### Every user stop and its auto rule` table now says an empty effort cell is not a stop (one clause, test repointed in `tests/test_stage_names.py` in the style of T284's row-19 exception) — RULE: AGENTS.md LR-0005 stale-text rule (`memory/learning-records/LR-0005-stale-text-after-change.md`), T297 reviewer P3 on `tracks.md:218`
5. No code or hook raises effort; the rule is doctrine text — RULE: `tasks/TASK_GUIDE_T299.md` § Requirement "Out of scope"
Checks: tests `python3 -m pytest tests/test_tracks.py tests/test_stage_names.py tests/test_auto_mode.py -q -p no:cacheprovider` — 214 passed on `739d55f8`; full suite `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — 4401 passed, 4 failed, all in `tests/test_auto_verify.py`; the 4 pass when run alone (12 passed), and another session's full suite ran at the same time, so I read them as load flakes; reviews code-review — round 1 no P0/P1, two P2 (fixed in `739d55f8`); narrow re-review of `739d55f8` — no P0/P1/P2, five P3 (two-triggers-in-one-spawn and empty-cell-with-explicit-last-effort cases are undefined; the first-raise and stacking clauses have no test that fails when deleted; the row-6 check has one mutation control; sentences are long because of the 4-sentence cap); real run — none, the auto verify run checks it
Memory: nothing new (candidate not written: several full suites running at once filled the `/tmp` inodes and Bash failed with ENOSPC; the cause is not verified end to end)
Not done: merge (yours; merge T297 first, T298 and T299 read its table); the five re-review P3s (not applied); auto verify: ☐ blocked (session d27aec23-725d-4266-8f49-feb1d0f15161, commit c9713bd723cd1741a9d01015d397ef6f9cac5c6b, log .claude/verify-runs/T299-c9713bd723cd.log); /verify (yours): the auto run was blocked, because it answered SKIP and `docs/claude-md/tracks.md` is not a docs-only path

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_tracks.py` (10 new checks with mutation controls), `tests/test_stage_names.py` (row-6 repoint); `python3 -m pytest tests/test_tracks.py tests/test_stage_names.py -q -p no:cacheprovider` printed `95 passed in 2.30s` on `c9713bd7` (2026-11-09) |
| Verification command run | ☑ pass | same command, `95 passed`; full suite: `4 failed, 4401 passed`, the 4 in `tests/test_auto_verify.py` pass alone (`12 passed`) |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ blocked | auto-run by hook, session d27aec23-725d-4266-8f49-feb1d0f15161, commit c9713bd723cd1741a9d01015d397ef6f9cac5c6b, log .claude/verify-runs/T299-c9713bd723cd.log — blocked (SKIP, and git does not show a change of docs-only files) |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component: the change is skill, doc and test text only |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI component: no tokens, colours or typography touched |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI component: no page or layout touched |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (verbatim prior content of `docs/claude-md/tracks.md` lines 54-67, `## Switching track`, captured 2026-11-09 before any implementation commit; `grep -n "effort" docs/claude-md/tracks.md` printed nothing):

```
## Switching track

- The user can reply `full` (extended track) or `minimal` at any time, and the Supervisor switches. The
  Supervisor does not prompt for it: never ask which track, never recommend a lower one; the user's `minimal`
  is their own choice.
- The Supervisor may move a task **up** (minimal → extended) mid-task when it finds a row of the rule that
  is true. It says so in one line: `Track: extended — moved up: <reason>`. It never moves a task **down** on
  its own.
- A task grows when it needs more than one file beyond its first estimate, a design choice, or a second
  session. Move it up, then write the task guide from what was learned. The extended track continues from
  Stage 2 with that guide.
- The user says `minimal` for a task that the rule puts on the extended track (for example High risk): the
  Supervisor complies. It states the risk in one line, and the record's `Decisions:` says "track set by the
  user".
```

**AFTER** (fix round, Stage 4 P2 findings: new bullet in `## Switching track` of `docs/claude-md/tracks.md`, directly after the "moves a task **up**" bullet, plus one clause in row 6 of `### Every user stop and its auto rule`; the other bullets and rows are unchanged):

```
- When a task moves up, or when `verify` returns `fail` (not `blocked`), the Supervisor first raises the
  effort of the next spawn by one step on the ladder `low`, `medium`, `high`, `xhigh`, `max`. The count
  starts from the effort of the task's last spawn, or for the first raise from the cell of its Complexity in
  `## CLI Effort Table`, so two failures raise two steps. This comes before it changes the model, splits the
  task or moves any other lever. At `max`, or with an empty or missing cell, the rule changes nothing and
  the other levers apply; the Supervisor never lowers effort on its own.
```

Row 6 rule cell, new tail: `... No row or an empty cell: row 14. Also read the `## CLI Effort Table`: an empty effort cell means no effort is passed, not a stop.`

**DELTA**: The Supervisor now has a written rule to raise effort one step (from the last spawn's effort, stopping at `max` or at an empty cell) before it changes the model or splits the task, whenever a task moves up or `verify` returns `fail`; an empty effort cell is not a stop.

**WITNESS**: Implemented by the common-infrastructure sub-agent on 2026-11-09 (first round, then a fix round: tests red before, green after; every mutation control red then restored green). To be confirmed by the reviewer from `memory/event-trace/T299.jsonl`.
