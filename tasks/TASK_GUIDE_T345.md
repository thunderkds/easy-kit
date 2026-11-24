# TASK_GUIDE — T345: Shared build base for multi-agent, multi-session work (`agent-ws`), Phase 0–1 with the 2026-11-24 review fixes
**Date**: 2026-11-24
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
5. Note the **Complexity Level** above and apply the matching process (brainstorm / decompose / verify depth) from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md` for directory layout, entry points, and blast-radius hotspots

---

## Handoff 2026-11-24 — continue on the target machine

User, 2026-11-24: "the real case is not this machine, so let summary and push, I will continue in another machine for real check".

- Every experiment below ran on the **dev machine** (16 cores, 31 GB RAM, ext4, git 2.34.1, no pnpm/sccache/ccache/Go/Gradle). The target machine that runs the agents is a different one: its filesystem, RAM, git version and toolchains are unknown.
- Findings that do NOT depend on the machine (hold everywhere): G1a, G1b, G1c (flock semantics), G2a (`git branch -D`), G2b and G3a (Claude Code docs), G3b, C1, C4.
- Findings to re-measure on the target: G3c (concurrent `git worktree add` race; newer git may not fail), S1 (copy-on-write: run `df -T` and the reflink probe), C2 (uv cache on the same filesystem as the worktrees?), C3, and every "not tested" toolchain that is installed there.
- Next steps on the target: (1) run `## Reproduce on the target machine` below and paste results into `## Experiments` as a new column or rows marked `target`; (2) answer D1–D3; (3) record the Phase 0 baseline (AC 1) on a real repo; (4) then sign the Fidelity Gate.

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-24, on the Claude Docs plan "Shared Build Base for Multi-Agent Workspaces: Implementation Plan" (https://claude.ai/artifact/VjwpdBJSzeMLSdFYn3hyYc): "the direction is that, we save the resource to build by the multi agents, and multi session, let check if the plan is good to proceed without any gap, if any needed, let experiment for making sure." Supervisor review verdict the same day: not ready; 3 blocking gaps, 5 smaller gaps, experiments below. User: "create the ticket and note all to this".

**Restated intent**:
> Agents and independent Claude Code sessions working on one repo get their worktrees through one command (`agent-ws`), share dependency stores and build caches read-only, and run heavy commands through a cross-process queue of N slots — without the three queue defects, the unsafe cleanup and the layout clash the review found. This ticket delivers the plan's Phase 0 (baseline) and Phase 1 (core in the harness) plus `gc`; Phases 2–4 become follow-up tickets.

**Out of scope** (this ticket):
- Plan Phase 2 (pnpm global virtual store, uv store layout, CoW filesystem move) — follow-up ticket.
- Plan Phase 3 (sccache, ccache, Gradle build cache, Turborepo/Nx cache wiring, warm base build hook) — follow-up ticket.
- Plan Phase 4 shims on `PATH` and `agent-ws stats` — follow-up ticket (`gc` is pulled INTO this ticket, see G2).
- Native Windows (PowerShell). Linux first; WSL2 later.

**Requirement Refs**: none in `PRD.md` yet — add an FR at Stage 2 sign-off.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [ ] Restated intent confirmed to match the user's request (by Supervisor / user — not the implementing agent)
- [ ] Domain terms align with `PROJECT_SPEC.md` glossary (`grill-with-docs` run if terminology was fuzzy)
- [ ] Every Acceptance Criterion below traces to a line in the Requirement
- [ ] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above
- [ ] Decisions D1–D3 (below) answered by the user

> An agent must NOT start implementing until this gate is checked.

### Open decisions (user)

- **D1 — language of `agent-ws`.** Plan prototype is bash. Kit hooks and `scripts/cleanup_task.py` are Python 3, which also answers the plan's Windows question. Supervisor recommendation: Python.
- **D2 — board scope.** Registered on this board (Gate 4) because the integration point is the kit's own hooks (`WorktreeCreate`/`WorktreeRemove`) and `scripts/`. If `agent-ws` should ship as a separate tool, it gets its own board.
- **D3 — slots default and target projects.** Plan open questions 2 and 5: which languages are in use, how many agents at once. Measure on the target machine (the dev machine's 16 cores, 31 GB RAM, ext4 are not the target).

---

## Review findings 2026-11-24 (all of them; evidence in `## Experiments`)

### Blocking gaps (must be fixed in this ticket)

**G1 — Build queue: three defects.** (E2a–E2g)
- G1a Re-entry deadlock: with `AGENT_BUILD_SLOTS=1`, a queued command that calls another queued command (shim inside a build, e.g. `pnpm test` → `npm`) waits forever on the slot it holds. Fix: when `AGENT_WS_SLOT` is already set in the environment, run the command directly. Tested: fix works.
- G1b Slot leak to daemons: the lock fd is inherited by every child; a build that leaves a background process (Gradle daemon, sccache server, dev server, watcher) keeps the slot after the build exits. Fix: `flock -o` semantics (close the lock fd before exec of the command). Tested: fix works.
- G1c Orphan build on wrapper crash: with G1b's fix, `kill -9` of the wrapper frees the slot while the build keeps running and using RAM nobody counts. Fix: start the command in its own process group (`setsid`) and kill the group when the wrapper dies. Tested: no orphan left.

**G2 — Cleanup can lose work, and `gc` is in the wrong phase.** (E4, docs check)
- G2a The plan's `agent-ws rm` deletes the branch; `git branch -D` deleted a branch holding an unmerged commit with no warning (E4b). Fix: `rm` and `gc` reuse `scripts/cleanup_task.py` rules (T327): refuse when unmerged, dirty, untracked or a process runs inside; `git branch -d` only; never `--force`.
- G2b Claude Code keeps a subagent's hook-created worktree when the subagent finishes and does NOT run `WorktreeRemove` (code.claude.com/docs/en/hooks.md, worktrees.md). So `gc` is required from Phase 1, not Phase 4. Live evidence 2026-11-24: `../wt-t326`, `../wt-t327`, `../wt-t340` still exist with their tasks Done; 2 more worktrees listed `prunable`.
- G2c Multi-session liveness: sessions are independent processes, so "agent is gone" needs a lease file per workspace (owner PID + session id + start time); `gc` treats a workspace as stale only when the PID is dead AND G2a's rules pass.

**G3 — Harness integration and layout.** (docs check, E3)
- G3a The harness is Claude Code (plan open question 1). `WorktreeCreate` / `WorktreeRemove` hooks replace git's default for `claude --worktree`, Agent `isolation: "worktree"`, `EnterWorktree`, background sessions and workflow agents. They do NOT fire for `git worktree add` run in Bash — how the kit makes `../wt-tNNN` today. `WorktreeCreate` input has `name`; a command hook prints the absolute path as the last non-empty stdout line (other output to stderr); non-zero exit fails creation; paths with `.`/`..` or through a symlink below the repo root are rejected; `.worktreeinclude` is not processed. `WorktreeRemove` gets `worktree_path`; the hook must remove the directory and any branch it created.
- G3b Layout clash: the plan's `agents/<name>/` collides with the kit's mandatory `agents/` folder, and worktrees inside the repo are scanned by grep, test discovery and file watchers. Put worktrees beside the repo (`../wt-<name>`, as today) and the shared cache in one sibling folder on the same filesystem.
- G3c Concurrent creation (intermittent race): 8 parallel `git worktree add -b` → 1 failed on run 1, 0 on run 2 (`fatal: failed to read .git/worktrees/a3/commondir: No such file or directory`, git 2.34.1). Fix: `agent-ws new` takes an exclusive lock around `git worktree add`.

### Smaller gaps (fix or record in this ticket)

- S1 Seeding on a filesystem without copy-on-write: the dev machine is ext4 (target: re-check); `cp --reflink` is unsupported, so the plan's fallback "full copy" costs a full build folder per agent. Default: skip seeding when a reflink probe fails; rely on caches.
- S2 Base checkout: the plan seeds from `<repo>/` "kept built on main", but the user's main checkout is often dirty or on another branch. Seed from a dedicated base worktree (`../wt-base-main` already exists, detached HEAD).
- S3 Resident daemons are outside the queue: Gradle and Kotlin daemons (and LSPs, dev servers) keep RAM after a build. Profile sets `org.gradle.daemon.idletimeout` (or `--no-daemon`); the RAM budget for slots counts resident daemons.
- S4 Queue wait vs Bash tool timeout: at the 2-minute default (`BASH_DEFAULT_TIMEOUT_MS`), Claude Code moves a still-running foreground command to the background, it does not kill it. A queued build can look "done" to the agent. `agent-ws run` prints `waiting for build slot (N ahead)` on stderr at start and when it gets the slot.
- S5 Node profile notes: pnpm `virtualStoreType: global` is valid (`enableGlobalVirtualStore: true` is the old spelling) but pnpm marks it experimental; a `node` started outside pnpm does not get its ESM `NODE_OPTIONS` hook. Turborepo already shares its cache with the main worktree when `cacheDir` is unset; a relative `cacheDir` turns sharing off — set `TURBO_CACHE_DIR` to an absolute path or leave unset. Nx: `NX_CACHE_DIRECTORY` (default already shared in `~/.nx/<id>/cache`).

### Confirmed by experiment (no change needed)

- C1 Env injection reaches subagents: a SessionStart hook that writes `export X=…` to `$CLAUDE_ENV_FILE` is seen by the main session's Bash AND by an Agent-tool subagent's Bash (E5). The plan's strongest queue-adoption layer works.
- C2 Python: uv hard-links from its cache on the same filesystem by default; a second workspace with numpy+pandas added ~2 MB to 102 MB (E6). Phase 2's "< 5%" check already passes for Python with no config.
- C3 npm: `node_modules` is a full copy per workspace (27 MB → 54 MB for two) (E7), as the plan says.
- C4 Alternative to `PATH` shims: a PreToolUse hook on Bash can rewrite the command via `hookSpecificOutput.updatedInput` (whole input object). Caveat: in auto mode, `updatedInput` without `permissionDecision` can get the call denied. Shims still matter for indirect calls (a script that runs `cargo`).

### Not tested (no tool on this machine)

pnpm, sccache, ccache, Go, Gradle, turbo, nx are not installed; cargo 1.100 and mvn 3.9.16 are, but no real project was built. Plan Phase 3 claims stay unverified.

---

## Experiments (2026-11-24, dev machine — not the target)

The scratchpad that held the scripts was cleared; the scripts are rebuilt in `## Reproduce on the target machine` below.

| ID | Test | Result |
|----|------|--------|
| E2a | 1 slot, `q.sh q.sh echo inner-ran`, no guard | `rc=124` — deadlock |
| E2b | same, guard on `AGENT_WS_SLOT` | `inner-ran`, `rc=0` |
| E2c | fd-in-wrapper lock, `kill -9` wrapper of `sleep 30` | next acquire `rc=124` — child holds lock |
| E2d | build runs `nohup sleep 20 &` and exits | next acquire `rc=124` — slot leaked |
| E2e | `flock -o` form, same daemon | `got-slot`, `rc=0` |
| E2f | `flock -o`, `kill -9` wrapper while build runs | slot freed; orphan build still running: 1 |
| E2g | `setsid flock -o …`, `kill -9 -- -PGID` | orphan left: 0 |
| E3 | 8 concurrent `git worktree add -b` (git 2.34.1) | Intermittent: run 1 → 7 created, 1 `fatal: failed to read .git/worktrees/a3/commondir`; run 2 (reproduce script) → 8 created |
| E4a | `git worktree remove` on worktree with untracked file | refused: `contains modified or untracked files, use --force` |
| E4b | `worktree remove --force` + `git branch -D` on branch with unmerged commit | `Deleted branch agent/a2 (was 5b787b8).` — commit lost, no warning |
| E5 | `claude -p --model haiku` with SessionStart hook writing `$CLAUDE_ENV_FILE`; main Bash and subagent Bash write the var to files | `MAIN=from-session-start`, `SUB=from-session-start` |
| E6 | `uv sync` numpy+pandas in two worktrees, cache `~/.cache/uv` on same ext4 | 102 M each, 104 M together; `.so` shows 3 links |
| E7 | `npm install` typescript+lodash in two worktrees | 27 M each, 54 M together |

### Target machine run, 2026-11-24 (`hungnguyenhuu-NUC11PAHi7`: 8 cores, 30 GB, ext4 on LVM, git 2.53.0, no reflink; pnpm 10.12.4, sccache 0.19.0, uv 0.6.10, cargo 1.99.1, mvn 3.9.16; no ccache/go/gradle/turbo/nx)

| ID | Result on target | Verdict vs dev machine |
|----|------------------|------------------------|
| E2a–E2g | identical: a `124`, b ok, c `124`, d `124`, e `0`, f `0` + orphan 1, g orphan 0 | G1a–G1c hold on this machine too |
| E3 | 10 runs × 8 concurrent `git worktree add -b`: 0 failures (git 2.53.0) | The race did not reproduce on newer git. Keep the lock (cheap; git 2.34 fails), but it is not required on 2.53 |
| E4 | dirty remove refused; `branch -D` deleted the unmerged branch | G2a holds |
| S1 | `cp --reflink=always` fails on `/` (ext4) | Seeding by copy = full copy here: skip seeding (AC 11 applies) |
| E6 | uv, cache on same ext4: 102 M + 1 M for the second (103 M total). Same run with worktrees on `/tmp` (tmpfs): 201 M — no sharing | C2 holds only when cache and worktrees share one filesystem. `agent-ws` must check that (`st_dev`) and warn |
| E7 | npm: 27 M each (full copy). pnpm default store: 27 M for two (23 M apparent each), `lodash.js` has 8 hard links | pnpm already shares through hard links on the same filesystem. Phase 2 gain is the global virtual store only |
| E8 | sccache, two target dirs, tiny crate: 2nd build 0.09 s vs 0.56 s, 1 hit / 1 miss | Works, but a toy crate; not a real-case measure |

#### Real-repo run, 2026-11-24: `easy-note-mcp` (Rust, 17 worktrees), on a fresh local clone, `nice -n 19`, `ionice -c3`, `-j2`, sccache off

Existing state (read-only): 7 worktrees hold `target/` of 5–23 GB, about 80 GB in total, with 81 GB free on `/`. One 17 GB `target/` is 14 GB `deps` (31 copies of `libsyn`; 18 of `zbus`, `toml_edit`), 2.8 GB `incremental`. `~/.cargo/config.toml` already sets `jobs = 4` and `rustc-wrapper = "sccache"`. `easy-personal-mcp` has 8 worktrees, its Rust `target/` is 6.8 GB. `orderly` is Maven plus npm, no build folders present.

| ID | Test | Result |
|----|------|--------|
| R1 | AC 1 baseline, 1 agent, cold, `cargo test --no-run`, default features | 60 s, `target/` 1.4 GB, peak RAM about 1 GB, load 3.5 |
| R2 | second worktree builds into the first one's `CARGO_TARGET_DIR` | 169 dependency units `Fresh`, `target/` +0 MB; only the project crate rebuilds (4 s) |
| R3 | two worktrees build at once on the shared target | both exit 0 in 19 s; cargo prints `Blocking waiting for file lock on build directory` once, and 6 × `... on package cache` (the package cache lock is global in `~/.cargo`, shared target or not) |
| R4 | `--features tray` into the shared target | +1.4 GB, 61 s: each feature combination adds a full set of dependency artifacts |
| R5 | **hazard**: worktree `w3` has a marker string `w1` lacks; `w3` builds, then `w1` builds | `w1` reports `Fresh`, and the artifact still holds `w3`'s code. Cargo's freshness check uses file times, not content. `w1` gets the wrong build until it edits its own source |

Reading: the 5–23 GB per worktree is accumulation (feature combinations × stale builds × test binaries), not one build (1.4 GB). sccache does not shrink `target/`. A shared `CARGO_TARGET_DIR` removes the duplicate dependencies but R5 makes it unsafe for worktrees with different code. Safe options to decide in this ticket: shared dependency cache with one `target/` per worktree (disk stays per worktree), pruning in `agent-ws gc` (delete `incremental/` and stale hashes), a fixed feature set per agent. 

3-agent run (same clone, `jobs = 4` from `~/.cargo/config.toml`, `nice -n 19`, `ionice -c3`, own `target/` each, cold, default features, 8 cores):

| ID | Test | Result |
|----|------|--------|
| R6 | 3 builds at once, no queue | wall 98 s; peak RAM 2.35 GB; peak load1 15.7 on 8 cores; peak 24 runnable processes; 4.2 GB for 3 `target/` |
| R7 | 3 builds through a 1-slot `flock` queue | agents finish at 41 s, 88 s, 139 s; wall 139 s (+42 %); peak RAM 1.0 GB; peak 17 runnable processes; 4.2 GB. Peak load1 14.2 is not reliable: load1 is a 1-minute average and still held R6's load |

Reading: on this machine RAM is not the limit (2.35 GB of 30 GB); CPU is. 3 builds × 4 jobs put 24 runnable processes on 8 cores. One slot at `jobs = 4` cuts the peak but leaves 4 cores idle and costs 42 % wall time. A default of slots = cores ÷ jobs (here 2) was not tested. These are default-feature builds (1.4 GB each); the real 5–23 GB worktrees build more, so the real lag is larger than measured. AC 1 baseline is now recorded for Rust on this machine (R1, R6, R7).

| ID | Test | Result |
|----|------|--------|
| R8 | 3 builds through a 2-slot queue, same setup, one run | agents finish at 67 s, 68 s, 111 s; wall 112 s; peak RAM 1.8 GB; peak 22 runnable processes; average 8.9 runnable over 108 s (about 8 cores saturated); 4.2 GB |

Reading R6–R8 (one run each, so run-to-run noise is unknown): wall time is 98 s with no queue, 112 s with 2 slots, 139 s with 1 slot. Peak runnable processes are 24, 22 and 17. On an idle 8-core machine with RAM to spare, a queue does not improve throughput and 2 slots barely lowers the peak; only 1 slot lowers it clearly, at the highest time cost. The queue's value here is a cap for builds where RAM or a shared resource is the limit, not CPU. Desktop lag was not measured directly (no latency probe); `nice -n 19` was on in every run. Open question for the design: does `nice`/`ionice` inside `agent-ws run` keep the desktop responsive with no slot cap at all (cheaper, no throughput loss)? Answered by R9 below.

R9 lag probe (3 cold builds, own `target/` each, `jobs = 4`, probe at normal priority: 10 ms sleep overshoot, `git status` on a 200-file repo, 4 KB write + `fsync`; one run per mode, run order nice → nice+1 slot → no nice, 15 s cool-down between):

| Mode | Builds | Wake-up delay p95 | `git status` p50 / p95 / max | write+fsync p50 / p95 / max |
|------|--------|-------------------|------------------------------|-----------------------------|
| idle | – | 0.1 ms | 1.7 / 2.4 / 5 ms | 5 / 11 / 26 ms |
| `nice -n 19`, `ionice -c3` | 106 s | 0.8 ms | 4.5 / 11.6 / 2506 ms | 9 / 16 / **8493 ms** |
| `nice`+`ionice` + 1 slot | 136 s | 0.1 ms | 3.2 / 4.4 / 737 ms | 6 / 11 / **4596 ms** |
| no `nice` | 108 s | 2.0 ms | 8.9 / 17.9 / 3359 ms | 9 / 17 / **12899 ms** |

Reading: CPU scheduling is not the lag: wake-up delay p95 stays at 2 ms or less even with no `nice`. The lag is **disk**: a write+`fsync` stalls for 5–13 s in every build mode, and 1 slot only halves it. `ionice -c3` does nothing here: the disk (`sda`) uses `mq-deadline`, and only BFQ honors I/O classes. `nice` helps `git status` p50 by half (8.9 → 4.5 ms) and costs no build time (108 s vs 106 s). Consequence for the design: `nice` is a free default; slots do not fix the stall; the stall comes from writing 1.4 GB per build at once, so less written data (no `incremental/`, one feature set, shared dependency artifacts) is the lever. Not tested at the time: `ionice`-capable scheduler (BFQ), `debug = 0`, `incremental = false`, `target/` on tmpfs. Tested next (R10).

R10 less-data and tmpfs probe (same setup, `nice -n 19` in every mode, `sync` and 20 s rest before each mode; `~/.cargo/config.toml` `debug = "line-tables-only"` applied to all, so the control already writes less than a default cargo build):

| Mode | Builds | 3 targets | `git status` p50 / max | write+fsync p50 / max |
|------|--------|-----------|------------------------|-----------------------|
| control (1st) | 99 s | 4.2 GB | 4.4 / 1902 ms | 9.5 / **5731 ms** |
| `CARGO_INCREMENTAL=0` + `CARGO_PROFILE_DEV_DEBUG=0` | 100 s | 2.2 GB | 5.0 / 436 ms | 7.8 / **5053 ms** |
| `target/` on tmpfs (`/tmp`) | 107 s | 4.2 GB in RAM | 5.1 / 44 ms | 7.4 / **238 ms** |
| control (2nd) | 118 s | 4.2 GB | 4.7 / 718 ms | 9.0 / **5932 ms** |

Reading: the stall repeats (5.7 s and 5.9 s in two controls; 8.5 s in R9, so run noise is about ±2 s). Halving the data written (4.2 → 2.2 GB) does not remove it (5.1 s). Moving `target/` off the disk does: fsync max 238 ms, `git status` max 44 ms, same build time. So the freeze is the writeback of build output to `sda`, and it needs a large cut, not a halving. Costs of tmpfs `target/`: RAM-backed (4.2 GB for 3 builds here, `/tmp` is 16 GB), lost on reboot, every build starts cold, and a 5–23 GB accumulated target (the real worktrees) does not fit; fits only a per-task `target/` that is removed with the worktree. Not tested: tmpfs plus sccache on disk (to win back the cold-build time), `vm.dirty_bytes` / `vm.dirty_background_bytes` tuning (system setting, needs root; current values: `vm.dirty_ratio` 20, `vm.dirty_background_ratio` 10, which on 30 GB RAM is a 3 GB background-flush threshold, about what 3 builds write), BFQ.

Still not measured: Phase 0 baseline on a real repo (AC 1), pnpm global virtual store, sccache on a real crate, Gradle/ccache (not installed), and the `agent-ws` code itself (not written).

---

## Reproduce on the target machine

Run in an empty temp folder ON THE FILESYSTEM WHERE AGENT WORKTREES WILL LIVE. Needs `bash`, `flock` (util-linux), `git`; E6 needs `uv` and network, E7 `npm`. It creates only files under `$W`.

```bash
# ci: skip — manual experiment for the target machine, not a test
W=${W:-$PWD/t345-exp}; mkdir -p "$W/locks" && cd "$W" || exit 1
echo "== machine"; nproc; free -g | head -2; df -T .; git --version
touch a; cp --reflink=always a b 2>/dev/null && echo "reflink: yes" || echo "reflink: NO (seeding = full copy)"; rm -f a b
for t in pnpm npm uv cargo sccache ccache go gradle mvn turbo nx; do printf '%s: ' $t; command -v $t >/dev/null && ($t --version 2>&1 | head -1) || echo missing; done

cat > q.sh <<'EOF'
#!/usr/bin/env bash
# naive queue: lock fd held by the wrapper (the plan's prototype shape)
LOCKDIR=${LOCKDIR:?}; N=${AGENT_BUILD_SLOTS:-1}
if [[ -n "$AGENT_WS_SLOT" && -n "$REENTRY_GUARD" ]]; then exec "$@"; fi
while :; do
  for ((i=0;i<N;i++)); do
    exec {fd}>"$LOCKDIR/slot.$i"
    if flock -n $fd; then export AGENT_WS_SLOT=$i; "$@"; exit $?; fi
    exec {fd}>&-
  done; sleep 0.2
done
EOF
chmod +x q.sh; export LOCKDIR=$W/locks AGENT_BUILD_SLOTS=1; L=$LOCKDIR/slot.0
echo "== E2a nested, no guard (expect 124)"; timeout 4 ./q.sh ./q.sh echo inner; echo rc=$?
echo "== E2b nested, guard (expect inner, 0)"; REENTRY_GUARD=1 timeout 4 ./q.sh ./q.sh echo inner; echo rc=$?
echo "== E2c kill -9 wrapper (expect 124: child holds lock)"; ./q.sh sleep 30 & P=$!; sleep 0.5; kill -9 $P; timeout 2 ./q.sh true; echo rc=$?; pkill -f '^sleep 30$'
echo "== E2d build leaves daemon (expect 124)"; ./q.sh bash -c 'nohup sleep 20 >/dev/null 2>&1 &'; timeout 3 ./q.sh true; echo rc=$?; pkill -f '^sleep 20$'
echo "== E2e flock -o + daemon (expect 0)"; flock -o $L bash -c 'nohup sleep 21 >/dev/null 2>&1 &'; timeout 3 flock -o $L true; echo rc=$?; pkill -f '^sleep 21$'
echo "== E2f flock -o, kill wrapper (expect 0 and orphan 1)"; flock -o $L sleep 22 & P=$!; sleep 0.3; kill -9 $P; timeout 2 flock -o $L true; echo rc=$? orphan=$(pgrep -fc '^sleep 22$'); pkill -f '^sleep 22$'
echo "== E2g setsid + group kill (expect orphan 0)"; setsid flock -o $L sleep 23 & sleep 0.3; PG=$(pgrep -f '^flock -o .* sleep 23'); kill -9 -- -$PG; sleep 0.2; echo orphan=$(pgrep -fc '^sleep 23$')

echo "== E3 8 concurrent worktree add"; git init -q repo; (cd repo && for i in $(seq 200); do echo $i > f$i; done && git add . && git -c user.email=x@y -c user.name=x commit -qm init)
for i in $(seq 8); do git -C repo worktree add -q -b agent/a$i ../agents/a$i 2>&1 | sed "s/^/a$i: /" & done; wait; echo created=$(git -C repo worktree list | grep -c agents/)
echo "== E4 dirty remove refused; branch -D loses an unmerged commit"
(cd agents/a1 && echo d > new.txt); git -C repo worktree remove "$W/agents/a1" 2>&1 | head -1
(cd agents/a2 && echo x >> f1 && git -c user.email=x@y -c user.name=x commit -qam w2); git -C repo worktree remove --force "$W/agents/a2"; git -C repo branch -D agent/a2

echo "== E6 uv sharing"; for w in a5 a6; do [ -d agents/$w ] && (cd agents/$w && printf '[project]\nname="p"\nversion="0"\nrequires-python=">=3.9"\ndependencies=["numpy","pandas"]\n' > pyproject.toml && uv sync -q); done; du -sh agents/a5/.venv; du -shc agents/a5/.venv agents/a6/.venv | tail -1; uv cache dir; df -T "$(uv cache dir)" | tail -1
echo "== E7 npm copies"; for w in a7 a8; do [ -d agents/$w ] && (cd agents/$w && echo '{"name":"p","version":"1.0.0","dependencies":{"typescript":"5.6.3","lodash":"4.17.21"}}' > package.json && npm install -s --no-audit --no-fund >/dev/null 2>&1); done; du -shc agents/a7/node_modules agents/a8/node_modules
```

E5 (env reaches subagents) does not depend on the machine; re-run it only if the Claude Code version differs a lot. Recipe: in a scratch git repo, a `settings.json` whose SessionStart hook runs `echo 'export AGENT_WS_PROBE=from-session-start' >> "$CLAUDE_ENV_FILE"`; then `claude -p --model haiku --setting-sources "" --settings ./settings.json --allowedTools "Bash" "Agent" -- "<ask main Bash and a foreground general-purpose subagent to each write echo \$AGENT_WS_PROBE to its own file>"`, and read the two files.

---

## Dependencies & Reachability

**Depends on**: T327 — `scripts/cleanup_task.py` safe-removal rules (Done)

**Entry point**: `WorktreeCreate`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Phase 0 baseline recorded for one real repo: disk per workspace (`du -sh`), peak RAM and build time for 1 and 3 agents, `df -T` of the worktree parent | Plan Phase 0 |
| 2 | `agent-ws new <name>` creates `../wt-<name>` beside the repo (never under `agents/`), writes a lease file, and prints only the absolute path on stdout's last line | G3a, G3b, G2c |
| 3 | 8 concurrent `agent-ws new` calls all succeed | G3c |
| 4 | A `WorktreeCreate` hook calls `agent-ws new`; a `WorktreeRemove` hook calls `agent-ws rm`; `claude --worktree` and Agent `isolation: "worktree"` both get an `agent-ws` worktree | G3a |
| 5 | With 1 slot, a nested `agent-ws run` inside `agent-ws run` completes (no deadlock) | G1a |
| 6 | A build that leaves a background process does not keep the slot after the build exits | G1b |
| 7 | `kill -9` of the `agent-ws run` wrapper frees the slot AND leaves no process of the build's group running | G1c |
| 8 | Never more than `AGENT_BUILD_SLOTS` heavy commands overlap across 3 sessions | Plan Phase 1 |
| 9 | `agent-ws rm` and `gc` refuse (exit 1, nothing removed) on an unmerged branch, uncommitted or untracked files, or a live process inside; they never use `--force` or `branch -D` | G2a |
| 10 | `gc` removes a workspace whose lease PID is dead and which passes AC 9's checks; it leaves a workspace whose lease PID is alive | G2b, G2c |
| 11 | On a filesystem where a reflink probe fails, `new` seeds nothing and says so on stderr | S1 |
| 12 | `agent-ws run` prints `waiting for build slot` on stderr while queued | S4 |
| 13 | A SessionStart hook exports the profile environment through `$CLAUDE_ENV_FILE` | C1 |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | 1 slot; `agent-ws run x -- agent-ws run x -- echo ok` | prints `ok` within 2 s | automated test |
| 2 | 1 slot; run 1 spawns `sleep 30 &` and exits; run 2 starts | run 2 gets the slot within 2 s | automated test |
| 3 | 1 slot; `kill -9` wrapper of `sleep 30` | slot free within 1 s; no `sleep 30` left | automated test |
| 4 | 8 parallel `agent-ws new` | 8 worktrees, exit 0 each | automated test |
| 5 | worktree with unmerged commit, dead lease PID; `agent-ws gc` | worktree and branch still there, exit 1, reason printed | automated test |
| 6 | merged, clean worktree, dead lease PID; `agent-ws gc` | worktree and branch gone | automated test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_agent_ws_t345.py -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T345.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T345.md`.

---

## Approach

**Pattern reference**: `scripts/cleanup_task.py` — refuse-first removal (Done row, merged branch, clean tree, no live process), one line per action, exit 0/1.

**Vital slice**: `agent-ws new` / `run` / `rm` / `gc` with the G1–G3 fixes, wired to `WorktreeCreate` / `WorktreeRemove` and a SessionStart env export.
**Cut list**:
- Language profiles beyond environment export (pnpm global store, sccache, ccache, Gradle cache) — Phase 2/3 tickets.
- Seeding by copy on non-CoW filesystems (S1) — skipped by default.
- `PATH` shims and PreToolUse `updatedInput` wrapping — Phase 4 ticket.
- `agent-ws stats` — Phase 4 ticket.

Queue: one lock file per slot under the shared cache folder; acquire with non-blocking `flock` per slot; close the lock fd before exec of the command (G1b); run the command in its own process group and kill the group on wrapper exit or signal (G1c); pass `AGENT_WS_SLOT` to children and skip acquiring when set (G1a).

---

## Edge Case Checklist

- [ ] Nested `agent-ws run` (G1a)
- [ ] Build leaves a daemon (G1b); wrapper killed mid-build (G1c)
- [ ] Two sessions call `new` with the same name at once
- [ ] Lease PID reused by an unrelated process after reboot (compare start time)
- [ ] `WorktreeCreate` path through a symlink below repo root is rejected by Claude Code
- [ ] Subagent worktree left after the subagent finishes (G2b) — `gc` picks it up
- [ ] Existing `../wt-tNNN` worktrees made by `git worktree add` (no lease file) — `gc` must not treat a missing lease as dead
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for the old worktree-creation wording in `docs/claude-md/pipeline-stages.md`, `agents/common-infrastructure.md`, `site/`

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `scripts/agent_ws.py` (new; language per D1) | `new`, `run`, `rm`, `gc` |
| `.claude/hooks/worktree_create.py` (new) | `WorktreeCreate` → `agent-ws new` |
| `.claude/hooks/worktree_remove.py` (new) | `WorktreeRemove` → `agent-ws rm` |
| `.claude/settings.json` | register the two hooks; SessionStart env export |
| `.claude/hooks/tests/test_agent_ws_t345.py` (new) | Success Criteria 1–6 |
| `docs/claude-md/pipeline-stages.md` | worktree creation and cleanup step names `agent-ws` |
| Pre-existing pin tests | To fill before work: grep `.claude/hooks/tests/` and `tests/` for `settings.json` hook lists and `pipeline-stages.md` text; check `test_agent_guide_dedup.py`, `test_vital_slice.py` and the memory budget tests. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `scripts/cleanup_task.py` | reuse its rules; T327 behavior stays as is |
| `.claude/skills`, `.claude/agents` symlinks | load-bearing relative symlinks |

---

## Test Plan

Unit tests for the queue (Success Criteria 1–3) and lifecycle (4–6) in a temp git repo. Then one live run: `claude --worktree` and one Agent `isolation: "worktree"` spawn in a scratch repo with the hooks on, checking AC 4 and AC 13. Phase 0 baseline (AC 1) on one real user repo picked under D3.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (if Medium/High risk)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T345.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run — feature confirmed working in running app
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review
