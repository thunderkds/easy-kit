#!/usr/bin/env python3
"""T374 — the T363 round-2 follow-ups in the sensitive-path hook's folder rule.

  * N1: `timeout` with an option value (`-s KILL`, `-k 5`, `--signal=KILL`, `-sKILL`) before its
    duration is still read past, so `timeout -s KILL 5 rm -rf config` asks; `xargs` and
    `find -exec sh -c` stay silent and are named in the header's "Recorded limitations".
  * N2: the walk budget is one per call (two folders together can spend it) and counts folders
    as well as files (only empty folders can spend it).

Same harness as `test_t363_folder_level.py` (`FixRoundTest`: a temp kit project, cwd = its root).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t374_folder_rule_followups.py -q -p no:cacheprovider
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest  # noqa: E402

WALK_ENV = "CLAUDE_SENSITIVE_FOLDER_WALK_MAX"
HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "pre_tool_sensitive_path.py")


class FollowUps(FixRoundTest):
    online = False

    def write(self, rel, text="x\n"):
        path = os.path.join(self.project, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def setUp(self):
        super().setUp()
        self.write("config/.env", "KEY=1\n")
        for rel in ("a/1.txt", "a/2.txt", "b/1.txt", "b/2.txt"):
            self.write(rel)
        for k in range(4):
            os.makedirs(os.path.join(self.project, "empty", f"d{k}"))

    # ── N1 — `timeout` option values ───────────────────────────────────────────────────────────
    def test_n1_timeout_with_an_option_value_still_asks(self):
        for cmd in ("timeout -s KILL 5 rm -rf config", "timeout -k 5 10 rm -rf config",
                    "timeout --signal=KILL 5 rm -rf config", "timeout -sKILL 5 rm -rf config",
                    "timeout --kill-after 3 5 rm -rf config", "timeout --preserve-status 5 rm -rf config",
                    "sudo -u root rm -rf config", "nice -n 5 rm -rf config", "env -u HOME rm -rf config"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r1_a_wrong_or_missing_table_entry_never_hides_the_command(self):
        """Round 1 (F1, F2, F4): each segment is read both with and without the value skips, so an
        option listed wrongly (`env -S` takes the command itself, a bare `sudo -h` is help) or a
        value option the table lacks can only add an ask, never remove one."""
        for cmd in ("env -S rm -rf config", "env --split-string rm -rf config", "sudo -h rm -rf config",
                    "timeout --signal KILL 5 rm -rf config", "sudo -R /x rm -rf config",
                    "sudo -T 5 rm -rf config", "time -o out.txt rm -rf config", "exec -a x rm -rf config",
                    "env -P /bin rm -rf config"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r2_a_cd_behind_a_wrapper_neither_hides_nor_moves(self):
        """Round 2 (G1, G2): only a bare `cd`/`pushd` moves the folder later segments resolve
        against (a wrapped `cd` does not change the shell's folder), and a reading that lands on
        `cd` does not stop the other reading from being judged."""
        self.write("cd/.env", "KEY=1\n")
        for cmd in ("sudo -u rm -rf cd", "env -C rm -rf cd", "nice -n 5 cd x && rm -rf config",
                    "sudo -u root cd cd; rm -rf config", "sudo --nonsense-opt rm -rf config"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))
        self.assert_ask(self.pre("Bash", "cd config && rm -rf ."))  # a bare cd still moves
        for cmd in ("FOO=1 cd build && rm -rf ../config", "command cd build && rm -rf ../config",
                    "\\cd build && rm -rf ../config", "time cd build && rm -rf ../config",
                    "FOO=1 cd build; rm -rf ../cd", "builtin cd build && rm -rf ../config"):  # round 3 (H1)
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_n1_timeout_on_a_reading_command_stays_silent(self):
        self.assert_silent(self.pre("Bash", "timeout -s KILL 5 ls config"))

    def test_n1_header_names_xargs_and_find_exec_sh(self):
        with open(HOOK, encoding="utf-8") as f:
            text = f.read()
        limits = text[text.index("Recorded limitations"):text.index('"""', text.index("Recorded limitations"))]
        self.assertIn("xargs", limits)
        self.assertIn("-exec sh -c", limits)

    # ── N2 — one walk budget per call, folders counted ─────────────────────────────────────────
    def test_n2_the_budget_is_shared_by_every_folder_of_the_call(self):
        # a and b hold 2 files each: either alone fits a cap of 3 entries, both together do not
        with mock.patch.dict(os.environ, {WALK_ENV: "3"}):
            self.assert_silent(self.pre("Bash", "rm -rf a"))
            self.assert_ask(self.pre("Bash", "rm -rf a b"))

    def test_n2_folders_count_against_the_budget(self):
        # `empty` holds 4 empty folders and no file: over a cap of 3 only if folders count
        with mock.patch.dict(os.environ, {WALK_ENV: "3"}):
            self.assert_ask(self.pre("Bash", "rm -rf empty"))
        self.assert_silent(self.pre("Bash", "rm -rf empty"))  # control: the default cap


if __name__ == "__main__":
    unittest.main()
