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
1. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High: changes a safety hook; C2).
2. Split the user's "[admin] has all rights" change into T342 (this hook fix, no shared file with T341) and T343 (merge-gate binding of every task the session started + `### Stops that stay` list; waits for T341, which edits `.claude/hooks/pre_bash_block_unsafe_merge.py` and `docs/claude-md/tracks.md` now) — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task").
3. Fix shape: A, default direction "expand" — a glob in a quoted span is not expanded only when the span's segment command is on a short allowlist of commands that neither glob nor run a shell (`grep`/`egrep`/`fgrep`/`rg`, `sed` without an `e` command, `sort`, `cut`, `tr`); every other quoted span (unknown wrappers such as `su -c`, `xargs`, `watch`, self-globbing `git`/`rsync`/`tar`) still expands; literal checks of every token stay; `sed`/`awk` stay out of `DATA_COMMAND_PATTERN` — DEBATED: A (Advocate 1: A, skip only for known non-executing commands so an unknown wrapper still expands; Advocate 2: A, keyed on `SPAN_EXECUTOR_PATTERN`, plus expand for self-globbing `git`/`rsync`/`tar`; Advocate 3: A, keyed on the segment's command, skip only for a short known list) — all three reject B (`cd .cl*` lands in `.claude` and stops being caught) and C (`sed e`/`w`, `awk system()` execute). The direction split is settled by RULE: `.claude/hooks/lib/shell_data.py:384` "Unknown must resolve toward **code**".
4. No `[admin]` bypass of the sensitive-path hook; a planned path is already silent in every mode (guide `## Files to Change (Predicted)`) — RULE: `.claude/hooks/pre_tool_sensitive_path.py:7` "unless the active task's guide predicted that exact path".
5. Implementer: a `common-infrastructure` sub-agent, not the Supervisor — RULE: `AGENTS.md:171` "The Supervisor must never write implementation code directly." (Hard-Stop Gate 1; T341 has not merged).
Checks: <filled at Stage 4>
Memory: <filled after merge>
Not done: merge (admin: after the auto verify pass); auto verify: <filled at Ready for Review>
Paused: auto-mode check failed — no `Memory:` line in the report — run the memory pass before you stop and record it there (each entry written, or `Memory: nothing new`); no test run in memory/event-trace/T342.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T342" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop; extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report 2d2e8c5a2443]

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
