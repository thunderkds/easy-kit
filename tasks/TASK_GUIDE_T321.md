# TASK_GUIDE — T321: the `[admin]`/`[ticket]` push remote is a setting (`EASY_KIT_ADMIN_REMOTE`), not the hard-coded `origin`
**Date**: 2026-11-15
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

User, 2026-11-15, after the merge gate refused `git push github main` under a session `[admin]` (this repo's `main` tracks `github`; `origin` is another repository, `easy-kit`, 231 commits behind): the Supervisor recommended "the gate should allow the remote that `main` tracks, not only one named `origin`". User: "push it first, and start the task as you suggestin".

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> The one remote that `[admin]` and `[ticket]` may push to is chosen by the user, once, in setup — not fixed to the name `origin`. The env var `EASY_KIT_ADMIN_REMOTE` in `.claude/settings.json` `"env"` names it; unset → `origin` (today's behaviour). Every gate check that today reads `origin` (the push destination, the bare-push config keys, the fetch/push URL equality, the own-remote check, the push-target hooks/config checks, the `ls-remote` read of the real `main`) reads that one remote instead. Everything else in `[admin]`/`[ticket]` is unchanged.

**Design decisions (Supervisor, Risk High, logged here):**
1. The remote comes from the env var, never from git config (`branch.main.remote`, `remote.pushDefault`): git config is repository state an agent can change, while the env var lives in `.claude/settings.json`, a file whose edits are already a user decision, and takes effect only in a new session — FACT: `tasks/TASK_GUIDE_T315.md:31` "The mode is the env var `EASY_KIT_SENSITIVE_PATH_MODE` in `.claude/settings.json` `"env"`" (the kit's pattern for a user-chosen hook setting).
2. Value check: the value must match `REMOTE_NAME_PATTERN` (a plain remote name). Any other value (empty after strip counts as unset → `origin`; a URL, a path, `--x`, spaces) → the gate refuses every `[admin]`/`[ticket]` push with a reason naming the bad value (fail toward the human).
3. Still one remote: the setting replaces `origin`, it never adds a second allowed remote.

**Out of scope** (what this task explicitly does NOT do):
- Any change to what `[admin]`/`[ticket]` allow besides the remote's name (branches, force, refspecs, verify pass, loop binding).
- A `settings-setup` profile for the env var (the user adds the line by hand; the docs say how).
- The untagged pipeline gate (it does not check the remote).
- `gh pr merge` (T320).

**Depends on**: None (T317 merged at `0efb8c57`)

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "start the task as you suggestin", 2026-11-15)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `ADMIN_REMOTE` in `.claude/hooks/pre_bash_block_unsafe_merge.py`, read from `EASY_KIT_ADMIN_REMOTE`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `EASY_KIT_ADMIN_REMOTE` unset or empty → every existing `[admin]`/`[ticket]` test result is unchanged (`origin`) | default unchanged |
| 2 | `EASY_KIT_ADMIN_REMOTE=github`, a repo whose `github` remote is the project's own: `[admin]` `git push github main` after the task's own merge and a passed auto verify → allowed; `git push origin main` → refused naming `github` as the one remote | the remote main tracks |
| 3 | Same setting: the bare-push config keys, the fetch/push URL equality, the own-remote check, the push-target hooks/config checks and the `ls-remote` read of the real `main` all use `github` (each has a test where only the `github` side is bad and the push is refused) | every origin check moves |
| 4 | `[ticket]` with the setting: `git push github <task branch>` allowed after the pass; `git push origin <task branch>` refused | ticket too |
| 5 | A bad value (`https://x/y.git`, `../repo`, `--upload-pack=x`, `a b`) → every `[admin]`/`[ticket]` push refused with a reason naming the bad value; a merge is unaffected | fail toward the human |
| 6 | `docs/claude-md/tracks.md` `### Admin tag` and `### Session tags` and the gate's refusal text name the setting in one line each: which remote, how to set it, default `origin` | the user knows |

---

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A: hook-only change.

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t321_admin_remote.py`. The implementer may not edit it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | unset / empty setting, existing suites | unchanged results (AC 1) | existing tests |
| 2 | `github` setting, `[admin]` session, own merge + pass | `git push github main` allowed; `git push origin main` refused (AC 2) | automated test (real throwaway repos) |
| 3 | `github` setting, one bad `github`-side condition at a time | refused (AC 3) | automated test |
| 4 | `github` setting, `[ticket]` session | task-branch push to `github` allowed, to `origin` refused (AC 4) | automated test |
| 5 | each bad value | push refused naming it; merge unaffected (AC 5) | automated test |
| 6 | full suites | no regression | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t321_admin_remote.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T321.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T321.md`.

---

## Approach

**Pattern reference**: `ADMIN_REMOTE` and its readers in `.claude/hooks/pre_bash_block_unsafe_merge.py` (`_admin_push_branch`, `_origin_url`, `_own_origin_refusal`, the push-target checks near `F2b`, the round-2 `ls-remote`); fixtures in `.claude/hooks/tests/test_admin_tag.py` and `test_admin_repo_allowlist.py`. Read the env var at call time (tests set it per case).
**Vital slice**: one function returning the allowed remote name (or a refusal for a bad value), used everywhere `ADMIN_REMOTE` is read today.
**Cut list**: a setup profile for the setting; more than one allowed remote; reading git config for the remote.

## Files to Change (Predicted)

- `.claude/hooks/pre_bash_block_unsafe_merge.py`
- `.claude/hooks/tests/test_t321_admin_remote.py` (new, qa-expert, locked)
- `.claude/hooks/tests/merge_gate_guard.py` (add `T321` to `AUTHORISED_TASKS` — user sign-off required)
- `docs/claude-md/tracks.md`
