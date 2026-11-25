# TASK_GUIDE — T372: The `[admin]` loop binds on the run record's own start stamp, and a repeated tag keeps the window
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

**User request (verbatim, 2026-11-25)**: "should investigate it" (why the T367 merge was refused), registered as the board row; started by "continue with the register tasks [admin]" and the user's "Take T372 and T370" (session 43b43f7e). The row:
`[admin]` loop binding misses the Supervisor's own `--start`: `_own_start_since` reads the transcript's Bash text through `_command_segments`, which returns None for any `<`, `>`, `$`, `{`, `}`, backtick or `(` (a heredoc, a `$(...)`), and never sees a `--start` inside a script file; T367 (2026-11-25) passed auto verify but could not merge. Bind on the run record instead (it can carry the starting session id), and make a prose mention of `[admin]` in a reply ("final flow with [admin] tag is …") not reset the tag request.

**Restated intent**: (1) `python3 .claude/hooks/stop_auto_verify.py --start <ID>` writes who started the run (`started_by`, the session id from `CLAUDE_CODE_SESSION_ID`) and when (`started_at`) into the hook's run record. The merge gate's loop binding accepts that stamp as this session's own start, whatever shell form launched it. (2) In the loop binding only, the window starts at the request that turned the current session tag on. A later request with the same tag does not move it. `[stop]`, a different tag and a resume still reset it.

Correction found by the Debate: `--start T1 2>&1 | tail -3` already counts today (`OUTPUT_REDIRECT_PATTERN` strips `2>&1`; `|` is a separator). `> file`, `; echo $?`, `$VAR`, `( … )`, a heredoc and a script file do not.

**Out of scope** (cut list):
- The transcript reading of `--start` (`_own_start_since`) stays as a second way to bind: nothing that binds today stops binding, and in-flight runs with no stamp still bind.
- The name, guide and short-yes bindings, and `_session_admin_merges` for the `main` push, keep the latest tag request (`session_request` unchanged).
- Advocate 1's latent issue: in a long loop, a `main` push after the second ticket's merge sees both merges since `when` and is refused ("covers one task only"). Not changed here; recorded for a follow-up task.
- A Stop-hook-started run writes no stamp (only `--start` is the Supervisor's own call).

**Requirement Refs**: T317 (`### Session tags`, R1), T354 (`_closed_out_since`), T182 (run records); `docs/claude-md/tracks.md` `### Session tags`.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row — auto (Supervisor), `[admin]`, 2026-11-25; direction by a 3-Advocate Debate (all three proposed the stamp + the same-tag window)
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (run record, session tag, merge gate: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement
- [x] Gate sign-off: the user signed off T372 for `AUTHORISED_TASKS` (gate sign-off question, 2026-11-25, session 43b43f7e)

---

## Dependencies & Reachability

**Depends on**: None (T317, T354 merged)
**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` `admin_refusal` (loop branch) — an `[admin]`/`[ticket]` loop `git merge` or `git push`; `.claude/hooks/stop_auto_verify.py --start <ID>`.

---

## Acceptance Criteria

1. A loop task whose `--start` Bash text the transcript reader cannot parse (`… --start T900 > run.log`, or a script that runs it) binds when its run record carries `started_by` = this session's id and `started_at` at or after the tag onset, and the pass record is held by the branch.
2. A stamp from another session id, a stamp dated before the tag onset, or a stamp for a commit the branch does not hold binds nothing (no transcript `--start` either).
3. A later typed request that only repeats `[admin]` (or `[ticket]`), dated after the `--start` and the pass, does not stop the loop binding. A `[stop]` or a different tag after the pass still ends it.
4. `--start` writes `started_by` (only when `CLAUDE_CODE_SESSION_ID` matches the session-id shape) and `started_at` into the run record; a Stop-hook run and `write_record` without them write the same record as before.
5. Every T317, T323, T354, T321 and T365 test passes unchanged.
6. `docs/claude-md/tracks.md` `### Session tags` says both rules.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | stamp = this session, no parseable `--start` | merge allowed | automated (`.claude/hooks/tests/test_t372_start_stamp.py` AC 1) |
| 2 | other session / before onset / commit not held | refused | automated (same file, AC 2) |
| 3 | `[admin]` repeated after the pass | merge allowed; `[stop]` → refused | automated (same file, AC 3) |
| 4 | `--start` with/without the env var; Stop hook | stamp present / absent | automated (same file, AC 4) |
| 5 | older suites | unchanged, pass | automated (Verification Command) |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t372_start_stamp.py tests/test_t372_start_stamp_run.py .claude/hooks/tests/test_t317_loop_binding.py .claude/hooks/tests/test_t317_session_tags.py .claude/hooks/tests/test_t317_fix_round.py .claude/hooks/tests/test_t323_answered_question.py .claude/hooks/tests/test_t354_loop_closed_out_row.py .claude/hooks/tests/test_t321_admin_remote.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py tests/test_auto_verify.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T372.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T372.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: hook code and doctrine text.

---

## Approach

**Pattern reference**: `_closed_out_since` / `_pass_recorded_since` (read the hook's run record, check it is held by the branch); `session_request` (one pass over typed requests).

**Vital slice**:
- `verify_record.write_record(..., started_by=None, started_at=None)`: stores the two keys only when given.
- `stop_auto_verify.py`: `start_one` reads `CLAUDE_CODE_SESSION_ID` (kept only when it fully matches `auto_mode.SESSION_ID`) and passes it to `start()`; `start()` adds it and the UTC start time as `--run` argv 9 and 10; `run()` passes them to `write_record`. The Stop hook path passes none. `main()` accepts the longer argv.
- `auto_mode.session_onset(source)`: the time of the request that turned the current session tag on (a same-tag request keeps it; `[stop]`, another tag, a resume reset it). `session_request` is unchanged.
- Gate: `_stamped_start_since(transcript_path, since, task_id, branch, where)` returns the earliest `started_at` of a record for the task whose `started_by` is the transcript's session id, whose `started_at` is at or after `since` (and not in the future), and whose commit the branch holds. The loop branch uses `since = onset` for `_own_start_since`, the stamp and `_session_holds`, and binds on the earlier of the two starts.

Options weighed (High risk, 3-Advocate Debate; all three proposed A + C):

| Option | Invasiveness | Regression risk | Chosen |
|---|---|---|---|
| A. Stamp `started_by`/`started_at` into the run record from `--start` | Low: additive record keys, one new gate helper | none for old records (keys absent → no stamp) | **yes** (Advocates 1, 3) |
| A'. A separate `<task>-<sha>.start.json` stamp file | Medium: a new file kind in the anchors folder | slug/cleanup code must learn it | no (Advocate 2; same fact, one more file) |
| B. Loosen the transcript parser | Medium: parser special cases | an echo or quote may start to count; scripts still missed | no (all three) |
| C. Same-tag request keeps the onset, loop branch only | Low: new function, one call site | the other bindings unchanged | **yes** (all three) |
| C'. Change `session_request` itself (keep first time, latest text) | Medium: moves `when` for every binding | widens `_session_admin_merges` (the main-push "one task" refusal) | no |

Replace vs. keep the transcript reading: Advocates proposed replacing `_own_start_since`. Kept as a second way (cut list): the safer option — it keeps what binds today, and the change is smaller.

---

## Edge Case Checklist

- [x] `CLAUDE_CODE_SESSION_ID` missing or not the id shape → no `started_by`; the stamp binds nothing (fail closed)
- [x] A stamp with `started_at` later than its pass record (clock skew, forged) → binds nothing: `_pass_recorded_since` needs the record written at or after the start (no separate future check: the test fixtures date the tag 60 s ahead)
- [x] `started_at` unparsable → ignored
- [x] Pin-test pre-flight: `tests/test_auto_verify.py` and the T182/T203 suites assert the `--run` argv length (8 or 9) and the record keys; the new argv is optional and the keys are absent when not stamped
- [x] Stale references: `docs/claude-md/tracks.md` `### Session tags` "This session ran `python3 .claude/hooks/stop_auto_verify.py --start <ID>` for it as its own Bash call" — updated

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/lib/verify_record.py` | `write_record` optional stamp keys |
| `.claude/hooks/stop_auto_verify.py` | `start_one` → `start()` → `--run` → `write_record` stamp; `main()` argv |
| `.claude/hooks/lib/auto_mode.py` | `session_onset` |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_stamped_start_since`; loop branch uses the onset and the stamp |
| `.claude/hooks/tests/test_t372_start_stamp.py` (new) | AC 1–3, AC 4 unit half, `session_onset` |
| `tests/test_t372_start_stamp_run.py` (new) | AC 4 end to end (`--start` with a stubbed `claude`) |
| `.claude/hooks/tests/merge_gate_guard.py`, `.claude/hooks/tests/test_merge_gate_guard.py` | `AUTHORISED_TASKS` gains T372; the rule it owns in the gate: the loop binds on the run record's own start stamp, and its window starts at the tag's onset. User sign-off 2026-11-25 |
| `docs/claude-md/tracks.md` | `### Session tags` binding text |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/trace_chain.py` | the slug is T369 |
| `.claude/settings.json` | the user's settings |
| `ADMIN_MAIN_BRANCH` and the `main` reads | T370 |

---

## Test Plan

Test first: `test_t372_start_stamp.py` fails on `main`. Then the change, the Verification Command, and the full suite compared with the `main` baseline (`60 failed, 7958 passed`, 2026-11-25 session 43b43f7e).

---

## Questions Log

- 2026-11-25 DEBATE How should the loop bind its own `--start` robustly, and keep the window on a repeated tag? → A + C, stamp in the run record, onset only in the loop branch (Advocate 1: stamp `requester`/`started` in the record, keep the first tag time in `session_request`; Advocate 2: a separate start stamp file + `session_onset`; Advocate 3: stamp in the record + `session_since`, loop branch only) — agreement on A + C; the record over a separate file and the loop-branch-only window by the safer option (smaller change)

---

## Completion Checklist

- [ ] Implementation done
- [ ] Lint passes
- [ ] Tests pass
- [ ] Smoke test confirmed
- [ ] `memory/` updated (if new patterns learned)
- [ ] TASK_GUIDE marked complete
