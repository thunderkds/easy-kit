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
Checks: full suite at `00b66ad` fails exactly the 54 `main` baseline tests (`comm -3` empty; 54 failed, 7572 passed); Verification Command 178 passed — auto-checked, not /verify. Stage 4 reviewer spawn, code-review and security-review NOT run (paused below).
Memory: nothing new (no merge; the async-spawn finding goes to memory when the question below is decided)
Not done: Stage 4 reviewer spawn, code-review, security-review, auto verify, merge (admin: after the auto verify pass)
Paused: unsure — every `Agent()` spawn in this harness is recorded `spawn.status: async_launched` (all 7 spawns of 2026-11-20 in `memory/event-trace/T341.jsonl` / `_untagged.jsonl`; the Agent tool has no foreground option), but `trace_shows_review` counts only `completed` or no status, so after merge every extended-track merge would be refused; options: A accept an `async_launched` reviewer record (proves a spawn on that commit, not that it finished) / B add a completion record written at the reviewer's end (SubagentStop hook) and count only that / C keep the gate as is and run the reviewer from a CLI session that records `completed`

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

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

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
