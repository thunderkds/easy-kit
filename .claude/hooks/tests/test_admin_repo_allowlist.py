#!/usr/bin/env python3
"""T295 — the `[admin]` gate reads the repository as an allowlist (`tasks/TASK_GUIDE_T295.md`,
AC 1-8; finding P1-2 of `tasks/GATE_HUNT_2026-11-08.md`).

An `[admin]` merge or push is allowed only when every repo/worktree config key is on a short
allowlist of keys that cannot run code or reach another host, no hook file is executable (a
`.sample` file is not a hook), no attributes line holds `merge=`, `filter=` or `diff=`, and no
other git command is chained with the one merge or push (`cd <dir> &&` stays).

Every repo here is a real throwaway git repo built by the `gate` fixture. Run with:
python3 -m pytest .claude/hooks/tests/test_admin_repo_allowlist.py -v
"""
import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_admin_tag import (  # noqa: E402
    MERGE, NO_FF, PUSH, G, admin_session, admin_tag_section, auto_verified, common_dir, gate, git,
    kanban, legit, merge_gate, publish, reason, session, write)
from test_merge_gate_t210 import GIT_ENV  # noqa: E402

assert gate  # the fixture, imported for pytest

BRANCH_MERGE = MERGE + " feat/t900-x"


def merge_ready(gate, tmp_path):
    """A verified T900 branch and an `[admin]` request: `git merge feat/t900-x` in `fx.main` is
    allowed (the control every test below asserts before it plants anything)."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    return fx, session(tmp_path, fx, "do it [admin]")


def append_config(repo, text):
    with open(os.path.join(common_dir(repo), "config"), "a", encoding="utf-8") as f:
        f.write(text)


# ── AC 1 — the allowlist is one constant with a reason per entry ────────────────────────────
FINDING_KEYS = (("merge", True, "driver"), ("filter", True, "smudge"), ("filter", True, "clean"),
                ("filter", True, "process"), ("diff", True, "textconv"), ("diff", False, "external"),
                ("gpg", False, "program"), ("commit", False, "gpgsign"), ("core", False, "editor"),
                ("core", False, "askpass"), ("core", False, "pager"), ("sequence", False, "editor"),
                ("credential", False, "helper"), ("http", False, "proxy"),
                ("http", False, "sslcainfo"), ("submodule", True, "update"),
                ("merge", False, "defaulttoupstream"))


def test_ac1_the_allowlist_is_one_constant_with_a_reason_per_key():
    allowed = merge_gate.ADMIN_ALLOWED_CONFIG
    assert allowed, "the allowlist is empty"
    for key, why in allowed.items():
        assert isinstance(why, str) and len(why.split()) >= 3, (key, why)
    for key in FINDING_KEYS:
        assert key not in allowed, f"{key} is a key the finding names"
    assert len(allowed) <= 25, "the allowlist is meant to stay short"


# AC 1: every key of the starting list (and the added ones, each with a reason in the constant)
# is allowed with a plausible value.
ALLOWED_KEYS = [
    ("core.repositoryformatversion", "0"), ("core.filemode", "false"), ("core.bare", "false"),
    ("core.logallrefupdates", "true"), ("core.ignorecase", "true"),
    ("core.precomposeunicode", "true"), ("core.autocrlf", "input"), ("core.safecrlf", "warn"),
    ("core.symlinks", "false"),
    ("remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*"),
    ("remote.upstream.url", "https://example.com/team/repo.git"),
    ("remote.upstream.fetch", "+refs/heads/*:refs/remotes/upstream/*"),
    ("branch.feat/t900-x.remote", "origin"), ("branch.feat/t900-x.merge", "refs/heads/feat/t900-x"),
    ("branch.main.vscode-merge-base", "origin/main"), ("pull.rebase", "true"),
    ("push.default", "simple"), ("push.default", "current"),
    ("user.name", "A Person"), ("user.email", "a@example.com"),
    ("extensions.worktreeConfig", "true"),
]


@pytest.mark.parametrize("key,value", ALLOWED_KEYS)
@pytest.mark.parametrize("command", ["merge", "push"])
def test_ac1_each_allowlisted_key_is_allowed(gate, tmp_path, key, value, command):
    fx, path = merge_ready(gate, tmp_path)
    cmd, cwd = (BRANCH_MERGE, fx.main) if command == "merge" else (PUSH + " origin feat/t900-x", fx.wt)
    assert reason(cmd, cwd, path) is None  # control
    git(fx.main, "config", key, value)
    assert reason(cmd, cwd, path) is None, key


def test_ac1_remote_origin_url_equal_to_the_fetch_url_is_allowed(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    url = git(fx.main, "remote", "get-url", "origin")
    git(fx.main, "config", "remote.origin.url", url)
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is None


@pytest.mark.parametrize("url", ["ext::sh -c touch% /tmp/x", "fd::3", "-oProxyCommand=evil",
                                 "ssh://-oProxyCommand=evil/x"])
def test_ac1_a_remote_url_that_runs_a_helper_or_an_option_is_refused(gate, tmp_path, url):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "remote.upstream.url", url)
    text = reason(BRANCH_MERGE, fx.main, path)
    assert text is not None and "remote.upstream.url" in text, text


@pytest.mark.parametrize("value", ["matching", "upstream", "nothing", "anything"])
def test_ac1_a_push_default_other_than_simple_or_current_is_refused(gate, tmp_path, value):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "push.default", value)
    assert reason(BRANCH_MERGE, fx.main, path) is not None


@pytest.mark.parametrize("value", ["interactive", "merges", "-x"])
def test_ac1_a_pull_rebase_other_than_a_boolean_is_refused(gate, tmp_path, value):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "pull.rebase", value)
    assert reason(BRANCH_MERGE, fx.main, path) is not None


# ── AC 2 — planted keys block, and the message names the key ────────────────────────────────
PLANTED = [
    ("merge.evil.driver", "/bin/true %A"), ("filter.evil.smudge", "/bin/true"),
    ("filter.evil.clean", "/bin/true"), ("filter.evil.process", "/bin/true"),
    ("filter.evil.required", "true"), ("diff.evil.textconv", "/bin/true"),
    ("diff.evil.command", "/bin/true"), ("diff.external", "/bin/true"),
    ("gpg.program", "/bin/true"), ("gpg.ssh.program", "/bin/true"), ("commit.gpgsign", "true"),
    ("core.editor", "/bin/true"), ("core.askPass", "/bin/true"), ("core.pager", "/bin/true"),
    ("sequence.editor", "/bin/true"), ("credential.helper", "/abs/prog"),
    ("credential.helper", "cache"), ("credential.helper", "store"), ("http.proxy", "http://x"),
    ("http.sslCAInfo", "/tmp/ca.pem"), ("submodule.evil.update", "!/bin/true"),
    ("merge.defaultToUpstream", "true"), ("merge.evil.name", "x"), ("core.attributesFile", "/tmp/a"),
    ("core.excludesFile", "/tmp/a"), ("core.worktree", "/tmp"), ("core.fsmonitor", "false"),
    ("core.untrackedCache", "true"), ("alias.st", "status"), ("alias.pp", "!sh -c x"),
    ("diff.evil.binary", "true"), ("merge.tool", "evil"), ("mergetool.evil.cmd", "/bin/true"),
    ("difftool.evil.cmd", "/bin/true"), ("rebase.autoSquash", "true"), ("gc.auto", "1"),
    ("uploadpack.packObjectsHook", "/bin/true"), ("protocol.ext.allow", "always"),
    ("core.hookspath", "/tmp/hooks"), ("branch.main.pushRemote", "origin"),
    ("remote.pushDefault", "origin"), ("init.templateDir", "/tmp/t"), ("trailer.evil.cmd", "x"),
    ("pager.log", "/bin/true"), ("log.showSignature", "true"), ("merge.verifySignatures", "true"),
    # every key T284 already refused:
    ("remote.origin.uploadpack", "/bin/true"), ("core.sshCommand", "/bin/true"),
    ("core.gitProxy", "/bin/true"), ("include.path", "/tmp/nothing"),
    ("includeIf.gitdir:/x/.path", "/tmp/nothing"), ("transfer.hideRefs", "refs/heads"),
    ("remote.origin.proxy", "http://x"), ("receive.denyDeletes", "true"),
    ("remote.origin.vcs", "x"), ("push.recurseSubmodules", "on-demand"),
    ("push.pushOption", "x"), ("push.followTags", "true"), ("remote.origin.pushurl", "https://a.example/x"),
    ("remote.origin.receivepack", "sh -c evil"), ("url.https://a.example/.insteadOf", "/nowhere"),
    ("url.https://a.example/.pushInsteadOf", "/"), ("remote.origin.push", "refs/heads/*:refs/heads/x"),
    ("remote.origin.mirror", "true"),
]


@pytest.mark.parametrize("key,value", PLANTED)
@pytest.mark.parametrize("command", ["merge", "push"])
def test_ac2_a_planted_key_blocks_an_admin_merge_or_push(gate, tmp_path, key, value, command):
    fx, path = merge_ready(gate, tmp_path)
    cmd, cwd = (BRANCH_MERGE, fx.main) if command == "merge" else (PUSH + " origin feat/t900-x", fx.wt)
    assert reason(cmd, cwd, path) is None  # control: the same command in the repo before the plant
    git(fx.main, "config", key, value)
    text = reason(cmd, cwd, path)
    assert text is not None and key.lower() in text.lower(), (key, text)


@pytest.mark.parametrize("planted", [
    '[Core]\n\tSshCommand = /bin/true\n', '[CORE]\n\tSSHCOMMAND = /bin/true\n',
    '[Remote "Origin"]\n\tPushURL = https://a.example/x\n', '[Merge "evil"]\n\tDriver = /bin/true\n',
    '[MERGE "Evil"]\n\tdriver = /bin/true\n', '[Include]\n\tPath = /tmp/nothing\n',
    '[core]\n\tfilemode = true\n[core]\n\teditor = /bin/true\n',
], ids=["sshcommand", "SSHCOMMAND", "Remote-PushURL", "Merge-Driver", "MERGE-Evil", "Include",
        "key-set-twice"])
def test_ac2_mixed_case_section_and_key_names_are_read_like_git_reads_them(gate, tmp_path, planted):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(BRANCH_MERGE, fx.main, path) is None
    append_config(fx.main, planted)
    assert reason(BRANCH_MERGE, fx.main, path) is not None


def test_ac2_a_key_set_twice_one_of_them_not_allowed_blocks(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "--add", "user.name", "A")
    git(fx.main, "config", "--add", "user.name", "B")
    assert reason(BRANCH_MERGE, fx.main, path) is None  # both values are allowed
    git(fx.main, "config", "--add", "core.editor", "/bin/true")
    assert reason(BRANCH_MERGE, fx.main, path) is not None


def test_ac2_a_value_with_a_newline_is_read_as_one_entry(gate, tmp_path):
    """`git config --list -z` ends an entry at NUL, so a newline inside a value is not a new key."""
    fx, path = merge_ready(gate, tmp_path)
    append_config(fx.main, '[user]\n\tname = "line one\\nline two"\n')
    assert reason(BRANCH_MERGE, fx.main, path) is None
    append_config(fx.main, '[user]\n\tname = "x\\nlocal\\tcore.editor=/bin/true"\n[core]\n\teditor = y\n')
    assert reason(BRANCH_MERGE, fx.main, path) is not None


def test_ac2_the_per_worktree_config_is_read_too(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "extensions.worktreeConfig", "true")
    assert reason(BRANCH_MERGE, fx.main, path) is None and \
        reason(PUSH + " origin feat/t900-x", fx.wt, path) is None  # control
    git(fx.wt, "config", "--worktree", "merge.evil.driver", "/bin/true")
    text = reason(PUSH + " origin feat/t900-x", fx.wt, path)
    assert text is not None and "merge.evil.driver" in text, text
    assert reason(BRANCH_MERGE, fx.main, path) is None  # the main checkout's own config is clean


def test_ac2_an_allowed_key_in_the_worktree_config_stays_allowed(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.main, "config", "extensions.worktreeConfig", "true")
    git(fx.wt, "config", "--worktree", "core.autocrlf", "input")
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is None


def test_ac2_user_global_config_stays_trusted_and_unread(gate, tmp_path, monkeypatch):
    fx, path = merge_ready(gate, tmp_path)
    glob = os.path.join(fx.root, "global.gitconfig")
    write(glob, "[core]\n\teditor = /bin/true\n[merge \"x\"]\n\tdriver = /bin/true\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", glob)
    assert reason(BRANCH_MERGE, fx.main, path) is None


def test_ac2_an_unreadable_config_blocks(gate, tmp_path, monkeypatch):
    fx, path = merge_ready(gate, tmp_path)
    monkeypatch.setattr(merge_gate, "_git", lambda *a, **k: None)
    assert reason(BRANCH_MERGE, fx.main, path) is not None


# ── AC 3 — hooks: any executable file that is not `.sample` blocks ──────────────────────────
GIT_HOOKS = ("applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
             "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout",
             "post-merge", "pre-push", "pre-receive", "update", "proc-receive", "post-receive",
             "post-update", "reference-transaction", "push-to-checkout", "pre-auto-gc",
             "post-rewrite", "sendemail-validate", "fsmonitor-watchman", "p4-changelist",
             "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit", "post-index-change")


def plant_hook(repo, name, mode=0o755):
    target = os.path.join(common_dir(repo), "hooks", name)
    write(target, "#!/bin/sh\nexit 0\n")
    os.chmod(target, mode)
    return target


@pytest.mark.parametrize("hook", GIT_HOOKS + ("my-own-hook", "README", "pre-push.bak"))
def test_ac3_any_executable_hook_file_blocks(gate, tmp_path, hook):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(BRANCH_MERGE, fx.main, path) is None
    plant_hook(fx.main, hook)
    text = reason(BRANCH_MERGE, fx.main, path)
    assert text is not None and hook in text, text
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is not None


@pytest.mark.parametrize("name,mode", [("pre-push", 0o644), ("post-index-change", 0o600),
                                       ("pre-push.sample", 0o755), ("x.sample", 0o755)],
                         ids=["not-executable", "0600", "sample", "unnamed-sample"])
def test_ac3_a_non_executable_file_and_a_sample_file_do_not_block(gate, tmp_path, name, mode):
    fx, path = merge_ready(gate, tmp_path)
    plant_hook(fx.main, name, mode)
    assert reason(BRANCH_MERGE, fx.main, path) is None
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is None


def test_ac3_a_symlinked_hook_file_to_an_executable_blocks(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    script = os.path.join(fx.root, "real-hook.sh")
    write(script, "#!/bin/sh\nexit 0\n")
    os.chmod(script, 0o755)
    os.symlink(script, os.path.join(common_dir(fx.main), "hooks", "post-index-change"))
    assert reason(BRANCH_MERGE, fx.main, path) is not None


def test_ac3_a_symlinked_hooks_directory_with_an_executable_blocks(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    other = os.path.join(fx.root, "other-hooks")
    os.makedirs(other)
    write(os.path.join(other, "pre-auto-gc"), "#!/bin/sh\nexit 0\n")
    os.chmod(os.path.join(other, "pre-auto-gc"), 0o755)
    hooks = os.path.join(common_dir(fx.main), "hooks")
    shutil.rmtree(hooks)
    os.symlink(other, hooks)
    assert reason(BRANCH_MERGE, fx.main, path) is not None


def test_ac3_core_hookspath_stays_refused(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    git(fx.wt, "config", "core.hooksPath", os.path.join(fx.root, "nohooks"))
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is not None


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads any directory")
def test_ac3_a_hooks_directory_that_cannot_be_read_blocks(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    hooks = os.path.join(common_dir(fx.main), "hooks")
    os.chmod(hooks, 0)
    try:
        assert reason(BRANCH_MERGE, fx.main, path) is not None
    finally:
        os.chmod(hooks, 0o755)


# ── AC 4 — attributes: `merge=`, `filter=`, `diff=` block ───────────────────────────────────
BAD_ATTRIBUTES = ["* merge=x\n", "*.png filter=x\n", "*.md diff=x\n", "*.txt  eol=lf   merge=union\n",
                  "[attr]mac merge=x\n", '"a b.txt" filter=lfs diff=lfs merge=lfs -text\n',
                  "# comment\n* text\n*.c MERGE=x\n", "*.c\tdiff=x\n"]


@pytest.mark.parametrize("text", BAD_ATTRIBUTES)
@pytest.mark.parametrize("where", ["worktree", "subdir", "info"])
def test_ac4_an_attributes_line_with_merge_filter_or_diff_blocks(gate, tmp_path, text, where):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(BRANCH_MERGE, fx.main, path) is None
    target = {"worktree": os.path.join(fx.main, ".gitattributes"),
              "subdir": os.path.join(fx.main, "sub", "deep", ".gitattributes"),
              "info": os.path.join(common_dir(fx.main), "info", "attributes")}[where]
    write(target, text)
    text_out = reason(BRANCH_MERGE, fx.main, path)
    assert text_out is not None and "attributes" in text_out, text_out


@pytest.mark.parametrize("text", ["* text eol=lf\n", "*.bin binary -diff\n", "*.sh text eol=lf\n",
                                  "# merge=x is only a comment\n", "*.md linguist-language=Markdown\n",
                                  "*.c !diff\n", "*.c diff\n", "docs/** -merge\n", "\n"])
def test_ac4_other_attributes_do_not_block(gate, tmp_path, text):
    fx, path = merge_ready(gate, tmp_path)
    write(os.path.join(fx.main, ".gitattributes"), text)
    write(os.path.join(common_dir(fx.main), "info", "attributes"), text)
    assert reason(BRANCH_MERGE, fx.main, path) is None


def test_ac4_the_attributes_of_the_checkout_the_command_runs_in_are_read(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    write(os.path.join(fx.wt, ".gitattributes"), "* merge=x\n")
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is not None
    assert reason(BRANCH_MERGE, fx.main, path) is None  # the main checkout has none


def test_ac4_an_attributes_file_that_cannot_be_read_blocks(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    target = os.path.join(fx.main, ".gitattributes")
    os.makedirs(target)  # a directory where a file is read: open() fails
    assert reason(BRANCH_MERGE, fx.main, path) is not None


# ── AC 5 — a chained git command blocks; `cd <dir> &&` stays ────────────────────────────────
CHAINED = [G + "status", G + "show HEAD", G + "diff HEAD", G + "log -1", G + "diff --cached",
           G + "status -s", G + "rev-parse HEAD", G + "show --stat", G + "log --oneline",
           G + "-C {main} status"]


@pytest.mark.parametrize("read", CHAINED)
@pytest.mark.parametrize("shape", ["before-merge", "after-merge", "before-push"])
def test_ac5_a_read_only_git_command_chained_with_a_merge_or_push_blocks(gate, tmp_path, read, shape):
    fx, path = merge_ready(gate, tmp_path)
    read = read.format(main=fx.main)
    cmd, cwd = {"before-merge": (read + " && " + BRANCH_MERGE, fx.main),
                "after-merge": (BRANCH_MERGE + " && " + read, fx.main),
                "before-push": (read + " && " + PUSH + " origin feat/t900-x", fx.wt)}[shape]
    text = reason(cmd, cwd, path)
    assert text is not None and "one git merge or push" in text, text


def test_ac5_the_main_push_with_a_chained_status_blocks(gate, tmp_path):
    fx, path = legit(gate, tmp_path)
    assert reason(PUSH + " origin main", fx.main, path) is None
    assert reason(G + "status && " + PUSH + " origin main", fx.main, path) is not None


@pytest.mark.parametrize("cmd", ["cd {main} && " + BRANCH_MERGE, BRANCH_MERGE,
                                 "cd {main} && cd . && " + BRANCH_MERGE])
def test_ac5_cd_and_a_lone_merge_stay_allowed(gate, tmp_path, cmd):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(cmd.format(main=fx.main), fx.main, path) is None


@pytest.mark.parametrize("cmd", [PUSH + " origin feat/t900-x", "cd {wt} && " + PUSH + " origin feat/t900-x"])
def test_ac5_cd_and_a_lone_push_stay_allowed(gate, tmp_path, cmd):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(cmd.format(wt=fx.wt), fx.wt, path) is None


# ── AC 6 — a merge driver no longer makes `main` look right ─────────────────────────────────
def driver_scenario(gate, tmp_path):
    """Branch tip `f.txt` is `A\\nb\\nc`; `main` is merged by a planted driver and holds
    `UNVERIFIED CONTENT`. Returns (fx, transcript path); the driver is configured."""
    fx = gate(kanban(done=("T900",)))
    write(os.path.join(fx.main, "f.txt"), "a\nb\nc\n")
    git(fx.main, "add", "-A")
    git(fx.main, "commit", "-qm", "shared f.txt")
    git(fx.wt, "merge", "-q", "--ff-only", "main")
    write(os.path.join(fx.wt, "f.txt"), "A\nb\nc\n")
    git(fx.wt, "commit", "-qam", "T900: tip")
    auto_verified(fx)
    write(os.path.join(fx.main, "f.txt"), "a\nb\nC\n")
    git(fx.main, "commit", "-qam", "main moves")
    publish(fx)
    driver = os.path.join(fx.root, "driver.sh")
    write(driver, "#!/bin/sh\necho 'UNVERIFIED CONTENT' > \"$1\"\nexit 0\n")
    os.chmod(driver, 0o755)
    git(fx.main, "config", "merge.evil.driver", driver + " %A")
    write(os.path.join(common_dir(fx.main), "info", "attributes"), "f.txt merge=evil\n")
    git(fx.main, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    assert open(os.path.join(fx.main, "f.txt")).read().strip() == "UNVERIFIED CONTENT"
    return fx, admin_session(tmp_path, fx, merge_cmd=NO_FF)


def test_ac6_the_main_push_after_a_planted_driver_is_blocked_by_the_config_rule(gate, tmp_path):
    fx, path = driver_scenario(gate, tmp_path)
    text = reason(PUSH + " origin main", fx.main, path)
    assert text is not None and "merge.evil.driver" in text, text


def test_ac6_main_push_refusal_itself_refuses_a_tree_a_driver_changed(gate, tmp_path):
    """The tree check cannot tell: `git merge-tree` runs the same driver and gets the same tree.
    The refusal must come from the repository rule it now repeats."""
    fx, _ = driver_scenario(gate, tmp_path)
    text = merge_gate._main_push_refusal(fx.main, "feat/t900-x")
    assert text is not None and "merge.evil.driver" in text, text


def test_ac6_main_push_refusal_still_accepts_the_same_merge_without_the_driver(gate, tmp_path):
    fx, path = legit(gate, tmp_path)
    assert merge_gate._main_push_refusal(fx.main, "feat/t900-x") is None
    assert reason(PUSH + " origin main", fx.main, path) is None


# ── AC 5 of the guide's success criteria — the planted driver, run for real ─────────────────
def planted_driver_repo(gate, tmp_path, tag):
    fx = gate(kanban(ready=("T900",)))
    write(os.path.join(fx.wt, "f.txt"), "branch\n")
    git(fx.wt, "add", "-A")
    git(fx.wt, "commit", "-qm", "T900: f.txt")
    auto_verified(fx)
    write(os.path.join(fx.main, "f.txt"), "main\n")
    git(fx.main, "add", "f.txt")
    git(fx.main, "commit", "-qm", "main f.txt")
    marker = os.path.join(fx.root, f"DRIVER_RAN_{tag}")
    driver = os.path.join(fx.root, "drv.sh")
    write(driver, f"#!/bin/sh\necho ran > {marker}\ncp \"$2\" \"$1\"\nexit 0\n")
    os.chmod(driver, 0o755)
    git(fx.main, "config", "merge.evil.driver", driver + " %A %B")
    write(os.path.join(common_dir(fx.main), "info", "attributes"), "* merge=evil\n")
    return fx, marker


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_sc5_the_planted_merge_driver_runs_without_the_gate_and_not_with_it(gate, tmp_path, shell):
    if shutil.which(shell) is None:
        pytest.skip(f"{shell} is not installed")
    env = {**os.environ, **GIT_ENV, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e.x",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e.x"}
    # control: no gate, the driver runs (proves the plant works, so the absence below means something)
    fx, marker = planted_driver_repo(gate, tmp_path, f"{shell}_control")
    subprocess.run([shell, "-c", BRANCH_MERGE], cwd=fx.main, env=env, capture_output=True, check=True)
    assert os.path.exists(marker), "control: the planted driver did not run"


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_sc5_with_the_gate_the_merge_is_refused_before_the_driver_runs(gate, tmp_path, shell):
    if shutil.which(shell) is None:
        pytest.skip(f"{shell} is not installed")
    env = {**os.environ, **GIT_ENV, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e.x",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e.x"}
    fx, marker = planted_driver_repo(gate, tmp_path, f"{shell}_gated")
    text = reason(BRANCH_MERGE, fx.main, session(tmp_path, fx, "do it [admin]"))
    if text is None:  # the gate allowed it: the command would run
        subprocess.run([shell, "-c", BRANCH_MERGE], cwd=fx.main, env=env, capture_output=True)
    assert text is not None and "merge.evil.driver" in text, text
    assert not os.path.exists(marker), "the driver ran although the gate refused"


# ── a safe repo keeps working (regression) ──────────────────────────────────────────────────
def test_sc4_a_clean_repo_merge_and_push_stay_allowed(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    assert reason(BRANCH_MERGE, fx.main, path) is None
    assert reason(PUSH + " origin feat/t900-x", fx.wt, path) is None
    assert reason(MERGE + " --no-ff -m 'T900 merge' feat/t900-x", fx.main, path) is None


def test_sc4_a_repo_with_sample_hooks_and_plain_attributes_stays_allowed(gate, tmp_path):
    fx, path = merge_ready(gate, tmp_path)
    for name in ("pre-push.sample", "post-update.sample"):
        plant_hook(fx.main, name)
    write(os.path.join(fx.main, ".gitattributes"), "* text=auto\n*.sh eol=lf\n")
    git(fx.main, "config", "user.name", "T")
    git(fx.main, "config", "user.email", "t@example.com")
    assert reason(BRANCH_MERGE, fx.main, path) is None


def test_sc4_the_main_push_after_a_legit_merge_stays_allowed(gate, tmp_path):
    fx, path = legit(gate, tmp_path)
    assert reason(PUSH + " origin main", fx.main, path) is None


# ── AC 7, 8 — text and tripwire ─────────────────────────────────────────────────────────────
def item2():
    return admin_tag_section()


def test_ac7_tracks_md_states_the_allowlist_rule_and_its_short_list():
    body = item2()
    for needle in ("allowlist", "core.repositoryformatversion", "remote.<name>.url",
                   "branch.<b>.remote", "user.email", "must hold no executable file",
                   "`.sample`", "`merge=`, `filter=` or `diff=`", "`.gitattributes`",
                   "`.git/info/attributes`", "`cd <dir> &&`"):
        assert needle in body, needle


def test_ac7_the_old_deny_list_and_the_chain_exception_are_gone_from_tracks_md():
    body = item2()
    for stale in ("`git status`, `log`, `diff`, `show`, `rev-parse` and `cd <dir> &&` may stay",
                  "no repo or worktree config that can run a command or send git elsewhere "
                  "(`include.*`", "The deny lists in item 2 are not complete"):
        assert stale not in body, stale


def test_ac7_the_known_limit_keeps_only_what_is_still_open():
    body = item2()
    limits = body.split("Known limits:", 1)[1]
    for fixed in ("`merge.<d>.driver`", "`filter.<f>.smudge`", "`diff.external`", "`gpg.program`",
                  "`post-index-change`", "`pre-auto-gc`", "`credential.helper` set to a path"):
        assert fixed not in limits, f"{fixed} is fixed by T295 and must leave the limit"
