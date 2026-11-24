"""T350 — `experiments/` stays on the owner's disk but out of the git repo.

The experiment harnesses (kit-arms, lean-kit) are not kit files: MANIFEST never lists them and no
test or CI runs them. They are untracked (`git rm -r --cached`) and ignored. History keeps them
(last tracked at 903328b9). No assertion about the files on disk: a fresh clone (CI) has none.
"""
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def test_experiments_is_not_tracked():
    assert _git("ls-files", "experiments").stdout == ""


def test_experiments_is_ignored():
    hit = _git("check-ignore", "-q", "experiments/kit-arms/run_arms.py")
    assert hit.returncode == 0, "experiments/ is not in .gitignore"


def test_manifest_never_ships_experiments():
    with open(os.path.join(ROOT, "MANIFEST"), encoding="utf-8") as fh:
        paths = [l.split()[0] for l in fh if l.strip() and not l.startswith(("#", "!"))]
    assert not any(p == "experiments" or p.startswith("experiments/") for p in paths)
