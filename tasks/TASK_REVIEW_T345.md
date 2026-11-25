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
14. Fix round on the Reviewer's findings: P2-1 (`gc` walks build folders only with `--dry-run`, and skips a file that vanishes), P3-1 (`--owner-pid abc` and a lease missing `name`/`path`/`branch`/`base` are refusals, not tracebacks), P3-3 (AC 14 / SC 7 path text in the guide); P3-2 left: a lease with no readable owner start time is treated as dead, and `rm`'s checks still guard the work; a new Reviewer spawn on the fixed commit `a9861d08` — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4: Review ("A later code fix needs a new reviewer spawn on the new commit")
15. Reviewer round 2 (`a9861d08`): pass, 0 P0/P1/P2; P3-5 (`raw.isdigit()` takes non-ASCII digits, then `int()` raises: a traceback, nothing created) and P3-6 (note) left unfixed, so no third Reviewer round — RULE: `skills/code-review/SKILL.md` § Phase 4 — Apply Safe Fixes ("Present P2/P3 fixes as suggestions only")
Checks: tests `python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q` — 59 passed (57 before the fix round); full suite `python3 -m pytest tests/ .claude/hooks/tests/ -q` in the worktree — 56 failed, 7786 passed, every one of the 56 also fails on `main` (61 failed there); reviews: Supervisor `code-review` — 0 P0, 1 P1 + 1 P2 + 2 P3 fixed (`a815b7cd`), 1 P3 left; `security-review` built-in cannot start here (`fatal: ambiguous argument 'origin/HEAD...'`, memory/learnings.md:2891), run inline against its criteria — 1 P2 fixed (`f5109b7e`), 1 P3 left; real run: `claude -p --worktree live1` (haiku, scratch repo, hooks in its `settings.local.json`) printed `/home/thunderkds/workspace/pets/t345-live/wt-live1` and `target-dir = "/dev/shm/agent-ws-1000/repo-f3a2b240/live1-e9d747"`, `AGENT_WS_BIN=…/scripts/agent_ws.py`, `CARGO_TARGET_DIR=unset`; Agent `isolation: "worktree"` printed `/home/thunderkds/workspace/pets/t345-live/wt-agent-ae9d79f248155162e` with its own tmpfs `target-dir`; `agent_ws.py gc` then removed both (exit 0); 3-agent lag test on an `easy-note-mcp` clone — tmpfs 63 s, fsync p95 80 ms / max 1110 ms; on-disk 81 s, fsync p95 466 ms / max 713 ms (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T345: `agent-ws` stays local, nothing ships; `memory/learnings.md` — 2026-11-25 T345 traps (Debate the Stop hook cannot see; Claude keeps a worktree with an untracked file; main's overwritten `CLAUDE.md` fails 2 tests; `git stash` negative check). `memory/MEMORY.md` not touched: over its budget (43,909 chars), a `/compact-memory` job
Not done: merge (admin: after the auto verify pass); auto verify: PENDING
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report c54b4e946dba]
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report 465fb71aaca2]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_agent_ws_t345.py` — 59 tests (2 added in the fix round: `test_gc_does_not_walk_build_folders_unless_dry_run`, `test_bad_owner_pid_and_broken_lease_are_refusals_not_tracebacks`, both red first: `2 failed`): SC 1 `test_nested_run_inside_a_slot_does_not_deadlock`, SC 2 `test_daemon_left_by_a_build_does_not_keep_the_slot`, SC 3 `test_kill_9_of_the_wrapper_frees_the_slot_and_kills_the_build`, SC 4 `test_eight_concurrent_new_all_succeed`, SC 5 `test_gc_keeps_unmerged_work_of_a_dead_owner`, SC 6 `test_gc_removes_merged_clean_worktree_of_a_dead_owner`, SC 7 `test_cargo_build_lands_on_tmpfs_and_home_config_still_applies`, SC 8 `test_no_tmpfs_falls_back_to_disk_and_says_so`, SC 9 `test_rm_ignores_its_own_pointer_file_but_not_a_user_edit` + `test_rm_keeps_tmpfs_folder_when_refused`, SC 10 `test_two_worktrees_never_share_a_target_dir[True/False]`, SC 11 `test_queue_off_by_default_three_runs_overlap`; AC 4/13 hook tests `test_hook_*`; AC 9 `test_rm_refuses_and_removes_nothing[unmerged/modified/untracked/process]`; AC 12, 15–19 named tests. `59 passed in 20.01s` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q` → `59 passed in 20.01s` (scratchpad venv on `PATH`; system Python has no pytest) |
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


---

## Stage 4 review (Reviewer: T345, fresh context)

Commit reviewed: `d5dc23bd91b72ef2d364f72a1658dd80c5b1f497` (`git diff main...d5dc23bd`: 9 files, 1641 insertions). Worktree `/home/thunderkds/workspace/pets/hungnguyen111/wt-t345`, branch `feat/t345-agent-ws`. Risk High, C3.

Method: no `Skill` tool was callable in this context, so `code-review` and `security-review` were done inline: the diff read in full against `skills/code-review/references/security-reviewer.md` (boundary, actor, resource, result; no built-in `security-review` was started). The guide's 19 Acceptance Criteria and 11 Success Criteria were traced to code and tests. No code was edited.

Verification command (scratchpad venv first on `PATH`):

```
$ python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q
.........................................................                [100%]
57 passed in 15.89s
```

The whole repo suite was not run, as instructed.

### Acceptance trace

| AC / SC | Code | Test | Result |
|---|---|---|---|
| AC 1 baseline | n/a (measurements in guide) | n/a | recorded, not re-run |
| AC 2 `new` path, lease, stdout | `cmd_new` | `test_new_creates_worktree_beside_repo_with_lease_and_path_only_on_stdout` | ok |
| AC 3 / SC 4 8 concurrent | `new.lock` flock | `test_eight_concurrent_new_all_succeed` | ok |
| AC 4 hooks | `hook-create` / `hook-remove`, registered locally (Debate, `## Questions Log`) | `test_hook_create_*`, `test_hook_remove_*` | ok at handler level; the live `claude --worktree` and Agent runs are in the record, not re-run by me |
| AC 5 / SC 1 nested run | `AGENT_WS_SLOT` bypass | `test_nested_run_inside_a_slot_does_not_deadlock` | ok |
| AC 6 / SC 2 daemon | O_CLOEXEC lock fd | `test_daemon_left_by_a_build_does_not_keep_the_slot` | ok |
| AC 7 / SC 3 kill -9 | `_watch` process group kill | `test_kill_9_of_the_wrapper_frees_the_slot_and_kills_the_build` | ok |
| AC 8 / SC 11 queue off by default, cap N | `slots()`, `take_slot` | `test_queue_off_by_default_*`, `test_n_slots_cap_overlap_across_sessions` | ok |
| AC 9 refusals, no force | `blockers`, `remove` | `test_rm_refuses_and_removes_nothing`, `test_rm_never_forces` | ok |
| AC 10 / SC 5, 6 gc | `owner_alive`, `cmd_gc` | `test_gc_*` (6 tests, incl. reused PID) | ok |
| AC 11 reflink | `reflink_probe` | `test_reflink_probe_says_nothing_seeded` | ok |
| AC 12 waiting message | `take_slot` | `test_waiting_for_slot_is_announced` | ok |
| AC 13 SessionStart env | `cmd_hook_env` | `test_hook_env_exports_the_profile_and_never_a_target_dir` | ok |
| AC 14 / SC 7 tmpfs folder | `pick_tmpfs`, `setup_build_dir` | `test_rust_worktree_points_*`, `test_cargo_build_lands_on_tmpfs_*` | ok, path shape differs from the AC text (F3) |
| AC 15 / SC 8 fallback | `pick_tmpfs` reasons | `test_no_tmpfs_falls_back_*`, `test_tmpfs_with_too_little_free_space_*` | ok |
| AC 16 / SC 9 rm and reboot | `remove_build_dir`, `ensure_build_dir` | `test_rm_*`, `test_cargo_recreates_*` | ok |
| AC 17 nice, no ionice | `os.nice(19)` | `test_run_uses_nice_19_and_leaves_io_class_alone` | ok |
| AC 18 / SC 10 no shared target | `build_env` | `test_two_worktrees_never_share_a_target_dir` | ok |
| AC 19 cache warning | `cache_warnings` | `test_cache_on_another_filesystem_warns` | ok |

All 19 ACs and 11 SCs have a check. The tests use real git repos and real processes, and the negative cases (refusals, symlinked private folder, forged lease `build_dir`, tracked cargo config) are present.

### Security review (inline)

Boundaries looked at: other local users on a shared `/dev/shm` and `/tmp`; the hook JSON on stdin (`name`, `worktree_path`, `cwd`); lease files under `.git/agent-ws`; the command given to `run`.

- Shared tmpfs: `private_dir` uses `lstat`, refuses a symlink, a foreign owner or a non-folder, and tightens the mode; a pre-created foreign folder only makes `new` fall back to disk. Rejected as a vulnerability (denial of tmpfs use only, no data reach).
- Hook `name`: reduced to `[A-Za-z0-9._-]` and checked by `NAME_RE` and `..`; the branch name goes through `git check-ref-format`; all `git` calls use argument lists, no shell. Rejected.
- Lease `build_dir` and `name` are trusted as written. The writer is the same user (`.git` is not shipped by clone). `remove_build_dir` still requires an `agent-ws-<uid>` grandparent, owner, non-symlink and `tmpfs` (test covers it). Hardening note only.
- `rm` and `gc` never use `--force` or `branch -D`; `remove` puts the pointer file back if `git worktree remove` fails. Rejected.
- Verdict: no confirmed security finding; no `needs_validation` lead.

### Findings

**P0: none.  P1: none.**

**P2-1: `gc` can crash on a build that is changing, and the size walk runs on every `gc`**
- `scripts/agent_ws.py` `cmd_gc`, the `used += sum(os.path.getsize(...) for ... os.walk(build) ...)` lines (inside the lease loop, before the `owner_alive` check).
- Scenario: agent A is building (cargo creates and deletes files in `target/`); agent B runs `agent_ws.py gc`. `os.walk` lists a file, cargo removes it, `os.path.getsize` raises `FileNotFoundError`. `main` catches only `Refused`, so `gc` ends with a traceback in the middle of the loop: later leases are not collected and the exit code is 1 with no reason line. The sum is only printed under `--dry-run`, yet it is computed (and walks up to 11 GB of files, per the lag test) on every real `gc`.
- Action: compute `used` only when `dry`, and catch `OSError` per file (use `os.lstat` in a `try`).

**P3-1: malformed input gives a traceback instead of `refused:`**
- `scripts/agent_ws.py` `cmd_new` (`--owner-pid abc` raises `ValueError` from `int(...)`); `Repo.find` and `cmd_gc` read `lease["path"]` / `lease["branch"]` / `lease["base"]` with no `.get`, so a lease file missing a key raises `KeyError` (the "unreadable lease" skip only covers invalid JSON).
- Scenario: a hand-edited or half-written lease makes `rm`, `gc` and `hook-remove` fail with a traceback. Exit is still 1 and nothing is removed, so the failure is safe, only unclear.
- Action: validate the required keys in `all_leases` and skip with the existing `unreadable lease` message; wrap the `int()` in `Refused`.

**P3-2: lease owner is unknown or PID 1 gives an immediately "dead" lease**
- `scripts/agent_ws.py` `owner_alive`, `owner_pid`. If `proc_start(pid)` is `None` at creation, `owner_start` is `None`, and `owner_alive` returns `False` at once, so `gc` treats the workspace as stale. `blockers` still guards unmerged, dirty and in-use work, so no work is lost; only a clean, merged, live workspace could be removed early. Narrow.
- Action: record it in `docs/agent-ws.md` limits, or refuse `new` when the owner start time cannot be read.

**P3-3: the guide's AC 14 text no longer matches the code**
- Guide AC 14 says `<mount>/agent-ws-<uid>/<name>/`; code and `## Auto decisions` item 6 use `<mount>/agent-ws-<uid>/<repo id>/<name>-<token>/` (the repo id is required by the edge-case list; the token by R5). Tests and the doc agree with the code, the AC row was not updated.
- Action: edit AC 14 and SC 7 to the real path, so the next reader does not think the code is wrong.

**P3-4 (note): AC 4 is met by local registration, not by a shipped hook**
- The Debate chose a project's untracked `.claude/settings.local.json`; the guide's "Files to change" row records this. The live runs in the record cover `claude --worktree` and the Agent spawn, on `coupd` only. The target-machine re-run stays open (`Not done:` in the record). No action beyond what the record already lists.

### Gate rows (not mine to close)

- The `verify` row of the Evidence table is the auto verify hook's; the record shows `Paused: auto-mode check failed` for missing `code-review` / `security-review` Skill calls in the Supervisor's trace. This review is the fresh-context reviewer run required by the merge gate; it does not repair those trace rows.
- Smoke suite: the record's `56 failed` are shared with `main` (61 there); I did not re-run the full suite.

### Verdict

PASS WITH FINDINGS: 0 P0, 0 P1, 1 P2, 4 P3. The P2 (F1) should be fixed before merge: it is small and safe to fix; the P3s may be fixed or recorded.


### Round 2 (Reviewer: T345, commit a9861d08)

Commit reviewed: `a9861d08e4d7156ae96de17fdd3e0217f2e258b8` (`git diff main...a9861d08`: 9 files; the fix itself is `git diff d2ba1e20 a9861d08`: `scripts/agent_ws.py`, the test file, `tasks/TASK_GUIDE_T345.md`). Risk High, C3.

Method: no `Skill` tool was run in this context, so `code-review` and `security-review` were done inline (the whole diff re-read against `skills/code-review/references/security-reviewer.md`; no built-in `security-review` started). No code edited.

```
$ python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q   (scratchpad venv first on PATH)
59 passed in 12.42s
```

Whole repo suite not run, as instructed.

#### Round-1 findings

| Finding | Status | Evidence |
|---|---|---|
| P2-1 `gc` size walk crash and cost | Fixed | `scripts/agent_ws.py` `cmd_gc`: the walk is guarded by `if dry and ...`, and each `islink`/`getsize` is in `try/except OSError`. Test `test_gc_does_not_walk_build_folders_unless_dry_run` |
| P3-1 tracebacks on bad input | Fixed | `cmd_new`: `--owner-pid` must be `isdigit()` else `Refused`; `all_leases` skips a lease lacking `name`/`path`/`branch`/`base` (`LEASE_KEYS`) with a stderr line. Test `test_bad_owner_pid_and_broken_lease_are_refusals_not_tracebacks`. Callers at `Repo.find`, `remove`, `cmd_gc` now see only leases with those keys |
| P3-2 unknown owner start means dead | Left open by decision (auto decision 14); `blockers` still guards unmerged, dirty and in-use work. Not re-raised | n/a |
| P3-3 AC 14 / SC 7 path text | Fixed | `tasks/TASK_GUIDE_T345.md` AC 14 and SC 7 row 7 now name `<mount>/agent-ws-<uid>/<repo id>/<name>-<token>/` and cite decision 6 |
| P3-4 note (AC 4 by local registration) | Unchanged, recorded in the record's `Not done:` | n/a |

#### Security review (inline), delta and whole

The fix adds no new boundary: `--owner-pid` is now stricter, lease validation only skips more, the walk only runs under `--dry-run`. The round-1 conclusion stands: private tmpfs chain checked by `lstat` (symlink, owner, mode), hook `name` reduced and matched by `NAME_RE`, argument-list `git` calls, no `--force` or `branch -D`, `remove_build_dir` re-checks the `agent-ws-<uid>` parent, owner, non-symlink and `tmpfs` regardless of the lease. No confirmed security finding; no `needs_validation` lead.

#### New findings

**P0: none. P1: none. P2: none.**

**P3-5: `--owner-pid` check accepts non-ASCII digits**
- `scripts/agent_ws.py` `cmd_new`, `raw.isdigit()`. `"²".isdigit()` is true but `int("²")` raises `ValueError`, so that one input still ends in a traceback (exit 1, nothing created, so safe).
- Action: use `raw.isascii() and raw.isdigit()`. Optional.

**P3-6 (note): `cmd_gc` prints `lease['owner_pid']` with a hard key**
- `scripts/agent_ws.py` the `kept {name}: owner {lease['owner_pid']} alive` line. Reached only when `owner_alive` is true, which needs a readable `owner_pid` matching `owner_start`, so no crash is reachable. `LEASE_KEYS` does not list `owner_pid`; harmless. No action.

#### Gate rows (not mine to close)

The `verify` row and the Supervisor-trace `Paused:` lines (missing `code-review` / `security-review` Skill calls) belong to the auto verify hook and the Supervisor; this review does not repair them. The smoke-suite comparison against `main` in the record was not re-run.

#### Verdict

PASS WITH FINDINGS: 0 P0, 0 P1, 0 P2, 1 P3 new (P3-5), 1 P3 note (P3-6); round-1 P2-1, P3-1, P3-3 confirmed fixed, P3-2 left by decision, P3-4 unchanged. Fit to merge once the gate rows are closed by their owners.
