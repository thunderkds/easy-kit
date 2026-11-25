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

## Review findings

Reviewer: qa-expert (fresh context), commit `8940df7b47f65f96a59a8c91f9c756dda07a4486`, branch `fix/t324-test-run-not-work`, 2026-11-25. Scope (blast radius): `.claude/hooks/lib/session_work.py`, `.claude/hooks/stop_auto_mode_check.py` (`session_owner`, `session_window`), `.claude/hooks/tests/test_debate_window.py`, the oracle; readers checked by grep: `pre_bash_block_unsafe_merge.py` (default `True`, byte-identical), `lib/task_context.py` and `lib/auto_mode.py` (no `worked_on`/`work_start` call).

Method note: the `Skill` tool was not available in this reviewer's tool set, so `code-review` and `security-review` were applied by hand to their criteria (P0-P3, confidence, fail-open/fail-closed, input handling). No `Skill` call is in the trace from this run: the Supervisor must run both Skills in its own session for the `Paused: ... no security-review Skill call` line to clear.

**Verdict: PASS. No P0, P1 or P2 finding.**

| Sev | Finding | Where | Evidence | Action |
|-----|---------|-------|----------|--------|
| P3 | A backtick command substitution after a test-run head hides a write: `pytest -q \`touch f\`` is not work under `test_runs_count=False` (`$(touch f)` is work). Same class as `cat`/`echo` today (`cat \`touch f\`` is False with the default), so not new; already named in `Checks:` | `session_work.py` `_test_run`, `_bash_works` | probe script, scratchpad `probe.py` | follow-up hardening, not a blocker |
| P3 | A file written by pytest options (`--junitxml=<wt>/o.xml`, `--basetemp=x`, `--cache-clear`) is not work under `False`; `--junitxml=<abs path in worktree>` too | `_test_run` | probe: `[False, True]` (False / default) | documented in the code comment (`session_work.py` "the same accepted limit as `python3 -c`") and the guide cut list; accepted |
| P3 | `bash -c 'cd <wt> && pytest -q'`, `eval`, `FOO=1 pytest`, `env pytest`, `timeout -k 5 5 pytest`, `timeout --signal=KILL` stay work: the false positive remains for these forms (fail-safe side). The `bash -c`/`eval` recursion does not pass the keyword on | `_bash_works` line `_bash_works(code, directory, task, depth + 1)` | probe: `True` | matches the cut list (`sh -c`/`eval` stay work) and AC 2 (double `timeout` stays work); accepted |
| P3 | The oracle changed after the lock commit `da67226d`: 3 lines in `8940df7b` (AC 3 pin compares the gate at `git merge-base HEAD main` instead of the `main` tip) and the `test_debate_window.py` stub in `17d722a1`; both commits say "user edit", author `thunderkds` (the repo user). Independence of those two edits cannot be proved from the repo. I re-checked the gate against both: `git diff main HEAD -- .claude/hooks/pre_bash_block_unsafe_merge.py .claude/hooks/tests/merge_gate_guard.py` is empty, and so is the diff from the fork point | `test_t324_test_run_not_work.py:152-158`, `test_debate_window.py:305` | `git diff da67226d HEAD -- <oracle>` shows only the fork-point change | none; the fork-point pin is the stricter-correct reading once `main` moves (it moved by 3 commits) |
| P3 (live) | The unfixed Stop hook on `main` reproduced the bug against this very task while this review ran: running the oracle in `wt-t324` made the main-checkout hook append `Paused: auto-mode check failed — extended track, but the trace has no code-review Skill call` to this file, twice. I removed those hook-written lines (`git checkout`) before the review commit; they are false positives of T324's own bug | `tasks/TASK_REVIEW_T324.md` | `git diff` after the neighbour-suite run | none; a witness for the Demonstration BEFORE |

Negative review of the cut list: it removes no Acceptance Criterion, stage or gate (no error handling or boundary case is cut). Fail direction: every unrecognised form returns "work" (fail-safe for the owner check: the task is checked); an exception in `worked_on`/`work_start` is caught in `session_owner`/`session_window` (`warn ... checked`, whole session counts). No input reaches a shell or the file system: `_test_run` only reads tokens (`re.fullmatch(r"\d+[smhd]?")`, no backtracking risk); `tokens` is never empty (`_segments` drops empty segments), and `words[2:]` after the `timeout` guard cannot be empty (`len(words) < 3` returns False).

Acceptance Criteria:

| # | Status | Evidence |
|---|--------|----------|
| 1 | PASS | `test_t324_test_run_not_work.py` AC 1 tests green; probe: incident command, `python3 -m pytest -q`, `pytest -q`, `py.test`, `python3 -B -m unittest`, `timeout 60 python -m pytest` → `False` with `test_runs_count=False` |
| 2 | PASS | probe, `False`-keyword: `pytest -q; rm x`, `pytest -q \| tee out.txt`, `python3 -m pytest -q >out.txt`, `2>out.txt`, `&>out.txt`, `&& echo done > notes.md`, `; git commit`, `\n git add -A` → `True`; AC 2 oracle tests green |
| 3 | PASS | default keyword: probe second column `True` for every test-run case; `pre_bash_block_unsafe_merge.py` and `merge_gate_guard.py` have an empty `git diff main HEAD`; only two non-test callers pass the keyword (`grep -rnE "worked_on\|work_start\|test_runs_count"`); the other callers (`pre_bash_block_unsafe_merge.py:1421, 2529, 2532`) pass none |
| 4 | PASS | AC 4 oracle tests green; mutation 2 below turns AC 6 window test red |
| 5 | PASS | AC 5 oracle tests green (the incident stop not blocked, "not checked" on stderr, review file byte-identical after two fires; with an `Edit` → blocked); mutation 1 turns it red |
| 6 | PASS | AC 6 oracle tests green (spy and Debate window); mutation 1 turns `test_ac6_both_stop_hook_readers_pass_test_runs_count_false` red |

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t324_test_run_not_work.py` (149 tests, AC 1-6); `.claude/hooks/tests/test_debate_window.py` (stub takes `**_kw`) |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q -p no:cacheprovider` → `149 passed in 1.01s` (2026-11-25). Neighbours: `python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py .claude/hooks/tests/test_stop_attribution_t287.py .claude/hooks/tests/test_t250_session_ownership.py .claude/hooks/tests/test_t252_marked_ownership.py .claude/hooks/tests/test_debate_window.py -q -p no:cacheprovider` → `432 passed in 41.77s` |
| Negative cases hold | ☑ pass | Mutations, each reverted with `git checkout --` (diff non-empty before each run): (1) `stop_auto_mode_check.py` `test_runs_count=False` → `True` on `session_owner`: `2 failed, 147 passed` (AC 5 incident, AC 6 spy); (2) `session_work.py` `(test_runs_count or not _test_run(tokens))` → `(test_runs_count or True)`: `12 failed, 137 passed`; (3) `timeout` prefix handling disabled in `_test_run`: `6 failed, 143 passed`. Prior content: guide BEFORE `75 failed, 74 passed` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `session_work.py` (diff + `_segments`, `_Task`), `stop_auto_mode_check.py` `session_owner`/`session_window`, the test-debate stub, oracle diff since lock; grep of all callers of `worked_on`/`work_start`; `pre_bash_block_unsafe_merge.py`, `merge_gate_guard.py` diffed against `main`. Skipped: `task_context.py`/`auto_mode.py` bodies (no call to the two functions; only `PYTHON_FLAGS` import read), unrelated hooks |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider -rf` → `95 failed, 8214 passed, 7 skipped` (646s). No failure is in a T324 or hooks-session file: 5 in `.claude/hooks/tests/` (`test_memory_channel_and_budget.py` x4, `test_token_audit_format.py` x1: `memory/MEMORY.md` over its char budget, fail identically in the main checkout) and 90 in `tests/` (`test_token_meter.py` 71, `test_plugin_double_install.py` 15, 4 others: `FileNotFoundError` in the environment; `tests/` alone: 90 failed in this worktree and 102 in the main checkout, this worktree's set is a subset of main's). `tests/test_token_meter.py` alone: `74 passed`. Not caused by T324; the guide's earlier 6th failure (the `test_debate_window` stub) is fixed |
| **Companion score (easy-verifier)** | ☑ N/A | not run: the companion tools are not in this reviewer's tool set; the merge gate blocks on ☑ fail only |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | hook-only change, no UI (guide: UI rows N/A) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | hook-only change, no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | hook-only change, no UI |
| Repro loop | ☑ pass | `worked_on([("Bash", {"command": "cd <wt-t321> && timeout 300 python3 -m pytest x.py -q 2>&1 \| tail -40"}, main)], "T321", [<wt-t321>])` → `True` before; with `test_runs_count=False` → `False` (re-run 2026-11-25, probe) |
| Regression test | ☑ pass | `.claude/hooks/tests/test_t324_test_run_not_work.py` |
| Smoke suite | ☑ pass | 32 adversarial forms probed with both keyword values (scratchpad `probe.py`): redirect, chained write, `git commit`, `tee`, `&>`, `2>`, script, double `timeout`, `$(…)` stay work; backticks and test-run options listed under Review findings (P3) |

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

**DELTA**: A session that only runs another task's tests inside that task's worktree no longer owns the task, so its Stop check skips the task with a "not checked" note and writes no false `Paused:` line into the other session's report; the merge gate still treats a test run as work.

**WITNESS**: qa-expert (fresh context, not the implementer), 2026-11-25, from the event trace `memory/event-trace/T324.jsonl` (`python3 scripts/verify_trace.py T324` → `INTACT: lines 1-257 chained and anchored`): the oracle run (`149 passed`), the neighbour suites (`432 passed`), three mutation runs (red) and the probe script are filed there under T324. Live BEFORE: while this review ran, the unfixed Stop hook of the main checkout wrote a false `Paused:` line into this file because the reviewer ran tests in the task's worktree (removed before the commit).
