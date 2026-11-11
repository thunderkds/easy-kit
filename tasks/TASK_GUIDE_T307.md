# TASK_GUIDE — T307: `[admin]` runs a task from start to end; it asks only at project start, and stops only for high-impact events
**Date**: 2026-11-11
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-11 (follow-up, same day): "I saw the supervisor useless here, cause it can not make decision, can not approve, you should update it". Asked where, the user chose: with the tag. So under `[admin]` the Supervisor makes every decision and gives every approval itself, except the stops below.

User, 2026-11-11: "I just want to run the tag in case I am busy too much, so I need agent run from start to final depend on the biz domain, and the legacy docs has existed, the important thing need to ask is the initial project steps only. I mean you have all things important to do, just auto. Just stop when you got the high priority impact."

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> With `[admin]`, one request runs the whole pipeline with no question to the user, except at project start. The Supervisor decides from the business domain: `PRD.md`, `PROJECT_SPEC.md` and, when it exists, `docs/legacy/`. It stops only for a high-impact event (the `### Stops that stay` list). `ship` (a plan, never a deploy) runs too.

Today's gaps, from `docs/claude-md/tracks.md` (`## Auto mode`):
- Row 1–4 of `### Every user stop and its auto rule`: Stage 0 questions are answered by the Supervisor or a Debate, even on a new project. The user wants them asked.
- Row 19 and `### Never in auto mode`: `ship` stays the user's. `ship` only plans (`skills/ship/SKILL.md`: "Planner, not Deployer").
- Citations for `FACT:` and `RULE:` name code and kit docs. `docs/legacy/` and the business-domain text of `PRD.md` / `PROJECT_SPEC.md` are not named as the first place to look (`grep docs/legacy skills/resolve-question` finds nothing).

**Out of scope** (what this task explicitly does NOT do):
- Plain `[auto]` keeps today's rules. Only `[admin]` changes.
- `### Stops that stay` is unchanged: a safety-hook block, a delete with no backup, the 4th Debate, a paid action, a missing login or secret, the step limit twice.
- No deploy, no `git pull`, no force push, no `Approved by` written by the Supervisor in a project that is already approved. Row 5 stays (no change to the user's permission settings or hooks).
- No change to the merge gate code.

**Depends on**: T306 (same section of `docs/claude-md/tracks.md`; merge T306 first). Start T307 from `main` after that merge.

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; the user confirmed the three rule choices on 2026-11-11: "go ahead, all three choices are fine")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Entry point**: `### Admin tag` in `docs/claude-md/tracks.md`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | `### Admin tag` says: under `[admin]`, Stage 0 step Requirements asks the user its questions only while `PROJECT_SPEC.md` `## Readiness` has no `Approved by: user <date>` line (a new project). With that line filled, no question goes to the user: rows 1–4 run on the auto rules | "ask only the initial project steps" |
| 2 | Under `[admin]`, a decision cites the business domain first: `PRD.md`, `PROJECT_SPEC.md` glossary and `docs/legacy/` (when the folder exists) come before code. The rule is in `### Admin tag` and in `skills/resolve-question/SKILL.md` (mind its 8 KB cap) | "depend on the biz domain, legacy docs" |
| 3 | Under `[admin]`, after a merge, the Supervisor runs `Skill({ skill: "ship" })` and writes the plan. It never runs a deploy command. `### Never in auto mode` and row 19 say `ship` is allowed with `[admin]` as a plan only | "all things important to do, just auto" |
| 4 | Under `[admin]`, the Supervisor stops only for the `### Stops that stay` list, and says so in one line. The `### Stops that stay` list is byte-for-byte unchanged | "stop when high priority impact" |
| 5 | Plain `[auto]`: rows 1–4, row 19 and `ship` read as today (negative control) | scope |
| 6 | `git pull` stays blocked and `Approved by` is never written by the Supervisor under `[admin]` on a new project | scope |
| 7 | `### Admin tag` holds one list of the approvals and decisions the Supervisor gives itself under `[admin]`: rows 2–4, 7–13, 15, 17 and 21 of `### Every user stop and its auto rule`, the Requirement Fidelity Gate, the agent team, the task breakdown, the direction, a `tdd` plan, the fix choice of a finding. Each is logged `RULE`, `FACT`, `SAFER OPTION` or `DEBATED`. The Supervisor never ends such a decision with "your decision" or "please approve" | "can not make decision, can not approve" |
| 8 | The only hand-backs left under `[admin]` are named in one sentence: the `### Stops that stay` list, `Approved by` on a new project (AC 1), the settings changes of row 5, `git pull`, and the second `blocked` verify (T306). Any other "ask the user" wording in the stop text of a skill the stages run (`grill-with-docs`, `brainstorming`, `to-issues`, `craft-agent`, `settings-setup`) gets a pointer: "under `[admin]`, decide by `tracks.md` row N". Skills stay under the 8 KB cap | same |

---

## Evaluation & Acceptance

**Locked oracle**: `tests/test_t307_admin_end_to_end.py`

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | `tracks.md` after the change | `### Admin tag` holds AC 1–4 and 6–8 wording | automated text pins on the section |
| 2 | The `### Stops that stay` section | Equal to the text at the base commit | automated test (hash of the section) |
| 3 | The `[auto]` rows and `### Never in auto mode` for `[auto]` | Unchanged | automated test |
| 4 | AC 7 list and AC 8 sentence present; each skill pointer present; the skill size tests still pass | automated test + `python3 -m pytest tests/ -q` |
| 5 | A mutation: drop the "Approved by" condition or the "plan only" words | Test goes red | mutation control |
| 6 | Full suites | No regression (`test_tracks.py`, `test_auto_verify.py`, `skills/` size budget tests) | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command

```bash
python3 -m pytest tests/test_t307_admin_end_to_end.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence

> **Moved.** `tasks/TASK_REVIEW_T307.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T307.md`.

---

## Approach

**Pattern reference**: T306's test (`tests/test_t306_admin_retry_blocked.py`) and `.claude/hooks/tests/test_tracks.py`.
**Vital slice**: the `### Admin tag` paragraph, row 19 and `### Never in auto mode`, plus the test.
**Cut list**: no hook change. The Stop hook `stop_auto_mode_check.py` and the pre-bash gate stay as they are; the rules are doctrine for the Supervisor. If a hook blocks `ship` under `[admin]`, the implementer reports it and stops (escalate; do not edit the hook).

Edit `AGENTS.md` only if its `## Tracks` paragraph states "`ship` stays the user's" for `[admin]`: keep the edit to that clause.

---

## Edge Case Checklist

- [ ] "New project" is read from `## Readiness` only (`Approved by` empty or placeholder), never guessed.
- [ ] A project with `Waived:` counts as approved for AC 1.
- [ ] `ship` with no `Deployment target` in `PROJECT_SPEC.md` writes `TODO: confirm with operator` (its own rule); that is not a stop.
- [ ] Pin-test pre-flight: fill `Pre-existing pin tests` before work starts
- [ ] Stale references: grep for "ship stays the user's", "`ship` stays", "Merge, push and `ship`: never in auto mode" in `docs/claude-md/`, `AGENTS.md`, `site/`, `templates/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `docs/claude-md/tracks.md` | `### Admin tag`, row 19, `### Never in auto mode`, `### Final report` `Not done:` wording |
| `skills/grill-with-docs/SKILL.md`, `skills/brainstorming/SKILL.md`, `skills/to-issues/SKILL.md`, `skills/craft-agent/SKILL.md`, `skills/settings-setup/SKILL.md` | one pointer line each (AC 8); check each file's size cap first and report one that would pass it |
| `skills/resolve-question/SKILL.md` | one line: domain documents are the first Citation source under `[admin]` (stay under the 8 KB cap) |
| `AGENTS.md` | only the `ship` clause of `## Tracks`, if present |
| `tests/test_t307_admin_end_to_end.py` | new |
| Pre-existing pin tests | Filled 2026-11-11 before the edits. Pins that the change breaks (repoint, same pattern as earlier tasks): `.claude/hooks/tests/test_admin_tag.py::test_ac8_ship_stays_the_users_under_admin` (asserts "`ship`[^.]*stays the user's" in `### Admin tag`: contradicts AC 3); `tests/test_stage_names.py::test_ac4_each_auto_mode_row_keeps_its_rule_and_its_log_label` (row 19 must equal base with only T284's clause: add a T307 clause like T306's row 18); `.claude/hooks/tests/test_agent_guide_dedup.py` `T070_BASELINE_REF` (AGENTS.md byte identity: repoint to the AGENTS.md edit commit). Pins kept green by the wording: `tests/test_auto_verify.py:1781` ("Merge, push and `ship`: never in auto mode" in row 19), `tests/test_auto_mode.py::test_ac1_d6_never_in_auto_mode` and `test_t189_ac9_…` (the `[auto]` list), `.claude/hooks/tests/test_admin_tag.py` AC 9/AC 10 needles in `### Admin tag` and `### Never in auto mode`, `test_ac9_agents_md_tracks_paragraph_names_admin`, `tests/test_resolve_question.py` (phrases in the trimmed file: "the question", "each Scanner's finding", "the decision needed" kept), `tests/test_settings_setup.py:327` (8192 cap), `tests/test_stage_names.py::test_ac5_…` (craft-agent "asks nothing"), `tests/test_site_content.py` (site word count, `site/docs.html`). Skill sizes before: grill-with-docs 4757, brainstorming 5052, to-issues 3141, craft-agent 6561, settings-setup 4865, resolve-question 8183 (cap 8192) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/**` (non-test), `.claude/settings.json` | gate and permissions |
| `### Stops that stay` text | AC 4 |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

Test first (red), then edit docs until green, then the full suite.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run
- [ ] `security-review` run (High risk)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T307.md` (Hard-Stop Gate 5)
- [ ] Auto verify run started: `python3 .claude/hooks/stop_auto_verify.py --start T307`
- [ ] `memory/MEMORY.md` updated (Supervisor)
- [ ] Supervisor notified: ready for Stage 4
