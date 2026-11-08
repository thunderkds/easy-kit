"""T290: a task guide can lock its oracle test while the task runs.

`pre_tool_locked_oracle.py` is a PreToolUse hook for Edit|Write|MultiEdit|NotebookEdit. A guide
lists oracle files on one `**Locked oracle**:` line. While that task's board row is In Progress, a
sub-agent that is not `qa-expert` (bare or `easy-kit:qa-expert`) is denied an Edit or Write to
them. The main thread (no `agent_id`: the Supervisor) and `qa-expert` pass.

Every test calls the hook script directly (subprocess, `CLAUDE_PROJECT_DIR` set to a temp
project), never through `.claude/settings.json` (AC6). Replay (AC7): commit 7448c0cd, T082's
implementer (common-infrastructure) edited T066's guard test and relaxed `<` to `<=`
(tasks/TASK_REVIEW_T082.md:92). The fixture is the real `tasks/TASK_GUIDE_T066.md` plus a lock line.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / ".claude" / "hooks" / "pre_tool_locked_oracle.py"
ORACLE = ".claude/hooks/tests/test_agent_guide_dedup.py"
SECOND = "tests/test_second_oracle.py"
IMPLEMENTERS = ["common-infrastructure", "backend-developer", "frontend-developer",
                "easy-kit:backend-developer", "easy-kit:common-infrastructure", "general-purpose"]
JUDGES = ["qa-expert", "easy-kit:qa-expert"]


def board(**sections):
    """A PROJECT_KANBAN.md body. sections: Todo / In_Progress / Ready_for_Review / Done -> [task id]."""
    out = ["# PROJECT_KANBAN.md", "", "## Board", ""]
    for title in ("Todo", "In Progress", "Ready for Review", "Done"):
        out += [f"### {title}"] + [f"- [ ] **{t}** — a row | x" for t in sections.get(title.replace(" ", "_"), [])] + [""]
    out += ["## Blocked", ""] + [f"- **{t}** — waits" for t in sections.get("Blocked", [])] + [""]
    return "\n".join(out)


def make_project(tmp_path, kanban=None, guides=None):
    """A kit project: PROJECT_KANBAN.md plus tasks/TASK_GUIDE_<id>.md for each (id, text)."""
    (tmp_path / "tasks").mkdir(exist_ok=True)
    if kanban is not None:
        (tmp_path / "PROJECT_KANBAN.md").write_text(kanban, encoding="utf-8")
    for task_id, text in (guides or {}).items():
        (tmp_path / "tasks" / f"TASK_GUIDE_{task_id}.md").write_text(text, encoding="utf-8")
    return tmp_path


def lock_guide(*paths, title="T066", extra=""):
    names = ", ".join(f"`{p}`" for p in paths)
    return f"# TASK_GUIDE — {title}: x\n**Complexity Level**: C2\n\n**Locked oracle**: {names}\n{extra}\n## Body\n"


def edit_event(root, path=ORACLE, agent_type=None, tool="Edit", agent_id="a1", **extra):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    target = path if os.path.isabs(path) else str(root / path)
    event = {"tool_name": tool, "tool_input": {key: target, "old_string": "<", "new_string": "<="}}
    if agent_id is not None:
        event["agent_id"] = agent_id
        if agent_type is not None:
            event["agent_type"] = agent_type
    event.update(extra)
    return event


def run_hook(root, event, hook=HOOK, raw=None, env_extra=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    env.update(env_extra or {})
    stdin = raw if raw is not None else json.dumps(event)
    return subprocess.run([sys.executable, "-B", str(hook)], input=stdin, capture_output=True,
                          text=True, env=env, cwd=str(root))


def verdict(proc):
    """'deny' / 'allow' (no output) for a finished hook call; fails on anything else."""
    assert proc.returncode == 0, proc.stderr
    if not proc.stdout.strip():
        return "allow"
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    return out["permissionDecision"]


def reason(proc):
    return json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.fixture
def locked(tmp_path):
    """T066 In Progress, its guide locks ORACLE."""
    return make_project(tmp_path, board(In_Progress=["T066"]), {"T066": lock_guide(ORACLE)})


# --- AC1: an implementer is denied while the row is In Progress ---------------------------

@pytest.mark.parametrize("agent_type", IMPLEMENTERS)
def test_ac1_implementer_edit_is_denied_and_names_the_guide(locked, agent_type):
    proc = run_hook(locked, edit_event(locked, agent_type=agent_type))
    assert verdict(proc) == "deny"
    assert "tasks/TASK_GUIDE_T066.md" in reason(proc)
    assert ORACLE in reason(proc)


@pytest.mark.parametrize("tool", ["Edit", "Write", "MultiEdit", "NotebookEdit"])
def test_ac1_every_edit_tool_is_covered(locked, tool):
    assert verdict(run_hook(locked, edit_event(locked, agent_type="common-infrastructure", tool=tool))) == "deny"


# --- AC2: qa-expert and the main thread pass ----------------------------------------------

@pytest.mark.parametrize("agent_type", JUDGES)
def test_ac2_qa_expert_is_allowed(locked, agent_type):
    proc = run_hook(locked, edit_event(locked, agent_type=agent_type))
    assert verdict(proc) == "allow" and proc.stdout == ""


def test_ac2_main_thread_supervisor_is_allowed(locked):
    proc = run_hook(locked, edit_event(locked, agent_id=None))
    assert verdict(proc) == "allow" and proc.stdout == ""


# --- AC3: the lock ends when the row leaves In Progress -----------------------------------

@pytest.mark.parametrize("sections", [
    {"Ready_for_Review": ["T066"]}, {"Done": ["T066"]}, {"Blocked": ["T066"]}, {"Todo": ["T066"]}, {},
], ids=["ready-for-review", "done", "blocked", "todo", "no-row"])
def test_ac3_lock_ends_when_row_is_not_in_progress(tmp_path, sections):
    root = make_project(tmp_path, board(**sections), {"T066": lock_guide(ORACLE)})
    assert verdict(run_hook(root, edit_event(root, agent_type="common-infrastructure"))) == "allow"


def test_ac3_same_edit_denied_in_progress_then_allowed_after_the_move(locked):
    event = edit_event(locked, agent_type="common-infrastructure")
    assert verdict(run_hook(locked, event)) == "deny"
    (locked / "PROJECT_KANBAN.md").write_text(board(Ready_for_Review=["T066"]), encoding="utf-8")
    assert verdict(run_hook(locked, event)) == "allow"


def test_ac3_a_mention_in_another_row_does_not_keep_the_lock(tmp_path):
    kanban = board(Done=["T066"]).replace("### In Progress\n", "### In Progress\n- [ ] **T999** — follows up **T066** later\n")
    root = make_project(tmp_path, kanban, {"T066": lock_guide(ORACLE)})
    assert verdict(run_hook(root, edit_event(root, agent_type="common-infrastructure"))) == "allow"


# --- AC4: no guide, no lock; fail closed when the call cannot be cleared ------------------

def test_ac4_no_guide_names_the_path_allows(locked):
    event = edit_event(locked, path="tests/unrelated.py", agent_type="common-infrastructure")
    assert verdict(run_hook(locked, event)) == "allow"


def test_ac4_guide_without_a_lock_line_locks_nothing(tmp_path):
    real = (REPO / "tasks" / "TASK_GUIDE_T066.md").read_text(encoding="utf-8")
    root = make_project(tmp_path, board(In_Progress=["T066"]), {"T066": real})
    assert verdict(run_hook(root, edit_event(root, agent_type="common-infrastructure"))) == "allow"


@pytest.mark.parametrize("tool", ["Read", "Bash", "Grep"])
def test_ac4_non_edit_tool_passes(locked, tool):
    event = edit_event(locked, agent_type="common-infrastructure")
    event["tool_name"] = tool
    assert verdict(run_hook(locked, event)) == "allow"


@pytest.mark.parametrize("raw", ["not json", "", "[]", "null", '"Edit"', '{"tool_name": 7}', "{}"],
                         ids=["garbage", "empty", "list", "null", "string", "tool-int", "empty-object"])
def test_ac4_unreadable_input_is_denied(locked, raw):
    assert verdict(run_hook(locked, None, raw=raw)) == "deny"


def test_ac4_subagent_with_missing_agent_type_is_denied(locked):
    proc = run_hook(locked, edit_event(locked, agent_type=None))  # agent_id present, agent_type absent
    assert verdict(proc) == "deny"


@pytest.mark.parametrize("agent_type", ["", 7, ["qa-expert"], "QA-EXPERT", "qa-expert "])
def test_ac4_odd_agent_type_is_not_a_judge(locked, agent_type):
    event = edit_event(locked, agent_type="x")
    event["agent_type"] = agent_type
    assert verdict(run_hook(locked, event)) == "deny"


@pytest.mark.parametrize("tool_input", [{}, {"file_path": ""}, {"file_path": 7}, None, "x"])
def test_ac4_subagent_edit_without_a_usable_path_is_denied(locked, tool_input):
    event = {"tool_name": "Edit", "tool_input": tool_input, "agent_id": "a1", "agent_type": "common-infrastructure"}
    assert verdict(run_hook(locked, event)) == "deny"


def test_ac4_unreadable_board_fails_closed(tmp_path):
    root = make_project(tmp_path, None, {"T066": lock_guide(ORACLE)})
    (root / ".claude").mkdir()
    (root / ".claude" / "board.json").write_text("{}", encoding="utf-8")  # kit project, no PROJECT_KANBAN.md
    assert verdict(run_hook(root, edit_event(root, agent_type="common-infrastructure"))) == "deny"
    assert verdict(run_hook(root, edit_event(root, agent_id=None))) == "allow"


def test_ac4_unreadable_guide_fails_closed(locked):
    (locked / "tasks" / "TASK_GUIDE_T077.md").mkdir()  # a directory where a guide file should be
    assert verdict(run_hook(locked, edit_event(locked, path="tests/other.py", agent_type="common-infrastructure"))) == "deny"
    assert verdict(run_hook(locked, edit_event(locked, path="tests/other.py", agent_id=None))) == "allow"


def test_ac4_lock_line_with_no_id_in_the_file_name_is_in_force(tmp_path):
    root = make_project(tmp_path, board(), {"NOTES": lock_guide(ORACLE)})
    assert verdict(run_hook(root, edit_event(root, agent_type="common-infrastructure"))) == "deny"


def test_ac4_import_failure_denies_a_bound_caller_and_passes_the_supervisor(locked, tmp_path):
    lone = tmp_path / "lone_hooks"
    lone.mkdir()
    shutil.copy(HOOK, lone / HOOK.name)  # no lib/ beside it: the helper import fails
    bound = run_hook(locked, edit_event(locked, agent_type="common-infrastructure"), hook=lone / HOOK.name)
    assert verdict(bound) == "deny" and "lib" in reason(bound)
    assert verdict(run_hook(locked, edit_event(locked, agent_id=None), hook=lone / HOOK.name)) == "allow"
    assert verdict(run_hook(locked, edit_event(locked, agent_type="qa-expert"), hook=lone / HOOK.name)) == "allow"


# --- Edge cases ---------------------------------------------------------------------------

def test_edge_two_paths_on_one_line_and_two_lock_lines(tmp_path):
    guide = lock_guide(ORACLE, SECOND, extra="\n**Locked oracle**: `tests/third.py`\n")
    root = make_project(tmp_path, board(In_Progress=["T066"]), {"T066": guide})
    for path in (ORACLE, SECOND, "tests/third.py"):
        assert verdict(run_hook(root, edit_event(root, path=path, agent_type="backend-developer"))) == "deny", path


def test_edge_paths_without_backticks_are_read(tmp_path):
    guide = f"# TASK_GUIDE — T066\n\n**Locked oracle**: {ORACLE}, {SECOND}\n"
    root = make_project(tmp_path, board(In_Progress=["T066"]), {"T066": guide})
    assert verdict(run_hook(root, edit_event(root, path=SECOND, agent_type="backend-developer"))) == "deny"


@pytest.mark.parametrize("spelling", [
    "./.claude/hooks/tests/test_agent_guide_dedup.py",
    ".claude/hooks/../hooks/tests/test_agent_guide_dedup.py",
    ".claude/hooks/tests//test_agent_guide_dedup.py",
    ".claude/hooks/TESTS/Test_Agent_Guide_Dedup.py",
], ids=["dot", "dotdot", "double-slash", "case"])
def test_edge_path_spellings_resolve_to_the_locked_file(locked, spelling):
    event = edit_event(locked, agent_type="common-infrastructure", cwd=str(locked))
    event["tool_input"]["file_path"] = spelling  # relative: resolved against the event cwd
    assert verdict(run_hook(locked, event)) == "deny"


def test_edge_dotdot_escape_from_a_sibling_dir_resolves(locked):
    spelling = str(locked / "tests" / ".." / ORACLE)
    assert verdict(run_hook(locked, edit_event(locked, path=spelling, agent_type="common-infrastructure"))) == "deny"


def test_edge_symlink_alias_to_the_locked_file_is_denied(locked, tmp_path_factory):
    (locked / ".claude" / "hooks" / "tests").mkdir(parents=True)
    (locked / ".claude" / "hooks" / "tests" / "test_agent_guide_dedup.py").write_text("x", encoding="utf-8")
    outside = tmp_path_factory.mktemp("outside")
    alias = outside / "alias.py"
    alias.symlink_to(locked / ORACLE)
    linkdir = outside / "linkdir"
    linkdir.symlink_to(locked / ".claude" / "hooks" / "tests", target_is_directory=True)
    for target in (alias, linkdir / "test_agent_guide_dedup.py"):
        event = edit_event(locked, path=str(target), agent_type="common-infrastructure")
        assert verdict(run_hook(locked, event)) == "deny", target


def test_edge_absolute_lock_entry_outside_the_repo(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("elsewhere") / "oracle.py"
    root = make_project(tmp_path, board(In_Progress=["T066"]), {"T066": lock_guide(str(outside))})
    assert verdict(run_hook(root, edit_event(root, path=str(outside), agent_type="backend-developer"))) == "deny"
    assert verdict(run_hook(root, edit_event(root, path="oracle.py", agent_type="backend-developer"))) == "allow"


def test_edge_relative_path_uses_the_event_cwd(locked):
    event = edit_event(locked, agent_type="common-infrastructure", cwd=str(locked))
    event["tool_input"]["file_path"] = ORACLE
    assert verdict(run_hook(locked, event)) == "deny"


def test_edge_locked_by_two_tasks_in_progress_wins_over_done(tmp_path):
    # T001 sorts first and is Done; T002 is In Progress. The In Progress lock must still apply.
    root = make_project(tmp_path, board(Done=["T001"], In_Progress=["T002"]),
                        {"T001": lock_guide(ORACLE, title="T001"), "T002": lock_guide(ORACLE, title="T002")})
    proc = run_hook(root, edit_event(root, agent_type="common-infrastructure"))
    assert verdict(proc) == "deny" and "TASK_GUIDE_T002.md" in reason(proc)
    root2 = make_project(tmp_path / "second", board(In_Progress=["T001"], Done=["T002"]),
                         {"T001": lock_guide(ORACLE, title="T001"), "T002": lock_guide(ORACLE, title="T002")})
    proc2 = run_hook(root2, edit_event(root2, agent_type="common-infrastructure"))
    assert verdict(proc2) == "deny" and "TASK_GUIDE_T001.md" in reason(proc2)


def test_edge_only_the_in_progress_task_of_two_locks_a_file(tmp_path):
    root = make_project(tmp_path, board(Done=["T001"], In_Progress=["T002"]),
                        {"T001": lock_guide(ORACLE, title="T001"), "T002": lock_guide(SECOND, title="T002")})
    assert verdict(run_hook(root, edit_event(root, path=ORACLE, agent_type="common-infrastructure"))) == "allow"
    assert verdict(run_hook(root, edit_event(root, path=SECOND, agent_type="common-infrastructure"))) == "deny"


# --- Worktrees: the implementer edits the oracle through its worktree path ----------------

def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t"))


@pytest.fixture
def with_worktree(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    make_project(main, board(In_Progress=["T066"]), {"T066": lock_guide(ORACLE)})
    _git(main, "init", "-q")
    _git(main, "add", "-A")
    _git(main, "commit", "-q", "-m", "init")
    wt = tmp_path / "wt-t066"
    _git(main, "worktree", "add", "-q", str(wt), "-b", "feat/t066")
    return main, wt


def test_worktree_path_of_the_locked_file_is_denied(with_worktree):
    main, wt = with_worktree
    for project in (main, wt):  # the session may be rooted in either checkout
        event = edit_event(wt, agent_type="common-infrastructure")
        assert verdict(run_hook(project, event)) == "deny", project


def test_worktree_nested_inside_the_main_checkout_is_denied(with_worktree, tmp_path):
    main, _ = with_worktree
    nested = main / ".claude" / "worktrees" / "wt-nested"
    _git(main, "worktree", "add", "-q", str(nested), "-b", "feat/nested")
    event = edit_event(nested, agent_type="common-infrastructure")
    assert verdict(run_hook(main, event)) == "deny"


def test_worktree_session_reads_the_board_of_the_main_checkout(with_worktree):
    main, wt = with_worktree
    (main / "PROJECT_KANBAN.md").write_text(board(Ready_for_Review=["T066"]), encoding="utf-8")  # moved on main only
    event = edit_event(wt, agent_type="common-infrastructure")
    assert verdict(run_hook(wt, event)) == "allow"


def test_worktree_other_file_is_not_locked(with_worktree):
    _, wt = with_worktree
    event = edit_event(wt, path="tests/unrelated.py", agent_type="common-infrastructure")
    assert verdict(run_hook(wt, event)) == "allow"


# --- AC7: the T082 replay with the real T066 guide ----------------------------------------

def test_ac7_t082_replay_implementer_less_than_to_less_equal_is_denied(tmp_path):
    real = (REPO / "tasks" / "TASK_GUIDE_T066.md").read_text(encoding="utf-8")
    root = make_project(tmp_path, board(In_Progress=["T066"]),
                        {"T066": real + f"\n**Locked oracle**: `{ORACLE}`\n"})
    event = edit_event(root, agent_type="common-infrastructure")
    event["tool_input"]["old_string"], event["tool_input"]["new_string"] = "assert a < b", "assert a <= b"
    proc = run_hook(root, event)
    assert verdict(proc) == "deny"
    assert "tasks/TASK_GUIDE_T066.md" in reason(proc)
    for same_edit_by in (edit_event(root, agent_type="qa-expert"), edit_event(root, agent_id=None)):
        assert verdict(run_hook(root, same_edit_by)) == "allow"


# --- AC5: the guide template ---------------------------------------------------------------

TEMPLATE = REPO / "templates" / "TASK_GUIDE_template.md"


def test_ac5_template_documents_the_optional_locked_oracle_line():
    text = TEMPLATE.read_text(encoding="utf-8")
    line = next(l for l in text.splitlines() if "**Locked oracle**:" in l)
    assert not line.startswith("**Locked oracle**:"), "the template line must stay inert"
    assert "In Progress" in line and "qa-expert" in line


def test_ac5_an_unedited_template_locks_nothing(tmp_path):
    root = make_project(tmp_path, board(In_Progress=["T066"]), {"T066": TEMPLATE.read_text(encoding="utf-8")})
    for path in (ORACLE, "path/to/oracle_test.py", "[path]", "tests/test_x.py"):
        assert verdict(run_hook(root, edit_event(root, path=path, agent_type="backend-developer"))) == "allow", path


def test_ac5_implementer_guides_need_no_mention():
    for name in ("common-infrastructure", "backend", "frontend", "qa"):
        assert "Locked oracle" not in (REPO / "agents" / f"{name}.md").read_text(encoding="utf-8")


def test_the_one_line_of_doctrine_names_the_lock():
    text = (REPO / "docs" / "claude-md" / "pipeline-stages.md").read_text(encoding="utf-8")
    line = next(l for l in text.splitlines() if "Locked oracle" in l)
    assert "In Progress" in line and "qa-expert" in line
