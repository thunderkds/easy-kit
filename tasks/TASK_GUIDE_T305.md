# TASK_GUIDE — T305: Plugin hooks do nothing when `setup.sh` already wired the same hook
**Date**: 2026-11-10
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P2
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

User, 2026-11-10: "just wanna make sure all update will work with claude plugin alongside" → after the report that a repo with both installs runs every gate twice: "yes, do as your recommend". The recommendation: make the plugin hooks do nothing when the repo already has its own copy from `setup.sh`, and add one README line saying to pick one install.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> A repo that has both the `setup.sh` install and the easy-kit plugin runs each gate once, not twice. A repo with only the plugin, or only `setup.sh`, behaves exactly as before.

**Out of scope** (what this task explicitly does NOT do):
- Changing `.claude/settings.json` hooks (the `setup.sh` side).
- Changing what `/easy-kit:init` copies. It copies `.claude/hooks/stop_auto_verify.py` and `.claude/hooks/lib/` into the repo; those files do not wire a hook, so they must NOT switch the plugin hook off.
- Detecting the double install at `setup.sh` time or at `/easy-kit:init` time (a warning there is a later task).
- Removing stale `/easy-kit:init` copies after a plugin update (known, documented in `commands/init.md`).

**Requirement Refs**: None — maintenance task; no `PRD.md` FR.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor; user said "yes, do as your recommend")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `hooks/hooks.json` (the plugin's hook list; Claude Code runs each `command` string)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Every command in `hooks/hooks.json` and `plugin/hooks/hooks.json` is skipped (exit 0, no output, the script does not run) when the project's `.claude/settings.json` wires that same script as a hook. | "do nothing when the repo already has its own copy" |
| 2 | The same command runs the plugin's script, with its exit code and output unchanged, when `.claude/settings.json` is missing, or does not wire that script. | "only the plugin … behaves exactly as before" |
| 3 | A `settings.json` that only mentions the script in a permission rule (for example `Bash(python3 .claude/hooks/stop_auto_verify.py:*)`) does NOT skip the hook. | `/easy-kit:init` out-of-scope note |
| 4 | A project that holds the `/easy-kit:init` copy of `.claude/hooks/stop_auto_verify.py` but no settings wiring still runs the plugin hook. | same |
| 5 | The skip test is per script: wiring script A in settings skips only A; plugin script B still runs. | "each gate once" |
| 6 | `hooks/hooks.json` and `plugin/hooks/hooks.json` stay identical; the 12 hooks and matchers still equal `.claude/settings.json` (existing `test_plugin_package.py` AC2). | existing contract |
| 7 | `README.md` Quick Start says in one line to pick one install (plugin or `setup.sh`) and what happens if both are present. | user's recommendation |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> Supervisor sign-off on the oracle: the tests below are written first (red), against the command strings in `hooks/hooks.json`, run with `sh -c` and a stub plugin root.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Temp project whose `.claude/settings.json` wires `X.py` the `setup.sh` way; stub plugin root whose `X.py` writes a marker file | Command exits 0; marker file absent | automated test, one case per hook command |
| 2 | Temp project with no `.claude/settings.json` | Stub runs: marker present; stub exit code 2 comes back as exit 2; stub stdout unchanged | automated test |
| 3 | `settings.json` has only a permission rule naming the script | Stub runs | automated test |
| 4 | Project has `.claude/hooks/stop_auto_verify.py` copy, empty `settings.json` `{}` | Stub runs | automated test |
| 5 | Settings wire A only | A skipped, B runs | automated test |
| 6 | Stdin carries a hook event JSON | Stub receives it when it runs; skip path does not fail or hang | automated test |
| 7 | Whole suite | Green | pytest |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_plugin_package.py tests/test_hooks_from_plugin.py tests/test_plugin_double_install.py -q
sh tests/test_update.sh | tail -2
claude plugin validate .
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T305.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T305.md`.

---

## Approach

**Pattern reference**: `tests/test_plugin_package.py` — loads both hook files and compares them; imitate its `load` / `hook_list` helpers.

**Vital slice**: one shell guard prefix on each of the 12 plugin hook commands, plus `tests/test_plugin_double_install.py`.
**Cut list**:
- A warning at `/easy-kit:init` or `setup.sh` time (later task).
- Any change to the `setup.sh` side or to hook scripts.

Design (Supervisor's decision; the agent may change the exact grep, not the behaviour): prefix each plugin command with a test of the project's `.claude/settings.json`, for example
`grep -qsF '<setup.sh-form of X.py>' "$CLAUDE_PROJECT_DIR/.claude/settings.json" || python3 "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/X.py"`.
The marker must be the `setup.sh` command form (`"$CLAUDE_PROJECT_DIR"/.claude/hooks/X.py`, JSON-escaped in the file), not a bare `.claude/hooks/X.py`, so a permission rule (AC 3) cannot match. Do not key on the existence of the script file: `/easy-kit:init` copies `stop_auto_verify.py` into the repo (AC 4). `grep -qs` is quiet when the file is missing. `grep` exits 1 on no match, so the `||` runs the plugin script and its exit code is the command's exit code.

Check `${CLAUDE_PROJECT_DIR}` is set for plugin hooks in Claude Code 2.1.322; if a plugin hook can run without it, the guard must fall through to running the script.

---

## Edge Case Checklist

- [ ] `$CLAUDE_PROJECT_DIR` unset or empty: guard falls through and the script runs
- [ ] `settings.json` missing or unreadable: script runs
- [ ] Path with spaces in `$CLAUDE_PROJECT_DIR`: quoting holds
- [ ] The easy-kit repo itself (wired in settings AND plugin-loaded): runs once; test AC1 covers the shape
- [ ] A second hook script whose name is a prefix of another (`pre_agent_step_limit.py` vs a longer name): the marker ends at `.py`, so no false match
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep the repo for the old command form `python3 "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/` (README, `site/`, `docs/claude-md/`, `commands/`, `tests/`, `tasks/`, `RUNBOOK.md`) and fix each that pins it

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `hooks/hooks.json` | guard prefix on each of the 12 commands |
| `plugin/hooks/hooks.json` | the same (it is a real file, not a symlink; keep identical) |
| `tests/test_plugin_double_install.py` | new: AC 1–6 against the command strings |
| `README.md` | one line in Quick Start (AC 7) |
| `commands/init.md` | one note in Step 3 if the report must tell a `setup.sh` user the plugin hooks step aside (only if short) |
| Pre-existing pin tests | `tests/test_plugin_package.py` (`SCRIPT` regex, `root_var in command`, hook count 12), `tests/test_hooks_from_plugin.py`, `tests/test_runbook_plugin_check.py`; grep `tests/` and `.claude/hooks/tests/` for `CLAUDE_PLUGIN_ROOT`; always check `test_agent_guide_dedup.py`, `test_vital_slice.py` and the memory budget tests. Handling: repoint if a test pins the old command text; narrow otherwise; escalate if one blocks. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | the `setup.sh` side stays as is |
| `.claude/hooks/*.py` | hook behaviour does not change |
| `scripts/plugin_init.py` | what init copies stays as is |
| `setup.sh`, `update.sh`, `MANIFEST` | out of scope |

---

## Test Plan

New `tests/test_plugin_double_install.py`: for each command in `hooks/hooks.json`, build a temp project and a stub plugin root (`<root>/.claude/hooks/<script>` writes a marker file and echoes stdin), then run the command with `sh -c` and `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PROJECT_DIR` set. Cases: Success Criteria 1–6. Include a mutant check: with the guard removed, case 1 fails. Then run the existing plugin tests and the update tests.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium risk: shell text in a hook command)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T305.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review
