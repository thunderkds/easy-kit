# TASK_GUIDE — T297: A `## CLI Effort Table` beside the CLI Model Table
**Date**: 2026-11-09
**Complexity Level**: C1
**Risk Level**: Low
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
6. Read the plan doc named under Requirement (the `easy-kit — update plan (base)` page; its text is quoted below)
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-09: *"yes, let create plan and start parallel [auto]"*, on the investigation of the plan doc `easy-kit — update plan (base)` (https://claude.ai/artifact/3iZvzXo14jkRZVXZuuQfBT). The doc's change: scale effort per Complexity level, not the model (talk: Lance Martin, Anthropic). Evidence in this repo: effort is set nowhere (`grep -rn effort docs/claude-md skills agents templates` finds no spawn setting); the model per level lives in `## CLI Model Table` (`templates/PROJECT_SPEC_template.md:77`, `PROJECT_SPEC.md:137`) and Stage 1 item 2 asks the user for it (`docs/claude-md/pipeline-stages.md:79-83`).

**Restated intent**:
> The project spec has a second table, `## CLI Effort Table`, directly after `## CLI Model Table`. It has the same shape: one row per CLI, one column per Complexity level C0–C3. A cell holds an effort level or is empty. The Stage 1 question asks for it. The model table, its header and its cells do not change in this task.

**Contract shared with T298 and T299** (fixed here so the three tasks run in parallel):
- Heading: `## CLI Effort Table`. Header row: `| CLI | Run command | C0 | C1 | C2 | C3 |`.
- Allowed cell values: `low`, `medium`, `high`, `xhigh`, `max`, or empty. These are the values `claude --effort` and the `Agent` tool's `effort` parameter accept.
- An empty cell means: pass no effort. It is **not** a STOP (unlike an empty model cell).
- Default `claude` row: C0 `low`, C1 `low`, C2 `medium`, C3 `high`. Default other rows (`codex`, `[cli]`): all empty.

**Out of scope** (what this task explicitly does NOT do):
- Changing any model cell (haiku → strong model waits for the T300 measurement; the plan doc says "keep the proposed table only if cost is lower and no pass is lost")
- Making `craft-spawn-prompt` read the table (T298) or the escalation rule in `tracks.md` (T299)
- Removing `model:` from the agent files (`tests/test_agent_frontmatter.py:24` requires it; the model passed at spawn overrides it)
- Minimal-track effort (the Supervisor writes the code itself; effort there is the session's `--effort`, not this table)

**Requirement Refs**: None — kit-internal.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (auto (Supervisor), 2026-11-09, from the plan doc and the user's go-ahead)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `## CLI Effort Table` in `templates/PROJECT_SPEC_template.md` and `PROJECT_SPEC.md`; Stage 1 item 2 in `docs/claude-md/pipeline-stages.md`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `templates/PROJECT_SPEC_template.md` has `## CLI Effort Table` directly after `## CLI Model Table`, with the header row `CLI \| Run command \| C0 \| C1 \| C2 \| C3` and a `claude` row of `low`, `low`, `medium`, `high` | Restated intent |
| 2 | `PROJECT_SPEC.md` has the same section with the same `claude` row; the `codex` row exists with four empty cells | Restated intent |
| 3 | Every non-empty cell of both tables is one of `low`, `medium`, `high`, `xhigh`, `max`; a test fails for any other value, and for a `claude` cell that is empty | Contract |
| 4 | `docs/claude-md/pipeline-stages.md` Stage 1 item 2 asks the user for the effort per level beside the model, says an empty effort cell means no effort is passed, and names `## CLI Effort Table` | Restated intent |
| 5 | The `## CLI Model Table` sections, their headers and cells are byte-identical to before (`tests/test_cli_model_table.py` still passes unchanged) | Out of scope |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The template and `PROJECT_SPEC.md` after the change | Both tables parse; the `claude` row reads `low, low, medium, high` | `tests/test_cli_effort_table.py` (new) |
| 2 | Mutation: change the template's `claude` C2 cell to `mediumm` | The value test turns red | mutation control that changes bytes |
| 3 | Mutation: empty the `claude` C0 cell | The non-empty `claude` test turns red | mutation control that changes bytes |
| 4 | Mutation: delete the `## CLI Effort Table` heading from `pipeline-stages.md` | The Stage 1 test turns red | mutation control that changes bytes |
| 5 | `python3 -m pytest tests/test_cli_model_table.py -q` | Passes with no edit to that file | unchanged pin test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_cli_effort_table.py tests/test_cli_model_table.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
grep -n "CLI Effort Table" templates/PROJECT_SPEC_template.md PROJECT_SPEC.md docs/claude-md/pipeline-stages.md
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T297.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T297.md`.

---

## Approach

**Pattern reference**: the `## CLI Model Table` section of `templates/PROJECT_SPEC_template.md:77-87` (copy its intro-quote style, keep the intro to three lines) and `tests/test_cli_model_table.py` (how it slices a section and parses a row).

**Vital slice**: the two tables and the value test. Then the Stage 1 sentence.
**Cut list**: no effort cells for `codex` or `gemini` (the user fills them; the kit never guesses a CLI's effort values); no cross-check with the allowlist in `craft-spawn-prompt` (T298 owns that list); no site or README change unless a pin test forces it.

---

## Edge Case Checklist

- [ ] The new section sits between `## CLI Model Table` and the next `---` rule; the pinned model-table tests slice up to the next `##` heading, so check their slice does not swallow the new section
- [ ] `PROJECT_SPEC.md` is not in `MANIFEST`: edit this repo's own copy by hand (Update never changes it)
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (the Stage 1 item 2 text, "one column per level"), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, `agents/`, `skills/craft-spawn-prompt`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| templates/PROJECT_SPEC_template.md | The new `## CLI Effort Table` section |
| PROJECT_SPEC.md | The same section with the `claude` and `codex` rows |
| docs/claude-md/pipeline-stages.md | Stage 1 item 2: ask for effort per level; empty = none passed |
| tests/test_cli_effort_table.py (new) | AC 1-4 and the mutation controls |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_cli_model_table.py` (AC1, AC6 slice the Stage 1 text), `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `skills/craft-spawn-prompt/**` | T298 owns it (parallel task) |
| `docs/claude-md/tracks.md` | T299 owns it (parallel task) |
| `agents/*.md`, `.claude/agents/**` | Keep `model:`; no change needed |
| `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes |

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
