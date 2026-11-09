# 0010. A strong model at low effort did not pay back its price on 6 replayed C0/C1 tasks

> **What this is**: A Design Decision Record — a permanent, dated note capturing *one* design decision and the trade-off behind it.
> **Gate**: 2-of-3 — (2) surprising without context ✅ (a plan doc and a public talk suggested the opposite), (3) genuine trade-off ✅ (cost against pass rate). Not (1) hard to reverse.

---

**Status**: Accepted
**Date**: 2026-11-09
**Deciders**: User (project owner) · Supervisor
**Related**: T297–T299 (the effort table and the spawn that passes it) · T300 · DDR-0009 (the meter and its rules) · `docs/ddr/data/t300-effort-trial.json` (the 12 records) · `tests/test_t300_effort_measurement.py`

---

## Context

T297–T299 added a `## CLI Effort Table` to `PROJECT_SPEC.md`. The Supervisor passes an effort level at each spawn.

A plan doc then suggested a change. It says a strong model at low effort costs less than a weaker model at high effort, and scores better. The proposal was the strong model `opus` at `low` effort for C0 and C1 tasks.

The user asked to measure first: keep the proposed table only if cost is lower and no pass is lost. Otherwise record the result here and stop.

## How the trials ran

- The Supervisor picked 6 past tasks that were already solved: 3 at C0 (T152, T164, T104) and 3 at C1 (T292, T252, T042).
- One trial is one `Agent()` spawn per task and arm. The `model` and `effort` come from the arm.
  - Arm A is the table on `main`: C0 `haiku` · `low`, C1 `sonnet` · `low`.
  - Arm B is the proposed table: `opus` · `low` for both levels.
- Each trial ran in a copy of the repo at the commit before the original change. The copy has one git commit and no history, so the agent cannot read the solution.
- After the run, the original test files were copied over the result. The task's oracle command was then run. Pass means exit code 0.
- Cost comes from `scripts/token_meter.py`, with the prices of each arm's model (USD per MTok, prompts up to 100K tokens, from the `claude-api` skill price table cached 2026-10-06): haiku-5-5 0.10 in / 0.50 out; sonnet-5-5 2 in / 10 out; opus-5-5 4 in / 20 out. The meter's cache weights were not changed.
- The numbers below are copied from the JSON. The DDR rounds only the totals (4 decimals) and the ratio (2 decimals). The test recomputes both from the JSON.

### Which model ran

Each trial transcript records only its arm's model on every assistant call: haiku-5-5, sonnet-5-5 or opus-5-5.

The `recorded_models` field in the JSON lists `claude-opus-5-5` for every arm A trial. That field lists every model named anywhere in the transcript. The requests also declared an `advisor` tool that points at opus-5-5. That declaration is the name. No transcript shows the advisor being called. So the opus name in arm A is not spend, and arm A has no hidden opus cost.

## Results

| Task | Level | Arm | Model | Effort | Cost | Oracle | Last pytest line |
|---|---|---|---|---|---|---|---|
| T152 | C0 | A | haiku | low | $0.012755 | pass | 13 passed in 0.44s |
| T152 | C0 | B | opus | low | $0.390105 | pass | 13 passed in 0.45s |
| T164 | C0 | A | haiku | low | $0.013423 | pass | 37 passed in 0.24s |
| T164 | C0 | B | opus | low | $0.306149 | pass | 37 passed in 0.23s |
| T104 | C0 | A | haiku | low | $0.011833 | pass | 22 passed in 0.09s |
| T104 | C0 | B | opus | low | $0.277113 | pass | 22 passed in 0.07s |
| T292 | C1 | A | sonnet | low | $0.176892 | pass | 43 passed in 0.09s |
| T292 | C1 | B | opus | low | $0.545474 | fail | 23 failed, 20 passed in 0.14s |
| T252 | C1 | A | sonnet | low | $0.398823 | fail | 1 failed, 94 passed, 1 deselected in 17.67s |
| T252 | C1 | B | opus | low | $1.265544 | fail | 1 failed, 94 passed, 1 deselected in 17.58s |
| T042 | C1 | A | sonnet | low | $0.166855 | pass | 7 passed in 0.37s |
| T042 | C1 | B | opus | low | $0.415003 | pass | 7 passed in 0.25s |

### Totals

Cost in USD. Ratio is arm B divided by arm A.

| Level | Arm A | Arm B | B/A |
|---|---|---|---|
| C0 | $0.0380 | $0.9734 | 25.61 |
| C1 | $0.7426 | $2.2260 | 3.00 |
| All | $0.7806 | $3.1994 | 4.10 |

### The failures, with cause

- **T292, arm B: a lost pass.** The oracle exit code is 1 (`23 failed, 20 passed`). The oracle test expects the shared function `parse_ts` in `lib/auto_mode.py`. Arm B put it in a new file `lib/timestamps.py`. The task text did not name the file, and the behaviour was the same. By the rule it still counts: arm A passed and arm B failed.
- **T252, both arms: not a lost pass.** The oracle exit code is 1 in both arms (`1 failed`). The same test fails in both: `test_edge_a_marked_minimal_track_task_is_still_checked_without_work_by_this_session` in `test_t252_marked_ownership.py`. One test, `test_merge_gate_is_untouched`, was left out of the oracle (shown as `1 deselected`). It needs the kit's git history, and it fails on the original solution in a copy with no history. Both arms failed T252, so no arm lost a pass.

## Decision

The rule from the user: keep the proposed table only if the total cost of arm B is lower than arm A, and no task that passed in arm A failed in arm B.

**Verdict**: do not keep

- Cost: arm B costs $3.1994 and arm A costs $0.7806. Arm B is 4.10 times dearer, so the first condition fails.
- Passes: arm A passed 5 of 6 tasks and arm B passed 4 of 6. T292 passed in A and failed in B, so the second condition fails too.
- The test applies this rule to the JSON. It does not rely on this text.

## Known limits

- There is one run per cell. Noise is not measured.
- The replayed tasks are small and in Python. The change in T104 is HTML.
- The three C0 tasks changed 7, 2 and 4 lines. That is below the 10-line floor the Supervisor set. No C0 task in the repo meets it. So the C0 comparison is weak evidence.
- Trial agents ran without the kit's hooks for their copy.
- The minimal track (the Supervisor writes the code and spawns nothing) is not covered by any table cell.
- The oracle is the original test file. For two tasks it pins a choice the task text did not state: the file for `parse_ts` in T292, and the behaviour tested in T252.

## What follows

- The tables in `PROJECT_SPEC.md` and `templates/PROJECT_SPEC_template.md` are unchanged by this task.
- The verdict is `do not keep`. Nothing changes. The plan doc's suggestion stops here, and no follow-up task is made.
- This result does not show that a strong model at low effort is worse than a small model at high effort. High effort was not tried. It shows only that on these tasks the 4.1 times cost gap between the arms was not paid back by the pass rate.
