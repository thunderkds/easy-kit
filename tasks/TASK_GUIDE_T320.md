# TASK_GUIDE — T320: the merge gate treats `gh pr merge` and the GitHub merge API as merges
**Date**: 2026-11-24
**Complexity Level**: C1
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read this file completely
3. Read `agents/common-infrastructure.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

Board row T320 (registered 2026-11-15 from the T317 code review): "The merge gate does not block `gh pr merge` or `gh api … /merges` in any mode (not in `BLOCKED_PATTERNS`); with session-wide `[admin]`/`[ticket]` (T317) and the `autonomous` profile this runs with no prompt; add them to the gate as merges". User, 2026-11-24: "yes, let go".

**Restated intent**:
> A merge made through GitHub's CLI or API goes through the same gate as `git merge`: the board checks run, and in auto mode (`[auto]`, `[admin]`, `[ticket]`) the command is blocked, because `[admin]` allows only a plain `git` merge or push of its own task branch.

**Out of scope**:
- Any new verify check. The gate's existing board-wide checks run unchanged.
- Letting `[admin]` run `gh pr merge`. The `[admin]` allowance reads git commands only, so a `gh` merge stays blocked in auto mode.
- Other `gh` write commands (`gh pr create`, `gh pr close`, `gh release`).
- A shell parser. The pattern over-blocks on doubt, like the git patterns.

**Depends on**: None

**Requirement Refs**: None — kit maintenance.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor; user said "yes, let go" to starting T320)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (merge gate, auto mode)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `BLOCKED_PATTERNS` in `.claude/hooks/pre_bash_block_unsafe_merge.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | With a task In Progress, `gh pr merge 12 --squash`, `gh -R o/r pr merge 12`, and `gh pr merge` after `cd x &&` get the same "cannot push/merge" block as `git merge` | `gh pr merge` |
| 2 | With a task In Progress, `gh api -X PUT repos/o/r/merges -f base=main -f head=x` and `gh api repos/o/r/pulls/3/merge -X PUT` are blocked the same way | `gh api … /merges` |
| 3 | With a clean board, the same commands are allowed (the gate behaves exactly as for `git merge`) | "as merges" |
| 4 | In auto mode (`[admin]` request in the transcript) every command in 1 and 2 is blocked with the auto-mode message, even with a clean board | auto mode, no prompt |
| 5 | Read-only and unrelated commands stay allowed with a task In Progress: `gh pr view 12`, `gh pr list`, `gh pr merge-base-notes` is not a command, `gh api repos/o/r/pulls/3`, and `echo "gh pr merge 12"`, `grep -n "gh pr merge" notes.md` (quoted mentions) | no false positives |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | In Progress T900, `gh pr merge 12` | block text holds `cannot push/merge` and `Tasks still In Progress: T900` | `test_t320_gh_merge_gate.py` |
| 2 | Clean board, `gh pr merge 12` | allowed | same file |
| 3 | `[admin]` request, clean board, `gh pr merge 12` | blocked, auto-mode message | same file |
| 4 | In Progress T900, `gh pr view 12` | allowed | same file |

### Verification Command

```bash
python3 -m pytest .claude/hooks/tests/test_t320_gh_merge_gate.py -q
```

---

## Approach

**Pattern reference**: `GIT_VERB_PREFIX` / `BLOCKED_PATTERNS` in `.claude/hooks/pre_bash_block_unsafe_merge.py` and `test_merge_gate_t210.py` (`test_ac1_pull_*`, the same shape for `git pull`).

**Vital slice**: two regexes added to `BLOCKED_PATTERNS`. `AUTO_MODE_PATTERNS` is derived from that list, so auto mode is covered with no other change.
**Cut list**: `gh` aliases and `gh` extensions; `curl` or `hub` calls to the GitHub API; `gh pr merge --auto` queueing is covered because it is still `gh pr merge`.

Patterns (match on the quote-stripped command, so a quoted mention is data):
- `\bgh\b[^;&|\n]*?\bpr\s+merge\b`
- `\bgh\b[^;&|\n]*?\bapi\b[^;&|\n]*?/(?:merges|pulls/[^/\s]+/merge)\b`

## Edge Case Checklist

- [ ] `gh` global flags before `pr` (`-R o/r`, `--repo o/r`) match
- [ ] A `gh pr merge` after `&&`, `;`, `|` matches (the scan is per whole command; the class stops at a separator only for the prefix)
- [ ] `gh pr view` / `gh pr list` / `gh api …/pulls/3` do not match
- [ ] A quoted mention (`echo`, `grep`) does not match
- [ ] Pin-test pre-flight: grep the tests for `BLOCKED_PATTERNS` and the pattern count (see Files to Change)
- [ ] Stale references: `docs/claude-md/tracks.md` and `site/docs.html` text that says what the gate blocks

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | two patterns in `BLOCKED_PATTERNS`; docstring/comment names them |
| `.claude/hooks/tests/test_t320_gh_merge_gate.py` | new test file (written first) |
| `docs/claude-md/tracks.md` | one line: the gate also covers `gh pr merge` and the merge API, if it lists what the gate blocks |
| Pre-existing pin tests | grep `BLOCKED_PATTERNS` and `AUTO_MODE_PATTERNS` in `.claude/hooks/tests` and `tests/` before editing; repoint any that pin the list length |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `lib/auto_mode.py`, `admin_refusal` code | the `[admin]` allowance stays git-only |
| `.claude/settings.json` | no permission change |

---

## Test Plan

Test first (red), then add the patterns (green), then run the hook test folder.

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review (Risk High)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T320.md`
- [ ] Supervisor notified: task ready for Stage 4 review
