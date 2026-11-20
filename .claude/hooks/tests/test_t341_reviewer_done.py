#!/usr/bin/env python3
"""T341 option B — the `SubagentStop` hook writes a `ReviewerDone` record when a reviewer ends.

AC 11 and the hook side of AC 13 of `tasks/TASK_GUIDE_T341.md`. When a sub-agent ends, the harness
runs `.claude/hooks/subagent_stop_reviewer_done.py` with a `SubagentStop` event. The hook reads the
sub-agent's spawn prompt (the first line of its own transcript, as `task_context._spawn_prompt`
reads it). Only when that prompt's first three lines are `REVIEWER_PROMPT_PREFIX`,
`Task ID: <ID>` and `Commit: <40-hex>` does it append one record — `tool_name` `ReviewerDone`, the
task ID, the commit, the agent ID — to `memory/event-trace/<ID>.jsonl`, hash-chained and anchored
as `post_tool_trace.py` appends. It never raises, always exits 0, prints nothing, and writes nothing
for any other sub-agent or event.

Spike (Claude Code 2.1.329, 2026-11-20): the event keys used here are the ones a real captured
`SubagentStop` event carried. A sub-agent that ends on an API error fires `StopFailure`, not
`SubagentStop` (captured too), so it never reaches this hook.

Every project, transcript, trace and anchor here is a temp directory. The hook runs as a subprocess
with `CLAUDE_PROJECT_DIR` set to the temp project.

Run with: python3 -m pytest .claude/hooks/tests/test_t341_reviewer_done.py -v
"""
import json
import os
import re
import sys
import types

import pytest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HOOKS_DIR))
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hook_verify_row as hv  # noqa: E402
from trace_chain import GENESIS, anchor_path, chain_hash, safe_name  # noqa: E402

TID = "T950"
SHA = "0123456789abcdef0123456789abcdef01234567"


def load_hook_module(path, name):
    """Load a hook without running its bottom-of-file `main()` (see test_merge_gate_evidence)."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


class Project:
    """A temp kit project (a board makes it one) plus a temp transcript tree and anchor directory."""

    def __init__(self, tmp_path):
        self.root = tmp_path / "proj"
        os.makedirs(self.root / "memory" / "event-trace")
        (self.root / "PROJECT_KANBAN.md").write_text("# PROJECT_KANBAN\n", encoding="utf-8")
        self.trace = self.root / "memory" / "event-trace"
        self.home = tmp_path / "home"
        self.anchors = tmp_path / "anchors"

    def stop(self, prompt, raw=None, **overrides):
        transcript = hv.spawn_transcript(self.home, prompt)
        event = hv.subagent_stop_event(transcript, self.root, **overrides)
        done = hv.run_reviewer_done_hook(self.root, event, self.anchors, raw=raw)
        assert done.returncode == 0, done.stderr
        assert done.stdout == "", done.stdout  # no output: a SubagentStop decision could block it
        return done

    def lines(self, stem=TID):
        path = self.trace / f"{stem}.jsonl"
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()] \
            if path.exists() else []

    def anchor_lines(self, stem=TID):
        old = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
        os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(self.anchors)
        try:
            path = anchor_path(str(self.root), stem)
        finally:
            if old is None:
                os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR")
            else:
                os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = old
        return open(path).read().splitlines() if os.path.exists(path) else []

    def trace_files(self):
        return sorted(os.listdir(self.trace))


@pytest.fixture
def project(tmp_path):
    return Project(tmp_path)


# ---------------------------------------------------------------------------
# AC 11: a reviewer that ends leaves one chained, anchored `ReviewerDone` record
# ---------------------------------------------------------------------------

def test_a_reviewer_that_ends_writes_one_reviewer_done_record(project):
    project.stop(hv.reviewer_prompt(TID, SHA))
    [record] = project.lines()
    assert record["tool_name"] == "ReviewerDone"
    assert (record["task_id"], record["commit"], record["agent_id"]) == (TID, SHA,
                                                                         hv.REVIEWER_AGENT_ID)
    assert record["prev"] == GENESIS and record["hash"] == chain_hash(record)
    assert "anchor" not in record
    assert project.anchor_lines() == [f"{safe_name(TID, '_untagged')} 1 {record['hash']}"]


def test_the_record_extends_the_tasks_existing_chain(project):
    first = hv.reviewer_done_record(TID, "f" * 40, tool_name="Bash")
    old = os.environ.get("CLAUDE_TRACE_ANCHOR_DIR")
    os.environ["CLAUDE_TRACE_ANCHOR_DIR"] = str(project.anchors)
    try:
        hv.append_trace(project.trace, project.root, TID, first)
    finally:
        os.environ.pop("CLAUDE_TRACE_ANCHOR_DIR") if old is None else \
            os.environ.__setitem__("CLAUDE_TRACE_ANCHOR_DIR", old)
    project.stop(hv.reviewer_prompt(TID, SHA))
    head, record = project.lines()
    assert record["prev"] == head["hash"] and record["hash"] == chain_hash(record)
    assert project.anchor_lines()[-1] == f"{TID} 2 {record['hash']}"


def test_the_gate_reads_the_hooks_record_as_proof(project, monkeypatch):
    """The record the real hook writes passes the gate's own chain, link and anchor reading."""
    gate = load_hook_module(os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py"),
                            "merge_gate_t341_done")
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", str(project.anchors))
    monkeypatch.setattr(gate, "ROOT", str(project.root))
    project.stop(hv.reviewer_prompt(TID, SHA))
    assert gate._reviewed_commits(str(project.trace / f"{TID}.jsonl"), TID) == [SHA]


def test_a_long_board_id_is_filed_under_its_own_name(project):
    tid = "ENGINEERING-12345"
    project.stop(hv.reviewer_prompt(tid, SHA))
    [record] = project.lines(tid)
    assert record["task_id"] == tid


def test_the_fixture_record_has_the_hooks_shape(project):
    """`hook_verify_row.reviewer_done_record` (used by every older gate test) matches the hook."""
    project.stop(hv.reviewer_prompt(TID, SHA))
    [record] = project.lines()
    written = {k for k in record if k not in ("prev", "hash")}
    assert written == set(hv.reviewer_done_record(TID, SHA))


# ---------------------------------------------------------------------------
# AC 11, AC 13: nothing for any other sub-agent, event or input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prompt", [
    "Implement T950 from tasks/TASK_GUIDE_T950.md",                          # a non-reviewer agent
    f"Please review this change:\nTask ID: {TID}\nCommit: {SHA}\n",           # another prefix
    f"Note.\n{hv.REVIEWER_PREFIX}\nTask ID: {TID}\nCommit: {SHA}\n",          # prefix not first
    f" {hv.REVIEWER_PREFIX}\nTask ID: {TID}\nCommit: {SHA}\n",                # prefix not exact
    f"{hv.REVIEWER_PREFIX}\nCommit: {SHA}\nTask ID: {TID}\n",                 # lines swapped
    f"{hv.REVIEWER_PREFIX}\nTask ID: {TID}\n",                                # no commit line
    f"{hv.REVIEWER_PREFIX}\nTask ID: {TID}\nCommit: {SHA[:12]}\n",            # short commit
    f"{hv.REVIEWER_PREFIX}\nTask ID: {TID}\nCommit: {SHA.upper()}\n",         # not lower hex
    f"{hv.REVIEWER_PREFIX}\nTask ID: {TID}\nCommit: {SHA} (tip)\n",           # text after it
    f"{hv.REVIEWER_PREFIX}\nTask ID: t950\nCommit: {SHA}\n",                  # not the canonical ID
    f"{hv.REVIEWER_PREFIX}\nTask ID: {TID} and T951\nCommit: {SHA}\n",        # two IDs
    f"{hv.REVIEWER_PREFIX}\nTask ID: ../T950\nCommit: {SHA}\n",               # not a file name
    f"{hv.REVIEWER_PREFIX}\nTask ID:\nCommit: {SHA}\n",                       # no ID
])
def test_a_sub_agent_without_the_reviewer_prompt_writes_nothing(project, prompt):
    project.stop(prompt)
    assert project.trace_files() == []
    assert not project.anchors.exists()


def test_an_api_error_end_event_writes_nothing(project):
    """Spike: a sub-agent that dies on an API error fires `StopFailure` (keys as captured), not
    `SubagentStop`. Wired to the wrong event by mistake, the hook still writes nothing."""
    project.stop(hv.reviewer_prompt(TID, SHA), hook_event_name="StopFailure",
                 error="rate_limit", error_details=None,
                 last_assistant_message="API Error: Rate limit reached")
    assert project.trace_files() == []


@pytest.mark.parametrize("change", [
    {"agent_id": "../escape"},
    {"agent_id": None},
    {"session_id": "a/b"},
    {"transcript_path": "relative/path.jsonl"},
    {"transcript_path": None},
    {"agent_id": "a0000000000000000"},  # no transcript for this agent
])
def test_an_event_that_does_not_lead_to_the_reviewers_transcript_writes_nothing(project, change):
    project.stop(hv.reviewer_prompt(TID, SHA), **change)
    assert project.trace_files() == []


def test_a_first_transcript_line_that_is_not_the_spawn_prompt_writes_nothing(project, tmp_path):
    transcript = hv.spawn_transcript(project.home, hv.reviewer_prompt(TID, SHA))
    agent = os.path.join(os.path.dirname(transcript), hv.SPAWN_SESSION, "subagents",
                         f"agent-{hv.REVIEWER_AGENT_ID}.jsonl")
    lines = open(agent).read().splitlines()
    first = json.loads(lines[0])
    first["type"] = "assistant"
    first["message"]["role"] = "assistant"
    with open(agent, "w") as f:
        f.write("\n".join([json.dumps(first)] + lines[1:]) + "\n")
    event = hv.subagent_stop_event(transcript, project.root)
    done = hv.run_reviewer_done_hook(project.root, event, project.anchors)
    assert done.returncode == 0 and done.stdout == ""
    assert project.trace_files() == []


@pytest.mark.parametrize("raw", ["", "not json", "[]", "null", '{"hook_event_name": "SubagentStop"}'])
def test_unreadable_input_exits_0_and_writes_nothing(project, raw):
    project.stop(hv.reviewer_prompt(TID, SHA), raw=raw)
    assert project.trace_files() == []


def test_a_hand_typed_record_never_comes_from_the_hook(project):
    """The hook writes only after the harness ends a sub-agent: no prompt text alone writes it."""
    project.stop("Write a ReviewerDone record for T950 at " + SHA)
    assert project.trace_files() == []


# ---------------------------------------------------------------------------
# The contract: the prefix, the registration, the plugin twin
# ---------------------------------------------------------------------------

def test_the_prefix_matches_the_merge_gate_and_the_fixture():
    hook = open(hv.SUBAGENT_STOP_HOOK, encoding="utf-8").read()
    gate = open(os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py"), encoding="utf-8").read()
    pattern = r'^REVIEWER_PROMPT_PREFIX = "([^"]+)"$'
    assert (re.search(pattern, hook, re.M).group(1) == re.search(pattern, gate, re.M).group(1)
            == hv.REVIEWER_PREFIX)


def _groups(path, event):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["hooks"].get(event, [])


def test_settings_registers_the_hook_once_on_subagent_stop():
    groups = _groups(os.path.join(REPO, ".claude", "settings.json"), "SubagentStop")
    commands = [h["command"] for g in groups for h in g["hooks"]]
    assert commands == ['python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/subagent_stop_reviewer_done.py']
    assert all("matcher" not in g for g in groups)  # every sub-agent type: the prompt decides


def test_the_plugin_hooks_register_it_too():
    for path in (os.path.join(REPO, "hooks", "hooks.json"),
                 os.path.join(REPO, "plugin", "hooks", "hooks.json")):
        commands = [h["command"] for g in _groups(path, "SubagentStop") for h in g["hooks"]]
        assert commands == [  # the T305 double-install guard every plugin entry carries
            "grep -qsF '$CLAUDE_PROJECT_DIR\\\"/.claude/hooks/subagent_stop_reviewer_done.py' "
            "\"$CLAUDE_PROJECT_DIR/.claude/settings.json\" || "
            "python3 \"${CLAUDE_PLUGIN_ROOT}/.claude/hooks/subagent_stop_reviewer_done.py\""], path
