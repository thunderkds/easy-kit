# TASK_GUIDE — T316: the sensitive-path hook treats its own pattern list as always sensitive
**Date**: 2026-11-25
**Complexity Level**: C1
**Risk Level**: High
**Priority**: P1
**Assigned agent**: Supervisor (writes the code itself, test first, in `../wt-t316`)
**Agent guide**: `agents/common-infrastructure.md`
**Track**: extended

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read this file completely
3. Read `agents/common-infrastructure.md`

> Read relevant files from `docs/legacy/` before making any code changes (this repo has none: skip when absent).

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-25: "continue the tasks as parallel [admin]" — the Supervisor picked this board ticket as one of three independent tickets to run in parallel. Board row: `.claude/sensitive-paths.txt` is not in its own list: an Edit of it gets no ask (`Edit .claude/sensitive-paths.txt: <silent>`), so an agent can drop any protection with no prompt; make the hook treat its own pattern list as always sensitive (like the T314 approval dir).

**Restated intent**:
> An Edit, Write or Bash call that touches `.claude/sensitive-paths.txt` always asks the human, the same way `.claude/state/**` does since T314: no line in the list (a `!` line, or the line removed) can unmark it, a guide's `## Files to Change (Predicted)` cannot pre-authorise it, and an online approval cannot cover it. A relative write after `cd .claude` asks too (the name is matched in any directory, as T314 S2 did for `sensitive-approvals.json`).

**Out of scope**: the plugin's own copy of the list in a plugin cache (outside the project; agents do not write there); the sandbox profile generator (`scripts/gen_sandbox_profile.py`); `.claude/settings.json`.

**Depends on**: T314 (Done)

**Requirement Refs**: None — kit maintenance; source is the board row above (T314 Stage 4 code review, P2).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the board row (Supervisor, [admin], 2026-11-25)
- [x] Every Acceptance Criterion traces to the row
- [x] Requirement Refs: none

---

## Dependencies & Reachability

**Depends on**: T314

**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` `main` (PreToolUse on Edit, Write, Bash)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Edit and Write of `.claude/sensitive-paths.txt` (relative and absolute path) ask, naming the path | Edit gets no ask today |
| 2 | A Bash call that names `.claude/sensitive-paths.txt` (e.g. `sed -i … .claude/sensitive-paths.txt`, `rm .claude/sensitive-paths.txt`) asks | Bash too |
| 3 | A `!.claude/sensitive-paths.txt` (or `!sensitive-paths.txt`) line in the list does not unmark it | no list edit can drop it |
| 4 | A guide that lists `.claude/sensitive-paths.txt` under `## Files to Change (Predicted)` (local mode) still asks | not pre-authorisable |
| 5 | Online mode with a recorded approval key for it still asks, and no pending approval is recorded for it | not approvable |
| 6 | A relative `sensitive-paths.txt` after `cd .claude` asks | the S2 case |
| 7 | A call that touches no sensitive path stays silent (exit 0, no output); the existing T146/T314 suites still pass | no over-reach |

## UI / Design Acceptance Criteria

Not applicable — no UI.

---

## Evaluation & Acceptance

**Locked oracle**: a new test file `.claude/hooks/tests/test_t316_list_self_protect.py`, written first (red for AC 1–6), then the fix.

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t314_online_approval.py .claude/hooks/tests/test_t314_fix_round.py .claude/hooks/tests/test_t314_security_round.py .claude/hooks/tests/test_t314_backslash_key.py
```

### Evidence

> **Moved.** Filled at Stage 4/5 in `tasks/TASK_REVIEW_T316.md`.

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T316.md`.

---

## Approach

`PROTECTED_PATTERNS` (`pre_tool_sensitive_path.py` ~line 90) is appended last to the project's patterns (`sensitive_hits`), so a protected pattern wins over any `!` line; `main` skips the predicted-path and approval paths for a protected hit (`protected = pat in PROTECTED_PATTERNS`, key None). Add the list's own name, `sensitive-paths.txt`, as a name pattern (no `/`: any directory) to `PROTECTED_PATTERNS`, beside `APPROVALS_NAME_PATTERNS`, and update the module docstring's "Always sensitive and never approvable" sentence and the list file's header comment.

## Files to Change (Predicted)

- `.claude/hooks/pre_tool_sensitive_path.py`
- `.claude/hooks/tests/test_t316_list_self_protect.py` (new)
- `.claude/sensitive-paths.txt` (header comment only)
- `tasks/TASK_REVIEW_T316.md`

## Files must NOT touch

- `PROJECT_KANBAN.md` (the Supervisor moves rows on `main`), `.claude/settings.json`, `.claude/hooks/pre_bash_block_unsafe_merge.py`, `scripts/gen_sandbox_profile.py`
