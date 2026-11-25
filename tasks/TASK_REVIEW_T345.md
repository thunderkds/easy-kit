# TASK_REVIEW — T345: Shared build base for multi-agent, multi-session work (`agent-ws`), Phase 0–1

> Sibling of `tasks/TASK_GUIDE_T345.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Close the Fidelity Gate's two bookkeeping boxes myself (glossary rows *Lease*, *Build slot*, *Build folder (tmpfs)*, *Base worktree*; PRD FR) — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13: the Gate is signed `auto (Supervisor)`)
2. The FR goes in a new `docs/prd/PRD_agent-ws.md`, not a root `PRD.md` — FACT: PROJECT_SPEC.md:31 "the kit has per-feature PRDs in `docs/prd/`, no single PRD"
3. Hook registrations stay out of every shipped file: handlers are `agent_ws.py hook-create` / `hook-remove` / `hook-env`, registered only in a project's untracked `.claude/settings.local.json`; no file under `.claude/hooks/`, no change to `.claude/settings.json`, `hooks/hooks.json` or `MANIFEST` — DEBATED: option C (Advocate 1: C — `tests/test_plugin_source.py:73` and `lib/merge-settings.py:13-17`; Advocate 2: ship `agent_ws.py` plus `.claude/hooks/` wrappers as dormant `MANIFEST` files, register nothing (T125, `tests/test_plugin_package.py:21,44-45`); Advocate 3: C, nothing shipped, `MANIFEST:46` ships `.claude/hooks` whole). The rerun of record (`resolve-question task=T345 risk=High`); the first run is not credited (no Skill call, before the work window). Split settled by written rules, so not a stop (`docs/claude-md/tracks.md:568`): `tasks/TASK_GUIDE_T345.md:106` "D2 — board scope: this board" and `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes); T125's rule binds only when a caller of the script ships ⚠ decided for you — please review
4. This repo's own `.claude/settings.local.json` is not written: the live run uses a scratch repo's local settings, and the snippet is in `docs/agent-ws.md` for you — RULE: `docs/claude-md/tracks.md` `### Admin tag` ("The only hand-backs left under `[admin]` are … the settings changes of row 5")
5. `docs/claude-md/pipeline-stages.md` is not edited: it ships to every install (MANIFEST line 55 `docs/claude-md`), agent-ws does not (decision 3), and `grep -n -i 'worktree add\|wt-t'` finds no worktree-creation wording in it to go stale — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task")
6. Build folder path is `<mount>/agent-ws-<uid>/<repo id>/<name>-<token>/`, one level more than AC 14's `<mount>/agent-ws-<uid>/<name>/` — RULE: tasks/TASK_GUIDE_T345.md § Edge Case Checklist ("Two repos with the same worktree name on one machine: tmpfs folder path includes a repo id"); the token keeps a crashed run's leftover folder from being reused (R5)
7. The untracked pointer file vs AC 9: the lease lists `.cargo/config.toml` with its sha256; `rm` ignores it only while byte-identical, deletes it before `git worktree remove` (never `--force`), and puts it back if that remove fails — RULE: tasks/TASK_GUIDE_T345.md § Run plan, design point "Untracked pointer file vs AC 9"
8. A repo that tracks `.cargo/config.toml` (or `.cargo/config`) keeps an on-disk `target/`: agent-ws never edits a tracked file — RULE: tasks/TASK_GUIDE_T345.md § Run plan, design point "Cargo config merging" ("the worktree file may set only `[build] target-dir`")
9. `hook-env` exports `AGENT_WS_BIN` only, never `CARGO_TARGET_DIR` — FACT: tasks/TASK_GUIDE_T345.md:141 "a SessionStart hook that writes `export X=…` to `$CLAUDE_ENV_FILE` is seen by … an Agent-tool subagent's Bash" (so a session-wide target would be shared by the subagents' worktrees: R5)
10. The lease owner is the nearest ancestor that is not a shell or wrapper (the Claude Code process), set before the first lease write — RULE: tasks/TASK_GUIDE_T345.md § Review findings, G2c ("a lease file per workspace (owner PID + session id + start time)")
11. With the queue off, `run` execs the command under `nice` (no wrapper left to kill); with the queue on, the command leads its own process group and a watcher process kills that group when the wrapper dies without saying "done" — RULE: tasks/TASK_GUIDE_T345.md § Approach, "Queue (opt-in)" ("run the command in its own process group and kill the group on wrapper exit or signal (G1c)")
12. After a reboot, `run` and `hook-env` re-create the private tmpfs chain (0700, owned, not a symlink) before cargo would make it with open permissions — RULE: tasks/TASK_GUIDE_T345.md § Decisions, D4 ("refused if it exists and is a symlink or not owned by the user")
13. The live run (run plan step 5) runs on this machine (`hostname` → `coupd`: 16 cores, git 2.34.1, `/tmp` on ext4), where `easy-note-mcp` is checked out; the re-run on the target machine `hungnguyenhuu-NUC11PAHi7` stays yours (see `Not done:`) — RULE: tasks/TASK_GUIDE_T345.md:50 "5. **Live run** (Test Plan): `claude --worktree` and one Agent `isolation: "worktree"` spawn in a scratch repo with the hooks on (AC 4, 13). Then the 3-agent lag test on a `git clone --local` copy of `easy-note-mcp`"
Checks: tests `python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q` — 57 passed; full suite `python3 -m pytest tests/ .claude/hooks/tests/ -q` in the worktree — 56 failed, 7786 passed, every one of the 56 also fails on `main` (61 failed there); reviews: Supervisor `code-review` — 0 P0, 1 P1 + 1 P2 + 2 P3 fixed (`a815b7cd`), 1 P3 left; `security-review` built-in cannot start here (`fatal: ambiguous argument 'origin/HEAD...'`, memory/learnings.md:2891), run inline against its criteria — 1 P2 fixed (`f5109b7e`), 1 P3 left; real run: `claude -p --worktree live1` (haiku, scratch repo, hooks in its `settings.local.json`) printed `/home/thunderkds/workspace/pets/t345-live/wt-live1` and `target-dir = "/dev/shm/agent-ws-1000/repo-f3a2b240/live1-e9d747"`, `AGENT_WS_BIN=…/scripts/agent_ws.py`, `CARGO_TARGET_DIR=unset`; Agent `isolation: "worktree"` printed `/home/thunderkds/workspace/pets/t345-live/wt-agent-ae9d79f248155162e` with its own tmpfs `target-dir`; `agent_ws.py gc` then removed both (exit 0); 3-agent lag test on an `easy-note-mcp` clone — tmpfs 63 s, fsync p95 80 ms / max 1110 ms; on-disk 81 s, fsync p95 466 ms / max 713 ms (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T345: `agent-ws` stays local, nothing ships; `memory/learnings.md` — 2026-11-25 T345 traps (Debate the Stop hook cannot see; Claude keeps a worktree with an untracked file; main's overwritten `CLAUDE.md` fails 2 tests; `git stash` negative check). `memory/MEMORY.md` not touched: over its budget (43,909 chars), a `/compact-memory` job
Not done: merge (admin: after the auto verify pass); auto verify: PENDING
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report c54b4e946dba]
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report c9567d477cc8]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_agent_ws_t345.py` — 57 tests: SC 1 `test_nested_run_inside_a_slot_does_not_deadlock`, SC 2 `test_daemon_left_by_a_build_does_not_keep_the_slot`, SC 3 `test_kill_9_of_the_wrapper_frees_the_slot_and_kills_the_build`, SC 4 `test_eight_concurrent_new_all_succeed`, SC 5 `test_gc_keeps_unmerged_work_of_a_dead_owner`, SC 6 `test_gc_removes_merged_clean_worktree_of_a_dead_owner`, SC 7 `test_cargo_build_lands_on_tmpfs_and_home_config_still_applies`, SC 8 `test_no_tmpfs_falls_back_to_disk_and_says_so`, SC 9 `test_rm_ignores_its_own_pointer_file_but_not_a_user_edit` + `test_rm_keeps_tmpfs_folder_when_refused`, SC 10 `test_two_worktrees_never_share_a_target_dir[True/False]`, SC 11 `test_queue_off_by_default_three_runs_overlap`; AC 4/13 hook tests `test_hook_*`; AC 9 `test_rm_refuses_and_removes_nothing[unmerged/modified/untracked/process]`; AC 12, 15–19 named tests. `57 passed in 9.70s` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q` → `57 passed in 9.70s` (scratchpad venv on `PATH`; system Python has no pytest) |
| Negative cases hold | ☑ pass | red run at `a47733cf` (before any implementation commit, tests copied in) 2026-11-25T03:53:47Z: `53 failed, 1 passed` (the 1 is `test_hook_create_failure_exits_non_zero`, which an absent script also satisfies). Mutation `scripts/agent_ws.py | 2 +-` (watcher given pgid 999999999): `test_kill_9_of_the_wrapper_frees_the_slot_and_kills_the_build` FAILED, restored. Review fixes red first: `test_rm_refuses_unmerged_commits_on_a_detached_head_after_the_branch_is_gone`, `test_rm_survives_a_pointer_file_the_user_deleted` (`2 failed`), `test_rm_never_deletes_a_build_folder_off_tmpfs_even_if_the_lease_says_so` against `a815b7cd`'s code (`1 failed`) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff --stat main...HEAD`: 7 files, all new or doc rows (`scripts/agent_ws.py`, its test, `docs/agent-ws.md`, `docs/prd/PRD_agent-ws.md`, 4 glossary rows, guide, this file). Only caller-side dependency: `import cleanup_task` (`scripts/cleanup_task.py`, read, not edited). No shipped surface touched (`.claude/settings.json`, `hooks/hooks.json`, `MANIFEST`, `.claude/hooks/*.py`). `lane_check.py`: `lane: C3, 6 files, 1509 lines, FITS; unpredicted: tasks/TASK_GUIDE_T345.md` |
| Full smoke suite still green (no regression) | ☑ pass | Not green, but no regression. Worktree `56 failed, 7786 passed, 24 skipped`; `main` (same time, same machine) `61 failed, 7727 passed, 24 skipped`. `comm` of the two FAILED lists: 0 only in the worktree. The shared 56: `test_stop_attribution_t287.py` 25, `test_slot2b_brace_glob.py` 19, `test_heredoc_quoted_marker.py` 4, `test_memory_channel_and_budget.py` 4, `test_gate_hidden_verbs.py`, `test_memory_usage_report.py`, `test_merge_gate_companion_rows.py`, `test_token_audit_format.py` 1 each; they fail with the session env unset too. `main`'s extra 5 include `test_agents_md_primary.py::test_ac2_claude_md_is_only_the_import` and `test_t352_release_plan_rename.py::test_ac2_no_live_file_names_the_skill_ship`: the uncommitted `CLAUDE.md` overwrite in the main checkout. `sh scripts/validate.sh` → `validate.sh: PASS` |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: a CLI script, tests and docs |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI |

---

## Demonstration

**BEFORE** (2026-11-25T03:53:47Z, checkout of `a47733cf`, the last commit before any implementation): `ls scripts/agent_ws.py` → `No such file or directory`; `python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q` → `53 failed, 1 passed in 12.37s`. Agents got Claude Code's default worktree and an on-disk `target/` each.

**AFTER**: same command at `f5109b7e` → `57 passed in 9.70s`. Live: `claude -p --worktree live1` landed in `/home/thunderkds/workspace/pets/t345-live/wt-live1` with `target-dir = "/dev/shm/agent-ws-1000/repo-f3a2b240/live1-e9d747"`; an Agent `isolation: "worktree"` subagent landed in `wt-agent-ae9d79f248155162e` with its own tmpfs folder; `agent_ws.py gc` removed both worktrees, branches and build folders.

**DELTA**: a project that adds the three hook lines gets, for every Claude worktree, a private tmpfs build folder that no other worktree shares, and a `gc` that cleans leftover subagent worktrees without losing unmerged work.

**WITNESS**: Supervisor session 7b4187fe, 2026-11-25 (red run, live runs, lag test); `Reviewer: T345` (fresh context) — see its section below

---

## Live lag test (run plan step 5)

Machine `coupd` (16 cores, `/dev/sda4` ext4, git 2.34.1), not the target `hungnguyenhuu-NUC11PAHi7`. `git clone --local` of `easy-note-mcp` (`6897345`), 3 worktrees made by `agent_ws.py new`, each built with `agent_ws.py run -- cargo test --no-run -q`, `CARGO_BUILD_JOBS=4`, `RUSTC_WRAPPER=` (cold), probe at normal priority, one run per mode, 20 s rest before each. Load before the run: `load average: 3.69, 4.31, 3.50` (another session was active).

```
== tmpfs: 63 s
wake-up delay ms   p50     0.1  p95     0.5  max     4.9  (n=4497)
git status ms      p50     3.4  p95     5.2  max    11.9  (n=449)
write+fsync ms     p50    32.5  p95    80.1  max  1110.4  (n=449)
11G	/dev/shm/agent-ws-1000
== disk: 81 s
wake-up delay ms   p50     0.1  p95     0.4  max     5.2  (n=3550)
git status ms      p50     3.2  p95     4.6  max     7.3  (n=355)
write+fsync ms     p50    37.7  p95   466.2  max   712.5  (n=355)
11G	total
```

Reading: the run plan expected an fsync max under 1 s with tmpfs (R10 on the target: 0.24 s); here it is 1.1 s, and the on-disk mode did not stall either (0.71 s, against 5–6 s on the target), so this machine does not reproduce the freeze and cannot confirm the fix. tmpfs cut fsync p95 (466 → 80 ms) and build time (81 → 63 s). The 3 build folders took 11 GB of the 16 GB `/dev/shm`, not R10's 4.2 GB: `easy-note-mcp` grew. `new`'s 4 GB free check is per call, so 3 parallel `new` calls all pass it, and a 4th build would hit ENOSPC (documented: `docs/agent-ws.md` "Full tmpfs"). The re-run on the target machine stays open (`Not done:`).

