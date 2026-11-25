#!/usr/bin/env python3
"""T321 — the one remote `[admin]`/`[ticket]` may push to is the setting `EASY_KIT_ADMIN_REMOTE`
(`.claude/settings.json` `"env"`), not the hard-coded `origin` (`tasks/TASK_GUIDE_T321.md`, AC 1-6).

  * Unset or blank: `origin`, exactly as before (AC 1).
  * `github`: every check that read `origin` reads `github` — the push destination, the bare-push
    keys, the fetch/push URL equality, the own-remote check, the push-target hooks/config checks and
    the `ls-remote` read of the real `main` (AC 2-4). Still one remote: `origin` is then refused.
  * A value that is not a plain remote name refuses every `[admin]`/`[ticket]` push, naming the
    value; a merge is unaffected (AC 5).

Every repo, board, record and transcript here is constructed.
Run with: python3 -m pytest .claude/hooks/tests/test_t321_admin_remote.py -q -p no:cacheprovider
"""
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_merge_gate_t210 import MERGE, PUSH, gate, git, kanban, merge_gate  # noqa: E402
from test_admin_tag import auto_verified, merged_session, reason, session  # noqa: E402
from test_t317_loop_binding import BRANCH, TAG_AT, pass_written_at  # noqa: E402
from test_t317_fix_round import _loop  # noqa: E402

assert gate  # the fixture, imported for pytest

ENV = "EASY_KIT_ADMIN_REMOTE"
ROOT = Path(__file__).resolve().parents[3]
TRACKS = ROOT / "docs" / "claude-md" / "tracks.md"


def own_remote(fx, name):
    """A second bare repo as remote `name`, holding `main` as it is now: the project's own remote
    when the setting names it. `origin` (from `auto_verified`) stays, as another repository."""
    bare = os.path.join(fx.root, f"{name}.git")
    git(fx.root, "init", "-q", "--bare", bare)
    git(fx.main, "remote", "add", name, bare)
    git(fx.main, "push", "-q", name, "main")
    git(fx.main, "fetch", "-q", name)
    return bare


def github_case(gate, monkeypatch, board):
    monkeypatch.setenv(ENV, "github")
    fx = gate(board)
    auto_verified(fx)
    own_remote(fx, "github")
    return fx


# ══ AC 1 — unset or blank: `origin`, unchanged ═══════════════════════════════════════════════════
@pytest.mark.parametrize("value", [None, "", "   "], ids=["unset", "empty", "blank"])
def test_ac1_unset_or_blank_setting_keeps_origin(gate, tmp_path, monkeypatch, value):
    if value is None:
        monkeypatch.delenv(ENV, raising=False)
    else:
        monkeypatch.setenv(ENV, value)
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    path = session(tmp_path, fx, "do it [admin]")
    assert reason(PUSH + " origin " + BRANCH, fx.wt, path) is None
    assert reason(PUSH, fx.wt, path) is None  # bare push: git's own default is `origin`
    own_remote(fx, "github")
    text = reason(PUSH + " github " + BRANCH, fx.wt, path)
    assert text is not None and "`origin`" in text, text


# ══ AC 2 — `github`: its push allowed, `origin` refused naming `github` ══════════════════════════
@pytest.mark.parametrize("command", [PUSH + " github " + BRANCH, PUSH + " -u github HEAD",
                                     PUSH + " github " + BRANCH + ":" + BRANCH],
                         ids=["named", "head-u", "same-dst"])
def test_ac2_admin_may_push_its_branch_to_the_set_remote(gate, tmp_path, monkeypatch, command):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    assert reason(command, fx.wt, session(tmp_path, fx, "do it [admin]")) is None


def test_ac2_admin_push_to_origin_is_refused_naming_the_set_remote(gate, tmp_path, monkeypatch):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    text = reason(PUSH + " origin " + BRANCH, fx.wt, session(tmp_path, fx, "do it [admin]"))
    assert text is not None and "`github`" in text and ENV in text, text


@pytest.mark.parametrize("command", [PUSH + " github main", PUSH + " -u github main"],
                         ids=["named", "u"])
def test_ac2_admin_may_push_main_to_the_set_remote_after_its_merge(gate, tmp_path, monkeypatch,
                                                                    command):
    fx = github_case(gate, monkeypatch, kanban(done=("T900",)))
    assert reason(command, fx.main, merged_session(tmp_path, fx)) is None


def test_ac2_admin_main_push_to_origin_is_refused(gate, tmp_path, monkeypatch):
    fx = github_case(gate, monkeypatch, kanban(done=("T900",)))
    text = reason(PUSH + " origin main", fx.main, merged_session(tmp_path, fx))
    assert text is not None and "`github`" in text, text


# ══ AC 3 — every check that read `origin` reads the set remote ══════════════════════════════════
def test_ac3_bare_push_needs_git_to_resolve_to_the_set_remote(gate, tmp_path, monkeypatch):
    """No push key set: git pushes a bare `git push` to `origin`, so it is refused; with
    `branch.<b>.remote=github` it goes to `github` and is allowed."""
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    path = session(tmp_path, fx, "do it [admin]")
    assert reason(PUSH, fx.wt, path) is not None
    git(fx.wt, "config", f"branch.{BRANCH}.remote", "github")
    assert reason(PUSH, fx.wt, path) is None


@pytest.mark.parametrize("key", [f"branch.{BRANCH}.pushRemote", "remote.pushDefault"])
def test_ac3_a_bare_push_key_naming_origin_is_refused(gate, tmp_path, monkeypatch, key):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    git(fx.wt, "config", f"branch.{BRANCH}.remote", "github")
    git(fx.wt, "config", key, "origin")
    assert reason(PUSH, fx.wt, session(tmp_path, fx, "do it [admin]")) is not None


def test_ac3_set_remotes_push_url_must_equal_its_fetch_url(gate, monkeypatch, tmp_path):
    """Only `github`'s push URL differs (a user-global `pushInsteadOf`, which the repo allowlist does
    not read); `origin`'s two URLs are equal. The check must read `github`."""
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    bare = os.path.join(fx.root, "github.git")
    glob = tmp_path / "global.gitconfig"
    glob.write_text(f'[url "{fx.root}/elsewhere.git"]\n\tpushInsteadOf = {bare}\n')
    assert merge_gate._admin_push_branch(["github", BRANCH], fx.wt) == BRANCH
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(glob))
    assert merge_gate._admin_push_branch(["github", BRANCH], fx.wt) is None


def _clone_with(fx, github_url, origin_url):
    clone = os.path.join(fx.root, "clone")
    git(fx.root, "init", "-q", clone)
    git(clone, "remote", "add", "origin", origin_url)
    git(clone, "remote", "add", "github", github_url)
    return clone


def test_ac3_own_remote_check_reads_the_set_remote(gate, monkeypatch):
    """A clone whose `origin` matches the project's but whose `github` is another remote is refused;
    one whose `github` matches is allowed."""
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    origin = os.path.join(fx.root, "origin.git")
    github = os.path.join(fx.root, "github.git")
    other = os.path.join(fx.root, "other.git")
    git(fx.root, "init", "-q", "--bare", other)
    bad = _clone_with(fx, other, origin)
    text = merge_gate._own_origin_refusal(bad, fx.main)
    assert text is not None and "github" in text, text
    good = os.path.join(fx.root, "clone2")
    git(fx.root, "init", "-q", good)
    git(good, "remote", "add", "github", github)
    git(good, "remote", "add", "origin", other)
    assert merge_gate._own_origin_refusal(good, fx.main) is None


def test_ac3_push_target_hooks_of_the_set_remote_refuse(gate, monkeypatch):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    assert merge_gate._admin_push_target_refusal(fx.wt) is None
    hook = os.path.join(fx.root, "github.git", "hooks", "pre-receive")
    with open(hook, "w") as f:
        f.write("#!/bin/sh\nexit 0\n")
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR)
    text = merge_gate._admin_push_target_refusal(fx.wt)
    assert text is not None and "github" in text, text


def test_ac3_push_target_config_of_the_set_remote_refuses(gate, monkeypatch):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    git(os.path.join(fx.root, "github.git"), "config", "receive.denyCurrentBranch", "updateInstead")
    text = merge_gate._admin_push_target_refusal(fx.wt)
    assert text is not None and "updateInstead" in text and "github" in text, text


def test_ac3_ls_remote_reads_the_set_remotes_main(gate, monkeypatch):
    """`origin` and `github` hold different `main` commits: the gate reads `github`'s."""
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    git(fx.main, "commit", "-q", "--allow-empty", "-m", "only on origin")
    git(fx.main, "push", "-q", "origin", "main")
    on_origin = git(fx.main, "rev-parse", "main")
    on_github = git(os.path.join(fx.root, "github.git"), "rev-parse", "main")
    assert on_origin != on_github
    assert merge_gate._remote_main(fx.main) == on_github


def test_ac3_ls_remote_clears_the_set_remotes_proxy(gate, monkeypatch):
    """The `-c remote.<name>.proxy=` override names the remote it reads."""
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    seen = []
    real = subprocess.run

    def spy(argv, *a, **k):
        seen.append(list(argv))
        return real(argv, *a, **k)
    monkeypatch.setattr(merge_gate.subprocess, "run", spy)
    merge_gate._remote_main(fx.main)
    calls = [argv for argv in seen if "ls-remote" in argv]
    assert calls and "remote.github.proxy=" in calls[0] and "github" in calls[0], calls


# ══ AC 4 — `[ticket]` too ════════════════════════════════════════════════════════════════════════
def test_ac4_ticket_pushes_the_task_branch_to_the_set_remote_only(gate, tmp_path, monkeypatch):
    fx = github_case(gate, monkeypatch, kanban(ready=("T900",)))
    pass_written_at(fx, TAG_AT + 60)
    path = _loop(tmp_path, "ticket")
    assert reason(PUSH + " github " + BRANCH, fx.wt, path) is None
    text = reason(PUSH + " origin " + BRANCH, fx.wt, path)
    assert text is not None and "`github`" in text, text


# ══ AC 5 — a bad value refuses every push, names the value; a merge is unaffected ═══════════════
BAD = ["https://x/y.git", "../repo", "--upload-pack=x", "a b", "-x", ".", ".."]


@pytest.mark.parametrize("value", BAD)
def test_ac5_a_bad_value_refuses_every_admin_push_and_names_it(gate, tmp_path, monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    path = session(tmp_path, fx, "do it [admin]")
    for command in (PUSH + " origin " + BRANCH, PUSH):
        text = reason(command, fx.wt, path)
        assert text is not None and ENV in text and value.strip() in text, (command, text)


@pytest.mark.parametrize("value", BAD)
def test_ac5_a_bad_value_refuses_the_ticket_push(gate, tmp_path, monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    pass_written_at(fx, TAG_AT + 60)
    text = reason(PUSH + " origin " + BRANCH, fx.wt, _loop(tmp_path, "ticket"))
    assert text is not None and ENV in text, text


@pytest.mark.parametrize("value", BAD)
def test_ac5_a_bad_value_leaves_the_admin_merge_alone(gate, tmp_path, monkeypatch, value):
    monkeypatch.setenv(ENV, value)
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    assert reason(MERGE + " " + BRANCH, fx.main, session(tmp_path, fx, "do it [admin]")) is None


@pytest.mark.parametrize("value", BAD)
def test_ac5_helpers_fail_closed_on_a_bad_value(gate, monkeypatch, value):
    """A direct call of a helper never falls back to `origin` on a bad value."""
    fx = gate(kanban(ready=("T900",)))
    auto_verified(fx)
    monkeypatch.setenv(ENV, value)
    assert merge_gate._admin_push_branch(["origin", BRANCH], fx.wt) is None
    assert merge_gate._admin_push_branch([], fx.wt) is None
    assert merge_gate._remote_main(fx.main) is None
    assert merge_gate._admin_push_target_refusal(fx.wt) is not None
    assert merge_gate._own_origin_refusal(fx.wt, fx.main) is not None


# ══ AC 6 — the docs and the refusal text name the setting ═══════════════════════════════════════
def _section(heading):
    text = TRACKS.read_text(encoding="utf-8")
    start = text.index(heading + "\n")
    end = text.find("\n### ", start + len(heading))
    return text[start:end if end > 0 else None]


@pytest.mark.parametrize("heading", ["### Admin tag", "### Session tags"])
def test_ac6_tracks_md_names_the_setting_and_its_default(heading):
    lines = [line for line in _section(heading).splitlines() if ENV in line]
    assert lines, heading
    assert any("settings.json" in line and "origin" in line for line in lines), lines


def test_ac6_the_refusal_text_names_the_setting():
    assert ENV in merge_gate.AUTO_MODE_LIMIT and "`origin`" in merge_gate.AUTO_MODE_LIMIT
