# TASK_REVIEW — T352: rename the kit's Stage 5 skill `ship` to `release-plan`

> Sibling of `tasks/TASK_GUIDE_T352.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. The new name is `release-plan` — RULE: `PROJECT_KANBAN.md` § Todo, row T352 (user: "yes, register T352 with release-plan")
2. No compatibility alias named `ship` — RULE: `tasks/TASK_GUIDE_T352.md` § Requirement, Out of scope ("an alias is the clash itself")
3. History keeps the old name (`tasks/`, `memory/`, `docs/archive/`, `docs/brainstorming/`, ADRs/DDRs/PRDs, `CLAUDE_LEGACY.md`, the site's Change log) — RULE: `tests/test_stage_names.py:41` "D7: history stays"
4. The verb *ship* in prose stays; only the skill's name changes — RULE: `AGENTS.md` § Writing Principles (ASD-STE100), One Term, One Meaning
5. The clash is real in interactive sessions, not in headless `claude -p` (probes 1 and 2, headless haiku, $0.008, listed the kit's `ship`) — FACT: tasks/TASK_GUIDE_T352.md:21 "In the interactive session of 2026-11-24 the skill list shows `ship-local (ship)`"
6. `update.sh` is not changed: SC11 pins its existing removal of an untouched `skills/ship/` — FACT: lib/harness-update.sh:500 "removed '$_unit' — upstream no longer ships it and you never edited it."
7. AGENTS.md grew 56 bytes past its byte cap: raise the cap 22414 -> 22470 with a recorded reason, cut no other doctrine — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task"). The Advocates disagreed (Advocate 1: raise the cap, the size change is the rename itself; Advocate 2: cut the duplicate Non-Claude CLIs sentence, 78 bytes, and lower the cap to 22392); the written rule picks Advocate 1, so it is not an unsettled Debate
Checks: PENDING
Memory: PENDING
Not done: merge (admin: after the auto verify pass); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | PENDING |
| Verification command run | ☐ pass / ☐ fail | PENDING |
| Negative cases hold | ☐ pass / ☐ fail | PENDING |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | PENDING |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | PENDING |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component: the site change is text only (skill name in 6 chips/lines) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no markup or style change; same classes |
| **UI: Responsiveness at target viewports** | ☑ N/A | text length +8 chars in chips; no layout change |

---

## Demonstration

**BEFORE** (verbatim prior content, `AGENTS.md:153` at `main` `8af7a081`): `merge + close Kanban, \`Skill({ skill: "ship" })\` for release planning.` — and `skills/ship/SKILL.md:2` `name: ship`. Red run 2026-11-24T16:24:41Z: `tests/test_t352_release_plan_rename.py` 4 failed (commit `8083fb78`).

**AFTER**: `merge + close Kanban, \`Skill({ skill: "release-plan" })\` for release planning.`; `skills/release-plan/SKILL.md:2` `name: release-plan`. Headless probe 3 (haiku, $0.0036): `release-plan: Post-merge release planning (not Claude Code's \`/ship\`, which`.

**DELTA**: Stage 5's `Skill({ skill: "release-plan" })` reaches the kit's release planner in an interactive session, where Claude Code's `/ship` used to shadow it.

**WITNESS**: PENDING
