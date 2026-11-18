#!/usr/bin/env python3
"""T326 — `_main_push_refusal` decides the same on git older than 2.38 (no `merge-tree --write-tree`)
as on new git (`tasks/TASK_GUIDE_T326.md`, AC 1-5). Every repo here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t326_old_git_main_push.py -v
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import GIT_ENV, git, merge_gate, write  # noqa: E402


@pytest.fixture(params=["real", "forced-old"])
def mode(request, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    if request.param == "forced-old":
        monkeypatch.setattr(merge_gate, "_git_has_write_tree", lambda where: False)
    return request.param


def build(tmp_path):
    """`origin` (bare) with `main`; branch `feat/t900-x` one commit ahead; returns the work repo."""
    bare, work = tmp_path / "origin.git", tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", str(bare))
    git(tmp_path, "init", "-q", "-b", "main", str(work))
    git(work, "remote", "add", "origin", str(bare))
    write(work / "a.txt", "a\n")
    write(work / "b.txt", "b\n")
    git(work, "add", "."), git(work, "commit", "-q", "-m", "base")
    git(work, "push", "-q", "origin", "main")
    git(work, "checkout", "-q", "-b", "feat/t900-x")
    write(work / "b.txt", "b2\n")
    git(work, "commit", "-q", "-am", "branch change")
    git(work, "checkout", "-q", "main")
    return work


def diverge(work):
    """The remote's `main` moves on (a different file), so a real merge commit is needed."""
    write(work / "a.txt", "a2\n")
    git(work, "commit", "-q", "-am", "main moves")
    git(work, "push", "-q", "origin", "main")


def test_clean_merge_commit_is_allowed(mode, tmp_path):
    work = build(tmp_path)
    diverge(work)
    git(work, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    assert merge_gate._main_push_refusal(str(work), "feat/t900-x") is None


def test_extra_change_in_the_merge_commit_is_refused(mode, tmp_path):
    work = build(tmp_path)
    diverge(work)
    git(work, "merge", "-q", "--no-ff", "--no-commit", "feat/t900-x")
    write(work / "extra.txt", "x\n")
    git(work, "add", "extra.txt"), git(work, "commit", "-q", "-m", "T900 merge")
    text = merge_gate._main_push_refusal(str(work), "feat/t900-x")
    assert text and "changes files" in text, text


def test_conflicting_merge_is_refused(mode, tmp_path):
    work = build(tmp_path)
    write(work / "b.txt", "b3\n")
    git(work, "commit", "-q", "-am", "main edits b")
    git(work, "push", "-q", "origin", "main")
    done = subprocess.run(["git", "-C", str(work), "merge", "--no-ff", "feat/t900-x"],
                          capture_output=True, text=True, env={**os.environ, **GIT_ENV})
    assert done.returncode != 0
    write(work / "b.txt", "resolved\n")
    git(work, "add", "b.txt"), git(work, "commit", "-q", "-m", "T900 merge")
    assert merge_gate._main_push_refusal(str(work), "feat/t900-x")


def test_fallback_leaves_index_and_refs_alone(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(merge_gate, "_git_has_write_tree", lambda where: False)
    work = build(tmp_path)
    diverge(work)
    git(work, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    before = (git(work, "status", "--porcelain"), git(work, "for-each-ref"),
              (work / ".git" / "index").read_bytes())
    assert merge_gate._main_push_refusal(str(work), "feat/t900-x") is None
    assert before == (git(work, "status", "--porcelain"), git(work, "for-each-ref"),
                      (work / ".git" / "index").read_bytes())


def test_fallback_refuses_when_git_fails(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(merge_gate, "_git_has_write_tree", lambda where: False)
    work = build(tmp_path)
    diverge(work)
    git(work, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    real = merge_gate.subprocess.run

    def broken(cmd, *a, **k):
        if "read-tree" in cmd:
            raise OSError("boom")
        return real(cmd, *a, **k)
    monkeypatch.setattr(merge_gate.subprocess, "run", broken)
    assert merge_gate._main_push_refusal(str(work), "feat/t900-x")


def test_criss_cross_merge_bases_are_refused(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(merge_gate, "_git_has_write_tree", lambda where: False)
    work = build(tmp_path)
    # remote main and the branch each merged the other's earlier commit: two merge bases
    write(work / "c.txt", "c\n")
    git(work, "add", "c.txt"), git(work, "commit", "-q", "-m", "main c")
    m1 = git(work, "rev-parse", "HEAD")
    git(work, "checkout", "-q", "feat/t900-x")
    write(work / "d.txt", "d\n")
    git(work, "add", "d.txt"), git(work, "commit", "-q", "-m", "branch d")
    d1 = git(work, "rev-parse", "HEAD")
    git(work, "merge", "-q", "--no-ff", "-m", "b<-m1", m1)
    git(work, "checkout", "-q", "main")
    git(work, "merge", "-q", "--no-ff", "-m", "m<-d1", d1)
    git(work, "push", "-q", "origin", "main")
    write(work / "e.txt", "e\n")
    git(work, "add", "e.txt"), git(work, "commit", "-q", "-m", "main e")
    git(work, "push", "-q", "origin", "main")
    git(work, "checkout", "-q", "feat/t900-x")
    write(work / "f.txt", "f\n")
    git(work, "add", "f.txt"), git(work, "commit", "-q", "-m", "branch f")
    git(work, "checkout", "-q", "main")
    git(work, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    # whatever the shape, it must be decided without error; refuse only if not a single base
    text = merge_gate._main_push_refusal(str(work), "feat/t900-x")
    bases = git(work, "merge-base", "--all", "HEAD^1", "HEAD^2").split()
    assert (len(bases) > 1) == bool(text) or len(bases) == 1
