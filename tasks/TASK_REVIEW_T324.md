# TASK_REVIEW — T324: a test run in a task's worktree is not work on the task (Stop check false positive)

> Sibling of `tasks/TASK_GUIDE_T324.md`. Filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. A test run is not work only for the Stop hook: `session_work.worked_on`/`work_start` get a `test_runs_count` keyword (default `True`), and only `stop_auto_mode_check.py` passes `False`; the merge gate keeps today's meaning — DEBATED: option D (Advocate 1: D, the keyword for `worked_on` and `work_start`, both Stop-hook readers pass it; Advocate 2: D, the keyword for `worked_on` only, `work_start` unchanged; Advocate 3: A, a test run is not work for every caller, flipping `test_t250_session_ownership.py:141`, `:146`). Picked by FACT: `.claude/hooks/pre_bash_block_unsafe_merge.py:1290` "this session worked on it (`session_work.worked_on`: an edit, a writing `Bash` command or a spawn" — option A changes that user-approved T250 G2 merge-gate meaning (`.claude/hooks/tests/merge_gate_guard.py` T250 "User-approved, 2026-11-04"), which `[admin]` may not do without the user ⚠ decided for you — please review
2. `work_start` takes the same keyword, and `session_window` passes it too — RULE: `.claude/hooks/lib/session_work.py:362` "changed the task has a readable date. Same test as `worked_on`, so the two never disagree."
3. The bugfix mental model is signed `auto (Supervisor)` instead of by the user — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13)
4. The false `Paused: auto-mode check failed` line the old hook wrote into `../wt-t321/tasks/TASK_REVIEW_T321.md` is not removed by T324: it is another session's file — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task")
Checks: pending
Memory: pending
Not done: merge (admin: after the auto verify pass); auto verify: not started

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |
| Repro loop | ☐ pass / ☐ fail | [command/observation that reproduced the bug before the fix] |
| Regression test | ☐ pass / ☐ fail | [test file path(s) added to lock the fix in] |
| Smoke suite | ☐ pass / ☐ fail | [bug-specific smoke check beyond the full suite row above] |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: [pasted timestamped command output showing the thing absent/failing, captured before the
first implementation commit] OR [verbatim excerpt of the prior content, for non-executable changes]

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
