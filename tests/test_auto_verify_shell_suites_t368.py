"""T368 — a branch that changes a shell test suite asks `/verify` for a real run of it, not a SKIP.

T367 changed only `tests/test_pack_catalog.sh`: both auto verify runs answered SKIP ("no runtime
surface: tests-only"), and a SKIP is a pass only for docs-only paths, which never include a `.sh`
file (T289). Now the hook names each changed `tests/**/test_*.sh` suite in the `/verify` request and
asks for PASS or FAIL by its exit code. The docs-only list, the record and the merge gate are unchanged.

  SC1  a changed `tests/test_x.sh` (or `.claude/hooks/tests/test_x.sh`) -> the long request names it
  SC2  no changed shell suite -> the request is exactly `/verify <ID>`, as before
  SC3  `tests/lib/x.sh`, a non-`test_*.sh` name, an unsafe name, a symlink -> not named
  SC4  any git doubt (missing `main`, a bad sha) -> nothing named, never an exception
  SC5  the docs say both new rules (fix rounds; the shell-suite request)

Every git repo and `claude` here is constructed; the real `claude` never runs.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / ".claude" / "hooks" / "lib"))
import test_auto_verify as tav  # noqa: E402  (module only: its tests are not re-collected)
import verify_record as vr  # noqa: E402

TRACKS = REPO / "docs" / "claude-md" / "tracks.md"


def _commit(checkout, rel, text="x\n", link=None):
    path = Path(checkout) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if link:
        os.symlink(link, path)
    else:
        path.write_text(text, encoding="utf-8")
    tav._git(checkout, "add", "-A")
    tav._git(checkout, "commit", "-qm", f"change {rel}")


def _request(tmp_path, changes=()):
    """Run the real Stop hook on a task branch with `changes` committed; return the `-p` argument."""
    project, checkout = tav._project(tmp_path, worktree=True)
    for rel in changes:
        _commit(checkout, rel)
    stub_dir, calls = tav._stub(tmp_path)
    tav._stop(project, tav._env(tmp_path, project, stub_dir))
    tav._wait_row(checkout)
    [call] = tav._calls(calls)
    assert call["argv"][0] == "-p"
    return call["argv"][1]


# ── SC1 ────────────────────────────────────────────────────────────────────────────────────────
def test_sc1_a_changed_shell_suite_is_named_with_a_pass_or_fail_ask(tmp_path):
    ask = _request(tmp_path, ["tests/test_x.sh", ".claude/hooks/tests/test_y.sh", "tests/test_z.py"])
    assert ask.startswith(f"/verify {tav.TASK} ")
    assert "tests/test_x.sh" in ask and ".claude/hooks/tests/test_y.sh" in ask
    assert "tests/test_z.py" not in ask
    assert "exit code" in ask and "PASS or FAIL" in ask


# ── SC2 ────────────────────────────────────────────────────────────────────────────────────────
def test_sc2_no_shell_suite_keeps_the_plain_request(tmp_path):
    assert _request(tmp_path, ["tests/test_z.py", "docs/note.md"]) == f"/verify {tav.TASK}"


# ── SC3 / SC4: the helper ──────────────────────────────────────────────────────────────────────
def _branch(tmp_path, changes, links=()):
    project, checkout = tav._project(tmp_path, worktree=True)
    for rel in changes:
        _commit(checkout, rel)
    for rel, target in links:
        _commit(checkout, rel, link=target)
    return str(checkout), tav._git(checkout, "rev-parse", "HEAD")


def test_sc3_only_test_star_sh_suites_under_the_test_dirs_are_named(tmp_path):
    checkout, head = _branch(tmp_path, ["tests/lib/helper.sh", "tests/run_all.sh", "scripts/test_a.sh",
                                        "tests/test_ok.sh", "tests/sub/test_deep.sh"])
    assert vr.shell_suites_changed(checkout, head) == ["tests/sub/test_deep.sh", "tests/test_ok.sh"]


def test_sc3_a_symlinked_suite_and_an_unsafe_name_are_not_named(tmp_path):
    checkout, head = _branch(tmp_path, ["tests/test_spa ce.sh"], links=[("tests/test_link.sh", "../x")])
    assert vr.shell_suites_changed(checkout, head) == []


def test_sc3_a_suite_added_then_deleted_on_the_branch_is_not_named(tmp_path):
    checkout, head = _branch(tmp_path, ["tests/test_gone.sh", "tests/test_kept.sh"])
    assert vr.shell_suites_changed(checkout, head) == ["tests/test_gone.sh", "tests/test_kept.sh"]
    tav._git(checkout, "rm", "-q", "tests/test_gone.sh")
    tav._git(checkout, "commit", "-qm", "drop it")
    assert vr.shell_suites_changed(checkout, tav._git(checkout, "rev-parse", "HEAD").strip()) == [
        "tests/test_kept.sh"]


def test_sc4_git_doubt_names_nothing(tmp_path):
    checkout, head = _branch(tmp_path, ["tests/test_ok.sh"])
    assert vr.shell_suites_changed(checkout, "not-a-sha") == []
    assert vr.shell_suites_changed(str(tmp_path / "nowhere"), head) == []
    tav._git(checkout, "update-ref", "-d", "refs/heads/main")
    assert vr.shell_suites_changed(checkout, head) == []


# ── SC5: the docs ──────────────────────────────────────────────────────────────────────────────
def _admin_tag():
    text = TRACKS.read_text(encoding="utf-8")
    return text.split("\n### Admin tag\n", 1)[1].split("\n### ", 1)[0]


def test_sc5_a_fail_starts_a_fix_round_at_most_two():
    section = _admin_tag()
    assert "A `fail` is never retried" not in section
    assert "fix round" in section and "at most 2" in section
    assert "Reviewer: <ID>" in section


def test_sc5_the_shell_suite_request_is_documented():
    text = TRACKS.read_text(encoding="utf-8")
    assert "test_*.sh" in text and "exit code" in text and "T368" in text
