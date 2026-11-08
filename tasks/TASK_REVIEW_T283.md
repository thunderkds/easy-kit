# TASK_REVIEW — T283: Karpathy autoresearch loop — seven spikes with evidence

> Sibling of `tasks/TASK_GUIDE_T283.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_spike_report_t283.py` (6 tests incl. 4 mutation controls); each spike branch holds its own test (`spike/t283-*`: `spike/test_*.py` or `tests/test_spike_*_t283.py`) |
| Verification command run | ☑ pass | 2026-11-08 `python3 -m pytest tests/test_spike_report_t283.py -q` — `6 passed`; `git diff --name-only main...HEAD` — `tasks/SPIKE_REPORT_T283.md`, `tasks/TASK_REVIEW_T283.md`; all 7 `spike/t283-*` exist and none is an ancestor of `main` |
| Negative cases hold | ☑ pass | BEFORE: report absent → `1 failed, 5 passed` (the real-report test red). The oracle's own mutation controls (blank field, toy baseline, bad verdict, missing idea) each fail the validator. Each spike's mutation diff and red run are pasted in its report section |
| verify | ☑ pass | /verify T283 typed by the user in session 9e7b73f3-3c09-4250-86c1-dac31ab338c5 (2026-11-08), commit 880e93b716f362f3a267bd0aefd39a79eb8e19c8: verdict SKIP, no runtime surface (a report and its review file only; `git diff main...feat/t283-karpathy-spikes --stat` lists `tasks/SPIKE_REPORT_T283.md` and `tasks/TASK_REVIEW_T283.md`). The headless run on this commit answered blocked (no single verdict line); the user's typed `/verify T283` is the pass for a docs-only task. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the two files in the diff against the guide's AC 1–7. Not reviewed: the throwaway spike scripts on `spike/t283-*` (never merged; guide marks them throwaway) |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q` in `../wt-t283` — `3442 passed, 25 subtests passed in 215.53s` |
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

**BEFORE**: captured by Run A (common-infrastructure) at `2026-11-07T23:25:05Z` (`date -u`), in
`/home/hungnguyenhuu/workspace/pets/wt-t283` on `feat/t283-karpathy-spikes` at `faa5180f`, before any spike
commit exists. The task changes no executable code on `main`, so BEFORE is the oracle run red with no report:

```
$ python3 -m pytest tests/test_spike_report_t283.py -q
E       assert False
E        +  where False = exists()
E        +    where exists = PosixPath('/home/hungnguyenhuu/workspace/pets/wt-t283/tasks/SPIKE_REPORT_T283.md').exists

tests/test_spike_report_t283.py:134: AssertionError
=========================== short test summary info ============================
FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid - Asser...
1 failed, 5 passed in 0.03s
```

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
