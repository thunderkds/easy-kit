#!/usr/bin/env python3
"""T314 Stage 4 fix-round locked oracle (F1-F6, TASK_GUIDE_T314 "Supervisor decisions", decision 2).

Written by qa-expert BEFORE the fix (Pillar 3). The implementer may not edit it.

Same style as `test_t314_online_approval.py`: every case drives the real hooks through their
protocol (JSON on stdin, decision or silence on stdout), in a temp project
(`CLAUDE_PROJECT_DIR`), task id from `CLAUDE_ACTIVE_TASK` only.

The fixed flow under test:
  PreToolUse asks (online, task T) -> writes `.claude/state/pending/<tool_use_id>.json`
  = {"task_id": T, "keys": [...]} -> the user says yes -> PostToolUse with the same
  `tool_use_id` and `permission_mode` `default` or `auto` promotes exactly those keys under
  T and deletes the pending entry. No pending entry, or any other permission mode -> nothing.

Run with:
    python3 -m pytest .claude/hooks/tests/test_t314_fix_round.py -q -p no:cacheprovider
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

# --- Pinned names -------------------------------------------------------------------------
RECORDER_NAME = "post_tool_sensitive_approval.py"
APPROVALS_RELPATH = ".claude/state/sensitive-approvals.json"
PENDING_RELDIR = ".claude/state/pending"
STATE_RELDIR = ".claude/state"
# Decision 4 (replaces F5's "including writes and deletes" sentence): approvals are
# Edit/Write-only, and the Bash ask says a later Edit or Write will not ask again.
EDIT_OR_WRITE_PHRASE = "edit or write"
RECORDING_MODES = ("default", "auto")
NON_RECORDING_MODES = ("bypassPermissions", "acceptEdits", "plan", "dontAsk", None, "yolo")
MISSING = None  # permission_mode=None -> the field is left out of the event

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE_HOOK = os.path.join(HOOKS_DIR, "pre_tool_sensitive_path.py")
RECORDER = os.path.join(HOOKS_DIR, RECORDER_NAME)
REPO_ROOT = os.path.dirname(os.path.dirname(HOOKS_DIR))
SHIPPED_PATTERNS = os.path.join(REPO_ROOT, ".claude", "sensitive-paths.txt")
SITE_DOCS = os.path.join(REPO_ROOT, "site", "docs.html")

SECRET = "tests/fixtures/secrets/x.json"
SECRET_2 = "tests/fixtures/secrets/y.json"
TASK = "T314"
OTHER_TASK = "T315"

ONLINE_BOARD = {"board": "fake", "fake_board": "board.json", "id_pattern": r"ENG-\d+"}


def _env(project, task_id):
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_ACTIVE_TASK", "CLAUDE_PROJECT_DIR")}
    env["CLAUDE_PROJECT_DIR"] = project
    if task_id:
        env["CLAUDE_ACTIVE_TASK"] = task_id
    return env


def run_script(script, project, task_id, payload):
    return subprocess.run([sys.executable, script], input=json.dumps(payload),
                          capture_output=True, text=True, env=_env(project, task_id),
                          cwd=project, timeout=20)


def decision(proc):
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)["hookSpecificOutput"]


class FixRoundTest(unittest.TestCase):
    online = True

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix="t314fix-")
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
        self.pending_dir = os.path.join(self.project, *PENDING_RELDIR.split("/"))

    def outside_dir(self):
        path = os.path.realpath(tempfile.mkdtemp(prefix="t314fix-ext-"))
        self.addCleanup(shutil.rmtree, path, True)
        return path

    # --- events -------------------------------------------------------------------------

    def _event(self, tool_name, target, post, tool_use_id, cwd=None, permission_mode="default"):
        if tool_name == "Bash":
            tool_input = {"command": target}
        elif tool_name == "Write":
            tool_input = {"file_path": target, "content": "{}"}
        else:
            tool_input = {"file_path": target, "old_string": "a", "new_string": "b"}
        event = {"tool_name": tool_name, "cwd": cwd or self.project, "tool_input": tool_input,
                 "tool_use_id": tool_use_id,
                 "hook_event_name": "PostToolUse" if post else "PreToolUse"}
        if permission_mode is not MISSING:
            event["permission_mode"] = permission_mode
        if post:
            event["tool_response"] = ({"stdout": "", "stderr": "", "interrupted": False}
                                      if tool_name == "Bash" else {"success": True})
        return event

    @staticmethod
    def new_id():
        return "toolu_" + uuid.uuid4().hex

    def pre(self, tool_name, target, task_id=TASK, tool_use_id=None, cwd=None):
        return run_script(PRE_HOOK, self.project, task_id,
                          self._event(tool_name, target, False, tool_use_id or self.new_id(), cwd))

    def post(self, tool_name, target, tool_use_id, task_id=TASK, cwd=None,
             permission_mode="default"):
        self.assertTrue(os.path.exists(RECORDER), f"recorder missing: {RECORDER_NAME}")
        proc = run_script(RECORDER, self.project, task_id,
                          self._event(tool_name, target, True, tool_use_id, cwd, permission_mode))
        self.assert_silent(proc)
        return proc

    def approve(self, tool_name, target, task_id=TASK, cwd=None, permission_mode="default",
                post_task_id=None):
        """Pre asks, the user says yes, Post fires with the same tool_use_id."""
        tool_use_id = self.new_id()
        self.assert_ask(self.pre(tool_name, target, task_id, tool_use_id, cwd))
        self.post(tool_name, target, tool_use_id,
                  task_id if post_task_id is None else post_task_id, cwd, permission_mode)
        return tool_use_id

    # --- state files --------------------------------------------------------------------

    def approved_keys(self, task_id=TASK):
        if not os.path.exists(self.approvals):
            return []
        with open(self.approvals, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        return data.get(task_id, [])

    def all_approved_keys(self):
        if not os.path.exists(self.approvals):
            return []
        with open(self.approvals, encoding="utf-8") as f:
            data = json.load(f)
        return [p for paths in data.values() for p in paths]

    def pending_path(self, tool_use_id):
        return os.path.join(self.pending_dir, f"{tool_use_id}.json")

    def pending_entries(self):
        if not os.path.isdir(self.pending_dir):
            return []
        return sorted(os.listdir(self.pending_dir))

    # --- assertions ---------------------------------------------------------------------

    def assert_ask(self, proc, *needles):
        out = decision(proc)
        self.assertIsNotNone(out, f"expected ask, got silence; stderr={proc.stderr!r}")
        self.assertEqual(out["permissionDecision"], "ask")
        reason = out["permissionDecisionReason"]
        for needle in needles:
            self.assertIn(needle, reason)
        self.assertEqual(proc.returncode, 0)
        return reason

    def assert_silent(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "", f"expected no output, got {proc.stdout!r}")


class F1RecordOnlyWhatPreAsked(FixRoundTest):
    """F1: Post promotes only the pending entry Pre wrote when it asked; nothing else."""

    def test_f1_glob_created_file_is_not_approved(self):
        ext = os.path.join(self.outside_dir(), "ext")
        os.makedirs(os.path.join(ext, "secrets"))
        with open(os.path.join(ext, "secrets", "k"), "w") as f:
            f.write("x")
        cmd = f"cp -r {ext} d && ls d/*/*"
        tool_use_id = self.new_id()
        self.assert_silent(self.pre("Bash", cmd, tool_use_id=tool_use_id))
        shutil.copytree(ext, os.path.join(self.project, "d"))  # the call runs
        self.post("Bash", cmd, tool_use_id)
        self.assertNotIn("d/secrets/k", self.all_approved_keys(),
                         "F1: a path Pre never asked about must not be recorded")
        self.assert_ask(self.pre("Write", "d/secrets/k"), "d/secrets/k")

    def test_f1_no_pending_entry_records_nothing(self):
        self.post("Write", SECRET, self.new_id())
        self.assertEqual(self.all_approved_keys(), [],
                         "F1: a Post with no pending entry from Pre must record nothing")
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_f1_pre_ask_writes_pending_entry(self):
        tool_use_id = self.new_id()
        self.assert_ask(self.pre("Write", SECRET, tool_use_id=tool_use_id))
        path = self.pending_path(tool_use_id)
        self.assertTrue(os.path.isfile(path), f"F1: Pre must write {PENDING_RELDIR}/<tool_use_id>.json")
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        self.assertIsInstance(entry, dict)
        self.assertEqual(entry.get("task_id"), TASK)
        self.assertEqual(entry.get("keys"), [SECRET])

    def test_f1_post_promotes_exactly_the_pending_keys_and_deletes_it(self):
        tool_use_id = self.new_id()
        self.assert_ask(self.pre("Write", SECRET, tool_use_id=tool_use_id))
        self.assertTrue(os.path.isfile(self.pending_path(tool_use_id)),
                        "F1: Pre must write the pending entry before Post runs")
        self.assertEqual(self.all_approved_keys(), [], "Pre alone records nothing")
        self.post("Write", SECRET, tool_use_id)
        self.assertEqual(self.approved_keys(TASK), [SECRET])
        self.assertFalse(os.path.exists(self.pending_path(tool_use_id)),
                         "F1: Post must delete the pending entry it promoted")
        self.assert_silent(self.pre("Write", SECRET))
        self.assert_silent(self.pre("Edit", SECRET))
        # Decision 4: Bash asks even on an approved file, and says Edit/Write will not.
        reason = self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.assertIn(EDIT_OR_WRITE_PHRASE, reason.lower())

    def test_f1_bash_event_records_nothing(self):
        # Decision 4: the recorder records nothing from a Bash event, even after Pre asked.
        self.approve("Bash", f"cp {SECRET} {SECRET_2}")
        self.assertEqual(self.all_approved_keys(), [],
                         "decision 4: a Bash call is never recorded as an approval")
        self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_f1_post_records_under_the_pending_task_id(self):
        self.approve("Write", SECRET, post_task_id=OTHER_TASK)
        self.assertIn(SECRET, self.approved_keys(TASK),
                      "F1: Post records under the task id Pre wrote, not the one re-resolved")
        self.assertNotIn(SECRET, self.approved_keys(OTHER_TASK))
        self.assert_ask(self.pre("Write", SECRET, task_id=OTHER_TASK), SECRET)

    def test_f1_pre_with_no_task_writes_no_pending_entry(self):
        tool_use_id = self.new_id()
        self.assert_ask(self.pre("Write", ".env", task_id=None, tool_use_id=tool_use_id))
        self.assertEqual(self.pending_entries(), [])
        self.post("Write", ".env", tool_use_id, task_id="T999")
        self.assertEqual(self.all_approved_keys(), [])

    def test_f1_silent_pre_writes_no_pending_entry(self):
        self.assert_silent(self.pre("Write", "src/app.py"))
        self.assertEqual(self.pending_entries(), [])


class F1LocalModeWritesNoPending(FixRoundTest):
    online = False

    def test_f1_local_pre_ask_writes_no_pending_entry(self):
        self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.assertEqual(self.pending_entries(), [])
        self.assertFalse(os.path.exists(os.path.join(self.project, STATE_RELDIR)),
                         "local mode: no .claude/state is created")


class F2PermissionMode(FixRoundTest):
    """F2: record only when Post's permission_mode is `default` or `auto`."""

    def test_f2_other_modes_record_nothing(self):
        for mode in NON_RECORDING_MODES:
            with self.subTest(permission_mode=mode if mode is not MISSING else "<missing>"):
                if os.path.exists(self.approvals):
                    os.remove(self.approvals)  # each mode fails for its own reason
                self.approve("Write", SECRET, permission_mode=mode)
                self.assertEqual(self.all_approved_keys(), [],
                                 f"F2: permission_mode {mode!r} must record nothing")
                self.assert_ask(self.pre("Write", SECRET), SECRET)

    def test_f2_default_and_auto_record(self):
        for mode in RECORDING_MODES:
            with self.subTest(permission_mode=mode):
                if os.path.exists(self.approvals):
                    os.remove(self.approvals)
                self.approve("Write", SECRET, permission_mode=mode)
                self.assertIn(SECRET, self.approved_keys(TASK))
                self.assert_silent(self.pre("Write", SECRET))


class F3OneCanonicalKey(FixRoundTest):
    """F3: one key per path: root-relative under root, else absolute realpath; never cwd-relative."""

    def test_f3_cwd_relative_form_is_not_recorded(self):
        infra = os.path.join(self.project, "infra")
        os.makedirs(infra)
        self.approve("Write", "prod.tf", cwd=infra)
        self.assertEqual(self.all_approved_keys(), ["infra/prod.tf"],
                         "F3: the only key is the root-relative form")
        self.assert_ask(self.pre("Write", "prod.tf"), "prod.tf")
        self.assert_ask(self.pre("Write", os.path.join(self.project, "prod.tf")), "prod.tf")
        self.assert_silent(self.pre("Write", "infra/prod.tf"))

    def test_f3_outside_root_key_is_absolute_realpath(self):
        outside = os.path.join(self.outside_dir(), "server.pem")
        self.approve("Write", outside)
        self.assertEqual(self.all_approved_keys(), [os.path.realpath(outside)])
        self.assert_silent(self.pre("Write", outside))


class F4StateDirProtected(FixRoundTest):
    """F4: `.claude/state` and everything under it is sensitive; a symlinked state is unread."""

    FORGERIES = (
        ("Bash", "cp /tmp/f.json .claude/state/"),
        ("Bash", "mv /tmp/f.json .claude/state"),
        ("Bash", "cd .claude/state && echo '{}' > sensitive-approvals.json"),
        ("Bash", "ln -s /tmp/evil .claude/state"),
        ("Bash", "rm -rf .claude/state"),
        ("Write", f"{PENDING_RELDIR}/x.json"),
        ("Edit", f"{PENDING_RELDIR}/x.json"),
    )

    def test_f4_calls_on_the_state_dir_ask(self):
        for tool, target in self.FORGERIES:
            with self.subTest(tool=tool, target=target):
                self.assert_ask(self.pre(tool, target))

    def test_f4_state_paths_cannot_be_approved(self):
        self.approve("Write", f"{PENDING_RELDIR}/x.json")
        self.assertEqual([k for k in self.all_approved_keys() if k.startswith(STATE_RELDIR)], [])
        self.assert_ask(self.pre("Write", f"{PENDING_RELDIR}/x.json"))

    def test_f4_symlinked_state_dir_is_not_read(self):
        evil = self.outside_dir()
        with open(os.path.join(evil, "sensitive-approvals.json"), "w") as f:
            json.dump({TASK: [".env"]}, f)
        os.symlink(evil, os.path.join(self.project, ".claude", "state"))
        self.assert_ask(self.pre("Write", ".env"), ".env")

    def test_f4_symlinked_approval_file_is_not_read(self):
        evil = self.outside_dir()
        forged = os.path.join(evil, "sensitive-approvals.json")
        with open(forged, "w") as f:
            json.dump({TASK: [".env"]}, f)
        os.makedirs(os.path.dirname(self.approvals))
        os.symlink(forged, self.approvals)
        self.assert_ask(self.pre("Write", ".env"), ".env")


class F5FileKeysOnly(FixRoundTest):
    """F5: never a directory key. Decision 4: the Bash ask names Edit or Write."""

    def test_f5_directory_read_does_not_approve_delete(self):
        os.makedirs(os.path.join(self.project, "infra"))
        self.approve("Bash", "ls infra")
        self.assertNotIn("infra", self.all_approved_keys(), "F5: no directory key")
        self.assert_ask(self.pre("Bash", "rm -rf infra"), "infra")

    def test_f5_bash_ask_reason_names_edit_or_write(self):
        reason = self.assert_ask(self.pre("Bash", f"cat {SECRET}"), SECRET)
        self.assertIn(EDIT_OR_WRITE_PHRASE, reason.lower())


class F6SiteRow(unittest.TestCase):
    """F6: the recorder's row in site/docs.html carries the `inert` tag."""

    def test_f6_recorder_row_is_tagged_inert(self):
        with open(SITE_DOCS, encoding="utf-8") as f:
            rows = [line.replace("<wbr>", "") for line in f if "<tr>" in line]
        ours = [r for r in rows if RECORDER_NAME in r]
        self.assertEqual(len(ours), 1, f"one site/docs.html row for {RECORDER_NAME}")
        self.assertRegex(ours[0], r'<span class="tag tag-inert">inert</span>')
        self.assertNotIn("tag-advise", ours[0])


if __name__ == "__main__":
    unittest.main()
