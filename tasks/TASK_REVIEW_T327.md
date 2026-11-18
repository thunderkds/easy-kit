# TASK_REVIEW — T327: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T327.md`. Everything here is **filled by the reviewer at Stage
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
1. Track extended, Risk High, C2 (deletes worktrees and branches) — RULE: AGENTS.md `## Tracks` ("a change that deletes ... user data", "Risk Medium or High" → extended)
2. Only `git worktree remove` (no `--force`) and `git branch -d` (merged only); never `git clean`, `-D` or prune — RULE: `docs/claude-md/tracks.md` `### Stops that stay` (no destructive action without the user)
3. Leftover processes inside the worktree are listed and the cleanup refuses while any runs; no signal is sent (option B), not SIGTERM (A) or ignore (C) — DEBATED: B (Advocate 1: A, teardown is the agent's duty per agents/common-infrastructure.md; Advocate 2: B, a worktree may hold another live session; Advocate 3: B, smallest safe thing, a refusal is a clean report line). Settled by `skills/wake/SKILL.md:69` "another live session is still working there — check the worktree's latest commit time and ask before relaunching or touching it" ⚠ decided for you — please review
4. Cleanup is a doctrine step (Supervisor runs the script after the merge), no hook auto-trigger — SAFER OPTION: guide cut list; a hook that deletes worktrees on its own is more risk than the request needs ⚠ decided for you — please review
5. P3 left as is: unreadable `/proc` entries are counted and skipped, not refused — SAFER OPTION: refusing on every unreadable entry (other users' processes) would block every run on a shared machine ⚠ decided for you — please review
6. Security review done by hand: the built-in `security-review` skill fails here (`git log origin/HEAD...`: this repo has no `origin` remote) — FACT: `git remote -v` "github	git@github.com:thunderkds/easy-kit.git (fetch)" ⚠ decided for you — please review
Checks: tests `uv run --with pytest python -m pytest -q tests/test_cleanup_task.py` — 14 passed (red first: 8 failed, 5 passed; mutation `if dirty:`→`if False:` caught); full suites: no failure in a file this task touched, all failures pre-existing on `main` (see Evidence); reviews code-review — 0 P0, 0 P1 code, 1 P1 process note resolved (agents/common-infrastructure.md arrives as the agent's system prompt), 1 P3; security-review (by hand) — no findings: task ID `T\d+`, list-arg subprocess, no force flags, no signals, branch must be in `refs/heads` and an ancestor of `main`; real run: not run against the real repo on purpose (it deletes the task's worktree) — fixture repos only (auto-checked, not /verify)
Memory: memory/learnings.md — "2026-11-18 — `[admin]` with two new guides, a repo without `origin`, and git 2.34"; memory/MEMORY.md — `[admin]` binds line extended
Not done: merge (admin: after the auto verify pass); push of `main` (yours: the gate pushes only to `origin`, this repo's remote is `github`); auto verify: running (T182)

## Evidence
| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_cleanup_task.py`: `uv run --with pytest python -m pytest -q tests/test_cleanup_task.py` -> `14 passed in 2.48s`. Covers AC1 (worktree, branch), AC2 (not Done, unmerged), AC3 (untracked, modified), AC4 (a `sleep` with cwd in the worktree, also via a symlink: listed, refused, still alive, worktree and branch kept; cleanup succeeds after it ends; no signal calls in the source), AC5 (second run, linked worktree), AC7 (other worktree untouched), bad ID, no-branch-in-row, no-force/no-signal source check |
| Verification command run | ☑ pass | `uv run --with pytest python -m pytest -q -p no:cacheprovider .claude/hooks/tests tests` -> `76 failed, 7481 passed, 24 skipped, 87 subtests passed in 412.45s`. All 76 failures are in files this task does not touch: test_admin_tag (20), test_slot2b_brace_glob (19), test_stop_attribution_t287 (25), test_admin_repo_allowlist (3), test_heredoc_quoted_marker (4), test_t317_session_tags (2), test_auto_verify_skip_pass (1), test_gate_hidden_verbs (1), tests/test_auto_verify.py (1, a timeout test; passes alone: `253 passed in 97.84s`). With my changes stashed, the same git-2.34.1 hook files fail the same way (29 failed in the six files re-run; 46 failed in slot2b/t287/t317). None names cleanup_task, tracks.md, pipeline-stages.md or MANIFEST |
| Negative cases hold | ☑ pass | Red run first: `8 failed, 5 passed` with no script. Mutation: `sed 's/if dirty:/if False:/'` on scripts/cleanup_task.py -> `1 failed, 12 passed` (`test_refuses_dirty_worktree_and_leaves_process_alone`); restored |
| verify | ☐ pass / ☐ fail / ☐ N/A | [the auto verify hook writes this row] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed `scripts/cleanup_task.py`, the 4 doc/MANIFEST edits, the 47 pin-test files by grep; skipped nothing else. The script imports `auto_mode.row_branch/board_rows/names_task/read` read-only. Safety: no `--force`, no `branch -D`, no `git clean`, no signal sent (Supervisor change 2026-11-18), list-form subprocess, ID matched by `T\d+` |
| Full smoke suite still green (no regression) | ☑ pass | No new failure versus baseline; see the verification row |
| **Companion score (easy-verifier)** | ☑ N/A | Not run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI |

-------|--------|------------------------|
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

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured 2026-11-18T15:34:27Z, before any implementation commit (HEAD e30e165):

```
$ python3 scripts/cleanup_task.py T327
python3: can't open file '/home/thunderkds/workspace/pets/hungnguyen111/wt-t327/scripts/cleanup_task.py': [Errno 2] No such file or directory
exit=2
```

Stage 5 step list from `docs/claude-md/pipeline-stages.md` (steps 2 to 5 verbatim, step 5 ends the list; no cleanup step):

```
2. **Confirm smoke tests pass** (coordinate with QA-Automation-Agent).

3. Update `PROJECT_SPEC.md` Memory/Insights section with key learnings.

4. **Memory update** (diff-driven pass — run before `ship`):
   - `git diff HEAD~1 --name-only` — identify files changed in this merge
   - If `agents/tech-lead.md` and `docs/architecture/README.md` both exist (tech-lead pack, `packs/tech-lead/PACK.md`), match this list against the map's watched paths: on a match, spawn `tech-lead` in refresh mode for the matched documents only; no match (or no watched-paths column), nothing.
   - Grep `memory/decisions.md`, `memory/glossary.md`, `memory/learnings.md` for references to those files
   - Update matched entries in place (fix stale facts, expand with new context)
   - Append any new decisions or learnings from this session to the appropriate cold file
   - Summarize new/changed entries as one-liners in `memory/MEMORY.md` (keep hot tier ≤50,000 characters)
   - **Self-review reminder** (a reminder only: you never start the loop): run `python3 skills/self-review/scripts/self_review.py pre`. It calls no model. Its one write marks register rows `fixed` once their fix task has merged, so commit `memory/self-review/register.md` with this pass if it changed. If it prints `"status": "ready"` with at least 3 `files`, tell the user in one line that N merged review files wait and that `/self-review` mines them. Never run `/self-review` or its miner yourself. Any other status, or an error: say nothing. In auto mode, put the line under `Not done:`.

5. Merge the worktree and close the task on PROJECT_KANBAN.md. In auto mode with `[auto]` the merge is never automatic: it waits for the user. With `[admin]` the Supervisor merges and pushes the task branch, then pushes `main`, only after the auto verify pass (`docs/claude-md/tracks.md` `### Admin tag`). After an auto verify pass, the hook moves the row to Done (`docs/claude-md/tracks.md` `### Auto close-out`), and the Supervisor ran item 4 before it stopped (the report's `Memory:` line).
```

**AFTER**: tests drive the script on temp fixture repos (the real repo was not touched):

```
$ uv run --with pytest python -m pytest -q tests/test_cleanup_task.py
14 passed in 2.48s
```

Stage 5 item 5 of `docs/claude-md/pipeline-stages.md` now continues: "**Clean up after the merge (T327).** When the task is in Done and its branch is merged into `main`, run `python3 scripts/cleanup_task.py <ID>` from the main checkout. ..." `docs/claude-md/tracks.md` names it after minimal step 7, in `### Admin tag` and in `### Session tags` step 4.

**DELTA**: after a merge the Supervisor can remove the task's worktree, merged branch and leftover test processes with one command that refuses unmerged or dirty work.

**WITNESS**: pytest runs by common-infrastructure agent, 2026-11-18, task trace `memory/event-trace/T327.jsonl`.
