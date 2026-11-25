"""T347: CI ran `tests/test_readme_current.sh` red on `main`.

The README names the Codex-skipped skills inline (`Skills currently affected: `a`, `b`.`),
because the README is held to 75 lines (`tests/test_readme_slim.py`). The shell test's
reverse check read only a bullet list after "Skills currently", so it parsed no names and
failed. These tests pin that the check reads the list as the README writes it, in both
directions.
"""
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join("tests", "test_readme_current.sh")


def _copy_repo_bits(tmp_path):
    for rel in ("README.md", "RUNBOOK.md", os.path.join("lib", "harness-fetch.sh"), SCRIPT):
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), dest)
    shutil.copytree(os.path.join(ROOT, "skills"), tmp_path / "skills", symlinks=True)
    return tmp_path


def _run(root):
    return subprocess.run(["sh", os.path.join(str(root), SCRIPT)], capture_output=True,
                          text=True, timeout=60)


def test_readme_current_passes_on_the_repo():
    result = _run(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "could not parse any skill names" not in result.stderr


NONE = "affected: none (long skills keep their detail in reference files)."


def _oversize(root, *names):
    """Pad each named fixture skill past the 8192-byte cap (T355: no real skill is over it)."""
    for name in names:
        path = root / "skills" / name / "SKILL.md"
        path.write_text(path.read_text() + "x" * 9000 + "\n")


def test_reverse_check_reads_every_inline_name(tmp_path):
    root = _copy_repo_bits(tmp_path)
    names = ("bugfix", "diagnose")
    _oversize(root, *names)
    readme = root / "README.md"
    readme.write_text(readme.read_text().replace(NONE, "affected: `bugfix`, `diagnose`."))
    result = _run(root)
    assert result.returncode == 0, result.stdout + result.stderr
    for name in names:
        assert f"AC2 (reverse): README-listed skill '{name}' is still over" in result.stdout


def test_an_oversize_skill_the_readme_omits_fails(tmp_path):
    root = _copy_repo_bits(tmp_path)
    _oversize(root, "diagnose")
    result = _run(root)
    assert result.returncode == 1
    assert "README does not name currently-oversize skill 'diagnose'" in result.stderr


def test_none_with_no_oversize_skill_passes_and_says_so():
    result = _run(ROOT)
    assert "AC2: README says no skill is skipped today" in result.stdout


def test_a_stale_inline_name_fails(tmp_path):
    root = _copy_repo_bits(tmp_path)
    readme = root / "README.md"
    text = readme.read_text()
    assert NONE in text
    readme.write_text(text.replace(NONE, "affected: `tdd`."))
    result = _run(root)
    assert result.returncode == 1
    assert "README lists 'tdd' as skipped, but it is no longer over" in result.stderr
