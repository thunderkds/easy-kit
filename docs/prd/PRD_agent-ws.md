# PRD — agent-ws: worktrees and build folders for many agents and sessions
**Last updated**: 2026-11-25
**Status**: Draft (auto, Supervisor 2026-11-25) — from the T345 restated intent the user confirmed on 2026-11-25 ("yes, confirmed"); not approved as a PRD by the user
**Owner**: kit maintainer (thunderkds)

> **Scope of this document**: *What* to build and *why*. Design, experiments and decisions live in
> `tasks/TASK_GUIDE_T345.md` (`## Experiments` R1–R10, decisions D1–D4).

---

## Overview

Several agents and independent Claude Code sessions work on one repo at once, each in its own git
worktree. Each worktree builds into its own on-disk build folder. On the target machine three Rust
builds at once freeze the desktop for 5–13 s: the cause is disk writeback of build output (R9, R10),
not CPU. A shared build folder gives stale builds (R5). Worktrees that agents leave behind pile up
(G2b): about 80 GB of `target/` folders in one repo.

---

## Personas

| ID | Name | Role | Pain Point |
|----|------|------|-----------|
| P1 | Maintainer | Runs several agents and sessions on one Rust repo on one machine | The desktop freezes during parallel builds; old worktrees and build folders fill the disk; cleanup can lose unmerged work. |

---

## Functional Requirements

| ID | Requirement | Acceptance |
|----|-------------|-----------|
| FR-001 | One command, `agent-ws` (`scripts/agent_ws.py`, Python 3), makes and removes agent worktrees beside the repo. A Rust worktree builds into a private tmpfs build folder by default (on-disk fallback). `agent-ws run` runs a heavy command under `nice -n 19`, with an opt-in cross-session build-slot queue. `rm` and `gc` never lose work: they refuse on unmerged, dirty or untracked work and on a live process inside. Claude Code's `WorktreeCreate` / `WorktreeRemove` hooks and a SessionStart env export call it. No two worktrees share one build folder. | `tasks/TASK_GUIDE_T345.md` `## Acceptance Criteria` 1–19 |

---

## Out of scope

Shipping the hooks to installed projects (`.claude/settings.json`, `hooks/hooks.json`, `MANIFEST`);
plan Phases 2–4 (pnpm/uv store layout, sccache/ccache/Gradle caches, `PATH` shims, `agent-ws stats`);
native Windows. See the T345 guide's cut list.
