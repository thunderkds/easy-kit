# TASK_REVIEW — T355: Split the 4 skills over Codex's 8 KB cap so a Codex install skips none

> Sibling of `tasks/TASK_GUIDE_T355.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Sign the Requirement Fidelity Gate myself — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13: the Gate is signed `auto (Supervisor)`)
2. Do T355 in this session and register T356–T362 for the rest, since T356, T359 and T360 wait on the user's choices — FACT: PROJECT_KANBAN.md:11 "Before start: brainstorming + the user's choice of what it drops (guide? reviewer spawn? auto verify?)"
3. Security review done inline, no findings: the built-in `security-review` cannot start here (`git diff origin/HEAD...`: unknown revision; this repo has no `origin` remote) — FACT: the Skill call's error output, 2026-11-25 "fatal: ambiguous argument 'origin/HEAD...': unknown revision"
4. Stage 4 code-review: 0 P0/P1, 1 P2 and 1 P3 fixed in `f5ca17a2` (headers of 3 reference files say which moved *above*/*below* name `SKILL.md` sections; guide Files table), 1 P3 left (redundant grep in `tests/test_readme_current.sh`) — RULE: .claude/skills/code-review/SKILL.md § Phase 4 "Present P2/P3 fixes as suggestions only."
Checks: _pending_
Memory: _pending_
Not done: _pending_

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ | |
| Verification command run | ☐ | |
| Negative cases hold | ☐ | |
| verify | ☐ | |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ | |
| Full smoke suite still green (no regression) | ☐ | |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | text only: one existing docs list item reworded |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no new class, style or token |
| **UI: Responsiveness at target viewports** | ☑ N/A | no layout change |

---

## Demonstration

**BEFORE** (2026-11-25, branch `feat/t355-skill-split` at its base, before any implementation commit): `wc -c` — `bugfix` 10261, `craft-spawn-prompt` 14946, `diagnose` 13548, `write-better-skill` 15777 bytes, each over the 8192-byte Codex cap, so a Codex install skips all four (README: "Skills currently affected: `bugfix`, `craft-spawn-prompt`, `diagnose`, `write-better-skill`").

**AFTER**: _pending_

**DELTA**: _pending_

**WITNESS**: _pending_
