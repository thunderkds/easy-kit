# TASK_GUIDE — T280: The home page journey flow gets a sixth step, "Improve it" (self-review)
**Date**: 2026-11-07
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: frontend-developer
**Agent guide**: `agents/frontend.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md` and `PROJECT_SPEC_SITE.md`
2. Read the memory slice in your spawn prompt
3. Read this file completely
4. Read `agents/frontend.md`
5. Read `site/index.html` (the `#journey` section, lines 78–110) and `tests/test_site_story.py` lines 211–262 (the journey pins and the 300-word cap)
6. Read `skills/self-review/SKILL.md` Rules (the facts the step may claim) and the new flow at `site/docs.html` `#skills`
7. Read `memory/learning-records/LR-0004-pin-tests-hit-later-tasks.md` and the T278 entry in `memory/learnings.md` (word budgets)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-07: *"I checked from the easy kits page but got no item"* (the self-review diagram is on `docs.html`, the home shows only a chip), then *"should show the overview flow in the home, maybe adding or just update the current flow, it's up to you"*.

**Restated intent** (the Supervisor decided "update the current flow", because `index.html` is at its 300-word cap and its six sections are pinned):
> The home page's "The full journey" flow gets one more step after "You merge": **Your step · Improve it · Optional: `/self-review`**, linked to the docs diagram. A visitor sees on the home page that the kit can propose improvements to itself and that the user starts it.

**Out of scope**:
- `site/docs.html` (its diagram stays as T278 built it), the chip rows, `skills/self-review/**`
- A new section, a new CSS class, or a new image on the home page
- The family-nav links to the dead `personal-agentic-claude.vercel.app` (separate, not decided)

**Requirement Refs**: None — follow-up to T278.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor; the user left the choice to the Supervisor)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none claimed)

---

## Dependencies & Reachability

**Depends on**: T278 — merged; the docs diagram this step links to

**Entry point**: `<section id="journey">` in `site/index.html`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The `#journey` ordered list has 6 steps. Steps 1–5 are unchanged in order, key, title and link. The sixth step is `flow-key` "Your step", `flow-title` a link "You improve it" to `docs.html#skills`, `flow-desc` "Optional: " plus `<code>/self-review</code>` | "update the current flow" |
| 2 | The sixth step has classes `flow-node is-yours is-link` and no `is-outcome`; `is-outcome` stays on "You merge" | Design |
| 3 | `index.html` `<main>` shows at most 300 visible words (`WORD_CAP`), and none of the banned terms. Make room by shortening the four "Go deeper" card descriptions (`#deeper`), not by raising the cap | Word cap |
| 4 | The journey heading stays "The full journey"; the "You merge" description stays "You review. Easy Kit merges only when you ask." | Existing pins |
| 5 | The step says only what is true: it does not claim the kit changes itself without the user (`skills/self-review/SKILL.md` Rules). No `autonomous`, `self-improving`, `automatic`, `automatically` | LR-0005 |
| 6 | At 375px the six steps stack with no sideways scroll; at 1280px the row shows six nodes, the last is not highlighted green | B-h |
| 7 | The existing site tests pass, with exactly these pin edits and no other: `test_journey_is_an_ordered_list_of_five_steps...` (5 → 6, rename the test), `test_journey_marks_the_users_two_steps...` (list becomes `[True, False, False, False, True, True]`, rename), `test_the_journey_heading_and_the_merge_step_say_what_is_true` (find the merge step by its title, not `[-1]`). Any other failing pin: stop and report | LR-0004 |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `site/index.html` after the change | `#journey` holds 6 `li`; the sixth links to `docs.html#skills` and holds `/self-review` | automated (the edited pin tests) |
| 2 | `<main>` word count | at most 300 | `test_main_holds_at_most_300_words` |
| 3 | Mutation: remove the sixth step | the edited step-count test fails | mutation control, run by the reviewer |
| 4 | The sixth step's text | none of the banned words (AC 5) | automated (new `tests/test_t280_home_improve_step.py`) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_t280_home_improve_step.py tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_t151.py -q
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer in `tasks/TASK_REVIEW_T280.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T280.md`.

---

## UI / Design Acceptance Criteria

### 1. Visual Regression

| Screen / Component | Verification method | Expected result |
|-------------------|---------------------|-----------------|
| Home `#journey` at 375px and 1280px | LLM-vision screenshot (`ux-evaluate`) | Six nodes in order; steps 1, 5 and 6 carry "Your step"; the green outcome stays on "You merge"; no other section moves |

### 2. Design-System Compliance

| Criterion | Verification method | Expected result |
|-----------|---------------------|-----------------|
| Colors match design tokens | CSS audit | No new color; `site/theme.css` untouched |
| Typography matches spec | computed style | Same as the other five nodes |
| Spacing / layout matches spec | computed style | Same gaps as the other five nodes |

### 3. Layout / Responsiveness

| Viewport | Verification method | Expected result |
|----------|---------------------|-----------------|
| Mobile (375px) | screenshot, `scrollWidth` | Steps stack; no sideways scroll |
| Tablet (768px) | screenshot | Same stacking rule as the docs six-node rows |
| Desktop (1280px) | screenshot | One row of six nodes, readable, no clipped text |

### 4. UX Acceptance Criteria

| User story | User goal | Flow / state | Pass condition (observable) |
|------------|-----------|--------------|-----------------------------|
| Request: "should show the overview flow in the home" | A visitor sees the kit can improve itself, and that they start it | Open the home page, look at "The full journey" | The sixth node "You improve it / Optional: /self-review" shows at 375px and 1280px without a click, and links to the docs diagram |

---

## Approach

**Pattern reference**: `site/index.html` lines 102–106 — the last journey node (`is-yours is-link is-outcome`); copy its markup for the new node minus `is-outcome`.

**Vital slice**: one `li` in `#journey`, shorter card text in `#deeper`, the three pin edits, one new test file.
**Cut list**: a second flow or section; a diagram of the loop on the home page (the docs diagram is one click away); mention of "up to 3 proposals" or citations (docs holds them).

Word budget: the page is at exactly 300 of 300. The new step adds about 6 visible words (`Your step` 2, `You improve it` 3, `Optional:` 1; the `<code>` is not counted). Remove at least that many from the card descriptions in `#deeper` (for example "Backend, frontend, infrastructure and QA roles." → "Backend, frontend, infrastructure, QA."). Keep each card's heading and link.

---

## Edge Case Checklist

- [ ] The fixture `tests/fixtures/site_story_baseline.json` pins old docs sentences; check that the card edits touch nothing it lists
- [ ] The new step's `href` id exists in `docs.html` (`skills`)
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep `README.md`, `RUNBOOK.md`, `docs/claude-md/`, `agents/` for "five steps" or "5 steps" of the journey and report any hit
- [ ] The step does not say "approve or reject" or "up to 3 proposals" (those are the docs diagram's wording and carry word cost)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/index.html` | One `li` in `#journey`; shorter card text in `#deeper` |
| `tests/test_site_story.py` | The three pin edits named in AC 7, and only those |
| `tests/test_t280_home_improve_step.py` | New: AC 1, 2, 4, 5 as tests, plus the mutation control |
| Pre-existing pin tests | `test_site_story.py` (journey count, labels, merge step, 300-word cap, banned terms, `deeper` four cards), `test_site_content.py`, `test_site_visual_first.py` (docs-only hashes), `tests/fixtures/site_story_baseline.json`. Handling: edit only the three journey pins; escalate anything else |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `site/docs.html`, `site/theme.css` | Out of scope |
| `skills/**`, `memory/**` | Out of scope |
| `tests/test_site_story.py` `WORD_CAP` and `BANNED_TERMS` | The cap is a design limit |

---

## Test Plan

1. Edit the three pin tests and write `tests/test_t280_home_improve_step.py` first (red: the page has 5 steps).
2. Add the step and trim the card text (green).
3. Run the Verification Command.
4. Screenshot the home `#journey` at 375px and 1280px; run `ux-evaluate`.
5. Mutation: remove the sixth step; the step-count test must fail. Restore it.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T280.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] UI Evidence rows (visual, design-system, responsiveness) filled (Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run
- [ ] Supervisor notified: task ready for Stage 4 review
