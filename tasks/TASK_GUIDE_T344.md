# TASK_GUIDE — T344: `site/docs.html` gets a Change log section listing every release
**Date**: 2026-11-20
**Complexity Level**: C2
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: frontend-developer
**Agent guide**: `agents/frontend.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/frontend.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-20: "create a section that about the change logs in the index docs, and add all of them to this". Forced choice the same day: page = "docs.html (Recommended)"; scope = "Every release (Recommended)" — one entry per release tag plus an "Unreleased" entry for work merged since v2.2.0, T341 included.

**Restated intent**:
> The reference page `site/docs.html` gains a "Change log" section, linked from its sidebar, that lists every release of the kit (tags `v1`, `v2.0.0`, `v2.1.0`, `v2.2.0`) and an "Unreleased" entry, newest first. Each entry names the tasks it shipped, every Done task exactly once, with its board title.

**Out of scope**:
- `site/index.html` (the story page) — the user chose docs.html only.
- A Features / Fixes / Internal split: about 60% of merge commits carry no type prefix (`Merge T164: …`), so the split would be a guess for most tasks.
- A generator kept in the repo or a test that regenerates the list: the section is written once; a later release adds its entry by hand (see cut list).
- A new release tag, a version bump, or the footer's "v2.2.0 release" text.

**Requirement Refs**: none in `PRD.md` (kit site content).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed — the user's two forced-choice answers, 2026-11-20
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (task, release, board, Done)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] No `PRD.md` refs; the AC cover the restated intent in full

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `id="changelog"`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `site/docs.html` has `<section id="changelog">` with `<h2>Change log</h2>`, placed after `<section id="options">` and before `<footer>`; the sidebar's `// reference` group ends with `<li><a href="#changelog">Change log</a></li>`. | a section, linked |
| 2 | Inside it, one `<details>` per release, newest first: `Unreleased`, `v2.2.0`, `v2.1.0`, `v2.0.0`, `v1`. Each `<summary>` names the release, its date (the tag's commit date; none for Unreleased) and its task count. Only `Unreleased` is `open`. | every release, newest first |
| 3 | Each released entry starts with one sentence summarising it, written from `RUNBOOK.md` `## Release Log` (`v1` covers that log's `v1.0.0` and `v1.1.0` rows). The Deployer and Approved columns are not copied (the Deployer cell is an email address). | release summaries |
| 4 | Each entry lists its tasks in ID order as `<li><code>Txxx</code> — <title></li>`, the title being the task's current `PROJECT_KANBAN.md` title, HTML-escaped, with Markdown backtick spans turned into `<code>`. | tasks named with titles |
| 5 | Placement rule: every `- [x]` task on `PROJECT_KANBAN.md` appears exactly once across the section. A task named in a `RUNBOOK.md` Release Log scope goes to that release; any other task goes to the earliest release tag whose history contains the commit where its board row first became `- [x]` (merge diffs included); a task no tag contains is `Unreleased`. | every task, once |
| 6 | `tests/test_site_changelog.py` (new) pins AC 1, 2, 5 (count and once-only against the live board's Done rows at test time, with the T344 Done set as the floor), the escaping of AC 4, and that the section holds no `@` character. | testable |
| 7 | The existing site tests pass: `tests/test_site_content.py`, `tests/test_site_story.py`, `tests/test_site_visual_first.py`, `tests/test_site_explorer.py`; any baseline they pin is repointed with a `CHANGED_BY_T344` record, not deleted. | no regression |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `site/docs.html` opened at 1280px | sidebar shows "Change log" last; clicking it jumps to the section; Unreleased is open, the four releases closed | screenshot read (ux-evaluate) |
| 2 | Same at 375px | the section is readable with no sideways scroll; task lines wrap | screenshot read (ux-evaluate) |
| 3 | The live board | every `- [x]` task appears exactly once in the section | automated test |
| 4 | A title with `<`, `&` or backticks | rendered escaped, backticks as `<code>` | automated test |

### Verification Command (exact, runnable)

```bash
uv run --with pytest python -m pytest tests/test_site_changelog.py tests/test_site_content.py tests/test_site_story.py tests/test_site_visual_first.py tests/test_site_explorer.py -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T344.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T344.md`.

---

## UI / Design Acceptance Criteria

### 1. Visual Regression

| Screen / Component | Verification method | Expected result |
|-------------------|---------------------|-----------------|
| `site/docs.html` `#changelog` and the sidebar | headless Chrome screenshot, read (ux-evaluate) | the section matches the page's other sections (heading, `<details>` style); no other section changes |

### 2. Design-System Compliance

| Criterion | Verification method | Expected result |
|-----------|---------------------|-----------------|
| Colors match design tokens | CSS audit of the diff | no new CSS rule and no inline `style=`; only existing `site/theme.css` classes |
| Typography matches spec | visual | `<h2>`, `<summary>`, `<code>` as elsewhere on the page |
| Spacing / layout matches spec | visual | `<details>` spacing as the existing `<details>` blocks |

### 3. Layout / Responsiveness

| Viewport | Verification method | Expected result |
|----------|---------------------|-----------------|
| Mobile (375px) | headless Chrome screenshot | no sideways scroll; long titles wrap |
| Desktop (1280px) | headless Chrome screenshot | section in the main column; sidebar link visible |

### 4. UX Acceptance Criteria

| User story | User goal | Flow / state | Pass condition (observable) |
|------------|-----------|--------------|-----------------------------|
| "create a section that about the change logs … add all of them" | see what changed in each release | open docs.html, click "Change log" in the sidebar | the section shows, Unreleased open with its tasks, four closed release rows each with date and task count, at 375px and 1280px |
| same | read one past release | click the `v2.1.0` summary | it opens and shows its RUNBOOK sentence and task list |

---

## Approach

**Pattern reference**: the `<section id="options">` block and the existing `<details>`/`<summary>` blocks in `site/docs.html`; `CHANGED_BY_T341` in `tests/test_site_story.py` for baseline repoints.

**Data**: the placement rule of AC 5 is computed once by a script outside the repo (the Supervisor's draft: scratchpad `cl/extract.py`, result `cl/data.json`: v1 77, v2.0.0 15, v2.1.0 45, v2.2.0 16, Unreleased 102 = 255 Done tasks). Recompute it at implementation time on the then-current board.

**Vital slice**: the section with all five entries and every task (AC 1-5) and its test (AC 6).

**Cut list**:
- No Features / Fixes / Internal split (type unknown for most merges).
- No generator script in the repo and no test that recomputes placement from git history; the test checks once-only and completeness against the board, not the release each task sits in.
- No change to `site/index.html` or the footer.

---

## Edge Case Checklist

- [ ] Titles hold Markdown backticks, `<`, `>`, `&` and `"` — escape, then turn backtick spans into `<code>`.
- [ ] A task done, reopened and done again (T094): the RUNBOOK scope wins.
- [ ] A row that became `- [x]` only inside a merge commit (T216): use `git log --diff-merges=first-parent`.
- [ ] The section must not copy the RUNBOOK Deployer email.
- [ ] Tasks Done after implementation starts (other sessions, T342/T343): the test reads the live board, so a later Done row fails the test until it is added — say so in the review; the floor is the T344 Done set.
- [ ] Pin-test pre-flight: `tests/test_site_story.py` sentence baseline, `tests/test_site_visual_first.py`, `tests/test_site_content.py` section/nav checks.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/docs.html` | the `#changelog` section and its sidebar link |
| `tests/test_site_changelog.py` | new (AC 6) |
| `tests/test_site_story.py`, `tests/fixtures/site_story_baseline.json`, `tests/test_site_visual_first.py`, `tests/test_site_content.py` | only if a pin needs a `CHANGED_BY_T344` repoint |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `site/index.html` | out of scope (user chose docs.html) |
| `site/theme.css` | no new styles |
| `RUNBOOK.md`, `PROJECT_KANBAN.md` | read only, as sources |
| `.claude/` | not a hook or config task |

---

## Test Plan

Write `tests/test_site_changelog.py` first and see it fail (no `#changelog` section), then add the section. Run the Verification Command, then the full suite (`uv run --with pytest python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider`) and compare its failing set with the 54-test `main` baseline (missing shells on this machine).

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: N/A (Risk Low)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T344.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run — feature confirmed working in running app
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review

---

## Questions Log

- 2026-11-20 USER Which page, and which scope? → page "docs.html (Recommended)", scope "Every release (Recommended)".
