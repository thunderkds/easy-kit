#!/usr/bin/env python3
"""T370 — the default branch is the setting `EASY_KIT_DEFAULT_BRANCH` (`.claude/settings.json`
`"env"`, default `main`), never a git ref an agent can write.

AC 1 — `auto_mode.default_branch()`: unset or blank is `main`; a plain branch name is itself; any
       other value (an option, a range, `HEAD`, a space, `.lock`) is None.
AC 2 — a `master` repo with the setting `master`: the `[admin]` merge of the task branch and the
       push of `master` after it are allowed; with the setting unset the push stays refused
       (today; the merge never checked its target branch, so it already ran).
AC 3 — a bad setting refuses every `[admin]` merge and push, and the refusal names the setting.
AC 4 — `verify_record.base_ref()` follows the setting; None for a bad value.

Run with: python3 -m pytest .claude/hooks/tests/test_t370_default_branch.py -q -p no:cacheprovider
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, git, kanban, merge_gate  # noqa: E402
from test_admin_tag import (  # noqa: E402
    auto_verified, bash, reason, result, session)

import auto_mode  # noqa: E402
import verify_record  # noqa: E402

assert gate and merge_gate  # the fixtures, imported for pytest

ENV = "EASY_KIT_DEFAULT_BRANCH"
BAD = ["HEAD", "-x", "a..b", "a b", "x.lock", "/x", "x/", ".x", "a//b", "a@{1}", "refs/heads/../x"]


# ── AC 1 ──────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("value", [None, "", "   "])
def test_ac1_unset_or_blank_is_main(monkeypatch, value):
    if value is None:
        monkeypatch.delenv(ENV, raising=False)
    else:
        monkeypatch.setenv(ENV, value)
    assert auto_mode.default_branch() == "main"


@pytest.mark.parametrize("value", ["master", "trunk", "release/2.x", "dev_1"])
def test_ac1_a_plain_branch_name_is_itself(monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    assert auto_mode.default_branch() == value


@pytest.mark.parametrize("value", BAD)
def test_ac1_any_other_value_is_none(monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    assert auto_mode.default_branch() is None


# ── AC 2 ──────────────────────────────────────────────────────────────────────────────────
def to_master(fx):
    """Rename the fixture's `main` to `master`, here and on its bare `origin`."""
    git(fx.main, "branch", "-m", "main", "master")
    git(fx.main, "push", "-q", "origin", "master")
    git(fx.main, "push", "-q", "origin", "--delete", "main")
    git(fx.main, "fetch", "-q", "--prune", "origin")


def test_ac2_a_master_repo_with_the_setting_may_merge(gate, tmp_path, monkeypatch):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    to_master(fx)
    monkeypatch.setenv(ENV, "master")
    assert reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "do it [admin]")) is None


def master_merged_session(tmp_path, fx):
    git(fx.main, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    return session(tmp_path, fx, "do it [admin]",
                   extra=[bash(MERGE + " --no-ff feat/t900-x", fx.main, -200), result()])


@pytest.mark.parametrize("command", [PUSH + " origin master", PUSH], ids=["named", "bare"])
def test_ac2_a_master_repo_with_the_setting_may_push_master_after_its_merge(
        gate, tmp_path, monkeypatch, command):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    to_master(fx)
    git(fx.main, "branch", "--set-upstream-to=origin/master", "master")
    monkeypatch.setenv(ENV, "master")
    assert reason(command, fx.main, master_merged_session(tmp_path, fx)) is None


def test_ac2_control_without_the_setting_a_master_push_is_refused(gate, tmp_path, monkeypatch):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    to_master(fx)
    git(fx.main, "branch", "--set-upstream-to=origin/master", "master")
    monkeypatch.delenv(ENV, raising=False)
    text = reason(PUSH + " origin master", fx.main, master_merged_session(tmp_path, fx))
    assert text is not None, "a `master` push must stay refused while the default is `main`"


def test_ac2_with_the_setting_main_is_no_longer_the_pushable_branch(gate, tmp_path, monkeypatch):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    to_master(fx)
    git(fx.main, "branch", "main", "master")  # an agent-made `main` beside the real default
    monkeypatch.setenv(ENV, "master")
    text = reason(PUSH + " origin main", fx.main, master_merged_session(tmp_path, fx))
    assert text is not None, "only the set default branch may be pushed after the merge"


# ── AC 3 ──────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("value", ["HEAD", "-x", "a..b"])
def test_ac3_a_bad_setting_refuses_the_merge_and_names_the_setting(gate, tmp_path, monkeypatch,
                                                                  value):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    monkeypatch.setenv(ENV, value)
    text = reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "do it [admin]"))
    assert text is not None and ENV in text and "None" not in text, text


def test_ac3_a_bad_setting_refuses_the_main_push(gate, tmp_path, monkeypatch):
    fx = gate(kanban(done=("T900",)))
    auto_verified(fx)
    git(fx.main, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    path = session(tmp_path, fx, "do it [admin]",
                   extra=[bash(MERGE + " --no-ff feat/t900-x", fx.main, -200), result()])
    monkeypatch.setenv(ENV, "a..b")
    text = reason(PUSH + " origin main", fx.main, path)
    assert text is not None and ENV in text, text


# ── AC 4 ──────────────────────────────────────────────────────────────────────────────────
def docs_only_repo(tmp_path):
    """A repo on `main` and a branch that changes one docs-only file: (checkout, base, tip)."""
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "feat/t900-x")
    os.makedirs(os.path.join(repo, "docs"))
    with open(os.path.join(repo, "docs", "note.md"), "w", encoding="utf-8") as f:
        f.write("x\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs")
    return repo, base, git(repo, "rev-parse", "HEAD")


def test_ac4_a_bad_setting_fails_the_docs_only_verify_closed(tmp_path, monkeypatch):
    """Reviewer P2-1: `_base()` raises inside the fail-closed `try`s, never falls back to `main`."""
    repo, base, tip = docs_only_repo(tmp_path)
    skip = {"verdict": verify_record.SKIP_PASS, "base": base, "commit": tip}
    monkeypatch.delenv(ENV, raising=False)
    assert verify_record.docs_only_change(repo, tip) == (base, ["docs/note.md"])
    assert verify_record.record_confirms_pass(repo, skip) is True
    monkeypatch.setenv(ENV, "a..b")
    assert verify_record.docs_only_change(repo, tip) is None
    assert verify_record.record_confirms_pass(repo, skip) is False
    assert verify_record.shell_suites_changed(repo, tip) == []


def test_ac4_the_verify_base_follows_the_setting(monkeypatch):
    monkeypatch.delenv(ENV, raising=False)
    assert verify_record.base_ref() == "refs/heads/main"
    monkeypatch.setenv(ENV, "master")
    assert verify_record.base_ref() == "refs/heads/master"
    monkeypatch.setenv(ENV, "a..b")
    assert verify_record.base_ref() is None
