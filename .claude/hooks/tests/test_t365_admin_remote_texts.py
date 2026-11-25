#!/usr/bin/env python3
"""T365 — the T321 follow-ups in the merge gate's refusal texts (`tasks/TASK_GUIDE_T365.md`).

  * AC 1: `EASY_KIT_ADMIN_REMOTE` naming a remote this repository does not have is refused with
    "no remote `<name>`", not the generic "allows only a plain push" text.
  * AC 2: under a value that is not a plain remote name, the `[ticket]` merge refusal and
    `_main_push_refusal` never print `None`.
  * AC 3: the `_own_origin_refusal` and `_remote_main` docstrings name the admin remote, not `origin`.

Every repo, board, record and transcript here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t365_admin_remote_texts.py -q -p no:cacheprovider
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, kanban, merge_gate  # noqa: E402
from test_admin_tag import auto_verified, reason, session  # noqa: E402
from test_t317_loop_binding import BRANCH, TAG_AT, pass_written_at  # noqa: E402
from test_t317_fix_round import _loop  # noqa: E402
from test_t321_admin_remote import BAD, ENV, own_remote  # noqa: E402

assert gate  # the fixture, imported for pytest


# ══ AC 1 — a set remote that does not exist: "no remote", named ════════════════════════════════
@pytest.mark.parametrize("command", [PUSH + " github " + BRANCH, PUSH],
                         ids=["named", "bare"])
def test_ac1_a_missing_set_remote_is_named(gate, tmp_path, monkeypatch, command):
    monkeypatch.setenv(ENV, "github")
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)  # `origin` only: no `github` remote
    text = reason(command, fx.wt, session(tmp_path, fx, "do it [admin]"))
    assert text is not None and "no remote `github`" in text, text
    # the setting is named by the refusal itself, not only by the AUTO_MODE_LIMIT text `reason` adds
    own = merge_gate._missing_remote_refusal(fx.wt)
    assert own is not None and ENV in own and "`github`" in own, own


def test_ac1_the_ticket_push_names_the_missing_remote_too(gate, tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, "github")
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    text = reason(PUSH + " github " + BRANCH, fx.wt, _loop(tmp_path, "ticket"))
    assert text is not None and "no remote `github`" in text, text


def test_ac1_control_the_remote_exists_and_the_push_runs(gate, tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, "github")
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    own_remote(fx, "github")
    assert reason(PUSH + " github " + BRANCH, fx.wt, session(tmp_path, fx, "do it [admin]")) is None


@pytest.mark.parametrize("returncode,stderr,named", [
    (2, "error: No such remote 'github'", True),
    (128, "fatal: not a git repository (or any of the parent directories): .git", False),
    (1, "error: could not lock config file", False),
    (0, "", False),
], ids=["no-such-remote", "not-a-repo", "other-error", "found"])
def test_ac1_only_git_no_such_remote_counts_as_missing(monkeypatch, returncode, stderr, named):
    """Another `git remote get-url` failure is not "no remote": the later checks refuse it."""
    import subprocess
    monkeypatch.setenv(ENV, "github")
    done = subprocess.CompletedProcess(["git"], returncode, stdout="", stderr=stderr)
    monkeypatch.setattr(merge_gate, "_git", lambda *a, **k: done)
    text = merge_gate._missing_remote_refusal("/nowhere")
    assert (text is not None) is named, text
    monkeypatch.setattr(merge_gate, "_git", lambda *a, **k: None)  # git could not run at all
    assert merge_gate._missing_remote_refusal("/nowhere") is None


# ══ AC 2 — a bad value: no refusal prints `None` ═══════════════════════════════════════════════
@pytest.mark.parametrize("value", BAD)
def test_ac2_the_ticket_merge_refusal_never_prints_none(gate, tmp_path, monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    text = reason(MERGE + " " + BRANCH, fx.main, _loop(tmp_path, "ticket"))
    assert text is not None and "`None`" not in text and "[ticket]" in text, text


@pytest.mark.parametrize("value", BAD)
def test_ac2_main_push_refusal_names_the_setting_not_none(gate, monkeypatch, value):
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    monkeypatch.setenv(ENV, value)
    text = merge_gate._main_push_refusal(fx.main, BRANCH)
    assert text is not None and "None" not in text and ENV in text, text


# ══ AC 3 — the docstrings name the admin remote ════════════════════════════════════════════════
def test_ac3_docstrings_name_the_admin_remote():
    own = merge_gate._own_origin_refusal.__doc__
    main = merge_gate._remote_main.__doc__
    assert "_admin_remote" in own and "its `origin` has the URL" not in own, own
    assert "_admin_remote" in main and "ls-remote origin" not in main, main
