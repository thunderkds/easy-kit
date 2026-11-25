# agent-ws — worktrees and build folders for many agents (T345)

`scripts/agent_ws.py` gives each agent or session its own git worktree beside the repo. A Rust
worktree builds into a private folder in RAM (tmpfs), so parallel builds do not freeze the disk.
It removes worktrees only when no work can be lost. Linux only; needs git 2.31 or newer.

It does **not** ship to installed projects yet. You turn it on per project, in that project's
untracked `.claude/settings.local.json` (below).

## Commands

```bash
python3 scripts/agent_ws.py new <name>          # ../wt-<name> on branch agent-ws/<name>; prints the path
python3 scripts/agent_ws.py run -- cargo test   # nice -n 19; this worktree's own build folder
python3 scripts/agent_ws.py rm <name|path>      # refuses on unmerged, dirty, untracked, or a live process
python3 scripts/agent_ws.py gc [--dry-run]      # removes worktrees whose owner session is gone
```

- **Build folder.** A worktree with `Cargo.toml` at its root gets
  `<mount>/agent-ws-<uid>/<repo id>/<name>-<token>/` on the first tmpfs of `/dev/shm`, `/tmp` that
  has 4 GB free. Its `.cargo/config.toml` (untracked, written by `new`) sets only
  `[build] target-dir`; cargo still reads `~/.cargo/config.toml` for everything else. No fit
  tmpfs, or a repo that tracks `.cargo/config.toml`: the worktree keeps an on-disk `target/`.
- **Lost on reboot.** The tmpfs folder is RAM. The next `agent-ws run` or session start
  re-creates it empty, so the first build is cold.
- **Full tmpfs.** A build that fills tmpfs fails with cargo's own error. The 4 GB check at `new`
  is the only guard. `gc --dry-run` prints how much the repo's build folders hold.
- **Build slots (off by default).** Set `AGENT_BUILD_SLOTS=N` to let at most N `agent-ws run`
  commands run at once across all sessions. A nested `agent-ws run` skips the queue. On the
  measured machine the queue made builds slower and did not stop the freeze (T345 R6–R9), so leave
  it off unless RAM is the limit.
- **CARGO_TARGET_DIR.** `agent-ws run` sets it to the worktree's own folder. A plain `cargo`
  with `CARGO_TARGET_DIR` set in your shell ignores the worktree's folder: `new` warns.
- **Leases.** `new` writes `<git common dir>/agent-ws/leases/<name>.json` with the owner process.
  `gc` removes a worktree only when that process is gone and `rm` would allow it. A worktree made
  by plain `git worktree add` has no lease, and `gc` never touches it.

## Turn on the Claude Code hooks (per project, by hand)

With these, `claude --worktree` and Agent `isolation: "worktree"` get an agent-ws worktree, and every
session gets `AGENT_WS_BIN` (the script path) in its Bash environment. Put this in the project's
`.claude/settings.local.json` (merge with what is there). Replace `/path/to/easy-kit` with the
absolute path of this repo; inside this repo you can use `"$CLAUDE_PROJECT_DIR"`.

```json
{
  "hooks": {
    "WorktreeCreate": [{"hooks": [{"type": "command", "command": "python3 /path/to/easy-kit/scripts/agent_ws.py hook-create"}]}],
    "WorktreeRemove": [{"hooks": [{"type": "command", "command": "python3 /path/to/easy-kit/scripts/agent_ws.py hook-remove"}]}],
    "SessionStart": [{"hooks": [{"type": "command", "command": "python3 /path/to/easy-kit/scripts/agent_ws.py hook-env"}]}]
  }
}
```

Restart Claude Code after the edit. To turn it off, delete the three entries. Claude Code does not
run `WorktreeRemove` when a subagent finishes and keeps its worktree, so run `agent-ws gc` now and
then.
