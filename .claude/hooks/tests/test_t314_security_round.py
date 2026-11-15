#!/usr/bin/env python3
"""T314 security-review locked oracle (S1-S4, TASK_GUIDE_T314 "Supervisor decisions", decision 3).

Written by qa-expert BEFORE the fix (Pillar 3). The implementer may not edit it.

Same harness as `test_t314_fix_round.py` (its `FixRoundTest` base: temp project, online
board, Pre -> Post with one `tool_use_id`, `permission_mode` `default`).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t314_security_round.py -q -p no:cacheprovider
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest  # noqa: E402

TASK = "T314"
ARROW = "→"  # S4: "config/prod.json → .env"


class SecurityRoundTest(FixRoundTest):
    def write_file(self, relpath, content="x"):
        path = os.path.join(self.project, *relpath.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path


class S1DirectoryChangeHonoursNoApproval(SecurityRoundTest):
    """S1: a Bash call that can change the directory a path resolves against asks for every
    sensitive path, approved or not. Edit/Write are unaffected."""

    def setUp(self):
        super().setUp()
        self.write_file(".env", "ROOT=1")
        self.write_file("svc/.env", "SVC=1")
        self.write_file("x", "")
        self.other = self.outside_dir()
        with open(os.path.join(self.other, ".env"), "w") as f:
            f.write("OTHER=1")
        self.approve("Bash", "cat .env")
        self.assertIn(".env", self.approved_keys(TASK), "setup: `.env` approved via Pre -> Post")

    def commands(self):
        return (
            "cd svc && cat .env",
            f"cd {self.other} && rm -f .env",
            "git -C svc show :.env",
            "pushd svc; cat .env",
            "env -C svc cat .env",
            "sh -c 'cd svc; cat .env'",
            'bash -c "cat .env"',
            'eval "cat .env"',
            "source x; cat .env",
        )

    def test_s1_directory_changing_calls_ask(self):
        for cmd in self.commands():
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_s1_plain_call_stays_silent(self):
        self.assert_silent(self.pre("Bash", "cat .env"))

    def test_s1_edit_and_write_of_the_approved_file_stay_silent(self):
        self.assert_silent(self.pre("Edit", ".env"))
        self.assert_silent(self.pre("Write", ".env"))


class S2ApprovalFileCannotBeForged(SecurityRoundTest):
    """S2: the approval file basename is sensitive anywhere; `.claude` / `.claude/state` reached
    through a directory change or `-C` asks; a forge call is never an approval of `.env`."""

    FORGE = ("cd .claude && mkdir -p state && "
             "printf '{\"T314\": [\".env\"]}' > state/sensitive-approvals.json")

    def test_s2_forge_calls_ask(self):
        for tool, target in (
            ("Bash", self.FORGE),
            ("Bash", "tar -C .claude -xf /tmp/x.tar"),
            ("Bash", "git -C .claude checkout -- state"),
            ("Write", "docs/sensitive-approvals.json"),
            ("Write", "sensitive-approvals.json"),
            ("Write", "sensitive-approvals.json.tmp"),
            ("Write", ".claude/sensitive-approvals.json.tmp"),
        ):
            with self.subTest(tool=tool, target=target):
                self.assert_ask(self.pre(tool, target))

    def test_s2_forge_call_is_never_recorded_as_approval_of_env(self):
        self.write_file(".env", "SECRET")
        tool_use_id = self.new_id()
        self.pre("Bash", self.FORGE, tool_use_id=tool_use_id)  # ask expected; see test above
        self.post("Bash", self.FORGE, tool_use_id)  # the user said yes to the forge call
        self.assertNotIn(".env", self.all_approved_keys(),
                         "S2: approving the forge call must not approve `.env`")
        self.assertEqual([k for k in self.all_approved_keys()
                          if k.rsplit("/", 1)[-1].startswith("sensitive-approvals.json")], [],
                         "S2: the approval file is never approvable")
        self.assert_ask(self.pre("Bash", "cat .env"), ".env")


class S3TrailingSlashNeverApproved(SecurityRoundTest):
    """S3: a token ending in `/` never matches an approval."""

    def test_s3_approved_file_reused_as_directory_asks(self):
        os.makedirs(os.path.join(self.project, "secrets"))
        self.approve("Write", "secrets/a")
        self.assertIn("secrets/a", self.approved_keys(TASK), "setup: `secrets/a` approved")
        self.assert_ask(self.pre(
            "Bash", "mkdir secrets/a && cp -r /etc/hostname secrets/a/ && rm -rf secrets/a/"))


class S4SymlinkAskNamesBoth(SecurityRoundTest):
    """S4: when the recorded key differs from the path as written, the ask names both."""

    def test_s4_symlink_ask_names_written_path_and_key(self):
        self.write_file(".env", "SECRET")
        os.makedirs(os.path.join(self.project, "config"))
        os.symlink("../.env", os.path.join(self.project, "config", "prod.json"))
        self.assert_ask(self.pre("Bash", "cat config/prod.json"), f"config/prod.json {ARROW} .env")


if __name__ == "__main__":
    unittest.main()
