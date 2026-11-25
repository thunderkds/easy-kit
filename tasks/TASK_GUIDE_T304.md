# TASK_GUIDE — T304: the docs layout table puts `general-agent-template.md` in `templates/`, not `agents/`
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Low
**Priority**: P3
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`
**Track**: minimal

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

> Read relevant files from `docs/legacy/` before making any code changes (this repo has none: skip when absent).

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-25: "continue the tasks as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: the docs layout puts `general-agent-template.md` in `templates/`, not `agents/` (follow-up named in the T303 record, `tasks/MINIMAL_LOG.md`: "the repository layout row for `agents/` still says it holds `general-agent-template.md`, which lives in `templates/` (pre-existing)").

**Restated intent**:
> In `site/docs.html`'s repository layout table, the `agents/` row no longer says it holds `general-agent-template.md`; the `templates/` row says it holds it (the shared base rules every role guide inherits). `docs/claude-md/folder-structure.md:33` already says this — match its wording. No other page text changes.

**Out of scope**: `CLAUDE.md` (the legacy protocol text, user-owned and modified in the working tree — do not touch); any other docs page.

**Depends on**: None (T183, T303 Done)

**Requirement Refs**: None — kit maintenance; source is the board row above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: Standalone — N/A (static docs page)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The `agents/` row of the layout table in `site/docs.html` does not name `general-agent-template.md` | the wrong row |
| 2 | The `templates/` row of that table names `general-agent-template.md` | where it lives |
| 3 | A test in `tests/test_site_content.py` checks 1 and 2 (red before, green after) | locked oracle |

## UI / Design Acceptance Criteria

Not applicable — a text change in one table cell pair; the page's markup and styles do not change.

---

## Evaluation & Acceptance

**Locked oracle**: the new test in `tests/test_site_content.py`, written first (red), then the fix.

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider tests/test_site_content.py
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/MINIMAL_LOG.md` (minimal).

## Demonstration

> **Moved.** See the `tasks/MINIMAL_LOG.md` record (minimal).

---

## Approach

The table is at `site/docs.html` ~line 3847 (`<code>agents/</code>` row) and ~line 3856 (`<code>templates/</code>` row). Keep the `<wbr>` style the page uses for long names (`general-<wbr>agent-<wbr>template.md`). The existing test at `tests/test_site_content.py:116` finds the first mention of `general-agent-template` on the page — read it so the new test does not break it.

## Files to Change (Predicted)

- `site/docs.html`
- `tests/test_site_content.py`
- `tasks/MINIMAL_LOG.md`

## Files must NOT touch

- `CLAUDE.md`, `PROJECT_KANBAN.md` (the Supervisor moves rows), `.claude/settings.json`, `.claude/hooks/pre_bash_block_unsafe_merge.py`
