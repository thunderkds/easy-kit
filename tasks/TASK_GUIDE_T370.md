# TASK_GUIDE — T370: The default branch is the setting `EASY_KIT_DEFAULT_BRANCH`, not a hard-coded `main`
**Date**: 2026-11-25
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
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
6. C2: read `memory/codebase-map.md` for the hook layout

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "final flow with [admin] tag is automatically to merge to the main or master." (split from T368), registered as the row; started by "continue with the register tasks [admin]" and the user's "Take T372 and T370" (session 43b43f7e). The row:
`[admin]` on a repo whose default branch is `master`: `main` is hard-coded in the merge gate (`ADMIN_MAIN_BRANCH`, `REVIEW_BASE_REF`, the remote `refs/heads/main` check), `verify_record.BASE_REF` and `scripts/cleanup_task.py` `MAIN`; read the default branch once (e.g. `git symbolic-ref refs/remotes/<remote>/HEAD`, else `main`).

**Restated intent**: one reader, `auto_mode.default_branch()`, gives the default branch to all four places: the setting `EASY_KIT_DEFAULT_BRANCH` in `.claude/settings.json` `"env"` (the user's choice, like `EASY_KIT_ADMIN_REMOTE`), `main` when unset. A `master` repo works after one setting line; a `main` repo behaves exactly as today; a bad value refuses every `[admin]`/`[ticket]` merge and push.

The row's example (`git symbolic-ref refs/remotes/<remote>/HEAD`) is not used: the 3-Advocate Debate found every git source writable by an agent (`git remote set-head`, a new `main` branch, the remote URL), so it could steer which branch the gate lets it push.

Found while testing: the `[admin]` merge never checked its target branch, so a merge on `master` already ran; what failed on `master` is the push of the default branch after the merge, the review span base, the docs-only verify base and cleanup.

**Out of scope** (cut list):
- Auto-detecting the branch (Debate: unsafe). A `master` repo needs the one setting line.
- The general refusal texts that say `main` ("a push of `main` needs the task's own `[admin]` merge …") stay as they are; only the two texts that name the ref (`refs/heads/<branch>`) print the setting.
- Hardening `.claude/settings.json` against agent writes (Advocate 2: its own deny list does not name it; the same exposure as `EASY_KIT_ADMIN_REMOTE`) — reported to the user, not changed here.
- `scripts/cleanup_task.py` reads the setting from its own environment, which the agent's shell controls; it is a helper, not a gate (Advocates 1-3).

**Requirement Refs**: T321 (`EASY_KIT_ADMIN_REMOTE`, the pattern), T368; `docs/claude-md/tracks.md` `### Admin tag`.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row — auto (Supervisor), `[admin]`, 2026-11-25; direction by a 3-Advocate Debate (all three proposed the setting)
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (merge gate, admin remote: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement
- [x] Gate sign-off: the user signed off T370 for `AUTHORISED_TASKS` (gate sign-off question, 2026-11-25, session 43b43f7e)

---

## Dependencies & Reachability

**Depends on**: None (T321 merged)
**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` `admin_refusal` (a `[admin]` merge or push), `review_in_scope`; `.claude/hooks/lib/verify_record.py` `docs_only_change`; `scripts/cleanup_task.py`.

---

## Acceptance Criteria

1. `auto_mode.default_branch()`: unset or blank is `main`; a plain branch name is itself; an option, a range, `HEAD`, a space, a `.lock` or `/` end is None.
2. A `master` repo with `EASY_KIT_DEFAULT_BRANCH=master`: the `[admin]` merge and the push of `master` after it are allowed; with the setting unset the push stays refused; with the setting `master`, a push of an agent-made `main` is refused.
3. A bad setting refuses every `[admin]` merge and push, and the refusal names the setting (never `None`).
4. `verify_record.base_ref()` follows the setting (None for a bad value: no docs-only pass).
5. `scripts/cleanup_task.py` judges "merged" against the setting, and refuses on a bad value.
6. Every existing gate, verify and cleanup test passes unchanged; `docs/claude-md/tracks.md` `### Admin tag` names the setting.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | each value | `main` / itself / None | automated (`.claude/hooks/tests/test_t370_default_branch.py` AC 1) |
| 2 | `master` repo ± setting | merge + push allowed / push refused | automated (same file, AC 2) |
| 3 | bad setting | refused, names the setting | automated (same file, AC 3) |
| 4 | `base_ref()` | follows the setting | automated (same file, AC 4) |
| 5 | cleanup on `master` | cleaned / refused | automated (`tests/test_t370_cleanup_default_branch.py`) |
| 6 | older suites | unchanged, pass | automated (Verification Command) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t370_default_branch.py tests/test_t370_cleanup_default_branch.py tests/test_cleanup_task.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_t321_admin_remote.py .claude/hooks/tests/test_merge_gate_t210.py .claude/hooks/tests/test_merge_gate_guard.py .claude/hooks/tests/test_t372_start_stamp.py tests/test_auto_verify.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T370.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T370.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: hook code, a script and doctrine text.

---

## Approach

**Pattern reference**: `_admin_remote` / `_admin_remote_refusal` (T321): a setting read at call time, a strict name check, a refusal that names the value.

**Vital slice**: `auto_mode.default_branch()` (+ `DEFAULT_BRANCH_ENV`); in the gate `_main_branch()` and `_default_branch_refusal()` (first check in `admin_refusal`) replace `ADMIN_MAIN_BRANCH`, and the review span reads `refs/heads/<branch>` (whole history on a bad value: fail closed); `verify_record.base_ref()`/`_base()` replace `BASE_REF` (a bad value raises inside the fail-closed `try`s); `cleanup_task.py` reads the setting once and refuses on a bad value.

Options weighed (High risk, 3-Advocate Debate; all three proposed option A):

| Option | Invasiveness | Regression risk | Chosen |
|---|---|---|---|
| A. The setting `EASY_KIT_DEFAULT_BRANCH`, default `main` | Low: one reader, four call sites | none with the setting unset | **yes** (all three) |
| B. Detect from local refs (`refs/remotes/<r>/HEAD`, `main` else `master`) | Low | an agent's `git remote set-head` / `git branch main` steers the gate | no |
| C. `git ls-remote --symref <remote> HEAD` | Medium: network in verify and cleanup | offline failures; the remote URL is agent-writable | no |
| Reader in `auto_mode.py` vs a new `lib/default_branch.py` | — | — | `auto_mode.py` (Advocate 3; already imported by all three callers: the smaller change) |

---

## Edge Case Checklist

- [x] A bad value never becomes `refs/heads/None`: the gate refuses first; `verify_record._base()` raises inside its `try`; cleanup refuses
- [x] A `main` repo, setting unset: the same argv and refs as before (the old suites pass unchanged)
- [x] Pin-test pre-flight: no test imports `ADMIN_MAIN_BRANCH`, `REVIEW_BASE_REF` or `verify_record.BASE_REF` (grep)
- [x] Stale references: `docs/claude-md/tracks.md` `### Admin tag` gains "The default branch (T370)"

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/lib/auto_mode.py` | `default_branch()` |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_main_branch`, `_default_branch_refusal`; the `main` uses and the review span |
| `.claude/hooks/lib/verify_record.py` | `base_ref()`, `_base()` |
| `scripts/cleanup_task.py` | the setting instead of `MAIN` |
| `.claude/hooks/tests/test_t370_default_branch.py`, `tests/test_t370_cleanup_default_branch.py` (new) | AC 1–5 |
| `.claude/hooks/tests/merge_gate_guard.py`, `.claude/hooks/tests/test_merge_gate_guard.py` | `AUTHORISED_TASKS` gains T370; the rule it owns in the gate: the default branch is the setting. User sign-off 2026-11-25 |
| `docs/claude-md/tracks.md` | `### Admin tag` "The default branch (T370)" |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | the user's settings |
| `.claude/hooks/lib/trace_chain.py` | the slug is T369 |

---

## Test Plan

Test first: the two new files fail on `main` (`27 failed, 4 passed` at 2026-11-25T11:45:57Z; the 4 are the controls and the merge that already ran). Then the change, the Verification Command, and the full suite compared with the `main` baseline.

---

## Questions Log

- 2026-11-25 DEBATE Where should the merge gate, the verify base and cleanup learn the default branch so that an agent cannot steer it? → the setting `EASY_KIT_DEFAULT_BRANCH`, default `main` (Advocate 1: the setting, a reader in a new `lib/default_branch.py`; Advocate 2: the setting, a new `lib/default_branch.py`, None never formatted into a ref; Advocate 3: the setting, the reader in `auto_mode.py`) — agreement; the reader in `auto_mode.py` by the safer option (the smaller change)

---

## Completion Checklist

- [ ] Implementation done
- [ ] Lint passes
- [ ] Tests pass
- [ ] Smoke test confirmed
- [ ] `memory/` updated (if new patterns learned)
- [ ] TASK_GUIDE marked complete
