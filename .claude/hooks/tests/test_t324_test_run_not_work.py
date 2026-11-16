#!/usr/bin/env python3
"""T324 — a test run in a task's worktree is not work on the task, for the Stop check only.
LOCKED ORACLE (qa-expert): the implementer may not edit this file.

  AC 1 — `worked_on(..., test_runs_count=False)` is False for a test run in the task's worktree.
  AC 2 — with `test_runs_count=False`, a write, a commit, a spawn, a redirect, a script, a chained
         write, a double `timeout` and a test run plus an `Edit` stay work.
  AC 3 — without the keyword every case keeps today's answer; the merge gate file is byte-identical
         to `main`.
  AC 4 — `work_start(..., test_runs_count=False)` starts at the first call `worked_on` counts with
         the same keyword; the default is unchanged.
  AC 5 — the incident end to end through the Stop hook: not blocked, "not checked" on stderr, the
         task's report byte-identical after the first and the second fire; plus an `Edit` → blocked.
  AC 6 — `session_owner` and `session_window` both pass `test_runs_count=False` (a spy on the
         copied lib, and the Debate window behaviour: a test run before the first edit does not
         start the window).

Fixture transcripts copy the shape of real Claude Code entries; no real transcript line is committed.

Run with: python3 -m pytest .claude/hooks/tests/test_t324_test_run_not_work.py -q -p no:cacheprovider
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t250_session_ownership import (  # noqa: E402
    HOOKS, SID, _git, gate_env, gate_project, human, sw, tool_use, write_transcript,
)

WT = "/work/wt-t900"   # the task's worktree
MAIN = "/work/repo"    # the main checkout: the session's cwd
REPO = HOOKS.parent.parent

INCIDENT = (f"cd {WT} && timeout 300 python3 -m pytest .claude/hooks/tests/test_t900_x.py -q "
            "--no-header -p no:cacheprovider -rf 2>&1 | tail -40")


def bash(command, cwd=MAIN):
    return ("Bash", {"command": command, "description": "x"}, cwd)


def call(name, tool_input, cwd=MAIN):
    return (name, tool_input, cwd)


def edit_review(path=f"{WT}/tasks/TASK_REVIEW_T900.md"):
    return call("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})


# ── the cases ────────────────────────────────────────────────────────────────────────────────
TEST_RUNS = [  # AC 1: a test run in the worktree — not work with test_runs_count=False
    ("incident", [bash(INCIDENT)]),
    ("pytest-module-cwd-in-wt", [bash("python3 -m pytest -q", cwd=WT)]),
    ("pytest-bare", [bash("pytest -q", cwd=WT)]),
    ("py.test", [bash("py.test", cwd=WT)]),
    ("unittest-with-flag", [bash("python3 -B -m unittest", cwd=WT)]),
    ("timeout-python", [bash("timeout 60 python -m pytest", cwd=WT)]),
    ("cwd-in-wt-subdir", [bash("python3 -m pytest -q", cwd=f"{WT}/sub")]),
    ("cd-relative-pytest", [bash("cd ../wt-t900 && python3 -m pytest -q")]),
]

STILL_WORK = [  # AC 2: work with test_runs_count=False too
    ("timeout-rm", [bash("timeout 300 rm -rf x", cwd=WT)]),
    ("pytest-redirect-into-wt", [bash(f"python3 -m pytest -q > {WT}/out", cwd=WT)]),
    ("pytest-redirect-relative", [bash("python3 -m pytest -q > out.txt", cwd=WT)]),
    ("python-script", [bash("python3 tool.py", cwd=WT)]),
    ("pytest-then-rm", [bash("pytest -q && rm x", cwd=WT)]),
    ("pytest-pipe-tee", [bash("timeout 300 python3 -m pytest -q | tee out.txt", cwd=WT)]),
    ("double-timeout", [bash("timeout 5 timeout 5 python3 -m pytest", cwd=WT)]),
    ("timeout-with-flag", [bash("timeout -s KILL 5 python3 -m pytest -q", cwd=WT)]),
    ("python-m-pip", [bash("python3 -m pip install x", cwd=WT)]),
    ("bash-c-pytest", [bash("bash -c 'python3 -m pytest -q'", cwd=WT)]),
    ("test-run-plus-edit", [bash(INCIDENT), edit_review()]),
    # every write/commit/spawn case of test_t250_session_ownership.py (AC 4 there)
    ("t250-edit-guide", [call("Edit", {"file_path": f"{MAIN}/tasks/TASK_GUIDE_T900.md",
                                       "old_string": "a", "new_string": "b"})]),
    ("t250-write-in-worktree", [call("Write", {"file_path": f"{WT}/src/app.py", "content": "x"})]),
    ("t250-write-review", [call("Write", {"file_path": f"{MAIN}/tasks/TASK_REVIEW_T900.md",
                                          "content": "x"})]),
    ("t250-notebook", [call("NotebookEdit", {"notebook_path": f"{WT}/n.ipynb", "new_source": "x"})]),
    ("t250-cd-worktree-commit", [bash(f"cd {WT} && git commit -qm 'T900 work'")]),
    ("t250-heredoc-into-review", [bash("cat > tasks/TASK_REVIEW_T900.md <<'EOF'\nhello\nEOF")]),
    ("t250-sed-in-place", [bash("sed -i 's/a/b/' tasks/TASK_GUIDE_T900.md")]),
    ("t250-sort-output", [bash("sort -o tasks/TASK_GUIDE_T900.md tasks/TASK_GUIDE_T900.md")]),
    ("t250-append-into-worktree", [bash("echo done >> ../wt-t900/notes.txt")]),
    ("t250-git-C-commit", [bash("git -C ../wt-t900 commit -qm x")]),
    ("t250-bash-c-string", [bash("bash -c 'echo x > tasks/TASK_REVIEW_T900.md'")]),
    ("t250-eval-string", [bash("eval \"rm ../wt-t900/old.txt\"")]),
    ("t250-agent-spawn", [call("Agent", {"description": "T900 implement",
                                         "subagent_type": "backend-developer",
                                         "prompt": "Task ID: T900\nGuide: tasks/TASK_GUIDE_T900.md\n"})]),
]

READS = [  # never work, either way
    ("bash-grep-review", [bash("grep -n Risk tasks/TASK_REVIEW_T900.md")]),
    ("cd-worktree-log", [bash(f"cd {WT} && git log --oneline -3")]),
]


def _ids(cases):
    return [c[0] for c in cases]


def _calls(cases):
    return [c[1] for c in cases]


# ── AC 1 ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("calls", _calls(TEST_RUNS), ids=_ids(TEST_RUNS))
def test_ac1_a_test_run_in_the_worktree_is_not_work_for_the_stop_check(calls):
    assert sw.worked_on(calls, "T900", [WT], test_runs_count=False) is False


@pytest.mark.parametrize("calls", _calls(READS), ids=_ids(READS))
def test_ac1_a_read_stays_not_work_with_the_keyword(calls):
    assert sw.worked_on(calls, "T900", [WT], test_runs_count=False) is False


# ── AC 2 ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("calls", _calls(STILL_WORK), ids=_ids(STILL_WORK))
def test_ac2_a_write_commit_or_spawn_stays_work_with_the_keyword(calls):
    assert sw.worked_on(calls, "T900", [WT], test_runs_count=False) is True


def test_ac2_the_keyword_is_keyword_only():
    with pytest.raises(TypeError):
        sw.worked_on([bash(INCIDENT)], "T900", [WT], False)  # noqa: FBT003 - positional on purpose


# ── AC 3 ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("calls", _calls(TEST_RUNS + STILL_WORK),
                         ids=_ids(TEST_RUNS + STILL_WORK))
def test_ac3_by_default_every_case_is_work_as_today(calls):
    assert sw.worked_on(calls, "T900", [WT]) is True


@pytest.mark.parametrize("calls", _calls(READS), ids=_ids(READS))
def test_ac3_by_default_a_read_is_not_work_as_today(calls):
    assert sw.worked_on(calls, "T900", [WT]) is False


def test_ac3_the_default_is_true_when_passed_explicitly():
    assert sw.worked_on([bash(INCIDENT)], "T900", [WT], test_runs_count=True) is True


def test_ac3_the_merge_gate_is_byte_identical_to_main():
    rel = ".claude/hooks/pre_bash_block_unsafe_merge.py"
    done = subprocess.run(["git", "-C", str(REPO), "show", f"main:{rel}"], capture_output=True,
                          timeout=30)
    assert done.returncode == 0, done.stderr  # fail closed: no `main` copy is a failure
    assert (REPO / rel).read_bytes() == done.stdout


# ── AC 4 ─────────────────────────────────────────────────────────────────────────────────────
T0 = datetime(2026, 11, 16, 10, 0, 0, tzinfo=timezone.utc)
T1 = T0 + timedelta(minutes=5)
T2 = T0 + timedelta(minutes=9)


def _entries(*timed):
    return [(ts, name, tool_input, cwd) for ts, (name, tool_input, cwd) in timed]


def test_ac4_a_test_run_before_the_first_edit_does_not_start_the_window():
    entries = _entries((T0, bash(INCIDENT)), (T1, bash("grep x tasks/TASK_REVIEW_T900.md")),
                       (T2, edit_review()))
    assert sw.work_start(entries, "T900", [WT], test_runs_count=False) == T2


def test_ac4_by_default_the_test_run_still_starts_the_window():
    entries = _entries((T0, bash(INCIDENT)), (T2, edit_review()))
    assert sw.work_start(entries, "T900", [WT]) == T0


def test_ac4_only_test_runs_give_no_window():
    entries = _entries((T0, bash(INCIDENT)), (T1, bash("pytest -q", cwd=WT)))
    assert sw.work_start(entries, "T900", [WT], test_runs_count=False) is None


def test_ac4_a_writing_test_command_still_starts_the_window():
    entries = _entries((T0, bash("pytest -q && rm x", cwd=WT)), (T2, edit_review()))
    assert sw.work_start(entries, "T900", [WT], test_runs_count=False) == T0


@pytest.mark.parametrize("calls", _calls(TEST_RUNS + STILL_WORK + READS),
                         ids=_ids(TEST_RUNS + STILL_WORK + READS))
@pytest.mark.parametrize("counts", [True, False], ids=["default", "no-test-runs"])
def test_ac4_work_start_and_worked_on_agree(calls, counts):
    entries = [(T0 + timedelta(seconds=i), *c) for i, c in enumerate(calls)]
    kw = {} if counts else {"test_runs_count": False}
    start = sw.work_start(entries, "T900", [WT], **kw)
    assert (start is not None) == sw.worked_on(calls, "T900", [WT], **kw)


# ── AC 5, AC 6 — the Stop hook end to end ────────────────────────────────────────────────────
STOP = "stop_auto_mode_check.py"
BRANCH = "fix/t900-x"
ROW = ("- [ ] **T900** — Another session's auto task | common-infrastructure | C2 | Risk: High | P1 "
       f"| Guide: `tasks/TASK_GUIDE_T900.md` | Started 2026-11-16: branch `{BRANCH}`, "
       "worktree `../wt-t900`")
GUIDE = "# TASK_GUIDE — T900\n**Complexity Level**: C2\n**Risk Level**: High\n"
ADVOCATES = "Advocate 1: D; Advocate 2: D; Advocate 3: A"
# A marked report with no Debate, no reviews in the trace, no `Memory:` line: it fails the check.
INCIDENT_REVIEW = ("# TASK_REVIEW — T900\n\n## Auto decisions\n\nMode: auto\n"
                   "1. picked D — RULE: `docs/claude-md/tracks.md` `### Backups`\n"
                   "Not done: merge (yours)\n\n## Evidence\n\n| Check | Result | Notes |\n")
# A marked report with one 3-Advocate Debate: only the Debate window decides D10.
DEBATED_REVIEW = ("# TASK_REVIEW — T900\n\n## Auto decisions\n\nMode: auto\n"
                  f"1. picked D — DEBATED: option D ({ADVOCATES})\n"
                  "Memory: nothing new\nNot done: merge (yours)\n\n"
                  "## Evidence\n\n| Check | Result | Notes |\n")
DEBATE_BEFORE_WINDOW = "a Debate was found before the task's first change in this session"
D10_REASON = "Risk High, but no decision was DEBATED with 3 Advocates"


def _at(seconds_ago):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()


def project_with_task_in_worktree(tmp_path, review):
    """A kit project; T900 In Progress at Risk High on `fix/t900-x`, checked out in `wt-t900`,
    whose report (only in the worktree) is marked `Mode: auto`."""
    project = gate_project(tmp_path, in_progress=(ROW,), files={"tasks/TASK_GUIDE_T900.md": GUIDE})
    _git(project, "checkout", "-q", "-b", BRANCH)
    (project / "tasks" / "TASK_REVIEW_T900.md").write_text(review, encoding="utf-8")
    (project / "t900.txt").write_text("unfinished\n", encoding="utf-8")
    _git(project, "add", "-A")
    _git(project, "commit", "-qm", "T900: work")
    _git(project, "checkout", "-q", "main")
    wt = tmp_path / "wt-t900"
    _git(project, "worktree", "add", "-q", str(wt), BRANCH)
    return project, wt


def entry(name, tool_input, ts, cwd, use_id):
    return {"type": "assistant", "timestamp": ts, "cwd": cwd, "sessionId": SID,
            "message": {"role": "assistant", "content": [
                {"type": "tool_use", "id": use_id, "name": name, "input": tool_input}]}}


def result(use_id, ts):
    return {"type": "user", "timestamp": ts, "sessionId": SID, "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": use_id, "content": "ok", "is_error": False}]}}


def incident_run(project, wt, ts):
    command = (f"cd {wt} && timeout 300 python3 -m pytest .claude/hooks/tests/test_t900_x.py -q "
               "--no-header -p no:cacheprovider -rf 2>&1 | tail -40")
    return [entry("Bash", {"command": command, "description": "run T900's oracle"}, ts,
                  str(project), "toolu_run"), result("toolu_run", ts)]


def review_edit(project, wt, ts):
    return [entry("Edit", {"file_path": str(wt / "tasks" / "TASK_REVIEW_T900.md"),
                           "old_string": "picked D", "new_string": "picked D"}, ts, str(project),
                  "toolu_edit"), result("toolu_edit", ts)]


def transcript(tmp_path, entries):
    """A session with no `[auto]`/`[admin]` tag in any request."""
    return write_transcript(tmp_path / "projects" / f"{SID}.jsonl",
                            [human("check T900's oracle, read-only", _at(900))] + entries)


def stop_env(project, **extra):
    env = gate_env(project, **extra)
    for key in ("CLAUDE_AUTO_VERIFY_RUN", "CLAUDE_ACTIVE_TASK", "CLAUDE_CODE_SESSION_ID"):
        env.pop(key, None)
    return env


def run_stop(project, transcript_path, second_fire=False, env=None):
    event = {"session_id": SID, "transcript_path": str(transcript_path), "hook_event_name": "Stop",
             "stop_hook_active": second_fire}
    done = subprocess.run([sys.executable, str(project / ".claude" / "hooks" / STOP)],
                          input=json.dumps(event), capture_output=True, text=True, cwd=project,
                          env=env or stop_env(project), timeout=60)
    out = json.loads(done.stdout) if done.stdout.strip() else {}
    return (out.get("reason", "") if out.get("decision") == "block" else None), done.stderr


def test_ac5_the_incident_test_run_does_not_block_and_writes_nothing(tmp_path):
    project, wt = project_with_task_in_worktree(tmp_path, INCIDENT_REVIEW)
    review = wt / "tasks" / "TASK_REVIEW_T900.md"
    before = review.read_bytes()
    t = transcript(tmp_path, incident_run(project, wt, _at(600)))

    reason, stderr = run_stop(project, t)
    assert reason is None, reason
    assert "T900" in stderr and "not checked" in stderr, stderr
    assert review.read_bytes() == before

    reason, stderr = run_stop(project, t, second_fire=True)
    assert reason is None, reason
    assert "Paused:" not in review.read_text(encoding="utf-8")
    assert review.read_bytes() == before


def test_ac5_the_test_run_plus_an_edit_of_the_report_blocks_as_today(tmp_path):
    project, wt = project_with_task_in_worktree(tmp_path, INCIDENT_REVIEW)
    t = transcript(tmp_path, incident_run(project, wt, _at(600)) + review_edit(project, wt, _at(300)))
    reason, stderr = run_stop(project, t)
    assert reason and "T900" in reason, (reason, stderr)
    assert "Memory:" in reason and D10_REASON in reason, reason


def test_ac5_the_test_run_plus_a_writing_command_in_the_worktree_blocks(tmp_path):
    project, wt = project_with_task_in_worktree(tmp_path, INCIDENT_REVIEW)
    write = [entry("Bash", {"command": f"cd {wt} && pytest -q && rm -f t900.txt", "description": "x"},
                   _at(300), str(project), "toolu_rm"), result("toolu_rm", _at(300))]
    t = transcript(tmp_path, incident_run(project, wt, _at(600)) + write)
    reason, stderr = run_stop(project, t)
    assert reason and "T900" in reason, (reason, stderr)


SPY = '''

# --- T324 oracle spy: record the keywords each Stop-hook reader passes ---
_t324_worked_on, _t324_work_start = worked_on, work_start


def _t324_log(fn, kwargs):
    with open(os.environ["T324_SPY"], "a", encoding="utf-8") as spy:
        spy.write(json.dumps({"fn": fn, "kwargs": {k: repr(v) for k, v in kwargs.items()}}) + "\\n")


def worked_on(*args, **kwargs):
    _t324_log("worked_on", kwargs)
    return _t324_worked_on(*args, **kwargs)


def work_start(*args, **kwargs):
    _t324_log("work_start", kwargs)
    return _t324_work_start(*args, **kwargs)
'''


def debate(project, wt, skill_at, advocates_at):
    """A `resolve-question` Skill call for T900, then 3 Advocate `Agent` calls that ran."""
    out = [entry("Skill", {"skill": "resolve-question", "args": "task=T900"}, skill_at,
                 str(project), "toolu_rq"), result("toolu_rq", skill_at)]
    for n in (1, 2, 3):
        use_id = f"toolu_adv{n}"
        out += [entry("Agent", {"description": f"Advocate {n}: option", "subagent_type": "general",
                                "prompt": "Using the repo, answer alone: which option?"},
                      advocates_at, str(project), use_id), result(use_id, advocates_at)]
    return out


def test_ac6_both_stop_hook_readers_pass_test_runs_count_false(tmp_path):
    """A spy on the copied `session_work`: `session_owner` calls `worked_on`, `session_window` calls
    `work_start` (read only for a task with a Debate in this session), each with the keyword False."""
    project, wt = project_with_task_in_worktree(tmp_path, DEBATED_REVIEW)
    lib = project / ".claude" / "hooks" / "lib" / "session_work.py"
    lib.write_text(lib.read_text(encoding="utf-8") + SPY, encoding="utf-8")
    spy = tmp_path / "spy.jsonl"
    t = transcript(tmp_path, debate(project, wt, _at(500), _at(450)) + review_edit(project, wt, _at(300)))
    run_stop(project, t, env=stop_env(project, T324_SPY=str(spy)))
    assert spy.exists(), "the Stop hook called neither worked_on nor work_start"
    seen = [json.loads(line) for line in spy.read_text(encoding="utf-8").splitlines()]
    by_fn = {fn: [s["kwargs"] for s in seen if s["fn"] == fn] for fn in ("worked_on", "work_start")}
    assert by_fn["worked_on"], seen
    assert by_fn["work_start"], seen
    for fn, calls in by_fn.items():
        assert all(kw.get("test_runs_count") == "False" for kw in calls), (fn, calls)


def test_ac6_a_test_run_before_the_first_edit_does_not_start_the_debate_window(tmp_path):
    """Test run (t-600), Debate (t-500/t-450), then the first edit (t-300). With the test run as
    work the window opens at t-600 and the Debate counts; without it the window opens at t-300, so
    the Debate falls before it: D10 fails with the "before the task's first change" hint."""
    project, wt = project_with_task_in_worktree(tmp_path, DEBATED_REVIEW)
    t = transcript(tmp_path, incident_run(project, wt, _at(600)) + debate(project, wt, _at(500), _at(450))
                   + review_edit(project, wt, _at(300)))
    reason, stderr = run_stop(project, t)
    assert reason and "T900" in reason, (reason, stderr)
    assert D10_REASON in reason and DEBATE_BEFORE_WINDOW in reason, reason


def test_ac6_a_debate_after_the_first_edit_still_counts(tmp_path):
    """Control: the same Debate after the first edit is inside the window either way."""
    project, wt = project_with_task_in_worktree(tmp_path, DEBATED_REVIEW)
    t = transcript(tmp_path, incident_run(project, wt, _at(600)) + review_edit(project, wt, _at(500))
                   + debate(project, wt, _at(400), _at(350)))
    reason, stderr = run_stop(project, t)
    assert not reason or (D10_REASON not in reason and DEBATE_BEFORE_WINDOW not in reason), reason
