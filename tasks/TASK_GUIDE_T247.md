# TASK_GUIDE — T247: the Stop check's `[auto]` span is not closed by an interrupt or a slash-command entry
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Low
**Priority**: P2
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

User, 2026-11-25: "continue the tasks as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: `stop_auto_mode_check.py` `request_text()`: an interrupt entry (`[Request interrupted by user`) and a slash-command entry (`<command-name>`, e.g. `/compact`) close an `[auto]` span (T229 verify step 6); treat both as not a request.

**Restated intent**:
> In the Stop check (`.claude/hooks/stop_auto_mode_check.py` `auto_windows`), a user entry whose text starts with `[Request interrupted by user` (both the plain form and `… for tool use]`), or whose text starts with a slash-command block (`<command-name>` or `<command-message>`), is not a request: it neither opens nor closes an `[auto]` span. Every other entry is read as today.

**Scope limit (important)**: change only the Stop check's reading. `request_text` in `.claude/hooks/lib/auto_mode.py` is also read by the merge gate (`pre_bash_block_unsafe_merge.py`, `latest_request`, `admin_request`), and the gate's `/verify` binding (`lib/session_work.py`) reads `<command-name>/verify</command-name>` entries on purpose. Do **not** change `auto_mode.request_text` or `NOT_A_REQUEST`. `stop_auto_mode_check.py:162` aliases `request_text = am.request_text`; replace that alias with a local function that calls `am.request_text` and returns None for the two entry kinds above.

**Out of scope**: the merge gate; session tags (`[admin]`/`[ticket]` already hold across untagged entries, T317).

**Depends on**: T229 (Done)

**Requirement Refs**: None — kit maintenance; source is the board row above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: T229

**Entry point**: `.claude/hooks/stop_auto_mode_check.py` `auto_windows`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Transcript: `[auto]` request, then `[Request interrupted by user]`, then a task's work: the work is inside the `[auto]` span (one open span) | interrupt |
| 2 | Same with `[Request interrupted by user for tool use]` (as a text block in a list content) | interrupt, list form |
| 3 | Same with a `/compact` entry (`<command-name>/compact</command-name>` …, string content, and the `<command-message>` first form) | slash command |
| 4 | An ordinary untagged request after `[auto]` still closes the span (T229 unchanged) | no over-reach |
| 5 | `auto_mode.request_text` returns the same as before for both entry kinds (the gate's reading is unchanged) | scope limit |

## UI / Design Acceptance Criteria

Not applicable — no UI.

---

## Evaluation & Acceptance

**Locked oracle**: a new test file `.claude/hooks/tests/test_t247_auto_span_entries.py`, written first (red for AC 1–3), then the fix.

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t247_auto_span_entries.py .claude/hooks/tests/test_stop_auto_mode_check.py
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/MINIMAL_LOG.md` (minimal).

## Demonstration

> **Moved.** See the `tasks/MINIMAL_LOG.md` record (minimal).

---

## Approach

Read `auto_windows` (`stop_auto_mode_check.py` ~line 165) and `auto_mode.request_text` (`lib/auto_mode.py:99`). Call `auto_windows(path)` directly in the test on a transcript written to `tmp_path` (entries: `{"type":"user","timestamp":…,"message":{"content":…}}`). Match the start of the stripped text only, so a request that merely quotes `[Request interrupted by user` later in its text is still a request.

## Files to Change (Predicted)

- `.claude/hooks/stop_auto_mode_check.py`
- `.claude/hooks/tests/test_t247_auto_span_entries.py` (new)
- `tasks/MINIMAL_LOG.md`

## Files must NOT touch

- `.claude/hooks/lib/auto_mode.py`, `.claude/hooks/pre_bash_block_unsafe_merge.py`, `.claude/hooks/lib/session_work.py`, `PROJECT_KANBAN.md` (the Supervisor moves rows), `.claude/settings.json`
