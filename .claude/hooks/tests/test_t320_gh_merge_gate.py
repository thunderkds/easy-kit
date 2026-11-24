#!/usr/bin/env python3
"""T320 — the merge gate treats `gh pr merge` and the GitHub merge API as merges
(`tasks/TASK_GUIDE_T320.md`, AC 1-5). Every board, transcript and repo here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t320_gh_merge_gate.py -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import gate, kanban, merge_gate, reason  # noqa: E402
from test_admin_tag import human, transcript  # noqa: E402

assert gate  # the fixture, imported for pytest

MERGES = [
    "gh pr merge 12 --squash",
    "gh -R o/r pr merge 12",
    "gh --repo o/r pr merge 12",
    "cd x && gh pr merge 12",
    "gh api -X PUT repos/o/r/merges -f base=main -f head=x",
    "gh api repos/o/r/pulls/3/merge -X PUT",
]
IDS = ["pr-merge", "short-repo-flag", "long-repo-flag", "after-cd", "merges-api", "pulls-merge-api"]
READ_ONLY = ["gh pr view 12", "gh pr list", "gh api repos/o/r/pulls/3", "gh pr create --fill",
             'echo "gh pr merge 12"', 'grep -n "gh pr merge" notes.md']


@pytest.mark.parametrize("command", MERGES, ids=IDS)
def test_ac1_ac2_gh_merge_is_blocked_with_the_merge_message_while_a_task_is_open(gate, command):
    fx = gate(kanban(in_progress=("T900",)))
    text = reason(command, fx.main)
    assert text is not None, f"{command!r} must be gated like a merge"
    assert "cannot push/merge" in text and "Tasks still In Progress: T900" in text


@pytest.mark.parametrize("command", MERGES, ids=IDS)
def test_ac3_gh_merge_is_allowed_with_a_clean_board(gate, command):
    fx = gate(kanban(done=("T900",)))
    assert reason(command, fx.main) is None


@pytest.mark.parametrize("command", MERGES, ids=IDS)
def test_ac4_gh_merge_is_blocked_in_auto_mode_even_with_a_clean_board(gate, tmp_path, command):
    fx = gate(kanban(done=("T900",)))
    path = transcript(tmp_path, [human("finish the work [admin]")])
    text = reason(command, fx.main, transcript=path)
    assert text is not None and "Auto-mode gate" in text, f"{command!r} must be the user's in auto mode"


@pytest.mark.parametrize("command", READ_ONLY)
def test_ac5_read_only_gh_commands_and_quoted_mentions_are_allowed(gate, command):
    fx = gate(kanban(in_progress=("T900",)))
    assert reason(command, fx.main) is None


# ---------------------------------------------------------------------------
# Review round 1 (tasks/TASK_REVIEW_T320.md): hidden forms, GraphQL, the ref API, `merge-base`
# ---------------------------------------------------------------------------
QUOTED_VERB = [
    'gh pr "merge" 1',
    'gh "pr" merge 1',
    "gh pr 'merge' 1",
    "gh api repos/o/r/pulls/3/'merge' -X PUT",
    'gh pr me"rge" 1',
]
VARIABLE_VERB = ["gh pr $cmd 1", "gh pr $(echo merge) 1", "gh pr `echo merge` 1"]
OTHER_MERGES = [
    """gh api graphql -f query='mutation { mergePullRequest(input: {pullRequestId: "X"}) { clientMutationId } }'""",
    "gh api repos/o/r/git/refs/heads/main -X PATCH -f sha=abc",
    "gh api repos/o/r/git/refs/heads/main --method PATCH -f sha=abc",
]
STILL_ALLOWED = [
    "gh pr merge-base-notes",
    "gh api repos/o/r/git/refs/heads/main",
    "echo 'gh api graphql mergePullRequest'",
    'echo "gh pr \\"merge\\" 1"',
    "gh pr create --title 'merge docs'",
    'gh api repos/o/r/issues -f title="merge notes"',
]


@pytest.mark.parametrize("command", QUOTED_VERB + VARIABLE_VERB + OTHER_MERGES)
def test_round1_hidden_and_other_merge_forms_are_blocked_while_a_task_is_open(gate, command):
    fx = gate(kanban(in_progress=("T900",)))
    text = reason(command, fx.main)
    assert text is not None and "cannot push/merge" in text, f"{command!r} must be gated"


@pytest.mark.parametrize("command", QUOTED_VERB + VARIABLE_VERB + OTHER_MERGES)
def test_round1_hidden_and_other_merge_forms_are_blocked_in_auto_mode(gate, tmp_path, command):
    fx = gate(kanban(done=("T900",)))
    path = transcript(tmp_path, [human("finish the work [admin]")])
    text = reason(command, fx.main, transcript=path)
    assert text is not None and "Auto-mode gate" in text, f"{command!r} must be the user's in auto mode"


@pytest.mark.parametrize("command", STILL_ALLOWED)
def test_round1_read_only_and_quoted_mentions_stay_allowed(gate, command):
    fx = gate(kanban(in_progress=("T900",)))
    assert reason(command, fx.main) is None, command


def test_round1_an_error_in_the_gh_check_is_a_hit_not_a_pass(monkeypatch):
    def boom(command):
        raise RuntimeError("x")
    monkeypatch.setattr(merge_gate, "_gh_merge_hit", boom)
    assert merge_gate.gh_merge_hit("gh pr view 1") is True


# Review round 2: a backslash-newline joins the words, so it must not hide the verb.
CONTINUED = ["gh \\\npr merge 1", "gh pr \\\nmerge 1", "gh api repos/o/r/pulls/3/\\\nmerge -X PUT"]


@pytest.mark.parametrize("command", CONTINUED, ids=["after-gh", "before-verb", "inside-endpoint"])
def test_round2_a_line_continuation_does_not_hide_a_gh_merge(gate, command):
    fx = gate(kanban(in_progress=("T900",)))
    text = reason(command, fx.main)
    assert text is not None and "cannot push/merge" in text, f"{command!r} must be gated"
