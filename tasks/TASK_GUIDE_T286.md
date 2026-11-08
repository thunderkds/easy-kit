# TASK_GUIDE — T286: AGENTS.md byte-size ratchet, and a list of cut candidates for the user to pick
**Date**: 2026-11-08
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read `tasks/SPIKE_REPORT_T283.md` (on branch `feat/t283-karpathy-spikes`; `git show feat/t283-karpathy-spikes:tasks/SPIKE_REPORT_T283.md`), the section named under Requirement
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

From the T283 spike report, section `### 7. Steering file` and `## Recommendation` item 2. The user approved it on 2026-11-08: *"let do as your recommend"*. Evidence: `CLAUDE.md` imports `AGENTS.md` whole into every session (21,402 B, 196 lines, about 5,350 tokens by a bytes/4 estimate at commit `faa5180f`). The only size test, `tests/test_claude_md_slim.py::test_claude_md_is_at_most_200_lines`, caps lines. Since `8080fdb8` (18,226 B) 18 commits grew the file by 17% and the line cap tripped 0 times; a byte cap would have tripped 18 times. 15 of 25 rules are text only.

**Restated intent**:
> A test fails when `AGENTS.md` grows past a byte cap, so a growth is a decision, not a drift. The task also lists which text-only rules could be cut or moved, for the user to pick. It cuts nothing itself.

**Out of scope** (what this task explicitly does NOT do):
- Cutting or moving any rule, section or sentence of `AGENTS.md` (needs the user's pick, a later task)
- A new steering file (the spike answer is: do not add one)
- A hook that enforces any text-only rule
- Changing the 200-line cap test

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `tests/test_claude_md_slim.py` (the size test; the new byte test sits beside it)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | A new test `test_agents_md_is_at_most_<N>_bytes` passes on the current `AGENTS.md` and fails when `AGENTS.md` grows by one byte past the cap. `<N>` is the size of `AGENTS.md` at the time of this task's merge, not a guess | Requirement |
| 2 | The failure message says what to do: lower the file, or raise the cap in the same commit with a recorded reason (a ratchet moves down by default) | Requirement |
| 3 | `tasks/TASK_REVIEW_T286.md` holds a table of cut or move candidates: each text-only rule, its bytes, and a recommendation (keep, move to `docs/claude-md/`, or cut) with one reason. The 25-rule inventory of the spike report is the starting point; each row is re-checked against `AGENTS.md` as it is now | user pick |
| 4 | Negative: the test cannot pass by making lines longer. It reads bytes, not lines | spike finding: the line cap fired 0 times |
| 5 | `AGENTS.md` itself is byte-identical before and after this task | Out of scope |
| 6 | Docs that say 'the size test caps lines' name the byte cap too | stale-text rule (LR-0005) |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Current `AGENTS.md` | Byte test passes | `tests/test_claude_md_slim.py` |
| 2 | Copy of `AGENTS.md` plus one byte | Byte test fails with the 'lower it or raise the cap with a reason' message | same file |
| 3 | Mutation: change the cap to a larger number | The grow-by-one-byte test turns red | mutation control that changes bytes |
| 4 | `git diff main -- AGENTS.md` | Empty | `git diff --stat` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_claude_md_slim.py -q
git diff --stat main -- AGENTS.md
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T286.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T286.md`.

---

## Approach

**Pattern reference**: `tests/test_claude_md_slim.py::test_claude_md_is_at_most_200_lines` — imitate its shape and failure message. For the candidate table, start from the spike report section 7 inventory (`### 7. Steering file`, 25 rules) and re-check every row against the live file.

Note: T284 (the `[admin]` tag) edits `AGENTS.md`. Set the cap from the size `AGENTS.md` has on `main` when you start (rebase onto `main` first), and say in the review file which commit the cap was measured at.

**Vital slice**: the byte test (AC 1, 2, 4)
**Cut list**: the cut itself; a per-section byte cap; a hook

---

## Edge Case Checklist

- [ ] A merge of T284 after this task grows `AGENTS.md`: the byte test then fails by design; the T284 author raises the cap with a reason (this is the ratchet working)
- [ ] Non-ASCII characters: count bytes of the UTF-8 file, not characters
- [ ] The cap must not be computed from the file at test time (a test that reads the file's own size passes forever, LR-0003)
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| tests/test_claude_md_slim.py | Add the byte test beside the line test |
| `tasks/TASK_REVIEW_T286.md` | Cut-candidate table (AC 3) |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| AGENTS.md | Out of scope: no cut in this task |
| `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes; hook wiring is unchanged unless this guide says so |

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
