#!/usr/bin/env python3
"""T287 — the auto-mode Stop check finds a task's tests and Advocate calls when they ran.

The T283 spike counted 6 avoidable `Paused:` stops as "trace attribution". Reproduced from the real
traces (`tasks/TASK_REVIEW_T287.md` § Root causes), they split three ways:

  Cause A — T219, T226: the Stop check fired before Stage 4 had run (the Supervisor ended its turn
            right after a background spawn). The work did not run yet: a real stop. Not changed.
  Cause B — T120 (×2): the Supervisor ran T120's tests in T120's worktree, but the session's one
            active-task pointer named T250 (then T119), so the trace hook filed them there.
  Cause C — T242 (×2): the Debate's `resolve-question` call said `task=T242`, but the pointer still
            named T241, and an Advocate prompt carries no task ID, so its calls went to T241.

Every fixture drives the real hooks as the harness does: each tool call goes through
`post_tool_trace.py` (so the trace files are written by the hook, never by hand), the same calls
are recorded in a session transcript of the real shape, and then `stop_auto_mode_check.py` runs.

  AC 1/2 — the T120- and T242-shaped runs are not paused; the work is found.
  AC 3   — the same runs with the work removed pause, with today's message.
  AC 4   — another session's calls, and calls for another task, are not credited.
  AC 5   — the stops that stay: their text is unchanged, and the step limit and the sensitive-path
           hook still resolve a call by the session pointer, as before.

Run with: python3 -m pytest .claude/hooks/tests/test_stop_attribution_t287.py -q
"""
import json
import os
import shutil

import pytest
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent
ROOT = HOOKS.parent.parent
SID = "aaaaaaaa-1111-2222-3333-444444444444"
OTHER_SID = "bbbbbbbb-1111-2222-3333-444444444444"
ADVOCATE_TEMPLATE = ROOT / "skills" / "resolve-question" / "references" / "advocate.md"


def _ago(seconds):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


def _git(cwd, *args):
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def kit_project(tmp_path, rows, files):
    """A temp kit project: the hooks, a board whose Ready for Review column holds `rows`, `files`,
    and one commit."""
    project = tmp_path / "repo"
    (project / ".claude").mkdir(parents=True)
    shutil.copytree(HOOKS, project / ".claude" / "hooks",
                    ignore=shutil.ignore_patterns("tests", "__pycache__", ".state"))
    for rel, text in files.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    (project / "PROJECT_KANBAN.md").write_text(
        "# Kanban\n\n### Todo\n\n### In Progress\n\n### Ready for Review\n" + "\n".join(rows) +
        "\n\n### Done\n", encoding="utf-8")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "config", "user.email", "t@example.com")
    _git(project, "config", "user.name", "t")
    _git(project, "add", "-A")
    _git(project, "commit", "-qm", "base")
    return project


def hook_env(project, tmp_path):
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_ACTIVE_TASK", "CLAUDE_PROJECT_DIR", "CLAUDE_AUTO_VERIFY_RUN",
                        "LINEAR_API_KEY", "CLAUDE_STEP_LIMIT")}
    env["CLAUDE_PROJECT_DIR"] = str(project)
    env["CLAUDE_TRACE_ANCHOR_DIR"] = str(tmp_path / "anchors")
    return env


class Session:
    """One Claude Code session: its transcript, and its tool calls sent through the real trace hook.
    A main-session call carries no `agent_id`, so the trace hook files it by its own signals or by
    the session's active-task pointer (`.claude/hooks/.state/active_task.d/<session id>`)."""

    def __init__(self, project, tmp_path, sid=SID):
        self.project, self.tmp_path, self.sid = project, tmp_path, sid
        self.transcript = tmp_path / "projects" / f"{sid}.jsonl"
        self.transcript.parent.mkdir(parents=True, exist_ok=True)
        self.transcript.touch()

    def _entry(self, entry):
        with open(self.transcript, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def request(self, text, seconds_ago=600):
        self._entry({"type": "user", "message": {"role": "user", "content": text},
                     "timestamp": _ago(seconds_ago), "origin": {"kind": "human"},
                     "isSidechain": False, "sessionId": self.sid, "cwd": str(self.project)})

    def point_at(self, task_id):
        """The session's pointer as a `printf '%s\\n%s\\n' "Txxx" "$(date ...)" > …` leaves it."""
        state = self.project / ".claude" / "hooks" / ".state" / "active_task.d"
        state.mkdir(parents=True, exist_ok=True)
        (state / self.sid).write_text(f"{task_id}\n{_ago(0)}\n", encoding="utf-8")

    calls = 0

    def call(self, name, tool_input, cwd=None, result="ok", env=None):
        """`result`: "ok" or "error" writes the call's `tool_result`; None writes none (a call a
        PreToolUse hook or the user denied never ran, so it gets no trace record either)."""
        cwd = str(cwd or self.project)
        Session.calls += 1
        use_id = f"toolu_{Session.calls:04d}"
        self._entry({"type": "assistant", "timestamp": _ago(0), "cwd": cwd, "sessionId": self.sid,
                     "message": {"role": "assistant", "content": [
                         {"type": "tool_use", "id": use_id, "name": name, "input": tool_input}]}})
        if result is None:
            return
        self._entry({"type": "user", "timestamp": _ago(0), "cwd": cwd, "sessionId": self.sid,
                     "message": {"role": "user", "content": [
                         {"type": "tool_result", "tool_use_id": use_id, "content": "done",
                          "is_error": result == "error"}]}})
        event = {"session_id": self.sid, "transcript_path": str(self.transcript), "cwd": cwd,
                 "hook_event_name": "PostToolUse", "tool_name": name, "tool_input": tool_input,
                 "tool_response": {}}
        done = subprocess.run([sys.executable, str(self.project / ".claude" / "hooks" /
                                                   "post_tool_trace.py")],
                              input=json.dumps(event), capture_output=True, text=True,
                              cwd=self.project, env=env or hook_env(self.project, self.tmp_path),
                              timeout=60)
        assert done.returncode == 0, done.stderr

    def stop(self):
        """(block reason or None, stderr) of the real Stop check at this session's stop."""
        event = {"session_id": self.sid, "transcript_path": str(self.transcript),
                 "hook_event_name": "Stop", "stop_hook_active": False}
        done = subprocess.run([sys.executable, str(self.project / ".claude" / "hooks" /
                                                   "stop_auto_mode_check.py")],
                              input=json.dumps(event), capture_output=True, text=True,
                              cwd=self.project, env=hook_env(self.project, self.tmp_path), timeout=60)
        out = json.loads(done.stdout) if done.stdout.strip() else {}
        return (out.get("reason", "") if out.get("decision") == "block" else None), done.stderr


def trace(project, task_id):
    path = project / "memory" / "event-trace" / f"{task_id}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def advocate_input(n, question="how to shrink the plugin install?"):
    """An Advocate `Agent` call as the Debate step builds it from `references/advocate.md`."""
    block = ADVOCATE_TEMPLATE.read_text(encoding="utf-8").split("```")[1].strip("\n")
    return {"description": f"Advocate {n}: {question}", "subagent_type": "Explore",
            "prompt": block.replace("{question}", question)}


# ── Cause B — T120: tests in the task's worktree, the session pointer names another task ───────
T120_ROW = ("- [ ] **T120** — Reinstall's closing summary names every CLI | Supervisor | C0 | "
            "Risk: Low | P2 | Track: minimal | Record: `tasks/MINIMAL_LOG.md`")
T120_RECORD = """# Minimal-track Decision records

## T120 — Reinstall's closing summary names every CLI the run touched · minimal
Mode: auto
**Asked:** "start the parallel task [auto]"
**Decisions:**
1. T120 runs on the minimal track — RULE: `docs/claude-md/tracks.md` `## Track rule`
**Checked:**
- Suite: `python3 -m pytest -q` — 3 passed
**Files:** `setup.sh`
**Memory:** nothing new
**Not done:** merge (yours); auto verify: running (T182)
"""
T120_PAUSE = "T120: no test run in memory/event-trace/T120.jsonl — write "


def t120_project(tmp_path):
    project = kit_project(tmp_path, [T120_ROW], {"tasks/MINIMAL_LOG.md": T120_RECORD,
                                                  "setup.sh": "echo v1\n"})
    for branch, name in (("fix/t120-reinstall-summary", "wt-t120"), ("fix/t121-other", "wt-t121")):
        _git(project, "worktree", "add", "-q", "-b", branch, str(tmp_path / name))
    return project


def gate_sees_test_run(project, tmp_path, task_id):
    """The merge gate's own `trace_shows_verification`, as the auto close-out's Gate 5 calls it."""
    code = ("import sys; sys.path.insert(0, '.claude/hooks/lib'); import auto_closeout as ac; "
            f"print(ac.load_gate().trace_shows_verification('{task_id}'))")
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          cwd=project, env=hook_env(project, tmp_path), timeout=60)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip() == "True"


def test_ac2_t120_tests_run_in_its_worktree_are_found(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.request("yes, and start the parallel task [auto]")
    s.point_at("T250")  # as at 10:40:16: another writer re-pointed the session's one pointer
    s.call("Bash", {"command": f"cd {tmp_path / 'wt-t120'} && python3 -m pytest -q",
                    "description": "Run T120's tests in its worktree"})
    reason, stderr = s.stop()
    assert reason is None, reason
    assert [r["tool_name"] for r in trace(project, "T120")] == ["Bash"]
    assert trace(project, "T250") == []
    assert gate_sees_test_run(project, tmp_path, "T120")  # T120's other pause: close-out Gate 5


def test_ac2_t120_relative_cd_and_a_later_segment_are_found(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.request("start [auto]")
    s.point_at("T119")  # as at 10:53:57
    # (A `for …; do python3 -m pytest; done` loop is filed under T120 too, but the merge gate's own
    # `invokes_test_runner` does not count a `do` body as a test run: the gate's rule, unchanged.)
    s.call("Bash", {"command": "cd ../wt-t120 && python3 -m pytest -q 2>&1 | tail -3"})
    reason, _ = s.stop()
    assert reason is None, reason
    assert len(trace(project, "T120")) == 1 and trace(project, "T119") == []


def test_ac3_t120_without_a_test_run_still_pauses_with_todays_message(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.request("start [auto]")
    s.point_at("T250")
    s.call("Bash", {"command": f"cd {tmp_path / 'wt-t120'} && git status --short"})
    reason, _ = s.stop()
    assert reason and T120_PAUSE in reason, reason
    assert "then rerun the task's tests so the trace records them under the task" in reason


def test_ac4_another_sessions_test_run_for_another_task_is_not_credited(tmp_path):
    project = t120_project(tmp_path)
    other = Session(project, tmp_path, OTHER_SID)
    other.point_at("T121")
    other.call("Bash", {"command": f"cd {tmp_path / 'wt-t121'} && python3 -m pytest -q"})
    s = Session(project, tmp_path)
    s.request("start [auto]")
    s.point_at("T120")
    reason, _ = s.stop()
    assert reason and T120_PAUSE in reason, reason
    assert len(trace(project, "T121")) == 1


def test_ac4_a_test_run_in_another_tasks_worktree_is_not_credited_to_the_pointer(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.request("start [auto]")
    s.point_at("T120")
    s.call("Bash", {"command": f"cd {tmp_path / 'wt-t121'} && python3 -m pytest -q"})
    reason, _ = s.stop()
    assert reason and T120_PAUSE in reason, reason
    assert len(trace(project, "T121")) == 1


def test_ac4_a_command_in_two_tasks_worktrees_keeps_the_pointer(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": f"cd {tmp_path / 'wt-t121'} && git log -1; "
                               f"cd {tmp_path / 'wt-t120'} && python3 -m pytest -q"})
    assert len(trace(project, "T250")) == 1


# Stage 4 security P0 (E1-E4 and kin): a test run that did not run in the task's worktree, or did
# not run at all, is never filed under the task. Every simple command must run in that worktree.
@pytest.mark.parametrize("command", [
    "true # ; cd {wt} ; python3 -m pytest -q",                 # E1: pytest sits in a comment
    "cd {wt} && true # ; python3 -m pytest -q",                # E1 after the `cd`: only the comment guard
    "python3 -m pytest -q; cd {wt} && true",                   # E2: tests ran in the main checkout
    "cd /tmp && python3 -m pytest -q; cd {wt} && true",        # E3: tests ran in a non-worktree
    "(cd {wt}) ; python3 -m pytest -q",                        # E4: a subshell `cd` does not last
    "cd {wt} & python3 -m pytest -q",                          # a background `cd`
    "cd {wt} | true; python3 -m pytest -q",                    # a `cd` in a pipeline
    "pushd {wt} && python3 -m pytest -q",                      # pushd / popd: not followed
    "cd {wt} && python3 -m pytest -q &",                       # a trailing `&`
    "cd {wt} && echo $(python3 -m pytest -q)",                 # command substitution
], ids=["e1-comment", "e1-comment-after-cd", "e2-main-then-cd", "e3-tmp-then-cd", "e4-subshell", "background-cd",
        "piped-cd", "pushd", "trailing-amp", "substitution"])
def test_p0_a_test_run_outside_the_worktree_is_not_filed_under_the_task(tmp_path, command):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": command.format(wt=tmp_path / "wt-t120")})
    assert trace(project, "T120") == []
    assert len(trace(project, "T250")) == 1
    assert not gate_sees_test_run(project, tmp_path, "T120")


# Fix round 2 (independent security re-check, P0): slot 2b is an ALLOWLIST. A call is filed under a
# worktree's task only when the whole command is `cd <dir> && cmd [&& cmd]...` with `<dir>` an
# existing directory that is the worktree. Every shape below ran pytest in the MAIN checkout, or did
# not run it, and used to be filed under T120 (the merge gate then accepted T120). The ids are the
# reviewer's: B = bypass shapes, C = environment cases.
CD_W = "cd @WT@ && "
ROUND2_SHAPES = {
    "B03-cd-dash": CD_W + "cd - && python3 -m pytest -q",
    "B04-nonexistent-dir-semicolon": "cd @WT@/nope; python3 -m pytest -q",
    "B05-nonexistent-dir-or": "cd @WT@/nope || python3 -m pytest -q",
    "B28-target-is-a-file": "cd @WT@/setup.sh; python3 -m pytest -q",
    "B06-builtin-cd": CD_W + "builtin cd @MAIN@ && python3 -m pytest -q",
    "B07-command-cd": CD_W + "command cd @MAIN@ && python3 -m pytest -q",
    "B08-cdpath": CD_W + "CDPATH=@TMP@ cd repo && python3 -m pytest -q",
    "B09-eval": CD_W + 'eval "cd @MAIN@" && python3 -m pytest -q',
    "B10-brace-group": CD_W + "{ cd @MAIN@; } && python3 -m pytest -q",
    "B11-if": CD_W + "if cd @MAIN@; then :; fi; python3 -m pytest -q",
    "B12-while": CD_W + "while cd @MAIN@; do break; done; python3 -m pytest -q",
    "B13-bang": CD_W + "! cd @MAIN@; python3 -m pytest -q",
    "B24-time": CD_W + "time cd @MAIN@; python3 -m pytest -q",
    "B27-function": CD_W + "function f { cd @MAIN@; }; f; python3 -m pytest -q",
    "B14-quoted-heredoc-marker": CD_W + 'echo "<<EOF"\ncd @MAIN@\nEOF\npython3 -m pytest -q',
    "B19-pytest-inside-a-heredoc-body": CD_W + "cat <<EOF\npython3 -m pytest -q\nEOF",
    "B18-pytest-on-the-far-side-of-or": CD_W + "true || python3 -m pytest -q",
    "B16-runner-pointed-at-main": CD_W + "python3 -m pytest -q --rootdir @MAIN@ @MAIN@",
    "relative-dotdot-argument": CD_W + "python3 -m pytest -q ../repo/tests",
    "second-cd-in-a-nested-shell": CD_W + "bash -c 'cd @MAIN@ && python3 -m pytest -q'",
    "cd-with-an-expansion": "cd @WT@* && python3 -m pytest -q",
    "cd-with-a-variable": "cd $WT && python3 -m pytest -q",
    "cd-home": "cd ~ && python3 -m pytest -q",
    "cd-with-flag": "cd -P @WT@ && python3 -m pytest -q",
    "only-a-cd": "cd @WT@",
    "newline-after-cd": "cd @WT@\npython3 -m pytest -q",
    "semicolon-after-cd": "cd @WT@; python3 -m pytest -q",
    "env-assignment-before-the-runner": CD_W + "FOO=1 python3 -m pytest -q",
    "subshell-as-first-word": "(cd @WT@ && python3 -m pytest -q)",
    # code-review P1: `cd -` after a `;` runs pytest in the directory the call started in
    "review-P1-cd-dash-after-a-semicolon": CD_W + "git status; cd - && python3 -m pytest -q",
    "review-P2-pushd": CD_W + "pushd @MAIN@ && python3 -m pytest -q",
    "nonexistent-dir-and-and": "cd @WT@/nope && python3 -m pytest -q",
    "target-is-a-file-and-and": "cd @WT@/setup.sh && python3 -m pytest -q",
    "debate-python-c-chdir": CD_W + "python3 -c \"import os;os.chdir('/home');import pytest\"",
    "debate-python-c-no-path": CD_W + 'python3 -c "import pytest"',
    "debate-bash-lc": CD_W + "bash -lc 'python3 -m pytest -q'",
    "debate-node-e": CD_W + "node -e 'process.exit(0)'",
    "debate-perl-e": CD_W + "perl -e 'exit 0'",
    "debate-ruby-e": CD_W + "ruby -e 'exit 0'",
    "debate-quote-and-slash-without-c": CD_W + "python3 -m pytest -q \"os.chdir('/home')\"",
    # fix round 3: zsh's `chdir` is `cd`, so the COMMAND WORDS are an allowlist too
    "N01-chdir-dash": CD_W + "chdir - && python3 -m pytest -q",
    "N19-quoted-chdir": CD_W + "'chdir' - && python3 -m pytest -q",
    "N20-chdir-minus-one": CD_W + "chdir -1 && python3 -m pytest -q",
    "N20-chdir-plus-one": CD_W + "chdir +1 && python3 -m pytest -q",
    "N20-numeric-argument": CD_W + "ls -1 && python3 -m pytest -q",
    "N20-dash-argument": CD_W + "cat - && python3 -m pytest -q",
    "word-env": CD_W + "env python3 -m pytest -q",
    "word-make": CD_W + "make test",
    "word-xargs": CD_W + "echo x | xargs python3 -m pytest -q",
    "word-find": CD_W + "find . -name x -exec python3 -m pytest -q {} +",
    "word-bash": CD_W + "bash ./run-tests.sh",
    "word-sudo": CD_W + "sudo python3 -m pytest -q",
    "word-path-to-runner": CD_W + "./venv/bin/pytest -q",
    "word-after-a-pipe": CD_W + "python3 -m pytest -q | zsh",
    "word-after-timeout": CD_W + "timeout 5 env python3 -m pytest -q",
    "timeout-with-a-flag": CD_W + "timeout -k 5 30 python3 -m pytest -q",
    "python-m-other-module": CD_W + "python3 -m json.tool",
    "python-absolute-script": CD_W + "python3 /dev/null",
    "git-dash-C": CD_W + "git -C . status && python3 -m pytest -q",
    "git-work-tree": CD_W + "git --work-tree=. status && python3 -m pytest -q",
    "N14-argfile": CD_W + "python3 -m pytest -q @args.txt",
    "N26-non-ascii-space": CD_W + "python3 -m pytest -q a\u00a0b",
    "N26-zero-width": CD_W + "python3 -m pytest -q a\u200bb",
    "N26-control-char": CD_W + "python3 -m pytest -q a\x0bb",
    "variable-argument": CD_W + 'python3 -m pytest -q "$ARGS"',
    "backtick-argument": CD_W + "python3 -m pytest -q `echo ok`",
    "review-P2-popd": CD_W + "popd && python3 -m pytest -q",
}


def _expand(command, tmp_path, project):
    return (command.replace("@WT@", str(tmp_path / "wt-t120")).replace("@MAIN@", str(project))
            .replace("@TMP@", str(tmp_path)))


@pytest.mark.parametrize("name", list(ROUND2_SHAPES))
def test_round2_a_command_outside_the_allowlist_is_not_filed_under_the_task(tmp_path, name):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(ROUND2_SHAPES[name], tmp_path, project)})
    assert trace(project, "T120") == [], name
    assert len(trace(project, "T250")) == 1, name
    assert not gate_sees_test_run(project, tmp_path, "T120"), name


@pytest.mark.parametrize("command", ["cd @WT@ && python3 -m pytest -q", "cd @WT@; python3 -m pytest -q"],
                         ids=["and-and", "semicolon"])
def test_round2_c3_a_pruned_worktree_directory_is_not_filed_under_the_task(tmp_path, command):
    """C3: `git worktree list` still lists a worktree whose directory is gone (prunable). `cd` into
    it fails, so the runner would run in the event's directory."""
    project = t120_project(tmp_path)
    shutil.rmtree(tmp_path / "wt-t120")
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(command, tmp_path, project)})
    assert trace(project, "T120") == []
    assert len(trace(project, "T250")) == 1
    assert not gate_sees_test_run(project, tmp_path, "T120")


@pytest.mark.parametrize("command", ["python3 -m pytest -q; cd @WT@", "python3 -m pytest -q && cd @WT@"],
                         ids=["semicolon", "and-and"])
def test_round2_a_trailing_cd_is_not_filed_when_the_event_cwd_is_the_directory_after_it(
        tmp_path, command):
    """If the PostToolUse `cwd` is the directory AFTER the command ran, this call ran pytest in the
    main checkout and then moved: only a leading `cd <dir> &&` may name the directory."""
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(command, tmp_path, project)}, cwd=tmp_path / "wt-t120")
    assert trace(project, "T120") == []
    assert len(trace(project, "T250")) == 1
    assert not gate_sees_test_run(project, tmp_path, "T120")


def test_round2_a_command_with_no_cd_is_not_filed_by_the_event_cwd(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": "python3 -m pytest -q"}, cwd=tmp_path / "wt-t120")
    assert trace(project, "T120") == [] and len(trace(project, "T250")) == 1


def test_round2_cdpath_in_the_environment_blocks_a_bare_relative_cd(tmp_path):
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    env = dict(hook_env(project, tmp_path), CDPATH=str(tmp_path / "decoy"))
    s.call("Bash", {"command": "cd wt-t120 && python3 -m pytest -q"}, cwd=tmp_path, env=env)
    assert trace(project, "T120") == [] and len(trace(project, "T250")) == 1
    s.call("Bash", {"command": "cd wt-t120 && python3 -m pytest -q"}, cwd=tmp_path)  # no CDPATH
    assert len(trace(project, "T120")) == 1


def test_round2_a_dotdot_through_a_symlink_is_not_filed(tmp_path):
    """`cd <wt>/lnk/..` lands in <wt> by the logical path but in lnk's target's parent by the
    physical one (`set -P`, `cd -P`): the two disagree, so the slot says nothing."""
    project = t120_project(tmp_path)
    (tmp_path / "elsewhere" / "deep").mkdir(parents=True)
    (tmp_path / "wt-t120" / "lnk").symlink_to(tmp_path / "elsewhere" / "deep")
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": f"cd {tmp_path / 'wt-t120' / 'lnk'}/.. && python3 -m pytest -q"})
    assert trace(project, "T120") == [] and len(trace(project, "T250")) == 1


@pytest.mark.parametrize("command", [
    "cd @WT@ && python3 -m pytest -q m",                       # N02: `m` is a symlink to main
    "cd @WT@ && python3 -m pytest -q --rootdir=m m",           # N03
    "cd @WT@ && python3 -m pytest -q m/tests",                 # N04
    "cd @WT@ && cat m/setup.sh",                               # a read through the link
    "cd @WT@ && env PYTEST_ADDOPTS=--rootdir=m pytest",        # N24 (`env` is no allowed word either)
    "cd @WT@ && python3 m/setup.sh",                           # a script path through the link
], ids=["N02", "N03", "N04", "cat-through-link", "N24", "script-through-link"])
def test_round3_a_relative_path_through_a_symlink_to_main_is_not_filed(tmp_path, command):
    """The link lives inside the worktree and points to the main checkout: the argument is
    relative, so only its real path shows it leaves the worktree."""
    project = t120_project(tmp_path)
    (tmp_path / "wt-t120" / "m").symlink_to(project)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": _expand(command, tmp_path, project)})
    assert trace(project, "T120") == [] and len(trace(project, "T250")) == 1
    assert not gate_sees_test_run(project, tmp_path, "T120")


# The honest shapes stay filed under the task (they were green before the allowlist, and stay so).
def _symlinked(tmp_path, project):
    (tmp_path / "link-to-wt").symlink_to(tmp_path / "wt-t120")


def _spaced(tmp_path, project):
    _git(project, "worktree", "add", "-q", "-b", "fix/t122-spaced", str(tmp_path / "wt t122"))


def _nested(tmp_path, project):
    _git(project, "worktree", "add", "-q", "-b", "fix/t123-nested", str(project / "nested-wt"))


def _subdir(tmp_path, project):
    (tmp_path / "wt-t120" / "sub").mkdir()


HONEST_SHAPES = [
    ("H1-absolute", "cd @WT@ && python3 -m pytest -q", None, "T120", None),
    ("H2-several-and-and", "cd @WT@ && git status --short && python3 -m pytest -q -x", None, "T120", None),
    ("H3-pipe-after-the-runner", "cd @WT@ && python3 -m pytest -q 2>&1 | tail -3", None, "T120", None),
    ("H4-redirect", "cd @WT@ && python3 -m pytest -q > /dev/null 2>&1", None, "T120", None),
    ("H5-line-continuation", "cd @WT@ && python3 -m pytest \\\n  -q", None, "T120", None),
    ("C13-relative-dotdot", "cd ../wt-t120 && python3 -m pytest -q", "project", "T120", None),
    ("C13-relative-dot-slash", "cd ./wt-t120 && python3 -m pytest -q", "tmp", "T120", None),
    ("bare-relative-name", "cd wt-t120 && python3 -m pytest -q", "tmp", "T120", None),
    ("python-flag-then-module", "cd @WT@ && python3 -B -m pytest -q", None, "T120", None),
    ("unittest", "cd @WT@ && python3 -m unittest -q", None, "T120", None),
    ("python-relative-script", "cd @WT@ && python3 tests/run.py -q", None, "T120", None),
    ("pytest-and-py.test", "cd @WT@ && pytest -q && py.test -q", None, "T120", None),
    ("timeout-then-runner", "cd @WT@ && timeout 60 python3 -m pytest -q", None, "T120", None),
    ("git-and-reading-commands", "cd @WT@ && git log -1 && ls && cat setup.sh | head -1 | wc -l && grep v1 setup.sh && echo ok && true && python3 -m pytest -q", None, "T120", None),
    ("dot-argument", "cd @WT@ && python3 -m pytest .", None, "T120", None),
    ("absolute-path-inside-the-worktree", "cd @WT@ && python3 -m pytest -q @WT@/setup.sh", None, "T120", None),
    ("C1-path-with-spaces", 'cd "@TMP@/wt t122" && python3 -m pytest -q', None, "T122", _spaced),
    ("C4-symlink-to-the-worktree", "cd @TMP@/link-to-wt && python3 -m pytest -q", None, "T120", _symlinked),
    ("C11-worktree-nested-in-main", "cd @MAIN@/nested-wt && python3 -m pytest -q", None, "T123", _nested),
    ("subdirectory-target", "cd @WT@/sub && python3 -m pytest -q", None, "T120", _subdir),
]


@pytest.mark.parametrize("name", [h[0] for h in HONEST_SHAPES])
def test_round2_the_honest_shapes_are_still_filed_under_the_task(tmp_path, name):
    _, command, cwd_kind, task, setup = next(h for h in HONEST_SHAPES if h[0] == name)
    project = t120_project(tmp_path)
    if setup:
        setup(tmp_path, project)
    s = Session(project, tmp_path)
    s.point_at("T250")
    cwd = {"project": project, "tmp": tmp_path, None: project}[cwd_kind]
    s.call("Bash", {"command": _expand(command, tmp_path, project)}, cwd=cwd)
    assert len(trace(project, task)) == 1, name
    assert trace(project, "T250") == [], name


def test_p2_slot_2b_failing_falls_through_to_the_pointer(tmp_path):
    """E5: with no `git` on PATH slot 2b fails; the call is still filed by the session pointer."""
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": "cd /tmp && python3 -m pytest -q"},
           env=dict(hook_env(project, tmp_path), PATH="/nonexistent"))
    assert len(trace(project, "T250")) == 1 and trace(project, "_untagged") == []


def test_ac4_a_bound_sub_agent_keeps_its_spawn_binding_in_another_worktree(tmp_path):
    """Slot 2 (T196) stays first: a sub-agent spawned for T121 that runs tests in T120's worktree
    is still filed under T121."""
    project = t120_project(tmp_path)
    s = Session(project, tmp_path)
    sub = s.transcript.parent / SID / "subagents" / "agent-a1.jsonl"
    sub.parent.mkdir(parents=True)
    sub.write_text(json.dumps({"type": "user", "message": {"role": "user", "content":
                                                           "Task ID: T121\nGuide: x\n"}}) + "\n")
    event = {"session_id": SID, "agent_id": "a1", "transcript_path": str(s.transcript),
             "cwd": str(project), "tool_name": "Bash", "tool_input": {
                 "command": f"cd {tmp_path / 'wt-t120'} && python3 -m pytest -q"}}
    assert resolve_in(project, tmp_path, event, per_call=True) == "T121"


def test_ac4_a_directory_that_is_no_worktree_keeps_the_pointer(tmp_path):
    project = t120_project(tmp_path)
    scratch = tmp_path / "scratch-t120"  # named like the task, but not a worktree of this repo
    scratch.mkdir()
    s = Session(project, tmp_path)
    s.point_at("T250")
    s.call("Bash", {"command": f"cd {scratch} && python3 -m pytest -q"})
    s.call("Bash", {"command": "D=../wt-t120; cd $D && python3 -m pytest -q"})
    assert len(trace(project, "T250")) == 2
    assert trace(project, "T120") == []


# ── Cause C — T242: a Debate for the task while the session pointer still names the last one ──
T242_ROW = ("- [ ] **T242** — Plugin install ships only what it needs | Supervisor | C2 | "
            "Risk: Medium | P1")
T242_REPORT = """# TASK_REVIEW — T242: Plugin install ships only what it needs

## Auto decisions

Mode: auto
1. Layout: plugin/ holds symlinks to the kit dirs — DEBATED: symlinks (Advocate 1: symlink the kit dirs; Advocate 2: copy at release) ⚠ decided for you — please review
Checks: tests `python3 -m pytest -q` — 3 passed; reviews code-review — pass, security-review — no findings; real run ok (auto-checked, not /verify)
Memory: nothing new
Not done: merge (yours); auto verify: running (T182)

## Evidence

| Check | Result | Notes |
|---|---|---|
| verify | ☐ pass / ☐ fail / ☐ N/A | |
"""
T242_PAUSE = ("T242: 1 `DEBATED` line(s) need ≥2 Advocate `Agent` calls (description `Advocate <n>:` "
              "and a prompt starting `Using the repo, answer alone:`); the trace has 0")


def t242_project(tmp_path):
    return kit_project(tmp_path, [T242_ROW], {
        "tasks/TASK_GUIDE_T242.md": "# TASK_GUIDE — T242\n**Complexity Level**: C2\n"
                                    "**Risk Level**: Medium\n",
        "tasks/TASK_REVIEW_T242.md": T242_REPORT})


def t242_run(project, tmp_path, debate_task="T242", advocates=2, args=None):
    """The T242 shape: the Debate runs while the pointer still names T241; then the Supervisor
    points the session at T242 and runs the tests and both reviews."""
    s = Session(project, tmp_path)
    s.request("plan and run T242 [auto]", seconds_ago=900)
    s.point_at("T241")
    s.call("Skill", {"skill": "resolve-question",
                     "args": args or f"task={debate_task} risk=Medium"})
    for n in range(1, advocates + 1):
        s.call("Agent", advocate_input(n))
    s.point_at("T242")
    s.call("Write", {"file_path": str(project / "tasks" / "TASK_REVIEW_T242.md"), "content": "x"})
    s.call("Bash", {"command": "python3 -m pytest -q"})
    s.call("Skill", {"skill": "code-review", "args": "task=T242"})
    s.call("Skill", {"skill": "security-review"})
    return s


def test_ac2_t242_advocates_of_its_own_debate_are_found(tmp_path):
    project = t242_project(tmp_path)
    reason, stderr = t242_run(project, tmp_path).stop()
    assert reason is None, (reason, stderr)


def test_ac3_t242_without_advocate_calls_still_pauses_with_todays_message(tmp_path):
    project = t242_project(tmp_path)
    reason, _ = t242_run(project, tmp_path, advocates=0).stop()
    assert reason and T242_PAUSE in reason, reason


def test_ac3_t242_one_advocate_is_still_too_few(tmp_path):
    project = t242_project(tmp_path)
    reason, _ = t242_run(project, tmp_path, advocates=1).stop()
    assert reason and "the trace has 1" in reason, reason


def t242_reviewed(project, tmp_path):
    """T242 with its tests and reviews filed right, and no Debate yet."""
    s = Session(project, tmp_path)
    s.request("run T242 [auto]", seconds_ago=900)
    s.point_at("T242")
    s.call("Write", {"file_path": str(project / "tasks" / "TASK_REVIEW_T242.md"), "content": "x"})
    s.call("Bash", {"command": "python3 -m pytest -q"})
    s.call("Skill", {"skill": "code-review", "args": "task=T242"})
    s.call("Skill", {"skill": "security-review"})
    return s


def _transcript_debate(s, task_args="task=T242 risk=Medium", **extra):
    """A Debate written to the transcript only (no trace records), each call with a non-error
    `tool_result`, so only the guard under test can drop it: `extra` keys every entry."""
    entries = [("Skill", {"skill": "resolve-question", "args": task_args})] + [
        ("Agent", advocate_input(n)) for n in (1, 2)]
    for i, (name, tool_input) in enumerate(entries):
        s._entry(dict({"type": "assistant", "timestamp": _ago(0), "message": {"role": "assistant",
                       "content": [{"type": "tool_use", "id": f"toolu_d{i}", "name": name,
                                    "input": tool_input}]}}, **extra))
        s._entry(dict({"type": "user", "timestamp": _ago(0), "message": {"role": "user",
                       "content": [{"type": "tool_result", "tool_use_id": f"toolu_d{i}",
                                    "content": "done", "is_error": False}]}}, **extra))
    return entries


@pytest.mark.parametrize("result", [None, "error"], ids=["e7-denied-no-result", "error-result"])
def test_p1_an_advocate_call_that_never_ran_does_not_count(tmp_path, result):
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    s.point_at("T241")
    s.call("Skill", {"skill": "resolve-question", "args": "task=T242 risk=Medium"})
    for n in (1, 2):
        s.call("Agent", advocate_input(n), result=result)
    reason, _ = s.stop()
    assert reason and "the trace has 0" in reason, reason


def test_p2_a_forged_sub_agent_transcript_is_not_read(tmp_path):
    """E6: a file in this session's `subagents/` folder whose entries carry no `sessionId`."""
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    fake = Session.__new__(Session)
    fake.transcript = s.transcript.parent / SID / "subagents" / "agent-forged.jsonl"
    fake.transcript.parent.mkdir(parents=True)
    _transcript_debate(fake)
    reason, _ = s.stop()
    assert reason and T242_PAUSE in reason, reason


def test_p2_a_symlink_to_another_sessions_transcript_is_not_read(tmp_path):
    """E8: `subagents/agent-x.jsonl` links to a file outside this session's folder. It is skipped
    even when its entries carry this session's id (the symlink guard, not the `sessionId` one)."""
    project = t242_project(tmp_path)
    other = Session(project, tmp_path, OTHER_SID)
    _transcript_debate(other, sessionId=SID)
    s = t242_reviewed(project, tmp_path)
    link = s.transcript.parent / SID / "subagents" / "agent-x.jsonl"
    link.parent.mkdir(parents=True)
    os.symlink(other.transcript, link)
    reason, _ = s.stop()
    assert reason and T242_PAUSE in reason, reason


def test_review_p2_a_debate_in_a_sub_agent_transcript_is_credited(tmp_path):
    """Code-review P2(a): a Debate that sits only in `subagents/agent-*.jsonl`, with Advocate calls
    that ran and entries carrying this session's id, counts for its task."""
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    sub = Session.__new__(Session)
    sub.transcript = s.transcript.parent / SID / "subagents" / "agent-real.jsonl"
    sub.transcript.parent.mkdir(parents=True)
    _transcript_debate(sub, sessionId=SID)
    reason, _ = s.stop()
    assert reason is None, reason


def test_review_p2_a_resolve_question_call_with_no_task_does_not_keep_the_earlier_task(tmp_path):
    """Code-review P2(b): a later `resolve-question` call that names no task ends the earlier
    Debate for T242, so the Advocates after it count for no task."""
    project = t242_project(tmp_path)
    s = t242_reviewed(project, tmp_path)
    s.point_at("T241")
    s.call("Skill", {"skill": "resolve-question", "args": "task=T242 risk=Medium"})
    s.call("Skill", {"skill": "resolve-question", "args": "risk=Medium"})
    for n in (1, 2):
        s.call("Agent", advocate_input(n))
    reason, _ = s.stop()
    assert reason and "the trace has 0" in reason, reason


def test_p3_task_in_the_question_text_does_not_name_the_debate(tmp_path):
    """E9: only a whole top-level `task=` token names the Debate, and the last one wins."""
    project = t242_project(tmp_path)
    reason, _ = t242_run(project, tmp_path,
                         args="question='why task=T242 failed' task=T241 risk=Medium").stop()
    assert reason and T242_PAUSE in reason, reason
    project2 = t242_project(tmp_path / "b")
    reason, _ = t242_run(project2, tmp_path / "b",
                         args="task=T241 question='x' task=T242 risk=Medium").stop()
    assert reason is None, reason


def test_ac3_an_advocate_filed_right_is_not_counted_twice(tmp_path):
    """With the pointer on T242, its one Advocate is both in `T242.jsonl` and in the transcript:
    it counts once, so one Advocate is still too few."""
    project = t242_project(tmp_path)
    s = Session(project, tmp_path)
    s.request("run T242 [auto]")
    s.point_at("T242")
    s.call("Skill", {"skill": "resolve-question", "args": "task=T242 risk=Medium"})
    s.call("Agent", advocate_input(1))
    s.call("Write", {"file_path": str(project / "tasks" / "TASK_REVIEW_T242.md"), "content": "x"})
    s.call("Bash", {"command": "python3 -m pytest -q"})
    s.call("Skill", {"skill": "code-review", "args": "task=T242"})
    s.call("Skill", {"skill": "security-review"})
    reason, _ = s.stop()
    assert reason and "the trace has 1" in reason, reason


def test_ac3_an_unreadable_transcript_counts_no_session_advocates(tmp_path):
    """Fail closed: when the session's transcript cannot be read, its Debates count nothing and
    the task is paused as before T287."""
    project = t242_project(tmp_path)
    s = t242_run(project, tmp_path)
    s.transcript.chmod(0)
    try:
        if os.access(s.transcript, os.R_OK):
            import pytest
            pytest.skip("running as a user that reads mode-0 files")
        reason, _ = s.stop()
        assert reason and T242_PAUSE in reason, reason
    finally:
        s.transcript.chmod(0o600)


def test_ac4_advocates_of_a_debate_for_another_task_are_not_credited(tmp_path):
    project = t242_project(tmp_path)
    reason, _ = t242_run(project, tmp_path, debate_task="T241").stop()
    assert reason and T242_PAUSE in reason, reason


def test_ac4_another_sessions_debate_is_not_credited(tmp_path):
    project = t242_project(tmp_path)
    other = Session(project, tmp_path, OTHER_SID)
    other.point_at("T241")
    other.call("Skill", {"skill": "resolve-question", "args": "task=T242 risk=Medium"})
    for n in (1, 2):
        other.call("Agent", advocate_input(n))
    assert len(trace(project, "T241")) == 3  # the other session's Debate, filed by its pointer
    reason, _ = t242_run(project, tmp_path, advocates=0).stop()
    assert reason and T242_PAUSE in reason, reason


# ── AC 5 — the stops that stay ────────────────────────────────────────────────────────────────
STOPS_THAT_STAY = (
    "- a safety-hook block;",
    "- an action that deletes or overwrites data with no backup;",
    "- the 4th Debate in a task (the `resolve-question` cap);",
    "- a paid action outside the task's own work;",
    "- a login or secret the Supervisor does not have;",
    "- the same sub-agent hitting the step limit twice.",
)


def test_ac5_the_text_of_the_stops_that_stay_is_unchanged():
    """Pins the bullets of `### Stops that stay` only. It does not run a stop: the hook behaviour of
    the stops is covered by the ac5 tests that drive the real hooks."""
    text = (ROOT / "docs" / "claude-md" / "tracks.md").read_text(encoding="utf-8")
    section = text.split("\n### Stops that stay\n", 1)[1].split("\n### ", 1)[0]
    bullets = tuple(l for l in section.splitlines() if l.startswith("- "))
    assert bullets == STOPS_THAT_STAY


def _tracks_section(heading):
    text = (ROOT / "docs" / "claude-md" / "tracks.md").read_text(encoding="utf-8")
    return " ".join(text.split(f"\n### {heading}\n", 1)[1].split("\n### ", 1)[0].split())


def test_ac6_tracks_md_states_the_new_attribution():
    check = _tracks_section("Auto-mode check (Stop hook)")
    assert ("the trace hook files a `Bash` call that runs in a task's worktree under that task, "
            "before the session's active-task file") in check, check
    assert "only for the exact form `cd <dir> && cmd [&& cmd]...`" in check, check
    assert "Any other form is not filed by its directory" in check, check
    assert "A call with no `cd` is not filed by the session's directory." in check, check
    assert "an inline-code flag (`-c`, `-e`, `-lc`)" in check, check
    assert ("made after a `resolve-question` Skill call whose last top-level `task=<ID>` names the "
            "task, wherever the trace filed them. Only a call that ran counts") in check, check
    assert "it skips symlinks and entries with another session's id." in check, check
    limits = _tracks_section("Known limits")
    assert "The Stop check finds misfiled work by two signals only (T287)." in limits, limits
    assert "Other work filed under another task is still not found." in limits, limits
    assert "(C9)" in limits and "invokes_test_runner" in limits, limits
    assert "The filing proves where the command started, not what it ran." in limits, limits


def resolve_in(project, tmp_path, event, **kwargs):
    code = ("import json, sys; sys.path.insert(0, '.claude/hooks/lib'); "
            "from task_context import resolve_task_id; "
            f"print(resolve_task_id(json.loads(sys.argv[1]), **{kwargs!r}))")
    done = subprocess.run([sys.executable, "-c", code, json.dumps(event)], capture_output=True,
                          text=True, cwd=project, env=hook_env(project, tmp_path), timeout=60)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def test_ac5_the_safety_hook_and_the_step_limit_still_resolve_by_the_pointer(tmp_path):
    """`pre_tool_sensitive_path.py` and `pre_agent_step_limit.py` call `resolve_task_id(event)`: the
    new per-call signals reach only the trace hook, so these two stops see the task they saw."""
    project = t120_project(tmp_path)
    Session(project, tmp_path).point_at("T250")
    event = {"session_id": SID, "cwd": str(project), "tool_name": "Bash",
             "tool_input": {"command": f"cd {tmp_path / 'wt-t120'} && python3 -m pytest -q"}}
    assert resolve_in(project, tmp_path, event) == "T250"
    assert resolve_in(project, tmp_path, event, per_call=True) == "T120"
    for name in ("pre_tool_sensitive_path.py", "pre_agent_step_limit.py"):
        source = (project / ".claude" / "hooks" / name).read_text(encoding="utf-8")
        assert "resolve_task_id(event)" in source and "per_call" not in source, name


def test_ac5_the_step_limit_still_blocks_the_call_over_its_limit(tmp_path):
    project = t120_project(tmp_path)
    Session(project, tmp_path).point_at("T120")
    event = {"session_id": SID, "cwd": str(project), "tool_name": "Bash", "hook_event_name":
             "PreToolUse", "tool_input": {"command": f"cd {tmp_path / 'wt-t120'} && ls"}}
    env = dict(hook_env(project, tmp_path), CLAUDE_STEP_LIMIT="1")
    outs = []
    for _ in range(2):
        done = subprocess.run([sys.executable, str(project / ".claude" / "hooks" /
                                                   "pre_agent_step_limit.py")],
                              input=json.dumps(event), capture_output=True, text=True,
                              cwd=project, env=env, timeout=60)
        outs.append(done.stdout + done.stderr)
    assert "T120" not in outs[0] or "block" not in outs[0].lower(), outs[0]
    assert "T120" in outs[1] and "block" in outs[1].lower(), outs[1]
