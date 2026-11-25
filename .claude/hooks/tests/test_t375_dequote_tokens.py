#!/usr/bin/env python3
"""T375 — the sensitive-path hook reads a word the way the shell does (`tasks/TASK_GUIDE_T375.md`).

  * AC 1: quotes and backslashes inside a word are dropped before the path match.
  * AC 2: `$'…'` and `$"…"` inside a word are dequoted in the folder rule.
  * AC 3: a word the shell still builds (`${x}`, `$x`) next to literal text is a glob; a bare
    variable stays a recorded limit.
  * AC 4: a quoted span with a space stays data.
  * AC 5: T371 round-3 pins under `[admin]`.
  * AC 6: the list header names the `[admin]` exception.

Same harness as `test_t374_folder_rule_followups.py` and `test_t371_admin_approval.py`.

Run with:
    python3 -m pytest .claude/hooks/tests/test_t375_dequote_tokens.py -q -p no:cacheprovider
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_t371_admin_approval as t371  # noqa: E402
from test_t314_fix_round import FixRoundTest  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class Dequote(FixRoundTest):
    online = False

    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.project, "config"), exist_ok=True)
        with open(os.path.join(self.project, "config", ".env"), "w") as f:
            f.write("KEY=1\n")
        os.makedirs(os.path.join(self.project, "infra"), exist_ok=True)  # R1 P2-3: a `*` finds a folder
        for name in ("prod-values.yaml", "tls_cert.pem", "server.pem", ".env"):  # R3: `*-*`, `*_*` find these; R4: `.??`
            with open(os.path.join(self.project, name), "w") as f:
                f.write("x\n")

    def test_ac1_quotes_and_backslashes_in_a_word_are_dropped(self):
        for cmd in ("cat .claude/sens''itive-paths.txt", 'cat .claude/sens""itive-paths.txt',
                    "cat .claude/sensitive-pa\\ths.txt", 'cat .claude/"sensitive-paths.txt"',
                    "cat conf''ig/.env"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r1_p1_a_data_command_does_not_hide_a_mixed_word(self):
        """Round 1 P1-1: `echo`, `printf`, `grep`, `rg` blank their quoted spans, so a word that mixes
        quoted and plain text (`.e"n"v`) must be read before that."""
        for cmd in ('echo x > .e"n"v', "echo x > .claude/sens''itive-paths.txt", "printf x > .e''nv",
                    "grep KEY .e''nv", "grep KEY config/.e''nv", 'rg KEY .e""nv',
                    'echo x >> ".claude/sens"itive-paths.txt'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))
        for cmd in ('echo ".env"', 'grep -n ".env" .gitignore', "grep -n '.env' .gitignore"):
            with self.subTest(command=cmd):  # a wholly quoted word is data behind a data command
                self.assert_silent(self.pre("Bash", cmd))

    def test_r1_p2_a_built_part_that_is_empty_is_tried_too(self):
        """Round 1 P2-1: `*` never matches a leading dot, and `$E` may be empty."""
        for cmd in ("cat ${E}.env", "cat $E.env", "cat config/${E}.env"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r1_p2_a_quote_next_to_a_brace_is_expanded(self):
        for cmd in ("cat .claude/sens''{itive,x}-paths.txt", "cat .claude/sens''itive-paths.tx{t,u}"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r1_p2_a_word_that_is_only_variables_stays_silent_next_to_a_folder(self):
        """Round 1 P2-3: with an `infra/` folder a `*` matches, so dropping the guard would ask."""
        for cmd in ('cat "$F"', "cat $F", "echo $HOME", "ls $D/$E"):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_r2_p1_a_variable_after_an_equals_or_colon_is_not_a_bare_star(self):
        """Round 2 P1-A: `TOKEN_PATTERN` splits at `=` and `:`, so a piece of only `*` or `./*` must not
        be globbed against the project root (it would find `infra/`)."""
        for cmd in ('export PATH="$HOME/bin:$PATH"', 'FOO="$BAR" make', 'X="$A:$B"', 'make build OUT="$DIR"',
                    'curl --output="$F" http://x', "cmd --opt=$V", 'docker run -v "$PWD":/app img',
                    'cat ./"$F"', "ls ./$D", "./$BIN --help", 'rm -rf ./"$TMP"'):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_r2_p2_a_wholly_quoted_word_with_a_built_part_is_read(self):
        """Round 2 P2-B: quotes round a whole word must not skip it when a built part is in it."""
        for cmd in ('cat ".claude/sens${x}itive-paths.txt"', 'cat ".claude/sens$xitive-paths.txt"',
                    'cat "$E.env"', 'cat "${E}.env"', 'cat "config/${E}.env"',
                    'grep KEY ".claude/sens${x}itive-paths.txt"'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r3_p2_a_piece_with_no_letter_or_digit_is_no_name(self):
        """Round 3 P2-1: `*-*`, `*_*` and `*?` are not names; they would match `prod-values.yaml`."""
        for cmd in ('docker build -t "$name-$ver" .', 'git commit -m "$a-$b"', 'echo "${a}_${b}"', 'ls "$D"?'):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_r3_p2_a_backslash_newline_inside_a_word_is_dropped(self):
        for cmd in ("cat .e\\\nnv", "cat .claude/sens\\\nitive-paths.txt"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r3_p3_at_and_star_are_built_parts_and_single_quotes_are_not(self):
        self.assert_ask(self.pre("Bash", 'cat .claude/sens"$@"itive-paths.txt'))
        for cmd in ("echo '$HOME/.env'", "grep -n '$HOME/.env' README.md"):
            with self.subTest(command=cmd):  # a `$` inside single quotes is a letter, not a variable
                self.assert_silent(self.pre("Bash", cmd))

    def test_r4_p2_a_dollar_inside_a_spaced_quoted_span_stays_data(self):
        for cmd in ('echo "Using $HOME/.env"', 'echo "see $x.env file"', 'grep -n "found $x.env here" README.md',
                    'echo "it\'s $HOME/.env"'):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_r4_p2_a_dot_led_glob_split_by_a_quote_or_variable_is_a_name(self):
        for cmd in ("cat .??''?", 'cat .?""??', "cat .*$x", "cat .?$x??", "cat .??${x}"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r5_p2_an_escaped_quote_in_a_spaced_span_does_not_hide_the_next_word(self):
        for cmd in ('cat "a \\" b" .e"n"v', 'cat "a\\" b" .e"n"v', 'cat "a \\"b" .e"n"v "c d"'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r5_p2_a_dot_led_glob_after_a_dot_slash_is_a_name(self):
        for cmd in ("cat ./.??''?", 'cat ./.?"?"?', "cat ./.*$x", "cat $PWD/.??''?"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r6_p2_a_quoted_command_substitution_is_code_not_a_message(self):
        for cmd in ('cat "$(cat .e\'\'nv)"', 'echo "$(cat .e"n"v) done"', 'x="$(cat .e\'\'nv)"',
                    'git commit -m "$(cat .e\'\'nv) a"', 'cat "`cat .e\'\'nv`"',
                    'echo "$(cat .claude/sens\'\'itive-paths.txt) y"'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))
        self.assert_silent(self.pre("Bash", 'echo "today is $(date +%F) and $x.env"'.replace("$x.env", "ok")))

    def test_r7_p2_a_spaced_span_behind_a_shell_is_code_not_a_message(self):
        for cmd in ('bash -c "cat .e\'\'nv"', "sh -c 'cat .e\"\"nv'", "bash -c 'cat .claude/sens\"\"itive-paths.txt'",
                    'eval "cat .e\'\'nv"', 'ssh h "cat .e\'\'nv"', 'xargs -I{} sh -c "cat .e\'\'nv"'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_r4_p3_bang_is_a_built_part(self):
        for cmd in ("cat .env$!", "cat .claude/sens$!itive-paths.txt"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))

    def test_ac2_a_dollar_quote_word_is_dequoted_in_the_folder_rule(self):
        for cmd in ("find config -d$'elete'", 'find config -d$"elete"'):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))
        self.assert_silent(self.pre("Bash", "find config -name x"))

    def test_ac3_a_built_word_next_to_literal_text_is_a_glob(self):
        for cmd in ("cat .claude/sens${x}itive-paths.txt", "cat .claude/sens$xitive-paths.txt"):
            with self.subTest(command=cmd):
                self.assert_ask(self.pre("Bash", cmd))
        for cmd in ('cat "$F"', "echo $HOME", "echo ${x}"):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))

    def test_ac4_a_quoted_span_with_a_space_stays_data(self):
        for cmd in ('echo "see .env file"', "echo 'a b .env c'"):
            with self.subTest(command=cmd):
                self.assert_silent(self.pre("Bash", cmd))


class AdminPins(t371.AdminApproval):
    def test_ac5_find_exec_or_ok_without_braces_is_a_write(self):
        for cmd in ("find config/.env -exec rm x ;", "find config/.env -ok rm x ;"):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(len(self.log_lines()), 2)

    def test_sec1_an_ansi_c_escape_in_a_word_is_not_a_read(self):
        """Security review: `$'\\x65lete'` is `elete` to the shell, so `-d$'\\x65lete'` is `-delete`;
        dropping its `$` and backslash made the call look read-only, so it was not logged."""
        for cmd in ("cat config/.env && find build -d$'\\x65lete'", "cat config/.env && find build -d$\"\\x65lete\""):
            with self.subTest(command=cmd):
                self.assert_approved(self.pre("Bash", cmd))
        self.assertEqual(len(self.log_lines()), 2)

    def test_ac5_an_empty_command_is_not_a_read(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hook", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "pre_tool_sensitive_path.py"))
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        for command in ("", "   ", None):
            with self.subTest(command=command):
                self.assertFalse(hook.only_reads("Bash", {"command": command}))

    def test_ac5_the_note_asks_for_a_final_report_line(self):
        out = self.assert_approved(self.pre("Write", ".env"))
        self.assertIn("final report", str(out))


class ListHeader(unittest.TestCase):
    def test_ac6_line_two_names_the_admin_exception(self):
        with open(os.path.join(REPO_ROOT, ".claude", "sensitive-paths.txt"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        header = " ".join(lines[:4])
        self.assertIn("[admin]", header)
        self.assertIn("T371", header)


if __name__ == "__main__":
    unittest.main()
