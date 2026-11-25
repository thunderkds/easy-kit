#!/usr/bin/env python3
"""T316 locked oracle: the sensitive-path hook treats its own pattern list as always sensitive.

Before T316 `.claude/sensitive-paths.txt` was in no pattern, so an Edit of it was silent and an
agent could drop every protection with no prompt. Like `.claude/state/**` (T314), the list's
name is now a protected pattern: it always asks, no `!` line unmarks it, a predicting guide
cannot pre-authorise it and an online approval cannot cover it.

Same harness as `test_t314_fix_round.py` (`FixRoundTest`: temp project, Pre -> Post).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t316_list_self_protect.py -q -p no:cacheprovider
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest  # noqa: E402

TASK = "T314"  # the harness's default task ID
LIST = ".claude/sensitive-paths.txt"
NAME = "sensitive-paths.txt"

PREDICTING_GUIDE = f"""# TASK_GUIDE — {TASK}: fixture

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `{LIST}` | edit |
| `src/app.py` | edit |
"""


class ListTest(FixRoundTest):
    def list_path(self):
        return os.path.join(self.project, *LIST.split("/"))

    def append_to_list(self, text):
        with open(self.list_path(), "a", encoding="utf-8") as f:
            f.write("\n" + text + "\n")


class OfflineList(ListTest):
    online = False

    def test_ac1_edit_and_write_ask(self):
        for tool in ("Edit", "Write"):
            for target in (LIST, self.list_path()):
                with self.subTest(tool=tool, target=target):
                    self.assert_ask(self.pre(tool, target), NAME)

    def test_ac2_bash_naming_the_list_asks(self):
        for cmd in (f"sed -i '/infra/d' {LIST}", f"rm {LIST}", f"printf '' > {LIST}",
                    f"git checkout -- {LIST}"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd), NAME)

    def test_ac3_a_negation_line_does_not_unmark_it(self):
        self.append_to_list(f"!{LIST}\n!{NAME}\n!**/{NAME}")
        self.assert_ask(self.pre("Edit", LIST), NAME)
        self.assert_ask(self.pre("Bash", f"rm {LIST}"), NAME)

    def test_ac4_a_predicting_guide_does_not_pre_authorise_it(self):
        with open(os.path.join(self.project, "tasks", f"TASK_GUIDE_{TASK}.md"), "w") as f:
            f.write(PREDICTING_GUIDE)
        self.assert_ask(self.pre("Edit", LIST), NAME)
        self.assert_ask(self.pre("Write", LIST), NAME)

    def test_ac6_relative_name_after_cd_claude_asks(self):
        self.assert_ask(self.pre("Bash", f"cd .claude && printf '' > {NAME}"))
        claude_dir = os.path.join(self.project, ".claude")
        self.assert_ask(self.pre("Write", NAME, cwd=claude_dir), NAME)

    def test_ac7_unrelated_calls_stay_silent(self):
        self.assert_silent(self.pre("Edit", "src/app.py"))
        self.assert_silent(self.pre("Bash", "ls -la"))
        self.assert_silent(self.pre("Write", "docs/sensitive-paths.md"))


class OnlineList(ListTest):
    online = True

    def seed_approval(self, keys):
        os.makedirs(os.path.dirname(self.approvals), exist_ok=True)
        with open(self.approvals, "w", encoding="utf-8") as f:
            json.dump({TASK: keys}, f)

    def test_ac5_a_recorded_approval_does_not_cover_it(self):
        self.seed_approval([LIST, NAME])
        self.assert_ask(self.pre("Edit", LIST), NAME)
        self.assert_ask(self.pre("Write", LIST), NAME)

    def test_ac5_a_yes_records_no_approval_for_it(self):
        self.approve("Write", LIST)
        self.assertEqual(self.pending_entries(), [])
        self.assertEqual(self.all_approved_keys(), [])
        self.assert_ask(self.pre("Write", LIST), NAME)

    def test_ac1_online_edit_asks(self):
        self.assert_ask(self.pre("Edit", LIST), NAME)


if __name__ == "__main__":
    unittest.main()
