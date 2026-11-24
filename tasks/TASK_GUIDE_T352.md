# TASK_GUIDE — T352: rename the kit's Stage 5 skill `ship` to `release-plan`
**Date**: 2026-11-24
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P0
**Assigned agent**: common-infrastructure (implemented by the Supervisor, Gate 1)
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read this file completely
3. Read `agents/common-infrastructure.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

Board row T352 (registered 2026-11-24, user: "yes, register T352 with release-plan"; started: "start T352 now [admin]"): Claude Code's built-in `/ship` (Claude Ship, announced 2026-11-23: commit, push, open a PR, watch it) shadows the kit's Stage 5 skill `ship`. In the interactive session of 2026-11-24 the skill list shows `ship-local (ship)` ("Never call it yourself") and no kit `ship`, while the kit calls `Skill({ skill: "ship" })` at `AGENTS.md:153`, `docs/claude-md/pipeline-stages.md:298` and `docs/claude-md/tracks.md:630`.

**Restated intent**:
> The kit's release-planning skill has a name no Claude Code built-in uses: `release-plan`. Every live place that names the skill (doctrine, role guides, packs, templates, README/RUNBOOK, the site, the tests that pin that text) names `release-plan`. A project that updates the kit loses the old `skills/ship/` when the user never edited it, and keeps it with a warning when they did.

**Out of scope**:
- History: `tasks/`, `memory/` (except the diff-driven pass), `docs/archive/`, `docs/brainstorming/`, `docs/ddr/`, `docs/adr/`, `docs/prd/`, boards, `CLAUDE_LEGACY.md` (a frozen pre-T173 doctrine copy).
- The verb *ship* in prose ("steps to ship a release", "before they ship", the README's pipeline line): only the skill's name changes.
- Any change to what the skill does. Its body changes only where it names itself.
- A compatibility alias named `ship`: an alias is the clash itself.
- `lib/harness-update.sh`: its removal of files upstream no longer ships already exists (`lib/harness-update.sh:500`); this task pins it for `skills/ship`, it does not change it.

**Depends on**: None

**Requirement Refs**: None — kit maintenance.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (auto (Supervisor), `[admin]`)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (skill, Stage 5, auto close-out)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `skills/release-plan/SKILL.md` (was `skills/ship/SKILL.md`), loaded by `Skill({ skill: "release-plan" })`; reaches projects through `MANIFEST` `skills`, `.claude/skills` (symlink) and `plugin/skills` (symlink).

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `skills/release-plan/SKILL.md` exists with frontmatter `name: release-plan`; its description says it is not Claude Code's `/ship`; `skills/ship/` does not exist | name no built-in uses |
| 2 | No live file names the skill `ship`: no `Skill({ skill: "ship" })`, no `` `ship` `` code span, no `skills/ship`, no "`ship` skill" / "ship skill" in `AGENTS.md`, `.cursor/rules/`, `agents/`, `packs/`, `templates/`, `skills/`, `docs/claude-md/`, `docs/MULTI_AGENT.md`, `README.md`, `RUNBOOK.md`, `PROJECT_SPEC.md`, `site/`, `.claude/hooks/` (comments and docstrings) | every live place |
| 3 | Each place that named `ship` names `release-plan` (the 3 `Skill(...)` calls, Gates 5 and 6, the Stage index, the Non-Claude CLIs list, row 19, `### Never in auto mode`, `### Admin tag`) | every live place |
| 4 | An update of a project installed with `skills/ship/SKILL.md` untouched removes it and logs `removed 'skills/ship'`; with it edited, keeps it and warns | update loses the old folder |
| 5 | The plugin tree serves `release-plan` (`plugin/skills/release-plan/SKILL.md` resolves) and the generated site data (`scripts/gen_kit_explorer.py` output in `site/docs.html`) lists `release-plan`, not `ship` | every live place |
| 6 | The full suite passes, except the 5 tests that already fail on `main` (`memory/MEMORY.md` over its 42,000-char budget) | no regression |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | the repo after the change | AC 1–3, 5 hold | `tests/test_t352_release_plan_rename.py` |
| 2 | a temp project installed with the old `skills/ship/`, then updated | untouched → removed; edited → kept + warning | `tests/test_update_removals.sh` (new case) |
| 3 | headless `claude -p` in a temp project with the renamed skill | lists `release-plan` | real run |

### Verification Command

```bash
python3 -m pytest -q tests/test_t352_release_plan_rename.py && sh tests/test_update_removals.sh
```

---

## Approach

**Pattern reference**: T340 (`tests/test_t340_remove_unused_files.py`) for the "gone / exists" test shape; `tests/test_update_removals.sh` for an update case.

**Vital slice**: `git mv skills/ship skills/release-plan`, frontmatter + description, then a word-boundary replace of the skill name in the live files of AC 2, then regenerate the site data, then repoint the pin tests the text change breaks.
**Cut list**: no alias, no change to the skill's behaviour, no edit of history files, no change to `lib/harness-update.sh`.

## Edge Case Checklist

- [ ] The verb *ship* in prose stays (README line 5, RUNBOOK "steps to ship a release", pack skills "before they ship")
- [ ] `CLAUDE_LEGACY.md` stays (frozen copy)
- [ ] Pin-test pre-flight: `test_agent_guide_dedup.py` (AGENTS.md byte pin), `tests/fixtures/site_story_baseline.json`, `test_site_story.py`, `test_site_visual_first.py`, `test_kit_explorer_data.py`, `test_site_content.py`, `test_provider_adapters.py`, `test_harness_projection.sh`, `test_agents_md_primary.py`, `test_auto_mode.py`, `test_auto_verify.py`, `test_stage_names.py`, `test_t307_admin_end_to_end.py`, `test_admin_tag.py`, `test_ship_approval_gate.py`
- [ ] `.codex/skills` projection: the skill name changes there too on the next Codex install (`MANIFEST` `skills codex=.codex/skills`)
- [ ] `plugin/skills` is a symlink to `../skills`: no copy to rename

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `skills/ship/` → `skills/release-plan/` | `git mv`; `name:`, description |
| `AGENTS.md`, `.cursor/rules/agent-base.mdc`, `docs/claude-md/pipeline-stages.md`, `docs/claude-md/tracks.md`, `docs/MULTI_AGENT.md` | skill name |
| `agents/backend.md`, `agents/frontend.md`, `packs/devops/agents/devops-engineer.md`, `packs/mobile/agents/mobile-developer.md` | skill name |
| `templates/RUNBOOK_template.md`, `RUNBOOK.md`, `skills/write-better-skill/SKILL.md` | skill name |
| `.claude/hooks/stop_auto_verify.py`, `.claude/hooks/lib/auto_closeout.py` | docstring only |
| `site/docs.html`, `site/index.html` | skill name; regenerated explorer data |
| `tests/test_t352_release_plan_rename.py` | new (written first) |
| `tests/test_update_removals.sh` | new case |
| pin tests listed above | repoint |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `tasks/` (other than T352's files), `docs/archive/`, `docs/brainstorming/`, `docs/ddr/`, `docs/adr/`, `docs/prd/`, `CLAUDE_LEGACY.md` | history |
| `lib/harness-update.sh` | its removal logic is pinned, not changed |
| `.claude/settings.json` | no permission or hook change |

---

## Test Plan

Test first (red), then the rename (green), then the full suite compared with `main`.

## Completion Checklist

- [ ] Implementation done
- [ ] Stage 4: reviewer spawn `Reviewer: T352`, `code-review`, `security-review` (Risk Medium)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T352.md`
- [ ] Auto verify run started
