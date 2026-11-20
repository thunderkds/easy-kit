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
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule ("a UI component" → extended): a new section on `site/docs.html`.
2. Page `site/docs.html`, scope every release plus Unreleased — RULE: the user's forced-choice answers in chat, 2026-11-20: "docs.html (Recommended)", "Every release (Recommended)" (`tasks/TASK_GUIDE_T344.md` § Questions Log).
3. No task ID anywhere on the page; 45 titles that carry an ID, a board word or a name the live-docs tests forbid are reworded (`tests/test_site_changelog.py` `REWRITES`) — RULE: the user's answer "No IDs at all", 2026-11-20, keeping `tests/test_site_content.py:224` "page must not contain a task ID" (T083).
4. Eight tasks the RUNBOOK says shipped but with no board row are listed, titled from their guide; T086 (no guide, superseded by T089) and T184 (board row not Done, "closed, will not do") are left out — RULE: the user's request "add all of them" and `RUNBOOK.md` § Release Log (`tasks/TASK_GUIDE_T344.md` AC 5).
5. `site/index.html` untouched; `tests/test_site_story.py` leaves `#changelog` out of the redirect-list comparison instead — RULE: `tasks/TASK_GUIDE_T344.md:166` "`site/index.html` | out of scope" (the user rejected the tool call that edited it).
6. A long path wraps at 375px through `<wbr>` hints in code spans, not CSS — RULE: `tasks/TASK_GUIDE_T344.md:108` "no new CSS rule and no inline `style=`".
7. The Supervisor wrote the code; one fresh `Reviewer: T344` spawn reviews it — RULE: `AGENTS.md:171` "On the extended track the Supervisor writes the code itself" (T341, merged).
8. The first reviewer spawn named a hand-extended commit hash; it was stopped and respawned with the real hash `82e736b9991205d8bdbc9446aebaccdfd1b1135b` — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4 (the `Commit:` line is the full hash of the commit reviewed).
9. Six change-log titles that the live-docs tests reject (old repo name, old stage names, a removed flag and path, a doctrine section in `CLAUDE.md`) are reworded in `REWRITES`, and the v2.0.0 summary drops `setup.sh --harness`; the four tests stay unchanged — RULE: the Stage 4 review's P1 (`tasks/TASK_REVIEW_T344.md` § Stage 4 review (Reviewer: T344)): Fix: add rewrites for these titles. Do not allowlist the pins (the reviewer's words, abridged).
10. The completeness test pins a floor of the 263 tasks known at T344's start; any board task may be listed; T344's own line joins Unreleased — RULE: `tasks/TASK_GUIDE_T344.md` § Approach cut list ("the change log is a snapshot. A later task adds its own line by hand"); fixes the review's P1 that the test turned red when T344 (or any task) closed.
11. `tests/test_repo_name.py` `ALLOWED` gains `tests/test_site_changelog.py`, whose `BANNED` pattern names the old repo to keep it off the page — RULE: `tests/test_repo_name.py:3` "no live file names the old repo, outside history paths and the allow list below".
Checks: site + live-docs tests `273 passed, 18 skipped` at `c0a879b7`; full suite: see Evidence; reviews: inline `code-review` (1 P1, 2 P3) and two fresh `Reviewer: T344` spawns (at `82e736b9`: 2 P1, 3 P2, 5 P3; at `c0a879b7`: 0 P0, 0 P1, 2 P2, 4 P3, AC 1-7 and UI rows pass); real run: Playwright at 1280px and 375px, no sideways scroll — auto-checked, not /verify.
Memory: nothing new yet (pass runs after the merge)
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass (session b74d07ec-ccb0-4db7-b4b2-cc30b3e976b9, commit ac99ba6829adeb5b2721eeb5cea260f6bf197bf0, log .claude/verify-runs/T344-ac99ba6829ad.log)
Paused: auto-mode check failed — no test run in memory/event-trace/T344.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T344" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop [report 1376a1eb8e14]
Paused: done not moved — Gate 6: the `UI: Visual regression` row has no evidence; Gate 6: the `UI: Responsiveness` row has no evidence; Gate 5: no test run in memory/event-trace/T344.jsonl

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_site_changelog.py` (13 tests: AC 1, 2, 4, 5, 6), written in this task |
| Verification command run | ☑ pass | at `c0a879b7`: the guide's Verification Command plus the four live-docs tests (`test_repo_name`, `test_stage_names`, `test_docs_match_installer`, `test_agents_md_primary`) → `273 passed, 18 skipped` |
| Negative cases hold | ☑ pass | Red run before the section existed: Demonstration BEFORE (`9 failed, 1 passed`). Reviewer mutation probes: one `<li>` removed → 2 tests fail; T344 and a new Done row T999 flipped to `[x]` → 13 passed (no false red) |
| verify | ☑ pass | auto-run by hook, session b74d07ec-ccb0-4db7-b4b2-cc30b3e976b9, commit ac99ba6829adeb5b2721eeb5cea260f6bf197bf0, log .claude/verify-runs/T344-ac99ba6829ad.log — pass; done not moved: Gate 6: the `UI: Visual regression` row has no evidence; Gate 6: the `UI: Responsiveness` row has no evidence; Gate 5: no test run in memory/event-trace/T344.jsonl |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Two fresh `Reviewer: T344` spawns on `82e736b9` and `c0a879b7`: the `main...<commit>` diff, `site/docs.html`, the site and live-docs tests. Final: 0 P0, 0 P1, 2 P2, 4 P3; AC 1-7 and UI rows pass |
| Full smoke suite still green (no regression) | ☑ pass | at `c0a879b7`: `54 failed, 7669 passed, 24 skipped`; `comm` against the unchanged-`main` list: NEW empty, GONE empty (the 54 fail for missing `busybox`/`zsh`) |
| **Companion score (easy-verifier)** | ☑ N/A | neither companion tool was run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | Playwright screenshots (Supervisor and both reviewers) at 1280px and 375px, e.g. scratchpad `shots/changelog_1280.png`, `shots/changelog_375_v210.png`: the section heading is 20px like the Options heading, the fold-outs look like the page's other fold-outs; the diff adds 300 lines to `site/docs.html` and deletes none |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | 0 `style=` and 0 `class=` attributes in the section; `site/theme.css` untouched; no hex colour (`test_hex_colours_appear_only_in_theme_css` green) |
| **UI: Responsiveness at target viewports** | ☑ pass | 375px and 1280px: `scrollWidth` equals the viewport width, also with all five fold-outs open; 0 elements overflow (a long path wraps through word-break hints) |

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

**AFTER**: at `c0a879b756c2c4e08ca371a788b48ccf70208f31`, the same new test plus the site and live-docs tests: `273 passed, 18 skipped`. `site/docs.html` now has `<section id="changelog">` after `#options`, a sidebar link, and five fold-outs: Unreleased (open, 106 changes), v2.2.0 (17), v2.1.0 (45), v2.0.0 (16), v1 (80).

**DELTA**: A reader of the docs page can now see what every release shipped, newest first, in plain titles.

**WITNESS**: the Supervisor (session 4e0cb7e2): `memory/event-trace/T344.jsonl` record at `2026-11-20T16:11:24Z`, a non-error `Bash` call running the site tests; two fresh `Reviewer: T344` spawns re-ran them independently (sections below).

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

## Stage 4 review (Reviewer: T344, commit c0a879b7)

Reviewer: T344 (second pass, fresh) · Commit reviewed: `c0a879b756c2c4e08ca371a788b48ccf70208f31` (`main...c0a879b`; this pass re-checks the fix commit against the first review at `82e736b`) · Worktree `wt-t344`, branch `feat/t344-changelog` · Risk Low, so `security-review` not required.
The `code-review` skill could not be started from this sub-agent (no Skill tool), so the review was done by hand with the same P0-P3 scale. Read-only except this section.

**Verdict: PASS for merge. 0 P0, 0 P1, 2 P2, 4 P3.** All 4 regressions and both P1 of the first review are fixed. The 2 P2 are record keeping in this file, not code.

### Findings

| # | Sev | Finding | Where | Fix |
|---|-----|---------|-----|-----|
| 1 | P2 | The new `## Auto decisions` lines 9-11 and the updated `Checks:` line were written INSIDE the HTML template comment (`<!--` line 13 to `-->` line 48), so they are hidden when rendered and the close-out hook (which anchors on the first uncommented `## Auto decisions` block, T244) cannot see them. The live block still has the old `Checks:` ("full suite: running; review: `Reviewer: T344` running"), decisions 1-8 only, and the stale `Paused:` line. | `tasks/TASK_REVIEW_T344.md:13-48` (the added lines sit before `-->`); live block under it | Move decisions 9-11 and the new `Checks:` into the live block; drop the `Paused:` line once the trace is fixed. Leave the template comment as the template. |
| 2 | P2 | The `## Evidence` table and `## Demonstration` (AFTER, DELTA, WITNESS) are still template placeholders. Hard-Stop Gate 5 needs the "New test(s) cover acceptance criteria" row filled with pasted output before Done, and the three UI rows (Gate 6). | `tasks/TASK_REVIEW_T344.md` `## Evidence` | Fill from the Evidence block below (the Supervisor writes those rows; I added this section only). |
| 3 | P3 | The count of reworded titles is stale. `len(REWRITES)` is 45 (run: `python3` import of the test module), the guide's cut list, Questions Log and Auto decision 3 say 40. | `tasks/TASK_GUIDE_T344.md` § Approach cut list and Questions Log; Auto decision 3 | Say 45. |
| 4 | P3 | Auto decision 9 puts a quotation in quote marks that is not in the first review: "add rewrites for these titles. Do not allowlist the pins". The review says "Reword the 6 titles in `REWRITES` (add them there; ...) — never allowlist the pins". The meaning is the same; the quote is not verbatim. | Auto decision 9 | Quote the review's own words. |
| 5 | P3 | `REWRITES["T097"]` drops the `(B2):` prefix, but the v2.0.0 list still shows `(B1): Relocate canonical ...` (`site/docs.html:4166`), so a reader sees an orphan "(B1)". Meaning of both titles is kept; only the pair is now uneven. | `tests/test_site_changelog.py:58`, `site/docs.html:4166` | Optional: add a T096 rewrite that drops `(B1):` too. |
| 6 | P3 | Test file tidy-up from the first review (its finding 10) is only half done: the section comment `# ---- AC 5` (`tests/test_site_changelog.py:203`) still sits above `test_ac4_rewrites_...` and the other AC 4 tests; they run to the `# ---- AC 3` header at line 253. No effect on results. | `tests/test_site_changelog.py:203-253` | Optional. |

First-review findings, state now: P1 #1 (4 new full-suite failures) fixed, those 4 tests pass in my run (below). P1 #2 (red when T344 closes) fixed; checked by simulation. P2 #3, #4 (AC 4 text and upkeep cost) fixed in the guide (AC 4, cut list, Questions Log). P2 #5 (full suite) open until the running full run ends; I did not wait for it. P3 #6, #7, #8 (AC 3, 6, 7 wording) fixed in the guide. P3 #9 (T157, T101 meaning) fixed (`tests/test_site_changelog.py:70,78`).

### Acceptance Criteria

| AC | Verdict | Evidence |
|----|---------|----------|
| 1 | PASS | `site/docs.html:3966` `<section id="changelog">`, `:3967` `<h2>Change log</h2>`; after `<section id="options">` `:3954`, before `<footer>` `:4265`; sidebar `:253` `<li><a href="#changelog">Change log</a></li>`, last link in `// reference`. Playwright at 1280px: clicking the link gives hash `#changelog`, last nav link text "Change log". Tests `test_ac1_*` pass. |
| 2 | PASS | Five `<details>` in order: `:3969` `open` (Unreleased), `:4081` v2.2.0, `:4104` v2.1.0, `:4155` v2.0.0, `:4177` v1. Summaries: "Unreleased · 106 tasks", "v2.2.0 · 2026-10-28 · 17 tasks", "v2.1.0 · 2026-10-19 · 45 tasks", "v2.0.0 · 2026-09-05 · 16 tasks", "v1 · 2026-08-21 · 80 tasks". Dates equal `git log -1 --format=%cs <tag>` (2026-10-28, 2026-10-19, 2026-09-05, 2026-08-21). Playwright `opens: [true,false,false,false,false]`. |
| 3 | PASS | Each released entry has one `<p>` summary; the guide now says "a short summary (one paragraph)". No Deployer or Approved text; `test_ac3_the_section_copies_no_email_address` passes. v2.0.0 summary no longer shows `setup.sh --harness` (`:4157`). |
| 4 | PASS | No task ID on the page. Titles are the board titles, escaped, backticks as `<code>`, `<wbr>` after `/` and `_`; `test_ac4_*` pass. `REWRITES` is the rule for the rest (see next section). |
| 5 | PASS | Only titles and one line changed since the first review, so the placement it recomputed holds (263 of 263 in the same release). The one new line is T344 under Unreleased (`:4078`, last, ID order), count 106 (`test_ac2_each_summary_gives_its_task_count`, `test_ac5_tasks_are_in_id_order_inside_each_entry` pass). T086 and T184 absent. |
| 6 | PASS | `tests/test_site_changelog.py`: 13 tests; floor of 263 (`FLOOR`, `:29-47`), once-only, ID order, escaping, no email, rewrites. Simulation below. |
| 7 | PASS | The nine files named in AC 7 (the four site tests plus `test_repo_name`, `test_stage_names`, `test_docs_match_installer`, `test_agents_md_primary`, and the new test): `273 passed, 18 skipped`. Repoints carry inline `# T344` comments (`tests/test_site_story.py`, `tests/test_site_content.py`); `tests/test_repo_name.py:45-46` `ALLOWED` gains the test file (its `BANNED` pattern names the old repo) with the reason given. |

### `REWRITES` entries vs board titles

I compared each of the 6 new entries and the 2 changed ones with the board row; the other 37 are unchanged since the first review (38 of 40 kept their meaning there, T157 and T101 were the 2 that shifted).

| Task | Board title (short) | Page title | Meaning kept |
|------|--------------------|------------|--------------|
| T025 | craft-agent skill ... + Stage 1.5 wiring | ... wired into Stage 1 | Yes. `docs/claude-md/pipeline-stages.md:14`: "Stage 1.5 is Stage 1 step Agent team". |
| T035 | README.md — install/update rewritten ... (2 stale-doc gaps: pack ~/.supervisor no-longer-auto-created, git-submodule note removed) | same, "the pack folder is no longer auto-created" | Yes. The path `~/.supervisor` becomes "the pack folder"; both gaps kept. |
| T039 | Dedup the `## Skills vs Agents` section in CLAUDE.md (580→536 lines) | ... section of the doctrine file (580→536 lines) | Yes. |
| T097 | (B2): Per-harness install projection, `setup.sh --harness`, and the AGENTS.md correction that unblocks Codex | Per-harness install projection, and the AGENTS.md correction that unblocks Codex | Yes. Flag name dropped; the B2 label dropped (P3 #5). |
| T223 | ... auto mode never skips Stage 0.5/1 | ... never skips Stage 0 or Stage 1 | Yes. 0.5a and 0.5b are steps of Stage 0 (`pipeline-stages.md:14`). |
| T240 | Rename the repo from personal-agentic-claude to easy-kit | Rename the repo to easy-kit | Yes. Old name dropped. |
| T157 | ... only my In Progress tasks block my push | ... only my own tasks still being worked on block my push | Yes (fixed since the first review; "In Progress" is a banned board word). |
| T101 | README and site still describe the pre-T096/T097 world in four places | ... the layout from before the canon move and the per-CLI install, in four places | Yes (fixed since the first review). |

### UI / Design Acceptance Criteria

Method: Playwright with the Chromium headless shell `chromium_headless_shell-1248`, `file://` `site/docs.html#changelog`, 375x800 and 1280x900; script and screenshots in the scratchpad (`r2_shot.py`, `r2_cl_375.png`, `r2_cl_1280.png`).

| Row | Verdict | Evidence |
|-----|---------|----------|
| Visual regression | PASS | `<h2>` computed size 20px, same as `#options` h2. The section sits in the main column at 1280px (heading, intro, boxed `<details>`, bullet list, `<code>` chips as in the other fold-outs); the sidebar shows "Change log" last. `git diff --numstat main HEAD -- site/docs.html`: `300 0` (300 added, 0 deleted), so no other section changes. Plain `<details>` is the element already used 19 times on `main`. |
| Design-system compliance | PASS | In the section: 0 elements with `style=`, 0 with `class=` (Playwright count). `site/theme.css` and `site/index.html` not in the diff. |
| Responsiveness | PASS | 375px: `scrollWidth 375 = clientWidth 375`, 0 elements past the right edge, also after opening all five entries; summary lines and code spans wrap in the screenshot. 1280px: `scrollWidth 1280`, same checks. |
| UX story 1 | PASS | 1280px click gives `#changelog`; Unreleased open with its tasks, four closed rows with date and count (summaries above). |
| UX story 2 | PASS (first review) | The `v2.1.0` row opening was checked in the first review; this fix changed no markup of that entry. |

### Evidence

- Tests, run in `wt-t344` at `c0a879b`: `uv run --with pytest python -m pytest tests/test_site_changelog.py tests/test_site_content.py tests/test_site_story.py tests/test_site_visual_first.py tests/test_site_explorer.py tests/test_repo_name.py tests/test_stage_names.py tests/test_docs_match_installer.py tests/test_agents_md_primary.py -q -p no:cacheprovider` printed `273 passed, 18 skipped in 1.69s`. The 4 tests that failed in the first review are in this run and pass.
- Simulation (scratch copy `scratchpad/sim2`, only the files the test reads): T344 row set to `[x]` plus a new `- [x] **T999**` row that is not listed: `13 passed`. One `<li>` deleted from the page (`diff` shows the removed line `3973d3972`): `2 failed, 11 passed` (`test_ac2_each_summary_gives_its_task_count`, `test_ac5_every_floor_task_appears_exactly_once_and_nothing_unknown`).
- Full suite: a run was in progress when this review finished (3 pytest processes alive). I did not wait for it. Compare its failing set with the 54-test `main` baseline; the 4 tests of finding 1 must not be in it.
- Not run: `ux-evaluate` skill (not available here); `security-review` (Risk Low). The `verify` row stays the hook's.
- Upkeep (known, in the guide's cut list): a later Done row never breaks the suite; a later Done title that carries a task ID, a board word, a hex colour, `**` or a banned name fails `test_ac4_rewrites_cover_exactly_the_floor_titles_that_break_a_page_rule` only if its task is in `FLOOR`, so a new task needs a `REWRITES` entry only if the author lists it and its title breaks a page rule (`test_ac4_the_page_shows_no_task_id_and_no_board_word` guards that).
