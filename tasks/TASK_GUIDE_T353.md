# TASK_GUIDE — T353: Ship agent-ws (T345) as an opt-in installer choice, and say so on the site's index page
**Date**: 2026-11-25
**Complexity Level**: C3
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Run plan — start here (written 2026-11-25)

**State:** registered 2026-11-25 under the `[admin]` session tag; extended track, C3 / High / P1; guide written, no worktree, no code. T345 is merged into local `main` (`f90c93f7`), not pushed, its row still in Ready for Review (hook close-out did not run: `tasks/TASK_REVIEW_T345.md` `Paused: done not moved`).

**Order:**
1. Active-task file first: `.claude/hooks/.state/active_task.d/<session id>` = `T353` (a Debate run before it, or before the first task-file change, is not credited: `memory/learnings.md` 2026-11-25 T345 traps).
2. Worktree `../wt-t353`, branch `feat/t353-agent-ws-installer`; row to In Progress (stage only the T353 row: another session may hold uncommitted board edits — build the change on `git show HEAD:PROJECT_KANBAN.md` and stage it with `git update-index --cacheinfo`; read the working file BEFORE opening it for write).
3. Debates (High: 3 Advocates each, through `Skill({ skill: "resolve-question", args: "task=T353 risk=High" })`): D1 below is the one of record; D2/D3 only if no written rule settles them.
4. Slices, test first (`Skill({ skill: "tdd" })`): (1) the question and its memory in the lock; (2) the script copy and its refresh on Update; (3) the hook entries per D1; (4) docs and the index page.
5. Stage 4: one fresh-context `Reviewer: T353` spawn; Supervisor `code-review` + `security-review` (the built-in cannot start: no `origin/HEAD`; review inline and say so). Stage 5: auto verify `--start T353`, then the `[admin]` merge. Fill every `Not done:` slot before verify (T345 lost its close-out to a `PENDING` placeholder).

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-25, after T345: "so for the update in another repos, we should add the option when reinstall the kit, right, by the way, let update the index page also". The Supervisor's answer, which the user accepted ("done", after restoring the board): an opt-in installer choice, default No; `scripts/agent_ws.py` reaches the project; the three hook entries are written so a later kit update can still manage them; the index page gets one line, in this ticket, because a public claim must be true for an installer the day it ships.

**Restated intent**:
> On Install and Reinstall, `setup.sh` asks one more question — turn on agent-ws (separate worktrees and RAM build folders for parallel agents)? `[y/N]`, default No, and No with no terminal. A yes copies `scripts/agent_ws.py` into the project and registers its three Claude Code hooks (`WorktreeCreate`, `WorktreeRemove`, `SessionStart`) for that project. The answer is remembered: Update asks nothing and keeps the project's choice, refreshing the script like any kit file. A project that said No gets nothing new, byte for byte. `site/index.html` says the choice exists, within its 300-word cap; `site/docs.html` `#install` describes it.

**Out of scope**: turning agent-ws on for plugin users (the plugin's `hooks/hooks.json` stays at its 15 hooks); Windows/macOS support of agent-ws itself (Linux only, T345); a flag (`setup.sh` takes no options, `setup.sh:36-43`); turning agent-ws off from the menu (record as follow-up unless D1's option makes it free).

**Requirement Refs**: `docs/prd/PRD_agent-ws.md` FR-001 (extend with FR-002: the installer choice) at run step 3.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — auto (Supervisor), `[admin]` session tag, 2026-11-25 (`docs/claude-md/tracks.md` `### Every user stop and its auto rule`, row 13)
- [ ] Domain terms align with the `PROJECT_SPEC.md` glossary — add *Opt-in kit file* if D1 creates one
- [x] Every Acceptance Criterion traces to a line of the Requirement
- [ ] `docs/prd/PRD_agent-ws.md` FR-002 added and covered
- [ ] D1 decided (Debate of record)

---

## Facts found before planning (Explore, 2026-11-25; cite these, do not re-derive)

- **Questions:** `choose_action` `setup.sh:601-645` → `prompt_clis` `:260-303` → `prompt_mode` `:307-328` → plan → `confirm_plan` `:650-672` → files → `offer_board_mode` `:793-810` (asked AFTER writes). Every prompt reads `/dev/tty` (`tty_probe`/`tty_read` `:207-220`); no terminal = each default. Rule: every prompt comes before any write (`setup.sh:823-825`), so ask right after `prompt_mode` (`:854` Install, `:859` Reinstall), add a plan line beside "Hooks:" (`setup.sh:759`, `lib/harness-update.sh:723,755`), and apply inside `run_install` / `run_reinstall` / `run_update`.
- **Memory:** a new lock key must be written by BOTH `write_harness_lock` (`setup.sh:458-464`) and `write_new_lock` (`lib/harness-update.sh:525-532`), or the next Update drops it; read with `lookup_lock_field` (`lib/harness-update.sh:84-87`).
- **Shipping one file only on opt-in:** no precedent in `MANIFEST` (every listed path ships to all). Model: `process_claude_md` (`lib/harness-update.sh:379+`) runs a non-MANIFEST file through `process_one_file`, driven by a lock field — copy that for `scripts/agent_ws.py`. Its import `scripts/cleanup_task.py` already ships (`MANIFEST:52`).
- **Hook entries and the merge:** `lib/merge-settings.py` owns an entry only when a command names `.claude/hooks/…` (`:56,64-77`); an owned entry the kit's `.claude/settings.json` does not list is DROPPED on every Install/Update (`:100-106`). An entry naming `scripts/agent_ws.py` is a user entry: never changed, never removed, never checked (`tests/test_settings_merge.sh` SC2).
- **Pins:** `tests/test_plugin_package.py:21,41-45` (kit settings = plugin hooks, 15, each a `/.claude/hooks/<x>.py`); `tests/test_plugin_source.py:72-76` (a plugin link for every `.claude/hooks/*.py`); `tests/test_one_command_menu.sh` (fixed answer strings `:77,98,126,197` — Enter must mean No, keep spare newlines); `tests/test_cli_and_project_menus.sh` (answer order comment `:73`); `tests/test_docs_match_installer.py` (no flags in docs or installer output; never "harness" in output `:103-109`); `tests/test_board_init.py:242-335` (how to test an `offer_*` function by `sed`-extracting it).
- **Index page:** `tests/test_site_story.py` — sections fixed `["hero","journey","stages","paths","stops","deeper"]` (`:37`); `WORD_CAP = 300` visible words and today's count is exactly 300 (`:38,255-257`): every added word must replace one; `BANNED_TERMS` (`:44-47`) include **`worktree`**, `harness`, `Risk`, `Stage` (outside `#stages`); no task ID; `#deeper` holds exactly 4 cards plus one `story-note` (`:371-384`): put the line in a second `story-note` or in an existing sentence. `docs.html` rules: `tests/test_site_content.py` (lead ≤35 words, cell ≤25 outside `<details>`, no task ID), `tests/test_site_visual_first.py` (`#install` ≤150 words on first load; put detail inside `<details class="more">`, `docs.html:544-553`), `tests/test_site_story.py:540-601` (baseline hashes: a changed docs.html paragraph needs a `CHANGED_BY_T353` entry).

---

## Decisions to make (run step 3)

- **D1 (Debate of record) — who owns the three hook entries in an opted-in project?** (a) user-owned: commands name `"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py`; they survive every update, but the kit can never fix or remove them (turning off = delete by hand). (b) `.claude/settings.local.json`: per user, usually untracked — not "for the project". (c) kit-owned: thin `.claude/hooks/agent_ws_*.py` wrappers plus a `merge-settings.py` rule that keeps an opted-in entry (e.g. an extra upstream file passed only when the lock says on); the wrappers then ship to every project as inert files and need plugin links (`tests/test_plugin_source.py:72-76`).
- **D2 — Reinstall default:** does Reinstall pre-select the remembered answer, or default No like `prompt_mode` (which always defaults to 1)?
- **D3 — Update on a project that said Yes, when the user edited `scripts/agent_ws.py`:** same edit-safe path as other kit files (`process_one_file`), so yes by rule — confirm no new prompt.

---

## Draft text (user-reviewed 2026-11-25)

`docs.html#parallel-builds` — **Parallel builds**. Lead: "Run several agents on one Rust repo without freezing your computer. Each agent gets its own copy of the repo and its own build folder in memory."
1. **Turn it on.** Run the install command, choose **Reinstall**, and answer `y` to *Turn on parallel builds?* Linux only.
2. **Work as usual.** `claude --worktree <name>`, or an agent started in its own copy, lands in `../wt-<name>` beside your repo.
3. **Run heavy commands through it.** `python3 scripts/agent_ws.py run -- cargo test` runs at low priority, in that copy's own build folder.
4. **Clean up.** `python3 scripts/agent_ws.py gc` removes copies whose session has ended. It never removes unmerged or unsaved work.
More (`<details class="more">`): `rm <name>` removes one copy now; `gc --dry-run` shows what it would remove and how much memory the build folders use; a restart empties the build folders, so the next build starts from scratch; each new copy needs 4 GB free in memory, else it builds on disk; `AGENT_BUILD_SLOTS=N` lets at most N heavy commands run at once (off by default); to turn it off, Reinstall and answer `n` (if D1 makes "off" possible; else say how to remove the three entries).

The installer question text follows the draft: `Turn on parallel builds (agent-ws)? [y/N]`.

## Dependencies & Reachability

**Depends on**: T345 — `scripts/agent_ws.py` (merged into local `main` `f90c93f7`)

**Entry point**: `offer_agent_ws`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Install and Reinstall ask the agent-ws question once, after the project-type question and before `Proceed?`; Enter, `n`, anything but `y`/`yes`, or no terminal means No | "add the option when reinstall the kit" |
| 2 | With No, the project's files, `.claude/settings.json` and lock are byte-identical to an install of the same kit commit today (no `agent_ws` key, no script) | opt-in |
| 3 | With Yes, `scripts/agent_ws.py` is a real file in the project, recorded in the lock with its hash, and the three hook entries are registered per D1 | ships the tool |
| 4 | The lock remembers the answer; Update asks no agent-ws question and keeps the choice; with Yes, Update refreshes `scripts/agent_ws.py` by the edit-safe rules of other kit files | "for the update in another repos" |
| 5 | After Install-with-Yes then Update, the three hook entries are still present exactly once (no duplicate, not dropped by `merge-settings.py`) | merge survival |
| 6 | The plan screen names the choice (one line beside "Hooks:") before `Proceed?` | plan before write |
| 7 | `hooks/hooks.json` and the kit's `.claude/settings.json` are unchanged; `tests/test_plugin_package.py` still passes at 15 | out of scope: plugin |
| 8 | `site/index.html` `#deeper` note reads "Pick parallel agent builds at install, or try the Settings tool." ("parallel agent builds" links to `docs.html#parallel-builds`), and the Add-ons card drops "Optional" to stay at 300 words; `tests/test_site_story.py` passes (300-word cap, no banned term) | "update the index page also" |
| 9 | `site/docs.html` gains a how-to section `#parallel-builds` (user, 2026-11-25: "don't see the detail to guide the users using this build"): a lead of 35 words or fewer, 4 numbered steps (turn it on at Reinstall; work as usual with `claude --worktree`; `agent_ws.py run -- cargo test`; `agent_ws.py gc`), and a `<details class="more">` block (`rm`, `gc --dry-run`, reboot empties the build folders, the 4 GB check, `AGENT_BUILD_SLOTS`, turning it off). Draft text: `## Draft text (user-reviewed 2026-11-25)` below. `#install` names the new question in one line. The pinned section-id list (`tests/test_site_story.py:483-487`) and the sidebar groups (`tests/test_site_content.py:1947-1961`) gain `parallel-builds`; `tests/test_site_content.py`, `tests/test_site_visual_first.py`, `tests/test_docs_match_installer.py` pass | docs ride with code; user follow-up |
| 10 | `docs/agent-ws.md` says how the installer turns it on, and keeps the by-hand snippet for projects installed before | docs ride with code |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | no terminal, fresh git repo, `setup.sh` | no agent-ws question asked; no `scripts/agent_ws.py`; lock has no `agent_ws` key | automated (shell test) |
| 2 | pty, Install, answers Enter at the new question | as SC 1, and the other menus behave as today (`tests/test_one_command_menu.sh` green) | automated |
| 3 | pty, Install, `y` | `scripts/agent_ws.py` present and in the lock; three hook entries in the chosen settings file | automated |
| 4 | SC 3's project, then Update | no question; script refreshed; entries present once | automated |
| 5 | SC 3's project with `scripts/agent_ws.py` edited, then Update | the edit is kept by the same rule as any edited kit file | automated |
| 6 | `python3 -m pytest tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_match_installer.py tests/test_plugin_package.py -q` | all pass | automated |

### Verification Command (exact, runnable)

```bash
bash tests/test_agent_ws_installer_t353.sh && python3 -m pytest tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_match_installer.py tests/test_plugin_package.py -q && bash tests/test_one_command_menu.sh && bash tests/test_cli_and_project_menus.sh && bash tests/test_settings_merge.sh
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T353.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T353.md`. Capture BEFORE (`setup.sh` in a pty on a fresh repo: the question list as today) before the first implementation commit.

---

## UI / Design Acceptance Criteria

Text-only change to two existing pages: same classes, no new component or style. Visual regression, design-system compliance and responsiveness rows: ☐ N/A with that reason, unless the index line needs a new element (then run `Skill({ skill: "ux-evaluate" })` at 375 px and 1280 px).

---

## Approach

**Pattern reference**: `offer_board_mode` (`setup.sh:787-810`) for the prompt shape; `process_claude_md` (`lib/harness-update.sh:379+`) for a lock-driven non-MANIFEST file.

**Vital slice**: one y/N question, the lock key, the script copy/refresh, the hook entries per D1, one index line, one docs block.
**Cut list**:
- Turning agent-ws off from the menu (follow-up, unless D1 (c) makes it free).
- Plugin opt-in.
- A Codex equivalent (Codex has no hooks).

---

## Edge Case Checklist

- [ ] No terminal: never asks, always No
- [ ] A project that already wired the hooks by hand (`docs/agent-ws.md` snippet in `settings.local.json`): Yes must not add a second set
- [ ] Reinstall over a Yes project: D2
- [ ] Update of a Yes project whose `scripts/agent_ws.py` the user deleted
- [ ] `setup.sh` Cancel after the new question: nothing written
- [ ] A non-Linux machine answering Yes: say agent-ws is Linux-only, still write nothing broken (a `WorktreeCreate` hook that fails breaks `claude --worktree`)
- [ ] Pin-test pre-flight: grep `tests/` for the installer answer strings and the plan screen text before the first edit

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `setup.sh` | `offer_agent_ws` after `prompt_mode`; plan line; lock key in `write_harness_lock`; apply in `run_install` |
| `lib/harness-update.sh` | lock key in `write_new_lock`; Update/Reinstall apply and refresh (like `process_claude_md`) |
| `lib/merge-settings.py` | only if D1 = (c) |
| `.claude/hooks/agent_ws_*.py` + `plugin/.claude/hooks/` links | only if D1 = (c) |
| `tests/test_agent_ws_installer_t353.sh` (new) | SC 1–5 |
| `tests/test_one_command_menu.sh`, `tests/test_cli_and_project_menus.sh` | answer strings only if the new prompt shifts them |
| `site/index.html`, `site/docs.html`, `tests/test_site_story.py` (`CHANGED_BY_T353`) | AC 8–9 |
| `docs/agent-ws.md`, `docs/prd/PRD_agent-ws.md` | AC 10, FR-002 |
| Pre-existing pin tests | fill at run step 4 |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `hooks/hooks.json`, the kit's `.claude/settings.json` hook list | AC 7: the plugin stays at 15 hooks |
| `scripts/cleanup_task.py` | T327 behaviour |
| `.claude/skills`, `.claude/agents` symlinks | load-bearing relative symlinks |

---

## Test Plan

A pty shell test (`tests/test_agent_ws_installer_t353.sh`, modelled on `tests/test_one_command_menu.sh` and `tests/test_setup.sh`) for SC 1–5 in temp git repos; the existing installer, merge, plugin and site suites for no regression; one real Install-with-Yes into a `git clone --local` of `easy-note-mcp`, then `claude -p --worktree` there (haiku) to show the hooks fire.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run (inline if the built-in cannot start)
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T353.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated
- [ ] Board current

---

## Questions Log

- 2026-11-25 DEBATE (`resolve-question task=T353 risk=High`) D1: who owns the three hook entries in an opted-in project? → kit-owned without wrappers: `lib/merge-settings.py` also owns the exact `"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py` form, and the installer passes `lib/agent-ws-hooks.json` as an overlay only when the lock says `agent_ws` on (Advocate 1: same — Reinstall `n` turns it off free, `drop_dangling` guards a missing script; Advocate 2: same — anchored rule, overlay outside the 15-hook settings; Advocate 3: (b) `.claude/settings.local.json`, add-only, gitignored — a tracked entry reaches teammates on non-Linux). Settled by a written line, not a stop (`docs/claude-md/tracks.md:568`): `tasks/TASK_GUIDE_T353.md:38` "the three hook entries are written so a later kit update can still manage them" and AC 5 (entries survive Update exactly once): the merge never reads `settings.local.json`, so (b) cannot meet them (Decide rule 1). Advocate 3's teammate risk is guarded in code: the question is asked only on Linux, and agent-ws falls back to an on-disk build folder on macOS ⚠ decided for you — please review
