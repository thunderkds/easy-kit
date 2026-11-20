#!/usr/bin/env python3
"""T342 — a glob inside a quoted span is not a path when the segment command neither globs nor runs a shell.

The outer shell does not expand quoted text (bash(1) QUOTING), so `sed 's/ - .*//'` names no
file. Before T342 `command_tokens` expanded the kept `sed` script's `.*` against the project
root, found `.claude`, and with a `cd` in the command rule S2 asked. That stopped `[admin]` runs.

Debate decision 3 (tasks/TASK_REVIEW_T342.md): the default stays *expand*. Only a span whose
segment command is on a short allowlist (grep, egrep, fgrep, rg, sed without an `e` command, sort,
cut, tr) is not expanded; every other quoted span still is.

Each test drives the real hook through stdin/stdout, like test_pre_tool_sensitive_path.py.

Run with: python3 -m pytest .claude/hooks/tests/test_t342_quoted_glob.py -q
"""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_pre_tool_sensitive_path as base  # noqa: E402

HOOK, HOOKS_DIR = base.HOOK, base.HOOKS_DIR

# The rule under test, and how AC 7 reverts it: every token is expanded again.
RULE_ANCHOR = "if GLOB_CHARS.search(masked[start:end]):"
RULE_REVERT = "if GLOB_CHARS.search(text[start:end]):"


class QuotedGlobTest(base.SensitivePathHookTest):
    def setUp(self):
        super().setUp()
        # The temp project root holds a `.claude/` folder (from the parent fixture) and a `.env`.
        for name in (".env", ".env.prod"):
            open(os.path.join(self.project, name), "w").close()
        os.makedirs(os.path.join(self.project, ".claude", "state"))
        open(os.path.join(self.project, ".claude", "state", "x"), "w").close()
        self.wt = tempfile.mkdtemp(prefix="t342-wt-")
        self.sp = tempfile.mkdtemp(prefix="t342-sp-")
        self.addCleanup(shutil.rmtree, self.wt, True)
        self.addCleanup(shutil.rmtree, self.sp, True)

    def session_commands(self):
        """The two test commands of the T341 session, worktree and scratchpad pointed at temp dirs."""
        wt, sp = self.wt, self.sp
        return [
            f'cd {wt}; uv run --with pytest python -m pytest .claude/hooks/tests tests -q '
            f'-p no:cacheprovider -n0 2>/dev/null | grep -E "^FAILED|passed|failed" '
            f"| sed 's/ - .*//' > {sp}/branch.txt; tail -1 {sp}/branch.txt",
            f"cd {wt}; uv run --with pytest python -m pytest .claude/hooks/tests tests -q "
            f"-p no:cacheprovider -n0 > {sp}/branch_full.txt 2>&1; tail -1 {sp}/branch_full.txt; "
            f"grep ^FAILED {sp}/branch_full.txt | sed 's/ - .*//' | sort > {sp}/branch_failed.txt",
        ]

    ALLOWLISTED_SPANS = [
        "sed 's/a.*//' f",
        "cd d; grep -E '.*' f",
        'cd d && sed "s/.*//" f',
        'cd d && sed "s/ .*//" f',
        "cd d; pytest x | sed 's/ - .*//' | sort",
        "cd d; sed -n 's/^.*: //p' f | cut -d' ' -f1 | tr '.*' '__' | sort -t'*' -k1",
        "cd d; /usr/bin/sed 's/x.*//' f",
    ]

    # --- AC 1: the T341 session commands are silent --------------------------

    def test_ac1_t341_session_commands_are_silent(self):
        for command in self.session_commands():
            with self.subTest(command=command):
                self.assert_silent(self.bash(command))

    # --- AC 2: a glob in a quoted span of an allowlisted command is not expanded

    def test_ac2_glob_in_allowlisted_command_span_is_silent(self):
        for command in self.ALLOWLISTED_SPANS:
            with self.subTest(command=command):
                self.assert_silent(self.bash(command))

    # --- AC 3: every other quoted span still expands --------------------------

    def test_ac3_glob_in_any_other_quoted_span_asks(self):
        cases = [
            ("bash -c 'cat .env*'", ".env"),
            ("cd d; bash -c 'rm -rf .c*'", ".claude"),
            ('eval "cat .env*"', ".env"),
            ('cd d; su u -c "cat .cl*/state/x"', ".claude/state"),
            ("cd d; xargs sh -c 'rm .c*'", ".claude"),
            ("cd d; git add '.cl*'", ".claude"),
            ("cd d; sed 'e cat .cl*' f", ".claude"),
            ("cd d; awk '{system(\"rm .c*\")}' f", ".claude"),
        ]
        for command, needle in cases:
            with self.subTest(command=command):
                self.assert_ask(self.bash(command), needle)

    def test_ac3_allowlisted_command_with_an_executing_span_asks(self):
        cases = [
            ("cd d; sed 's/x/ls .cl* /e' f", ".claude"),     # sed `s///e` flag
            ("cd d; sed '1e rm .c*' f", ".claude"),           # sed `e` command after an address
            ("cd d; sed 's/x/rm .c* /ge' f", ".claude"),      # sed `s///e` flag after `g`
            ("cd d; sed 's/x/rm .c* /eg' f", ".claude"),      # sed `s///e` flag before `g`
            ("cd d; sed 's/x/rm .c* /3ew o' f", ".claude"),   # sed `s///e` flag inside `3ew`
            ("cd d; sed 'x;$e rm .c*' f", ".claude"),         # sed `e` command after `$`
            ('cd d; grep "$(ls .c*)" f', ".claude"),         # command substitution runs
            ("cd d; sudo sed 's/ .c* //' f", ".claude"),      # wrapper before the command word
            ("cd d; find . -name '.c*' -delete", ".claude"),  # find is not on the list
            # Stage 4 P1: `\"` is a literal quote in the shell, so the glob after it is unquoted.
            (r'cd d; sed \" .c* \" f', ".claude"),
            (r'cd d; sed -i -e "s/a/b/" \" .cl* \"', ".claude"),
        ]
        for command, needle in cases:
            with self.subTest(command=command):
                self.assert_ask(self.bash(command), needle)

    # --- AC 4: unquoted globs keep today's behaviour -------------------------

    def test_ac4_unquoted_glob_still_asks(self):
        cases = [
            ("cat .env*", ".env.prod"),
            ("cd d; rm -rf .c*", ".claude"),
            ("cd d; rm -rf .claude/sta*", ".claude/state"),
        ]
        for command, needle in cases:
            with self.subTest(command=command):
                self.assert_ask(self.bash(command), needle)

    def test_ac4_mixed_word_with_unquoted_glob_after_a_quoted_span_asks(self):
        # `'x' .env*`: the glob is outside the quotes, so the shell expands it.
        self.assert_ask(self.bash("sed 's/a.*//' .env*"), ".env")

    def test_unterminated_quote_tail_is_still_expanded(self):
        self.assert_ask(self.bash("cat .env* 'open"), ".env")

    # --- AC 5: literal sensitive paths in a kept quoted span still ask -------

    def test_ac5_literal_sensitive_path_still_asks(self):
        cases = [
            ("sed -i 's/x/y/' .env", ".env"),
            ("sed 'w .claude/state/x' f", ".claude/state"),
            ("cd d; sed 's/x/y/' .claude/state/a", ".claude/state"),
        ]
        for command, needle in cases:
            with self.subTest(command=command):
                self.assert_ask(self.bash(command), needle)

    # --- AC 7: anti-vacuity --------------------------------------------------

    def _rule_reverted(self):
        with open(HOOK) as f:
            source = f.read()
        self.assertIn(RULE_ANCHOR, source, "mutation anchor drifted — update the control")
        sandbox = tempfile.mkdtemp(prefix="t342-mutant-")
        self.addCleanup(shutil.rmtree, sandbox, True)
        shutil.copytree(os.path.join(HOOKS_DIR, "lib"), os.path.join(sandbox, "lib"))
        path = os.path.join(sandbox, "pre_tool_sensitive_path.py")
        with open(path, "w") as f:
            f.write(source.replace(RULE_ANCHOR, RULE_REVERT))
        return path

    def test_ac7_reverting_the_rule_turns_ac1_red(self):
        mutant = self._rule_reverted()
        for command in self.session_commands():
            with self.subTest(command=command):
                proc = self.bash(command, hook=mutant)
                self.assertNotEqual(proc.stdout.strip(), "", "mutant should ask on AC 1 (RED)")

    def test_ac7_reverting_the_rule_turns_ac2_red(self):
        mutant = self._rule_reverted()
        # Only the spans that tokenize to a bare glob (`.*//`, `.*`) were red before T342;
        # `s/a.*//` is one token that globs to nothing, silent with or without the rule.
        for command in ("cd d; pytest x | sed 's/ - .*//' | sort",
                        "cd d; sed -n 's/^.*: //p' f | cut -d' ' -f1 | tr '.*' '__' | sort -t'*' -k1",
                        'cd d && sed "s/ .*//" f'):
            with self.subTest(command=command):
                proc = self.bash(command, hook=mutant)
                self.assertNotEqual(proc.stdout.strip(), "", "mutant should ask on AC 2 (RED)")


# The parent's tests run in their own module; do not run them a second time here.
for _name in [n for n in dir(base.SensitivePathHookTest) if n.startswith("test_")]:
    if _name not in QuotedGlobTest.__dict__:
        setattr(QuotedGlobTest, _name, None)
del _name


if __name__ == "__main__":
    unittest.main()
