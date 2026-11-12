# TASK_REVIEW — T309: the ordinary merge gate stops accepting a hand-typed `☑ pass` verify row with no proof

> Sibling of `tasks/TASK_GUIDE_T309.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t309_hand_typed_pass_row.py` (oracle by `qa-expert`, 43 tests); `hook_verify_row.py` helper; pins repointed in `test_verify_row_fill_detection.py`, `test_merge_gate_t095.py` and 10 more files (AC 5)
| Verification command run | ☑ pass | 2026-11-12T03:19:11Z at `afcb3ed`: `pytest .claude/hooks/tests/test_t309_hand_typed_pass_row.py -q` → `43 passed in 9.42s`
| Negative cases hold | ☑ pass | Red run at `eedd717` before any implementation commit: `18 failed, 25 passed` (see Demonstration BEFORE). The oracle's `test_mutation_the_old_any_pass_branch_lets_a_hand_typed_row_through` (2 cases) puts the old branch back and shows the hand-typed row passes
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Scope: `pre_bash_block_unsafe_merge.py` (`verify_row_passes`, `_verify_row_passes`, callers `has_filled_verify_row` and `committed_verify_row`), 14 repointed test files, glossary, `skills/bugfix/SKILL.md`, review template. Skipped: `[admin]` push-scope code and `verify_record.py` (not touched). Lane check: C2, 21 files, 1017 lines, EXCEEDS (files 21 > 14; lines 1017 > 500), all unpredicted files are fixture fallout or the AC 4 docs
| Full smoke suite still green (no regression) | ☑ pass | 2026-11-12, worktree at `afcb3ed`: `pytest .claude/hooks/tests tests -q` → `2 failed, 7170 passed, 6 skipped`. The 2 failures, `test_heredoc_quoted_marker.py::test_round4_premise_the_shell_runs_the_push_and_the_scanner_keeps_it[d-busybox-ash-bash|zsh]`, fail the same way on `main` (checked: `2 failed, 814 passed` in that file alone): no busybox `ash` on this machine, not T309
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier was not run for this task
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component (hook, tests and docs only)
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI component (hook, tests and docs only)
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI component (hook, tests and docs only)

---

## Stage 4 results

- `code-review` (2026-11-12): P0 0, P1 0, P2 1, P3 1. Entry-point check: `verify_row_passes` is reached from `has_filled_verify_row` and `committed_verify_row`, both found. Stale-reference sweep: `tracks.md:658` and the `Known limits` item at `tracks.md:935` already say a hand-typed row does not count; the glossary row, `skills/bugfix/SKILL.md` and the template placeholder are fixed in this task.
  - P2 (process): lane check EXCEEDS (21 files > 14, 1017 lines > 500). The extra files are the fixture fallout of AC 5 that the guide lists, so the label C2 stands; raised to the Supervisor.
  - P3 (`pre_bash_block_unsafe_merge.py:544`, `:560`): `_verify_row_passes` keeps its `hook_only` parameter, which no line in it reads now, and `AUTO_ROW_TAG in notes and` is redundant after the new `continue`. Left alone: removing them touches the T284 signature that `committed_verify_row` and the tests pass through (Surgical Changes).
- Rows that would now fail: none. The board has no other task at Ready for Review, and a Done task is not read by the gate.
- `security-review` (2026-11-12): no findings at confidence 8 or above. The change only narrows what the gate accepts. Residual: an agent that forges the transcript or the run record, as `### Known limits` already records.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured 2026-11-11T15:49:09Z at `eedd717` (oracle locked, no implementation commit yet),
by common-infrastructure in `/home/thunderkds/workspace/pets/wt-t309`:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ && git rev-parse --short HEAD && python -m pytest .claude/hooks/tests/test_t309_hand_typed_pass_row.py -q -p no:cacheprovider | tail -25
2026-11-11T15:49:09Z
eedd717
E       AssertionError: the real gate must block a hand-typed row: None
E       assert False
E        +  where False = blocked(None)

.claude/hooks/tests/test_t309_hand_typed_pass_row.py:354: AssertionError
=========================== short test summary info ============================
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[ran-verify-myself-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[ran-verify-myself-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[confirmed-working-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[confirmed-working-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[user-shape-sid-pass-1-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[user-shape-sid-pass-1-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[pass-slash-na-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_review_file_blocks[pass-slash-na-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_without_a_transcript_blocks[working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_without_a_transcript_blocks[own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_guides_inline_evidence_blocks[ran-verify-myself-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_guides_inline_evidence_blocks[ran-verify-myself-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_guides_inline_evidence_blocks[confirmed-working-working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_pass_row_in_the_guides_inline_evidence_blocks[confirmed-working-own-branch]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_hand_typed_row_committed_only_in_the_tasks_worktree_blocks
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_ac1_a_user_shaped_row_with_a_transcript_for_another_session_blocks
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_mutation_the_old_any_pass_branch_lets_a_hand_typed_row_through[working-tree-read]
FAILED .claude/hooks/tests/test_t309_hand_typed_pass_row.py::test_mutation_the_old_any_pass_branch_lets_a_hand_typed_row_through[own-branch]
18 failed, 25 passed in 5.52s
```

The gate returns `None` (allows the merge) for every hand-typed `☑ pass` row with "pass" in Notes.

**AFTER**: captured 2026-11-12T03:19:11Z at `afcb3ed`, same command:

```
$ pytest .claude/hooks/tests/test_t309_hand_typed_pass_row.py -q -p no:cacheprovider
...........................................                              [100%]
43 passed in 9.42s
```

**DELTA**: A `☑ pass` verify row typed by hand no longer opens the merge gate; only the hook's row with its run record, or your own proven `/verify` line, does.

**WITNESS**: Supervisor session 5f36b464, 2026-11-12, re-ran the oracle and the full suite in `/home/thunderkds/workspace/pets/wt-t309` (BEFORE capture by `common-infrastructure`, 2026-11-11).
