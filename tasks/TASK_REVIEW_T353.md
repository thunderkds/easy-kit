# TASK_REVIEW — T353: Ship agent-ws (T345) as an opt-in installer choice, and say so on the site's index page

> Sibling of `tasks/TASK_GUIDE_T353.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Sign the Requirement Fidelity Gate myself — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13: the Gate is signed `auto (Supervisor)`)
2. FR-002 goes in `docs/prd/PRD_agent-ws.md` beside T345's FR-001 — FACT: PROJECT_SPEC.md:31 "the kit has per-feature PRDs in `docs/prd/`, no single PRD"
3. Ask the question right after the project-type question, before the plan and `Proceed?` — RULE: setup.sh:823-825 "Every prompt below comes BEFORE any write to the project, so Cancel (or Ctrl-C) leaves it untouched."
4. The answer lives in a new lock key `agent_ws`, written only on yes, so a No install stays byte-identical — RULE: tasks/TASK_GUIDE_T353.md § Acceptance Criteria, AC 2 ("With No, the project's files, `.claude/settings.json` and lock are byte-identical to an install of the same kit commit today")
5. D1: the three hook entries are kit-owned without wrappers (`lib/merge-settings.py` owns the exact `"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py` form; overlay `lib/agent-ws-hooks.json` passed only when opted in) — DEBATED: (c) narrow rule (Advocate 1: (c) narrow rule + overlay, off comes free; Advocate 2: (c) narrow rule + overlay, `drop_dangling` checks the real script; Advocate 3: (b) `.claude/settings.local.json`, nothing reaches teammates). Split settled by `tasks/TASK_GUIDE_T353.md:38` "the three hook entries are written so a later kit update can still manage them" (Decide rule 1; `docs/claude-md/tracks.md:568`) ⚠ decided for you — please review
6. Ask the agent-ws question only on Linux (`uname -s` = `Linux`), so no one registers a hook agent-ws cannot run — FACT: scripts/agent_ws.py:29 "Exit 0: done. Exit 1: refused or failed. Linux only (`/proc`, `flock`)."
7. D2: Reinstall pre-selects the project's current answer (`[Y/n]` when on), as it does for CLIs; no terminal keeps it — RULE: setup.sh:225 "Reinstall pre-selects what the project already has instead,"
8. D3: a user's edit of `scripts/agent_ws.py` survives Update by the same edit-safe path as every kit file (`process_one_file`), with no new prompt — RULE: tasks/TASK_GUIDE_T353.md § Acceptance Criteria, AC 4 ("refreshes `scripts/agent_ws.py` by the edit-safe rules of other kit files")
9. The `#parallel-builds` id is left out of the index page's redirect list, as `#changelog` was: no old story-page link targeted it — RULE: tests/test_site_story.py:625 "T344: #changelog is new on docs.html; no old link on the story page ever targeted it"
Checks: (filled at the end)
Memory: (filled at the end)
Not done: merge (admin: after the auto verify pass); auto verify: (filled at the end)
Paused: auto-mode check failed — no test run in memory/event-trace/T353.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T353" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop; Risk High, but no decision was DEBATED with 3 Advocates; extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report ea28300862ce]
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report 0ad4148d9826]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | |
| Verification command run | ☐ pass / ☐ fail | |
| Negative cases hold | ☐ pass / ☐ fail | |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | |

---

## Demonstration

**BEFORE**:

**AFTER**:

**DELTA**:

**WITNESS**:
