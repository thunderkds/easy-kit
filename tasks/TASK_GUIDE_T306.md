# TASK_GUIDE — T306: `[admin]` retries a blocked auto verify run once, then asks the user
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
5. Note the **Complexity Level** above and apply the matching process (brainstorm / decompose / verify depth) from the Complexity matrix in your role guide (`agents/common-infrastructure.md`)
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md` for directory layout, entry points, and blast-radius hotspots

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-11: "when I use the tag admin, the agent still ask me for the /verify manual, let investigate, in admin, agent have all rights". After the investigation: "yes, retry once then ask me".

Finding: under `[admin]` the Supervisor asks the user for `/verify` whenever the headless auto verify run ends `blocked`. `docs/claude-md/tracks.md:618-622` says "On `blocked` or `fail` it merges nothing and reports why", and the report templates end with `/verify (yours)`. The merge gate accepts only a pass line that the hook wrote, so the Supervisor cannot fill the gap itself.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> With `[admin]`, when the auto verify run ends `blocked`, the Supervisor re-runs it once on its own. Only if the second run is also `blocked` does it stop and ask the user for `/verify`. A `fail` is never retried. The merge gate keeps its rule: only a hook-written pass unlocks the merge.

**Out of scope** (what this task explicitly does NOT do):
- No change to `.claude/hooks/pre_bash_block_unsafe_merge.py`, `.claude/hooks/stop_auto_verify.py` or `.claude/hooks/lib/verify_record.py`. The retry uses what `--start` already does.
- No change to the no-runtime-surface path list (the alternative the user did not choose).
- No retry under `[auto]` alone, and none after a `fail`.
- The Supervisor never writes a `verify` pass itself and never runs `/verify` in its own session.

**Requirement Refs** (FR/NFR/US IDs from `PRD.md` this task satisfies):
- None — kit-maintenance task; no `PRD.md` ID. Source: the user request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor / user — not the implementing agent)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (`grill-with-docs` run if terminology was fuzzy)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above

> An agent must NOT start implementing until this gate is checked. If anything here is unclear,
> STOP and ask the Supervisor (Karpathy: Think Before Coding).

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `### Admin tag` in `docs/claude-md/tracks.md` (the paragraph that starts "With `[admin]`, the Supervisor starts the run itself")

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `### Admin tag` says: on a `blocked` result, the Supervisor re-runs the auto verify once, on the same task, in the same `[admin]` request, without asking. It names the exact steps (below) | "retry once" |
| 2 | The steps work with `--start` as it is: `--start` refuses when the result is filled for this commit or a log exists, so the retry resets the hook's `blocked` verify row (extended) or `- verify:` line (minimal) to the unwritten state and deletes that run's log first. Precedent: commit `e5c0e26` (T295). The implementer checks this against `stop_auto_verify.py` `start()` and says so in the report if a step is wrong | "retry once" |
| 3 | After the second `blocked`, the Supervisor stops, merges nothing, says why in one line and asks the user to run `/verify <ID>`. A third run never starts | "then ask me" |
| 4 | A `fail` result is not retried: merge nothing, report why (unchanged) | keeps the gate meaningful |
| 5 | Only a hook-written pass unlocks the merge, as before. The text says the Supervisor never edits a `pass` row, never runs `/verify` in its own session, and never writes the reset row as anything but the unwritten state | gate stays |
| 6 | `[auto]` alone is unchanged: no retry, the `Not done:` line keeps `/verify (yours)` | admin only |
| 7 | `templates/TASK_REVIEW_template.md:42` and `templates/MINIMAL_LOG_template.md:59` still allow `/verify (yours)` and say it is the state after the retry also ended `blocked` | consistency |
| 8 | Every other place that says "on `blocked` … merges nothing" for `[admin]` agrees: grep `docs/claude-md/tracks.md` (lines 105, 282, 448, 622, 775 at least), `docs/claude-md/pipeline-stages.md:267`, `AGENTS.md` and `site/` | One Term, One Meaning |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: `tests/test_t306_admin_retry_blocked.py`

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `docs/claude-md/tracks.md` after the change | `### Admin tag` holds the retry-once rule, the reset-then-`--start` steps, the stop-and-ask after the second `blocked`, and the `fail` exclusion | automated test (text pins on the section, not the whole file) |
| 2 | The same file, text of the `[auto]`-only paragraphs | Unchanged: no retry words outside `### Admin tag` and the pointers to it | automated test |
| 3 | A mutation: delete the "once" or the "fail" sentence from a copy of the section | The test goes red | mutation control inside the test |
| 4 | Both templates | `/verify (yours)` still present; the retry wording is present | automated test |
| 5 | The full hook and kit suites | No regression, in particular `test_tracks.py`, `test_auto_verify.py`, the site word-count test | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_t306_admin_retry_blocked.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T306.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T306.md`.

---

## Approach

**Pattern reference**: `tests/test_t300_effort_measurement.py` and `.claude/hooks/tests/test_tracks.py` — text pins on a doc section with mutation controls.

**Vital slice**: the `### Admin tag` paragraph plus its test. The pointers elsewhere are one-line edits.
**Cut list**:
- A code path in `stop_auto_verify.py` for "retry" (a doc rule is enough while `--start` already works after a reset).
- A retry count in a state file (the rule is one retry per task per request; the Supervisor counts it in its report).
- A fix for the SKIP-on-`.json` cause (the alternative the user did not pick).

Doc-only rule. The gate is not touched, so the independent check stays: a retry that still ends `blocked` goes to the user. The risk is a Supervisor that loops, so the text must say "once" in the same sentence as the steps.

---

## Edge Case Checklist

- [ ] The reset row must not look like a pass to `has_filled_verify_row`. Use the template's unwritten row exactly (`templates/TASK_REVIEW_template.md`).
- [ ] A reset commit changes the head commit: the new log name differs, which is fine. Say whether the reset is committed before `--start` or not, after reading `start()`.
- [ ] The retry costs up to `CLAUDE_AUTO_VERIFY_BUDGET_USD` again. Say so in one sentence.
- [ ] Minimal track: the `- verify:` line is hook-written; the reset removes only the hook's `blocked` line, never a line the user wrote (T250 shape).
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep the repo for the old wording ("merges nothing and reports why", "falls back to you", `/verify (yours)`) in README, `site/`, `docs/claude-md/`, `agents/`, board notes

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `docs/claude-md/tracks.md` | `### Admin tag` retry-once rule; pointer edits at the lines named in AC 8 |
| `templates/TASK_REVIEW_template.md`, `templates/MINIMAL_LOG_template.md` | `/verify (yours)` slot wording (AC 7) |
| `docs/claude-md/pipeline-stages.md` | line 267 pointer, if it states the `blocked` rule |
| `tests/test_t306_admin_retry_blocked.py` | new: AC 1–7 pins and the mutation controls |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the strings and paths of every edited file (`test_tracks.py`, `test_auto_verify.py`, `test_agent_guide_dedup.py`, `test_vital_slice.py`, the memory budget tests, the site word-count test). Repoint or narrow each; escalate any that pins a rule this task changes. **Filled before work (2026-11-11, `git grep` at `0bc6bcd`)**: `.claude/hooks/tests/test_admin_tag.py` `AC10_NEEDLES` (6 phrases, each exactly once in `### Admin tag`: "the Supervisor starts the run itself", the `--start <ID>` command, "waits for the verdict", "never runs `/verify` in its own session", "Only on a pass does it go on to merge and push", "On `blocked` or `fail` it merges nothing") and `test_ac10_a_skip_falls_back…` ("A `skip` for any other task is `blocked`: its `/verify` then falls back to you") — kept as substrings, still true (a `blocked` run merges nothing; the user gets `/verify` after the retry); `test_ac10_agents_md…`, `.claude/hooks/tests/test_auto_verify_skip_pass.py:638-653` (Admin tag skip sentences; AGENTS.md "on `blocked` or `fail` merges nothing") and `.claude/hooks/tests/test_agent_guide_dedup.py` (`T070_BASELINE_REF = "83ac3e7a"` pins AGENTS.md) — AGENTS.md not edited, its sentence stays true; `tests/test_auto_verify.py:2258-2265` (row 18 keeps `--start <ID>` and `` `/verify (yours)` ``; line 105 keeps "Stage 5 verify is still mandatory before any merge: the Supervisor starts the headless auto verify run"); `tests/test_auto_mode.py` `D4_LINES` (template keeps "auto verify: running (T182)" and "/verify (yours)"); `.claude/hooks/stop_auto_verify.py` `SLOT_UNWRITTEN` matches `<auto verify:…>` on one line — the slot stays one line. No pin needs a repoint. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/**` (non-test) | The gate and `--start` stay as they are (Out of scope) |
| `.claude/settings.json` | Permission rules |
| `memory/MEMORY.md` | Supervisor-only writes |

---

## Test Plan

Write `tests/test_t306_admin_retry_blocked.py` first and watch it fail (red). Then edit the docs and templates until it passes. Run the full suite once at the end.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (High risk: it changes what a merge gate rule tells the Supervisor to do)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T306.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] Auto verify run started by the Supervisor: `python3 .claude/hooks/stop_auto_verify.py --start T306`
- [ ] `memory/MEMORY.md` updated (Supervisor, diff-driven pass)
- [ ] Supervisor notified: task ready for Stage 4 review
