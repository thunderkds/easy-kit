# TASK_REVIEW — T324: a test run in a task's worktree is not work on the task (Stop check false positive)

> Sibling of `tasks/TASK_GUIDE_T324.md`. Filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. A test run is not work only for the Stop hook: `session_work.worked_on`/`work_start` get a `test_runs_count` keyword (default `True`), and only `stop_auto_mode_check.py` passes `False`; the merge gate keeps today's meaning — DEBATED: option D (Advocate 1: D, the keyword for `worked_on` and `work_start`, both Stop-hook readers pass it; Advocate 2: D, the keyword for `worked_on` only, `work_start` unchanged; Advocate 3: A, a test run is not work for every caller, flipping `test_t250_session_ownership.py:141`, `:146`). Picked by FACT: `.claude/hooks/pre_bash_block_unsafe_merge.py:1290` "this session worked on it (`session_work.worked_on`: an edit, a writing `Bash` command or a spawn" — option A changes that user-approved T250 G2 merge-gate meaning (`.claude/hooks/tests/merge_gate_guard.py` T250 "User-approved, 2026-11-04"), which `[admin]` may not do without the user ⚠ decided for you — please review Re-run 2026-11-16 in session 4e7ced6b (3 new Advocates, `Advocate 1-3: T324 test-run rule`): all three pick D again (A loosens the user-approved T250 G2 meaning, `merge_gate_guard.py:61-64`; D' splits `worked_on`/`work_start`, `session_work.py:396`); shared weakest point: default True means a new caller silently counts test runs, and the merge gate keeps the safe-side false positive.
2. `work_start` takes the same keyword, and `session_window` passes it too — RULE: `.claude/hooks/lib/session_work.py:362` "changed the task has a readable date. Same test as `worked_on`, so the two never disagree."
3. The bugfix mental model is signed `auto (Supervisor)` instead of by the user — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13)
4. The false `Paused: auto-mode check failed` line the old hook wrote into `../wt-t321/tasks/TASK_REVIEW_T321.md` is not removed by T324: it is another session's file — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task")
Paused: a safety block — the Claude Code auto-mode classifier denied the implementer's edit of `.claude/hooks/tests/test_debate_window.py` (stub `work_start(_entries, _task_id, _worktrees)` → add `**_kw`), so `test_p3_1_a_window_reader_that_raises_keeps_the_whole_session_rule` fails (`Debate window unknown (TypeError)`, expects `(RuntimeError)`); the Supervisor does not repeat a denied action — waiting for the user
Checks: tests — locked oracle `python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q` at `8fa4b824`: 149 passed (red at `ffdbdd04`: 75 failed, 74 passed); full suite: 6 failed, 7636 passed — 1 is the stub above, 5 are `memory/MEMORY.md` over its char budget on `main` (42,050 / 42,000, not T324); security-review on `ffdbdd04..8fa4b824` (session_work.py, stop_auto_mode_check.py) — no findings; not new: backticks and `>(…)`/`<(…)` hide a write behind a test-run head, the same class `echo`/`cat` already had (hardening follow-up); code-review not run yet (auto-checked, not /verify)
Memory: pending
Not done: merge (admin: after the auto verify pass); auto verify: not started
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report 4063e1e5fb86]

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

**BEFORE**: captured by qa-expert at 2026-11-16T04:04:36Z (UTC) on commit
`bb41db536c9279db03bb95bd6ee427a20dd7311b` (branch `fix/t324-test-run-not-work`, no implementation
commit yet), in `/home/hungnguyenhuu/workspace/pets/wt-t324`.

Phase 1 repro (`session_work.worked_on` today; a script loads `.claude/hooks/lib/session_work.py` of
this worktree and passes the incident command, cwd = main checkout, worktree `../wt-t321`):

```
incident test run -> True
grep of the review -> False
```

Locked oracle, red on the unchanged code:

```
$ python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q -p no:cacheprovider
75 failed, 74 passed in 1.54s
```

Red causes: AC 1/2/4 `TypeError: worked_on() got an unexpected keyword argument 'test_runs_count'`
(72 tests); AC 5 the incident stop is blocked (`T900: Risk High, but no decision was DEBATED with 3
Advocates`, no test run in the trace, no `code-review`, no `security-review`, no `Memory:` line); AC 6
the spy sees `worked_on` called with no keyword (`('worked_on', [{}])`), and the Debate window opens at
the test run, so the `before the task's first change` hint is missing.

**AFTER**: captured by common-infrastructure at 2026-11-16T04:11:03Z (UTC) in
`/home/hungnguyenhuu/workspace/pets/wt-t324`, with the fix applied on top of `ffdbdd04` (working tree,
before its commit). Same Phase 1 repro (incident command, cwd = main checkout, worktree `../wt-t321`):

```
incident test run (default) -> True
incident test run (test_runs_count=False) -> False
grep of the review -> False
```

Locked oracle, green:

```
$ python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q -p no:cacheprovider
149 passed in 1.28s
```

`git diff main -- .claude/hooks/pre_bash_block_unsafe_merge.py | wc -l` → `0` (merge gate unchanged).

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
