# TASK_REVIEW — T322: site/docs.html explains the session tags

> Sibling of `tasks/TASK_GUIDE_T322.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | tests/test_t322_session_tags_docs.py: 4 failed (red, before the paragraph), then 4 passed in 0.02s |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q` — 7497 passed, 5 skipped, 87 subtests passed in 386.65s |
| Negative cases hold | ☑ pass | red run 4 failed against prior content (no Session tags p); diff +8 lines in site/docs.html |
| verify | ☑ pass | auto-run by hook, session 17d92b9f-8bd4-4dc7-b501-59605bd349df, commit fff1e7446fbe335b4f43e24c95926ccaee6c9a30, log .claude/verify-runs/T322-fff1e7446fbe.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff main...HEAD`: site/docs.html (one new <p> in #tracks details), tests/test_t322_session_tags_docs.py, this file, the guide's pin row. Wording checked line by line against `docs/claude-md/tracks.md` 877–937. Nothing else in scope (no code, no hook) |
| Full smoke suite still green (no regression) | ☑ pass | 7497 passed, 5 skipped |
| **Companion score (easy-verifier)** | ☑ N/A | not run: C1 / Risk Low docs-only change; optional tool |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | ux-evaluate (formal, no UX rows: baseline checks only), #tracks Details open, screenshots /tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/8147f53b-32a0-4c0c-9272-6a5901bdfcc0/scratchpad/ux/t-375.png, /tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/8147f53b-32a0-4c0c-9272-6a5901bdfcc0/scratchpad/ux/t-1280.png (375 is a real 375px-wide capture with scrollbars kept; 1280 hidden scrollbars). U1 pass at 375 and 1280: Session tags p has the same type, spacing and code style as the Close-out p above it. B-a/B-b/B-c/B-e/B-i pass; B-f/B-g not applicable (static text). ux-evaluate: 9 baseline pass (B-f, B-g n/a), 0 fail. Overall: pass |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | U2 pass: diff has only p, strong, code; 0 class=/style= additions. B-i pass: same accent and code style as neighbours. B-d pass: tap_probe run (/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/8147f53b-32a0-4c0c-9272-6a5901bdfcc0/scratchpad/ux/open-probe.html, shot p-375.png); the block has no tap target besides the Details summary, no red box in the block |
| **UI: Responsiveness at target viewports** | ☑ pass | U3 pass: 375 real viewport (--window-size=375, scrollbars kept): no horizontal scrollbar at the bottom of t-375.png; long code strings (settings-setup, permissions.defaultMode: "auto") wrap. 1280: paragraph stays in the 650px text column, no overflow. B-h pass |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Non-executable change (docs). Verbatim prior content: the `#tracks` `<details class="more">` of `site/docs.html` ends with the Close-out paragraph, whose last sentence is: "The `[admin]` merge and push also refuse when the repo config holds a key that can run code or reach another host, such as a merge driver, a filter or `core.hooksPath`; the refusal names the key." followed directly by `</p></details>`. `grep -c "\[ticket\]" site/docs.html` gives 0; `[stop]` is absent too. (Captured 2026-11-16 before any implementation commit.)

**AFTER**: the `#tracks` details block gains `<p><strong>Session tags</strong>: <code>[ticket]</code> and <code>[admin]</code> hold for the whole session. … The kit never sets <code>bypassPermissions</code>.</p>` (8 lines, see `git diff site/docs.html`).

**DELTA**: a reader of `site/docs.html` can now learn that `[ticket]` and `[admin]` last the whole session, how `[stop]` ends them, what the board loop pushes or merges after a pass, and that Bash without prompts needs the `autonomous` profile; before, no site page named `[ticket]` or `[stop]`.

**WITNESS**: Supervisor, 2026-11-16, read `git diff main...HEAD -- site/docs.html` (commits e2cc4089, 4dd257f6) against tracks.md `### Session tags`; frontend-developer ran the tests and ux-evaluate (above).

### Re-run after review fixes (2026-11-16)

`python3 -m pytest tests/test_t322_session_tags_docs.py tests/test_site_visual_first.py tests/test_site_story.py tests/test_site_content.py -q -p no:cacheprovider` — 217 passed in 0.87s

## Stage 4 — code-review (Supervisor, 2026-11-16)

lane: C1, 3 files, 54 lines, FITS; unpredicted: tasks/TASK_GUIDE_T322.md (the pin-test row the guide asks the implementer to fill — expected)
Entry point `site/docs.html#tracks` Details: found. Stale-reference sweep: no other page or doc lists the tags.

| Sev | File:line | Finding | Conf | Outcome |
|---|---|---|---|---|
| P1 (process) | agent report | `Startup reads:` misses `PROJECT_SPEC.md` and `agents/frontend.md` (Permanent Rule reads), on both passes | 100 | recorded; no effect on a docs-only <p> checked line by line by the Supervisor |
| P2 | site/docs.html:473 | "The Supervisor then works the board" read as starting after the tag ends | 100 | fixed in 4dd257f6 ("While a session tag holds, …") |
| P2 | UI Evidence | ux-evaluate not run formally; 375px read from a ~485px window | 75 | fixed in 4dd257f6 (formal ux-evaluate, real 375 viewport) |

Totals: P0 0 · P1 1 (process) · P2 2 (both fixed) · P3 0. security-review: not required (Risk Low).
