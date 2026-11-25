# TASK_GUIDE — T365: The merge gate's T321 refusal texts name the remote, never `None`
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

**User request (verbatim, 2026-11-25)**: "continue your work on the pending tasks, [admin]". The task is the board row registered from the T321 close-out. It has four items:
(1) `EASY_KIT_ADMIN_REMOTE` naming a remote that does not exist is refused with the generic push text, not "no such remote";
(2) the verify run-record slug comes from `origin`'s URL whatever the setting, so renaming or removing `origin` hides earlier passes;
(3) under a bad value, the `[ticket]` merge refusal and `_main_push_refusal` read `None`;
(4) the `_own_origin_refusal` and `_remote_main` docstrings still say `origin`.

**Restated intent**: items 1, 3 and 4 are text fixes in `.claude/hooks/pre_bash_block_unsafe_merge.py`. A refusal says what is wrong: "this repository has no remote `<name>`", or the setting, never `None`. The docstrings name the admin remote. No refusal becomes an allow, and no allow becomes a refusal.

**Item 2 is moved to a task of its own, T369.** `repo_slug` (`.claude/hooks/lib/trace_chain.py:61`) names the folder of every trace anchor as well as every verify run record. Any change to it moves all existing records and anchors for every installed project. Choosing a slug that does not depend on a remote, and a migration that keeps earlier passes and anchors readable, is a design decision on tamper-evidence state. It is not a text fix.

**Out of scope**: item 2 (T369); the static `AUTO_MODE_LIMIT` text (T321 accepted it as it is).

**Requirement Refs**: T321 (`tasks/TASK_GUIDE_T321.md`, `.claude/hooks/tests/test_t321_admin_remote.py`); `docs/claude-md/tracks.md` `### Admin tag` "The remote (T321)".

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — auto (Supervisor), `[admin]`, 2026-11-25; item 2 split out to T369 (task breakdown, self-approved under `[admin]`)
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (merge gate, admin remote: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T321 (merged)
**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` (PreToolUse:Bash hook) — an `[admin]`/`[ticket]` `git push` or `git merge`.

---

## Acceptance Criteria

1. With `EASY_KIT_ADMIN_REMOTE=github` and no `github` remote, an `[admin]` or `[ticket]` push (named or bare) is refused with text holding "no remote `github`" and the setting's name.
2. With a value that is not a plain remote name, the `[ticket]` merge refusal and `_main_push_refusal` hold no `None`, and `_main_push_refusal` names the setting.
3. The `_own_origin_refusal` and `_remote_main` docstrings name `_admin_remote`. They no longer say only `origin`.
4. Every T321 test passes unchanged: no allow or refusal changes, only the text.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | setting `github`, remote absent | "no remote `github`" | automated (`.claude/hooks/tests/test_t365_admin_remote_texts.py` AC 1) |
| 2 | each bad value of T321's `BAD` | no `None` in either text | automated (same file, AC 2) |
| 3 | the two docstrings | name `_admin_remote` | automated (same file, AC 3) |
| 4 | T321 suite | unchanged, all pass | automated (`.claude/hooks/tests/test_t321_admin_remote.py`) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t365_admin_remote_texts.py .claude/hooks/tests/test_t321_admin_remote.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_t210.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T365.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T365.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: hook refusal texts and docstrings.

---

## Approach

**Pattern reference**: `_admin_remote_refusal()` in the same file (T321): a helper that returns the refusal text, called first in the push path.

**Vital slice**: two helpers. `_missing_remote_refusal(where)` runs `git remote get-url <remote>` and returns a refusal only when git says "No such remote". It is called right after `_admin_remote_refusal` in the push path, so the generic text never hides it. `_admin_remote_text()` returns `` `<name>` `` or the setting's description, and the `[ticket]` merge text uses it. `_main_push_refusal` returns `_admin_remote_refusal()` first when the setting is bad.

Options weighed (High risk):

| Option | Invasiveness | Regression risk | Chosen |
|---|---|---|---|
| A. New refusal checks placed before the generic one; texts only | Low: one hook, new code paths only add a refusal where one already happened | none: every case they catch was already refused | **yes** |
| B. Make `_admin_push_branch` return a reason, not None | Medium: changes a helper the tests call directly (`_admin_push_branch(...) is None`) | T321 AC 5 helper tests | no |
| C. Do item 2 here too (slug from the admin remote) | High: re-slugs every anchor and record | earlier passes and trace anchors become unreadable | no: T369 |

**Cut list**: item 2 (T369). No change to which commands are allowed.

---

## Edge Case Checklist

- [x] `git remote get-url` failing for another reason (no git, a timeout) is not "no remote": the helper returns None and the later checks refuse
- [x] The missing-remote check runs only after a good setting (`_admin_remote_refusal` first)
- [x] A bare push: `git push` with the set remote absent also names it (AC 1, bare case)
- [x] Pin-test pre-flight: `.claude/hooks/tests/test_t321_admin_remote.py` asserts `"`github`" in text` and `ENV in text` for refusals; the new text keeps both. No test pins the generic text for a missing remote
- [x] Stale references: `docs/claude-md/tracks.md` "The remote (T321)" says nothing about a missing remote; no doc change needed

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2 helpers, 3 call sites, 2 docstrings |
| `.claude/hooks/tests/test_t365_admin_remote_texts.py` (new) | AC 1–3 |
| `.claude/hooks/tests/merge_gate_guard.py`, `.claude/hooks/tests/test_merge_gate_guard.py` | `AUTHORISED_TASKS` gains T365; the rule it owns in the gate: the T321 refusal texts (a missing set remote is named, no `None`), texts only. User sign-off 2026-11-25 |
| Pre-existing pin tests | `test_t321_admin_remote.py`: stays unchanged, must pass |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/trace_chain.py`, `.claude/hooks/lib/verify_record.py` | item 2 is T369 |
| `.claude/settings.json` | the user sets `EASY_KIT_ADMIN_REMOTE` by hand |

---

## Test Plan

Test first: the new file fails on `main` (`18 failed, 1 passed`). Then the change, the Verification Command, and the full suite compared with the `main` baseline (60 failures).

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T365.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log
