# TASK_GUIDE — T364: The sub-agent sandbox profile denies the hook's protected patterns too
**Date**: 2026-11-25
**Complexity Level**: C1
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

**User request (verbatim, 2026-11-25)**: "continue your work on the pending tasks, [admin]". The task is the board row registered from the T316 code review (P3): "`scripts/gen_sandbox_profile.py` builds the sub-agent sandbox deny rules from the list's own lines only, so the hook's hard-coded protected patterns (`.claude/state/**`, `sensitive-approvals.json*`, `sensitive-paths.txt`) are not denied in `templates/subagent-sandbox.settings.json`".

**Restated intent**: the hook `.claude/hooks/pre_tool_sensitive_path.py` always treats `PROTECTED_PATTERNS` as sensitive, whatever the project's list says (T314, T316). The CLI sub-agent profile claims one deny per sensitive pattern, but it denies only the list's own lines. Today a sub-agent's write to those paths is stopped by two other layers. The hook's ask becomes a refusal under `dontAsk`, and the sandbox write-protects `.claude/` (`skills/craft-spawn-prompt/references/sandbox.md` § Limits). The permission layer of the profile does not stop it on its own: a spawn whose hook is missing or fails open, or a protected name outside `.claude/` (`sensitive-approvals.json` and `sensitive-paths.txt` match in any directory), has no profile deny. The generator reads the protected patterns from the hook, the same way it already reads `expand_braces`, so the two cannot drift.

**Out of scope**: the hook's own matching (T363); the Supervisor's `.claude/settings.json`; Read denies for the protected patterns (see Approach).

**Requirement Refs**: T316 review (`tasks/TASK_REVIEW_T316.md` if present, else the board row); T147 (`tests/test_subagent_sandbox_profile.py` header).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — auto (Supervisor), `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (sensitive path, sandbox profile: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: none (T316 merged)
**Entry point**: `python3 scripts/gen_sandbox_profile.py` (and `--check`); the profile is passed by the CLI spawn command in `skills/craft-spawn-prompt/references/sandbox.md`.

---

## Acceptance Criteria

1. `templates/subagent-sandbox.settings.json` holds an `Edit(...)` deny for each hook protected pattern: `Edit(.claude/state/**)`, `Edit(**/sensitive-approvals.json)`, `Edit(**/sensitive-approvals.json.*)`, `Edit(**/sensitive-paths.txt)`.
2. The generator takes those patterns from the hook's `PROTECTED_PATTERNS`, not from a second copy. A pattern added to `PROTECTED_PATTERNS` shows up in the generated profile, and `--check` fails until the profile is regenerated.
3. Every existing rule of the profile stays, in the same order. The new denies come after the list's own denies and before `Edit(memory/**)`.
4. `python3 scripts/gen_sandbox_profile.py --check` exits 0 on the committed profile.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | the committed profile | the 4 `Edit` denies above | automated (`tests/test_subagent_sandbox_profile.py::test_t364_hook_protected_patterns_are_denied_for_edit`) |
| 2 | a fake hook module whose `PROTECTED_PATTERNS` gains one name | `build_profile` emits `Edit(**/<name>)` | automated (`test_t364_generator_reads_protected_patterns_from_the_hook`) |
| 3 | the whole deny list | the T147 rules unchanged and in order | automated (existing T147 tests + SC1) |
| 4 | `gen_sandbox_profile.py --check` | exit 0 | automated (`test_ac3_profile_is_exactly_what_the_generator_produces`) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q tests/test_subagent_sandbox_profile.py tests/test_plugin_names.py tests/test_craft_spawn_effort.py && python3 scripts/gen_sandbox_profile.py --check
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T364.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T364.md`. BEFORE: `grep -c 'sensitive-paths.txt\|.claude/state' templates/subagent-sandbox.settings.json` prints `0`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a generator script and a JSON settings template.

---

## Approach

**Pattern reference**: `scripts/gen_sandbox_profile.py` `_expand_braces()`, which loads the hook module to share its brace expansion ("so the hook and the profile read the list identically").

**Vital slice**: load the hook module once, and read both `expand_braces` and `PROTECTED_PATTERNS` from it. Turn each protected pattern into a cwd-relative glob: a name with no `/` becomes `**/<name>`, because the hook matches it in any directory (gitignore rules). Leave a pattern that has a `/` as it is. Then emit one `Edit(...)` deny per glob, deduplicated against the list's globs.

Options weighed (Medium risk, brainstorming in place of a separate log):

| Option | Invasiveness | Regression risk | Chosen |
|---|---|---|---|
| A. Read the hook's `PROTECTED_PATTERNS`; `Edit` deny only | Low: one script, one JSON file | none for reads: sandboxed test runs still read the list | **yes** |
| B. Same, `Read` + `Edit` deny | Low | the OS sandbox takes read denies from `Read` rules too, so a sandboxed `pytest` reading `.claude/sensitive-paths.txt` (the kit's own suite does) would fail | no |
| C. Copy the four patterns into `.claude/sensitive-paths.txt` | Low | a second copy that can drift, and a project can delete its lines, which is the T314/T316 reason they are hard-coded | no |

Option A matches what the hook guards: the protected patterns protect integrity (a write that drops a protection or forges an approval), not secrecy. The hook asks on `Edit`/`Write`/`Bash`, never on `Read`.

**Cut list**: no `Read` denies for the protected patterns (option B); no change to the hook.

---

## Edge Case Checklist

- [x] A protected name with no `/` must match at any depth: `**/` prefix, as the list's `**/*.pem` lines do
- [x] `.claude/state/**` must stay cwd-relative (no leading `/`; `test_no_rule_is_anchored_at_the_profile_file`)
- [x] A protected glob already produced by the list is not emitted twice
- [x] Pin-test pre-flight: `tests/test_subagent_sandbox_profile.py` (re-derives the list's denies; `--check` drift test) and `tests/test_plugin_names.py`, `tests/test_craft_spawn_effort.py` (name the profile file). None pins the deny count
- [x] Stale references: `skills/craft-spawn-prompt/references/sandbox.md` and the generator docstring describe what the profile denies; update the sentence that says the denies come from the list only, if there is one

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `scripts/gen_sandbox_profile.py` | read `PROTECTED_PATTERNS` from the hook; emit their `Edit` denies; docstring line |
| `templates/subagent-sandbox.settings.json` | regenerated |
| `tests/test_subagent_sandbox_profile.py` | 2 new tests (SC1, SC2) |
| `skills/craft-spawn-prompt/references/sandbox.md` | the regenerate line also names the hook's `PROTECTED_PATTERNS` |
| Pre-existing pin tests | `tests/test_subagent_sandbox_profile.py` `test_ac3_profile_is_exactly_what_the_generator_produces`: stays, passes after the regenerate |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | read only; its matching is T363 |
| `.claude/sensitive-paths.txt` | option C was rejected |
| `.claude/settings.json` | the Supervisor's permissions stay as T147/T148 fixed them |

---

## Test Plan

Test first: the two new tests fail on `main`. Then the change, the regenerate and the Verification Command. Then the full suite, compared with the `main` baseline (60 failures before this task, measured 2026-11-25 for T366).

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T364.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log
