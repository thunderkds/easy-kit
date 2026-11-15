#!/usr/bin/env python3
"""T314 backslash-key locked oracle (security-review finding, Medium, confirmed by probe).

Written by qa-expert BEFORE the fix (Pillar 3). The implementer may not edit it.

The finding: `file_key()` and `written_key()` in `pre_tool_sensitive_path.py` turn `\\` into
`/` and apply `normpath` before they build the approval key. On Linux `\\` is a literal
file-name character, so after `infra/main.tf` is approved through a Write, a Write of
`<root>/infra/evil\\..\\main.tf` is silent, and the OS creates a NEW literal file in `infra/`.

Locked expectations:
- A Write of `<root>/infra/evil\\..\\main.tf` after `infra/main.tf` is approved asks.
- A Write of `app/secrets/new\\..\\db.yml` after `app/secrets/db.yml` is approved asks.
- A Write and an Edit of `infra\\main.tf` after `infra/main.tf` is approved ask.
- Post never records a key containing `\\`, nor a key that differs from the realpath of
  the path as given (root-relative under the root, else absolute).
- Control: the approved exact path stays silent (Write and Edit).
- Local mode (no board.json) is unchanged: same results as on `main`.

Same harness as `test_t314_security_round.py` (`FixRoundTest`: temp project, online board,
Pre -> Post with one `tool_use_id`, `permission_mode` `default`).

Run with:
    python3 -m pytest .claude/hooks/tests/test_t314_backslash_key.py -q -p no:cacheprovider
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_t314_fix_round import FixRoundTest  # noqa: E402

BS = "\\"
TASK = "T314"
INFRA = "infra/main.tf"
SECRETS = "app/secrets/db.yml"
INFRA_EVIL_REL = "infra/evil" + BS + ".." + BS + "main.tf"
SECRETS_EVIL_REL = "app/secrets/new" + BS + ".." + BS + "db.yml"
INFRA_BS_REL = "infra" + BS + "main.tf"

LOCAL_GUIDE = f"""# TASK_GUIDE — {TASK}: fixture

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `{INFRA}` | edit |

## Files Must NOT Touch
"""


class BackslashKeyTest(FixRoundTest):
    def setUp(self):
        super().setUp()
        self.write_file(INFRA, "x")
        self.write_file(SECRETS, "x")

    def write_file(self, relpath, content="x"):
        path = os.path.join(self.project, *relpath.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    def abs_path(self, relpath):
        # Only `/` is a separator; a `\\` stays inside the file-name component.
        return os.path.join(self.project, *relpath.split("/"))

    def realpath_key(self, path, cwd=None):
        """The key the oracle allows: realpath of the path AS GIVEN (no `\\` rewrite)."""
        real = os.path.realpath(os.path.join(cwd or self.project, path))
        rel = os.path.relpath(real, os.path.realpath(self.project))
        if rel == ".." or rel.startswith(".." + os.sep):
            return real
        return rel

    def approve_infra(self):
        self.approve("Write", self.abs_path(INFRA))
        self.assertIn(INFRA, self.approved_keys(TASK), "setup: `infra/main.tf` approved via Write")

    def approve_secrets(self):
        self.approve("Write", SECRETS)
        self.assertIn(SECRETS, self.approved_keys(TASK), "setup: `app/secrets/db.yml` approved")

    def assert_keys_sound(self, given_paths):
        allowed = {self.realpath_key(p) for p in given_paths}
        for key in self.all_approved_keys():
            with self.subTest(key=key):
                self.assertNotIn(BS, key, "no recorded key may contain a backslash")
                self.assertIn(key, allowed,
                              "a recorded key must equal the realpath of a path as given")


class EvilDotDotWritesAsk(BackslashKeyTest):
    """The two probe cases: a literal `x\\..\\name` file is a new file, never the approved one."""

    def test_infra_evil_dotdot_write_asks_after_approval(self):
        self.approve_infra()
        self.assert_ask(self.pre("Write", self.abs_path(INFRA_EVIL_REL)))

    def test_secrets_new_dotdot_write_asks_after_approval(self):
        self.approve_secrets()
        self.assert_ask(self.pre("Write", SECRETS_EVIL_REL))

    def test_evil_path_is_a_distinct_literal_file_on_this_os(self):
        # Guards the premise: on this OS `\\` is a name character, so the evil Write
        # creates a new file, not `infra/main.tf`. Skipped where `\\` is a separator.
        if os.sep == BS or (os.altsep or "") == BS:
            self.skipTest("backslash is a path separator on this OS")
        evil = self.abs_path(INFRA_EVIL_REL)
        with open(evil, "w") as f:
            f.write("z")
        self.assertEqual(sorted(os.listdir(os.path.join(self.project, "infra"))),
                         sorted(["main.tf", "evil" + BS + ".." + BS + "main.tf"]))
        with open(self.abs_path(INFRA)) as f:
            self.assertEqual(f.read(), "x")


class BackslashSeparatorAsks(BackslashKeyTest):
    """`infra\\main.tf` is a different file from `infra/main.tf` on Linux."""

    def test_write_of_backslash_form_asks_after_approval(self):
        self.approve_infra()
        self.assert_ask(self.pre("Write", INFRA_BS_REL))

    def test_edit_of_backslash_form_asks_after_approval(self):
        self.approve_infra()
        self.assert_ask(self.pre("Edit", INFRA_BS_REL))

    def test_absolute_backslash_form_asks_after_approval(self):
        self.approve_infra()
        self.assert_ask(self.pre("Write", self.abs_path(INFRA_BS_REL)))
        self.assert_ask(self.pre("Edit", self.abs_path(INFRA_BS_REL)))


class PostRecordsOnlyRealpathKeys(BackslashKeyTest):
    """Post never records a key with `\\`, nor a key other than the realpath as given."""

    def test_approving_backslash_paths_records_no_collapsed_key(self):
        given = [self.abs_path(INFRA_EVIL_REL), SECRETS_EVIL_REL, INFRA_BS_REL]
        for tool, path in (("Write", given[0]), ("Write", given[1]), ("Edit", given[2])):
            with self.subTest(tool=tool, path=path):
                self.approve(tool, path)  # Pre asks (no approvals yet), the user says yes
        self.assert_keys_sound(given)
        self.assertNotIn(INFRA, self.all_approved_keys(),
                         "approving `infra/evil\\..\\main.tf` must not approve `infra/main.tf`")
        self.assertNotIn(SECRETS, self.all_approved_keys(),
                         "approving `new\\..\\db.yml` must not approve `app/secrets/db.yml`")

    def test_exact_paths_stay_asking_after_backslash_approvals(self):
        self.approve("Write", self.abs_path(INFRA_EVIL_REL))
        self.approve("Edit", INFRA_BS_REL)
        self.approve("Write", SECRETS_EVIL_REL)
        self.assert_ask(self.pre("Write", INFRA), INFRA)
        self.assert_ask(self.pre("Edit", SECRETS), SECRETS)

    def test_mixed_session_keys_are_all_realpath_keys(self):
        given = [self.abs_path(INFRA), SECRETS, self.abs_path(INFRA_EVIL_REL),
                 SECRETS_EVIL_REL, INFRA_BS_REL]
        self.approve_infra()
        self.approve_secrets()
        for tool, path in (("Write", given[2]), ("Write", given[3]),
                           ("Write", given[4]), ("Edit", given[4])):
            tid = self.new_id()
            self.pre(tool, path, tool_use_id=tid)
            self.post(tool, path, tid)  # whatever Pre did, Post must record nothing unsound
        self.assert_keys_sound(given)
        self.assertEqual(sorted(self.all_approved_keys()), sorted([INFRA, SECRETS]))


class ApprovedExactPathControl(BackslashKeyTest):
    """Control: the fix must not break the approve-once path for the exact file."""

    def test_approved_infra_stays_silent(self):
        self.approve_infra()
        self.assert_silent(self.pre("Write", self.abs_path(INFRA)))
        self.assert_silent(self.pre("Write", INFRA))
        self.assert_silent(self.pre("Edit", INFRA))

    def test_approved_secrets_stays_silent(self):
        self.approve_secrets()
        self.assert_silent(self.pre("Write", SECRETS))
        self.assert_silent(self.pre("Edit", self.abs_path(SECRETS)))


class LocalModeUnchanged(BackslashKeyTest):
    """Local board mode: results equal `main` (checked against `main`'s hook when locked)."""

    online = False

    def test_local_no_guide_backslash_paths_ask(self):
        for tool, path in (("Write", self.abs_path(INFRA_EVIL_REL)), ("Write", SECRETS_EVIL_REL),
                           ("Write", INFRA_BS_REL), ("Edit", INFRA_BS_REL), ("Write", INFRA)):
            with self.subTest(tool=tool, path=path):
                self.assert_ask(self.pre(tool, path))

    def test_local_recorder_writes_nothing(self):
        tid = self.new_id()
        self.assert_ask(self.pre("Write", INFRA_BS_REL, tool_use_id=tid))
        self.post("Write", INFRA_BS_REL, tid)
        self.assertFalse(os.path.exists(self.approvals),
                         "local mode: the recorder must not create the approval file")

    def test_local_predicted_guide_unchanged(self):
        # As on `main`: the predicted-path match normalises `\\` (path_forms), so the
        # predicted file and its backslash forms are silent; an unpredicted secret asks.
        with open(os.path.join(self.project, "tasks", f"TASK_GUIDE_{TASK}.md"), "w") as f:
            f.write(LOCAL_GUIDE)
        self.assert_silent(self.pre("Write", INFRA))
        self.assert_silent(self.pre("Edit", INFRA_BS_REL))
        self.assert_silent(self.pre("Write", self.abs_path(INFRA_EVIL_REL)))
        self.assert_ask(self.pre("Write", SECRETS_EVIL_REL))
        self.assertFalse(os.path.exists(self.approvals))


if __name__ == "__main__":
    unittest.main()
