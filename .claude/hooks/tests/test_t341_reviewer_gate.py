#!/usr/bin/env python3
"""T341 — the merge gate refuses an extended-track task branch until a fresh reviewer ran on its code.

AC 4-6, 9, 12 and 13 of `tasks/TASK_GUIDE_T341.md`. The proof is a hook-written trace record: a
`ReviewerDone` record for the task, which the `SubagentStop` hook `subagent_stop_reviewer_done.py`
writes when a sub-agent whose spawn prompt starts with `REVIEWER_PROMPT_PREFIX`, `Task ID: <ID>` and
`Commit: <40-hex>` ends (option B), with its chain hash, its link and its anchor intact. The `Agent`
spawn record alone no longer counts, whatever its status. The named commit is an ancestor of the
branch tip, and between the two
only the review file, the board, `tasks/MINIMAL_LOG.md` and `memory/*.md` (not `memory/MEMORY.md`)
changed. A task is extended track when its guide exists at the tip, in the main checkout, or in a
commit of `main..tip`; no date is trusted. The check runs per merged (or narrowed pushed) branch,
never inside the board-wide Ready-for-Review loop.

Every board, guide, trace, anchor and git repo here is constructed. Git runs with the user's global
and system config switched off.

Run with: python3 -m pytest .claude/hooks/tests/test_t341_reviewer_gate.py -v
"""
import io
import json
import os
import subprocess
import sys
import types

import pytest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py")
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def load_hook_module(path, name):
    """Load the hook without running its bottom-of-file `main()` (see test_merge_gate_evidence)."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


merge_gate = load_hook_module(HOOK_PATH, "merge_gate_t341")
import hook_verify_row  # noqa: E402  (on sys.path: the hook put its lib/ there)
from hook_verify_row import (REVIEWER_PREFIX, append_trace, prove_review,  # noqa: E402
                             reviewer_done_record, reviewer_record)

# Spelled in halves so this file's own text never reads as a command to the live gate.
G = "git "
MERGE, PUSH = G + "merge", G + "push"
TID, BRANCH = "T950", "feat/t950-x"
REVIEW = ("# TASK_REVIEW - {tid}\n\n## Evidence\n\n| Check | Result | Notes |\n|---|---|---|\n"
          "| verify | {cells} |\n")
GUIDE = "# TASK_GUIDE - {tid}\n\n## Evidence\n\n> Moved to `tasks/TASK_REVIEW_{tid}.md`.\n"
REVIEW_BLOCK = f"{TID} (extended track) has no fresh reviewer record"


def kanban(ready=(), done=()):
    rows = lambda ids: "".join(f"- [ ] **{t}** — fixture {t} | agent | C2 | Risk: Low | P1\n"
                               for t in ids)
    return ("# PROJECT_KANBAN\n\n### Todo\n\n### In Progress\n\n### Ready for Review\n"
            + rows(ready) + "\n### Done\n" + rows(done))


def pytest_record():
    return json.dumps({"timestamp": "2026-11-20T00:00:00+00:00", "tool_name": "Bash",
                       "summary": json.dumps({"command": "python3 -m pytest -q"}),
                       "is_error": False})


def git(cwd, *args, env=None):
    done = subprocess.run(["git", "-C", str(cwd), "-c", "user.email=t@example.com",
                           "-c", "user.name=t", *args], capture_output=True, text=True,
                          timeout=30, env={**os.environ, **GIT_ENV, **(env or {})})
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def write(path, text):
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class Fixture:
    """A main checkout on `main` (a real git repo) and the task worktree on `feat/t950-x`."""

    def __init__(self, root, board):
        self.main = os.path.join(str(root), "main")
        self.tasks = os.path.join(self.main, "tasks")
        self.trace = os.path.join(self.main, "memory", "event-trace")
        os.makedirs(self.tasks)
        os.makedirs(self.trace)
        self.kanban = os.path.join(self.main, "PROJECT_KANBAN.md")
        write(self.kanban, board)
        git(self.main, "init", "-q", "-b", "main")
        git(self.main, "commit", "-q", "--allow-empty", "-m", "base")
        self.wt = os.path.join(str(root), "wt-t950")
        git(self.main, "worktree", "add", "-q", "-b", BRANCH, self.wt)
        write(os.path.join(self.trace, f"{TID}.jsonl"), pytest_record() + "\n")

    def commit(self, files, where=None, env=None, remove=()):
        where = where or self.wt
        for rel, text in files.items():
            write(os.path.join(where, rel), text)
        for rel in remove:
            git(where, "rm", "-q", rel)
        git(where, "add", "-A")
        git(where, "commit", "-qm", f"{TID}: {', '.join(files) or 'remove'}", env=env)
        return git(where, "rev-parse", "HEAD")

    def tip(self):
        return git(self.main, "rev-parse", BRANCH)

    def extended(self, env=None):
        """The task's guide and code, committed on the branch. Returns the code commit."""
        return self.commit({f"tasks/TASK_GUIDE_{TID}.md": GUIDE.format(tid=TID),
                            "app.py": "x = 1\n"}, env=env)

    def verified(self):
        """The hook's own verify pass for the head commit, committed in the review file."""
        sha = hook_verify_row.prove(merge_gate.ROOT, self.wt, TID)
        self.commit({f"tasks/TASK_REVIEW_{TID}.md":
                     REVIEW.format(tid=TID, cells=hook_verify_row.hook_cells(sha, TID))})
        return sha

    def review(self, commit=None, stem=None, **overrides):
        return prove_review(self.trace, merge_gate.ROOT, TID, commit or self.tip(), stem,
                            **overrides)


@pytest.fixture
def gate(tmp_path, monkeypatch):
    for key, value in GIT_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", str(tmp_path / "anchors"))

    def build(board):
        fx = Fixture(tmp_path / "fx", board)
        monkeypatch.setattr(merge_gate, "KANBAN", fx.kanban)
        monkeypatch.setattr(merge_gate, "TASKS_DIR", fx.tasks)
        monkeypatch.setattr(merge_gate, "TRACE_DIR", fx.trace)
        monkeypatch.setattr(merge_gate, "worktree_tasks_dirs",
                            lambda: [os.path.join(fx.wt, "tasks")])
        return fx
    return build


def reason(command, cwd):
    """Drive the hook's real `main()`; the block reason, or None when it allows."""
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}
    saved = (sys.stdin, sys.stdout, sys.stderr)
    sys.stdin, sys.stdout, sys.stderr = io.StringIO(json.dumps(event)), io.StringIO(), io.StringIO()
    try:
        try:
            merge_gate.main()
        except SystemExit:
            pass
        out = sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved
    return json.loads(out)["reason"] if out.strip() else None


def merge(fx):
    return reason(MERGE + " --no-ff " + BRANCH, fx.main)


def assert_review_block(text):
    assert text is not None, "the merge must be refused: no valid reviewer record for the tip"
    assert REVIEW_BLOCK in text, text
    assert f"Reviewer: {TID}" in text and "active-task state" in text, text  # the remedy
    assert "`SubagentStop`" in text and "`ReviewerDone`" in text, text  # AC 12
    assert "foreground" not in text, text  # AC 12: a background spawn is fine


# ---------------------------------------------------------------------------
# Success criteria 1-2: Ready for Review, hook verify pass committed
# ---------------------------------------------------------------------------

def test_sc1_ready_for_review_with_a_verify_pass_but_no_reviewer_record_is_refused(gate):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    assert_review_block(merge(fx))


def test_sc2_a_valid_reviewer_record_naming_the_tip_allows_the_merge(gate):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    fx.review()
    assert merge(fx) is None


# ---------------------------------------------------------------------------
# Success criteria 3-4: the reviewed commit and what may follow it
# ---------------------------------------------------------------------------

def test_sc3_a_code_change_after_the_reviewed_commit_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.review(reviewed)
    fx.commit({"app.py": "x = 2\n"})
    assert_review_block(merge(fx))


def test_sc4_only_board_review_log_and_memory_commits_after_the_reviewed_commit_are_allowed(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.review(reviewed)
    fx.commit({"PROJECT_KANBAN.md": "# board\n", f"tasks/TASK_REVIEW_{TID}.md": "# review\n"})
    fx.commit({"tasks/MINIMAL_LOG.md": "# log\n", "memory/learnings.md": "# l\n",
               "memory/decisions.md": "# d\n"})
    assert merge(fx) is None


@pytest.mark.parametrize("rel", ["memory/MEMORY.md", "memory/sub/notes.md",
                                 "tasks/TASK_REVIEW_T951.md", "tasks/TASK_GUIDE_T950.md"])
def test_any_other_file_after_the_reviewed_commit_is_refused(gate, rel):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.review(reviewed)
    fx.commit({rel: "changed\n"})
    assert_review_block(merge(fx))


def test_a_code_file_renamed_into_memory_after_the_reviewed_commit_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.review(reviewed)
    os.makedirs(os.path.join(fx.wt, "memory"))
    git(fx.wt, "mv", "app.py", "memory/app.md")
    git(fx.wt, "commit", "-qm", f"{TID}: move")
    assert_review_block(merge(fx))


# ---------------------------------------------------------------------------
# Success criterion 5, AC 6: which tasks are in scope
# ---------------------------------------------------------------------------

def test_sc5_a_minimal_track_branch_with_no_guide_anywhere_is_never_checked(gate):
    fx = gate(kanban(done=(TID,)))
    fx.commit({"app.py": "x = 1\n"})
    assert merge(fx) is None


def test_a_guide_only_in_the_main_checkout_makes_the_task_extended(gate):
    fx = gate(kanban(done=(TID,)))
    fx.commit({"app.py": "x = 1\n"})
    write(os.path.join(fx.tasks, f"TASK_GUIDE_{TID}.md"), GUIDE.format(tid=TID))
    assert_review_block(merge(fx))


def test_a_guide_added_then_removed_on_the_branch_still_makes_the_task_extended(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.commit({}, remove=(f"tasks/TASK_GUIDE_{TID}.md",))
    assert_review_block(merge(fx))


def test_a_guide_committed_with_a_backdated_committer_date_is_still_checked(gate):
    fx = gate(kanban(done=(TID,)))
    old = {"GIT_COMMITTER_DATE": "2020-01-01T00:00:00+00:00",
           "GIT_AUTHOR_DATE": "2020-01-01T00:00:00+00:00"}
    fx.extended(env=old)
    assert_review_block(merge(fx))


def test_the_done_row_of_an_extended_task_is_checked_too(gate):
    """After the auto close-out the row is Done before the merge: the check reads the merged
    branch, not the board lane."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    assert_review_block(merge(fx))


def test_an_already_merged_ready_for_review_task_with_no_record_blocks_nothing_new(gate):
    """Task B (T951) sits in Ready for Review, merged long ago, with its verify pass and no reviewer
    record. Merging task A (T950) with its reviewer record is allowed: the check is per target."""
    fx = gate(kanban(ready=(TID, "T951")))
    sha = hook_verify_row.prove(merge_gate.ROOT, fx.main, "T951")
    write(os.path.join(fx.tasks, "TASK_GUIDE_T951.md"), GUIDE.format(tid="T951"))
    write(os.path.join(fx.tasks, "TASK_REVIEW_T951.md"),
          REVIEW.format(tid="T951", cells=hook_verify_row.hook_cells(sha, "T951")))
    write(os.path.join(fx.trace, "T951.jsonl"), pytest_record() + "\n")
    fx.extended()
    fx.verified()
    text = merge(fx)
    assert_review_block(text)
    assert "T951" not in text  # only the merged branch is checked
    fx.review()
    assert merge(fx) is None


# ---------------------------------------------------------------------------
# AC 5, AC 9: what a reviewer record must be
# ---------------------------------------------------------------------------

def test_a_reviewer_done_record_for_another_task_is_refused(gate):
    """AC 13: filed in T950's own trace, but it names T999."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    append_trace(fx.trace, merge_gate.ROOT, TID, reviewer_done_record("T999", fx.tip()))
    assert_review_block(merge(fx))


@pytest.mark.parametrize("status", ["async_launched", "completed", None])
def test_an_agent_spawn_record_alone_is_refused(gate, status):
    """AC 12-13: the spawn record of a `Reviewer: <ID>` call with the documented prompt does not
    count, whether it says `async_launched` (every spawn here), `completed` or nothing."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    record = reviewer_record(TID, fx.tip())
    if status is None:
        del record["spawn"]
    else:
        record["spawn"]["status"] = status
    append_trace(fx.trace, merge_gate.ROOT, TID, record)
    assert_review_block(merge(fx))


@pytest.mark.parametrize("commit", ["0123456789ab", "0123456789ABCDEF0123456789ABCDEF01234567",
                                    None, 12345])
def test_a_reviewer_done_record_with_no_full_commit_is_refused(gate, commit):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    append_trace(fx.trace, merge_gate.ROOT, TID, reviewer_done_record(TID, commit))
    assert_review_block(merge(fx))


def test_a_record_of_another_tool_naming_the_task_and_commit_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    append_trace(fx.trace, merge_gate.ROOT, TID,
                 reviewer_done_record(TID, fx.tip(), tool_name="Agent"))
    assert_review_block(merge(fx))


def test_a_commit_not_in_the_tips_history_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    elsewhere = fx.commit({"other.py": "y = 1\n"}, where=fx.main)  # on `main`, after the fork
    fx.review(elsewhere)
    assert_review_block(merge(fx))


def test_an_unknown_commit_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.review("0123456789abcdef0123456789abcdef01234567")
    assert_review_block(merge(fx))


@pytest.mark.parametrize("stem", ["_untagged", "T777"])
def test_a_record_filed_under_another_trace_file_still_counts(gate, stem):
    """The hook files it under the task's own name; a record is still the task's by its content,
    not by its file."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.review(stem=stem)
    assert merge(fx) is None


# ---------------------------------------------------------------------------
# Success criterion 6, AC 5: chain hash and anchor
# ---------------------------------------------------------------------------

def _rewrite_last_line(path, change):
    lines = open(path, encoding="utf-8").read().splitlines()
    lines[-1] = json.dumps(change(json.loads(lines[-1])))
    write(path, "\n".join(lines) + "\n")


def test_sc6_a_record_edited_after_anchoring_with_its_hash_recomputed_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.commit({"app.py": "x = 2\n"})
    fx.review(reviewed)

    def retarget(rec):
        rec["commit"] = fx.tip()
        rec["hash"] = merge_gate.chain_hash(rec)
        return rec
    _rewrite_last_line(os.path.join(fx.trace, f"{TID}.jsonl"), retarget)
    assert_review_block(merge(fx))


def test_a_record_edited_without_recomputing_its_hash_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.commit({"app.py": "x = 2\n"})
    fx.review(reviewed)

    def retarget(rec):
        rec["commit"] = fx.tip()
        return rec
    _rewrite_last_line(os.path.join(fx.trace, f"{TID}.jsonl"), retarget)
    assert_review_block(merge(fx))


def test_a_forged_append_with_a_valid_chain_but_no_anchor_is_refused(gate):
    """`echo >>` from an agent's own shell: the chain links, the anchor directory is denied."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    append_trace(fx.trace, merge_gate.ROOT, TID, reviewer_done_record(TID, fx.tip()), anchor=False)
    assert_review_block(merge(fx))


def test_a_record_typed_into_the_trace_by_hand_is_refused(gate):
    """AC 13: `echo '{"tool_name": "ReviewerDone", ...}' >> memory/event-trace/T950.jsonl`."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    with open(os.path.join(fx.trace, f"{TID}.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(reviewer_done_record(TID, fx.tip())) + "\n")
    assert_review_block(merge(fx))


def test_a_record_whose_prev_does_not_link_is_refused_even_when_anchored(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    record = reviewer_done_record(TID, fx.tip())
    path = os.path.join(fx.trace, f"{TID}.jsonl")
    record["prev"] = "f" * 64  # the line before it is a pre-chain record: prev must be genesis
    record["hash"] = merge_gate.chain_hash(record)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    anchors = merge_gate.anchor_path(merge_gate.ROOT, TID)
    os.makedirs(os.path.dirname(anchors), exist_ok=True)
    with open(anchors, "a", encoding="utf-8") as f:
        f.write(f"{TID} 2 {record['hash']}\n")
    assert_review_block(merge(fx))


def test_a_record_marked_anchor_failed_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    append_trace(fx.trace, merge_gate.ROOT, TID, dict(reviewer_done_record(TID, fx.tip()),
                                                      anchor="failed"))
    assert_review_block(merge(fx))


# ---------------------------------------------------------------------------
# AC 4: the narrowed task-branch push
# ---------------------------------------------------------------------------

def test_a_narrowed_push_of_the_task_branch_is_refused_without_a_reviewer_record(gate):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    assert_review_block(reason(PUSH + " origin " + BRANCH, fx.wt))


def test_a_narrowed_push_of_the_task_branch_is_allowed_with_one(gate):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    fx.review()
    assert reason(PUSH + " origin " + BRANCH, fx.wt) is None


# ---------------------------------------------------------------------------
# The contract the docs state: prefix, description, the 300-character cut, fail closed
# ---------------------------------------------------------------------------

def test_the_prefix_is_the_documented_literal():
    assert merge_gate.REVIEWER_PROMPT_PREFIX == REVIEWER_PREFIX


def test_the_remedy_names_the_spawn_shape_and_the_hook_record(gate):
    """AC 12: the block line names the spawn shape, says the record is written when the reviewer
    ends, and no longer asks for a foreground spawn (`assert_review_block` checks all three)."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    text = merge(fx)
    assert_review_block(text)
    assert f"{REVIEWER_PREFIX}\\nTask ID: {TID}\\nCommit: {fx.tip()}" in text, text


# ---------------------------------------------------------------------------
# AC 13 end to end: the real `SubagentStop` hook writes the record the gate counts
# ---------------------------------------------------------------------------

def _hook_run(fx, prompt, monkeypatch, tmp_path):
    monkeypatch.setattr(merge_gate, "ROOT", fx.main)  # the hook's project is the main checkout
    transcript = hook_verify_row.spawn_transcript(tmp_path / "home", prompt)
    event = hook_verify_row.subagent_stop_event(transcript, fx.wt)
    done = hook_verify_row.run_reviewer_done_hook(fx.main, event, os.environ["CLAUDE_TRACE_ANCHOR_DIR"])
    assert done.returncode == 0 and done.stdout == "", done.stderr


def test_the_record_the_real_hook_writes_when_the_reviewer_ends_allows_the_merge(
        gate, monkeypatch, tmp_path):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    assert_review_block(merge(fx))
    _hook_run(fx, hook_verify_row.reviewer_prompt(TID, fx.tip()), monkeypatch, tmp_path)
    assert merge(fx) is None


def test_a_sub_agent_that_ends_with_a_non_reviewer_prompt_leaves_the_merge_refused(
        gate, monkeypatch, tmp_path):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    _hook_run(fx, f"Implement {TID}: tasks/TASK_GUIDE_{TID}.md\nCommit: {fx.tip()}", monkeypatch,
              tmp_path)
    assert_review_block(merge(fx))


def test_trace_shows_review_is_false_on_a_git_error(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.review()
    assert merge_gate.trace_shows_review(TID, fx.tip(), fx.main)
    assert not merge_gate.trace_shows_review(TID, fx.tip(), os.path.join(fx.main, "missing"))


def test_a_merge_whose_branch_cannot_be_resolved_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.review()
    text = reason(MERGE + " --no-ff " + BRANCH + "; echo done", fx.main)
    assert text is not None and "cannot tell which branch this merge brings in" in text, text


# ---------------------------------------------------------------------------
# Stage 4 P1: a merge or task-branch push chained with another git command is checked too
# ---------------------------------------------------------------------------
#
# `branch_targets` resolves only a command with one git action, so before the fix every chained
# shape below was allowed with no reviewer record. Each merge action's sources (and each push
# action's task-branch refspecs) are now resolved per action; a merge whose source cannot be read
# is refused (AC 5: any doubt is false).

CHAINED = [
    G + "checkout main && " + MERGE + " --no-ff " + BRANCH,
    G + "pull github main && " + MERGE + " --no-ff " + BRANCH,
    MERGE + " --no-ff " + BRANCH + " && " + PUSH + " github main",
    MERGE + " " + BRANCH + " && " + PUSH,
    MERGE + " " + BRANCH + " && " + G + "branch -d " + BRANCH,
    MERGE + " " + BRANCH + " || " + PUSH + " github main",
    PUSH + " github " + BRANCH + " && " + PUSH + " github main",
]
CHAINED_IDS = ["checkout-merge", "pull-merge", "merge-push-main", "merge-push", "merge-branch-d",
               "merge-or-push", "push-branch-push-main"]


@pytest.mark.parametrize("command", CHAINED, ids=CHAINED_IDS)
def test_a_chained_merge_or_task_branch_push_with_no_reviewer_record_is_refused(gate, command):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    assert_review_block(reason(command, fx.main))


@pytest.mark.parametrize("command", CHAINED, ids=CHAINED_IDS)
def test_a_chained_merge_or_task_branch_push_with_a_record_on_the_tip_is_allowed(gate, command):
    fx = gate(kanban(ready=(TID,)))
    fx.extended()
    fx.verified()
    fx.review()
    assert reason(command, fx.main) is None


def test_a_chained_merge_of_a_code_change_after_the_reviewed_commit_is_refused(gate):
    fx = gate(kanban(done=(TID,)))
    reviewed = fx.extended()
    fx.review(reviewed)
    fx.commit({"app.py": "x = 2\n"})
    assert_review_block(reason(G + "checkout main && " + MERGE + " --no-ff " + BRANCH, fx.main))


def test_a_chained_merge_that_names_no_branch_is_refused(gate):
    """`git checkout main && git merge` merges the upstream: which task it brings in is a doubt."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    fx.review()
    text = reason(G + "checkout main && " + MERGE, fx.main)
    assert text is not None and "cannot tell which branch" in text and "(T341)" in text, text


def test_a_chained_merge_of_a_branch_that_names_no_task_is_not_checked(gate):
    """Bringing `main` into the task branch is not a merge of a task branch."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    assert reason("cd " + fx.wt + " && " + MERGE + " main && " + G + "branch -d feat/none",
                  fx.main) is None


@pytest.mark.parametrize("command", [
    MERGE + " --abort", MERGE + " --continue", MERGE + " --quit",
    MERGE + " --abort && " + G + "checkout main",
    G + "checkout main && " + MERGE + " --abort",
])
def test_merge_abort_continue_and_quit_still_pass(gate, command):
    fx = gate(kanban(done=(TID,)))
    fx.extended()  # extended track, no reviewer record: nothing is merged, so nothing is checked
    assert reason(command, fx.main) is None


# ---------------------------------------------------------------------------
# Second Stage 4 P1: one merge action whose directory is unknown (`cd <dir> ;`, `cd <dir> ||`)
# ---------------------------------------------------------------------------
#
# After `cd <dir> ;` or `cd <dir> ||` the resolver cannot be sure where the merge runs, so the
# action's directory is unknown and `branch_targets` gives no target. The merge is refused as a
# doubt (AC 5), with or without a reviewer record: the gate cannot tell which checkout it merges in.

@pytest.mark.parametrize("sep", [" ; ", " || "], ids=["semicolon", "or"])
def test_a_merge_after_an_uncertain_cd_is_refused_as_a_doubt(gate, sep):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    command = "cd " + fx.main + sep + MERGE + " --no-ff " + BRANCH
    text = reason(command, fx.main)
    assert text is not None and "cannot tell which branch this merge brings in" in text, text
    fx.review()
    text = reason(command, fx.main)  # a record does not settle where the merge runs
    assert text is not None and "cannot tell which branch this merge brings in" in text, text


def test_a_merge_after_a_certain_cd_is_judged_as_before(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    command = "cd " + fx.main + " && " + MERGE + " --no-ff " + BRANCH
    assert_review_block(reason(command, fx.main))
    fx.review()
    assert reason(command, fx.main) is None


def test_a_lone_merge_and_merge_abort_behave_as_before(gate):
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    assert_review_block(merge(fx))
    assert reason(MERGE + " --abort", fx.main) is None
    fx.review()
    assert merge(fx) is None


# ---------------------------------------------------------------------------
# Second Stage 4 P3: the ancestor check on its own
# ---------------------------------------------------------------------------

def test_a_reviewed_commit_with_the_tips_tree_that_is_not_its_ancestor_is_refused(gate):
    """A rebase or cherry-pick of the same code: the tree diff to the tip is empty (review-free),
    but the named commit is not in the tip's history, so it is not the code being merged."""
    fx = gate(kanban(done=(TID,)))
    fx.extended()
    tip = fx.tip()
    base = git(fx.main, "rev-parse", "main")
    twin = git(fx.main, "commit-tree", tip + "^{tree}", "-p", base, "-m", "same tree, other history")
    assert git(fx.main, "diff", "--name-only", twin, tip) == ""  # review-free: nothing differs
    fx.review(twin)
    assert_review_block(merge(fx))
