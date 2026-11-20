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
1. Track extended — RULE: `docs/claude-md/tracks.md` `## Track rule` (C3, Risk High: changes Hard-Stop Gate 1 and the merge gate).
2. Option B of the lean-kit proposal, staged: this task is step 1 (Supervisor implements + reviewer spawn gated at merge); Advocate counts wait for step 2 — DEBATED (task none, 2026-11-20, `docs/brainstorming/BRAINSTORMING_LOG_lean-kit.md` `## Questions Log`): B staged (Advocate 1: B in one task, gate check in the same task as the Gate 1 rewrite; Advocate 2: B, gate check first, Advocate counts last; Advocate 3: B in two steps, Advocate counts after more replays) — all three agree; reverses DDR-0004, user's go: "should start the enhance now", "run by automate, [admin]".
3. Merge-gate proof of the review: a hook-written trace record of a `Reviewer: <ID>` spawn whose prompt names the reviewed commit, chain hash and anchor checked, tree diff to the tip limited to review/board/memory files; no committed text line counts as proof — DEBATED: commit-bound trace record (Advocate 1: trace record + committed `Reviewed:` line naming the same commit, anchor optional; Advocate 2: trace record with the commit in the prompt, no committed line, `<ID>.jsonl` only, `REVIEW_RULE_SINCE` cutoff; Advocate 3: trace record with the commit in the prompt, anchor required, scan all trace files by description, grandfather tuple). Settled by RULE: `.claude/hooks/pre_bash_block_unsafe_merge.py:560` "a row with no `auto-run by hook` tag is typed by hand and counts for nothing" (T309) — so the committed line is not proof; anchor check and all-files scan taken as the fail-closed variants (Advocates 1 and 3 name the `echo >>` forgery and the T196 misfiling).
4. Cutoff for tasks registered before the rule: `_guides_added_since` against `REVIEW_RULE_SINCE`, None fails closed — SAFER OPTION: reuses an existing helper (`.claude/hooks/pre_bash_block_unsafe_merge.py:2366`) instead of a hand-kept tuple of ~90 Todo IDs ⚠ decided for you — please review
5. Implementer: a `common-infrastructure` sub-agent, not the Supervisor — RULE: `AGENTS.md` Hard-Stop Gate 1 (still in force until this task merges).
6. Merge-gate sign-off: T341 added to `AUTHORISED_TASKS` by the Supervisor under session `[admin]` — RULE: `.claude/hooks/tests/merge_gate_guard.py:22` "**Adding a task is the record.**" (precedent T323, T326).
Checks: <filled at Stage 4>
Memory: <filled after merge>
Not done: merge (admin: after the auto verify pass); auto verify: running (T182)
Paused: auto-mode check failed — no `Memory:` line in the report — run the memory pass before you stop and record it there (each entry written, or `Memory: nothing new`); no test run in memory/event-trace/T341.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T341" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop; Risk High: decision 1 (`RULE`) is a choice — its RULE cites no written rule (`path:line`, `path § <heading>` or `docs/claude-md/tracks.md` `### <section>`) — so it must be `DEBATED` with exactly 3 Advocates named; Risk High: decision 4 (`SAFER OPTION`) is a choice — it is flagged ⚠ — so it must be `DEBATED` with exactly 3 Advocates named; Risk High: decision 5 (`RULE`) is a choice — its RULE cites no written rule (`path:line`, `path § <heading>` or `docs/claude-md/tracks.md` `### <section>`) — so it must be `DEBATED` with exactly 3 Advocates named; extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report 51f5a2a68a7d]


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
