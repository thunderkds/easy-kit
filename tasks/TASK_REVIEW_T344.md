# TASK_REVIEW — T344: `site/docs.html` gets a Change log section listing every release

> Sibling of `tasks/TASK_GUIDE_T344.md`. Everything here is **filled by the reviewer at Stage
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
9. Six change-log titles that the live-docs tests reject (old repo name, old stage names, a removed flag and path, a doctrine section in `CLAUDE.md`) are reworded in `REWRITES`, and the v2.0.0 summary drops `setup.sh --harness`; the four tests stay unchanged — RULE: the Stage 4 review's P1 (`tasks/TASK_REVIEW_T344.md` § Stage 4 review (Reviewer: T344)): "add rewrites for these titles. Do not allowlist the pins".
10. The completeness test pins a floor of the 263 tasks known at T344's start; any board task may be listed; T344's own line joins Unreleased — RULE: `tasks/TASK_GUIDE_T344.md` § Approach cut list ("the change log is a snapshot. A later task adds its own line by hand"); fixes the review's P1 that the test turned red when T344 (or any task) closed.
11. `tests/test_repo_name.py` `ALLOWED` gains `tests/test_site_changelog.py`, whose `BANNED` pattern names the old repo to keep it off the page — RULE: `tests/test_repo_name.py:3` "no live file names the old repo, outside history paths and the allow list below".
Checks: site + live-docs tests `273 passed, 18 skipped` after the Stage 4 fixes; full suite: rerun on the fix commit; reviews: inline `code-review` (1 P1, 2 P3) and `Reviewer: T344` at `82e736b9` (2 P1, 3 P2, 5 P3), all P1 fixed, a second fresh reviewer on the fix commit; real run: Playwright at 1280px and 375px, no sideways scroll — auto-checked, not /verify.
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule ("a UI component" → extended): a new section on `site/docs.html`.
2. Page `site/docs.html`, scope every release plus Unreleased — RULE: the user's forced-choice answers in chat, 2026-11-20: "docs.html (Recommended)", "Every release (Recommended)" (`tasks/TASK_GUIDE_T344.md` § Questions Log).
3. No task ID anywhere on the page; 40 titles that carry an ID or a board word are reworded (`tests/test_site_changelog.py` `REWRITES`) — RULE: the user's answer "No IDs at all", 2026-11-20, keeping `tests/test_site_content.py:224` "page must not contain a task ID" (T083).
4. Eight tasks the RUNBOOK says shipped but with no board row are listed, titled from their guide; T086 (no guide, superseded by T089) and T184 (board row not Done, "closed, will not do") are left out — RULE: the user's request "add all of them" and `RUNBOOK.md` § Release Log (`tasks/TASK_GUIDE_T344.md` AC 5).
5. `site/index.html` untouched; `tests/test_site_story.py` leaves `#changelog` out of the redirect-list comparison instead — RULE: `tasks/TASK_GUIDE_T344.md:166` "`site/index.html` | out of scope" (the user rejected the tool call that edited it).
6. A long path wraps at 375px through `<wbr>` hints in code spans, not CSS — RULE: `tasks/TASK_GUIDE_T344.md:108` "no new CSS rule and no inline `style=`".
7. The Supervisor wrote the code; one fresh `Reviewer: T344` spawn reviews it — RULE: `AGENTS.md:171` "On the extended track the Supervisor writes the code itself" (T341, merged).
8. The first reviewer spawn named a hand-extended commit hash; it was stopped and respawned with the real hash `82e736b9991205d8bdbc9446aebaccdfd1b1135b` — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4 (the `Commit:` line is the full hash of the commit reviewed).
Checks: Verification Command `231 passed, 18 skipped` at `82e736b9`; full suite: running; review: `Reviewer: T344` running; real run: Playwright screenshots at 1280px and 375px, no sideways scroll at 375px — auto-checked, not /verify.
Memory: nothing new yet (pass runs after the merge)
Not done: Stage 4 review result, Evidence rows, merge (admin: after the auto verify pass); auto verify: not started
Paused: auto-mode check failed — no test run in memory/event-trace/T344.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T344" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop [report 371f46c7515c]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
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

**BEFORE**: the Supervisor, before any implementation commit, on `feat/t344-changelog` at `d2499ce9108fd4e27e04616a26049c44b9534175` (`site/docs.html` unchanged), the new test against the unchanged page:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; uv run --with pytest python -m pytest tests/test_site_changelog.py -q -p no:cacheprovider
2026-11-20T15:09:44Z
d2499ce9108fd4e27e04616a26049c44b9534175
FAILED tests/test_site_changelog.py::test_ac1_the_section_has_its_heading_after_options_and_before_the_footer
FAILED tests/test_site_changelog.py::test_ac1_the_reference_nav_group_ends_with_the_changelog_link
FAILED tests/test_site_changelog.py::test_ac2_one_entry_per_release_newest_first_only_unreleased_open
FAILED tests/test_site_changelog.py::test_ac2_each_summary_gives_its_task_count
FAILED tests/test_site_changelog.py::test_ac2_each_released_summary_gives_a_date
FAILED tests/test_site_changelog.py::test_ac5_every_done_task_on_the_board_appears_exactly_once
FAILED tests/test_site_changelog.py::test_ac5_tasks_are_in_id_order_inside_each_entry
FAILED tests/test_site_changelog.py::test_ac4_each_task_shows_its_board_title_escaped_with_code_spans
FAILED tests/test_site_changelog.py::test_ac3_the_section_copies_no_email_address
9 failed, 1 passed in 0.06s
```

The one pass is `test_ac4_render_title_escapes_and_keeps_code_spans`, a pure helper check. The page has no `#changelog` section and no sidebar link.

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T344.jsonl`, never the
implementing agent alone]

## Stage 4 review (Reviewer: T344)

Reviewer: T344 · Commit reviewed: `82e736b9991205d8bdbc9446aebaccdfd1b1135b` (`main...82e736b`, 6 files, +543/-8) · Worktree `wt-t344`, branch `feat/t344-changelog` · Risk Low, so `security-review` not required.
The `code-review` skill could not be started from this sub-agent (no Skill tool), so the review was done by hand, with the same P0-P3 scale. Read-only except this section.

**Verdict: FAIL for merge as it stands. 0 P0, 2 P1, 3 P2, 5 P3.** Both P1 are small fixes; the section itself is correct (placement, titles, layout all verified).

### Findings

| # | Sev | Finding | Where | Fix |
|---|-----|---------|-------|-----|
| 1 | P1 | The change adds 4 failures to the full suite. Full run `.claude/hooks/tests tests` on `main` (d2499ce): 54 failed. Same run on the branch: 58 failed. The 4 new: `tests/test_agents_md_primary.py::test_ac9_no_shipped_text_points_at_a_claude_md_section` (title "Dedup the `## Skills vs Agents` section in CLAUDE.md"), `tests/test_docs_match_installer.py::test_live_docs_show_no_install_flags` (`--harness` at `site/docs.html:4156`, `:4166`; `~/.supervisor` at `:4212`), `tests/test_repo_name.py::test_no_live_file_names_the_old_repo` (`:4021` "Rename the repo from personal-agentic-claude to easy-kit"), `tests/test_stage_names.py::test_ac1_no_old_stage_name_is_left_outside_history_and_the_mapping_note` (`:4008` "Stage 0.5/1", `:4202` "Stage 1.5 wiring"). The guide's Test Plan says to compare the full failing set with the `main` baseline; the baseline must not grow. AC 7 names only 4 site test files, so those pass, but these 4 guard `site/docs.html` content. | `site/docs.html:4008,4021,4156,4166,4202,4212` and the Unreleased/v2.0.0/v1 entries around them; `REWRITES` in `tests/test_site_changelog.py` | Reword the 6 titles in `REWRITES` (add them there; `test_ac4_rewrites_cover_exactly_the_titles_that_break_the_page_rule` then needs its `BANNED` pattern widened, or make the rewrites avoid the banned wording) — never allowlist the pins. |
| 2 | P1 | The new test goes red when T344 itself closes. `_done_titles()` reads the live board; the T344 row becomes `- [x]` at auto close-out, but T344's own title is not in the page (105 + 80 + 45 + 17 + 16 = 263 = the floor, T344 excluded). Simulated in a scratch copy with only the T344 row flipped to `[x]`: `FAILED test_ac5_every_done_task_on_the_board_appears_exactly_once`, "Done on the board but not in the change log: ['T344']". CI re-runs a task's Verification Command when a PR moves it to Done, so the close-out PR would be red. | `tests/test_site_changelog.py:182-192`; `site/docs.html` Unreleased list | Add T344's own line to the Unreleased list (106 tasks, summary and `FLOOR_COUNT` 264) before it moves to Done. |
| 3 | P2 | AC 4 as written (`<li><code>Txxx</code> — <title></li>`) is not what the page shows: no task ID is on the page. The cause is the existing T083 pin `tests/test_site_content.py:222-224` (`page must not contain a task ID`). The user's "No IDs at all" is recorded only in the Supervisor's uncommitted `## Auto decisions` #3 and in the test docstring (`tests/test_site_changelog.py:8-9,29-30`), not in the guide: AC 4 and AC 5 ("in ID order", `Txxx`) and the Questions Log still say IDs. | `tasks/TASK_GUIDE_T344.md` AC 4, AC 5 | Amend AC 4 and add a Questions Log line with the user's answer. I cannot confirm the quote from the repo. |
| 4 | P2 | Hidden upkeep cost beyond the one the guide accepted. The guide accepts that a later Done row fails the test until it is listed. A second coupling is not recorded: any new Done title with a task ID, "KANBAN", "In Progress", "Ready for Review", `**` or a hex colour fails `test_ac4_rewrites_cover_exactly_the_titles_that_break_the_page_rule` until `REWRITES` gains an entry. 40 of 263 titles (15%) already needed one, so most releases will hit it. | `tests/test_site_changelog.py:72,173-175` | Say it in the guide's cut list / the test docstring (one line). No code change needed. |
| 5 | P2 | The guide's Test Plan baseline ("54-test `main` baseline") was true when written and is still true on `main` d2499ce (re-run: 54), so finding 1 is a real regression and not baseline drift. No evidence in the branch that the implementer ran the full suite: `## Auto decisions` still says "full suite: running". | `tasks/TASK_REVIEW_T344.md` Auto decisions Checks line | Run it after the P1 fixes and paste the failing-set diff. |
| 6 | P3 | AC 3 says each released entry starts with "one sentence". v2.2.0 (`site/docs.html:4082`) and v2.0.0 (`:4156`) have three; v1 and v2.1.0 have one (v1 is one long sentence with a semicolon). Content matches `RUNBOOK.md` Release Log; the Deployer email and Approved column are not copied. | `site/docs.html:4082,4156` | Loosen the AC to "a short summary", or trim. |
| 7 | P3 | AC 6 says "the section holds no `@` character". The section holds one: `<code>@AGENTS.md</code>` (task title for the `CLAUDE.md` import). The test checks an email pattern instead (`tests/test_site_changelog.py:213-215`), which is the sensible check. | `tasks/TASK_GUIDE_T344.md` AC 6 | Reword the AC to "no email address". |
| 8 | P3 | AC 7 asks for a `CHANGED_BY_T344` record for a repointed baseline. None exists (`grep CHANGED_BY_T344` finds nothing). Two pins were repointed inline with a `# T344 ...` comment (`tests/test_site_story.py:486-487,614-616`, `tests/test_site_content.py:1951-1952`). The sentence baseline itself did not change, so no record is needed; the inline form is fine. | AC 7 wording | Reword AC 7. |
| 9 | P3 | Two `REWRITES` shift meaning slightly (see the table below): T157 "my In Progress tasks" became "my own open tasks" (open also covers Todo); T101 dropped the T097 half ("the pre-T096/T097 world" became "the layout from before the canon move", so the per-harness install projection is no longer implied). | `tests/test_site_changelog.py:41,49` | T157: "only the tasks I am working on block my push". T101: "...from before the canon move and the per-CLI install, in four places". |
| 10 | P3 | Style: two functions follow each other with one blank line instead of two (`tests/test_site_changelog.py:193-194,199-200`); the AC section comment above `test_ac4_rewrites_cover...` says `# ---- AC 5` while the test is AC 4. | `tests/test_site_changelog.py` | Tidy. |

### Acceptance Criteria

| AC | Verdict | Evidence |
|----|---------|----------|
| 1 | PASS | `site/docs.html:3966` `<section id="changelog">` + `<h2>Change log</h2>`; after `<section id="options">` (`:3954`) and before `<footer>` (`:4264`); sidebar `:253` `<li><a href="#changelog">Change log</a></li>` is last in `// reference` (test `test_ac1_*` pass). Screenshot 1280px: "Change log" last, highlighted after click. |
| 2 | PASS | Five `<details>` in order `Unreleased` (`:3969`, `open`), `v2.2.0` `:4081`, `v2.1.0` `:4104`, `v2.0.0` `:4155`, `v1` `:4177`; dates 2026-10-28, 2026-10-19, 2026-09-05, 2026-08-21 equal the tag commit dates (`git log -1 --format=%cs <tag>`); counts 105/17/45/16/80 equal the `<li>` counts. Playwright: `opens: [true,false,false,false,false]`. |
| 3 | PASS (P3 #6) | Summaries match `RUNBOOK.md` Release Log; no Deployer or Approved text; no email (`@` only in `@AGENTS.md`). Unreleased summary (not in the log) checks out: `[admin]`/`[ticket]`/`[stop]` are in `docs/claude-md/tracks.md`, DDR-0011 exists (`docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md`). |
| 4 | FAIL as written, PASS in substance (P2 #3) | No `<code>Txxx</code>` prefix; forced by the T083 pin `tests/test_site_content.py:222-224`. Titles are the board titles, HTML-escaped (`&lt;ID&gt;`), backticks as `<code>`. `<wbr>` hints added after `/` and `_` in code spans (79 of them). |
| 5 | PASS | Independent recompute (own script, not the Supervisor's): a task named in a RUNBOOK scope (before "Not in scope") goes to that release; else the earliest tag containing the first commit that added `- [x] **Txxx**` to the board (`git log --diff-merges=first-parent -p`). Result 80/16/45/17/105 = 263 (255 Done + the 8 guide-only tasks). Per-task comparison against the page: 263 of 263 in the same release, no extra, no duplicate. T086 and T184 absent. |
| 6 | PASS (P3 #7) | `tests/test_site_changelog.py` pins AC 1, 2, 5, 4-escaping and no-email; 12 tests. Mutation (scratch copy, one `<li>` deleted): `test_ac2_each_summary_gives_its_task_count` and `test_ac5_every_done_task_on_the_board_appears_exactly_once` fail. |
| 7 | PASS (P1 #1 is outside AC 7's list) | `uv run --with pytest python -m pytest tests/test_site_changelog.py tests/test_site_content.py tests/test_site_story.py tests/test_site_visual_first.py tests/test_site_explorer.py -q -p no:cacheprovider` printed `231 passed, 18 skipped in 0.85s`. |

### The 40 `REWRITES` titles

I compared all 40 with the board title (and the T120/T250 long ones in full). 38 keep the meaning. The 2 with a slight shift are T157 and T101 (finding 9). Fine detail checked: T019, T021, T036, T038, T046, T057, T063, T069, T099, T103, T120, T123, T130, T151, T153 (`T142` became "kit IDs", `ENG-170` kept), T156, T161, T180, T186, T203, T208, T212 (hex dropped), T215, T220, T229, T230, T242, T244, T246, T248, T250 (three fixes kept), T251, T252, T285, T290, T302, T303. Dropped text is only IDs, line numbers and side detail; no claim was reversed. Note T252 and T229 state the fix where the board states the problem; acceptable for a Done task.

### UI / Design Acceptance Criteria

Method: headless Chromium shell 1248 via Playwright, `file://` `site/docs.html`, viewports 375x800 and 1280x900, section reached by clicking the sidebar link at 1280px (hash at 375px, the sidebar is a menu there). Screenshots: `/tmp/claude-1000/-home-thunderkds-workspace-pets-hungnguyen111-easy-kit/4e0cb7e2-077e-4b1d-bf64-6baa9212ca72/scratchpad/cl_1280_open.png`, `cl_375_open.png`, `cl_1280_v21.png`, `cl_375_v21.png` (same folder).

| Row | Verdict | Evidence |
|-----|---------|----------|
| Visual regression | PASS | `<h2>` computed size 20px, equal to `#options` h2; the `<details>` frame, summary and code chips match the page's other fold-outs. The diff adds 299 lines and deletes 0 in `site/docs.html`, so no other section changes. Clicking the `v2.1.0` summary opens it (`open: true`) and shows its sentence and 45 tasks. |
| Design-system compliance | PASS | The section holds no `style=` and no `class=`; `site/theme.css` is not in the diff. Only existing elements (`h2`, `details`, `summary`, `p`, `ul`, `li`, `code`, `wbr`). |
| Responsiveness | PASS | 375px: `scrollWidth 375 = clientWidth 375`, 0 elements past the right edge, also with all five entries open; long titles and code spans wrap. 1280px: `scrollWidth 1280`, section in the main column, sidebar link visible and highlighted. |
| UX story 1 (click "Change log") | PASS | Section top lands at ~80px under the sticky header; Unreleased open, four closed rows with date and count. |
| UX story 2 (open `v2.1.0`) | PASS | Opens, shows the RUNBOOK sentence (online board mode) and its task list. |

### Evidence

- Verification Command (guide): `231 passed, 18 skipped in 0.85s`.
- Full suite (`.claude/hooks/tests tests -rf`), `main` d2499ce: 54 failed. Branch `82e736b`: 58 failed (`7664 passed`). Diff of the failing sets: only the 4 tests in finding 1.
- Mutation with `git diff --stat`: scratch copy at `/tmp/claude-1000/-home-thunderkds-workspace-pets-hungnguyen111-easy-kit/4e0cb7e2-077e-4b1d-bf64-6baa9212ca72/scratchpad/sim` (one `<li>` removed from `site/docs.html`): 2 failed, 10 passed. T344 row set to `[x]` in the same copy: 1 failed (`test_ac5_every_done_task...`, `['T344']`).
- Not run: `ux-evaluate` skill (not available here); `security-review` (Risk Low); the hook-written `verify` row stays the hook's.
- The working-tree `tasks/TASK_REVIEW_T344.md` held uncommitted Supervisor edits (`## Auto decisions`) while this review ran. They are left as they were; only this section is committed.
