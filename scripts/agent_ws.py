#!/usr/bin/env python3
"""T345 - agent-ws: worktrees and build folders for many agents and sessions on one repo.

    python3 scripts/agent_ws.py new <name> [--branch B] [--owner-pid PID]
    python3 scripts/agent_ws.py rm <name|path>
    python3 scripts/agent_ws.py gc [--dry-run]
    python3 scripts/agent_ws.py run [--] <command> [args...]
    python3 scripts/agent_ws.py hook-create | hook-remove | hook-env   (Claude Code hooks, JSON on stdin)

`new` makes `../wt-<name>` beside the main checkout on branch `agent-ws/<name>`, from the main
checkout's current branch, and writes a lease (`<git common dir>/agent-ws/leases/<name>.json`). It
prints the absolute path as the only stdout line; every other line goes to stderr. A Rust worktree
(`Cargo.toml` at its root) builds into a private tmpfs build folder: the first tmpfs of
`/dev/shm`, `/tmp` with 4 GB free, at `<mount>/agent-ws-<uid>/<repo id>/<name>-<token>/`; the
`agent-ws-<uid>` folder is 0700, owned by the user, never a symlink. The worktree's untracked
`.cargo/config.toml` holds only `[build] target-dir` (cargo merges it with ~/.cargo/config.toml).
With no fit tmpfs, the worktree keeps an on-disk `target/`. A full tmpfs mid-build fails with
cargo's own error: the free-space check at `new` is the only guard.

`rm` and `gc` reuse the removal rules of `scripts/cleanup_task.py`: they refuse, and remove
nothing, on an unmerged branch, uncommitted or untracked files, or a live process inside. They
never force a removal and never delete an unmerged branch. The tmpfs folder goes last. `gc` removes
only worktrees whose lease owner is dead (PID gone, or reused: start time differs); a worktree with
no lease is never stale.

`run` runs the command under `nice -n 19` (never `ionice`: no effect on `mq-deadline`). The build
slot queue is off unless `AGENT_BUILD_SLOTS` is a positive number.

Exit 0: done. Exit 1: refused or failed. Linux only (`/proc`, `flock`).
"""
import fcntl
import hashlib
import json
import os
import re
import secrets
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cleanup_task as ct  # noqa: E402  (removal rules: T327; not edited)

NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
POINTER = ".cargo/config.toml"
SHELLS = {"sh", "bash", "zsh", "dash", "fish", "python3", "python", "env", "timeout", "nice", "flock"}


class Refused(Exception):
    pass


def err(text):
    print(f"agent-ws: {text}", file=sys.stderr, flush=True)


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_atomic(path, text, mode=0o600):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


# ── repo and lease ───────────────────────────────────────────────────────────────────────────


class Repo:
    def __init__(self, cwd):
        out = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if out.returncode != 0:
            raise Refused("not inside a git repository")
        self.common = os.path.realpath(out.stdout.strip())
        if os.path.basename(self.common) != ".git":
            raise Refused(f"no main checkout for {self.common} (bare repository?)")
        self.main = os.path.dirname(self.common)
        self.state = os.path.join(self.common, "agent-ws")
        self.leases = os.path.join(self.state, "leases")
        slug = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(self.main))[:40] or "repo"
        self.id = f"{slug}-{hashlib.sha256(self.common.encode()).hexdigest()[:8]}"

    def lease_path(self, name):
        return os.path.join(self.leases, f"{name}.json")

    def all_leases(self):
        if not os.path.isdir(self.leases):
            return []
        out = []
        for n in sorted(os.listdir(self.leases)):
            if n.endswith(".json"):
                try:
                    with open(os.path.join(self.leases, n)) as f:
                        out.append(json.load(f))
                except (OSError, ValueError):
                    err(f"unreadable lease {n}: skipped")
        return out

    def find(self, key):
        """Lease by name, or by worktree path."""
        real = os.path.realpath(key) if os.sep in key else None
        for lease in self.all_leases():
            if lease.get("name") == key or (real and os.path.realpath(lease["path"]) == real):
                return lease
        return None


def proc_start(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def proc_comm(pid):
    try:
        with open(f"/proc/{pid}/comm") as f:
            return f.read().strip()
    except OSError:
        return ""


def proc_parent(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return int(f.read().rsplit(")", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        return 0


def owner_pid():
    """The nearest ancestor that is not a shell or wrapper: the Claude Code process (or the
    user's terminal program) that lives as long as the session using the worktree."""
    pid = os.getppid()
    while pid > 1 and proc_comm(pid) in SHELLS:
        pid = proc_parent(pid)
    return pid if pid > 1 else os.getppid()


def owner_alive(lease):
    start = proc_start(lease.get("owner_pid", 0))
    return start is not None and start == lease.get("owner_start")


# ── tmpfs build folder (D4) ──────────────────────────────────────────────────────────────────


def fstype(path):
    real, best, kind = os.path.realpath(path), "", None
    try:
        with open("/proc/self/mounts") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 3:
                    continue
                mnt = parts[1].replace("\\040", " ")
                if (real == mnt or real.startswith(mnt.rstrip("/") + "/")) and len(mnt) >= len(best):
                    best, kind = mnt, parts[2]
    except OSError:
        return None
    return kind


def private_dir(path):
    """Create or check a folder only this user can enter. Returns a refusal reason, or None."""
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        pass
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        return f"{path} is a symlink"
    if not stat.S_ISDIR(st.st_mode):
        return f"{path} is not a folder"
    if st.st_uid != os.getuid():
        return f"{path} belongs to another user"
    if stat.S_IMODE(st.st_mode) != 0o700:
        os.chmod(path, 0o700)
    return None


def tmpfs_candidates():
    raw = os.environ.get("AGENT_WS_TMPFS_CANDIDATES")
    if raw is None:
        return ["/dev/shm", "/tmp"]
    return [c for c in raw.split(os.pathsep) if c]


def pick_tmpfs(repo):
    """(private repo folder on tmpfs, None) or (None, reason)."""
    need = float(os.environ.get("AGENT_WS_MIN_FREE_GB", "4")) * 1024 ** 3
    reasons = []
    for cand in tmpfs_candidates():
        if not os.path.isdir(cand) or fstype(cand) != "tmpfs":
            reasons.append(f"{cand}: not tmpfs")
            continue
        sv = os.statvfs(cand)
        if sv.f_bavail * sv.f_frsize < need:
            reasons.append(f"{cand}: under {need / 1024 ** 3:g} GB free")
            continue
        base = os.path.join(cand, f"agent-ws-{os.getuid()}")
        why = private_dir(base)
        if why:
            reasons.append(why)
            continue
        mine = os.path.join(base, repo.id)
        why = private_dir(mine)
        if why:
            reasons.append(why)
            continue
        return mine, None
    return None, "; ".join(reasons) or "no tmpfs candidate"


def setup_build_dir(repo, path, name):
    """(build folder or None, {relpath: sha256} of files written)."""
    if not os.path.isfile(os.path.join(path, "Cargo.toml")):
        err("no Cargo.toml at the worktree root: build folder not moved")
        return None, {}
    for rel in (POINTER, ".cargo/config"):
        if os.path.lexists(os.path.join(path, rel)):
            err(f"the repo already has {rel}: on-disk target/ kept (agent-ws never edits it)")
            return None, {}
    mine, why = pick_tmpfs(repo)
    if not mine:
        err(f"no usable tmpfs ({why}): on-disk target/ in the worktree")
        return None, {}
    build = os.path.join(mine, f"{name}-{secrets.token_hex(3)}")
    os.mkdir(build, 0o700)
    os.makedirs(os.path.join(path, ".cargo"), exist_ok=True)
    cfg = os.path.join(path, POINTER)
    write_atomic(cfg, "# Written by agent-ws (T345): this worktree builds into a private tmpfs folder.\n"
                      "# `agent-ws rm` deletes this file; edit it and `rm` refuses.\n"
                      f"[build]\ntarget-dir = {json.dumps(build)}\n", 0o644)
    err(f"build folder on tmpfs: {build} (lost on reboot)")
    return build, {POINTER: sha256(cfg)}


def reflink_probe(folder):
    src = tempfile.NamedTemporaryFile(dir=folder, prefix=".agent-ws-probe-", delete=False)
    src.close()
    dst = src.name + ".copy"
    ok = subprocess.run(["cp", "--reflink=always", src.name, dst], capture_output=True).returncode == 0
    for p in (src.name, dst):
        if os.path.exists(p):
            os.unlink(p)
    if ok:
        err("copy-on-write works here, but seeding is not built yet: nothing seeded")
    else:
        err(f"no copy-on-write on {folder} (reflink probe failed): nothing seeded")


def cache_warnings(parent):
    """AC 19: a uv cache or pnpm store on another filesystem than the worktrees gets no hard links."""
    home = os.path.expanduser("~")
    xdg_cache = os.environ.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    dev = os.stat(parent).st_dev
    for label, path in (("uv cache", os.environ.get("UV_CACHE_DIR") or os.path.join(xdg_cache, "uv")),
                        ("pnpm store", os.environ.get("PNPM_STORE_DIR") or os.path.join(xdg_data, "pnpm"))):
        if os.path.isdir(path) and os.stat(path).st_dev != dev:
            err(f"{label} {path} is on another filesystem than {parent}: no hard-link sharing")


# ── new ──────────────────────────────────────────────────────────────────────────────────────


def cmd_new(args):
    name, branch, pid = None, None, None
    it = iter(args)
    for a in it:
        if a == "--branch":
            branch = next(it, None)
        elif a == "--owner-pid":
            pid = int(next(it, "0"))
        elif name is None:
            name = a
        else:
            raise Refused(f"unexpected argument {a!r}")
    if name is None or not NAME_RE.fullmatch(name) or ".." in name:
        raise Refused("usage: new <name> (letters, digits, . _ -; up to 64; not starting with . or -)")
    branch = branch or f"agent-ws/{name}"
    if git(".", "check-ref-format", f"refs/heads/{branch}").returncode != 0:
        raise Refused(f"bad branch name {branch!r}")
    repo = Repo(os.getcwd())
    path = os.path.join(os.path.dirname(repo.main), f"wt-{name}")
    base = git(repo.main, "symbolic-ref", "-q", "--short", "HEAD").stdout.strip() \
        or git(repo.main, "rev-parse", "HEAD").stdout.strip()
    pid = pid or owner_pid()
    os.makedirs(repo.leases, exist_ok=True)
    with open(os.path.join(repo.state, "new.lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # G3c: one `git worktree add` at a time per repo
        if os.path.lexists(path) or os.path.exists(repo.lease_path(name)):
            raise Refused(f"{path} or its lease already exists")
        done = git(repo.main, "worktree", "add", "-q", "-b", branch, path, base)
        if done.returncode != 0:
            raise Refused(f"git worktree add failed: {done.stderr.strip()}")
        lease = {"version": 1, "name": name, "path": path, "branch": branch, "base": base,
                 "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                 "session_id": os.environ.get("CLAUDE_SESSION_ID", ""),
                 "owner_pid": pid, "owner_start": proc_start(pid), "build_dir": None, "files": {}}
        write_atomic(repo.lease_path(name), json.dumps(lease, indent=2) + "\n")
    build, files = setup_build_dir(repo, path, name)
    reflink_probe(os.path.dirname(path))
    cache_warnings(os.path.dirname(path))
    if os.environ.get("CARGO_TARGET_DIR"):
        err("CARGO_TARGET_DIR is set in this environment: it overrides the worktree's build folder "
            "for plain cargo; `agent-ws run` sets its own")
    lease.update(build_dir=build, files=files)
    write_atomic(repo.lease_path(name), json.dumps(lease, indent=2) + "\n")
    print(path, flush=True)
    return 0


COMMANDS = {"new": cmd_new}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__, file=sys.stderr)
        return 1
    try:
        return COMMANDS[argv[1]](argv[2:])
    except Refused as exc:
        err(f"refused: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
