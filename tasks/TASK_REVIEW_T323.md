# TASK_REVIEW — T323: a short yes [admin] binds the asked task

> Sibling of `tasks/TASK_GUIDE_T323.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` or `[admin]` tag; with `[admin]`, the `Not done:` line names `merge (admin: after the auto verify pass)`,
`docs/claude-md/tracks.md` `## Auto mode`). To use it, copy the block below out of this comment, to this
place, and replace every <...>. Keep `Mode: auto` as its first line, exactly as written: T182's hook reads
it. Write it to this file before the run ends; the chat message is a copy, not the report. The same
block is the Supervisor's final chat message. It is not the `delivery-report` page and not
Evidence. A taste decision (what the user wants) also ends with the flag. Write `DEBATED` only when ≥2
Advocate `Agent` calls ran for that question, naming each Advocate's option. A decision with no Advocates is
labelled `RULE`, `FACT` or `SAFER OPTION`, never `DEBATED`. A decision flagged `⚠ decided for you` is a choice, and is never labelled `FACT`. A
safety action a rule requires (for example the backup before a delete) is `RULE` without the flag.
At Risk Medium or High, a `RULE:` counts only when it names a written rule (`path:line`,
`path § <heading>`, or `docs/claude-md/tracks.md` `### <section>`), and a `FACT:` needs a Citation
(`path:line "quoted text"`); without one it is a choice and must be `DEBATED`. Good: `2. backed up the CSV
— RULE: `docs/claude-md/tracks.md` `### Stops that stay``. Bad: `1. kept recurring.csv — RULE: Surgical Changes`.
`Memory:` records the diff-driven memory pass you run before you stop: each entry written, or `nothing new`.
After an auto verify pass the hook, never you, adds `Closed: row moved to Done <date> — …` and moves the row,
or adds `Paused: done not moved — <reason>`. It moves the row only when this block holds `Mode: auto`, a
numbered decision, `Checks:`, `Memory:`, the `Not done:` auto verify slot with its result, and `Not done:`
naming the merge — no `<...>` left (`docs/claude-md/tracks.md` `### Auto close-out`).
With `/verify (yours)`, your pass goes in the `verify` row below: Result `☑ pass`, Notes `/verify by the user, session <id>, commit <sha>`.

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. a short yes to the Supervisor's own one-task question binds that task (strict gate path) plus the doctrine fallback — RULE: PROJECT_KANBAN.md:11 "bind the task the Supervisor's immediately preceding question named" (Decide rule 1, necessary: doctrine alone leaves "yes [admin]" refused; 3 Advocates were heard before the first change, see the guide's Questions Log and reports/question_T323_20261116T112957.html)
2. under a session `[admin]`, an untagged yes is read from the latest human request for this check only — DEBATED: read the latest request (Advocate 1: separate `latest` argument, tag request kept for other bindings; Advocate 2: same, tag from `session_request`; Advocate 3: same, plus 4 oracle cases) — all three agree; docs/claude-md/tracks.md:879 "`[ticket]` and `[admin]` hold for the whole session"
Checks: tests `python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q` — 65 passed (red 53/12 before); admin+session `test_admin_tag.py test_t317_*.py` — 401 passed; full suite at 912a07c2 — 7555 passed, 7 failed (2 guard pins fixed in 33630738, 5 MEMORY.md budget fixed in f0f34f2f; budget tests 18 passed); reviews code-review — P0 0/P1 0/P2 1/P3 0, security-review — no findings ≥ 8 (auto-checked, not /verify)
Memory: memory/decisions.md — 2026-11-16 T323 answered-question binding; memory/MEMORY.md — back under 42,000 chars (83ae08a8)
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass (session 1421f695-e984-4356-8bf2-292e69fb24ec, commit 30a851bf7d0ed4bf1fcb1205a04d2c8f822d997a, log .claude/verify-runs/T323-30a851bf7d0e.log); follow-up T325 (P2: the question need not be about merging)
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report 009a40b61469]
Closed: row moved to Done 2026-11-16 — auto verify pass (session 1421f695-e984-4356-8bf2-292e69fb24ec, commit 30a851bf7d0ed4bf1fcb1205a04d2c8f822d997a); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | Locked oracle `.claude/hooks/tests/test_t323_answered_question.py` (qa-expert, written first). Red run before any implementation, 2026-11-16T04:33Z, at `1d68ba33`: `python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q -p no:cacheprovider` → `50 failed, 10 passed in 3.47s` (AC 1-8 cases). Every failure is the binding refusal `T900 is not the task of the `[admin]` request: ...`: 17 positive cases (T322 shape, push, by-ID, each short yes, split entries, per-request path) are refused instead of allowed; 32 negative cases are refused but lack the AC 6 hint; `test_ac5_the_answered_task_still_needs_its_committed_auto_verify` is refused by the binding instead of the verify-row check. The 10 passing are guards that must stay green: octopus merge, force push, `[ticket]` x2, unreadable transcript x4, request naming the ID binds, `[ticket]` naming the ID does not. AC 9 cases added (coordinator, after Debate 2), red run 2026-11-16T04:37:40Z: same command → `53 failed, 12 passed in 4.88s`. The new failures are refused by the binding: an untagged yes under session `[admin]` and the T900 merge in `test_ac9_only_the_question_directly_before_the_latest_yes_binds` should be allowed; `test_ac9_a_yes_typed_before_the_tag_request_does_not_bind` is refused but lacks the hint. 2 new guards already pass: `[ticket]` + untagged yes stays refused, and after `[stop]` no `[admin]` path applies (the gate answers like the never-tagged control). Green run (implementer, common-infrastructure, after the change, oracle unedited), 2026-11-16T04:42:06Z: same command → `65 passed in 3.16s`. Reviewer ticks after re-running. |
| Verification command run | ☑ pass | Implementer run, worktree `/home/hungnguyenhuu/workspace/pets/wt-t323`, 2026-11-16T04:42:06Z: `python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q -p no:cacheprovider` → `65 passed in 3.16s`; `python3 -m pytest .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_t317_*.py -q` → `401 passed in 16.05s`. |
| Negative cases hold | ☑ pass | oracle red at 1d68ba33: 53 failed, 12 passed (refusal "T900 is not the task of the `[admin]` request…"); green at 912a07c2: 65 passed; the 12 guards (force push, octopus merge, `[ticket]`, unreadable transcript, `[stop]`) stayed green throughout |
| verify | ☑ pass | auto-run by hook, session 1421f695-e984-4356-8bf2-292e69fb24ec, commit 30a851bf7d0ed4bf1fcb1205a04d2c8f822d997a, log .claude/verify-runs/T323-30a851bf7d0e.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff main...HEAD`: the gate (`_short_yes`, `_answered_task`, `answered()` in `admin_refusal`), `lib/auto_mode.py` callers, tracks.md `### Admin tag`/`### Session tags`, `merge_gate_guard.py` allowlist. security-review rescoped from all of local `main` (69 commits) to this diff |
| Full smoke suite still green (no regression) | ☑ pass | Implementer run at `912a07c2`, finished 2026-11-16T04:58:18Z: `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider -rf` → `7 failed, 7555 passed, 5 skipped, 87 subtests passed in 404.05s`. 5 are pre-existing on main `1d68ba33` (same 5 fail there: `memory/MEMORY.md` over its hot-tier char budget, 42,207 / 42,000; Supervisor-only file): `test_memory_channel_and_budget.py::test_live_memory_md_is_within_budget_today`, `::test_ac10_growth_in_chars_without_growth_in_lines_turns_the_gate_red`, `::test_ac11_many_short_lines_past_200_stay_green_while_under_budget`, `::test_ac3_per_entry_report_is_advisory_and_never_fails`, `test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget`. 2 come from this task and wait for the Supervisor's sign-off: `test_stop_auto_mode_check.py::test_merge_gate_is_untouched` and `tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged` (T323 is not in `merge_gate_guard.AUTHORISED_TASKS`; the implementer did not add itself). Resolved after the Supervisor's sign-off (session `[admin]`, 2026-11-16) at `33630738` "T323: authorise T323 in merge_gate_guard (Supervisor sign-off)", 2026-11-16T04:59:29Z: `python3 -m pytest .claude/hooks/tests/test_stop_auto_mode_check.py::test_merge_gate_is_untouched tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider` → `28 passed in 0.55s`; oracle `python3 -m pytest .claude/hooks/tests/test_t323_answered_question.py -q -p no:cacheprovider` → `65 passed in 3.91s`. Left: the 5 pre-existing MEMORY.md budget failures (Supervisor). |
| **Companion score (easy-verifier)** | ☑ N/A | not run: optional tool; code-review and security-review ran |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: hook and doctrine only |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI: hook and doctrine only |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI: hook and doctrine only |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: qa-expert, worktree `/home/hungnguyenhuu/workspace/pets/wt-t323` at `1d68ba33` (no implementation commit yet), the locked oracle's T322-shape cases run against the current gate:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-11-16T04:33:38Z
$ python3 -m pytest ".claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_the_merge_under_the_admin_tag" ".claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_on_the_per_request_admin_path" -q -p no:cacheprovider --tb=line
.../test_t323_answered_question.py:104: AssertionError: assert 'T900 is not the task of the `[admin]` request: the request does not name it, and it is not the one task whose guide was first added after the request' is None
FAILED .claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_the_merge_under_the_admin_tag
FAILED .claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_on_the_per_request_admin_path
2 failed in 0.15s
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-11-16T04:33:43Z
$ python3 -m pytest "...::test_sc1_the_t322_shape_binds_the_merge_under_the_admin_tag" -q -p no:cacheprovider -vv --tb=short   (the hook's block reason, session `[admin]` path)
E   assert "[hook:pre_bash] Auto-mode gate — cannot push/merge:\n  • `[admin]` does not allow this command: T900 is not the task of the `[admin]` request: the request does not name it, and it is not the one task whose guide was first added after the request, nor the task of this session's loop (its row in Ready for Review, changed by this session since the tag request, its only task In Progress or Ready for Review, its auto verify started by this session's own `python3 .claude/hooks/stop_auto_verify.py --start <ID>` call after the request, and the pass recorded after that call)\nWith `[auto]`, merge and push stay the user's. ...
```

Transcript of that case: assistant text "Do you want me to merge `feat/t900-x` into `main`?", then human (`origin.kind: "human"`) "yes [admin]"; `feat/t900-x` commits a hook-written pass row with its run record; T900 in Ready for Review. Today the gate refuses `git merge feat/t900-x` — the user's T322 refusal, reproduced.

**AFTER**: common-infrastructure (implementer), same worktree, after the change in `.claude/hooks/pre_bash_block_unsafe_merge.py` (`_answered_task`, one `or answered()` in `bound`, the AC 6 hint):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-11-16T04:47:35Z
$ python3 -m pytest ".claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_the_merge_under_the_admin_tag" ".claude/hooks/tests/test_t323_answered_question.py::test_sc1_the_t322_shape_binds_on_the_per_request_admin_path" -q -p no:cacheprovider --tb=line
..                                                                       [100%]
2 passed in 0.24s
```

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

## Stage 4 — code-review (Supervisor, 2026-11-16)

lane: C2, 6 files, 487 lines, FITS; unpredicted: merge_gate_guard.py + test_merge_gate_guard.py (allowlist, Supervisor sign-off under session `[admin]`), TASK_GUIDE_T323.md (pin row)

| Sev | File | Finding | Conf | Outcome |
|---|---|---|---|---|
| P2 | .claude/hooks/pre_bash_block_unsafe_merge.py `_answered_task` | the bound question need not be about merging: "T900 passed verify. Should I wait?" + "yes" binds T900 (still needs its committed hook pass; Ready for Review under a session tag) | 75 | suggestion; follow-up T325 (require a merge/push verb in the ID's clause) |

## Stage 4 — security-review (2026-11-16)

Scope: `git diff main...HEAD` of this branch (the built-in first diffed all of local `main`; rescoped). No findings at confidence ≥ 8. Below the bar (4/10): the same "any question binds" point as the P2 above.
