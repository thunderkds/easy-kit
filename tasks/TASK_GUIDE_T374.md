# TASK_GUIDE — T374: The T363 folder rule reads past wrapper option values, names its xargs limit, and pins its walk budget
**Date**: 2026-11-25
**Complexity Level**: C1
**Risk Level**: High
**Priority**: P2
**Assigned agent**: common-infrastructure (the Supervisor writes the code, DDR-0011)
**Agent guide**: `agents/common-infrastructure.md`

> Read relevant files from `docs/legacy/` before making any code changes. (This repo has no `docs/legacy/`: `PROJECT_SPEC.md` and `docs/claude-md/` are the source of truth.)

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "continue [admin] 371 and 374". The T374 board row comes from the T363 round-2 review (N1, N2, P3):
- `timeout -s KILL 5 rm -rf config` reads `KILL` as the duration and stays silent.
- `xargs rm -rf config` and `find . -exec sh -c 'rm {}' \;` are silent too.
- Fix: skip the `-s`/`-k` values, and name `xargs` and `find -exec sh -c` in the header's "Recorded limitations" (AC 5 of T363).
- Also pin the walk budget: one budget per call, with folders counted (two mutants stay green).

**Restated intent**:
1. A wrapper option that takes its value as the next word is read past together with that value. This covers `timeout -s/-k`, `sudo -u/-g/…`, `env -u/-C/-S` and `nice -n`. So the command after the wrapper is the one the folder rule judges.
2. The header names `xargs` and `find -exec sh -c` as open cases.
3. Tests pin that one walk budget is shared by every folder of a call, and that folders count against it.

**Out of scope**: resolving `xargs` input or `sh -c` code (they stay recorded limits); T371 (the `[admin]` approval).

**Requirement Refs**: `tasks/TASK_REVIEW_T363.md` `## Round 2` (N1, N2); T363 decision 6.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row — auto (Supervisor), `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T363 (branch `fix/t363-folder-level-sensitive`, Done, not merged yet: this branch is built on it and merges after it)
**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` (PreToolUse hook on `Edit|Write|Bash`) — a Bash call.

---

## Acceptance Criteria

1. These ask in a project whose `config/` holds `.env`:
   - `timeout -s KILL 5 rm -rf config`, `timeout -k 5 10 …`, `timeout --signal=KILL 5 …`, `timeout -sKILL 5 …`, `timeout --kill-after 3 5 …`, `timeout --preserve-status 5 …`
   - `sudo -u root rm -rf config`, `nice -n 5 rm -rf config`, `env -u HOME rm -rf config`

   `timeout -s KILL 5 ls config` stays silent.
2. The header's "Recorded limitations" names `xargs` and `find -exec sh -c`.
3. With a cap of 3 entries, `rm -rf a` (2 files) is silent and `rm -rf a b` (4 files) asks. A folder of 4 empty subfolders asks.
4. Every T363 and other sensitive-path test passes unchanged.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | each AC 1 command | ask / silent | automated (`.claude/hooks/tests/test_t374_folder_rule_followups.py`) |
| 2 | the hook header | names both | automated (same file) |
| 3 | cap 3 | as AC 3 | automated (same file) |
| 4 | the sensitive-path suites | pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T374.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T374.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a PreToolUse hook.

---

## Approach

**Pattern reference**: `_segment_command` in the same hook (T363): it already reads past `COMMAND_PREFIXES` and their options.

**Vital slice**: `PREFIX_VALUE_OPTIONS`, a map from each wrapper to the options that take a separate value. The prefix loop steps 2 words for those options and 1 for any other. A joined form (`--signal=KILL`, `-sKILL`) is one word, as before. Plus two lines in the header and one new test file.

**Cut list**: no parsing of `xargs` input or `sh -c` code; no change to the verb list.

---

## Edge Case Checklist

- [x] A joined option value (`--signal=KILL`, `-sKILL`) stays one word
- [x] An option with no value (`--preserve-status`) still steps one word
- [x] A reading command behind `timeout -s KILL` stays silent
- [x] Pin-test pre-flight: `test_t363_folder_level.py` (its `timeout 5 rm -rf config` case) — unchanged, must pass
- [x] Stale references: the hook header (the only place that lists the limits)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | `PREFIX_VALUE_OPTIONS`, the prefix loop, two header lines |
| `.claude/hooks/tests/test_t374_folder_rule_followups.py` (new) | AC 1–3 |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/sensitive-paths.txt` | unchanged |
| `.claude/hooks/lib/shell_data.py` | shared by the merge gate |

---

## Test Plan

Test first: the new file fails on the T363 branch (`4 failed, 4 passed` at 2026-11-25T11:44:04Z: the N1 cases and the header test; the N2 tests pass there, because T363's code is right and they now pin it). Then the change, the Verification Command, and the full suite compared with the `main` baseline.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T374.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log
