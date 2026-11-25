#!/usr/bin/env python3
"""T371 — under `[admin]` the sensitive-path hook approves instead of asking, and logs every
approved write (`tasks/TASK_GUIDE_T371.md`, AC 1-7).

  * Outside `[admin]` nothing changes: every sensitive call asks.
  * Under `[admin]` (a session tag, or the latest typed request carrying it) a call that only reads
    passes with no log; a write, delete, move or run passes (no decision: the normal permission
    flow) after one JSON line is appended to `<anchors base>/<repo slug>/sensitive-admin-<session>.jsonl`.
    The hook never emits `allow`.
  * The guard's own files (`PROTECTED_PATTERNS`: `.claude/state/**`, the approval file, the list)
    still ask for a write under `[admin]`.
  * A log line that cannot be written asks.

Same harness as `test_t316_list_self_protect.py` (`FixRoundTest`), plus a constructed transcript.

Run with:
    python3 -m pytest .claude/hooks/tests/test_t371_admin_approval.py -q -p no:cacheprovider
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest, decision  # noqa: E402

SID = "11111111-2222-3333-4444-555555555555"


def _ts(offset_s):
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_s)).isoformat().replace("+00:00", "Z")


def human(text, offset_s=-600):
    return {"type": "user", "message": {"role": "user", "content": text}, "timestamp": _ts(offset_s),
            "origin": {"kind": "human"}, "isSidechain": False, "sessionId": SID}


class AdminApproval(FixRoundTest):
    online = False
    requests = ("do the task [admin]",)

    def setUp(self):
        super().setUp()
        self.anchors = tempfile.mkdtemp(prefix="t371-anchors-")
        self.addCleanup(__import__("shutil").rmtree, self.anchors, True)
        patcher = mock.patch.dict(os.environ, {"CLAUDE_TRACE_ANCHOR_DIR": self.anchors})
        patcher.start()
        self.addCleanup(patcher.stop)
        os.makedirs(os.path.join(self.project, "config"))
        with open(os.path.join(self.project, "config", ".env"), "w") as f:
            f.write("KEY=1\n")
        self.transcript = os.path.join(self.anchors, "t.jsonl")
        self.write_transcript(*self.requests)

    def write_transcript(self, *texts):
        with open(self.transcript, "w", encoding="utf-8") as f:
            for k, text in enumerate(texts):
                f.write(json.dumps(human(text, -600 + 10 * k)) + "\n")

    def _event(self, *a, **k):
        event = super()._event(*a, **k)
        event["transcript_path"] = self.transcript
        event["session_id"] = SID
        return event

    def log_lines(self):
        found = []
        for top, _, files in os.walk(self.anchors):
            for name in files:
                if name.startswith("sensitive-admin-") and name.endswith(".jsonl"):
                    with open(os.path.join(top, name), encoding="utf-8") as f:
                        found += [json.loads(line) for line in f if line.strip()]
        return found

    def assert_approved(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = decision(proc)
        self.assertTrue(out is None or "permissionDecision" not in out, out)  # never ask, never allow
        return out


class OutsideAdmin(AdminApproval):
    requests = ("do the task",)

    def test_ac1_without_the_tag_every_sensitive_call_asks(self):
        for tool, target in (("Write", ".env"), ("Bash", "rm -rf config"), ("Bash", "cat config/.env")):
            with self.subTest(tool=tool, target=target):
                self.assert_ask(self.pre(tool, target))
        self.assertEqual(self.log_lines(), [])

    def test_ac6_a_later_stop_ends_the_approval(self):
        self.write_transcript("do the task [admin]", "pause now [stop]")
        self.assert_ask(self.pre("Write", ".env"))


class UnderAdmin(AdminApproval):
    def test_ac2_a_write_passes_and_is_logged(self):
        out = self.assert_approved(self.pre("Write", ".env"))
        lines = self.log_lines()
        self.assertEqual(len(lines), 1, lines)
        line = lines[0]
        for key in ("time", "session", "task", "tool", "target", "patterns"):
            self.assertIn(key, line)
        self.assertEqual(line["session"], SID)
        self.assertEqual(line["tool"], "Write")
        self.assertIn(".env", json.dumps(line["patterns"]))
        self.assertIn("sensitive-admin-", json.dumps(out))  # the context names the log for the report

    def test_ac2_destructive_bash_passes_and_is_logged(self):
        for cmd in ("rm -rf config", "printf x > .env", "mv config/.env /tmp/x"):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(len(self.log_lines()), 3)

    def test_ac3_a_read_passes_with_no_log(self):
        for cmd in ("cat config/.env", "grep -rn KEY config", "ls -a config", "head -1 .env",
                    "wc -l config/.env", "find config -name '*.env'", "cat config/.env | grep KEY"):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(self.log_lines(), [])

    def test_ac3_a_read_with_a_write_in_it_is_a_write(self):
        for cmd in ("cat config/.env > out.txt", "cat config/.env | tee x", "find config -delete",
                    "git diff --output=x -- config/.env", "cat config/.env && rm -rf config"):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(len(self.log_lines()), 5)

    def test_ac4_the_guards_own_files_still_ask_for_a_write(self):
        for tool, target in (("Edit", ".claude/sensitive-paths.txt"), ("Bash", "rm -rf .claude"),
                             ("Write", ".claude/state/sensitive-approvals.json"),
                             ("Bash", "printf '' > .claude/sensitive-paths.txt")):
            with self.subTest(tool=tool, target=target):
                self.assert_ask(self.pre(tool, target))

    def test_ac5_a_log_that_cannot_be_written_asks(self):
        os.rmdir(self.anchors) if not os.listdir(self.anchors) else None
        blocker = os.path.join(self.anchors, "blocker")
        with open(blocker, "w") as f:
            f.write("x")
        with mock.patch.dict(os.environ, {"CLAUDE_TRACE_ANCHOR_DIR": blocker}):
            self.assert_ask(self.pre("Write", ".env"))

    def test_ac5_a_symlinked_log_asks(self):
        self.assert_approved(self.pre("Write", ".env"))  # creates the folder and the log
        log = next(os.path.join(t, n) for t, _, fs in os.walk(self.anchors) for n in fs
                   if n.startswith("sensitive-admin-"))
        os.remove(log)
        os.symlink(os.path.join(self.anchors, "elsewhere.jsonl"), log)
        self.assert_ask(self.pre("Write", ".env"))

    def test_ac7_the_log_only_grows(self):
        self.assert_approved(self.pre("Write", ".env"))
        self.assert_approved(self.pre("Bash", "rm -rf config"))
        self.assertEqual([line["tool"] for line in self.log_lines()], ["Write", "Bash"])


class RoundOneFixes(AdminApproval):
    """Reviewer round 1 (F1-F4) and the security scan (V1, V2)."""

    def mark_resume(self, text):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
        import auto_mode
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.project}):
            path = auto_mode.resume_mark_path(SID)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def test_f1_a_tag_typed_before_a_resume_approves_nothing(self):
        self.mark_resume(_ts(-60))  # resumed after the `[admin]` request at -600 s
        self.assert_ask(self.pre("Write", ".env"))

    def test_f1_an_unreadable_resume_mark_approves_nothing(self):
        self.mark_resume("garbage")
        self.assert_ask(self.pre("Write", ".env"))

    def test_f3_ticket_and_auto_are_not_admin(self):
        for texts in (("do it [ticket]",), ("do it [auto]",), ("do it [admin]", "next [ticket]"),
                      ("do it [admin] [stop]",)):
            with self.subTest(texts=texts):
                self.write_transcript(*texts)
                self.assert_ask(self.pre("Write", ".env"))

    def test_f3_the_session_tag_holds_over_a_later_plain_request(self):
        self.write_transcript("do it [admin]", "and now the next step")
        self.assert_approved(self.pre("Write", ".env"))

    def test_v1_the_guards_own_files_ask_even_for_a_read_form(self):
        for cmd in ("find .claude/state -name sensitive-approvals.json -ex''ec cp x {} ;",
                    "cat .claude/sensitive-paths.txt", "find .claude -name sensitive-paths.txt -delete"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_v2_f2_quoted_flags_and_code_runners_are_writes(self):
        for cmd in ("find config -de''lete", "find config -ex\"ec\" rm {} +", "find config -\\delete",
                    "git diff --out''put=.env -- config/.env", "git diff -- config/.env",
                    "GIT_EXTERNAL_DIFF=rm git diff --ext-diff config/.env", "rg --pre ./x.sh KEY config/.env",
                    "file -C -m config/.env", "FOO=1 cat config/.env"):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(len(self.log_lines()), 9)

    def test_v2_quoted_find_flags_ask_outside_admin_too(self):
        self.write_transcript("do the task")
        for cmd in ("find config -de''lete", "find config -ex\"ec\" rm {} +", "find config -\\delete"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_f4_the_log_folder_and_file_are_private(self):
        self.assert_approved(self.pre("Write", ".env"))
        log = next(os.path.join(t, n) for t, _, fs in os.walk(self.anchors) for n in fs
                   if n.startswith("sensitive-admin-"))
        self.assertEqual(os.stat(log).st_mode & 0o777, 0o600)
        self.assertEqual(os.stat(os.path.dirname(log)).st_mode & 0o077, 0)

    def test_f4_a_shared_or_symlinked_log_folder_asks(self):
        self.assert_approved(self.pre("Write", ".env"))
        log = next(os.path.join(t, n) for t, _, fs in os.walk(self.anchors) for n in fs
                   if n.startswith("sensitive-admin-"))
        folder = os.path.dirname(log)
        os.chmod(folder, 0o777)
        self.assert_ask(self.pre("Write", ".env"))
        os.chmod(folder, 0o700)
        real = folder + "-real"
        os.rename(folder, real)
        os.symlink(real, folder)
        self.assert_ask(self.pre("Write", ".env"))

    def test_f5_the_note_says_the_hook_did_not_ask(self):
        out = self.assert_approved(self.pre("Write", ".env"))
        self.assertIn("not asked", json.dumps(out))
        self.assertEqual(self.log_lines()[0].get("decision"), "not asked by the hook ([admin])")


class AdminInAToolResult(AdminApproval):
    """`[admin]` that the user did not type (no human origin) approves nothing."""
    def write_transcript(self, *texts):
        with open(self.transcript, "w", encoding="utf-8") as f:
            entry = human("do the task [admin]")
            entry["origin"] = {"kind": "tool"}
            f.write(json.dumps(entry) + "\n")

    def test_ac6_an_untyped_tag_approves_nothing(self):
        self.assert_ask(self.pre("Write", ".env"))


if __name__ == "__main__":
    unittest.main()
