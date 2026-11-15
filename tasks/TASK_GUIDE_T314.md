# TASK_GUIDE — T314: in board mode `online`, the sensitive-path hook asks once per path per task, not once per call
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

User, 2026-11-15, in easy-note-mcp (board mode `online`, Linear), a backend-developer sub-agent ran a Bash call that edits `tests/fixtures/secrets/planted.json`. `.claude/hooks/pre_tool_sensitive_path.py` asked for confirmation: "board mode is online, where guides come from the board and cannot pre-authorise a sensitive path". The user: "I don't want to run it too, you got the approve for that", then "do your job" after the Supervisor proposed a kit change so an `online` task can pre-authorise its sensitive paths.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> In board mode `online`, the user approves a sensitive path once per task. After the user has said yes to a call that touches path P for task T, later calls in task T that touch only already-approved paths get no extra prompt from this hook. The trust source is the user's own approval, never board text: NFR-005 (T157) stays — a guide pulled from the board still pre-authorises nothing.

**Design decision (Supervisor, Risk High, logged here):** the hook cannot see the user's answer to its own `ask`. A PostToolUse hook fires only after the call ran, which, for a call this hook asked about, means the user approved it. So a new PostToolUse recorder writes `(task_id, normalised path)` pairs to a local approval file, and the PreToolUse hook reads that file in `online` mode. Rejected: (a) trusting the pulled guide's `## Files to Change (Predicted)` — breaks NFR-005; (b) removing `**/secrets/**` from the project's list — drops protection for every task.

**Out of scope** (what this task explicitly does NOT do):
- Any change to local board mode: the guide's `## Files to Change (Predicted)` stays its only exemption.
- Any change to `.claude/sensitive-paths.txt` patterns.
- Approval across tasks, or with no active task: no task id → every call asks, as today.
- The merge gate and the T313 hand-back text.

**Depends on**: None

**Requirement Refs**: None — kit maintenance; source is the request above. Keeps NFR-005 (T157).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; user: "do your job" on 2026-11-15)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` (PreToolUse on Edit, Write, Bash) and a new PostToolUse hook wired in `.claude/settings.json` on the same matchers

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Board `online`, active task T, call touches sensitive path P, P not approved for T → the hook asks, as today. The reason adds one sentence: after you approve, later calls in T that touch only this path will not ask again | approve once |
| 2 | After an approved call (PostToolUse fired for an Edit/Write/Bash call that touches sensitive P with active task T, board `online`), the recorder adds (T, P) to the approval file. It records only paths that match `.claude/sensitive-paths.txt`, with the same path forms and Bash parsing the PreToolUse hook uses (shared code, not a copy) | the user's approval is the trust source |
| 3 | Board `online`, task T, every sensitive path of the call is approved for T → no output, exit 0 (no decision, never `allow`), as for a predicted path in local mode | no prompt per call |
| 4 | A call touching an approved path plus an unapproved sensitive path asks, naming only the unapproved one | per path |
| 5 | An approval for task T never exempts a call under task U, nor a call with no active task | per task |
| 6 | The approval file lives under `.claude/` outside the repo's tracked files (gitignored), and its own path is always sensitive, protected inside the hook itself (not by a new line in `.claude/sensitive-paths.txt`, so `test_ac1_shipped_list_carries_the_default_patterns` stays unchanged and a project cannot drop the protection by editing its list), so an agent's Edit, Write or Bash call that touches it asks, even when the file lists itself | no forged approval |
| 7 | An unreadable, malformed or non-object approval file counts as empty (asks); the recorder never crashes the session: any recorder error exits 0 with no output | fail toward the human |
| 8 | Local board mode is unchanged: the approval file is neither read nor written; all existing tests in `.claude/hooks/tests/test_pre_tool_sensitive_path.py` pass unchanged | out of scope kept |
| 9 | `docs/claude-md/tracks.md` (or the doc that states NFR-005 for this hook) and the hook docstring say in one short paragraph how online approval works | the user knows the rule |

---

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A: hook-only change.

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t314_online_approval.py`. The implementer may not edit it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | online board, no approval file, Bash call touching `tests/fixtures/secrets/x.json`, task T | `ask`; reason names the path and the approve-once sentence (AC 1) | automated test (subprocess, JSON stdin) |
| 2 | same event fed to the PostToolUse recorder, then the PreToolUse hook again | approval file holds (T, path); second PreToolUse prints nothing, exit 0 (AC 2, 3) | automated test |
| 3 | approved path + `.env` in one call | `ask` naming `.env` only (AC 4) | automated test |
| 4 | approval for T; event for task U; event with no task | both `ask` (AC 5) | automated test |
| 5 | Write to the approval file | `ask` (AC 6); file path is matched by `git check-ignore` | automated test |
| 6 | approval file holds `[]`, `{bad`, a binary blob | `ask`; recorder with bad stdin exits 0, no stdout (AC 7) | automated test |
| 7 | local board, predicted and unpredicted paths | same outputs as before; approval file not created (AC 8) | existing tests + one new |
| 8 | full suites | no regression | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t314_online_approval.py .claude/hooks/tests/test_pre_tool_sensitive_path.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T314.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T314.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/pre_tool_sensitive_path.py` (`candidate_paths`, `path_forms`, `matching_pattern`, `resolve_task_id`, `board_mode`) — move what the recorder needs into `.claude/hooks/lib/` or import it, do not duplicate. PostToolUse wiring: the existing entries in `.claude/settings.json` `"PostToolUse"`. Approval file: `.claude/state/sensitive-approvals.json` (or the existing `.claude/` state folder the hooks already use, if one exists), shape `{"<task_id>": ["<normalised path>", ...]}`.
**Vital slice**: recorder + online read path + self-protection of the approval file + docs paragraph.
**Cut list**: expiry of approvals; a command to list or clear approvals (the user deletes the file); approvals by pattern instead of exact path; any local-mode change.

## Files to Change (Predicted)

- `.claude/hooks/pre_tool_sensitive_path.py`
- `.claude/hooks/post_tool_sensitive_approval.py` (new)
- `.claude/hooks/lib/` (shared helpers, if moved)
- `.claude/hooks/tests/test_t314_online_approval.py` (new, qa-expert, locked)
- `.claude/settings.json`
- `.gitignore`
- `docs/claude-md/tracks.md` or the doc that states NFR-005 for this hook

## Supervisor decisions during Stage 3

1. 2026-11-15, qa-expert question (AC6 vs AC8): the approval file is protected inside the hook, not by a pattern-list line — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes: AC8 keeps the existing tests unchanged) and SAFER OPTION (a project's list edit cannot remove it). Folder stays `.claude/state/` as pinned by the locked oracle; add it to `.gitignore`.
