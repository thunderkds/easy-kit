"""T355 — no kit skill is over Codex's skill-body cap, and the split lost no text.

  SC1 — every `skills/*/SKILL.md` is at most the cap `lib/harness-fetch.sh` gives Codex (8192 bytes).
  SC2 — for the 4 skills T355 split (`bugfix`, `craft-spawn-prompt`, `diagnose`, `write-better-skill`),
        every non-blank line of the pre-split `SKILL.md` (commit BASE) is still a line of that
        skill's `SKILL.md` or of one of its `references/*.md` files: text moved, none dropped.
  SC2b — each `references/*.md` file of those skills is named in its `SKILL.md` (a pointer exists).
"""
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
BASE = "f6292ac9"  # main when T355 started: the last commit with the oversize bodies
SPLIT = ("bugfix", "craft-spawn-prompt", "diagnose", "write-better-skill")


def _codex_cap():
    text = (ROOT / "lib" / "harness-fetch.sh").read_text(encoding="utf-8")
    m = re.search(r"codex\)\s*printf\s*'(\d+)'", text)
    assert m, "could not read the Codex cap from lib/harness-fetch.sh"
    return int(m.group(1))


def test_sc1_no_skill_over_the_codex_cap():
    cap = _codex_cap()
    over = {p.parent.name: p.stat().st_size for p in sorted(SKILLS.glob("*/SKILL.md"))
            if p.stat().st_size > cap}
    assert not over, f"SKILL.md over the {cap}-byte Codex cap (Codex would skip them): {over}"


def _base_text(name):
    try:
        return subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:skills/{name}/SKILL.md"],
                              capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip(f"base commit {BASE} not in this clone (shallow?)")


def _lines(text):
    return {ln.strip() for ln in text.splitlines() if ln.strip()}


@pytest.mark.parametrize("name", SPLIT)
def test_sc2_split_moved_every_line(name):
    old = _lines(_base_text(name))
    new = _lines((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))
    for ref in sorted((SKILLS / name / "references").glob("*.md")):
        new |= _lines(ref.read_text(encoding="utf-8"))
    lost = sorted(old - new)
    assert not lost, f"{name}: {len(lost)} line(s) of the pre-split SKILL.md are gone: {lost[:5]}"


@pytest.mark.parametrize("name", SPLIT)
def test_sc2b_every_reference_has_a_pointer(name):
    body = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    refs = sorted((SKILLS / name / "references").glob("*.md"))
    missing = [r.name for r in refs if f"references/{r.name}" not in body]
    assert not missing, f"{name}: SKILL.md never points to {missing}"
