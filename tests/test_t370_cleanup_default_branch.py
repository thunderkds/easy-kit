"""T370 AC 5 — `scripts/cleanup_task.py` judges "merged" against the set default branch
(`EASY_KIT_DEFAULT_BRANCH`, default `main`), and refuses on a bad value.

Run with: python3 -m pytest tests/test_t370_cleanup_default_branch.py -q -p no:cacheprovider
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_cleanup_task import BRANCH, ENV, SCRIPT, branches, git, merge, repo  # noqa: E402

assert repo  # the fixture, imported for pytest


def run(cwd, extra):
    return subprocess.run([sys.executable, SCRIPT, "T900"], cwd=str(cwd), capture_output=True,
                          text=True, env={**ENV, **extra})


def test_ac5_a_master_repo_with_the_setting_is_cleaned(repo):
    main, wt = repo
    git(main, "branch", "-m", "main", "master")
    merge(main)
    out = run(main, {"EASY_KIT_DEFAULT_BRANCH": "master"})
    assert out.returncode == 0, out.stdout + out.stderr
    assert not wt.exists() and not branches(main)


def test_ac5_control_a_master_repo_without_the_setting_is_refused(repo):
    main, wt = repo
    git(main, "branch", "-m", "main", "master")
    merge(main)
    env = {k: v for k, v in ENV.items() if k != "EASY_KIT_DEFAULT_BRANCH"}
    out = subprocess.run([sys.executable, SCRIPT, "T900"], cwd=str(main), capture_output=True,
                         text=True, env=env)
    assert out.returncode != 0 and wt.exists() and BRANCH in branches(main)


def test_ac5_a_bad_setting_refuses_and_removes_nothing(repo):
    main, wt = repo
    merge(main)
    out = run(main, {"EASY_KIT_DEFAULT_BRANCH": "a..b"})
    assert out.returncode != 0 and "EASY_KIT_DEFAULT_BRANCH" in out.stdout + out.stderr
    assert wt.exists() and BRANCH in branches(main)
