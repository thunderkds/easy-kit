"""T327 - scripts/cleanup_task.py: after a task is Done and merged, remove its linked worktree,
its merged branch and the processes running inside the worktree. Never unmerged or dirty work.

Every test builds a temp fixture repo (main checkout + linked worktree + fake board). The real
repo is never touched.
"""
import os
import subprocess
import sys
import time

import pytest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "scripts", "cleanup_task.py")
BRANCH = "feat/t900-demo"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=ENV,
                          check=True).stdout


def board(section, tid="T900", branch=BRANCH):
    return (f"### Done\n" + (f"- [x] **{tid}** - demo | Started: branch `{branch}`, worktree "
                             f"`../wt`\n" if section == "Done" else "") +
            "\n### Ready for Review\n" +
            (f"- [ ] **{tid}** - demo | Started: branch `{branch}`\n" if section == "Ready" else "") +
            "\n")


@pytest.fixture
def repo(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "-q", "-b", "main")
    (main / ".gitignore").write_text("build/\n")
    (main / "a.txt").write_text("a\n")
    (main / "PROJECT_KANBAN.md").write_text(board("Done"))
    git(main, "add", "-A")
    git(main, "commit", "-qm", "init")
    wt = tmp_path / "wt"
    git(main, "worktree", "add", "-q", "-b", BRANCH, str(wt))
    (wt / "b.txt").write_text("b\n")
    git(wt, "add", "-A")
    git(wt, "commit", "-qm", "work")
    (wt / "build").mkdir()
    (wt / "build" / "out.bin").write_text("x")
    return main, wt


def merge(main):
    git(main, "merge", "-q", "--no-ff", "-m", "merge", BRANCH)


def run(cwd, tid="T900"):
    return subprocess.run([sys.executable, SCRIPT, tid], cwd=str(cwd), capture_output=True,
                          text=True, env=ENV)


def branches(main):
    return git(main, "branch", "--list", BRANCH).strip()


def test_done_merged_clean_removes_worktree_and_branch(repo):
    main, wt = repo
    merge(main)
    out = run(main)
    assert out.returncode == 0, out.stdout + out.stderr
    assert not wt.exists() and not branches(main)
    assert "removed worktree" in out.stdout and "deleted branch" in out.stdout


def test_running_process_refuses_lists_it_and_is_left_alone(repo):
    main, wt = repo
    merge(main)
    proc = subprocess.Popen(["sleep", "60"], cwd=str(wt))
    try:
        out = run(main)
        assert out.returncode != 0
        assert str(proc.pid) in out.stdout and "sleep 60" in out.stdout
        assert proc.poll() is None  # no signal sent
        assert wt.exists() and branches(main)
        proc.terminate()
        proc.wait(timeout=5)
        again = run(main)
        assert again.returncode == 0, again.stdout + again.stderr
        assert not wt.exists() and not branches(main)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def test_process_in_a_subdirectory_via_symlink_is_found(repo, tmp_path):
    main, wt = repo
    merge(main)
    (wt / "build").mkdir(exist_ok=True)
    link = tmp_path / "link"
    link.symlink_to(wt / "build")
    proc = subprocess.Popen(["sleep", "60"], cwd=str(link))
    try:
        out = run(main)
        assert out.returncode != 0 and str(proc.pid) in out.stdout
        assert wt.exists()
    finally:
        proc.kill()
        proc.wait()


def test_main_checkout_and_other_worktree_untouched(repo, tmp_path):
    main, wt = repo
    other = tmp_path / "other"
    git(main, "worktree", "add", "-q", "-b", "feat/t901-other", str(other))
    merge(main)
    assert run(main).returncode == 0
    assert main.exists() and other.exists()
    assert git(main, "branch", "--list", "feat/t901-other").strip()


@pytest.mark.parametrize("section", ["Ready"])
def test_refuses_when_row_not_done(repo, section):
    main, wt = repo
    (main / "PROJECT_KANBAN.md").write_text(board(section))
    merge(main)
    out = run(main)
    assert out.returncode != 0
    assert wt.exists() and branches(main)


def test_refuses_when_branch_unmerged(repo):
    main, wt = repo
    out = run(main)
    assert out.returncode != 0
    assert wt.exists() and branches(main)


def test_refuses_dirty_worktree(repo):
    main, wt = repo
    merge(main)
    (wt / "untracked.txt").write_text("u")
    out = run(main)
    assert out.returncode != 0
    assert wt.exists() and branches(main)


def test_refuses_modified_tracked_file(repo):
    main, wt = repo
    merge(main)
    (wt / "b.txt").write_text("changed\n")
    assert run(main).returncode != 0
    assert wt.exists()


def test_second_run_is_idempotent(repo):
    main, wt = repo
    merge(main)
    assert run(main).returncode == 0
    again = run(main)
    assert again.returncode == 0, again.stdout + again.stderr
    assert "already clean" in again.stdout


def test_run_from_linked_worktree_removes_nothing(repo):
    main, wt = repo
    merge(main)
    out = run(wt)
    assert out.returncode == 0
    assert wt.exists() and branches(main)
    assert "linked worktree" in out.stdout


def test_bad_task_id_refused(repo):
    main, wt = repo
    out = run(main, "T900; rm -rf /")
    assert out.returncode != 0 and wt.exists()


def test_no_branch_in_row_uses_the_one_worktree_naming_the_task(repo):
    main, wt = repo
    (main / "PROJECT_KANBAN.md").write_text(
        "### Done\n- [x] **T900** - demo | no branch noted\n\n### Ready for Review\n")
    merge(main)
    assert run(main).returncode == 0
    assert not wt.exists() and not branches(main)


def test_task_with_nothing_left_is_already_clean(repo):
    main, wt = repo
    (main / "PROJECT_KANBAN.md").write_text(board("Done", tid="T902", branch="feat/t902-x"))
    out = run(main, "T902")
    assert out.returncode == 0 and "already clean" in out.stdout
    assert wt.exists()


def test_never_uses_force_flags():
    src = open(SCRIPT).read()
    for bad in ("--force", "branch\", \"-D", "SIGKILL", "SIGTERM", "os.kill", "\"clean\""):
        assert bad not in src
