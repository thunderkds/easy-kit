# TASK_GUIDE — T368: `[admin]` auto verify loops back on a fail (2 fix rounds) and runs a changed shell suite instead of skipping it
**Date**: 2026-11-25
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
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

**User (2026-11-25)**: "may we want another agent to auto init another session to verify your tasks, if the verify have done, you can move on, if not, comeback to fix. It work like the debate agents" — then, to the proposal (fix rounds capped at 2; a changed shell suite gets a real run): "yes, I think. final flow with [admin] tag is automatically to merge to the main or master."

**Restated intent**: under `[admin]` the verify loop finishes without the user in two more cases.
(a) **A changed shell suite.** T367 changed only `tests/test_pack_catalog.sh`; both auto verify runs answered SKIP ("no runtime surface: tests-only"), and the hook passes a SKIP only for docs-only paths, which by T289's rule never include a `.sh` file (`docs/claude-md/tracks.md:491`). Fix: when the branch changes one or more `tests/**/test_*.sh` suites, the `/verify` request names them and asks for PASS or FAIL by each suite's exit code. The docs-only list, the merge gate and the record format do not change.
(b) **A fail loops back.** Today "A `fail` is never retried: the Supervisor reports why and stops" (`docs/claude-md/tracks.md` `### Admin tag`). New rule: on a `fail` the Supervisor fixes the cause on the task branch, gets a fresh `Reviewer: <ID>` pass on the new commit (the merge gate needs it on the code it merges), and starts a new run — at most 2 fix rounds, then it stops and says why. The one retry after `blocked` (T306) is unchanged.

**Out of scope**: `[admin]` on a repo whose default branch is `master` (T370: `main` is hard-coded in the gate, the push rule, `verify_record.BASE_REF` and `scripts/cleanup_task.py`); widening the docs-only list.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — auto (Supervisor), `[admin]` session tag, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (auto verify, run record, fix round: defined here)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T182 (auto verify), T289 (docs-only skip), T306 (one retry)
**Entry point**: `call_claude` in `.claude/hooks/stop_auto_verify.py`

---

## Acceptance Criteria

1. A branch that changes `tests/test_x.sh` (or `.claude/hooks/tests/test_x.sh`) gets `claude -p "/verify <ID> — …tests/test_x.sh…: run each … answer PASS or FAIL by its exit code"`; a branch with no changed shell suite gets exactly `"/verify <ID>"` as today.
2. Only paths that pass `verify_record.docs_only_path`'s safe-name check shape reach the prompt; a path with any other character, a `tests/lib/` file or a non-`test_*.sh` name is not named; any git doubt names none.
3. `docs/claude-md/tracks.md` `### Admin tag`: a `fail` starts a fix round (fix, fresh reviewer, new run), at most 2, then the stop; the shell-suite request is described where the SKIP rule is.
4. Existing auto-verify, merge-gate and docs-only tests stay green.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | a fixture repo whose branch changes `tests/test_x.sh` | the fake `claude` gets the long prompt naming it | automated (`tests/test_auto_verify_shell_suites_t368.py`) |
| 2 | the same with only `.py`/docs changes | the prompt is `/verify <ID>` | automated |
| 3 | `tests/lib/x.sh`, an unsafe name, two merge-bases | no suite named | automated |
| 4 | `tests/test_auto_verify.py`, merge-gate and verify-record suites | pass (same failures as `main` only) | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_auto_verify_shell_suites_t368.py tests/test_auto_verify.py .claude/hooks/tests/test_verify_record_docs_only.py -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T368.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T368.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A.

---

## Approach

**Pattern reference**: `verify_record.docs_only_change` / `_raw_diff` (one merge-base, `--raw -z`, fail closed).
**Vital slice**: `verify_record.shell_suites_changed(checkout, tip)`; `call_claude` appends the suite sentence when it returns names; the `tracks.md` paragraphs.
**Cut list**: no hook-side test execution; no new record kind; no change to the docs-only list or the merge gate.

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/lib/verify_record.py` | `shell_suites_changed` |
| `.claude/hooks/stop_auto_verify.py` | `call_claude` takes the head; prompt sentence |
| `docs/claude-md/tracks.md` | fix rounds; shell-suite request |
| `tests/test_auto_verify_shell_suites_t368.py` (new) | SC 1–3 |
| `tests/test_auto_verify.py` | only if a call signature pin moves |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | the gate's record checks stay as they are |
| `DOCS_ONLY_*` tuples in `verify_record.py` | T289's list stays |

---

## Test Plan

New pytest file with a fixture git repo and the fake `claude` the existing `tests/test_auto_verify.py` uses; the existing auto-verify and docs-only suites; the full suite against `main`.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T368.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated
- [ ] Board current

---

## Questions Log
