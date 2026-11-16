# TASK_GUIDE — T322: `site/docs.html` explains the session tags `[ticket]`, `[admin]` and `[stop]`
**Date**: 2026-11-16
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
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

User, 2026-11-16: "for the tag auto, admin, ticket, did we add it into the index page". The Supervisor found: `site/index.html` names no tag (it is a landing page that links to `site/docs.html`); `site/docs.html` "Auto mode" (lines 406–469) explains `[auto]` and `[admin]`; no site page names `[ticket]` or `[stop]`, the session tags T317 added. User: "should add it, cause it will affect to the workflow".

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> The "Auto mode" `<details class="more">` block of `site/docs.html` gains a short "Session tags" part that says what `[ticket]`, `[admin]` and `[stop]` do, as `docs/claude-md/tracks.md` `### Session tags` defines them today on `main`.

**Out of scope** (what this task explicitly does NOT do):
- `site/index.html` (a landing page; it names no tag and links to the docs page).
- Any change to the flow diagram, the lane chips, CSS or `site/theme.css`.
- Any change to doctrine (`docs/claude-md/tracks.md`, `AGENTS.md`) or to a hook.
- The configurable push remote of T321 (In Progress). The text says `origin`, which is true on `main` today. T321 owns any later wording change.

**Depends on**: None (T317, Done, defines the behaviour)

**Requirement Refs**: None — kit documentation; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor, 2026-11-16: "should add it")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (session tag, ticket, auto verify, Supervisor)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `site/docs.html#tracks`, "Auto mode" → "Details"

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Inside the existing `<details class="more">` of `#tracks` (after the current last `<p>`, before `</details>`), a new `<p>` starting with `<strong>Session tags</strong>` names `[ticket]`, `[admin]` and `[stop]` (each in `<code>`) and says: `[ticket]` and `[admin]` hold for the whole session, `[auto]` holds for one request only; `[stop]` or a request with another tag ends a session tag; a resume, continue or fork ends it, `/compact` does not | the tags are on the site |
| 2 | The same part says what the loop does: the Supervisor works the board one ready ticket at a time (highest Priority first), runs each in auto mode, starts its auto verify and waits; after a pass `[ticket]` pushes only the task branch to `origin`, `[admin]` merges the task branch into `main` and pushes `main`; after `blocked` or `fail` it pushes and merges nothing; it opens no pull request | it will affect the workflow |
| 3 | The same part says: no tag approves a tool call; to run Bash without prompts, apply the `settings-setup` profile `autonomous` (`permissions.defaultMode: "auto"`); the kit never sets `bypassPermissions` | workflow effect |
| 4 | Every sentence matches `docs/claude-md/tracks.md` `### Session tags` (no claim the doctrine does not make). Plain English per AGENTS.md Writing Principles: short sentences, one action each, active voice | correct and readable |
| 5 | Nothing outside that `<details>` block changes; the first-load word count is unchanged (the new text is inside `<details>`); all existing site tests stay green | no regression |
| 6 | A new test `tests/test_t322_session_tags_docs.py` checks AC 1–3 against the page text (the three tags, "whole session", "one request", `[stop]` ends it, `origin`, `main`, `autonomous`, `bypassPermissions`) and that the new `<p>` sits inside the `#tracks` `<details class="more">` | Gate 5 |

### UI / Design Acceptance Criteria

| # | Criterion | How checked |
|---|-----------|-------------|
| U1 | Visual regression: the closed page looks the same; the open "Details" block shows the new paragraph in the same style as its neighbours | `ux-evaluate` screenshots at 375px and 1280px, Details open |
| U2 | Design-system compliance: only existing elements (`<p>`, `<strong>`, `<code>`); no new class, inline style or colour | grep of the diff |
| U3 | Responsiveness: no sideways scroll at 375px with Details open (long `<code>` strings may wrap) | `ux-evaluate` 375px screenshot |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The page after the change | AC 1–3 phrases present inside the `#tracks` details block | `tests/test_t322_session_tags_docs.py` |
| 2 | The full suites | no regression, site tests green (AC 5) | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |
| 3 | The page in a browser | U1–U3 | `ux-evaluate` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_t322_session_tags_docs.py -q -p no:cacheprovider
python3 -m pytest tests/test_site_visual_first.py tests/test_site_story.py tests/test_site_content.py -q
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T322.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T322.md`.

---

## Approach

**Pattern reference**: the `<p><strong>Auto verify</strong> …</p>` and `<p><strong>Close-out:</strong> …</p>` paragraphs at `site/docs.html:454-469`.
**Vital slice**: one paragraph (or a `<p>` plus a short `<ul>`) inside the existing Details block, and its test.
**Cut list**: no new flow diagram or chip lane for session tags, no index-page change, no nav link, no per-gate detail (the merge-gate binding rules stay in `tracks.md`).

Source of truth: `docs/claude-md/tracks.md` lines 877–937 (`### Session tags`). Keep it short: about 80–120 words.

---

## Edge Case Checklist

- [ ] `test_site_story.py` pins sentence hashes of existing `<p>`: add a new `<p>`, never edit an existing one.
- [ ] `test_site_visual_first.py` word cap: the new text must be inside `<details>`.
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: `tests/test_kit_explorer_data.py` / `scripts/gen_kit_explorer.py --check` still pass (the data block is not touched)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/docs.html` | one new paragraph inside the `#tracks` Details block |
| `tests/test_t322_session_tags_docs.py` | new |
| Pre-existing pin tests | List each test that pins text, size, word count, line count or hash of `site/docs.html`, and its handling. Grep `tests/` and `.claude/hooks/tests/` for `docs.html`. **Filled by the implementer:** Grep found 22 files naming `docs.html`. Pinned and run green after the change: `test_site_story.py` (sentence hashes of existing `<p>`: untouched, new `<p>` added), `test_site_visual_first.py` (word cap: text is inside `<details>`), `test_site_content.py`, `test_kit_explorer_data.py`, `test_site_explorer.py`. Full suite 7497 passed. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `site/index.html`, `site/theme.css` | out of scope |
| `docs/claude-md/*.md`, `AGENTS.md`, `.claude/hooks/**` | doctrine and hooks; read only |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

Write the test first (red), add the paragraph (green), run the full suites, run `ux-evaluate`. The Supervisor runs `code-review` (Risk Low: no `security-review`).

---

## Completion Checklist

- [ ] Test written first, red
- [ ] Pin-test row filled
- [ ] Implementation done
- [ ] `ux-evaluate` run, U1–U3 filled
- [ ] `code-review` run
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T322.md` (Hard-Stop Gate 5)
- [ ] UI Evidence rows filled (Hard-Stop Gate 6)
- [ ] Supervisor notified: ready for Stage 4
