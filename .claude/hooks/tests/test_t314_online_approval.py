#!/usr/bin/env python3
"""T314 locked oracle — in board mode `online`, a sensitive path is approved once per task.

Written by qa-expert BEFORE the implementation (Pillar 3). The implementer may not edit it.

Every case drives the hooks through their real protocol: a JSON payload on stdin, the
decision (or silence) read back from stdout. Each test builds its own project in a temp dir
(`CLAUDE_PROJECT_DIR`), so nothing reads the live board, `tasks/` or state. The task id comes
from `CLAUDE_ACTIVE_TASK` only: the events carry no `session_id` and no `agent_id`, so the
state-file and spawn-binding slots of `resolve_task_id` stay silent.

The flow under test (TASK_GUIDE_T314 "Design decision"): the PreToolUse hook asks; the user
says yes; the call runs; the PostToolUse recorder writes (task, normalised path) to the
approval file; the next PreToolUse call in the same task that touches only approved paths
prints nothing.

The two names the implementer must use are pinned in RECORDER_NAME and APPROVALS_RELPATH.

Run with:
    python3 -m pytest .claude/hooks/tests/test_t314_online_approval.py -q -p no:cacheprovider
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

# --- Pinned names (the implementer's file names must match these) -----------------------
RECORDER_NAME = "post_tool_sensitive_approval.py"
APPROVALS_RELPATH = ".claude/state/sensitive-approvals.json"
# AC1: the one sentence the `ask` reason adds in online mode. Matched case-insensitively.
APPROVE_ONCE_PHRASE = "will not ask again"
# Decision 4: approvals are Edit/Write-only; the Bash ask says so. Matched case-insensitively.
EDIT_OR_WRITE_PHRASE = "edit or write"

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE_HOOK = os.path.join(HOOKS_DIR, "pre_tool_sensitive_path.py")
RECORDER = os.path.join(HOOKS_DIR, RECORDER_NAME)
REPO_ROOT = os.path.dirname(os.path.dirname(HOOKS_DIR))
SHIPPED_PATTERNS = os.path.join(REPO_ROOT, ".claude", "sensitive-paths.txt")
SETTINGS = os.path.join(REPO_ROOT, ".claude", "settings.json")

SECRET = "tests/fixtures/secrets/x.json"
SECRET_2 = "tests/fixtures/secrets/y.json"
TASK = "T314"
OTHER_TASK = "T315"

ONLINE_BOARD = {"board": "fake", "fake_board": "board.json", "id_pattern": r"ENG-\d+"}

PREDICTING_GUIDE = f"""# TASK_GUIDE — {TASK}: fixture

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `{SECRET}` | edit |

## Files Must NOT Touch
"""


def _env(project, task_id):
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_ACTIVE_TASK", "CLAUDE_PROJECT_DIR")}
    env["CLAUDE_PROJECT_DIR"] = project
    if task_id:
        env["CLAUDE_ACTIVE_TASK"] = task_id
    return env


def run_script(script, project, task_id, payload=None, raw_stdin=None):
    stdin = raw_stdin if raw_stdin is not None else json.dumps(payload)
    return subprocess.run([sys.executable, script], input=stdin, capture_output=True,
                          text=isinstance(stdin, str), env=_env(project, task_id),
                          cwd=project, timeout=20)


def decision(proc):
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)["hookSpecificOutput"]


class OnlineApprovalTest(unittest.TestCase):
    online = True

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix="t314-")
        self.addCleanup(shutil.rmtree, self.project, True)
        os.makedirs(os.path.join(self.project, ".claude"))
        os.makedirs(os.path.join(self.project, "tasks"))
        os.makedirs(os.path.join(self.project, "tests", "fixtures", "secrets"))
        shutil.copy(SHIPPED_PATTERNS, os.path.join(self.project, ".claude", "sensitive-paths.txt"))
        with open(os.path.join(self.project, "PROJECT_KANBAN.md"), "w") as f:
            f.write("### Todo\n")  # T232: a kit project, or the hooks stand down
        if self.online:
            with open(os.path.join(self.project, ".claude", "board.json"), "w") as f:
                json.dump(ONLINE_BOARD, f)
        self.approvals = os.path.join(self.project, *APPROVALS_RELPATH.split("/"))

    # --- events -------------------------------------------------------------------------

    def _event(self, tool_name, tool_input, post=False, tool_use_id=None):
        # Fix round (guide decision 2, F1/F2): real events carry tool_use_id and permission_mode.
        event = {"tool_name": tool_name, "cwd": self.project, "tool_input": tool_input,
                 "tool_use_id": tool_use_id or "toolu_" + uuid.uuid4().hex,
                 "permission_mode": "default"}
        if post:
            event["hook_event_name"] = "PostToolUse"
            event["tool_response"] = ({"stdout": "", "stderr": "", "interrupted": False}
                                      if tool_name == "Bash" else {"success": True})
        else:
            event["hook_event_name"] = "PreToolUse"
        return event

    @staticmethod
    def _input(tool_name, target):
        if tool_name == "Bash":
            return {"command": target}
        if tool_name == "Write":
            return {"file_path": target, "content": "{}"}
        return {"file_path": target, "old_string": "a", "new_string": "b"}

    def pre(self, tool_name, target, task_id=TASK):
        return run_script(PRE_HOOK, self.project, task_id,
                          self._event(tool_name, self._input(tool_name, target)))

    def record(self, tool_name, target, task_id=TASK):
        self.assertTrue(os.path.exists(RECORDER),
                        f"recorder missing: {RECORDER_NAME} does not exist in .claude/hooks/")
        # Fix round (F1): Post records only what Pre asked, so the same call runs Pre first.
        tool_use_id = "toolu_" + uuid.uuid4().hex
        run_script(PRE_HOOK, self.project, task_id,
                   self._event(tool_name, self._input(tool_name, target), tool_use_id=tool_use_id))
        proc = run_script(RECORDER, self.project, task_id,
                          self._event(tool_name, self._input(tool_name, target), post=True,
                                      tool_use_id=tool_use_id))
        self.assert_silent(proc)
        return proc

    def record_raw(self, raw_stdin, task_id=TASK, recorder=RECORDER):
        self.assertTrue(os.path.exists(recorder),
                        f"recorder missing: {RECORDER_NAME} does not exist in .claude/hooks/")
        return run_script(recorder, self.project, task_id, raw_stdin=raw_stdin)

    # --- approval file ------------------------------------------------------------------

    def approvals_data(self):
        self.assertTrue(os.path.exists(self.approvals),
                        f"approval file not written at {APPROVALS_RELPATH}")
        with open(self.approvals, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict, "approval file must be a JSON object")
        for key, value in data.items():
            self.assertIsInstance(value, list, f"approvals for {key} must be a list")
        return data

    def seed(self, content):
        os.makedirs(os.path.dirname(self.approvals), exist_ok=True)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(self.approvals, mode) as f:
            f.write(content if isinstance(content, (bytes, str)) else json.dumps(content))

    # --- assertions ---------------------------------------------------------------------

    def assert_ask(self, proc, *needles, absent=()):
        out = decision(proc)
        self.assertIsNotNone(out, f"expected ask, got silence; stderr={proc.stderr!r}")
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "ask")
        reason = out["permissionDecisionReason"]
        for needle in needles:
            self.assertIn(needle, reason)
        for needle in absent:
            self.assertNotIn(needle, reason)
        self.assertEqual(proc.returncode, 0)
        return reason

    def assert_silent(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "", f"expected no output, got {proc.stdout!r}")


class SC1FirstCallAsks(OnlineApprovalTest):
    """SC1 / AC1: no approval yet -> ask, naming the path and the approve-once sentence."""

    def test_sc1_unapproved_bash_call_asks_with_approve_once_sentence(self):
        reason = self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.assertIn(APPROVE_ONCE_PHRASE, reason.lower(),
                      "AC1: online ask must say later calls touching only this path will not ask again")

    def test_sc1_unapproved_write_and_edit_ask_too(self):
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                reason = self.assert_ask(self.pre(tool, SECRET), SECRET)
                self.assertIn(APPROVE_ONCE_PHRASE, reason.lower())

    def test_sc1_pre_hook_alone_writes_no_approval(self):
        # Only the recorder (PostToolUse = the user said yes) may create approvals.
        self.pre("Bash", f"cat {SECRET}")
        self.assertFalse(os.path.exists(self.approvals),
                         "the PreToolUse hook must not record an approval on its own ask")


class SC2RecordThenSilent(OnlineApprovalTest):
    """SC2 / AC2 / AC3: recorder stores (T, P); the next call in T is silent, never `allow`."""

    def test_sc2_bash_is_not_recorded_and_asks_again(self):
        # Decision 4: the recorder records nothing from a Bash event.
        self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.record("Bash", f"cat {SECRET}")
        if os.path.exists(self.approvals):
            self.assertNotIn(SECRET, self.approvals_data().get(TASK, []))
        reason = self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.assertIn(EDIT_OR_WRITE_PHRASE, reason.lower())

    def test_sc2_write_recorded_then_second_write_is_silent(self):
        self.assert_ask(self.pre("Write", SECRET), SECRET)
        self.record("Write", SECRET)
        self.assertIn(SECRET, self.approvals_data().get(TASK, []))
        self.assert_silent(self.pre("Write", SECRET))

    def test_sc2_approval_covers_every_tool_and_path_form(self):
        # Same normalised path whether given relative, absolute or `./`-prefixed.
        self.record("Write", os.path.join(self.project, SECRET))
        self.assertIn(SECRET, self.approvals_data().get(TASK, []),
                      "an absolute path is stored in its project-relative normalised form")
        self.assert_silent(self.pre("Edit", SECRET))
        self.assert_silent(self.pre("Write", "./" + SECRET))
        # Decision 4: Bash always asks, even on an Edit/Write-approved file.
        reason = self.assert_ask(self.pre("Bash", f"sed -i s/a/b/ {SECRET}"), SECRET)
        self.assertIn(EDIT_OR_WRITE_PHRASE, reason.lower())

    def test_sc2_edit_is_recorded(self):
        self.record("Edit", SECRET)
        self.assertIn(SECRET, self.approvals_data().get(TASK, []))

    def test_sc2_bash_call_with_two_sensitive_paths_records_nothing(self):
        self.record("Bash", f"cp {SECRET} {SECRET_2}")
        if os.path.exists(self.approvals):
            approved = self.approvals_data().get(TASK, [])
            self.assertNotIn(SECRET, approved)
            self.assertNotIn(SECRET_2, approved)
        self.assert_ask(self.pre("Bash", f"diff {SECRET} {SECRET_2}"), SECRET, SECRET_2)

    def test_sc2_recording_twice_keeps_one_entry(self):
        self.record("Write", SECRET)
        self.record("Edit", SECRET)
        self.assertEqual(self.approvals_data()[TASK].count(SECRET), 1)

    def test_ac2_records_only_sensitive_paths(self):
        for target in ("README.md", "src/app.py", SECRET):
            self.record("Write", target)
        approved = self.approvals_data().get(TASK, [])
        self.assertIn(SECRET, approved)
        for ordinary in ("README.md", "src/app.py", "cp"):
            self.assertNotIn(ordinary, approved)

    def test_ac2_non_sensitive_call_records_nothing(self):
        self.record("Write", "src/app.py")
        if os.path.exists(self.approvals):
            self.assertEqual(self.approvals_data().get(TASK, []), [])

    def test_ac2_recorder_uses_the_pre_hook_bash_parsing(self):
        # Quoted data and heredoc bodies are not paths (shell_data), for the recorder too:
        # mentioning `.env` in data must not approve `.env`.
        self.record("Bash", 'echo "edit .env later"')
        self.record("Bash", "cat <<EOF > notes.md\nremember .env\nEOF")
        if os.path.exists(self.approvals):
            self.assertNotIn(".env", self.approvals_data().get(TASK, []))
        self.assert_ask(self.pre("Write", ".env"), ".env")

    def test_ac2_recorder_shares_code_with_the_pre_hook(self):
        self.assertTrue(os.path.exists(RECORDER), f"recorder missing: {RECORDER_NAME}")
        with open(RECORDER, encoding="utf-8") as f:
            source = f.read()
        for helper in ("path_forms", "matching_pattern", "command_tokens", "glob_to_regex",
                       "parse_patterns", "candidate_paths"):
            self.assertIsNone(re.search(rf"^\s*def {helper}\b", source, re.M),
                              f"AC2: {helper} must be shared code, not a copy in the recorder")

    def test_ac2_recorder_is_wired_on_post_tool_use(self):
        with open(SETTINGS, encoding="utf-8") as f:
            post = json.load(f)["hooks"]["PostToolUse"]
        ours = [g for g in post if any(RECORDER_NAME in h.get("command", "") for h in g["hooks"])]
        self.assertEqual(len(ours), 1, f"{RECORDER_NAME} must be wired once under PostToolUse")
        # Decision 4: Bash records nothing, so `Bash` in the matcher is optional.
        matcher = set(ours[0]["matcher"].split("|"))
        self.assertTrue({"Edit", "Write"} <= matcher <= {"Edit", "Write", "Bash"}, matcher)

    def test_ac3_silence_is_no_decision_not_allow(self):
        self.record("Write", SECRET)
        proc = self.pre("Edit", SECRET)
        self.assert_silent(proc)
        self.assertNotIn("allow", proc.stdout)

    def test_ac3_seeded_approval_file_is_read(self):
        # The read path, independent of the recorder: a well-formed file exempts the path.
        self.seed({TASK: [SECRET]})
        self.assert_silent(self.pre("Write", SECRET))
        self.assert_silent(self.pre("Edit", SECRET))
        self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)  # decision 4


class SC3PerPath(OnlineApprovalTest):
    """SC3 / AC4: approved path + unapproved sensitive path -> ask naming only the unapproved one."""

    def test_sc3_mixed_call_asks_naming_env(self):
        # Decision 4: a Bash call asks for every sensitive path, as on `main`.
        self.record("Write", SECRET)
        self.assert_ask(self.pre("Bash", f"cp {SECRET} .env"), ".env")

    def test_sc3_approval_is_exact_path_not_directory(self):
        self.record("Write", SECRET)
        self.assert_ask(self.pre("Edit", SECRET_2), SECRET_2)


class SC4PerTask(OnlineApprovalTest):
    """SC4 / AC5: an approval for T never exempts task U, nor a call with no active task."""

    def test_sc4_other_task_asks(self):
        self.record("Write", SECRET)
        self.assertIn(SECRET, self.approvals_data().get(TASK, []))
        self.assert_ask(self.pre("Write", SECRET, task_id=OTHER_TASK), SECRET)

    def test_sc4_no_active_task_asks(self):
        self.record("Write", SECRET)
        self.assertIn(SECRET, self.approvals_data().get(TASK, []))
        self.assert_ask(self.pre("Write", SECRET, task_id=None), SECRET)

    def test_sc4_recorder_with_no_active_task_records_nothing(self):
        self.record("Write", SECRET, task_id=None)
        if os.path.exists(self.approvals):
            data = self.approvals_data()
            self.assertEqual([p for paths in data.values() for p in paths], [],
                             f"no task -> no approval under any key, got {data!r}")
        self.assert_ask(self.pre("Write", SECRET, task_id=None), SECRET)


class SC5ApprovalFileProtected(OnlineApprovalTest):
    """SC5 / AC6: the approval file is gitignored and is itself a sensitive path."""

    def test_sc5_write_edit_bash_on_approval_file_ask(self):
        self.assert_ask(self.pre("Write", APPROVALS_RELPATH), APPROVALS_RELPATH)
        self.assert_ask(self.pre("Edit", APPROVALS_RELPATH), APPROVALS_RELPATH)
        self.assert_ask(self.pre("Bash", f"echo x > {APPROVALS_RELPATH}"), APPROVALS_RELPATH)

    def test_sc5_absolute_path_to_approval_file_asks(self):
        self.assert_ask(self.pre("Write", self.approvals))

    def test_sc5_approval_file_cannot_approve_itself(self):
        # A forged (or once-approved) entry for the approval file must never exempt it.
        self.seed({TASK: [APPROVALS_RELPATH]})
        self.assert_ask(self.pre("Write", APPROVALS_RELPATH), APPROVALS_RELPATH)

    def test_sc5_approval_file_is_gitignored_and_untracked(self):
        ignored = subprocess.run(["git", "check-ignore", "-q", APPROVALS_RELPATH],
                                 cwd=REPO_ROOT, capture_output=True, timeout=20)
        self.assertEqual(ignored.returncode, 0, f"{APPROVALS_RELPATH} is not gitignored")
        tracked = subprocess.run(["git", "ls-files", "--", APPROVALS_RELPATH],
                                 cwd=REPO_ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(tracked.stdout.strip(), "")


class SC6FailTowardTheHuman(OnlineApprovalTest):
    """SC6 / AC7: a bad approval file counts as empty; the recorder never breaks the session."""

    BAD_FILES = {
        "list": "[]",
        "broken json": "{bad",
        "binary": b"\x00\xff\xfe\x89PNG\r\n\x1a\n\x00",
        "value not a list": json.dumps({TASK: SECRET}),
        "list of non-strings": json.dumps({TASK: [1, None, {"p": SECRET}]}),
        "empty file": "",
    }

    def test_sc6_bad_approval_file_asks(self):
        for label, content in self.BAD_FILES.items():
            with self.subTest(file=label):
                self.seed(content)
                self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc6_unreadable_approval_file_asks(self):
        self.seed({TASK: [SECRET]})
        os.chmod(self.approvals, 0)
        self.addCleanup(os.chmod, self.approvals, 0o600)
        if os.access(self.approvals, os.R_OK):
            self.skipTest("running as root: chmod 0 does not block reads")
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc6_approval_path_is_a_directory_asks(self):
        os.makedirs(self.approvals)
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc6_recorder_bad_stdin_exits_0_silently(self):
        for raw in ("not json{", "", "[]", "null", '{"tool_name": "Bash"}',
                    '{"tool_name": "Bash", "tool_input": "x"}',
                    '{"tool_name": "Write", "tool_input": {}}'):
            with self.subTest(stdin=raw):
                self.assert_silent(self.record_raw(raw))

    def test_sc6_recorder_with_bad_approval_file_exits_0_silently(self):
        for label, content in self.BAD_FILES.items():
            with self.subTest(file=label):
                self.seed(content)
                self.record("Write", SECRET)

    def test_sc6_recorder_unwritable_state_exits_0_silently(self):
        # `.claude/state` is a plain file, so the approval file cannot be created.
        with open(os.path.join(self.project, ".claude", "state"), "w") as f:
            f.write("not a dir")
        self.record("Write", SECRET)
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc6_recorder_import_failure_exits_0_silently(self):
        self.assertTrue(os.path.exists(RECORDER), f"recorder missing: {RECORDER_NAME}")
        sandbox = tempfile.mkdtemp(prefix="t314-noimport-")
        self.addCleanup(shutil.rmtree, sandbox, True)
        copy = os.path.join(sandbox, RECORDER_NAME)
        shutil.copy(RECORDER, copy)  # no lib/ and no pre hook beside it
        event = self._event("Write", {"file_path": SECRET, "content": "{}"}, post=True)
        self.assert_silent(self.record_raw(json.dumps(event), recorder=copy))


class SC7LocalModeUnchanged(OnlineApprovalTest):
    """SC7 / AC8: local board mode neither reads nor writes the approval file."""

    online = False

    def test_sc7_local_unpredicted_asks_and_recorder_writes_nothing(self):
        reason = self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET, TASK)
        self.assertNotIn(APPROVE_ONCE_PHRASE, reason.lower(),
                         "the approve-once sentence is for online mode only")
        self.record("Write", SECRET)
        self.assertFalse(os.path.exists(self.approvals),
                         "local mode: the recorder must not create the approval file")
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc7_local_mode_ignores_a_seeded_approval_file(self):
        self.seed({TASK: [SECRET]})
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_sc7_local_predicted_path_stays_silent_and_records_nothing(self):
        with open(os.path.join(self.project, "tasks", f"TASK_GUIDE_{TASK}.md"), "w") as f:
            f.write(PREDICTING_GUIDE)
        self.assert_silent(self.pre("Edit", SECRET))
        self.record("Edit", SECRET)
        self.assertFalse(os.path.exists(self.approvals))

    def test_sc7_online_predicted_guide_still_asks_nfr005(self):
        # NFR-005 kept: in online mode the guide's prediction exempts nothing; only approval does.
        with open(os.path.join(self.project, "tasks", f"TASK_GUIDE_{TASK}.md"), "w") as f:
            f.write(PREDICTING_GUIDE)
        with open(os.path.join(self.project, ".claude", "board.json"), "w") as f:
            json.dump(ONLINE_BOARD, f)
        self.assert_ask(self.pre("Edit", SECRET), SECRET)


if __name__ == "__main__":
    unittest.main()
