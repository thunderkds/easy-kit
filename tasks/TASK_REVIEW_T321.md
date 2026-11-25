# TASK_REVIEW — T321: the `[admin]`/`[ticket]` push remote is a setting (`EASY_KIT_ADMIN_REMOTE`), not the hard-coded `origin`

> Sibling of `tasks/TASK_GUIDE_T321.md`. Evidence is filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Ran T321 after T354 under the session `[admin]` — RULE: the user's request "merge T347 [admin], T321 [admin]" and, after the compaction, "T321 [admin]" (`tasks/TASK_GUIDE_T321.md § Requirement`).
2. Track extended — RULE: docs/claude-md/tracks.md § Track rule (Risk High: the merge gate; C2: gate, new test, guard, tracks.md).
3. The Supervisor writes the oracle test and the code itself, test first, in `../wt-t321`; no qa-expert or implementer spawn (the guide's "written first by `qa-expert`" predates DDR-0011) — RULE: `AGENTS.md § Hard-Stop Gates` (Gate 1: "the Supervisor writes the code itself, in the task's worktree, test first").
4. Reader shape and bad-value rule — DEBATED: PENDING
5. `merge_gate_guard.py` `AUTHORISED_TASKS` gains T321 with the Supervisor's sign-off — RULE: .claude/hooks/tests/merge_gate_guard.py:22 ("A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off").
Checks: PENDING
Memory: PENDING
Not done: merge (admin: after the auto verify pass); push (the user sets `EASY_KIT_ADMIN_REMOTE=github` in `.claude/settings.json` `"env"`: a settings change stays the user's); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | |
| Verification command run | ☐ pass / ☐ fail | |
| Negative cases hold | ☐ pass / ☐ fail | |
| verify | ☐ pass / ☐ fail / ☐ N/A | |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: neither companion tool is installed for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | No UI: hook-only change. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | No UI: hook-only change. |
| **UI: Responsiveness at target viewports** | ☐ N/A | No UI: hook-only change. |

---

## Demonstration

**BEFORE**: captured 2026-11-25T05:12:59Z on `5054139f` (before any implementation commit), `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t321_admin_remote.py`:

```
39 failed, 12 passed in 7.37s
```

Failing: every AC 2–6 case (the `github` push allowed and `origin` refused naming `github`; each `github`-side check; `[ticket]` to `github`; every bad value refused naming it, helpers failing closed; the docs and refusal text). Passing: AC 1 (unset/empty/blank keep `origin`), the AC 3 refusals that hold by accident today (the gate refuses any non-`origin` remote), and AC 5's merge-unaffected cases.

**AFTER**: PENDING

**DELTA**: PENDING

**WITNESS**: PENDING
