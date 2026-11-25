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
