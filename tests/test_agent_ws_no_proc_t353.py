"""T353 - agent-ws degrades on a machine with no /proc (macOS): hook-create still makes the
worktree and prints its path, so a teammate who clones an opted-in project keeps a working
`claude --worktree`. /proc is hidden in-process; native Windows (no fcntl) stays unsupported."""
import builtins
import importlib.util
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "agent_ws.py")


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def test_hook_create_without_proc_makes_the_worktree_and_prints_its_path(tmp_path, monkeypatch, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.1.0"\n')
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "init")

    spec = importlib.util.spec_from_file_location("agent_ws_no_proc", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    real_open, real_isdir, real_readlink = builtins.open, os.path.isdir, os.readlink

    def no_proc_open(path, *a, **k):
        if str(path).startswith("/proc/"):
            raise FileNotFoundError(path)
        return real_open(path, *a, **k)
    monkeypatch.setattr(builtins, "open", no_proc_open)
    monkeypatch.setattr(os.path, "isdir", lambda p: False if str(p).startswith("/proc") else real_isdir(p))
    monkeypatch.setattr(os, "readlink", lambda p: (_ for _ in ()).throw(FileNotFoundError(p))
                        if str(p).startswith("/proc/") else real_readlink(p))
    monkeypatch.delenv("AGENT_WS_TMPFS_CANDIDATES", raising=False)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"name": "mac1", "cwd": str(repo)})))

    assert mod.cmd_hook_create([]) == 0
    out = capsys.readouterr()
    path = str(tmp_path / "wt-mac1")
    assert out.out.strip().splitlines()[-1] == path
    assert os.path.isdir(path)
    assert "on-disk target/" in out.err  # no /proc/self/mounts: no tmpfs, builds on disk

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"worktree_path": path, "cwd": str(repo)})))
    assert mod.cmd_hook_remove([]) == 0  # no process check without /proc, but the rest still guards
    assert not os.path.exists(path)
