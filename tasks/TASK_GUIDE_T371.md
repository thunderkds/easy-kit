# TASK_GUIDE — T371: Under `[admin]` the sensitive-path hook approves and logs instead of asking
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

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "continue [admin] 371 and 374". The T371 board row, with the user's scope line "with [admin] I think it's good, just make sure you logs the high priority approval is good to go":
- Under `[admin]` the hook approves a sensitive-path ask instead of asking.
- Reads pass with no log.
- Writes, deletes, moves and runs are approved AND logged: time, session, task, command and matched pattern, to an append-only log, plus one line in the task's final report.
- Outside `[admin]` it still asks.
- A hard deny stays a deny.

**Restated intent**:
1. `[admin]` is the session tag, read from the transcript (`auto_mode.session_request`, which honours `[stop]`, another tag and a resume).
2. A read passes with no output.
3. Any other sensitive call gets no decision (the normal permission flow; the hook never emits `allow`, T146). The hook first appends one JSON line to `<anchors base>/<repo slug>/sensitive-admin-<session>.jsonl`, and emits an `additionalContext` note that asks for the final-report line.
4. A call that touches the guard's own files (`PROTECTED_PATTERNS`) still asks, a read included.
5. A call whose log line cannot be written asks.

**Out of scope**: headless verify sessions (no `[admin]` is typed there, so they still ask); a Stop-check rule that enforces the report line (the note asks for it); changing which paths are sensitive.

**Requirement Refs**: T146 (never `allow`), T314/T316 (protected patterns), T317 (session tags), T148 (the anchors folder).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row and the user's scope line — auto (Supervisor), `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (session tag, sensitive path, anchors folder: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T363, T374 (Done, not merged yet: this branch is stacked on T374's)
**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` (PreToolUse hook on `Edit|Write|Bash`).

---

## Acceptance Criteria

1. Without `[admin]` (or after `[stop]`, or with a tag the user did not type), every sensitive call asks, and nothing is logged.
2. Under `[admin]`, these get no decision, and each appends one log line naming session, task, tool, target and patterns:
   - a Write of `.env`
   - `rm -rf config` (holding `.env`)
   - `printf x > .env`
   - `mv config/.env /tmp/x`

   The `additionalContext` names the log.
3. Under `[admin]`, a read (`cat config/.env`, `grep -rn KEY config`, `ls -a config`, `find config -name …`, `git diff -- …`, a pipe of reads) passes with no log line. A read with a redirect, `tee`, `find -delete`, `git diff --output=…` or a destructive segment is a write.
4. Under `[admin]`, a read or a write of `.claude/sensitive-paths.txt`, `.claude/state/**`, the approval file, or `rm -rf .claude` still asks.
5. Under `[admin]`, a log folder that cannot be created or a symlinked log file asks.
6. The log only grows (append), one line per approved call.
7. Every earlier sensitive-path and `tracks.md` test passes unchanged; `docs/claude-md/tracks.md` `### Admin tag` says the rule.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | no tag / `[stop]` / untyped tag | ask | automated (`.claude/hooks/tests/test_t371_admin_approval.py`) |
| 2 | `[admin]`, writes | no decision + one log line each | automated (same file) |
| 3 | `[admin]`, reads | no output, no log | automated (same file) |
| 4 | `[admin]`, the guard's own files | ask | automated (same file) |
| 5 | log not writable / symlinked | ask | automated (same file) |
| 6 | two approvals | two lines | automated (same file) |
| 7 | older suites | pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t371_admin_approval.py .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py tests/test_tracks.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T371.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T371.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a PreToolUse hook and doctrine text.

---

## Approach

**Pattern reference**: the merge gate's tag reading (`pre_bash_block_unsafe_merge.py`: `auto_mode.session_request`, then `latest_request`/`admin_request`); the run records in the anchors folder (`verify_record.record_dir`).

**Vital slice**: four helpers in the hook:
- `admin_in_force(event)`
- `only_reads(tool_name, tool_input)`, which reads both forms of `_segment_command`, as T374 does
- `admin_log_path(root, session_id)`
- `log_admin_approval(...)`

In `main()`, after the unpredicted hits are known and only under `[admin]`: a read exits silent; a call with no protected-pattern hit is logged and gets the note; anything else falls through to the ask. Every exception still becomes an ask.

**Decisions** (3-Advocate Debate, 2026-11-25): Advocates 2 and 3 say the protected patterns still ask for a write (reads pass), and the log lives in the anchors folder (`.claude/settings.json` denies agents writes there), opened with `O_NOFOLLOW`. A sub-agent of an `[admin]` session inherits, because only the user's typed request sets the tag.

**Cut list**: no `allow` decision; no report-line enforcement in the Stop check; no read-only allowance outside `[admin]`; `sed -n` and `cp` count as writes (a log line, not an ask).

---

## Edge Case Checklist

- [x] A transcript with no readable request, or no session id: no `[admin]` (ask), and no log path (ask)
- [x] `[stop]` in the latest request, or after the tag, ends it
- [x] A tag in a tool result or a sub-agent prompt does not count (`origin.kind` must be "human")
- [x] An unknown command in a read pipe makes the call a write (a log line)
- [x] Pin-test pre-flight: the sensitive-path suites and `tests/test_tracks.py` / `tests/test_t306_admin_retry_blocked.py` (read `### Admin tag`) — unchanged, must pass
- [x] Stale references: the hook header; `docs/claude-md/tracks.md` `### Admin tag`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | the four helpers, the `main()` branch, the header |
| `.claude/hooks/tests/test_t371_admin_approval.py` (new) | AC 1–6 |
| `docs/claude-md/tracks.md` | `### Admin tag`: "Sensitive paths (T371)" paragraph |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | the user's settings (its anchor deny rules already cover the log folder) |
| `.claude/sensitive-paths.txt` | unchanged |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | the merge gate's own tag rules are unchanged |

---

## Test Plan

Test first: the new file fails on T374's branch (`18 failed, 6 passed` at 2026-11-25T13:13:29Z). Then the change, the Verification Command, and the full suite compared with the `main` baseline.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T371.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log
