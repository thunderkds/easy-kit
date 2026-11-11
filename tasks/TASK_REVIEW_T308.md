# TASK_REVIEW — T308: the merge gate accepts the user's own `/verify <ID>` for an extended-track task

> Sibling of `tasks/TASK_GUIDE_T308.md`. Everything here is **filled by the reviewer at Stage
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

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t308_user_verify_extended.py` (locked oracle by qa-expert, commit c2c1252; not edited). At HEAD `c34f2a2`, 2026-11-11T14:37:20Z: `python -m pytest .claude/hooks/tests/test_t308_user_verify_extended.py -q -p no:cacheprovider` → `36 passed in 9.26s` (was `9 failed, 27 passed` at BEFORE). |
| Verification command run | ☑ pass | Oracle as above: `36 passed in 9.26s`. Pin tests (pre-flight list in the guide) at HEAD `c34f2a2`: `test_merge_gate_guard.py`, `test_stop_auto_mode_check.py::test_merge_gate_is_untouched`, `tests/test_auto_mode.py::test_ac4_merge_gate_file_is_unchanged`, the oracle, `test_t250_session_ownership.py`, `test_admin_tag.py`, `test_verify_row_fill_detection.py`, `test_merge_gate_t095.py`, `test_merge_gate_t210.py`, `test_guide_sections.py`, `tests/test_auto_mode.py`, `tests/test_t306_admin_retry_blocked.py`, `tests/test_stage_names.py`, `tests/test_auto_verify.py`, `test_agent_guide_dedup.py` → `1017 passed in 129.21s`. One pin repointed: `test_merge_gate_guard.py::test_the_allowlist_names_the_tasks_that_own_rules_in_the_gate` now expects `"T308"` at the end of `AUTHORISED_TASKS` (the file's documented record for a task that changes the gate); no assertion weakened. |
| Negative cases hold | ☑ pass | Oracle AC 3 (no transcript, short hash, other code, entry before the code, entry after the row's commit — review file and inline guide, other task ID, no human origin, four non-`USER_LINE` Notes shapes) and AC 4 (unwritten row, user-shaped row with no proof, hook row with no record, minimal track unchanged) all block with `T900 (no evidence row)`; the oracle's own time-blind mutation turns green only with the bound. Extra mutation (implementer): `report_rel=_evidence_rel(...)` and `report_rel=row_rel` replaced by `report_rel=MINIMAL_LOG_REL`; `git diff --stat` → `.claude/hooks/pre_bash_block_unsafe_merge.py | 93 ++++++++++++++++++++++++----` (non-empty) → oracle `9 failed, 27 passed`; restored → `36 passed in 5.29s`. |
| verify | ☑ pass | auto-run by hook, session 99b79120-0df5-466c-a6f6-f1a31679e200, commit bf82cca783a81ccabdffb41d1c36c9ed8762f10b, log .claude/verify-runs/T308-bf82cca783a8.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Affected set: `.claude/hooks/pre_bash_block_unsafe_merge.py` (`has_filled_verify_row`, `verify_row_passes`, `user_line_confirmed`, `committed_verify_row`, new `_evidence_rel`, `_user_row_passes`), their callers (`main`, the `[admin]` path with `hook_only`), `merge_gate_guard.py` and its test (the gate-owner allowlist), `docs/claude-md/tracks.md` (`### Auto verify (Stop hook)`, `### Final report`, `### Known limits`), `templates/TASK_REVIEW_template.md`. Untouched, confirmed by `git diff fbdbd62 HEAD`: `verify_record.py`, `.claude/settings.json`, `### Admin tag`, the locked oracle since `c2c1252`. Not reviewed: the minimal-track code path beyond the default `report_rel` (unchanged, pinned by the oracle's AC 4 cases) |
| Full smoke suite still green (no regression) | ☑ pass | 2026-11-11T14:37:16Z, HEAD `c34f2a2`: `python -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` → `2 failed, 7037 passed, 6 skipped, 25 subtests passed in 411.17s (0:06:51)`. The 2 failures are the known busybox cases: `test_heredoc_quoted_marker.py::test_round4_premise_the_shell_runs_the_push_and_the_scanner_keeps_it[d-busybox-ash-bash]` and `[d-busybox-ash-zsh]`. (The first run, before the commit, also failed the 3 gate-owner guard tests because the gate change was uncommitted and T308 was not on the allowlist; fixed by the commit and the allowlist entry.) |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured 2026-11-11T14:23:39Z by common-infrastructure in `/home/thunderkds/workspace/pets/wt-t308`,
HEAD `c997e09564fcd094b1f16de6843d19ab239dabd7` (the locked oracle, no implementation commit yet):

```
$ python -m pytest .claude/hooks/tests/test_t308_user_verify_extended.py -q -p no:cacheprovider
...
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac1_the_users_verify_row_with_the_transcript_entry_passes[working-tree-read]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac1_the_users_verify_row_with_the_transcript_entry_passes[own-branch]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac2_a_row_in_the_guides_inline_evidence_passes[working-tree-read]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac2_a_row_in_the_guides_inline_evidence_passes[own-branch]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac1_a_row_committed_only_in_the_tasks_worktree_passes
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_ac1_the_named_session_may_be_another_file_in_the_same_folder
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_mutation_a_time_blind_copy_lets_an_out_of_window_entry_through[before-code-working-tree]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_mutation_a_time_blind_copy_lets_an_out_of_window_entry_through[after-row-working-tree]
FAILED .claude/hooks/tests/test_t308_user_verify_extended.py::test_mutation_a_time_blind_copy_lets_an_out_of_window_entry_through[before-code-own-branch]
9 failed, 27 passed in 7.20s
```

Each AC 1/AC 2 failure is the gate's block `Tasks in Ready for Review missing Stage 5 verify evidence ... T900 (no evidence row)`
for a `| verify | ☑ pass | /verify by the user, session <sid>, commit <sha> |` row with a valid transcript entry.

**AFTER**: 2026-11-11T14:37:20Z, HEAD `c34f2a2a1c3ba67b2f5111676a3e50adb1fe55da`:

```
$ python -m pytest .claude/hooks/tests/test_t308_user_verify_extended.py -q -p no:cacheprovider
....................................                                     [100%]
36 passed in 9.26s
```

**DELTA**: On an extended-track task whose auto verify run ended `blocked`, the user can now type `/verify <ID>` and record `| verify | ☑ pass | /verify by the user, session <id>, commit <sha> |`. The merge gate accepts that row with the same transcript proof as the minimal track.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

## Stage 4 review (2026-11-11, Supervisor)

- `code-review`: scope is `git diff fbdbd62...HEAD` (8 files). P0 0, P1 0, P2 2, P3 2. `lane_check`: `C2, 7 files, 608 lines, EXCEEDS (lines 608 > 500); unpredicted: .claude/hooks/tests/merge_gate_guard.py, .claude/hooks/tests/test_merge_gate_guard.py, tasks/TASK_GUIDE_T308.md`. 318 of the 608 lines are the locked oracle; the two guard files are the gate-owner allowlist (P3, below). The oracle is unchanged since `c2c1252`. Pin and gate tests run by the Supervisor: `861 passed in 148.60s` (`test_t308_user_verify_extended.py`, `test_merge_gate_guard.py`, `test_merge_gate_t095.py`, `test_verify_row_fill_detection.py`, `test_t250_session_ownership.py`, `test_admin_tag.py`, `tests/test_auto_verify.py`, `test_auto_mode.py`, `test_stage_names.py`, `test_t306_admin_retry_blocked.py`). The implementer's full suite: `2 failed, 7037 passed` (the 2 busybox cases). Startup-reads line holds `PROJECT_SPEC.md`, the guide and `agents/common-infrastructure.md`.
  - P2: `PROJECT_SPEC.md:102` (glossary "Auto verify") still says the gate accepts "either an `auto-run by hook` row or a minimal-track `verify:` line only with a record". Stale since T250; outside the guide's file list. Goes to T309.
  - P2: the `verify` row placeholder in `templates/TASK_REVIEW_template.md` says Notes "must literally state pass", which reads as a conflict with the user-row shape (Notes exactly `/verify by the user, …`). AC 6 forbids other template edits. Goes to T309.
  - P3: `merge_gate_guard.py` `AUTHORISED_TASKS` gets `T308`; the file's own rule says the Supervisor signs the line off, and the spawn prompt did not name that file. Reported to the user for sign-off at merge.
  - P3: lane `EXCEEDS` (oracle lines).
- `security-review` (High risk, a merge gate; done on the branch diff): no finding at confidence 8 or higher. The user row counts only when all hold: the Check cell is exactly `verify`, Result holds a checked `☑ pass` and no `☐ pass`, Notes (stripped) equal `USER_LINE`, and `user_line_confirmed` proves it (human `/verify <ID>` in the named session's transcript, dated after `<sha>` and before the row's commit, `<sha>` the same code as the head with only the report file allowed to differ). An empty `report_rel` or a missing section returns False. `hook_only` (`[admin]`) never reaches the user path: item 4 of `### Admin tag` holds. The time bound reads the file the row came from (mutation: both new `report_rel` arguments set back to `MINIMAL_LOG_REL` turns 9 oracle tests red). Residual, restated, not widened: (1) the gate shows only that the user typed `/verify <ID>`, not its verdict; (2) a forged transcript is still the limit `### Known limits` names (agents cannot write transcripts: T251); (3) the older hole, a hand-typed row with the word "pass" in Notes passing the old path, is not changed and is T309. A `USER_LINE` row whose session id contains "pass" passes through that old path with no proof, which T309 closes.
