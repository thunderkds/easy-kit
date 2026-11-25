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

## Stage 4 review (Reviewer: T353, fresh context)

Scope: `main...492c5efb` (setup.sh, lib/harness-update.sh, lib/merge-settings.py, lib/agent-ws-hooks.json, tests, site, docs). Method: code-review and security-review criteria applied inline (`skills/code-review/references/security-reviewer.md`); the Skill tool was not used.

Verification command (venv on PATH), all green:
- `bash tests/test_agent_ws_installer_t353.sh`: 33 passed, 0 failed
- `pytest tests/test_merge_settings_agent_ws_t353.py tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_match_installer.py tests/test_plugin_package.py -q`: 236 passed
- `tests/test_one_command_menu.sh` 22/0, `tests/test_cli_and_project_menus.sh` 25/0, `tests/test_settings_merge.sh` 49/0
- Extra probe (edge case): opted-in project, user deleted `scripts/agent_ws.py`, no-terminal Update: script restored, 3 entries present, lock keeps `agent_ws: on` and the script hash.

Acceptance and Success Criteria: AC 1-10 and SC 1-6 are met by code and tests (AC 1 with the D2 note below). AC 7: `hooks/hooks.json` and the kit `.claude/settings.json` are not in the diff. AC 2: SC2 diffs a pty Enter install against a no-terminal install byte for byte.

Security: no injection path found. The overlay path comes from the fetch temp dir and is quoted; the lock value is compared literally to `on`; the ownership regex is anchored and only matches the exact `"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py` form; a No answer ships nothing new. Hooks run a project-local script, the same trust level as the repo's other hooks.

### Findings

- **P2** `lib/agent-ws-hooks.json` + `setup.sh:430-435`: the three entries are written to the tracked `.claude/settings.json`, so a teammate on macOS or Windows who clones an opted-in project gets a `WorktreeCreate` hook that the script itself calls Linux only (`scripts/agent_ws.py:29`). Failure scenario: `claude --worktree` fails for that teammate if `hook-create` exits non-zero off Linux. `docs/agent-ws.md` says macOS is "untested" and Windows unsupported, and the question is asked on Linux only, but nothing here shows `hook-create` degrades. Action: confirm (or test) that `hook-create` falls back to plain `git worktree` or exits 0 off Linux, or record the risk in the guide as accepted. Not blocking: debated as D1, flagged "decided for you".
- **P3** `setup.sh:350-353` vs AC 1: on Reinstall of an opted-in project, Enter keeps Yes (D2), so "Enter means No" holds only for Install. It is documented (auto decision 7) and tested (SC6), so reword AC 1 or accept as is.
- **P3** `lib/harness-update.sh:979` (Reinstall answered n): `scripts/agent_ws.py` stays on disk but leaves the lock, so it becomes an untracked orphan the kit no longer refreshes. The log line says it is left in place. Accepted behaviour; mention it in `docs/agent-ws.md` "turn it off".
- **P3** `lib/merge-settings.py` `AGENT_WS_RE`: a user who hand-wired the exact `"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py` form (the form the docs give for this repo) loses those entries when they answer No or the script is absent. The doc's by-hand snippet in a project installed before T353 uses an absolute path, so it is unaffected. Action: none needed; optional doc sentence.
- **P3** process: the Evidence table, `Checks:`, `Memory:` and `Not done:` slots in this file and the guide's Completion and Edge-Case checklists are still unfilled, and the Test Plan's real `claude -p --worktree` run in an easy-note-mcp clone is not recorded. Supervisor to fill before verify.

Counts: P0 0, P1 0, P2 1, P3 4.

Verdict: PASS (no P0/P1; resolve or accept the P2 before merge).
