"""T345 - scripts/agent_ws.py: worktrees, tmpfs build folders, opt-in build slots, safe removal.

Each test makes its own git repo under pytest's tmp_path; worktrees land beside it
(`<tmp_path>/wt-<name>`). tmpfs build folders go under a per-test folder in /dev/shm
(test seam AGENT_WS_TMPFS_CANDIDATES), and slot locks under a per-test state folder
(AGENT_WS_STATE_DIR), so no test touches the user's real folders.
"""
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "scripts", "agent_ws.py")
HAS_SHM = os.path.isdir("/dev/shm") and subprocess.run(
    ["stat", "-f", "-c", "%T", "/dev/shm"], capture_output=True, text=True).stdout.strip() == "tmpfs"
HAS_CARGO = shutil.which("cargo") is not None
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True,
                          env={**os.environ, **GIT_ENV})


@pytest.fixture
def shm():
    if not HAS_SHM:
        pytest.skip("no tmpfs at /dev/shm")
    path = f"/dev/shm/t345-test-{uuid.uuid4().hex[:8]}"
    os.mkdir(path, 0o700)
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def env(tmp_path):
    state = tmp_path / "state"
    e = {**os.environ, **GIT_ENV, "AGENT_WS_STATE_DIR": str(state), "AGENT_WS_TMPFS_CANDIDATES": ""}
    for k in ("AGENT_BUILD_SLOTS", "AGENT_WS_SLOT", "CARGO_TARGET_DIR", "UV_CACHE_DIR",
              "AGENT_WS_MIN_FREE_GB"):
        e.pop(k, None)
    return e


def make_repo(tmp_path, rust=False):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "README").write_text("r\n")
    if rust:
        (repo / "Cargo.toml").write_text('[package]\nname = "t345crate"\nversion = "0.1.0"\n'
                                         'edition = "2021"\n\n[dependencies]\n')
        (repo / "src").mkdir()
        (repo / "src" / "lib.rs").write_text('pub const MARK: &str = "base-mark";\n')
        (repo / ".gitignore").write_text("/target\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "init")
    return repo


def ws(cwd, env, *args, timeout=60):
    return subprocess.run([sys.executable, SCRIPT, *args], cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=timeout)


def dead_pid():
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def lease_of(repo, name):
    common = git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    with open(os.path.join(repo, common, "agent-ws", "leases", f"{name}.json")) as f:
        return json.load(f)


def cargo_env(env, tmp_path):
    """A private CARGO_HOME whose config sets a logging rustc-wrapper: proves the worktree's
    .cargo/config.toml merges with the home config (only build.target-dir changes)."""
    home = tmp_path / "cargo-home"
    home.mkdir(exist_ok=True)
    log = tmp_path / "wrapper.log"
    wrapper = tmp_path / "wrapper.sh"
    wrapper.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\nexec "$@"\n')
    wrapper.chmod(0o755)
    (home / "config.toml").write_text(f'[build]\nrustc-wrapper = "{wrapper}"\njobs = 1\n')
    e = {**env, "CARGO_HOME": str(home)}
    real_home = os.environ.get("CARGO_HOME", os.path.expanduser("~/.cargo"))
    e["PATH"] = os.path.join(real_home, "bin") + os.pathsep + e.get("PATH", "")
    e.setdefault("RUSTUP_HOME", os.environ.get("RUSTUP_HOME", os.path.expanduser("~/.rustup")))
    return e, log


# ── Slice 1: new ─────────────────────────────────────────────────────────────────────────────


def test_new_creates_worktree_beside_repo_with_lease_and_path_only_on_stdout(tmp_path, env):
    repo = make_repo(tmp_path)
    r = ws(repo, env, "new", "a1")
    assert r.returncode == 0, r.stderr
    path = str(tmp_path / "wt-a1")
    assert r.stdout.strip() == path  # AC 2: only the absolute path on stdout
    assert os.path.isfile(os.path.join(path, "README"))
    assert "agents" not in path.split(os.sep)
    lease = lease_of(repo, "a1")
    assert lease["path"] == path and lease["branch"] == "agent-ws/a1" and lease["base"] == "main"
    assert isinstance(lease["owner_pid"], int) and lease["owner_start"]
    assert git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "agent-ws/a1"


def test_new_refuses_bad_names_and_existing_names(tmp_path, env):
    repo = make_repo(tmp_path)
    for bad in ("../x", "a/b", "", ".hidden", "x" * 80):
        r = ws(repo, env, "new", bad)
        assert r.returncode == 1 and not r.stdout.strip(), bad
    assert ws(repo, env, "new", "dup").returncode == 0
    r = ws(repo, env, "new", "dup")
    assert r.returncode == 1 and "exists" in r.stderr


def test_eight_concurrent_new_all_succeed(tmp_path, env):  # SC 4, AC 3
    repo = make_repo(tmp_path)
    procs = [subprocess.Popen([sys.executable, SCRIPT, "new", f"c{i}"], cwd=repo, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for i in range(8)]
    outs = [p.communicate(timeout=60) for p in procs]
    assert [p.returncode for p in procs] == [0] * 8, [o[1] for o in outs]
    listed = git(repo, "worktree", "list").stdout
    assert all(f"wt-c{i}" in listed for i in range(8))


def test_same_name_twice_at_once_one_wins(tmp_path, env):
    repo = make_repo(tmp_path)
    procs = [subprocess.Popen([sys.executable, SCRIPT, "new", "same"], cwd=repo, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for _ in range(2)]
    for p in procs:
        p.communicate(timeout=60)
    assert sorted(p.returncode for p in procs) == [0, 1]


def test_new_from_inside_a_linked_worktree_still_goes_beside_the_main_checkout(tmp_path, env):
    repo = make_repo(tmp_path)
    first = ws(repo, env, "new", "outer").stdout.strip()
    r = ws(first, env, "new", "inner")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(tmp_path / "wt-inner")


def test_reflink_probe_says_nothing_seeded(tmp_path, env):  # AC 11
    repo = make_repo(tmp_path)
    r = ws(repo, env, "new", "s1")
    assert r.returncode == 0 and "nothing seeded" in r.stderr


def test_non_rust_repo_gets_no_build_folder(tmp_path, env, shm):
    repo = make_repo(tmp_path)
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "n1")
    assert r.returncode == 0
    assert lease_of(repo, "n1")["build_dir"] is None
    assert not os.path.exists(tmp_path / "wt-n1" / ".cargo")
    assert "no Cargo.toml" in r.stderr


def test_rust_worktree_points_target_at_private_tmpfs_folder(tmp_path, env, shm):  # AC 14
    repo = make_repo(tmp_path, rust=True)
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "r1")
    assert r.returncode == 0, r.stderr
    lease = lease_of(repo, "r1")
    build = lease["build_dir"]
    base = os.path.join(shm, f"agent-ws-{os.getuid()}")
    assert build.startswith(base + os.sep) and os.path.isdir(build)
    st = os.lstat(base)
    assert stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700 and st.st_uid == os.getuid()
    cfg = tmp_path / "wt-r1" / ".cargo" / "config.toml"
    assert json.dumps(build) in cfg.read_text()
    assert ".cargo/config.toml" in lease["files"]


@pytest.mark.skipif(not HAS_CARGO, reason="cargo not installed")
def test_cargo_build_lands_on_tmpfs_and_home_config_still_applies(tmp_path, env, shm):  # SC 7
    repo = make_repo(tmp_path, rust=True)
    ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "r2")
    wt = tmp_path / "wt-r2"
    cenv, log = cargo_env(env, tmp_path)
    b = subprocess.run(["cargo", "build", "-q"], cwd=wt, env=cenv, capture_output=True, text=True,
                       timeout=300)
    assert b.returncode == 0, b.stderr
    build = lease_of(repo, "r2")["build_dir"]
    assert os.path.isdir(os.path.join(build, "debug"))
    assert subprocess.run(["stat", "-f", "-c", "%T", build], capture_output=True,
                          text=True).stdout.strip() == "tmpfs"
    assert not (wt / "target").exists()
    assert log.exists() and "rustc" in log.read_text()  # rustc-wrapper from CARGO_HOME applied


def test_no_tmpfs_falls_back_to_disk_and_says_so(tmp_path, env):  # SC 8, AC 15
    repo = make_repo(tmp_path, rust=True)
    r = ws(repo, env, "new", "f1")  # candidates forced empty by the fixture
    assert r.returncode == 0
    assert "on-disk target/" in r.stderr
    assert lease_of(repo, "f1")["build_dir"] is None
    assert not (tmp_path / "wt-f1" / ".cargo").exists()


def test_tmpfs_with_too_little_free_space_falls_back(tmp_path, env, shm):  # AC 15
    repo = make_repo(tmp_path, rust=True)
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm, "AGENT_WS_MIN_FREE_GB": "100000"},
           "new", "f2")
    assert r.returncode == 0 and "on-disk target/" in r.stderr
    assert lease_of(repo, "f2")["build_dir"] is None


def test_candidate_that_is_not_tmpfs_is_skipped(tmp_path, env):
    repo = make_repo(tmp_path, rust=True)
    disk = tmp_path / "disk"
    disk.mkdir()
    fstype = subprocess.run(["stat", "-f", "-c", "%T", str(disk)], capture_output=True,
                            text=True).stdout.strip()
    if fstype == "tmpfs":
        pytest.skip("tmp_path is tmpfs on this machine")
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": str(disk)}, "new", "f3")
    assert r.returncode == 0 and lease_of(repo, "f3")["build_dir"] is None


def test_symlinked_private_folder_is_refused(tmp_path, env, shm):  # D4
    repo = make_repo(tmp_path, rust=True)
    elsewhere = os.path.join(shm, "elsewhere")
    os.mkdir(elsewhere)
    os.symlink(elsewhere, os.path.join(shm, f"agent-ws-{os.getuid()}"))
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "f4")
    assert r.returncode == 0 and "symlink" in r.stderr and "on-disk target/" in r.stderr
    assert os.listdir(elsewhere) == []


def test_loose_private_folder_mode_is_tightened(tmp_path, env, shm):
    repo = make_repo(tmp_path, rust=True)
    base = os.path.join(shm, f"agent-ws-{os.getuid()}")
    os.mkdir(base)
    os.chmod(base, 0o777)
    assert ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "f5").returncode == 0
    assert stat.S_IMODE(os.lstat(base).st_mode) == 0o700


def test_tracked_cargo_config_is_never_overwritten(tmp_path, env, shm):
    repo = make_repo(tmp_path, rust=True)
    (repo / ".cargo").mkdir()
    (repo / ".cargo" / "config.toml").write_text("[alias]\nb = \"build\"\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "cfg")
    r = ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "f6")
    assert r.returncode == 0 and "on-disk target/" in r.stderr
    assert (tmp_path / "wt-f6" / ".cargo" / "config.toml").read_text() == "[alias]\nb = \"build\"\n"
    assert lease_of(repo, "f6")["build_dir"] is None


def test_two_repos_same_name_get_different_build_folders(tmp_path, env, shm):
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    (tmp_path / "x").mkdir()
    (tmp_path / "y").mkdir()
    a = make_repo(tmp_path / "x", rust=True)
    b = make_repo(tmp_path / "y", rust=True)
    assert ws(a, e, "new", "same").returncode == 0
    assert ws(b, e, "new", "same").returncode == 0
    assert lease_of(a, "same")["build_dir"] != lease_of(b, "same")["build_dir"]


def test_cache_on_another_filesystem_warns(tmp_path, env, shm):  # AC 19
    repo = make_repo(tmp_path)
    on_shm = os.path.join(shm, "uv-cache")
    os.mkdir(on_shm)
    r = ws(repo, {**env, "UV_CACHE_DIR": on_shm}, "new", "u1")
    assert r.returncode == 0 and "uv cache" in r.stderr and "another filesystem" in r.stderr
    near = tmp_path / "uv-near"
    near.mkdir()
    r = ws(repo, {**env, "UV_CACHE_DIR": str(near)}, "new", "u2")
    assert "uv cache" not in r.stderr


def test_cargo_target_dir_in_environment_warns(tmp_path, env):  # AC 18
    repo = make_repo(tmp_path, rust=True)
    r = ws(repo, {**env, "CARGO_TARGET_DIR": str(tmp_path / "shared")}, "new", "w1")
    assert r.returncode == 0 and "CARGO_TARGET_DIR" in r.stderr


# ── Slice 2: rm and gc ───────────────────────────────────────────────────────────────────────


def commit_in(path, fname="w.txt"):
    (path / fname).write_text("work\n")
    git(path, "add", fname)
    git(path, "commit", "-qm", "work")


def branches(repo):
    return git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()


def test_rm_removes_clean_merged_worktree_branch_and_lease(tmp_path, env):
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "m1")
    r = ws(repo, env, "rm", "m1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (tmp_path / "wt-m1").exists() and "agent-ws/m1" not in branches(repo)
    assert not os.path.exists(os.path.join(repo, ".git", "agent-ws", "leases", "m1.json"))


def test_rm_accepts_the_worktree_path(tmp_path, env):
    repo = make_repo(tmp_path)
    path = ws(repo, env, "new", "m2").stdout.strip()
    assert ws(repo, env, "rm", path).returncode == 0
    assert not os.path.exists(path)


@pytest.mark.parametrize("dirt", ["unmerged", "modified", "untracked", "process"])
def test_rm_refuses_and_removes_nothing(tmp_path, env, dirt):  # AC 9
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "d1")
    wt = tmp_path / "wt-d1"
    proc = None
    if dirt == "unmerged":
        commit_in(wt)
    elif dirt == "modified":
        (wt / "README").write_text("changed\n")
    elif dirt == "untracked":
        (wt / "new.txt").write_text("x\n")
    else:
        proc = subprocess.Popen(["sleep", "30"], cwd=wt)
    try:
        r = ws(repo, env, "rm", "d1")
        assert r.returncode == 1, r.stdout + r.stderr
        assert "refused" in r.stderr
        assert wt.is_dir() and "agent-ws/d1" in branches(repo)
        assert os.path.exists(os.path.join(repo, ".git", "agent-ws", "leases", "d1.json"))
    finally:
        if proc:
            proc.kill()
            proc.wait()


def test_rm_never_forces(tmp_path):
    text = open(SCRIPT).read()
    assert "--force" not in text and '"-D"' not in text and "'-D'" not in text


def test_rm_ignores_its_own_pointer_file_but_not_a_user_edit(tmp_path, env, shm):
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "p1")
    build = lease_of(repo, "p1")["build_dir"]
    assert ws(repo, e, "rm", "p1").returncode == 0  # SC 9: untouched pointer: rm goes ahead
    assert not (tmp_path / "wt-p1").exists() and not os.path.exists(build)
    ws(repo, e, "new", "p2")
    cfg = tmp_path / "wt-p2" / ".cargo" / "config.toml"
    cfg.write_text(cfg.read_text() + "[alias]\nx = \"build\"\n")
    r = ws(repo, e, "rm", "p2")
    assert r.returncode == 1 and cfg.exists() and os.path.isdir(lease_of(repo, "p2")["build_dir"])


def test_rm_keeps_tmpfs_folder_when_refused(tmp_path, env, shm):  # SC 9 second half
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "p3")
    commit_in(tmp_path / "wt-p3")
    build = lease_of(repo, "p3")["build_dir"]
    assert ws(repo, e, "rm", "p3").returncode == 1
    assert os.path.isdir(build) and (tmp_path / "wt-p3").is_dir() and "agent-ws/p3" in branches(repo)


def test_rm_after_reboot_tmpfs_gone_is_no_error(tmp_path, env, shm):  # AC 16
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "b1")
    ws(repo, e, "new", "b2", "--owner-pid", str(dead_pid()))
    shutil.rmtree(os.path.join(shm, f"agent-ws-{os.getuid()}"))  # what a reboot does
    assert ws(repo, e, "rm", "b1").returncode == 0
    r = ws(repo, e, "gc")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (tmp_path / "wt-b2").exists()


@pytest.mark.skipif(not HAS_CARGO, reason="cargo not installed")
def test_cargo_recreates_build_folder_after_reboot(tmp_path, env, shm):  # AC 16
    repo = make_repo(tmp_path, rust=True)
    ws(repo, {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}, "new", "b3")
    build = lease_of(repo, "b3")["build_dir"]
    shutil.rmtree(os.path.join(shm, f"agent-ws-{os.getuid()}"))
    cenv, _ = cargo_env(env, tmp_path)
    r = ws(tmp_path / "wt-b3", cenv, "run", "--", "cargo", "build", "-q", timeout=300)
    assert r.returncode == 0, r.stderr
    assert os.path.isdir(os.path.join(build, "debug"))
    assert stat.S_IMODE(os.lstat(os.path.join(shm, f"agent-ws-{os.getuid()}")).st_mode) == 0o700


def test_gc_keeps_unmerged_work_of_a_dead_owner(tmp_path, env):  # SC 5
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "g1", "--owner-pid", str(dead_pid()))
    commit_in(tmp_path / "wt-g1")
    r = ws(repo, env, "gc")
    assert r.returncode == 1 and "not merged" in r.stdout + r.stderr
    assert (tmp_path / "wt-g1").is_dir() and "agent-ws/g1" in branches(repo)


def test_gc_removes_merged_clean_worktree_of_a_dead_owner(tmp_path, env):  # SC 6, AC 10
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "g2", "--owner-pid", str(dead_pid()))
    commit_in(tmp_path / "wt-g2")
    git(repo, "merge", "-q", "--ff-only", "agent-ws/g2")
    r = ws(repo, env, "gc")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (tmp_path / "wt-g2").exists() and "agent-ws/g2" not in branches(repo)


def test_gc_leaves_a_live_owner_alone(tmp_path, env):  # AC 10
    repo = make_repo(tmp_path)
    live = subprocess.Popen(["sleep", "30"])
    try:
        ws(repo, env, "new", "g3", "--owner-pid", str(live.pid))
        r = ws(repo, env, "gc")
        assert r.returncode == 0 and (tmp_path / "wt-g3").is_dir()
        assert "alive" in r.stdout
    finally:
        live.kill()
        live.wait()


def test_gc_treats_a_reused_pid_as_dead(tmp_path, env):
    repo = make_repo(tmp_path)
    live = subprocess.Popen(["sleep", "30"])
    try:
        ws(repo, env, "new", "g4", "--owner-pid", str(live.pid))
        lp = os.path.join(repo, ".git", "agent-ws", "leases", "g4.json")
        lease = json.load(open(lp))
        lease["owner_start"] = "1"  # same PID, other start time: a reused PID
        open(lp, "w").write(json.dumps(lease))
        assert ws(repo, env, "gc").returncode == 0
        assert not (tmp_path / "wt-g4").exists()
    finally:
        live.kill()
        live.wait()


def test_gc_skips_worktrees_with_no_lease(tmp_path, env):
    repo = make_repo(tmp_path)
    git(repo, "worktree", "add", "-q", "-b", "plain", str(tmp_path / "wt-plain"))
    r = ws(repo, env, "gc")
    assert r.returncode == 0 and "no lease" in r.stdout
    assert (tmp_path / "wt-plain").is_dir() and "plain" in branches(repo)


def test_gc_dry_run_removes_nothing(tmp_path, env):
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "g5", "--owner-pid", str(dead_pid()))
    r = ws(repo, env, "gc", "--dry-run")
    assert r.returncode == 0 and "would remove" in r.stdout
    assert (tmp_path / "wt-g5").is_dir()


def test_gc_cleans_lease_of_a_worktree_folder_deleted_by_hand(tmp_path, env):
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "g6", "--owner-pid", str(dead_pid()))
    shutil.rmtree(tmp_path / "wt-g6")
    git(repo, "worktree", "prune")
    r = ws(repo, env, "gc")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not os.path.exists(os.path.join(repo, ".git", "agent-ws", "leases", "g6.json"))
    assert "agent-ws/g6" not in branches(repo)  # merged (no commits): branch -d


# ── Slice 3: run ─────────────────────────────────────────────────────────────────────────────


def procs_matching(text):
    out = []
    for name in os.listdir("/proc"):
        if name.isdigit():
            try:
                with open(f"/proc/{name}/cmdline", "rb") as f:
                    if text in f.read().replace(b"\0", b" ").decode("utf-8", "replace"):
                        out.append(int(name))
            except OSError:
                pass
    return out


def slot_free(env, i=0):
    import fcntl
    path = os.path.join(env["AGENT_WS_STATE_DIR"], "slots", f"slot.{i}")
    if not os.path.exists(path):
        return True
    with open(path, "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False


def wait_for(cond, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return cond()


def test_queue_off_by_default_three_runs_overlap(tmp_path, env):  # SC 11, AC 8
    t = time.time()
    procs = [subprocess.Popen([sys.executable, SCRIPT, "run", "--", "sleep", "1"], cwd=tmp_path,
                              env=env) for _ in range(3)]
    assert [p.wait(timeout=10) for p in procs] == [0, 0, 0]
    assert time.time() - t < 2


def test_nested_run_inside_a_slot_does_not_deadlock(tmp_path, env):  # SC 1, AC 5
    e = {**env, "AGENT_BUILD_SLOTS": "1"}
    r = ws(tmp_path, e, "run", "--", sys.executable, SCRIPT, "run", "--", "echo", "ok", timeout=2)
    assert r.returncode == 0 and r.stdout.strip() == "ok"


def test_daemon_left_by_a_build_does_not_keep_the_slot(tmp_path, env):  # SC 2, AC 6
    e = {**env, "AGENT_BUILD_SLOTS": "1"}
    mark = f"sleep 30.{os.getpid()}1"
    try:
        r = ws(tmp_path, e, "run", "--", "bash", "-c", f"nohup {mark} >/dev/null 2>&1 &", timeout=5)
        assert r.returncode == 0
        assert procs_matching(mark)  # the daemon still runs
        r = ws(tmp_path, e, "run", "--", "true", timeout=2)
        assert r.returncode == 0
    finally:
        for pid in procs_matching(mark):
            os.kill(pid, signal.SIGKILL)


def test_kill_9_of_the_wrapper_frees_the_slot_and_kills_the_build(tmp_path, env):  # SC 3, AC 7
    e = {**env, "AGENT_BUILD_SLOTS": "1"}
    mark = f"sleep 30.{os.getpid()}2"
    p = subprocess.Popen([sys.executable, SCRIPT, "run", "--", "bash", "-c", f"{mark}; true"],
                         cwd=tmp_path, env=e)
    try:
        assert wait_for(lambda: not slot_free(e), 5)  # the wrapper holds the slot
        assert wait_for(lambda: len(procs_matching(mark)) >= 3, 5)  # wrapper, bash, sleep
        p.kill()
        p.wait()
        assert wait_for(lambda: slot_free(e), 1)
        assert wait_for(lambda: not procs_matching(mark), 2)
    finally:
        for pid in procs_matching(mark):
            os.kill(pid, signal.SIGKILL)


def test_waiting_for_slot_is_announced(tmp_path, env):  # AC 12
    e = {**env, "AGENT_BUILD_SLOTS": "1"}
    first = subprocess.Popen([sys.executable, SCRIPT, "run", "--", "sleep", "1"], cwd=tmp_path, env=e)
    try:
        assert wait_for(lambda: not slot_free(e), 5)
        r = ws(tmp_path, e, "run", "--", "true", timeout=10)
        assert r.returncode == 0 and "waiting for build slot" in r.stderr
    finally:
        first.wait(timeout=10)


def test_n_slots_cap_overlap_across_sessions(tmp_path, env):  # AC 8
    e = {**env, "AGENT_BUILD_SLOTS": "2"}
    log = tmp_path / "log"
    job = f'echo "+ $(date +%s.%N)" >> {log}; sleep 0.6; echo "- $(date +%s.%N)" >> {log}'
    procs = [subprocess.Popen([sys.executable, SCRIPT, "run", "--", "bash", "-c", job],
                              cwd=tmp_path, env=e) for _ in range(3)]
    assert [p.wait(timeout=20) for p in procs] == [0, 0, 0]
    events = sorted((float(t), 1 if s == "+" else -1) for s, t in
                    (line.split() for line in log.read_text().splitlines()))
    level = peak = 0
    for _, d in sorted(events, key=lambda x: (x[0], x[1])):
        level += d
        peak = max(peak, level)
    assert peak == 2


@pytest.mark.parametrize("slots", ["", "1"])
def test_run_uses_nice_19_and_leaves_io_class_alone(tmp_path, env, slots):  # AC 17
    e = {**env, "AGENT_BUILD_SLOTS": slots}
    r = ws(tmp_path, e, "run", "--", sys.executable, "-c", "import os; print(os.nice(0))")
    assert r.returncode == 0 and r.stdout.strip() == "19"
    if shutil.which("ionice"):
        outside = subprocess.run(["ionice"], capture_output=True, text=True).stdout
        inside = ws(tmp_path, e, "run", "--", "ionice").stdout
        assert inside == outside
    assert "ionice" not in open(SCRIPT).read().split('"""', 2)[2]  # no ionice call in the code


def test_run_passes_exit_code_and_reports_missing_command(tmp_path, env):
    assert ws(tmp_path, env, "run", "--", "bash", "-c", "exit 7").returncode == 7
    assert ws(tmp_path, {**env, "AGENT_BUILD_SLOTS": "1"}, "run", "--", "bash", "-c",
              "exit 7").returncode == 7
    r = ws(tmp_path, env, "run", "--", "no-such-command-t345")
    assert r.returncode == 127 and "not found" in r.stderr


@pytest.mark.skipif(not HAS_CARGO, reason="cargo not installed")
@pytest.mark.parametrize("tmpfs", [True, False])
def test_two_worktrees_never_share_a_target_dir(tmp_path, env, shm, tmpfs):  # SC 10, AC 18 (R5)
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm if tmpfs else "",
         "CARGO_TARGET_DIR": str(tmp_path / "shared-target")}  # a shared target set by the user
    ws(repo, e, "new", "k1")
    ws(repo, e, "new", "k2")
    (tmp_path / "wt-k2" / "src" / "lib.rs").write_text('pub const MARK: &str = "k2-only-mark";\n')
    cenv, _ = cargo_env(e, tmp_path)
    for name in ("k2", "k1"):  # R5 order: the changed worktree builds first
        r = ws(tmp_path / f"wt-{name}", cenv, "run", "--", "cargo", "build", "-q", timeout=300)
        assert r.returncode == 0, r.stderr
    found = {}
    for name in ("k1", "k2"):
        build = lease_of(repo, name)["build_dir"] or str(tmp_path / f"wt-{name}" / "target")
        rlib = os.path.join(build, "debug", "libt345crate.rlib")
        found[name] = open(rlib, "rb").read()
    assert b"k2-only-mark" in found["k2"] and b"k2-only-mark" not in found["k1"]
    assert b"base-mark" in found["k1"]
    assert not (tmp_path / "shared-target").exists()


# ── Slice 4: Claude Code hooks ───────────────────────────────────────────────────────────────


def hook(cwd, env, sub, event, timeout=60):
    return subprocess.run([sys.executable, SCRIPT, sub], cwd=cwd, env=env, input=json.dumps(event),
                          capture_output=True, text=True, timeout=timeout)


def test_hook_create_prints_the_path_last_and_records_the_session(tmp_path, env):  # AC 4
    repo = make_repo(tmp_path)
    r = hook(tmp_path, env, "hook-create", {"hook_event_name": "WorktreeCreate", "name": "h1",
                                            "cwd": str(repo), "session_id": "sess-1"})
    assert r.returncode == 0, r.stderr
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    assert lines[-1] == str(tmp_path / "wt-h1") and os.path.isabs(lines[-1])
    assert lease_of(repo, "h1")["session_id"] == "sess-1"


def test_hook_create_cleans_an_odd_name_and_reuses_an_existing_worktree(tmp_path, env):
    repo = make_repo(tmp_path)
    ev = {"name": "Feature X/1", "cwd": str(repo), "session_id": "s"}
    first = hook(tmp_path, env, "hook-create", ev)
    assert first.returncode == 0, first.stderr
    path = first.stdout.strip().splitlines()[-1]
    assert os.path.basename(path) == "wt-Feature-X-1"
    again = hook(tmp_path, env, "hook-create", ev)
    assert again.returncode == 0 and again.stdout.strip().splitlines()[-1] == path


def test_hook_create_failure_exits_non_zero(tmp_path, env):
    r = hook(tmp_path, env, "hook-create", {"name": "x", "cwd": str(tmp_path)})  # not a repo
    assert r.returncode != 0 and not r.stdout.strip()


def test_hook_remove_removes_or_refuses_and_keeps(tmp_path, env):  # AC 4, G3a
    repo = make_repo(tmp_path)
    keep = ws(repo, env, "new", "h2").stdout.strip()
    gone = ws(repo, env, "new", "h3").stdout.strip()
    commit_in(tmp_path / "wt-h2")
    r = hook(tmp_path, env, "hook-remove", {"worktree_path": keep, "cwd": str(repo)})
    assert r.returncode != 0 and os.path.isdir(keep) and "agent-ws/h2" in branches(repo)
    r = hook(tmp_path, env, "hook-remove", {"worktree_path": gone, "cwd": str(repo)})
    assert r.returncode == 0, r.stderr
    assert not os.path.exists(gone) and "agent-ws/h3" not in branches(repo)


def test_hook_env_exports_the_profile_and_never_a_target_dir(tmp_path, env):  # AC 13, AC 18
    repo = make_repo(tmp_path)
    env_file = tmp_path / "claude-env"
    r = hook(repo, {**env, "CLAUDE_ENV_FILE": str(env_file)}, "hook-env",
             {"hook_event_name": "SessionStart", "source": "startup", "cwd": str(repo)})
    assert r.returncode == 0 and r.stdout == ""
    text = env_file.read_text()
    assert f"export AGENT_WS_BIN={SCRIPT}" in text
    assert "CARGO_TARGET_DIR" not in text
    sourced = subprocess.run(["bash", "-c", f". {env_file}; echo \"$AGENT_WS_BIN\""],
                             capture_output=True, text=True).stdout.strip()
    assert sourced == SCRIPT


def test_hook_env_without_env_file_or_repo_is_quiet(tmp_path, env):
    r = hook(tmp_path, env, "hook-env", {"cwd": str(tmp_path)})
    assert r.returncode == 0 and r.stdout == ""


def test_hook_env_recreates_build_folders_after_reboot(tmp_path, env, shm):
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "h4")
    build = lease_of(repo, "h4")["build_dir"]
    shutil.rmtree(os.path.join(shm, f"agent-ws-{os.getuid()}"))
    r = hook(repo, {**e, "CLAUDE_ENV_FILE": str(tmp_path / "f")}, "hook-env", {"cwd": str(repo)})
    assert r.returncode == 0
    assert os.path.isdir(build) and stat.S_IMODE(os.lstat(build).st_mode) == 0o700


# ── Stage 4 review fixes ─────────────────────────────────────────────────────────────────────


def test_rm_refuses_unmerged_commits_on_a_detached_head_after_the_branch_is_gone(tmp_path, env):
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "x1")
    wt = tmp_path / "wt-x1"
    git(wt, "checkout", "-q", "--detach")
    commit_in(wt)
    git(repo, "branch", "-D", "agent-ws/x1")
    r = ws(repo, env, "rm", "x1")
    assert r.returncode == 1 and "HEAD" in r.stderr and wt.is_dir()


def test_rm_survives_a_pointer_file_the_user_deleted(tmp_path, env, shm):
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "x2")
    os.unlink(tmp_path / "wt-x2" / ".cargo" / "config.toml")
    r = ws(repo, e, "rm", "x2")
    assert r.returncode == 0, r.stderr
    assert not (tmp_path / "wt-x2").exists()


def test_rm_never_deletes_a_build_folder_off_tmpfs_even_if_the_lease_says_so(tmp_path, env):
    repo = make_repo(tmp_path)
    ws(repo, env, "new", "x3")
    fstype = subprocess.run(["stat", "-f", "-c", "%T", str(tmp_path)], capture_output=True,
                            text=True).stdout.strip()
    if fstype == "tmpfs":
        pytest.skip("tmp_path is tmpfs on this machine")
    victim = tmp_path / f"agent-ws-{os.getuid()}" / "r" / "keep"
    victim.mkdir(parents=True)
    (victim / "data").write_text("precious\n")
    lp = os.path.join(repo, ".git", "agent-ws", "leases", "x3.json")
    lease = json.load(open(lp))
    lease["build_dir"] = str(victim)  # a tampered lease
    open(lp, "w").write(json.dumps(lease))
    r = ws(repo, env, "rm", "x3")
    assert r.returncode == 1 and (victim / "data").read_text() == "precious\n"


def load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_ws_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gc_does_not_walk_build_folders_unless_dry_run(tmp_path, env, shm, monkeypatch):
    repo = make_repo(tmp_path, rust=True)
    e = {**env, "AGENT_WS_TMPFS_CANDIDATES": shm}
    ws(repo, e, "new", "y1", "--owner-pid", str(dead_pid()))
    open(os.path.join(lease_of(repo, "y1")["build_dir"], "f"), "w").write("x")
    mod = load_module()

    def vanished(_path):
        raise FileNotFoundError("a cargo build deleted it")
    monkeypatch.setattr(mod.os.path, "getsize", vanished)
    monkeypatch.chdir(repo)
    for k, v in e.items():
        monkeypatch.setenv(k, v)
    assert mod.cmd_gc([]) == 0  # no walk, no crash
    assert not (tmp_path / "wt-y1").exists()
    ws(repo, e, "new", "y2", "--owner-pid", str(os.getpid()))
    open(os.path.join(lease_of(repo, "y2")["build_dir"], "f"), "w").write("x")
    assert mod.cmd_gc(["--dry-run"]) == 0  # a vanished file is skipped, not fatal


def test_bad_owner_pid_and_broken_lease_are_refusals_not_tracebacks(tmp_path, env):
    repo = make_repo(tmp_path)
    r = ws(repo, env, "new", "z1", "--owner-pid", "abc")
    assert r.returncode == 1 and "Traceback" not in r.stderr
    leases = os.path.join(repo, ".git", "agent-ws", "leases")
    os.makedirs(leases, exist_ok=True)
    open(os.path.join(leases, "broken.json"), "w").write('{"name": "broken"}')
    for args in (["gc"], ["rm", "broken"], ["rm", str(tmp_path / "wt-none")]):
        r = ws(repo, env, *args)
        assert "Traceback" not in r.stderr, (args, r.stderr)
