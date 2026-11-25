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
10. `tests/test_agent_ws_installer_t353.sh` gets its own CI step — RULE: tests/test_ci_wires_shell_suites.py:5 "every tests/*.sh file must be either wired as its own `run:` step in"
11. Reviewer round 1 (`492c5efb`, PASS, 0 P0/P1): P2 answered with a test, not a code change (`tests/test_agent_ws_no_proc_t353.py`: with `/proc` hidden, `hook-create` still makes the worktree and prints its path; builds on disk); P3s fixed: AC 1 names the Reinstall default, turning off says the script stays as the user's file; P3 "exact-form hand entries in a No project are dropped" accepted (documented); a second Reviewer round on `864415b7` — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4: Review ("A later code fix needs a new reviewer spawn on the new commit")
12. Reviewer round 2 (`864415b7`, PASS, 0 P0/P1/P2): its 2 P3s are left unfixed — the guide's checklist boxes and a `docs/agent-ws.md` sentence that on macOS `gc` sees every owner as gone (clean, merged worktrees of a live session can be removed; no work is lost). Either edit is outside the files allowed after the reviewed commit, so a fix would need a third Reviewer round — RULE: `skills/code-review/SKILL.md` § Phase 4 — Apply Safe Fixes ("Present P2/P3 fixes as suggestions only")
Checks: tests `bash tests/test_agent_ws_installer_t353.sh` — 33 passed, 0 failed; `python3 -m pytest tests/test_merge_settings_agent_ws_t353.py tests/test_agent_ws_no_proc_t353.py` — 9 passed; installer suites `test_one_command_menu.sh` 22/0, `test_cli_and_project_menus.sh` 25/0, `test_settings_merge.sh` 49/0, `test_setup.sh` 21/0, `test_update.sh` 38/0, `test_install_update_smoke.sh` 9/0, `test_install_backups.sh` 18/0, `test_update_removals.sh` 34/0, `test_harness_projection.sh` 41/0, `test_t098_harness_presence.sh` 20/0, `test_update_claude_md.sh` 52/0; site tests 238 passed; `shellcheck -x setup.sh update.sh lib/harness-update.sh …` rc=0; full suite 60 failed / 7795 passed, every failure also fails on `main` or passes alone (3 checked, see Evidence); reviews: Supervisor `code-review` 0 P0/P1, 3 P2 fixed (`4b7cc9cc`); security review inline (built-in needs `origin/HEAD`): 0 findings above P3; Reviewer: T353 round 1 PASS (1 P2, 4 P3); real run: Reinstall with `y` into a `git clone --local` of `easy-note-mcp`, then `claude -p --worktree live353` (haiku, `--setting-sources project`) printed `/home/thunderkds/workspace/pets/t353-live/wt-live353`, `AGENT_WS_BIN=…/wt-live353/scripts/agent_ws.py` and `target-dir = "/dev/shm/agent-ws-1000/repo-09b2a9e9/live353-4cc61d"`; `agent_ws.py gc` then refused it (`M memory/event-trace/_untagged.jsonl`, tracked in that repo) (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T353: agent-ws is an opt-in installer choice; `memory/learnings.md` — 2026-11-25 T353 traps (a write that empties the file first; gate-safe loops; pty.sh hides claude; easy-note-mcp's tracked event-trace blocks gc; staging only your board row). `memory/MEMORY.md` not touched: over its budget, a `/compact-memory` job
Merged: `main` (`git merge --no-ff feat/t353-agent-ws-installer`, [admin], after the auto verify pass); post-merge on `main`: `bash tests/test_agent_ws_installer_t353.sh` `33 passed, 0 failed`, `bash tests/test_readme_current.sh` `ALL PASS`; `python3 scripts/cleanup_task.py T353` removed the worktree and the merged branch. `release-plan` waits for the push of `main` (`docs/claude-md/tracks.md` `### Admin tag`: it runs after the merge and the push).
Not done: merge (admin: after the auto verify pass) — done, see `Merged:`; push (yours: no `origin` remote, `git push github main`); T345 to Done (yours); `easy-note-mcp`: untrack `memory/event-trace/` so `gc` can clean its worktrees (yours, another repo); auto verify: ☑ pass (session 926a0dc0-89cd-4a92-8c42-d97aabdd1655, commit b65bb0af65d791f89649e3df885f7a6c6da70cab, log .claude/verify-runs/T353-b65bb0af65d7.log)
Paused: auto-mode check failed — no test run in memory/event-trace/T353.jsonl — write /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID with the task ID (minimal-track step 1): `mkdir -p /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d && printf '%s\n%s\n' "T353" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/thunderkds/workspace/pets/hungnguyen111/easy-kit/.claude/hooks/.state/active_task.d/$CLAUDE_CODE_SESSION_ID`, then rerun the task's tests so the trace records them under the task, then stop; Risk High, but no decision was DEBATED with 3 Advocates; extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report ea28300862ce]
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report 0ad4148d9826]
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report de9002c13728]
Closed: row moved to Done 2026-11-25 — auto verify pass (session 926a0dc0-89cd-4a92-8c42-d97aabdd1655, commit b65bb0af65d791f89649e3df885f7a6c6da70cab); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_agent_ws_installer_t353.sh` (33 checks: SC 1–9: no terminal, Enter = No byte-identical, y, Update keeps + refreshes, user edit kept, Reinstall default/off/no spurious backup, plan line, not Linux, hand-wired warning) — `--- 33 passed, 0 failed ---`; `tests/test_merge_settings_agent_ws_t353.py` (8: overlay once, idempotent, off drops, kit SessionStart kept, hand-wired kept, `.bak` path not taken, missing script dropped, 3/4-arg and bad overlay) + `tests/test_agent_ws_no_proc_t353.py` (1) — `9 passed` |
| Verification command run | ☑ pass | guide `### Verification Command`: installer `33 passed, 0 failed`; pytest set `236 passed` (Reviewer run); `test_one_command_menu.sh` `22 passed, 0 failed`; `test_cli_and_project_menus.sh` `25 passed, 0 failed`; `test_settings_merge.sh` `49 passed, 0 failed` |
| Negative cases hold | ☑ pass | red first: merge tests `5 failed, 3 passed` before `acaa5ebf` (the 3 are the stay-the-user's guards); installer test `16 passed, 15 failed` before `9814e0af`; SC6 backup check `32 passed, 1 failed` before `4b7cc9cc`. Vacuous pass found and noted: SC5 "edit is kept" passed before the script existed (`printf >>` created the file); meaningful after `9814e0af` |
| verify | ☑ pass | auto-run by hook, session 926a0dc0-89cd-4a92-8c42-d97aabdd1655, commit b65bb0af65d791f89649e3df885f7a6c6da70cab, log .claude/verify-runs/T353-b65bb0af65d7.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff --stat main...HEAD`: installer (`setup.sh`, `lib/harness-update.sh`, `lib/merge-settings.py`, `lib/agent-ws-hooks.json`), their tests, 2 pinned menu/site tests, `site/`, `docs/`, `README.md` (1 line, still 75), `ci.yml` (1 step). Callers: `update.sh` (thin alias, `EASYKIT_ACTION=update`), every installer suite run. `lane_check.py`: `lane: C3, 14 files, 519 lines, FITS` |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression. `python3 -m pytest tests/ .claude/hooks/tests/ -q`: `60 failed, 7795 passed, 24 skipped`. Against the `main` run of the same session: only-in-T353 = 3: `test_ci_wires_shell_suites.py` (real: fixed in `492c5efb`), `test_auto_verify_skip_pass.py::test_ac5_a_missing_base_ref_is_not_a_skip_pass` and `test_auto_verify.py::test_ac4_blocked_row_never_says_pass[bypass-subtype]` (pass alone: `10 passed` three times). The other 57 fail on `main` too (`test_stop_attribution_t287.py` 25, `test_slot2b_brace_glob.py` 19, …). `test_readme_current.sh` fails on this branch and passes on `main` after T347 (`da038f57`), which this branch predates |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | text only: one new docs section built from existing elements (`h2`, `p.lead`, `ol.lead`, `details.more`), one index note reworded, same classes |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no new class, style or token; `tests/test_site_content.py` + `tests/test_site_story.py` + `tests/test_site_visual_first.py` pass (238) |
| **UI: Responsiveness at target viewports** | ☑ N/A | no layout change; index stays at its 300-word cap |

---

## Demonstration

**BEFORE** (2026-11-25T04:44:02Z, `setup.sh` from this branch before any implementation commit, in a pty on a fresh repo, Enter at every prompt): prompts `Choose [1]` (action), `Which CLIs…`, `Is this a new or an existing project?`, `Proceed? [Y/n]`, `Use an online board (Linear) for tasks? [y/N]`; `scripts/agent_ws.py: absent`; `lock agent_ws key: 0`.

**AFTER**: the same prompts plus `Turn on parallel builds (agent-ws)? [y/N]` after the project type and the plan line `- agent-ws: on (scripts/agent_ws.py and its 3 hooks: …)`; with `y`: `scripts/agent_ws.py` present, `"agent_ws": "on"`, 3 entries. Live: Reinstall + `y` in an `easy-note-mcp` clone, then `claude -p --worktree live353` printed `/home/thunderkds/workspace/pets/t353-live/wt-live353` with `target-dir = "/dev/shm/agent-ws-1000/repo-09b2a9e9/live353-4cc61d"`.

**DELTA**: any Easy Kit project on Linux turns on agent-ws with one `y` at Install or Reinstall, keeps it through Update, and turns it off with `n`; `docs.html#parallel-builds` tells users how to use it.

**WITNESS**: Supervisor session 7b4187fe, 2026-11-25 (BEFORE, red runs, live run); `Reviewer: T353` (fresh context) round 1 confirmed the verification command at `492c5efb`

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

### Round 2 (Reviewer: T353, commit 864415b7)

Scope: `main...864415b7`, plus `git diff 864415b7 HEAD` (only `memory/` and this record). Method: code-review and security-review criteria applied inline (`skills/code-review/references/security-reviewer.md`); the Skill tool was not used.

Verification (venv first on PATH):
- `bash tests/test_agent_ws_installer_t353.sh`: `--- 33 passed, 0 failed ---`
- `python3 -m pytest tests/test_merge_settings_agent_ws_t353.py tests/test_agent_ws_no_proc_t353.py tests/test_site_story.py tests/test_site_content.py -q`: `207 passed in 0.94s`

Round 1 findings:
- **P2** hook-create on a machine with no /proc: FIXED, with a caveat. `tests/test_agent_ws_no_proc_t353.py` hides `/proc` in-process; `hook-create` returns 0, prints `../wt-mac1` as its last stdout line, the worktree exists, stderr says `on-disk target/`; `hook-remove` then removes it. It reads the code truthfully (`scripts/agent_ws.py:127-150` return None/"" on OSError; `fcntl` is available on macOS). It simulates /proc, it does not run on macOS.
- **P3** AC 1 wording: FIXED (`tasks/TASK_GUIDE_T353.md:99` names the Reinstall default).
- **P3** turning off leaves the script: FIXED in `docs/agent-ws.md:7-12` and `site/docs.html:3381` ("stays as your own file").
- **P3** exact-form hand entries dropped on No: ANSWERED (accepted, record decision 11).
- **P3** unfilled record slots: PARTLY OPEN. The record's Evidence, Checks, Memory, Not done and the real `claude -p --worktree` run are now filled. The guide's Fidelity Gate boxes (domain terms, FR-002, D1 decided), Edge Case Checklist and Completion Checklist at `tasks/TASK_GUIDE_T353.md:50,52,53,163-169,205-210` are still `[ ]`.

Whole-diff re-review: no new code in 864415b7 beyond one test and wording. Security unchanged from round 1: no injection path, overlay path quoted, anchored ownership regex, lock value compared literally to `on`, a No answer ships nothing new. The test uses a tmp repo and in-process patches only.

### Findings

- **P3** `scripts/agent_ws.py:127-150,163-165` with `tests/test_agent_ws_no_proc_t353.py:55`: without /proc `owner_alive` is always False, so on macOS every lease reads as an ended session. Failure scenario: a macOS teammate runs `agent_ws.py gc` (or `hook-remove`) while another session is live, and a clean, merged worktree under that live session is removed. The unmerged/unsaved guards still hold, so no work is lost. The test comment ("no process check without /proc, but the rest still guards") says this; `docs/agent-ws.md` calls macOS untested. Action: optional one sentence in `docs/agent-ws.md` that off Linux `gc` cannot tell a live session from an ended one.
- **P3** `tasks/TASK_REVIEW_T353.md` (`Paused:` lines, record top) and `tasks/TASK_GUIDE_T353.md` checklists (see above): stale auto-mode "Paused" notes about a missing `code-review`/`security-review` Skill call, and unchecked guide boxes. Action: Supervisor ticks the guide boxes and clears or answers the Paused lines before verify. Not a code defect.

Counts: P0 0, P1 0, P2 0, P3 2.

Verdict: PASS (round 1 P2 fixed, no open P0/P1/P2).
