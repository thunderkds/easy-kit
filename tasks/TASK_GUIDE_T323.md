# TASK_GUIDE — T323: a short "yes [admin]" to the Supervisor's own question binds the one task that question named
**Date**: 2026-11-16
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

User, 2026-11-16. The Supervisor asked: "Do you want me to merge `feat/t322-session-tags-docs` into `main`?" The user replied "yes [admin]". The merge gate refused: `T322 is not the task of the [admin] request: the request does not name it, and it is not the one task whose guide was first added after the request, nor the task of this session's loop`. The loop binding could not hold either: the auto verify pass predated the tag, so `stop_auto_verify.py --start T322` printed `its result is already filled for commit 8dc2bbe9bb08 — nothing started`. User: "why using the admin but got this one", then "let do what my expected", then "[admin] let completes all tasks".

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> Under `[admin]` (per-request or session tag), a request that is only a short yes, answering the Supervisor's immediately preceding visible question that names exactly one task, binds that task for the merge gate. The tag is still read only from the user's own text; the question only narrows consent to one task the user was shown. All other gate checks stay. The Supervisor's merge questions also ask for the task ID in the reply (doctrine fallback).

**Design decision (Debate, Risk High, 3 Advocates, 2026-11-16):** Advocate 1 proposed doctrine only (ask the user to type the ID). Advocates 2 and 3 proposed a strict gate path "answered question" plus that doctrine as a fallback. Decided: gate path + doctrine — RULE (Decide rule 1, necessary): the registered requirement `PROJECT_KANBAN.md:11` "bind the task the Supervisor's immediately preceding question named"; doctrine alone leaves "yes [admin]" refused (Advocate 1's own WHAT). See `## Questions Log`.

**Out of scope** (what this task explicitly does NOT do):
- `stop_auto_verify.py` (`--start` keeps refusing `FILLED`; T203's rule stays).
- The `main` push rule (one merge ahead of the remote) and the push remote (T321).
- `[ticket]`: no change (it never binds by request).
- Any binding from thinking blocks, tool_use input, tool results, sidechain (sub-agent) entries, or an assistant message older than the one directly before the request.

**Depends on**: None

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor under `[admin]`, RULE: `docs/claude-md/tracks.md` `### Admin tag` — the Supervisor gives the Requirement Fidelity Gate itself)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (request, session tag, merge gate, auto verify)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `_answered_task` called from `admin_refusal`'s `bound` expression in `.claude/hooks/pre_bash_block_unsafe_merge.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | New helper `_answered_task(transcript_path, request_entry, id_regex)` (in the gate or `lib/auto_mode.py`) returns the one task ID, or None. The gate's `bound` (per-request and session `[admin]`, never `[ticket]`) becomes true also when `_answered_task(...) == task_id` | yes [admin] binds the asked task |
| 2 | The request qualifies only when its text, after removing code spans, `>` quoted lines and the tag (`[admin]`), is a short yes matched in full, case-insensitive, by `^\s*(yes|y|ok|okay|sure|go( ahead)?|do it|merge( it)?)\W*$` (≤ 40 chars). Any other word, a second sentence, a task ID or a negation → None | only a bare yes |
| 3 | The question is the newest `type: "assistant"` transcript entry before the request entry that has at least one `text` block, not `isSidechain`, with no other user request (`origin.kind == "human"`) between them. Only its `text` blocks are read — never `thinking`, `tool_use` input or tool results | only what the user saw |
| 4 | That text names exactly one task (by `_named_tasks`, so a negated ID drops out; a task branch such as `feat/t322-…` counts as its ID through `_ref_task_id`), and its last non-empty line or sentence ends with `?`. Zero or ≥ 2 tasks → None | one task, asked |
| 5 | That task equals the command's task, and every other check still runs unchanged: one task per command, `committed_verify_row(..., hook_only=True)`, repo allowlist, push target, `main` push rules. Under a session tag the row must also be in Ready for Review for the merge/branch push (as the loop path requires) | nothing else loosened |
| 6 | Any exception or unreadable transcript → None (fail closed); the refusal text adds one hint: "a bare yes binds only when the Supervisor's last message asked about exactly one task; else reply with the task ID and `[admin]`" | fail closed, clear hint |
| 7 | Doctrine: `docs/claude-md/tracks.md` `### Admin tag` item 3 and `### Session tags` "The merge gate" bullet name the fourth binding in one or two sentences, and add: when the Supervisor asks to merge, it names exactly one task and asks for `merge <ID> [admin]` or a yes | doctrine fallback |
| 8 | Tests (written first, by `qa-expert`, locked) cover: the T322 transcript shape binds; yes with extra words; two IDs in the question; a negated ID; ID only in thinking; ID only in tool_use input; sidechain assistant entry; a human request between question and yes; question not ending in `?`; question naming T1 while the command merges T2; `[ticket]` unchanged; row not in Ready for Review under a session tag; malformed transcript → refusal | Gate 5 |
| 9 | Under a session `[admin]` tag, the answered-question check (only this check) reads the latest human request (`auto_mode.latest_request`), which may carry no tag, dated at or after the session tag request; the tag and every other binding (`_named_tasks`, `_guides_added_since`, `_own_start_since`, `_session_admin_merges`) keep reading the tag request's `(when, text)`. An untagged yes binds under session `[admin]`; never under `[ticket]`; never after `[stop]`; with an older tagged request followed by an untagged yes, only the question directly before the yes is read | Debate 2 (tracks.md:879 "hold for the whole session") |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t323_answered_question.py`. The implementer may not edit it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Synthetic transcript: assistant text "Do you want me to merge `feat/t322-x` into `main`?", then human "yes [admin]"; branch with a committed hook pass | `git merge feat/t322-x` allowed | oracle test |
| 2 | Each negative shape in AC 8 | refused, reason names the task | oracle test |
| 3 | Existing admin/session tests | unchanged, green | `python3 -m pytest .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_t317_*.py -q` |
| 4 | Full suites | no regression | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T323.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T323.md`.

---

## Approach

**Pattern reference**: `_named_tasks` / `_own_start_since` in `.claude/hooks/pre_bash_block_unsafe_merge.py` (2233–2330); `auto_mode.latest_request` / `request_text` (`.claude/hooks/lib/auto_mode.py` 99–160) for the transcript walk; `lib/session_work.py:141` for reading assistant entries.
**Vital slice**: one helper, one `or` in `bound`, one hint in the refusal, two doctrine sentences, the oracle.
**Cut list**: no free-form NLP of the reply; no reading older assistant messages; no change to `--start`; no site page text (T322's paragraph already says the request binds a task).

Risk: High. The gate decides what may reach `main`. Every doubt must fail closed. The model's text may only narrow consent to one shown task, never widen or supply the tag.

---

## Edge Case Checklist

- [ ] The question names the task only as a branch path, not an ID
- [ ] Unicode / trailing punctuation in the yes ("yes!", "Yes.")
- [ ] The assistant entry is split into several entries (one per content block): use the newest entry with a `text` block, and stop at any human request
- [ ] Compact summary (`isCompactSummary`) between question and reply → None
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep `docs/claude-md/`, `site/`, `README`, `AGENTS.md` for "binds the task in one of three ways" and update the count

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_answered_task`, one `or` in `bound`, refusal hint |
| `.claude/hooks/lib/auto_mode.py` | only if the helper or a transcript reader lives there |
| `docs/claude-md/tracks.md` | `### Admin tag` item 3, `### Session tags` merge-gate bullet |
| `.claude/hooks/tests/test_t323_answered_question.py` | new, `qa-expert`, locked |
| Pre-existing pin tests | List each test that pins the refusal text or "three ways" wording, and its handling. **Filled by the implementer:** |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/stop_auto_verify.py` | out of scope (T203 rule) |
| `.claude/settings.json` | permissions |
| `memory/MEMORY.md` | Supervisor-only |

---

## Test Plan

`qa-expert` writes the oracle first (red). The implementer makes it green and runs the full suites. The Supervisor runs `code-review` and `security-review` (Risk High), then the auto verify run.

---

## Questions Log

- 2026-11-16 DEBATE how should a "yes [admin]" reply bind the task the Supervisor asked about → strict gate path "answered question" + doctrine fallback (Advocate 1: doctrine only, ask for the ID; Advocate 2: gate path 4 with bare-yes list, text blocks only, exactly one ID, Ready for Review, plus doctrine; Advocate 3: same gate path with a full-match yes regex, plus doctrine) — RULE: necessary per `PROJECT_KANBAN.md:11` (reports/question_T323_20261116T112957.html) ⚠ decided for you — please review
- 2026-11-16 DEBATE under a session `[admin]` tag, does an untagged "yes" answer the Supervisor's merge question? → yes: the answered-question check reads the latest human request; tag and other bindings keep the tag request (Advocate 1: read latest request, narrow, separate argument; Advocate 2: read latest request, tag from session_request; Advocate 3: same, plus 4 oracle cases) — all three agree; RULE: docs/claude-md/tracks.md:879 "`[ticket]` and `[admin]` hold for the whole session"

---

## Completion Checklist

- [ ] Oracle written by `qa-expert`, red
- [ ] Pin-test row filled before work starts
- [ ] Implementation done
- [ ] `code-review` run
- [ ] `security-review` run (Risk High)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T323.md` (Hard-Stop Gate 5)
- [ ] Supervisor notified: ready for Stage 4
