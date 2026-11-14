# TASK_GUIDE — T310: `[admin]` stops when a Debate does not settle a choice
**Date**: 2026-11-14
**Complexity Level**: C2
**Risk Level**: Medium
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

User, 2026-11-14, after reading https://github.com/KKKKhazix/agent-autoloop ("a background command-line agent that asks only when unsure"): "this contain the auto-loop, maybe we need it for the [admin] tag, just stop when we have unsure". The user then chose option 1 of 3 ("stop-when-unsure inside `[admin]`", no daemon, no new dependency) and answered two design questions:

- What counts as unsure: **the Debate is unsettled** — the Advocates disagree and no written rule or Citation (`path:line` or `path § <heading>`) picks one. A decision with a written rule still goes on without a stop.
- What the stop does: **pause, notify, report** — the `Paused:` line of the final report holds the question and 2–3 options, a push notification goes out, the run ends, and the user answers by replying in chat. No question file.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> Under `[admin]`, when a Debate (`resolve-question`) ends with Advocates that disagree and no written rule or Citation that picks one, the Supervisor does not choose. It writes one `Paused: unsure — …` line in the final report, sends one push notification, and ends the run. Every other decision still goes on with no question, as `### Admin tag` says today.

**Out of scope** (what this task explicitly does NOT do):
- `[auto]` alone: it keeps its rule (an unsettled Debate is decided by the Supervisor's rules and logged `⚠ decided for you`).
- A daemon, a cron or webhook trigger, a card channel, a question file such as `tasks/ASK_<ID>.md`, or any dependency on agent-autoloop.
- A new log label for decisions, a new hook, a change to `.claude/settings.json`, and a change to the merge gate (`pre_bash_block_unsafe_merge.py`).
- A way for the Supervisor to resume the run on its own. The user's reply in chat is the resume.

**Depends on**: None. T306–T309 (the `[admin]` tag) are merged.

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; the user chose option 1 and both design answers on 2026-11-14)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (Debate, Advocate, Citation, `Paused:`, Stops that stay are existing terms; "unsettled Debate" is defined once, in `tracks.md`)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `### Stops that stay` in `docs/claude-md/tracks.md` (the list `### Admin tag` points at for its stops)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `docs/claude-md/tracks.md` `### Stops that stay` gains one bullet for `[admin]` only: a Debate whose Advocates disagree and no written rule or Citation picks one. It defines "unsettled Debate" in one sentence, and says `[auto]` alone does not stop for it | what counts as unsure |
| 2 | `### Admin tag` (its `Stops:` line and its list of hand-backs) and the `### Debate size by Risk` text name the new stop, so no section says `[admin]` stops *only* for the old list | no stale text |
| 3 | The stop's content is fixed in `tracks.md`: the `Paused:` line reads `Paused: unsure — <question>; options: <A> / <B> [/ <C>]`. The Supervisor logs no decision line for it, and sends one `PushNotification` (one line, under 200 characters, leads with the task ID and the question). A "not sent" result is not an error and never blocks the pause | what the stop does |
| 4 | `skills/resolve-question/SKILL.md` tells the Supervisor to take this stop under `[admin]` when the Debate is unsettled. The file stays **at or below 8,192 bytes** (it is 8,191 today: the edit must replace text, not add it) | stop is reachable |
| 5 | The Stop check (`.claude/hooks/stop_auto_mode_check.py`) does not flag, rewrite or double-stamp a final report that holds a Supervisor-written `Paused: unsure — …` line and no decision line for that question, at Risk Medium and High. Proven by a test that runs the hook; the hook file itself stays unchanged unless that test shows it cannot accept the line (then stop and report to the Supervisor) | the stop is not punished |
| 6 | After the user answers, the Supervisor logs the answer as a numbered decision with an existing label that the Stop check accepts, and says which one in `tracks.md`. If no existing label passes the check, stop and report: do not add a label | resume |
| 7 | Negative: a Debate whose Advocates disagree **but** a written rule or Citation picks one is not a stop. `tracks.md` says so with one example | the rule is narrow |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert`, in `.claude/hooks/tests/test_t310_admin_unsure_stop.py`. The implementer may not edit it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `tracks.md` after the change | the new bullet sits under `### Stops that stay`, names `[admin]`, defines "unsettled Debate", and says `[auto]` alone is unchanged (AC 1, 7) | automated test on the doc text |
| 2 | `tracks.md` and `skills/resolve-question/SKILL.md` | no sentence says `[admin]` stops *only* for the six old stops; `SKILL.md` is at most 8,192 bytes (AC 2, 4) | automated test |
| 3 | A temp repo with an `[admin]` task at Risk Medium and a report with `Paused: unsure — <q>; options: A / B` and no decision line for `<q>` | the Stop check passes and writes nothing to the report (AC 5) | automated test that runs the hook as a subprocess |
| 4 | The same report at Risk High | same result (AC 5) | automated test |
| 5 | A report with an unsettled-Debate decision logged as `DEBATED` under `[admin]` | out of scope for the hook (it cannot know Advocates disagreed): the test pins that the hook's behavior is unchanged | mutation-free regression test |
| 6 | The full suites | no failure other than a pin test repointed for the new text | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t310_admin_unsure_stop.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T310.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T310.md`.

---

## Approach

**Pattern reference**: T306/T307's text in `### Admin tag` of `docs/claude-md/tracks.md` (how an `[admin]`-only rule is worded, with `[auto]` kept unchanged) and `.claude/hooks/tests/test_t309_hand_typed_pass_row.py` for the subprocess fixtures.
**Vital slice**: one bullet in `### Stops that stay`, the pointers in `### Admin tag` and `### Debate size by Risk`, one byte-neutral edit in `resolve-question/SKILL.md`, and one hook test.
**Cut list**: no daemon or trigger layer (cron, webhook); no question file; no new hook; no new log label; no automatic resume; no per-channel notification (Feishu etc.); no machine check that a Debate was really unsettled (the hook cannot tell, so the Supervisor's `Paused:` line is the record).

Why this shape: agent-autoloop's own "unsure" is the agent's self-report plus a risky-action list, with no classifier. Here the trigger is narrower and checkable by a reader: Advocates differ AND no written rule or Citation decides. The line is the audit record, in the same place as every other stop (`Paused:`).

Known limit to write into `### Known limits` of `tracks.md`: the hook cannot prove a Debate was unsettled, so a Supervisor can still decide an unsettled choice and log `DEBATED`. The stop is a rule, not a gate.

---

## Edge Case Checklist

- [ ] An unsettled Debate at Risk Low: Risk Low has no Debate (`### Debate size by Risk`), so no stop. Say so.
- [ ] The 4th Debate cap stop and this stop fire together: one `Paused:` line names both.
- [ ] A `PushNotification` result of "not sent": the pause still happens.
- [ ] Two unsettled questions in one run: the first one stops the run; the line holds one question.
- [ ] `[auto]` alone with an unsettled Debate: unchanged, decided and logged `⚠ decided for you`.
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for "stops only for", "only for the", "Stops that stay", "hand-backs left" in `docs/claude-md/`, `templates/`, `skills/`, `site/`, `README`, `agents/`, `tests/`, `.claude/hooks/tests/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `docs/claude-md/tracks.md` | `### Stops that stay` (new bullet), `### Admin tag` (`Stops:` line and hand-back list), `### Debate size by Risk`, `### Known limits` |
| `skills/resolve-question/SKILL.md` | one byte-neutral edit: the unsettled-Debate stop under `[admin]` |
| `.claude/hooks/tests/test_t310_admin_unsure_stop.py` | new, written by `qa-expert` |
| `AGENTS.md` | only if its `[admin]` paragraph says `[admin]` stops only for the old list (it names the tag at the Tracks paragraph; check the `stops that stay` wording) |
| `templates/TASK_REVIEW_template.md`, `templates/MINIMAL_LOG_template.md` | only if their `Paused:` hint needs the new line shape |
| Pre-existing pin tests | List each test that pins the text, size, line count, location or a baseline ref of a file this task edits, and its handling. Find them: grep `.claude/hooks/tests/` and `tests/` for the changed strings; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the memory budget tests, the Codex 8 KB skill-cap test, and any test that reads `### Admin tag`. **Filled 2026-11-14 before work:** (1) `tests/test_t307_admin_end_to_end.py` `STOPS_SHA` pins the sha256 of `### Stops that stay` byte for byte: repoint the hash (one-line comment T310). (2) `tests/test_auto_verify.py` `STOPS_THAT_STAY_SHA256`: same, repoint. (3) `.claude/hooks/tests/test_stop_attribution_t287.py` `STOPS_THAT_STAY` bullet tuple: add the new bullet, and the old last bullet ends `;` not `.`. (4) `tests/test_t307_admin_end_to_end.py` AC4/AC8 (Admin tag sentences with `only`, `one line`, `Approved by`, `row 5`, `git pull`, second `blocked`): keep all anchors in place, no change expected. (5) `tests/test_auto_mode.py` D5 stops list (substring checks): holds. (6) Size caps (`tests/test_resolve_question.py`, `tests/test_auto_mode.py`: `SKILL.md` <= 8192): hold if SKILL.md stays <= 8192. (7) `.claude/hooks/tests/test_verify_row_fill_detection.py` `TEMPLATE_PLACEHOLDER_ROW` and `is_allowed_difference`: the pin was stale before T310 (it held the pre-T309 template wording, so any fresh review file failed `test_ac6_old_vs_new_pattern...`); now read from `templates/TASK_REVIEW_template.md`. `test_agent_guide_dedup.py`, `test_vital_slice.py`, memory budget tests: no pin on `tracks.md` Stops text or `SKILL.md` (grep found none; confirmed by the full run). |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | the merge gate has an allowlist of tasks that may edit it (`merge_gate_guard.py`); this task does not need it |
| `.claude/hooks/stop_auto_mode_check.py` | stays unchanged unless AC 5 shows it cannot accept the line (then stop and report) |
| `.claude/settings.json` | permissions |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

`qa-expert` writes the oracle first (red). The implementer edits the docs and the skill until it is green, then runs the full suites. The Supervisor runs `code-review` and `security-review` (Medium risk). The real run: a fixture `[admin]` report with the new `Paused:` line goes through the Stop check as a subprocess, and its output is pasted into the review file.

---

## Completion Checklist

- [ ] Oracle written by `qa-expert`, red
- [ ] Pin-test row filled before work starts
- [ ] Implementation done
- [ ] `code-review` run
- [ ] `security-review` run (Medium risk)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T310.md` (Hard-Stop Gate 5)
- [ ] `resolve-question/SKILL.md` is at most 8,192 bytes (size pasted)
- [ ] `memory/MEMORY.md` updated (Supervisor)
- [ ] Supervisor notified: ready for Stage 4
