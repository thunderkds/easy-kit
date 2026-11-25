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
Checks: PENDING
Memory: PENDING
Not done: merge (admin: after the auto verify pass); auto verify: PENDING
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk High, but the trace has no `security-review` Skill call [report c54b4e946dba]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | PENDING |
| Verification command run | ☐ pass / ☐ fail | PENDING |
| Negative cases hold | ☐ pass / ☐ fail | PENDING |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | PENDING |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | PENDING |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: a CLI script, tests and docs |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI |

---

## Demonstration

**BEFORE**: PENDING

**AFTER**: PENDING

**DELTA**: PENDING

**WITNESS**: PENDING
