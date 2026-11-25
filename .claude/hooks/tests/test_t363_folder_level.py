#!/usr/bin/env python3
"""T363 (option C) — the sensitive-path hook asks when a destructive command targets a folder that
holds a sensitive path, and expands `{a,b}` brace tokens (`tasks/TASK_GUIDE_T363.md`, AC 1-4).

Before T363 the hook matched each Bash token as a path only: `rm -rf .claude` named no listed
file, so it was silent although it deletes `.claude/sensitive-paths.txt`.

Same harness as `test_t316_list_self_protect.py` (`FixRoundTest`: a temp kit project whose
`.claude/sensitive-paths.txt` is the shipped list, cwd = the project root).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t363_folder_level.py -q -p no:cacheprovider
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest  # noqa: E402

WALK_ENV = "CLAUDE_SENSITIVE_FOLDER_WALK_MAX"


class FolderLevel(FixRoundTest):
    online = False

    def setUp(self):
        super().setUp()
        for rel, text in (("config/.env", "KEY=1\n"), ("build/out.txt", "x\n"),
                          ("src/app.py", "print(1)\n"), ("notes.txt", "n\n"),
                          ("secrets/token.txt", "t\n")):
            path = os.path.join(self.project, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    # ── AC 1 — a destructive command on a folder that holds a sensitive path asks ──────────────
    def test_ac1_destructive_commands_on_a_holding_folder_ask(self):
        for cmd in ("rm -rf .claude", "rm -r .claude", "rm -R .claude/", "rm --recursive .claude",
                    "find .claude -delete", "find . -name x -exec rm {} +", "find -delete",
                    "mv .claude old", "git checkout HEAD~1 -- .claude", "git restore .",
                    "rm -rf config", "rm -rf secrets", "sudo rm -rf .claude",
                    "FOO=1 /bin/rm -rf .claude", "ls && rm -rf .claude", "cd src; rm -rf ..",
                    "env rm -rf config"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_ac1_the_ask_names_the_folder(self):
        reason = self.assert_ask(self.pre("Bash", "rm -rf config"))
        self.assertIn("config", reason)

    def test_ac1_a_predicting_guide_does_not_cover_the_folder(self):
        guide = os.path.join(self.project, "tasks", "TASK_GUIDE_T314.md")
        with open(guide, "w", encoding="utf-8") as f:
            f.write("# TASK_GUIDE — T314: fixture\n\n## Files to Change (Predicted)\n\n"
                    "| File | Change |\n|------|--------|\n| `config/.env` | edit |\n")
        self.assert_ask(self.pre("Bash", "rm -rf config"))

    # ── AC 2 — everything else stays silent ────────────────────────────────────────────────────
    def test_ac2_reads_and_other_targets_stay_silent(self):
        for cmd in ("ls .claude", "ls -a .claude", "cat .claude/x.md", "python3 -m pytest .",
                    "grep -rn x .claude", "rm -rf build", "rm notes.txt", "git checkout main",
                    "git restore src/app.py", "mv src/app.py src/main.py", "find . -name '*.py'",
                    "rm -rf missing-dir", "ls -la"):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_ac2_a_folder_outside_both_roots_is_skipped(self):
        outside = self.outside_dir()
        os.makedirs(os.path.join(outside, ".claude"))
        with open(os.path.join(outside, ".claude", "sensitive-paths.txt"), "w") as f:
            f.write(".env\n")
        self.assert_silent(self.pre("Bash", f"rm -rf {outside}"))

    # ── AC 3 — brace tokens are expanded ───────────────────────────────────────────────────────
    def test_ac3_a_brace_token_naming_a_sensitive_path_asks(self):
        for cmd in ("cp x .claude/{sensitive-paths.txt,y}", "rm .{env,bak}",
                    "printf '' > .claude/sensitive-{paths.txt,x}"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_ac3_a_harmless_brace_token_stays_silent(self):
        self.assert_silent(self.pre("Bash", "cp a.{txt,md} out"))

    # ── AC 4 — a walk that reaches its cap asks ───────────────────────────────────────────────
    def test_ac4_the_walk_cap_fails_toward_asking(self):
        with mock.patch.dict(os.environ, {WALK_ENV: "0"}):  # build holds one file: over the cap
            self.assert_ask(self.pre("Bash", "rm -rf build"))
        self.assert_silent(self.pre("Bash", "rm -rf build"))  # control: no cap, nothing inside

    # ── Round 1 review fixes ───────────────────────────────────────────────────────────────────
    def test_r1_brace_bomb_asks_fast(self):
        import time
        start = time.monotonic()
        self.assert_ask(self.pre("Bash", "cat notes.txt #" + "{a,b}" * 24))
        self.assertLess(time.monotonic() - start, 10)

    def test_r1_an_unreadable_folder_asks(self):
        ro = os.path.join(self.project, "ro", "sub")
        os.makedirs(ro)
        os.chmod(ro, 0)
        self.addCleanup(os.chmod, ro, 0o755)
        if os.access(ro, os.R_OK):
            self.skipTest("running as a user who can read mode-000 folders")
        self.assert_ask(self.pre("Bash", "rm -rf ro"))

    def test_r1_read_only_finds_and_index_only_restores_stay_silent(self):
        for cmd in ("find . -name '*.py' -exec grep -l x {} +", "find . -type f -exec wc -l {} +",
                    "git restore --staged .", "git restore -S .", "rm config", "mv notes.txt .",
                    "mv notes.txt src/"):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_r1_destructive_forms_the_first_round_missed_ask(self):
        for cmd in ("find . -name x -exec rm {} +", "find config -execdir rm {} ;",
                    "git restore --staged --worktree .", "rm -rf conf*", "rm -rf ./conf*",
                    "timeout 5 rm -rf config", "\\rm -rf config", "rm -rf config>/dev/null"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r1_a_secret_only_under_git_stays_silent(self):
        git_dir = os.path.join(self.project, "repo", ".git")
        os.makedirs(git_dir)
        with open(os.path.join(git_dir, ".env"), "w") as f:
            f.write("x\n")
        self.assert_silent(self.pre("Bash", "rm -rf repo"))


if __name__ == "__main__":
    unittest.main()
