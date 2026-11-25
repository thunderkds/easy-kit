# TASK_GUIDE — T346: `gh_merge_hit` strips heredoc bodies before it unquotes words
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Medium
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

**User request (verbatim, 2026-11-25)**: "continue your work by picking tasks [admin]". The T346 board row: "The T320 check (`gh_merge_hit`) unquotes `<<'EOF'` to `<<EOF` before stripping heredoc bodies, so a heredoc body that names a GitHub merge command is scanned and the command is blocked; strip heredoc bodies first, with a test."

**Restated intent**:
1. `_gh_merge_hit` calls `strip_heredoc_bodies` on the raw command first, then `GH_QUOTED_WORD`, then `strip_quoted_spans`.
2. A heredoc body that only names `gh pr merge …` is data: the check does not hit, and the gate lets the command through.
3. A real `gh` merge outside the heredoc body is still a hit, and a heredoc that feeds a shell is still scanned.

**Out of scope**: `strip_heredoc_bodies` itself (T294); the `git` merge patterns; the per-segment GraphQL and ref-API check (it already strips first).

**Requirement Refs**: T320 (the check), T294 (heredoc stripping).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row — Supervisor, `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T320 (Done).
**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` `_gh_merge_hit` (the PreToolUse merge gate on `Bash`).

---

## Acceptance Criteria

1. `gh_merge_hit` is False for each of: a quoted-tag heredoc (`<<'EOF'`, `<<"EOF"`) whose body names a `gh` merge command (plain, to a file, the API form, and the `git commit -m "$(cat <<'EOF' … )"` form).
2. The gate lets those commands through while a task is In Progress.
3. `gh_merge_hit` is True for a real `gh` merge before or after a heredoc, for a quoted-verb merge (`gh pr "merge" 12`) after a heredoc, and for a heredoc that feeds a shell (`bash <<'EOF'`).
4. Every T320 test passes unchanged.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | heredoc body names a merge | no hit | automated (`.claude/hooks/tests/test_t346_heredoc_gh_merge.py`) |
| 2 | the same, through the gate | allowed | automated (same file) |
| 3 | a real merge near a heredoc | hit | automated (same file) |
| 4 | T320 suite | pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t346_heredoc_gh_merge.py .claude/hooks/tests/test_t320_gh_merge_gate.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T346.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T346.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a PreToolUse hook.

---

## Approach

**Vital slice**: swap the order of two calls in one line of `_gh_merge_hit`. Test first: the new file fails on `main` for the commit-message form (`2 failed, 12 passed`, 2026-11-25).

**Cut list**: no change to `strip_heredoc_bodies`; no new patterns.

---

## Edge Case Checklist

- [x] A heredoc that feeds a shell stays visible (AC 3)
- [x] A quoted verb after a heredoc is still unquoted and caught (AC 3)
- [x] Pin-test pre-flight: `test_t320_gh_merge_gate.py` and the merge-gate suites — unchanged, must pass

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_gh_merge_hit`: strip heredoc bodies before unquoting |
| `.claude/hooks/tests/test_t346_heredoc_gh_merge.py` (new) | AC 1–3 |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/shell_data.py` | `strip_heredoc_bodies` is unchanged (T294) |
| `.claude/settings.json` | the user's settings |

---

## Test Plan

Test first (done), then the one-line change, the Verification Command, and the full suite compared with the `main` baseline.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run (Medium risk: `security-review` run)
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T346.md` Evidence
- [ ] Auto verify pass
- [ ] Board current

---

## Questions Log

None.
