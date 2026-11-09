# TASK_GUIDE — T300: Measure the effort table on 6 replayed C0/C1 tasks, then record a DDR
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
6. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`
7. Read `docs/ddr/0009-measure-token-work-from-transcripts-and-aim-at-focus.md` (the DDR style and the meter rules) and `scripts/token_meter.py` (module docstring only)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-09: *"execute T300"*, on the plan doc `easy-kit — update plan (base)`: "Measure first: run 6 C0/C1 tasks on the current table and the proposed table with `scripts/token_meter.py`. Record cost and pass rate. Keep the proposed table only if cost is lower and no pass is lost. Otherwise record the result in a DDR and stop." The talk's claim to test: a strong model at low effort costs less than a weaker model at high effort and scores better.

**Restated intent**:
> Replay 6 past, already-solved C0/C1 tasks twice in clean copies of the repo (no git history, so the solution cannot be read). Arm A uses the CLI Effort Table and CLI Model Table as they stand on `main` (C0 `haiku` · `low`, C1 `sonnet` · `low`). Arm B uses the proposed table (the strong model `opus` at `low` for C0 and C1). Cost comes from `scripts/token_meter.py` with each arm's own per-model prices. A pass is the original tests of the task passing on the agent's result. Record the numbers and the verdict in a DDR. The proposed table is kept only if the total cost of arm B is lower than arm A and no task that passed in arm A fails in arm B.

**Method (the Supervisor runs the trials; this task's implementer records the result)**:
- Tasks and clean copies: `/home/hungnguyenhuu/workspace/pets/.eff-tmp/t300/candidates.json` (6 tasks, 3 C0 and 3 C1; each has a `base/` export, an `oracle/` folder of original test files and a `statement.md`).
- One trial = one `Agent()` spawn per (task, arm) with that arm's `model` and `effort`, working only in its own copy of `base/`. After the run the oracle test files are copied over the result and the oracle command is run. Pass = exit code 0.
- Cost: `python3 scripts/token_meter.py --session <agent transcript> --price-in <P_in> --price-out <P_out> --json`. The meter prices at a flat default, so each arm passes its model's prices (per MTok, prompts up to 100K tokens, from the `claude-api` skill table cached 2026-10-06): haiku-5-5 $0.10 in / $0.50 out; sonnet-5-5 $2 / $10; opus-5-5 $4 / $20. The meter's cache weights (1h write 2x, 5m write 1.25x, read 0.1x) stay as it computes them.
- Result file: `/home/hungnguyenhuu/workspace/pets/.eff-tmp/t300/results.json` (per trial: task, arm, model, effort, tokens, cost, oracle exit code, last pytest line, wall time).

**Known limits (say them in the DDR)**: one run per cell, so noise is not measured; replayed tasks are small and Python; the agent runs without the kit's hooks for its copy; the minimal track (where the Supervisor codes and spawns nothing) is not covered by any table cell.

**Out of scope** (what this task explicitly does NOT do):
- Changing `## CLI Model Table` or `## CLI Effort Table` in `PROJECT_SPEC.md` or the template. If the verdict is to keep the proposed table, a follow-up task does that, because the model-table pin tests and the other repos' tables are affected.
- Running the trials (the Supervisor does) or any new script in `scripts/`
- `AGENTS.md`, `PROJECT_KANBAN.md`, `memory/**`

**Requirement Refs**: None — kit-internal.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, 2026-11-09, from the plan doc and the user's "execute T300")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: T297, T298 (merged 2026-11-09: the effort table and the spawn that passes it)

**Entry point**: `docs/ddr/` (new DDR `0010-...`), `docs/ddr/data/t300-effort-trial.json` (new)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `docs/ddr/data/t300-effort-trial.json` holds one record per trial (6 tasks x 2 arms = 12), copied from the Supervisor's `results.json`, with the prices used per arm | Method |
| 2 | A new DDR `docs/ddr/0010-...md` has: the table of 6 tasks x 2 arms (model, effort, cost, oracle result), the totals per arm and per Complexity level, the verdict, the known limits above, and what follows from the verdict | Restated intent |
| 3 | The verdict in the DDR equals the rule applied to the data: `keep` only if the total cost of arm B < the total cost of arm A and no task passed in A and failed in B; otherwise `do not keep` | Restated intent |
| 4 | Every number in the DDR table equals the value in the JSON (the test recomputes totals from the JSON) | Restated intent |
| 5 | The DDR says plainly that the tables in `PROJECT_SPEC.md` and the template are unchanged, and on a `keep` verdict names the follow-up (a task to change them) | Out of scope |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the test first and sees it fail. The test must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The JSON and the DDR | 12 records; the DDR table rows match them; totals recompute | new `tests/test_t300_effort_measurement.py` |
| 2 | The verdict rule | The DDR verdict equals the rule applied to the JSON | same test file |
| 3 | Mutation: change one cost in the JSON | The table-match test turns red | mutation control that changes bytes |
| 4 | Mutation: flip the verdict word in the DDR | The verdict test turns red | mutation control that changes bytes |
| 5 | Mutation: make one oracle result in arm B a failure with a lower cost | The verdict rule (as the test computes it) says `do not keep` | mutation control on the rule |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_t300_effort_measurement.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T300.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T300.md`.

---

## Approach

**Pattern reference**: `docs/ddr/0009-measure-token-work-from-transcripts-and-aim-at-focus.md` for the DDR shape; `tests/test_cli_model_table.py` for a test that reads a doc as text.

**Vital slice**: the JSON, the DDR with the table and verdict, the test that recomputes the totals and the verdict.
**Cut list**: no chart, no HTML report, no change to the tables, no script.

---

## Edge Case Checklist

- [ ] Write for a reader who has not followed the project: plain words, short sentences, one idea each (AGENTS.md Writing Principles)
- [ ] The data come from the Supervisor's `results.json`: copy them, never invent or round a number (round only in the DDR, and say so)
- [ ] A trial that errored or timed out is a record with `oracle_exit` of 1 and a note, never dropped (a dropped failure would hide a lost pass)
- [ ] Pin-test pre-flight: grep `tests/` and `.claude/hooks/tests/` for `docs/ddr` (a test may count or list the DDR files) and fill the `Pre-existing pin tests` row below before work starts
- [ ] Stale references: `memory/MEMORY.md` and the decisions entry for T297-T299 say T300 is unmeasured; do not edit them (Supervisor-only), name the line in your report so the Supervisor updates it (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| docs/ddr/0010-effort-table-measured-on-replayed-tasks.md (new) | The DDR |
| docs/ddr/data/t300-effort-trial.json (new) | The 12 records and the prices |
| tests/test_t300_effort_measurement.py (new) | AC 1-5 and the mutation controls |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for `docs/ddr` and the DDR index; repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `PROJECT_SPEC.md`, `templates/PROJECT_SPEC_template.md`, `docs/claude-md/**`, `skills/**` | The tables and rules are not changed by this task |
| `AGENTS.md`, `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes or size ratchet |

---

## Test Plan

Write the test for the Acceptance Criteria first and see it fail. Add the JSON and the DDR. Run the verification command and the full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` (bare `pytest` skips the hidden hook tests; set `TMPDIR` and `--basetemp` to a folder in your home, not `/tmp`). Run each mutation control, paste the red output, restore, and paste the green output.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium/High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
