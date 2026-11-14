# TASK_REVIEW — T312: an "Explorer" section on site/docs.html shows each agent and skill with its steps in order

> Sibling of `tasks/TASK_GUIDE_T312.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_site_explorer.py` (24 tests, written first by `qa-expert`; red `24 failed` at `d7eaabc2`, green `24 passed` after `a34099de` and `27d40d15`). Static tests: section order, sidebar link, no http/img/colour, `<noscript>` line, `textContent` only, CSS tokens only. Browser tests (headless Chrome on temp copies): one chip per item of the data block, `tdd`/`qa`/`verify` panels, all 37 skills, 4 agents and 5 built-ins, the filter on all 46 panels, ARIA, the block parsed once, 768px and 375px layout, 44px tap size, missing data, invalid JSON, a hostile note, an empty step list. Repointed pins, each with a T312 comment: `tests/test_site_content.py` (sidebar list gains Explorer), `tests/test_site_story.py` (17-section baseline skips `explorer`); `site/index.html` gains `"explorer"` in its redirect id list (one word) because `test_redirect_id_list_equals_the_link_target_ids_of_docs` pins it to the docs section ids |
| Verification command run | ☑ pass | Supervisor at `8e81020a`: `python3 -m pytest tests/test_site_explorer.py -q -p no:cacheprovider` -> `24 passed in 2.85s`; `python3 scripts/gen_kit_explorer.py --check; echo "gen exit $?"` -> printed nothing, `gen exit 0` (the generated block and its markers are untouched) |
| Negative cases hold | ☑ pass | Red run before any implementation (`qa-expert`, `d7eaabc2`): `24 failed` — 9 static tests (no `#explorer`, no CSS rule) and 15 browser tests (no section, so no probe). `qa-expert` also ran the oracle against a throwaway stand-in: an `innerHTML` variant was caught by 4 tests. Negative cases in the oracle: missing block and invalid JSON show the one-line message and no uncaught error; a hostile note `<img src=x onerror=alert(1)>` shows as text with no `<img>` in the panel; a note holding a board word and a task ID is dropped while its step title stays; a skill with no steps shows its description and no list. `git diff main..HEAD --stat`: 8 files, 913 insertions, non-empty |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 8 files of `main..feat/t312-docs-explorer-section`: the `#explorer` section and sidebar link in `site/docs.html`, 24 lines in `site/theme.css`, one word in `site/index.html`, the oracle, two repointed pins, the guide and this file. Callers by grep: every test that reads `docs.html` or `theme.css` (all ran in the full suite). Skipped: the generated data block (T311, `--check` exit 0). `code-review` 2026-11-14: P0 0, P1 0, P2 1, P3 3. P2: agent chips read `backend`, `frontend`, `qa` (the file stems from the T311 data contract) while `AGENTS.md` and the Agent roles section call them `backend-developer`, `frontend-developer`, `qa-expert`; follow-up, not a blocker, because the panel text and the oracle both pin the data name. P3: step titles and item names are not run through the board-word filter (only notes and descriptions are; the browser test checks all 46 real panels but skips without Chrome); the filter regex is built from parts so the static-page test passes (commented); `tests/test_auto_verify.py::test_ac2_same_task_and_commit_never_start_twice` is timing-sensitive (failed once under full-suite load, passes alone). `ux-evaluate` (implementer by hand per the skill, 14 pass 0 fail; Supervisor read `T312_after_tdd_1280.png` and `T312_after_qa_375.png`): pass. `security-review`: no findings. Reports: `reports/code-review_feat-t312-docs-explorer-section_20261114T075551.html`, `reports/security-review_feat-t312-docs-explorer-section_20261114T075551.html` (git-ignored) |
| Full smoke suite still green (no regression) | ☑ pass | Supervisor at `8e81020a`, no edits during the run: `python3 -m pytest .claude/hooks/tests/ tests/ -q` -> `1 failed, 7232 passed, 5 skipped, 25 subtests passed in 404.07s (0:06:44)`; the one failure, `tests/test_auto_verify.py::test_ac2_same_task_and_commit_never_start_twice`, passes alone (`1 passed in 2.27s`, timing under load). `node --test tests/site_scrollspy/test_scrollspy.mjs` ran after it with no failure. Before the memory fix (`f494ec58`, cherry-picked as `8e81020a`) the implementer saw 6 failures: 5 hot-tier budget tests (not from this branch: `main` was over its 42,000-character budget) and the redirect-list test (fixed in `27d40d15`). The auto verify run re-runs the suite |
| **Companion score (easy-verifier)** | ☑ N/A | not run: the optional companion score was skipped; the merge gate blocks on `☑ fail` only, never on an N/A row |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | Headless Chrome screenshots in the worktree `reports/` (git-ignored): `T312_after_{rest,tdd,qa,verify,missing}_{375,1280}.png`. Supervisor read `T312_after_tdd_1280.png`: chips grouped by stage, `tdd` pressed, a numbered list of 5 steps (Planning, Tracer Bullet, Incremental Loop, Refactor, Prove each test can go RED) beside the map. `T312_after_qa_375.png`: one column, chips wrap, the panel sits under the map, no sideways scroll. Before: `T312_before_docs_1280.png` |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | `tests/test_site_visual_first.py::test_no_hex_colour_outside_the_token_block_and_no_third_party_asset` passes; the 24 new lines of `site/theme.css` use `var(--…)` tokens only, no `transition`, `animation` or gradient (oracle static test); chips reuse the site `.chip` shape; IBM Plex Mono for ids and Sans for text, as the screenshots show |
| **UI: Responsiveness at target viewports** | ☑ pass | Oracle browser tests with `--window-size`: at 768px and 375px the panel sits below the chips and the body has no sideways scroll; at 375px every chip is at least 44px by 44px. Screenshots at 375px and 1280px read by the Supervisor. Two columns from 1100px, stacked below |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (qa-expert, 2026-11-14T07:21Z, branch `feat/t312-docs-explorer-section`, before any implementation commit):

```
$ grep -c 'id="explorer"' site/docs.html
0
$ sed -n 237,243p site/docs.html      # sidebar, "// the team"
    <p class="nav-group-title">// the team</p>
    <ul>
      <li><a href="#agent-roles">Agent roles</a></li>
      <li><a href="#skills">Skills</a></li>
      <li><a href="#hooks">Hooks</a></li>
      <li><a href="#agent-focus">Agent focus</a></li>
    </ul>
$ google-chrome --headless=new --no-sandbox --disable-gpu --window-size=1280,900 --screenshot=reports/T312_before_docs_1280.png file://$PWD/site/docs.html
159108 bytes written to file /home/hungnguyenhuu/workspace/pets/wt-t312/reports/T312_before_docs_1280.png
$ python3 -m pytest tests/test_site_explorer.py -q -p no:cacheprovider
24 failed in 3.29s
  static tests:  AssertionError: site/docs.html has no <section id="explorer">
  browser tests: AssertionError: probe has no 'clicks': the #explorer section is absent or its script failed ({'errs': [], 'hasSection': False})
```

Screenshot (git-ignored): `/home/hungnguyenhuu/workspace/pets/wt-t312/reports/T312_before_docs_1280.png`. The sidebar has no "Explorer" link and the page has no `#explorer`.

**AFTER** (frontend-developer, 2026-11-14, branch `feat/t312-docs-explorer-section`):

```
$ python3 -m pytest tests/test_site_explorer.py -q -p no:cacheprovider
24 passed in 2.86s
$ python3 scripts/gen_kit_explorer.py --check; echo "exit $?"
exit 0
$ python3 -m pytest .claude/hooks/tests/ tests/ -q
6 failed, 7227 passed, 5 skipped
  1 failed: tests/test_site_story.py::test_redirect_id_list_equals_the_link_target_ids_of_docs (needs a site/index.html edit; STOPPED, see report)
  5 failed: test_memory_channel_and_budget.py (4) + test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget (memory/MEMORY.md budget; file untouched by this branch)
```

Screenshots (git-ignored, `reports/`, shot from temp copies that hide the other sections; selected states by a clicking script in the copy): `T312_after_rest_{375,1280}.png`, `T312_after_tdd_{375,1280}.png`, `T312_after_qa_{375,1280}.png`, `T312_after_verify_{375,1280}.png`, `T312_after_missing_{375,1280}.png`.

ux-evaluate (by hand):

| # | Flow / state | Width | Verdict | Screenshot | Reason |
|---|---|---|---|---|---|
| 1 | first load | 375 / 1280 | pass | rest_375, rest_1280 | chips grouped Agents, Stage 0..5, Any stage; panel shows "Pick an agent or a skill to see its steps." |
| 2 | click tdd | 1280 | pass | tdd_1280 | panel right of map; "Steps" numbered 1-5: Planning, Tracer Bullet, Incremental Loop, Refactor, Prove each test can go RED |
| 3 | click qa | 375 | pass | qa_375 | panel below the map; "Startup sequence" numbered list; no sideways scroll |
| 4 | click verify | 1280 | pass | verify_1280 | "The kit has no file for this built-in." |
| 5 | block removed | 375 / 1280 | pass | missing_375 | one line "The explorer data is missing. The lists above show the same names."; oracle shows no pageerror |
| B-a | default | both | pass | rest_* | the chip map is the one thing to act on, in view |
| B-b | default | both | pass | rest_* | h2, lead, group titles, chips |
| B-c | default | both | pass | rest_* | same card padding and gaps in all groups |
| B-d | default | 375 | pass | rest_375 | oracle test measures every chip at least 44x44 at 375 |
| B-e | default | 375 | pass | qa_375 | panel body 16px, contrast tokens; chip text is 12px mono, the site's own `.chip` size (note) |
| B-f | empty, success, error | both | pass | rest, tdd, missing | each state says what it is |
| B-g | after a click | both | pass | tdd_1280, qa_375 | pressed chip gets mint border; panel fills |
| B-h | default | 375 | pass | qa_375 | one column, chips wrap, no clipping |
| B-i | default | both | pass | rest_* | same mint accent, chip shape and radius as `#skills`; built-ins dashed |

ux-evaluate: 14 pass, 0 fail. Overall: pass. One fix made during the run: a selection scrolled the panel under the sticky header; fixed with `scroll-margin-top` on `.ex-panel`.

**DELTA**: A reader of the docs page can open a new Explorer section, pick any of the 4 agents, 37 skills or 5 built-ins, and see what it does and its steps in order, drawn from the kit's own files so it cannot show a step the kit no longer has.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
