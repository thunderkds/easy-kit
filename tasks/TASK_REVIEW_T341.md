# TASK_REVIEW — T341: Extended track: the Supervisor writes the code, a fresh reviewer spawn is required at merge

> Sibling of `tasks/TASK_GUIDE_T341.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Auto decisions

Mode: auto
1. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule ("Complexity C2 or above … extended"; "Risk Medium or High … extended"): C3, Risk High, changes Hard-Stop Gate 1 and the merge gate.
2. Option B of the lean-kit proposal, staged: this task is step 1 (Supervisor implements + reviewer spawn gated at merge); Advocate counts wait for step 2. User's answer in chat, 2026-11-20: "should start the enhance now", then "run by automate, [admin]" — RULE: `docs/brainstorming/BRAINSTORMING_LOG_lean-kit.md` § Questions Log (the task-none Debate there: all 3 Advocates chose B; it reverses DDR-0004).
3. Merge-gate proof of the review is a hook-written trace record of a `Reviewer: <ID>` spawn whose prompt names the reviewed commit (chain hash and anchor checked, tree diff to the tip limited to review/board/memory files); no committed text line counts as proof — RULE: `.claude/hooks/pre_bash_block_unsafe_merge.py:560` "a row with no `auto-run by hook`" … "tag is typed by hand and counts for nothing" (T309). Input: 3 Advocates ran on this before the task's window opened (Advocate 1: trace record + committed `Reviewed:` line naming the same commit; Advocate 2: trace record with the commit in the prompt, no committed line; Advocate 3: trace record with the commit in the prompt, anchor required, scan all trace files by description); the rule picks the trace-only variants.
4. No cutoff for tasks planned before the rule; the check runs per merged/pushed target, not in the board-wide Ready-for-Review loop — RULE: `memory/decisions.md:2664` "Existing projects are checked too (no grandfathering)" and `.claude/hooks/pre_bash_block_unsafe_merge.py:2378` "B11: a commit dated in the future is not trusted" (a date cutoff would trust `%ct`). Input: 3 Advocates ran on this in an earlier session, before this trace window (Advocate 1: C, no exemption; Advocate 2: C, no exemption; Advocate 3: C, no exemption, wire per target so the merged T326/T327 rows block nothing); all three agree with the rule.
5. Implementer: a `common-infrastructure` sub-agent, not the Supervisor — RULE: `AGENTS.md:171` "The Supervisor must never write implementation code directly." (Gate 1 stays in force until this task merges).
6. Merge-gate sign-off: T341 added to `AUTHORISED_TASKS` by the Supervisor under session `[admin]` — RULE: `.claude/hooks/tests/merge_gate_guard.py:22` "**Adding a task is the record.**" (precedent T323, T326).
7. Supervisor-written fixture repair (`d06a85d8`, `d425b47e`: test helpers, pins, AGENTS.md wording) reverted; a `common-infrastructure` sub-agent redoes it — DEBATED: B (Advocate 1: A, keep both, record the breach of main's Gate 1 plainly, the required `Reviewer: T341` covers them; Advocate 2: B, revert both and have a `common-infrastructure` sub-agent redo them, because main's Gate 1 holds until the merge; Advocate 3: A, keep both, smallest change, the reviewer covers the tip) — settled by RULE: `AGENTS.md:171` on `main` "The Supervisor must never write implementation code directly." and `AGENTS.md:168` "not skippable by any rationale"; matches decision 5.
8. Gate proof is a `ReviewerDone` record written by a new `SubagentStop` hook when the reviewer ends, not the spawn record (option B; `.claude/settings.json` gains that one hook entry) — RULE: the user's answer in chat, 2026-11-20, "so B" (after the Supervisor's Paused: unsure with options A/B/C; recorded in `tasks/TASK_GUIDE_T341.md` § Questions Log).
9. Final review's P2 (the uncertain-`cd` fix also refuses a bare `git merge`, `--ff-only`, `--no-edit` and a minimal-track branch after `cd … ;`, with a remedy that does not fit) left as a follow-up, not fixed before merge — RULE: `skills/code-review/SKILL.md:27` "| **P2** | Code quality, maintainability, non-critical test gap | Recommended |" (P0/P1 must be fixed; this one fails closed, on the safe side).
Checks: tests — Verification Command + hook tests `246 passed` at `78fa654a`; full suite at `42da381` equals the 54-test `main` baseline (`comm -3` empty); reviews — three fresh `Reviewer: T341` spawns (final, at `42da3819`: 0 P0, 0 P1, 2 P2, 5 P3, AC 1-14 pass), code-review and security-review done by hand in each (the reviewer has no Skill tool; the built-in `security-review` reads `origin/HEAD` and this repo's remote is `github`); real run — the gate probed on real commands by the Supervisor and three reviewers. Auto-checked, not /verify.
Memory: `memory/decisions.md` "2026-11-20 — T341 merged: the Supervisor writes extended-track code; the merge gate requires a finished fresh reviewer (DDR-0011)"; `memory/learnings.md` "2026-11-20 — T341 traps: async spawn records, gate tests that break on a new merge rule, a skill that needs `origin/HEAD`"; two `memory/MEMORY.md` index lines (commit `0545dcf`)
Not done: push (admin: after the merge); live check that the `SubagentStop` hook writes a `ReviewerDone` for a real reviewer (needs a session that loaded the new settings); follow-up P2 (decision 9); auto verify: ☑ pass (session 5a385c9a-5a12-464f-8c6b-13d34e2c3e5b, commit 5b6c5074bd4aa378755589b13970a70df1f0f7f3)
Closed: row moved to Done 2026-11-20 — auto verify pass (session 5a385c9a-5a12-464f-8c6b-13d34e2c3e5b, commit 5b6c5074bd4aa378755589b13970a70df1f0f7f3); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t341_reviewer_gate.py` (AC 4-6, 9, 12, 13), `.claude/hooks/tests/test_t341_reviewer_done.py` (AC 11, 13), `tests/test_t341_gate1_doctrine.py` (AC 1-3, 7, 8, 10, 14), `.claude/hooks/tests/test_admin_tag.py::test_t341_admin_merge_is_refused_without_a_reviewer_record`; all written in this task |
| Verification command run | ☑ pass | 2026-11-20T14:48:29Z at `78fa654a`: guide Verification Command + `test_t341_reviewer_done.py` → `246 passed in 5.76s` |
| Negative cases hold | ☑ pass | Red runs before each fix are in the Demonstration BEFORE blocks (30 red on the unchanged gate; 78 red before option B; 9 red before the chained-merge fix; 2 red before the uncertain-`cd` fix). Mutation probes by Reviewer 3: removing the anchor check fails 2 tests, the freshness check 7, the ancestor check 1, the `cd` fix 2 |
| verify | ☑ pass | auto-run by hook, session 5a385c9a-5a12-464f-8c6b-13d34e2c3e5b, commit 5b6c5074bd4aa378755589b13970a70df1f0f7f3, log .claude/verify-runs/T341-5b6c5074bd4a.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Three fresh `Reviewer: T341` spawns on `0fb03d6e`, `cde2e785`, `42da3819`: the `main...<commit>` diff, its callers (`branch_targets`, `_git_actions`, `merge_brought_task_ids`) and the gate tests. Final review: 0 P0, 0 P1, 2 P2, 5 P3, AC 1-14 pass |
| Full smoke suite still green (no regression) | ☑ pass | At `42da381` (code identical to `78fa654a`; only the review file differs): `54 failed, 7646 passed`; `comm -3` against the unchanged-`main` list (54 failures for missing `busybox`/`zsh`) is empty. Reviewer 3's run had 1 more (`test_auto_verify_skip_pass.py`, a timeout under probe load); that file alone: `222 passed` |
| **Companion score (easy-verifier)** | ☑ N/A | neither companion tool was run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component: hooks, tests and docs (`site/` changes are one table row and a hook count, text only) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI component: hooks, tests and docs (`site/` changes are one table row and a hook count, text only) |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI component: hooks, tests and docs (`site/` changes are one table row and a hook count, text only) |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured by the common-infrastructure sub-agent before any implementation commit, on
`feat/t341-reviewer-gate` at `62b45ec62ca62ba229a11984b3b36869df5fb341` (the merge gate unchanged:
`git diff --stat HEAD -- .claude/hooks/pre_bash_block_unsafe_merge.py` empty). The new test
`.claude/hooks/tests/test_t341_reviewer_gate.py` runs against the unchanged gate.

(1) The gate allows the merge of an extended-task branch that has a committed hook verify pass and
no reviewer record (`merge(fx)` returns `None`: the gate printed no block):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; python3 -m pytest .claude/hooks/tests/test_t341_reviewer_gate.py -q -p no:cacheprovider -k "sc1 or sc2 or done_row or backdated"
2026-11-20T05:06:26Z
62b45ec62ca62ba229a11984b3b36869df5fb341
F.FF                                                                     [100%]
_ test_sc1_ready_for_review_with_a_verify_pass_but_no_reviewer_record_is_refused _
    def test_sc1_ready_for_review_with_a_verify_pass_but_no_reviewer_record_is_refused(gate):
        fx = gate(kanban(ready=(TID,)))
        fx.extended()
        fx.verified()
>       assert_review_block(merge(fx))
text = None
    def assert_review_block(text):
>       assert text is not None, "the merge must be refused: no valid reviewer record for the tip"
E       AssertionError: the merge must be refused: no valid reviewer record for the tip
E       assert None is not None
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_sc1_ready_for_review_with_a_verify_pass_but_no_reviewer_record_is_refused
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_guide_committed_with_a_backdated_committer_date_is_still_checked
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_the_done_row_of_an_extended_task_is_checked_too
3 failed, 1 passed, 33 deselected in 0.51s
```

The whole new file at 2026-11-20T05:06:08Z on the same commit: `30 failed, 7 passed in 11.37s`. Every
"is refused" case fails with `assert None is not None`, or on a missing `trace_shows_review` /
`reviewer_commit` / `REVIEWER_PROMPT_PREFIX` / `chain_hash`. The 7 "is allowed" cases already pass:
the unchanged gate allows every one of these merges.

(2) The current last two sentences of `AGENTS.md` Hard-Stop Gate 1 (line 171), verbatim:

> The Supervisor must never write implementation code directly. On the minimal track the Supervisor writes the code itself, with no guide, and ends with a Decision record (`docs/claude-md/tracks.md`).

**BEFORE (option B)**: captured by the common-infrastructure sub-agent on `feat/t341-reviewer-gate`
at `27eacfe9a29ea40ba5dd8b00fdad6921f15fb48a`, after the red AC 11-14 tests were written and before
any implementation commit. The gate and `.claude/settings.json` are unchanged (`git diff --stat HEAD`
on both is empty), and `.claude/hooks/subagent_stop_reviewer_done.py` does not exist. The old gate
still counts an `Agent` spawn record (`completed`, or no status) as proof, and refuses a `ReviewerDone`
record on the tip:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; python3 -m pytest .claude/hooks/tests/test_t341_reviewer_done.py .claude/hooks/tests/test_t341_reviewer_gate.py -q -p no:cacheprovider --tb=no -rf -k "writes_one_reviewer_done or spawn_record_alone or sc2_ or real_hook_writes or remedy_names or another_task_is"
2026-11-20T11:03:11Z
27eacfe9a29ea40ba5dd8b00fdad6921f15fb48a
FFFFFFFF                                                                 [100%]
FAILED .claude/hooks/tests/test_t341_reviewer_done.py::test_a_reviewer_that_ends_writes_one_reviewer_done_record - AssertionError: /home/thunderkds/.cache/uv/builds-v0/.tmpCmNZ4r/bin/python: can't ...
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_sc2_a_valid_reviewer_record_naming_the_tip_allows_the_merge - AssertionError: assert '[hook:pre_bash] Pipeline gate failed — cannot push/...
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_reviewer_done_record_for_another_task_is_refused - AssertionError: [hook:pre_bash] Pipeline gate failed — cannot push/merge:
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_an_agent_spawn_record_alone_is_refused[async_launched] - AssertionError: [hook:pre_bash] Pipeline gate failed — cannot push/merge:
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_an_agent_spawn_record_alone_is_refused[completed] - AssertionError: the merge must be refused: no valid reviewer record for the tip
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_an_agent_spawn_record_alone_is_refused[None] - AssertionError: the merge must be refused: no valid reviewer record for the tip
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_the_remedy_names_the_spawn_shape_and_the_hook_record - AssertionError: [hook:pre_bash] Pipeline gate failed — cannot push/merge:
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_the_record_the_real_hook_writes_when_the_reviewer_ends_allows_the_merge - AssertionError: [hook:pre_bash] Pipeline gate failed — cannot p...
8 failed, 69 deselected in 10.06s
```

(`python3 -m pytest` ran as `uv run --with pytest python -m pytest`.) `can't ...` is `can't open file
'.../subagent_stop_reviewer_done.py'`. The refused cases show the old remedy, which asks for a spawn "in
the foreground" and names no `SubagentStop` record. The whole changed set at 2026-11-20T11:02:29Z on the
same commit (`test_t341_reviewer_done.py`, `test_t341_reviewer_gate.py`,
`tests/test_t341_gate1_doctrine.py`): `78 failed, 14 passed in 12.34s`.

The doctrine text of AC 14 as it is now, `docs/claude-md/pipeline-stages.md` Stage 4 step 0, verbatim:

> The exact shape, in the foreground (not `run_in_background`), with this session's active-task state set to `<ID>`:

**BEFORE (Stage 4 P1 fix, chained merge)**: captured by the common-infrastructure sub-agent at
`9024d6ed8065d3af75c492cb91c2ffcb08d73e2b`, after the red tests were written and before any fix
commit (the gate unchanged: `git diff --stat HEAD -- .claude/hooks/pre_bash_block_unsafe_merge.py`
is empty). Every chained shape is allowed with no reviewer record; `git merge --abort/--continue/--quit`
and the `[admin]` case already pass:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; git diff --stat HEAD -- .claude/hooks/pre_bash_block_unsafe_merge.py; python3 -m pytest .claude/hooks/tests/test_t341_reviewer_gate.py .claude/hooks/tests/test_admin_tag.py -q -p no:cacheprovider --tb=no -rf -k "chained or abort_continue or t341_admin"
2026-11-20T11:37:15Z
9024d6ed8065d3af75c492cb91c2ffcb08d73e2b
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[checkout-merge]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[pull-merge]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[merge-push-main]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[merge-push]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[merge-branch-d]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[merge-or-push]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused[push-branch-push-main]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_of_a_code_change_after_the_reviewed_commit_is_refused
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_chained_merge_that_names_no_branch_is_refused
9 failed, 19 passed, 268 deselected in 1.32s
```

**BEFORE (second Stage 4 P1 fix, merge after an uncertain `cd`)**: captured by the common-infrastructure
sub-agent at `f3096282f860cc52747b44a8e7d176ca41fc1236`, after the red tests were written and before any
fix commit (the gate's `git diff --stat` is empty). `cd <main> ; git merge --no-ff <b>` and
`cd <main> || git merge --no-ff <b>` are allowed with no reviewer record; the `&&` shape, a lone merge,
`git merge --abort` and the new ancestor-only case already behave as wanted:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse HEAD; git diff --stat HEAD -- .claude/hooks/pre_bash_block_unsafe_merge.py; python3 -m pytest .claude/hooks/tests/test_t341_reviewer_gate.py -q -p no:cacheprovider --tb=no -rf -k "uncertain_cd or certain_cd or lone_merge_and or not_its_ancestor"
2026-11-20T14:29:43Z
f3096282f860cc52747b44a8e7d176ca41fc1236
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt[semicolon]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt[or]
2 failed, 3 passed, 64 deselected in 0.35s
```

The ancestor-only test kills the reviewer's mutation: with `merge-base --is-ancestor`'s result ignored
(a temporary in-place edit, reverted with `git checkout --` before any commit), only it fails beyond the
two P1 reds:

```
mutation (is-ancestor result ignored):
 .claude/hooks/pre_bash_block_unsafe_merge.py   |  2 -
 .claude/hooks/tests/test_t341_reviewer_gate.py | 55 ++++++++++++++++++++++++++
 2 files changed, 55 insertions(+), 2 deletions(-)
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt[semicolon]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt[or]
FAILED .claude/hooks/tests/test_t341_reviewer_gate.py::test_a_reviewed_commit_with_the_tips_tree_that_is_not_its_ancestor_is_refused
3 failed, 66 passed in 2.85s
```

**AFTER**: 2026-11-20T14:48:29Z at `78fa654ad384d6a668a9b845b901b2cfc1d5d715`, the guide's Verification Command plus `.claude/hooks/tests/test_t341_reviewer_done.py`: `246 passed in 5.76s` — every BEFORE red case above is green. Supervisor probe of the gate at `42da381`: `git merge --no-ff feat/t341-reviewer-gate`, `git checkout main && git merge --no-ff …`, `cd /tmp ; git merge --no-ff …`, `cd /tmp || git merge --no-ff …` are all refused with no `ReviewerDone`; `git merge --abort` passes. `AGENTS.md:171` Gate 1 now reads "On the extended track the Supervisor writes the code itself, in the task's worktree, test first; …".

**DELTA**: The Supervisor may now write extended-track code itself, and the merge gate refuses an extended-task branch until a `SubagentStop`-written `ReviewerDone` record shows a fresh reviewer finished on that exact code.

**WITNESS**: the Supervisor (session 4e0cb7e2), not the implementing sub-agent: `memory/event-trace/T341.jsonl` record at `2026-11-20T14:48:35Z`, a non-error `Bash` call running the Verification Command + `test_t341_reviewer_done.py` at `78fa654a`. Three fresh `Reviewer: T341` spawns re-ran the tests independently (sections below).

## Stage 4 code-review (Supervisor, inline, 2026-11-20, range `main...a7e7512f`)

Not the independent `Reviewer: T341` spawn: that spawn waits on the Paused question. Lane: `C3, 27 files, 1409 lines, FITS`; 16 files unpredicted by the guide's Files table (the fixture and pin files). Startup reads of the implementer (`5f54ee3`, `00b66ad`): all four Permanent-Rule reads reported — pass. Entry point `trace_shows_review`: found.

| Sev | File | Line | Finding | Conf | Action |
|-----|------|------|---------|------|--------|
| P1 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `_spawn_finished` | Every `Agent()` spawn in this harness is recorded `spawn.status: async_launched` (7 of 7 on 2026-11-20); the gate counts only `completed` or no status, so after merge no extended-track merge can pass. `test_a_background_spawn_that_only_launched_is_refused` pins it; the remedy text and `pipeline-stages.md` Stage 4 ask for a foreground spawn the Agent tool cannot make. | 100 | User decision (Paused: unsure, options A/B/C) |
| P2 | `tasks/TASK_GUIDE_T341.md` | Files to Change | 16 changed files not predicted (fixture helpers, older gate tests, pins, `CLAUDE_LEGACY.md`). | 75 | Add them to the Files table at the next guide touch |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `main` board read | No `PROJECT_KANBAN.md` exits before `review_blockers` runs, so a project with no board gets no reviewer check (the existing exit, unchanged). | 75 | Note only |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `review_blockers` | A bare `git merge` (upstream) resolves no task target and is not checked. | 75 | Note only |

P0: none. Probed: `git merge --abort/--continue/--quit` pass through; `git merge -m x <task branch>` is refused with the remedy. Safe fixes applied: none (the P1 needs the user's choice).

## Stage 4 security-review (Supervisor, by hand, 2026-11-20)

The built-in `security-review` skill could not run: it reads `origin/HEAD`, and this repo's only remote is `github` (`fatal: ambiguous argument 'origin/HEAD...'`). Reviewed by hand instead, scope `pre_bash_block_unsafe_merge.py` T341 block. Findings: none.
- Git calls take argument lists, no shell; the reviewed commit comes only from `Commit: ([0-9a-f]{40})`; the tip is checked against `SHA_PATTERN`; `glob.escape` on `TRACE_DIR`.
- Probed: `git merge --no-ff -- --output=/tmp/x-t341` → no target, no git call with that argument; `git merge feat/t341-x^{commit}` → refused fail-closed; a summary whose prompt carries a quoted `"description": "Reviewer: T341"` while the real description differs → not a reviewer record.
- Known limit (documented in `docs/claude-md/tracks.md` `### Known limits`): an agent's own Python can write a chained, anchored record; the anchor raises the bar and is not a proof.

## Stage 4 review (Reviewer: T341, commit 0fb03d6e)

Fresh-context reviewer, from the repo only. Range `main...0fb03d6e31a12cf9f0d3b0b16a79f9b36a309872` (37 files, +2069/-52). Lane (`scripts/lane_check.py`): `C3, 36 files, 2008 lines, FITS`; 21 files unpredicted by the guide's Files table (older gate tests, `CLAUDE_LEGACY.md`, plugin `hooks.json`, site, pins). Entry point `trace_shows_review`: found (`.claude/hooks/pre_bash_block_unsafe_merge.py:2772`). The `Skill` tool is not available to this reviewer: `code-review` was run by hand from `skills/code-review/SKILL.md` (always-on personas plus security and adversarial), and `security-review` by hand (see below).

### Tests

- Verification Command set plus the two new hook test files: `219 passed in 14.78s` (`test_t341_reviewer_gate.py`, `test_t341_reviewer_done.py`, `tests/test_t341_gate1_doctrine.py`, `test_merge_gate_guard.py`, `tests/test_tracks.py`, `tests/test_agents_md_primary.py`).
- Full suite in the worktree: `54 failed, 7618 passed, 24 skipped, 87 subtests passed in 396.42s`. The 54 failed test IDs are identical to the 54 in `main_f.txt` (unchanged `main`): `comm` of the two sorted lists shows 0 new failures, 0 fixed.
- Adversarial probe (scratch test outside the repo, driving the real `main()` of the gate on the task's own fixture: guide and code committed, verify pass committed, no reviewer record): see P1-1.

### Findings

| Sev | File | Line | Finding | Conf | Action |
|-----|------|------|---------|------|--------|
| P1 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2806-2834 (`review_blockers`), via `branch_targets` L1242 | **A merge chained with another git command is not checked.** `branch_targets` returns `([], [])` unless the command holds exactly one git action, so `review_blockers` finds no target and returns `[]`. Probed with no reviewer record and the verify pass committed: `git checkout main && git merge --no-ff feat/t950-x` ALLOW; `git pull github main && git merge --no-ff feat/t950-x` ALLOW; `git merge --no-ff feat/t950-x && git push github main` ALLOW; `git merge … && git push` ALLOW; `git merge … && git branch -d …` ALLOW; `git merge … || git push github main` ALLOW; `git push github feat/t950-x && git push github main` ALLOW. The same bare `git merge --no-ff feat/t950-x` and `git merge … && git status` are refused. `git checkout main && git merge <branch>` is the usual way to merge, so AC 4 ("refuses `git merge <task branch>`") and AC 9 are not met for the common shape. `git merge x; echo` is refused ("cannot tell which branch"): only `&&`/`\|\|` chains escape. No test chains commands. | 100 | In `review_blockers`, when any action is a merge (or a narrowed push) and `branch_targets` is empty, resolve each merge action's sources itself (as `merge_brought_task_ids` L1292 does per action) or refuse as `UNRESOLVED_MERGE` does. Add tests for `checkout main && merge`, `merge && push`, `merge \|\| push` that fail before the fix. |
| P2 | `.claude/hooks/tests/test_t341_reviewer_gate.py` | whole file | No test drives the check through the `[admin]` path (guide Edge Case "`[admin]` path: the same check applies"); `grep admin` on the file is empty. The code path is shared (`main()` reaches `review_blockers` after `auto_mode_blocker`), but the claim is unpinned. | 75 | Add one `[admin]`-session merge case: refused without a `ReviewerDone`, allowed with one. |
| P3 | `.claude/hooks/subagent_stop_reviewer_done.py` | 133-150 | The hook does not read the event's `agent_type` (the spike lists it). A no-op sub-agent of any type, spawned by the Supervisor with the three prompt lines, leaves a `ReviewerDone` record. Documented in `tracks.md` Known limits ("whatever it did"), so a hardening note only. | 75 | Optionally require `agent_type` to end in `qa-expert`; keep the limit text. |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2710 | `is_reviewer_call` has no caller (grep over the repo: only its definition). Leftover from the first design (spawn record). | 100 | Delete it, or use it in `_reviewed_commits` in place of `reviewer_commit`. |
| P3 | `tasks/TASK_GUIDE_T341.md` | AC 5, AC 9, Edge Case list | AC 5 and AC 9 still describe the spawn record (`description` exactly `Reviewer: <ID>`, `completed`); AC 12-13 replace that with the `ReviewerDone` record. The code follows AC 12. | 75 | Mark AC 5/9 "superseded by AC 12/13" at the next guide touch. |
| P3 | `docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md` | 25-27 | Context says the trace hook's record "of every `Agent` call" lets the gate require the reviewer; the shipped gate counts the `SubagentStop` record instead (the Decision section says so correctly). | 75 | Reword the Context sentence. |
| P3 | `.claude/hooks/tests/test_agent_guide_dedup.py`, `tests/test_agents_md_primary.py` | `T070_BASELINE_REF`, `CLAUDE_LEGACY_REF` | The pins now name branch commits `5f54ee3c` and `08226d34`. They resolve only if the branch commits stay in `main`'s history: a squash merge or a rebase would break both tests. | 75 | Merge with `--no-ff` (as the board already does), or repoint after the merge. |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `branch_targets` doc L1243-1250 | Routes that bring a task branch in without `git merge` or a narrowed push are not checked: `git pull . <branch>`, `git cherry-pick`, `git rebase`, `git fetch . <branch>:main`, `git push github <branch>:main` (probed: all ALLOW). Same scope as the verify check and as AC 4's wording; DDR-0011 "Revisit if" covers it. | 75 | Note only. |

P0: none. P1: 1. P2: 1. P3: 6.

### Acceptance Criteria

| AC | Verdict | Evidence |
|----|---------|----------|
| 1 | pass | `AGENTS.md:171` keeps the title and the guide-before-code rule; the "never write implementation code" sentence is gone; it says the Supervisor writes the code in the worktree, test first, implementer spawn only for 2+ independent tasks or a C3 task too big for one context, one reviewer spawn required by the merge gate. Stage 3 and 4 lines `AGENTS.md:151-152` match. `test_ac1_*` pass. `CLAUDE_LEGACY.md` mirrors it. |
| 2 | pass | `docs/ddr/0011-…md` exists: supersedes DDR-0004, evidence table (15,669 vs ~47k floor, replay named with no result file, kit-arms), user's choice (L78-80). `docs/ddr/0004-…md:3` reads `**Status**: Superseded by DDR-0011`. See P3 on one Context sentence. |
| 3 | pass | `docs/claude-md/pipeline-stages.md:219-226` (Stage 4 step 0): exact `Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: "Review alone, from the repo only:\nTask ID: <ID>\nCommit: <40-hex>\nDiff: …\nGuide: …" })`, 300-character note, diff range and guide path only, `code-review` then `security-review` at Medium/High, findings to `tasks/TASK_REVIEW_<ID>.md`. Stage 3 at L198. `test_ac3_*` pass, incl. the prompt/hook match. |
| 4 | **fail (partial)** | Refused for a lone `git merge <task branch>` and a narrowed push (`test_sc1`, `test_a_narrowed_push_*`; the block line names the task and the remedy, `REVIEW_REMEDY` L2690). Not refused for a merge chained with `&&`/`\|\|` (P1). |
| 5 | pass (as superseded by AC 12) | `trace_shows_review` L2772: own file first, any file; chain hash, `prev` link, `"anchor" not in record`, anchor line, as `scripts/verify_trace.py` `read_anchors`/`verify` read them (`_reviewed_commits` L2728); `_reviewed_code_is_tip` L2760 (`merge-base --is-ancestor`, `diff --name-only -z`, allowlist `_review_free` L2755); any exception is False. The spawn-record wording of AC 5 is replaced by AC 12. |
| 6 | pass | `review_in_scope` L2788: guide in the main checkout, at the tip, or in `main..tip`; any git error is in scope; no date read (`test_a_guide_committed_with_a_backdated_committer_date…`). Check runs in `review_blockers` (L3103), not in the board-wide loop (`test_an_already_merged_ready_for_review_task…`). |
| 7 | pass | `merge_gate_guard.py:105-112` comment names the rule and "Supervisor sign-off under session `[admin]`, 2026-11-20"; `"T341"` in `AUTHORISED_TASKS`; gate commit subjects start `T341:`; `test_ac7_*` pass. |
| 8 | pass | `docs/claude-md/tracks.md:12-17` names the new merge-gate condition; `### Known limits` L999-1006 adds "raises the bar; it is not a proof" (own Python can write a matching record, T148/T182). |
| 9 | pass | Refused: no record, another task, record lacking a full 40-hex commit, other tool name, commit not in history, unknown commit, code change after the reviewed commit (`test_sc3`, `test_any_other_file…`, rename into `memory/`), edited or unanchored or `anchor: failed` or unlinked record (`test_sc6`, `test_a_forged_append…`, `test_a_record_whose_prev…`), backdated guide. Allowed: tip equals commit, review-free commits after it (`test_sc4`), minimal track (`test_sc5`), task A merged while task B sits in Ready for Review. The prefix cases are in `test_t341_reviewer_done.py` (hook side, per AC 13). Single-command shapes only (P1). |
| 10 | pass | `grep` over `AGENTS.md`, `CLAUDE_LEGACY.md`, `README.md`, `docs/*.md`, `docs/claude-md`, `agents/`, `templates/`, `skills/*/SKILL.md`, `site/`, `.cursor/rules/`, `packs/` finds no live "never write implementation code" or similar wording; `test_ac10` pins it. Stay as they are, with the reason: `docs/MULTI_AGENT.md` (an implementer on one task is still allowed by Gate 1), `.cursor/rules/agent-base.mdc` (gate titles only), `agents/*.md` and `templates/PROJECT_SPEC_template.md` (role lists; spawned implementers still exist), dated records under `tasks/`, `memory/`, `docs/ddr/`, `docs/archive/`, `docs/brainstorming/`. `skills/craft-spawn-prompt/SKILL.md` and `site/` updated. |
| 11 | pass | `.claude/hooks/subagent_stop_reviewer_done.py`: prompt read as `_spawn_prompt` reads it (L141); `reviewer_target` L64 needs the prefix, `Task ID:`, `Commit: <40-hex>` as lines 1-3 and a task ID that `normalize_task_id` leaves unchanged; record `ReviewerDone`/task/commit/agent_id into `memory/event-trace/<ID>.jsonl`, chained and anchored as `post_tool_trace.py` (`append_record` L112); every error path returns, exit 0, no output. `.claude/settings.json` registers it once. Spike recorded in the module docstring (field names). Not run end-to-end by this reviewer: see Security `needs_validation`. |
| 12 | pass | Gate counts `tool_name == "ReviewerDone"` only (`reviewer_commit` L2699); `test_an_agent_spawn_record_alone_is_refused[async_launched/completed/None]`; remedy text says the record is written when the reviewer ends and "it may run in the background", no "foreground" (`assert_review_block`). |
| 13 | pass | All listed refusals and the two allowed cases have tests in `test_t341_reviewer_gate.py` and `test_t341_reviewer_done.py` (non-reviewer prompt writes nothing, API-error event writes nothing, hand-typed record refused). |
| 14 | pass | `pipeline-stages.md:219` "may run in the background", `tracks.md:15-17`, `DDR-0011` L93-96 say it; `git diff main...0fb03d6e -- .claude/settings.json` adds the `SubagentStop` entry only. Plugin `hooks/hooks.json` and `plugin/hooks/hooks.json` carry the same entry with the existing dedup `grep` form. |

### Security review (by hand)

`security-review` as a skill was not run: this reviewer has no `Skill` tool, and the skill reads `origin/HEAD` (this repo's remote is `github`). Done by hand from `skills/code-review/references/security-reviewer.md`, scope: the gate block, the `SubagentStop` hook, the settings and plugin hook entries.

- Boundary 1, spawn prompt and event fields into a file path (hook). `session_id` and `agent_id` pass `_safe_key`; the task ID must equal its own `normalize_task_id` (probed: `../x`, `T341/../..`, `..`, NUL, 80 characters all give None, so none is written); the commit is `[0-9a-f]{40}` via `fullmatch`. The trace path is `memory/event-trace/<canonical ID>.jsonl`. Rejected: no path escape.
- Boundary 2, trace text into git arguments (gate). The commit comes only from a `ReviewerDone` record that passed `[0-9a-f]{40}` `fullmatch`; the tip from `SHA_PATTERN`; git runs with argument lists (no shell), `--no-replace-objects`, `-z`, `--no-ext-diff`, `--no-textconv`; `glob.escape(TRACE_DIR)`. A `--option`-shaped commit or task ID cannot reach git. Rejected.
- Forged record: an `echo >>` has no anchor, an edited line fails its hash or its anchor line, a chained forged line needs an anchor line the anchor directory (denied to agents by permission rules) would hold; this is the documented T148 limit. Same bar as `trace_shows_verification`. Hardening note only.
- Confirmed (Low, hardening): any sub-agent given the three prompt lines yields a record, whatever it did, even one that is stopped (documented in `tracks.md` Known limits and DDR-0011). Covered by P3 (`agent_type`).
- Confirmed gate gap: the chained-command bypass, P1 above. The actor is the Supervisor (or an agent with Bash), the boundary is the merge gate, the resource is `main`, the result is a merge with no independent review. It is a process-control bypass, not a data exposure, so it is rated P1 and not Critical/High under the security scale; the Supervisor may raise it.
- `needs_validation`: that a real `SubagentStop` fires for a background `qa-expert` sub-agent in a non-plugin install, with the transcript at `<dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl`. Missing fact: a real event from this harness for the reviewer that wrote this section. Safe check: after this reviewer ends, `python3 scripts/verify_trace.py T341` and grep `memory/event-trace/T341.jsonl` for a `ReviewerDone` record naming `0fb03d6e…`. (The directory layout was confirmed by listing this session's `subagents/` folder; the spike in the hook docstring and `test_the_record_the_real_hook_writes…` cover the rest.)
- Settings and plugin hooks: the new entry runs a repo-local script with `$CLAUDE_PROJECT_DIR`; no permission key changed (AC 14). `hooks/hooks.json` and `plugin/hooks/hooks.json` are identical.

Result: no P0 or Critical/High security finding; one P1 gate gap; hardening notes above.

## Stage 4 review (Reviewer: T341, commit cde2e785)

Fresh-context reviewer, from the repo only. Range `main...cde2e785782bbe18aa2f393b8d747b11c5b63441` (37 files). Lane (`scripts/lane_check.py`): `C3, 36 files, 2135 lines, FITS`; the unpredicted files are the fixture, pin and site files as before. Entry point `trace_shows_review`: found (`.claude/hooks/pre_bash_block_unsafe_merge.py:2768`). The `Skill` tool is not available to this reviewer, so `code-review` was run by hand from `skills/code-review/SKILL.md` (always-on personas, plus security, adversarial and over-engineering) and `security-review` by hand from `skills/code-review/references/security-reviewer.md`. The earlier section above (commit 0fb03d6e) was read as claims only; each of its fixes was re-probed.

### Tests

- Verification Command set plus `test_t341_reviewer_done.py`: `241 passed in 5.89s` (`test_t341_reviewer_gate.py`, `test_t341_reviewer_done.py`, `tests/test_t341_gate1_doctrine.py`, `test_merge_gate_guard.py`, `tests/test_tracks.py`, `tests/test_agents_md_primary.py`).
- Full suite in the worktree (`.claude/hooks/tests tests`): `55 failed, 7640 passed, 24 skipped, 87 subtests passed in 393.77s`. `comm` against `main_f.txt`: 54 identical, 1 extra, 0 fixed. The extra is `test_auto_verify_skip_pass.py::test_ac3_one_path_outside_the_list_and_a_skip_answer_stays_blocked[.claude/hooks/foo.py]` (`_wait_row` found no verify row while the suite shared the machine with my probe runs); the whole file re-run alone: `222 passed in 23.42s`. A timing flake of a polling test, not a regression.
- Mutation probe (a copy of `.claude/hooks` in the scratchpad, one change at a time, `test_t341_reviewer_gate.py` re-run): anchor check removed: `2 failed`; freshness (tree diff allowlist) removed: `7 failed`; scope (`review_in_scope`) forced out: `1 failed`; **`merge-base --is-ancestor` check removed: `64 passed`, the mutation survives** (P3).
- Adversarial probe (a scratch test outside the repo, driving the real `main()` of the gate on the task's own fixture: guide and code committed, verify pass committed, no reviewer record) and a subprocess probe of the real `SubagentStop` hook (see below).

### Findings

| Sev | File | Line | Finding | Conf | Action |
|-----|------|------|---------|------|--------|
| P1 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2836-2859 (`review_blockers`), 1242-1296 (`branch_targets`) | **A single merge action whose directory is unknown is not checked.** `_git_actions` gives a `where` of `None` after a `cd` that does not certainly run the next command (`cd <dir> ;`, `cd <dir> \|\|`). `branch_targets` then returns `([], [])` (L1285: `directory is not None` else no task), `chained` is False (one action), and the per-action path L2855, which holds the rule "a merge whose directory is unknown is a doubt" (`_per_action_review_targets` L2807-2830), never runs. Probed with the verify pass committed and no reviewer record: `cd <main> ; git merge --no-ff feat/t950-x` ALLOW; `cd <main> \|\| git merge --no-ff feat/t950-x` ALLOW. The same with `&&` is refused, and so is `git checkout main && git merge …`. AC 4 and AC 5 ("any doubt is false") are not met for this shape. Same root cause as the earlier chained P1: the single-action path trusts an empty `branch_targets` to mean "no task branch". No test covers it. | 100 | In `review_blockers`, when `branch_targets` gives no target and any action is a merge (or a narrowed push), run `_per_action_review_targets` for single-action commands too (it already refuses a merge with `where is None`). Add `cd <dir> ; git merge <task branch>` and `\|\|` cases that fail before the fix. |
| P2 | `tasks/TASK_REVIEW_T341.md` | `## Evidence`, `## Demonstration` | The Evidence rows (new tests, verification command, negative cases, scope, smoke) are still the template placeholders, and `AFTER`, `DELTA` and `WITNESS` are blank. Hard-Stop Gate 5 needs the "New test(s) cover acceptance criteria" row filled with pasted output before Done. The data is in `### Tests` above; the `verify` row is the auto verify hook's. | 100 | Supervisor fills the rows (and the Demonstration tail) at Stage 5 from the pasted runs. |
| P3 | `.claude/hooks/tests/test_t341_reviewer_gate.py` | whole file | No test pins the ancestor check alone: removing `merge-base --is-ancestor` (L2758-2760) leaves all 64 tests green, because every "not in history" fixture also changes code. A commit that is not an ancestor but has the tip's tree (a rebase or cherry-pick of the same code) would pass. | 100 | Add one case: a record naming a non-ancestor commit with the tip's tree, refused (AC 5, AC 9). |
| P3 | `.claude/hooks/subagent_stop_reviewer_done.py` | 133-150 | Carried over: the hook does not read the event's `agent_type`, so any sub-agent given the three prompt lines yields a record. Documented in `tracks.md` Known limits ("whatever it did"). | 75 | Optional: require a `qa-expert` agent type; keep the limit text. |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `branch_targets` doc L1243-1250 | Carried over, with two more probed shapes: routes that bring the code in without a task-named branch are not checked. `git merge <40-hex tip>` ALLOW; `git pull . <branch>`, `git cherry-pick`, `git rebase`, `git push github <branch>:main`, and `git push --tags github <branch> && git status` all ALLOW. Same scope as the verify check and AC 4's wording ("task branch"); DDR-0011 "Revisit if" covers it. | 75 | Note only. |
| P3 | `tasks/TASK_GUIDE_T341.md` | AC 5, AC 9, Edge Case list, Files table | They still describe the spawn record (`is_reviewer_call`, `completed`); the code has no `is_reviewer_call` any more (dead code removed) and follows AC 12/13. | 75 | Mark AC 5/9 "superseded by AC 12/13" and drop `is_reviewer_call` from the Files row at the next guide touch. |
| P3 | `.claude/hooks/tests/test_agent_guide_dedup.py`, `tests/test_agents_md_primary.py` | `T070_BASELINE_REF` `5f54ee3c`, `CLAUDE_LEGACY_REF` `08226d34` | Carried over: the pins name branch commits, which resolve only while those commits stay in `main`'s history. A squash merge or a rebase breaks both tests. | 75 | Merge with `--no-ff` (or fast-forward); never squash. |

P0: none. P1: 1. P2: 1. P3: 5.

Earlier findings (section for 0fb03d6e), re-checked on this commit: chained-merge P1 fixed (all 7 probed chained shapes now refused, `checkout main && merge`, `pull … && merge`, `merge && push`, `merge \|\| push`, `merge && branch -d`, push-branch `&& push main`; tests `test_a_chained_merge_or_task_branch_push_*`); `[admin]` P2 fixed (`test_t341_admin_merge_is_refused_without_a_reviewer_record`); `is_reviewer_call` removed; DDR-0011 Context reworded. Open: the rows above.

### Acceptance Criteria

| AC | Verdict | Evidence |
|----|---------|----------|
| 1 | pass | `AGENTS.md:171` keeps the title `1. **No TASK_GUIDE = no work.**` and the guide-before-code rule; the "never write implementation code" sentence is gone; it says the Supervisor writes the code in the task's worktree, test first, an implementer spawn only for 2+ independent tasks or a C3 task too big for one context, one fresh reviewer spawn required by the merge gate. Stage 3 and Stage 4 lines `AGENTS.md:151-152` match. `tests/test_t341_gate1_doctrine.py` ac1 cases pass. |
| 2 | pass | `docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md` exists, supersedes DDR-0004, holds the evidence rows (floor, replay named with no result file, kit-arms) and the user's choice; `docs/ddr/0004-…md:3` `**Status**: Superseded by DDR-0011`. |
| 3 | pass | `docs/claude-md/pipeline-stages.md:219-226` (Stage 4 step 0): exact `Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: "Review alone, from the repo only:\nTask ID: <ID>\nCommit: <40-hex>\nDiff: …\nGuide: …" })`, the 300-character note, diff range and guide path only, `code-review` then `security-review` at Medium/High, findings to `tasks/TASK_REVIEW_<ID>.md`; Stage 3 at L198. The prompt I was spawned with has this shape. |
| 4 | **fail (partial)** | Refused: lone `git merge <task branch>`, narrowed push, and every chained shape with a known directory (probes above; block line names the task and the remedy, `REVIEW_REMEDY` L2690). Not refused: a single merge after `cd <dir> ;` or `cd <dir> \|\|` (P1). |
| 5 | pass (as superseded by AC 12) | `trace_shows_review` L2768: own file first, any file; `_reviewed_commits` L2724 checks the chain hash, the `prev` link, no `anchor: failed`, and the anchor line, as `scripts/verify_trace.py` reads them; `_reviewed_code_is_tip` L2756 (`merge-base --is-ancestor`, `diff --name-only -z`, allowlist `_review_free` L2751); any exception is False. The ancestor step has no isolating test (P3). |
| 6 | pass | `review_in_scope` L2784: guide in the main checkout, at the tip, or in `main..tip`; any git error is in scope; no date read (`test_a_guide_committed_with_a_backdated_committer_date…`); the check runs in `review_blockers` (L3138), not in the board-wide loop (`test_an_already_merged_ready_for_review_task…`). Mutation "scope forced out": 1 test fails. |
| 7 | pass | `merge_gate_guard.py:105-112` comment names the rule and "Supervisor sign-off under session `[admin]`, 2026-11-20"; `"T341"` in `AUTHORISED_TASKS`; gate commit subjects start `T341:`. |
| 8 | pass | `docs/claude-md/tracks.md:12-19` names the merge-gate condition; `### Known limits` adds "The reviewer record raises the bar; it is not a proof (T341)" naming T148/T182 and own Python. |
| 9 | pass (one shape in P1) | Refused: no record, another task, other tool name, commit not in history, unknown commit, code change after the reviewed commit, edited, unanchored, `anchor: failed` or unlinked record, backdated guide. Allowed: tip equals commit, review-free commits after it, minimal track, task A merged while task B sits in Ready for Review. Mutations on anchor and freshness fail 2 and 7 tests. |
| 10 | pass | `grep -rniE` for "never write implementation", "must never write", "Implementation = sub-agent", "sub-agent implements", "Supervisor never/must not code" over `AGENTS.md`, `CLAUDE_LEGACY.md`, `README.md`, `docs/*.md`, `docs/claude-md`, `agents`, `templates`, `skills`, `site`, `.cursor`, `packs` finds only `tracks.md:607` (about `Approved by`, unrelated). `skills/craft-spawn-prompt/SKILL.md` and `site/` updated; `test_ac10` pins it. |
| 11 | pass | `.claude/hooks/subagent_stop_reviewer_done.py`: prompt read as `_spawn_prompt` reads it (L141); `reviewer_target` L64 needs the prefix, `Task ID:` and `Commit: <40-hex>` as lines 1-3 and a task ID `normalize_task_id` leaves unchanged; the record (`ReviewerDone`, task, commit, agent_id) goes to `memory/event-trace/<ID>.jsonl`, chained and anchored as `post_tool_trace.py`; spike in the docstring; `.claude/settings.json` registers it once. Real run of the hook as a subprocess (scratch project, real transcript layout): a valid prompt wrote one chained record (`prev: genesis`, then linked); uppercase hex, `../../x` task, a leading space, CRLF lines, a 39-hex commit, a missing transcript and a `SubagentStart` event wrote nothing; every run exit 0, empty stdout and stderr. |
| 12 | pass | Gate counts `tool_name == "ReviewerDone"` only (`reviewer_commit` L2699); `test_an_agent_spawn_record_alone_is_refused[async_launched/completed/None]`; `assert_review_block` pins that the remedy names `SubagentStop` and `ReviewerDone` and not "foreground". |
| 13 | pass | The listed refusals and both allowed cases have tests in `test_t341_reviewer_gate.py` and `test_t341_reviewer_done.py` (non-reviewer prompt writes nothing, hand-typed record refused, bad hash or no anchor refused). |
| 14 | pass | `pipeline-stages.md:219` "may run in the background", `tracks.md:12-19`, DDR-0011 say the gate counts the `SubagentStop` record; `git diff main...cde2e78 -- .claude/settings.json` adds the `SubagentStop` entry only (`tests/test_subagent_sandbox_profile.py` allowlist grew by that entry's three lines only). Plugin `hooks/hooks.json` and `plugin/hooks/hooks.json` carry the same entry with the existing dedup `grep` form (`tests/test_plugin_package.py`: 15 hooks, plugin equals settings). |

### Security review (by hand)

`security-review` as a skill was not run: this reviewer has no `Skill` tool. Done by hand from `skills/code-review/references/security-reviewer.md`; scope: the gate block, the `SubagentStop` hook, the settings and plugin hook entries.

- Boundary 1, hook input into a file path. `session_id` and `agent_id` pass `_safe_key`; the task ID must equal its own `normalize_task_id` (probed `../../x`: nothing written); the commit is `[0-9a-f]{40}` by `fullmatch` (uppercase and 39-hex rejected). The trace path is `memory/event-trace/<canonical ID>.jsonl`. No path escape.
- Boundary 2, trace text into git arguments (gate). The commit comes only from a `ReviewerDone` record that passed `fullmatch`; the tip from `SHA_PATTERN`; git runs with argument lists (no shell), `--no-replace-objects`, `-z`, `--no-ext-diff`, `--no-textconv`; `glob.escape(TRACE_DIR)`. An option-shaped commit or task ID cannot reach git.
- Forged record: an `echo >>` line has no anchor, an edited line fails its hash or anchor line; a chained forged line needs a matching anchor line in the anchor directory, which is the documented T148 limit (`tracks.md` Known limits). Same bar as `trace_shows_verification`. Hardening note only.
- Confirmed gate gap: P1 above. Actor: the Supervisor or an agent with Bash; boundary: the merge gate; resource: `main`; result: a merge with no independent review. A process-control bypass, not a data exposure, so P1 and not Critical/High on the security scale; the Supervisor may raise it.
- Low (hardening): a sub-agent given the three prompt lines leaves a record whatever it did, even a stopped one (documented). Covered by the `agent_type` P3.
- `needs_validation`: that a real `SubagentStop` fires for a background `qa-expert` sub-agent and that its transcript sits at `<dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl`. Missing fact: a real event from this harness. This reviewer could not read its own transcript folder (permission denied), so it is not confirmed here. Safe check: after this reviewer ends, `python3 scripts/verify_trace.py T341` and grep `memory/event-trace/T341.jsonl` in the main checkout for a `ReviewerDone` record naming `cde2e785…`.
- Settings and plugin hooks: the entry runs a repo-local script through `$CLAUDE_PROJECT_DIR`; no permission key changed.

Result: no P0 or Critical/High security finding; one P1 gate gap (a single merge after `cd <dir> ;` or `cd <dir> ||`) to fix and re-review before the merge.

## Stage 4 review (Reviewer: T341, commit 42da3819)

Fresh-context reviewer, from the repo only. Range `main...42da38198d0481a49ef02ce74522b19b0432ee94` (37 files; the change since the last reviewed commit `cde2e785` is 3 files: the gate's `review_blockers` `single` term at `.claude/hooks/pre_bash_block_unsafe_merge.py:2858-2859`, 55 new test lines, the review log). Lane (`scripts/lane_check.py`): `C3, 36 files, 2194 lines, FITS`; the unpredicted files are the fixture, pin, plugin and site files as before. Entry point `trace_shows_review`: found (`pre_bash_block_unsafe_merge.py:2768`). The `Skill` tool is not available to this reviewer (`No such tool available: Skill`), so `code-review` was run by hand from `skills/code-review/SKILL.md` and `security-review` by hand from `skills/code-review/references/security-reviewer.md`. The two earlier reviewer sections above were read as claims only; every verdict below was re-derived from the code, tests and probes on this commit.

### Tests

- Verification Command set plus `test_t341_reviewer_done.py`: `246 passed in 5.48s` (`test_t341_reviewer_gate.py`, `test_t341_reviewer_done.py`, `tests/test_t341_gate1_doctrine.py`, `test_merge_gate_guard.py`, `tests/test_tracks.py`, `tests/test_agents_md_primary.py`), run with `uv run --with pytest python -m pytest … -q -p no:cacheprovider`.
- Full suite in the worktree (`.claude/hooks/tests tests`): `55 failed, 7645 passed, 24 skipped, 87 subtests passed in 392.81s`. `comm` against `main_f.txt`: 54 identical, 0 fixed, 1 extra: `test_auto_verify_skip_pass.py::test_ac1_docs_only_branch_and_a_skip_answer_is_a_pass_row_and_a_skip_pass_record` (`_wait_row` polling timeout while the machine ran my probes). The whole file re-run alone: `222 passed in 23.59s`. A timing flake, not a regression (the same file flaked on another case in the previous review).
- Mutation probe (a copy of `.claude/hooks` in the scratchpad, one change at a time, `test_t341_reviewer_gate.py` re-run; baseline `69 passed`): `single = False` (the new fix removed): `2 failed` (the fix is pinned); `merge-base --is-ancestor` forced true: `1 failed` (the previous P3 is fixed, the ancestor check is pinned); **the `or narrowed_push` term of `single` removed: `69 passed`, the mutation survives** (P3-1).
- Adversarial probes (a scratch test outside the repo drives the real `main()` of the gate on the task's own fixture: guide and code committed, verify pass committed, Ready for Review, no reviewer record). About 80 command shapes. All of these were refused: `cd <main> ; git merge …` and `cd <main> || git merge …` (with and without a record: "cannot tell which branch"), `(cd <main> && git merge …)`, `bash -c`, `sh -c "cd …; …"`, `eval`, `$B`, `FOO=1 git merge`, `command git merge`, `/usr/bin/git merge`, `git -C <dir> merge`, `--git-dir=`, `--work-tree=`, `refs/heads/<b>`, `heads/<b>`, quoted names, `-m`, `-F`, `-s`, `-X`, `--squash`, option after the branch, `merge a b` (octopus), `echo hi ; git merge …`, `if …; then git merge …; fi`, `git merge … | cat`, `git merge … & …`. Allowed with no record (all single-scope limits, see P3-2 and P3-1): `git merge <b>~0`, `git merge <b>^`, `cd <main> ; git push github <b>`, `git push github <b>:main`, `git push github HEAD`, bare `git push`.

### Findings

| Sev | File | Line | Finding | Conf | Action |
|-----|------|------|---------|------|--------|
| P2 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2858-2859 (`single`), 2807-2830 (`_per_action_review_targets`), 2803 (`UNREAD_MERGE_REASON`) | **The second P1 fix also refuses merges that are not extended-track task merges, and the remedy text is wrong for them.** Since this commit a lone merge goes through the per-action path, whose doubt rules (a merge with no source and no `--abort/--continue/--quit`; a merge whose directory is unknown) apply to any merge. Probed on the fixture (board present, no record, nothing to do with T950): `git merge` bare, `git merge --ff-only`, `git merge --no-edit` (all three allowed on `cde2e785`, refused now), `cd <main> ; git merge origin/main`, and `cd <main> ; git merge feat/t960-minimal` (a branch with no guide, minimal track) are all refused with "cannot tell which branch this merge brings in … run `git merge <branch>` on its own". The last one contradicts AC 9 ("Allowed for … a minimal-track branch with no guide") for that shape. The remedy says "on its own" although the command already is alone; the useful remedy is `cd <dir> && git merge <branch>`. No test pins either shape as intended (`test_a_lone_merge_and_merge_abort_behave_as_before` covers only a task branch and `--abort`). The chained path already had this behaviour since the first P1 fix; the lone path is new. | 75 | Either narrow the single-action doubt to a merge that names a task branch or has unknown directory and a task-named source, or keep it and (a) reword the message for the single case (`cd <dir> && git merge <branch>`), (b) add tests that pin bare `git merge`, `--ff-only` and `cd <dir> ; git merge <non-task>`. Supervisor's call; the refusal is on the safe side. |
| P2 | `tasks/TASK_REVIEW_T341.md` | `## Evidence`, `## Demonstration` | Evidence rows (new tests, verification command, negative cases, scope, smoke) are still the template placeholders; `AFTER`, `DELTA`, `WITNESS` blank (as in the previous review). Hard-Stop Gate 5 needs the "New test(s) cover acceptance criteria" row with pasted output before Done. The data is in `### Tests` above and in the section of each earlier review. The `verify` row is the auto verify hook's. | 100 | The Supervisor fills the rows at Stage 5 from the pasted runs. |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | 2855-2859 | **The `or narrowed_push` term of `single` is dead, and the comment claims coverage it does not give.** After `cd <dir> ;` or `cd <dir> \|\|` the directory is unknown, `pushed_task_ids` returns None, so `narrowed_push` is False and the term never fires. Mutation: term removed, 69 tests pass. Probed: `cd <main> ; git push github feat/t950-x` and `cd <main> \|\| git push github feat/t950-x` are ALLOWED with no record (`cd <main> && git push …` and plain `git push github feat/t950-x` are refused). A push of a branch to a remote does not integrate it into `main`, and AC 4 limits the push to the one the gate "already judges", so this is not an AC failure. | 100 | Remove the term and the "(or a narrowed push)" comment words, or add the push-after-uncertain-`cd` case to the doubt path with a test. |
| P3 | `.claude/hooks/pre_bash_block_unsafe_merge.py` | `branch_targets` doc L1243-1250 | Carried over, with the shapes probed again on this commit: routes that bring the code in without a task-named branch are not checked: `git merge <b>~0`, `git merge <b>^`, `git merge <40-hex>` (refused only after `cd ;`), `git push github <b>:main`, `git push github HEAD`, bare `git push`, `git pull . <b>`, `git cherry-pick`, `git rebase`. Same scope as the verify check; the anchor-and-trace gate is a bar, not a proof (`tracks.md:999`); DDR-0011 "Revisit if" covers it. | 75 | Note only. |
| P3 | `.claude/hooks/subagent_stop_reviewer_done.py` | 133-150 | Carried over: the event's `agent_type` is not read, so any sub-agent given the three prompt lines yields a `ReviewerDone` record. Documented in `tracks.md:999-1006` ("whatever it did"). | 75 | Optional: require a `qa-expert` agent type; keep the limit text. |
| P3 | `.claude/hooks/tests/test_agent_guide_dedup.py`, `tests/test_agents_md_primary.py` | `T070_BASELINE_REF` `5f54ee3c`, `CLAUDE_LEGACY_REF` `08226d34` | Carried over: the pins name branch commits and resolve only while those commits stay in `main`'s history. A squash merge or a rebase breaks both tests. (`AGENTS_MD_BYTE_CAP` 21886 to 22414 is the sanctioned repoint, with its reason in the test comment.) | 75 | Merge with `--no-ff`; never squash. |
| P3 | `tasks/TASK_GUIDE_T341.md` | AC 5, AC 9, Edge Case list | They still describe the spawn record (`is_reviewer_call`, `completed`); the code follows AC 12/13. | 75 | Mark AC 5/9 "superseded by AC 12/13" at the next guide touch. |

P0: none. P1: none. P2: 2. P3: 5.

Earlier findings re-checked on this commit: the `cd <dir> ;` / `cd <dir> ||` single-merge P1 is fixed (probed: both refused, with and without a valid record; `test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt[semicolon/or]`; `single = False` mutation fails 2 tests). The chained-merge P1 stays fixed (all 7 `CHAINED` shapes pass; `(cd … && …)`, `bash -c`, `eval` also refused). The ancestor-check P3 is fixed (`test_a_reviewed_commit_with_the_tips_tree_that_is_not_its_ancestor_is_refused`; mutation fails 1 test). `[admin]` pin present (`test_t341_admin_merge_is_refused_without_a_reviewer_record`). No P1 remains open in the gate's merge path.

### Acceptance Criteria

| AC | Verdict | Evidence |
|----|---------|----------|
| 1 | pass | `AGENTS.md:171` keeps the title `1. **No TASK_GUIDE = no work.**` and the guide-before-code rule; "The Supervisor must never write implementation code directly" is gone; it says the Supervisor writes the code in the task's worktree, test first, an implementer spawn only for 2+ independent tasks or a C3 task too big for one context, one fresh-context reviewer spawn (`Reviewer: <ID>`) required by the merge gate. Stage 3 and Stage 4 lines `AGENTS.md:151-152` match. `tests/test_t341_gate1_doctrine.py` ac1 cases pass. |
| 2 | pass | `docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md` exists, DDR format of 0004, "supersedes DDR-0004", evidence table (15,669 vs ~47k floor, replay named with no result file, kit-arms), user's choice ("so B"); `docs/ddr/0004-…md:3` reads `**Status**: Superseded by DDR-0011`. |
| 3 | pass | `docs/claude-md/pipeline-stages.md:219-226` Stage 4 step 0: `Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: "Review alone, from the repo only:\nTask ID: <ID>\nCommit: <40-hex>\nDiff: main...<40-hex>\nGuide: …" })`, the 300-character note (`post_tool_trace.py:33` `MAX_SUMMARY_LEN = 300`), diff range and guide path only, `code-review` then `security-review` at Medium/High, findings to `tasks/TASK_REVIEW_<ID>.md`; Stage 3 at L198. The prompt this reviewer was spawned with has exactly this shape. |
| 4 | pass | `review_blockers` (L2836) refuses `git merge <task branch>` and the narrowed push (`test_sc1`, `test_a_narrowed_push_*`), every chained shape, and now a lone merge after an uncertain `cd` (probes above); the block line names the task and the remedy (`REVIEW_REMEDY` L2690; `assert_review_block` pins the spawn shape, `SubagentStop`, `ReviewerDone`, and no "foreground"). A narrowed push after an uncertain `cd` is not judged (P3-1), and that push is not one the gate "already judges". See P2-1 on false refusals. |
| 5 | pass (as superseded by AC 12) | `trace_shows_review` L2768: own file first, then every `*.jsonl`; `_reviewed_commits` L2724: chain hash, `prev` link, no `"anchor"` key (so `anchor: failed` is out), anchor line at the same line number, as `scripts/verify_trace.py` reads them; `_reviewed_code_is_tip` L2756: `merge-base --is-ancestor`, then `diff --name-only -z` against the allowlist (`_review_free`: the review file, `PROJECT_KANBAN.md`, `tasks/MINIMAL_LOG.md`, `memory/*.md` not `MEMORY.md`); any exception returns False. Ancestor step now has an isolating test. |
| 6 | pass | `review_in_scope` L2784: guide in the main checkout, at the tip, or in `main..tip`; any git error is in scope; no date read (`test_a_guide_committed_with_a_backdated_committer_date_is_still_checked`). The check runs from `review_blockers` (called L3142), not in the board-wide Ready-for-Review loop (`test_an_already_merged_ready_for_review_task_with_no_record_blocks_nothing_new`). |
| 7 | pass | `.claude/hooks/tests/merge_gate_guard.py:105-111` comment names the rule and "Supervisor sign-off under session `[admin]`, 2026-11-20"; `"T341"` is in `AUTHORISED_TASKS`; the four gate commits (`da30de9`, `d3759b8`, `4019d59`, `42da381`) start `T341:`; `test_ac7_*` pass. |
| 8 | pass | `docs/claude-md/tracks.md:12-19` names the merge-gate condition; `### Known limits` L999 "The reviewer record raises the bar; it is not a proof (T341)", naming T148/T182 and an agent's own Python. |
| 9 | pass (one shape in P2-1) | Refused (tests in `test_t341_reviewer_gate.py`): no record; a record for another task (`test_a_reviewer_done_record_for_another_task_is_refused`); no full commit; another tool name; commit not in history; unknown commit; code change after the reviewed commit (`test_sc3`, `test_any_other_file…`, rename into `memory/`); edited, unanchored, `anchor: failed`, unlinked record (`test_sc6`, `test_a_forged_append…`, `test_a_record_whose_prev…`); backdated guide. Allowed: tip equals commit (`test_sc2`), review-free commits after it (`test_sc4`), minimal track (`test_sc5`), task A merged while an already merged task B sits in Ready for Review. The prefix case is in `test_t341_reviewer_done.py` (`test_a_sub_agent_without_the_reviewer_prompt_writes_nothing`). The minimal-track branch merged after `cd <dir> ;` is refused as a doubt (P2-1). |
| 10 | pass | `grep -rniE` over `AGENTS.md`, `CLAUDE_LEGACY.md`, `README.md`, `docs/*.md`, `docs/claude-md`, `agents`, `templates`, `skills/*/SKILL.md` and `references`, `site`, `.cursor/rules`, `packs` for "never write implementation", "must never write", "Implementation = sub-agent", "sub-agent implements", "Supervisor never/must not code/implement" finds only `skills/tdd/SKILL.md:11` (about tests) and `tracks.md:607` (about `Approved by`): neither is the old rule. `skills/craft-spawn-prompt/SKILL.md` and `site/docs.html` updated; `test_ac10` pins it. |
| 11 | pass (not run end to end here) | `.claude/hooks/subagent_stop_reviewer_done.py`: `reviewer_target` L64 needs the prefix, `Task ID: <ID>` and `Commit: <40-hex>` as lines 1-3 and a task ID that `normalize_task_id` leaves unchanged; `main` L133 reads the prompt with `_spawn_prompt` (L141); record `ReviewerDone`/task/commit/agent ID into `memory/event-trace/<ID>.jsonl`, chained and anchored as `post_tool_trace.py` (`append_record`); every error path returns, exit 0, no output; the spike is in the docstring. `.claude/settings.json` registers it once. A real `SubagentStop` was not available to me: `memory/event-trace/*.jsonl` in the main checkout holds 0 records with `tool_name` `ReviewerDone`, as expected because the main checkout's `settings.json` has no `SubagentStop` entry until the merge. |
| 12 | pass | The gate counts `tool_name == "ReviewerDone"` only (`reviewer_commit` L2699); `test_an_agent_spawn_record_alone_is_refused[async_launched/completed/None]`; the remedy names `SubagentStop` and `ReviewerDone` and says the spawn may run in the background. |
| 13 | pass | The listed refusals and both allowed cases have tests in `test_t341_reviewer_gate.py` and `test_t341_reviewer_done.py` (spawn record alone, another task, other commit via the ancestor and freshness tests, bad hash or no anchor, `echo >>` record, non-reviewer prompt writes nothing, API-error event writes nothing). |
| 14 | pass | `pipeline-stages.md:219` "The spawn may run in the background", `tracks.md:12-19`, DDR-0011 Decision and Consequences say the gate counts the record the `SubagentStop` hook writes. `git diff main...42da3819 -- .claude/settings.json` adds the `SubagentStop` entry only (11 added lines, no other key). `hooks/hooks.json` and `plugin/hooks/hooks.json` carry the same entry with the dedup `grep` form; `plugin/.claude/hooks/subagent_stop_reviewer_done.py` is a symlink; `tests/test_plugin_package.py` and `tests/test_subagent_sandbox_profile.py` pass. |

### Security review (by hand)

`security-review` as a skill was not run: this reviewer has no `Skill` tool. Done by hand from `skills/code-review/references/security-reviewer.md`; scope: the gate block (`pre_bash_block_unsafe_merge.py:2660-2870`), the `SubagentStop` hook, the settings and plugin hook entries.

- Boundary 1, hook input into a file path. `session_id` and `agent_id` pass `_safe_key`; the task ID must equal its own `normalize_task_id` (`reviewer_target` L64-75); the commit is `[0-9a-f]{40}` by `fullmatch`. The trace path is `memory/event-trace/<canonical ID>.jsonl`. No path escape found.
- Boundary 2, trace text into git arguments (gate). The commit comes only from a `ReviewerDone` record that passed `REVIEWED_COMMIT.fullmatch`; the tip from `SHA_PATTERN`; git runs with argument lists, no shell, `--no-replace-objects`, `-z`, `--no-ext-diff`, `--no-textconv`; `glob.escape(TRACE_DIR)`. An option-shaped commit or task ID cannot reach git. No finding.
- The new `single` branch adds no new input into git: it reuses `_per_action_review_targets`, whose sources go through `_ref_task_id` and then `rev-parse --verify "<branch>^{commit}"` as an argument. No finding.
- Forged record: an `echo >>` line has no anchor, an edited line fails its hash or anchor line; a chained forged line needs a matching anchor line in the anchor directory, which is the documented T148 limit (`tracks.md:999`). Same bar as `trace_shows_verification` (L313). Hardening note only.
- Gate gaps (actor: the Supervisor or an agent with Bash; boundary: the merge gate; resource: `main`; result: a merge with no independent review): the alternate-spelling and non-merge routes in P3-2. A process-control limit, not a data exposure, so not Critical/High on the security scale; the Supervisor may raise it. No open shape in the plain `git merge <task branch>` family (80 probed).
- Low (hardening): a sub-agent given the three prompt lines leaves a record whatever it did (documented; `agent_type` P3).
- `needs_validation`: that a real `SubagentStop` fires for a background `qa-expert` sub-agent and that its transcript sits at `<dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl`. Missing fact: a real event from this harness. Safe check after the merge: spawn one reviewer, then `python3 scripts/verify_trace.py T341` and grep `memory/event-trace/T341.jsonl` for `"tool_name": "ReviewerDone"` naming the commit.
- Settings and plugin hooks: the new entry runs a repo-local script through `$CLAUDE_PROJECT_DIR`; no permission key changed.

Result: no P0, no P1, no Critical/High security finding. Two P2 (a false-refusal widening with a wrong remedy text; Evidence rows still blank) and five P3. Ready for the Supervisor's decision on P2-1.
