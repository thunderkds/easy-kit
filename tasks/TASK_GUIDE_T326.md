# TASK_GUIDE — T326: `[admin]` push of `main` works on git older than 2.38
**Date**: 2026-11-18
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
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in `agents/common-infrastructure.md`
6. Read `memory/codebase-map.md` (multi-file task)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-18: "yes, register both tasks, and execute 2 of them parallel [admin]" — in reply to the
Supervisor's finding: `[admin]` cannot push `main` on this machine. `.claude/hooks/tests/test_admin_tag.py`
gives 20 failed / 211 passed with `` `[admin]` does not allow this command: `git merge-tree --wri... ``
because `_main_push_refusal` (`.claude/hooks/pre_bash_block_unsafe_merge.py:2223`) runs
`git merge-tree --write-tree`, which needs git >= 2.38; this machine has `git version 2.34.1`.

**Restated intent**:
> On git older than 2.38, the `[admin]` push of `main` after the one merge of the task branch is decided
> exactly as on new git: allowed when the merge commit's tree equals the clean three-way merge of the
> remote's `main` and the branch tip, refused otherwise. The check stays fail-closed.

**Out of scope**:
- The remote name: the gate allows only `origin` (`### Admin tag` item 2). This repo's remote is `github`; not changed here.
- `main` carrying board commits besides the merge (known, `memory/learnings.md` 2026-11-16): unchanged.
- Any other rule of the merge gate.

**Requirement Refs**: none in `PRD.md` (kit has per-feature PRDs); doctrine `docs/claude-md/tracks.md` `### Admin tag` item "Merge and push".

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, [admin] 2026-11-18, RULE)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: doctrine section named above

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `_main_push_refusal`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | On git < 2.38 (and on git >= 2.38), a `main` that is one clean merge commit of the remote's `main` and the tip is allowed to push | "push of main works on old git" |
| 2 | On either git, a merge commit whose tree differs from the clean merge (an extra file changed in the merge commit) is refused | "decided exactly as on new git" |
| 3 | On either git, a conflicting merge (no clean tree) is refused | fail-closed |
| 4 | The fallback never touches the real index, working tree or refs (uses a temporary `GIT_INDEX_FILE` or an equivalent read-only path) and never runs a repo merge driver or textconv the T295 rule forbids | fail-closed, T295 |
| 5 | Any failure of the fallback (git error, timeout, unparsable output) refuses with a clear reason | fail-closed |
| 6 | `.claude/hooks/tests/test_admin_tag.py` passes in full on this machine (git 2.34.1); full hook suite has no new failures | the reported 20 failures |
| 7 | `T326` is added to `AUTHORISED_TASKS` in `.claude/hooks/tests/merge_gate_guard.py` with the rule it owns (Supervisor sign-off, [admin] 2026-11-18) | gate audit trail |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Fixture repo, git without `--write-tree` support (real 2.34 here; plus a forced-fallback path on any git) | clean merge → `None`; extra-change merge → refusal; conflict → refusal | automated test |
| 2 | Fallback git call fails | refusal string returned | automated test |

### Verification Command (exact, runnable)

```bash
uv run --with pytest python -m pytest -q .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_t326_old_git_main_push.py .claude/hooks/tests/test_merge_gate_guard.py
uv run --with pytest python -m pytest -q .claude/hooks/tests tests
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled in `tasks/TASK_REVIEW_T326.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T326.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/pre_bash_block_unsafe_merge.py` `_main_push_refusal` and `_git` — existing fail-closed git calls with timeouts.

**Vital slice**: a fallback that computes the expected merge tree without `merge-tree --write-tree` when git lacks it, plus tests that force both paths.
**Cut list**: no git upgrade instructions in installer; no change to remote-name rule.

Supervisor decision (RULE: fail-closed, smallest change): detect support once (try `merge-tree --write-tree`; on the "unknown option"/usage failure, or by `git version` < 2.38, use the fallback). Fallback: in a temp dir, `GIT_INDEX_FILE=<tmp>` with `git read-tree -i -m --aggressive <merge-base> <remote> <tip>` then `git write-tree` (fails on any unmerged entry → refuse). If `read-tree -m` with three trees cannot resolve content-level merges that `merge-tree` would (it resolves only trivial/aggressive cases), then a content merge must be refused, not guessed: a refusal there is acceptable and must be documented as a known limit in `docs/claude-md/tracks.md` (one line). Check the T295 driver rule still holds (`_admin_repo_refusal` runs first). Agent may choose an equivalent method if it is read-only and fail-closed; say why in the report.

---

## Edge Case Checklist

- [ ] Multiple merge bases (criss-cross) → refuse
- [ ] Temp index file always removed, even on exception
- [ ] Environment `GIT_INDEX_FILE`, `GIT_DIR` etc. from the caller do not leak into the fallback beyond what `_git` already sanitises
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for "merge-tree --write-tree" wording in docs/site

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | fallback in `_main_push_refusal` |
| `.claude/hooks/tests/test_t326_old_git_main_push.py` | new tests |
| `.claude/hooks/tests/merge_gate_guard.py` | add `T326` to `AUTHORISED_TASKS` |
| `docs/claude-md/tracks.md` | one line in `### Admin tag` if a known limit is added |
| Pre-existing pin tests | `test_merge_gate_guard.py`, `test_stop_auto_mode_check.py::test_merge_gate_is_untouched`, `tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged` (allowlist); any test pinning tracks.md size/lines — agent fills before work |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/stop_auto_verify.py` | T327's area / verify writer |
| `scripts/cleanup_task.py` | T327 |
| git remote config | user's decision |

---

## Test Plan

TDD: write tests forcing the fallback (monkeypatch the support check) and tests on real local git; red, then implement; run full suites.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T326.md`
- [ ] `Skill({ skill: "verify" })` run (headless auto verify)
- [ ] Supervisor notified: task ready for Stage 4 review
