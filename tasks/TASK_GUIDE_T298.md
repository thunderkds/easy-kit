# TASK_GUIDE — T298: `craft-spawn-prompt` passes the effort from the table at spawn
**Date**: 2026-11-09
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P2
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read `tasks/TASK_GUIDE_T136.md` (the rule this task must keep: no hard-coded model names) and `tasks/TASK_GUIDE_T297.md` (the table contract)
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-09: *"yes, let create plan and start parallel [auto]"*, on the plan doc `easy-kit — update plan (base)`: "`craft-spawn-prompt` step 5: read effort from the table and pass it at spawn. Keep the T136 rule: no hard-coded model names." Evidence: `skills/craft-spawn-prompt/SKILL.md:68-71` (step 5) looks up only the model; `skills/craft-spawn-prompt/references/sandbox.md:7` builds `claude --settings … --model <model> -p "<prompt>"` with no effort; `claude --effort <level>` exists (`low, medium, high, xhigh, max`) and the `Agent` tool takes an `effort` parameter.

**Restated intent**:
> Step 5 reads the task's effort from the `## CLI Effort Table` row of the CLI that runs the task, next to the model. The output reports it as `<cli> · <Cn> → <model> · effort <level>`. The `Agent()` call carries the level as its `effort` parameter. The sandboxed command carries `--effort <level>`. An empty effort cell passes no effort and never stops the spawn. A cell that is not an allowed value is never put into a command.

**Contract shared with T297 and T299**: section `## CLI Effort Table`, header `| CLI | Run command | C0 | C1 | C2 | C3 |`; allowed values `low`, `medium`, `high`, `xhigh`, `max`, or empty; empty means pass no effort. T297 adds the table. This task does not need it on disk: its tests use a fixture table inside the test.

**Why Risk Medium**: a project file (`PROJECT_SPEC.md`) supplies a value that reaches a shell command line (`--effort <level>`). The skill must allowlist the value before it builds the command.

**Out of scope** (what this task explicitly does NOT do):
- Adding the table to the template or `PROJECT_SPEC.md` (T297)
- The raise-effort rule (T299)
- Changing how the model is looked up, the STOP rules for a missing model cell or CLI, or any model name
- Changing the spawn hook (`pre_agent_validate_guide.py`)
- Auto-mode row 14 of `docs/claude-md/tracks.md` (it covers the model; an empty effort cell is not a stop, so no new row)

**Requirement Refs**: None — kit-internal.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (auto (Supervisor), 2026-11-09, from the plan doc and the user's go-ahead)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None (the table contract above is fixed; T297 adds the table in parallel)

**Entry point**: `#### 5. Recommend spawn model` in `skills/craft-spawn-prompt/SKILL.md`; `skills/craft-spawn-prompt/references/sandbox.md`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Step 5 says: look the Complexity up in the CLI's row of `## CLI Effort Table` too; the effort is that cell | Restated intent |
| 2 | Step 5 says an empty effort cell, or no effort row, passes no effort and does not stop the spawn; the model STOP rules are unchanged word for word | Restated intent |
| 3 | Step 5 names the allowlist `low`, `medium`, `high`, `xhigh`, `max`; a cell outside it is never used: no effort is passed and the output says `effort none (cell "<value>" not allowed)` | Why Risk Medium |
| 4 | The output line (step 6) and the Default Notification read `<cli> · <Cn> → <model> · effort <level|none>`; the notification keeps its STOP forms | Restated intent |
| 5 | Step 6 says: pass the level as the `Agent()` `effort` parameter, and put `--effort <level>` in the sandboxed command | Restated intent |
| 6 | `references/sandbox.md` shows the command with `--effort <level>` after `--model <model>`, says to add it only for an allowed value, and shows the command without it for `none` | Restated intent |
| 7 | No hard-coded `C0→model` map or model name is added (`tests/test_cli_model_table.py` AC3, AC8 still pass); no effort map `C0→low` is hard-coded in the skill either | T136 rule |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003). The skill is text, so the tests read the skill and the reference file as text and a small helper in the test parses a fixture table.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The skill text after the change | Step 5 names `## CLI Effort Table`, the allowlist and the empty-cell rule; step 6 and the notification carry `effort` | `tests/test_craft_spawn_effort.py` (new) |
| 2 | `references/sandbox.md` | Has `--effort <level>` after `--model <model>` and the "allowed value only" sentence | same test file |
| 3 | The model STOP sentences of step 5 | Byte-identical to `main` (the test pins the three STOP phrases) | same test file |
| 4 | Mutation: delete the allowlist sentence from step 5 | The allowlist test turns red | mutation control that changes bytes |
| 5 | Mutation: delete `--effort <level>` from `sandbox.md` | The sandbox test turns red | mutation control that changes bytes |
| 6 | Mutation: add `C0 → low` to the skill | The no-hard-coded-map test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_craft_spawn_effort.py tests/test_cli_model_table.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
grep -n "effort" skills/craft-spawn-prompt/SKILL.md skills/craft-spawn-prompt/references/sandbox.md
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T298.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T298.md`.

---

## Approach

**Pattern reference**: step 5 and step 6 of `skills/craft-spawn-prompt/SKILL.md`, and `tests/test_cli_model_table.py` (how it slices step 5 and checks the output format; AC5 of that file pins the output and notification text, so read it first).

**Vital slice**: step 5 lookup + allowlist, the output/notification format, the `sandbox.md` flag. Then the tests.
**Cut list**: no script that validates the value (the skill is text the Supervisor follows; a script is a later task if the review asks for one); no Codex/Gemini effort flags (their cells stay empty, so no flag is passed); no change to `bugfix` Step 4 beyond what its own pin test forces.

---

## Edge Case Checklist

- [ ] A cell holding a shell metacharacter (`high; rm -rf ~`) is not in the allowlist, so it never reaches the command (the test covers the sentence; say so in the review)
- [ ] The skill file is already over Codex's 8 KB cap (it is skipped there): do not trim it to fit; keep the added text short
- [ ] `tests/test_cli_model_table.py` AC5 pins the output and notification wording: extend the wording, then repoint that pin (LR-0004) and list it under `Pre-existing pin tests`
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep the repo for the old output form `<cli> · <Cn> → <model>` (docs, `bugfix` skill, site, `tasks/` templates, comments) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| skills/craft-spawn-prompt/SKILL.md | Step 5, step 6, Default Notification |
| skills/craft-spawn-prompt/references/sandbox.md | `--effort <level>` rule and the no-effort form |
| tests/test_craft_spawn_effort.py (new) | AC 1-7 and the mutation controls |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_cli_model_table.py`, `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins, any test that reads `sandbox.md`, and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `templates/PROJECT_SPEC_template.md`, `PROJECT_SPEC.md`, `docs/claude-md/pipeline-stages.md` | T297 owns them (parallel task) |
| `docs/claude-md/tracks.md` | T299 owns it (parallel task) |
| `.claude/hooks/pre_agent_validate_guide.py`, `.claude/settings.json` | Not in scope |
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |

---

## Test Plan

Write the tests for the Acceptance Criteria first and see them fail. Implement. Run the verification command and the full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` (bare `pytest` skips the hidden hook tests). Run each mutation control, paste the red output, restore, and paste the green output.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium/High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
