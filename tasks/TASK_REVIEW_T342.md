# TASK_REVIEW — T342: a glob inside a quoted span is not a path (sensitive-path hook false positive)

> Sibling of `tasks/TASK_GUIDE_T342.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Auto decisions

Mode: auto
1. Track extended — RULE: `docs/claude-md/tracks.md` `## Track rule` (Risk High: changes a safety hook; C2).
2. Split the user's "[admin] has all rights" change into T342 (this hook fix, no shared file with T341) and T343 (merge-gate binding of every task the session started + `### Stops that stay` list; waits for T341, which edits `.claude/hooks/pre_bash_block_unsafe_merge.py` and `docs/claude-md/tracks.md` now) — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task").
3. Fix shape: no glob expansion for a token from a quoted span unless the span runs in a shell (`SPAN_EXECUTOR_PATTERN`); literal checks of every token stay; `sed` stays a code command — FACT: `docs/claude-md/tracks.md:355` "a `*`, `?` or `[` outside quotes (a glob)" and `.claude/hooks/pre_tool_sensitive_path.py:261` "A token carrying glob characters is expanded against the filesystem the way the shell would".
4. No `[admin]` bypass of the sensitive-path hook; a planned path is already silent in every mode (guide `## Files to Change (Predicted)`) — RULE: `.claude/hooks/pre_tool_sensitive_path.py:7` "unless the active task's guide predicted that exact path".
5. Implementer: a `common-infrastructure` sub-agent, not the Supervisor — RULE: `AGENTS.md` Hard-Stop Gate 1 (T341 has not merged).
Checks: <filled at Stage 4>
Memory: <filled after merge>
Not done: merge (admin: after the auto verify pass); auto verify: <filled at Ready for Review>

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

**BEFORE**:
```
captured 2026-11-20T15:46:14 hook at <kit> HEAD 62b45ec
$ cd <tmp>/wt; uv run --with pytest python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider -n0 2>/dev/null | grep -E "^FAILED|passed|failed" | sed 's/ - .*//' > <tmp>/branch.txt; tail -1 <tmp>/branch.txt
-> {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Bash call touches a sensitive path: <kit>/.claude/ (pattern `.claude/st
$ cd <tmp>/wt; pytest x > /tmp/a.txt
-> (no output: allow)
```

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
