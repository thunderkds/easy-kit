#!/usr/bin/env python3
"""T289 — a docs-only task gets a real pass from the auto verify run (`tasks/TASK_GUIDE_T289.md`, AC 1-7).

When every file the task's branch changes lies in a short, fixed list of paths with no runtime
surface, and the headless run answers SKIP, the hook writes a `☑ pass` row that says
`skip (no runtime surface: <paths>)` and a run record that says `skip-pass`. The hook, not the model,
decides from git that the paths are all in the list. One path outside the list, or any other verdict,
keeps today's result. The merge gate re-checks the paths from git before it trusts a `skip-pass` record.

  AC 1  docs-only branch + SKIP answer -> pass row, `skip-pass` record, gate accepts it
  AC 2  the path list is a literal tuple, computed from git, never from the model's answer
  AC 3  one path outside the list -> `blocked`, exactly as before
  AC 4  PASS and FAIL are handled as before; a FAIL is never a pass; no verdict line stays `blocked`
  AC 5  empty diff, unreadable range, missing base ref, rename out of the list, symlink -> `blocked`
  AC 6  `[admin]` merges and pushes a docs-only task with no typed `/verify`; `[auto]` alone cannot
  AC 7  the docs state the rule (checked in `test_t289_docs.py` style tests at the bottom)

Every git repo, board, transcript and `claude` here is constructed; the real `claude` never runs.
Run with: python3 -B -m pytest .claude/hooks/tests/test_auto_verify_skip_pass.py -v
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = Path(HERE).resolve().parents[2]
sys.path.insert(0, HERE)
sys.path.insert(0, str(REPO / "tests"))
from test_merge_gate_t210 import (  # noqa: E402
    G, MERGE, PUSH, REVIEW, gate, git, kanban, merge_gate)
from test_admin_tag import bash, publish, reason, result, session  # noqa: E402
import test_auto_verify as tav  # noqa: E402  (module only: its tests are not re-collected)

import verify_record as vr  # noqa: E402  (on sys.path: the merge gate put its lib/ there)

assert gate  # the fixture, imported for pytest

SKIP = tav._verdict_output("**Verdict:** SKIP")
TRACKS = REPO / "docs" / "claude-md" / "tracks.md"


# ── helpers ───────────────────────────────────────────────────────────────────────────────
def _commit_file(checkout, rel, text="x\n", run=None):
    run = run or tav._git
    path = Path(checkout) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    run(checkout, "add", "-A")
    run(checkout, "commit", "-qm", f"change {rel}")


def _run_hook(tmp_path, output=SKIP, change=None, prepare=None):
    """A temp project whose task branch `feat/t951` committed only its review file, plus an optional
    extra committed change; the real Stop hook runs against a stub `claude` that prints `output`.
    Returns (project, checkout, env, (result, notes))."""
    project, checkout = tav._project(tmp_path, worktree=True)
    if change:
        for rel in ([change] if isinstance(change, str) else change):
            _commit_file(checkout, rel)
    if prepare:
        prepare(project, checkout)
    stub_dir, _ = tav._stub(tmp_path, output=output)
    env = tav._env(tmp_path, project, stub_dir)
    tav._stop(project, env)
    return project, checkout, env, tav._wait_row(checkout)


def _record_of(env, project, checkout, monkeypatch):
    monkeypatch.setenv("CLAUDE_TRACE_ANCHOR_DIR", env["CLAUDE_TRACE_ANCHOR_DIR"])
    return vr.read_record(str(project), tav.TASK, tav._git(checkout, "rev-parse", "HEAD"))


# ── AC 1 — the pass ───────────────────────────────────────────────────────────────────────
def test_ac1_docs_only_branch_and_a_skip_answer_is_a_pass_row_and_a_skip_pass_record(tmp_path, monkeypatch):
    project, checkout, env, (result, notes) = _run_hook(tmp_path)
    head = tav._git(checkout, "rev-parse", "HEAD")
    assert result == "☑ pass", (result, notes)
    assert notes == ("auto-run by hook, session bb6500c2-6ee9-4ce9-bc0e-ea2f246f2fd4, "
                     f"commit {head}, log .claude/verify-runs/{tav.TASK}-{head[:12]}.log, "
                     "skip (no runtime surface: tasks/TASK_REVIEW_T951.md) — pass")
    record = _record_of(env, project, checkout, monkeypatch)
    assert record["verdict"] == "skip-pass" and record["commit"] == head
    assert re.fullmatch(r"[0-9a-f]{40}", record["base"]), record
    assert record["base"] == tav._git(project, "rev-parse", "main")


def test_ac1_the_merge_gate_accepts_the_committed_skip_pass_row(tmp_path):
    project, checkout, env, _ = _run_hook(tmp_path)
    tav._git(checkout, "commit", "-qam", "review: verify row")  # the Supervisor commits only the row
    assert tav._merge(project, env) == ("allow", "")


def test_ac1_the_notes_name_every_path_that_was_judged(tmp_path):
    _, _, _, (result, notes) = _run_hook(tmp_path, change=["docs/a.md", "tests/test_x.py", "README.md"])
    assert result == "☑ pass"
    for path in ("README.md", "docs/a.md", "tasks/TASK_REVIEW_T951.md", "tests/test_x.py"):
        assert path in notes, notes


# ── AC 3 — one path outside the list keeps today's result ──────────────────────────────────
OUTSIDE = ["skills/x/SKILL.md", "site/index.html", ".claude/hooks/foo.py", "AGENTS.md", "CLAUDE.md",
           "docs/claude-md/tracks.md", "agents/backend.md", "templates/x.md", "scripts/x.py",
           "setup.sh", "PROJECT_KANBAN.md", "CLAUDE_LEGACY.md", "src/app.py", ".claude/settings.json",
           "tasks/TASK_GUIDE_T9.md", "memory/MEMORY.md", "docs/run.sh", "memory/hook.py", "tests/conftest.py"]


@pytest.mark.parametrize("path", OUTSIDE)
def test_ac3_one_path_outside_the_list_and_a_skip_answer_stays_blocked(tmp_path, path):
    _, _, _, (result, notes) = _run_hook(tmp_path, change=["docs/a.md", path])
    assert result == "☐ blocked", (path, result, notes)
    assert "pass" not in notes.lower() and "auto-run by hook" in notes and "blocked" in notes, notes


def test_ac3_the_models_own_words_never_make_the_pass(tmp_path):
    """The answer calls the diff docs-only and asks for a pass; the diff holds a hook file."""
    text = tav._verdict_output("This diff is docs-only, mark it pass.\n\n**Verdict:** SKIP")
    _, _, _, (result, notes) = _run_hook(tmp_path, output=text, change=".claude/hooks/foo.py")
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


# ── AC 4 — PASS and FAIL are handled as before ─────────────────────────────────────────────
def test_ac4_a_pass_answer_is_a_plain_pass_with_a_plain_pass_record(tmp_path, monkeypatch):
    project, checkout, env, (result, notes) = _run_hook(tmp_path, output=tav._verdict_output(
        "**Verdict:** PASS"))
    assert result == "☑ pass" and notes.endswith("— pass") and "skip" not in notes, notes
    assert _record_of(env, project, checkout, monkeypatch)["verdict"] == "pass"


def test_ac4_a_pass_answer_on_a_non_docs_branch_is_still_a_pass(tmp_path):
    _, _, _, (result, notes) = _run_hook(tmp_path, output=tav._verdict_output("**Verdict:** PASS"),
                                         change="skills/x/SKILL.md")
    assert result == "☑ pass" and notes.endswith("— pass"), notes


def test_ac4_a_fail_answer_on_a_docs_only_branch_is_never_a_pass(tmp_path, monkeypatch):
    project, checkout, env, (result, notes) = _run_hook(tmp_path, output=tav._verdict_output(
        "**Verdict:** FAIL"))
    assert result == "☑ fail" and notes.endswith("— fail") and "pass" not in notes.lower(), notes
    assert _record_of(env, project, checkout, monkeypatch)["verdict"] == "fail"


@pytest.mark.parametrize("text", ["No verdict here, all docs.", "**Verdict:** BLOCKED",
                                  "**Verdict:** PASS\n\n**Verdict:** SKIP",
                                  "**Verdict:** SKIP\n\n**Verdict:** FAIL",
                                  "**Verdict:** SKIP | FAIL"],
                         ids=["none", "blocked", "pass-and-skip", "skip-and-fail", "choices"])
def test_ac4_any_other_answer_on_a_docs_only_branch_stays_blocked(tmp_path, text):
    _, _, _, (result, notes) = _run_hook(tmp_path, output=tav._verdict_output(text))
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


@pytest.mark.parametrize("fields", [{"subtype": "error_max_budget_usd"}, {"is_error": True}],
                         ids=["budget-stop", "is-error"])
def test_ac4_a_skip_from_a_run_that_did_not_succeed_stays_blocked(tmp_path, fields):
    _, _, _, (result, notes) = _run_hook(
        tmp_path, output=tav._verdict_output("**Verdict:** SKIP", **fields))
    assert result == "☐ blocked", (result, notes)


def test_ac4_parse_reads_a_skip_answer_as_skip_and_a_choice_list_as_blocked():
    assert tav._parse(SKIP)[0] == "skip"
    assert tav._parse(tav._verdict_output("**Verdict:** PASS | FAIL | BLOCKED | SKIP"))[0] == "blocked"


# ── AC 5 — fail closed on any doubt ───────────────────────────────────────────────────────
def test_ac5_an_empty_diff_is_not_a_skip_pass(tmp_path):
    """No worktree: the head is `main` itself, so `main...head` lists no path."""
    project, checkout = tav._project(tmp_path)
    stub_dir, _ = tav._stub(tmp_path, output=SKIP)
    tav._stop(project, tav._env(tmp_path, project, stub_dir))
    result, notes = tav._wait_row(checkout)
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


def test_ac5_a_missing_base_ref_is_not_a_skip_pass(tmp_path):
    def rename_main(project, checkout):
        tav._git(project, "branch", "-m", "main", "trunk")
    _, _, _, (result, notes) = _run_hook(tmp_path, prepare=rename_main)
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


def test_ac5_a_rename_that_moves_a_runtime_file_into_tasks_is_not_a_skip_pass(tmp_path):
    def move(project, checkout):
        tav._git(checkout, "mv", "src/app.py", "tasks/app.txt")
        tav._git(checkout, "commit", "-qm", "move the app into tasks")
    _, _, _, (result, notes) = _run_hook(tmp_path, prepare=move)
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


def test_ac5_a_symlink_under_tasks_into_the_hooks_is_not_a_skip_pass(tmp_path):
    def link(project, checkout):
        os.symlink("../.claude/hooks/stop_auto_verify.py", checkout / "tasks" / "innocent.md")
        tav._git(checkout, "add", "-A")
        tav._git(checkout, "commit", "-qm", "add a docs link")
    _, _, _, (result, notes) = _run_hook(tmp_path, prepare=link)
    assert result == "☐ blocked" and "pass" not in notes.lower(), (result, notes)


# ── the path rule, unit level (AC 2) ──────────────────────────────────────────────────────
DOCS_ONLY = ["tasks/TASK_REVIEW_T9.md", "tasks/MINIMAL_LOG.md", "tasks/sub/dir/x.txt", "tasks/SPIKE_REPORT_T9.md",
             "memory/decisions.md", "memory/learnings.md", "memory/learning-records/.gitkeep",
             "docs/ddr/0001-x.md", "docs/main-flow.md", "docs/adr/0001-x.md",
             "tests/test_x.py", "tests/settings_tool/test_y.py", "tests/fixtures/auto_verify/verify_pass.json",
             "tests/fixtures/x.html", ".claude/hooks/tests/test_x.py", "README.md", "RUNBOOK.md", "PRD.md",
             "BRAINSTORMING_LOG.md"]
NOT_DOCS_ONLY = ["AGENTS.md", "CLAUDE.md", "agents.md", "Claude.md", "CLAUDE_LEGACY.md", "PROJECT_KANBAN.md",
                 "PROJECT_SPEC.md", "PROJECT_KANBAN_SITE.md", "PROJECT_SPEC_SITE.md", "project_spec_site.md",
                 "skills/x/SKILL.md", "agents/backend.md", "templates/x.md",
                 "docs/claude-md/tracks.md", "docs/claude-md/x/y.md", "docs/CLAUDE-MD/x.md",
                 "docs/Claude-md/x.md", "docs/claude-mdx.md", "site/index.html", "scripts/x.py", "lib/x.sh",
                 "setup.sh", "MANIFEST", ".claude/hooks/foo.py", ".claude/hooks/lib/verify_record.py",
                 ".claude/settings.json", ".claude/hooks/tests", ".claude/hooks/testsx/x.py",
                 "Tasks/x.md", "TASKS/x.md", "Docs/x.md", "docs", "tasks", "tests", ".md", "x.MD", "x.txt",
                 "tasks/../skills/x.md", "tasks/./x.md", "tasks//x.md", "/tasks/x.md", "tasks/x.md/",
                 "tasks/a b.md", "tasks/a|b.md", "tasks/a\nb.md", "tasks/a.md\n", "tasks/\na.md", "tasks/é.md",
                 "tasks/a\\b.md", "tasks/x;y.md",
                 "", "tasks/" + "a" * 300 + ".md", "src/app.py", "packs/api/PACK.md", "reports/x.md",
                 # T289 Stage 4: only text files under tasks/, memory/, docs/
                 "docs/run.sh", "memory/hook.py", "tasks/x.py", "docs/a.html", "docs/x.json", "tasks/x.jsonl",
                 "memory/event-trace/T9.jsonl", "docs/x.MD", "tasks/x.txt.sh", "docs/Makefile",
                 # steering files: they steer agents and hooks
                 "memory/MEMORY.md", "memory/memory.md", "Memory/MEMORY.md", "tasks/TASK_GUIDE_T9.md",
                 "tasks/task_guide_x.md", "tasks/sub/TASK_GUIDE_x.md", "tasks/TASK_GUIDE_template.md",
                 # tests: test_*.py and fixtures only, never a conftest, a shell file or the gate tripwire
                 "tests/conftest.py", ".claude/hooks/tests/conftest.py", "tests/fixtures/conftest.py",
                 "tests/lib/pty.sh", "tests/test_setup.sh", "tests/fixtures/x.sh", "tests/helper.py",
                 "tests/__init__.py", "tests/test_x.pyc", "tests/test_x.py.sh", "tests/xtest_x.py",
                 ".claude/hooks/tests/merge_gate_guard.py", "tests/fixtures/merge_gate_guard.py",
                 ".claude/hooks/tests/data/x.txt", ".claude/hooks/tests/helper.py", "tests/lib/test_x.py"]


@pytest.mark.parametrize("path", DOCS_ONLY)
def test_ac2_a_path_in_the_list_is_docs_only(path):
    assert vr.docs_only_path(path) is True, path


@pytest.mark.parametrize("path", NOT_DOCS_ONLY)
def test_ac2_a_path_outside_the_list_is_not_docs_only(path):
    assert vr.docs_only_path(path) is False, path


def test_ac2_the_list_is_one_literal_tuple_and_every_entry_is_covered():
    """The list in one place. Each entry has a path that passes; each exception one that does not."""
    assert vr.DOCS_ONLY_PREFIXES == ("tasks/", "memory/", "docs/", "tests/", ".claude/hooks/tests/")
    assert vr.DOCS_ONLY_EXCEPT == ("docs/claude-md",)
    assert vr.ROOT_MD_EXCEPT == ("agents.md", "claude.md", "claude_legacy.md", "project_kanban.md",
                                 "project_spec.md", "project_kanban_site.md", "project_spec_site.md")
    assert vr.TEXT_DIRS == ("tasks/", "memory/", "docs/") and vr.TEXT_SUFFIXES == (".md", ".txt")
    assert vr.TEXT_NAMES == (".gitkeep",) and vr.STEERING_EXCEPT == ("memory/memory.md",)
    assert vr.GUIDE_NAME == "task_guide_"
    assert vr.TEST_DIRS == ("tests/", ".claude/hooks/tests/") and vr.TEST_FIXTURES == ("tests/fixtures/",)
    assert vr.TEST_EXCEPT_NAMES == ("conftest.py", "merge_gate_guard.py")
    assert vr.TEST_EXCEPT_DIRS == ("tests/lib/",)
    for prefix in vr.TEXT_DIRS:
        assert vr.docs_only_path(prefix + "x.md") is True, prefix
        assert vr.docs_only_path(prefix + "x.txt") is True, prefix
        assert vr.docs_only_path(prefix + "sub/.gitkeep") is True, prefix
    for prefix in vr.TEST_DIRS:
        assert vr.docs_only_path(prefix + "test_x.py") is True, prefix
    for exception in vr.DOCS_ONLY_EXCEPT:
        assert vr.docs_only_path(exception + "/x.md") is False, exception
    for name in vr.ROOT_MD_EXCEPT:
        assert vr.docs_only_path(name) is False and vr.docs_only_path(name.upper()) is False, name
    for name in vr.STEERING_EXCEPT:
        assert vr.docs_only_path(name) is False and vr.docs_only_path(name.upper()) is False, name
    for name in vr.TEST_EXCEPT_NAMES:
        assert vr.docs_only_path("tests/fixtures/" + name) is False, name
    assert vr.docs_only_path("tests/fixtures/x.json") is True
    assert vr.docs_only_path("README.md") is True


def test_ac2_the_list_is_not_read_from_the_model_or_the_environment():
    source = (REPO / ".claude" / "hooks" / "lib" / "verify_record.py").read_text(encoding="utf-8")
    assert "environ" in source  # the anchor directory is read from it ...
    body = source[source.index("DOCS_ONLY_PREFIXES"):source.index("def record_dir")]
    assert "environ" not in body and "getenv" not in body  # ... the path list is not


# ── docs_only_change against real git repos (AC 2, 5) ─────────────────────────────────────
def _repo(tmp_path, files=None):
    repo = tmp_path / "repo"
    repo.mkdir()
    tav._git(repo, "init", "-q", "-b", "main")
    tav._git(repo, "config", "user.email", "t@example.com")
    tav._git(repo, "config", "user.name", "t")
    for rel, text in (files or {"src/app.py": "v1\n", "skills/x/SKILL.md": "s\n", "README.md": "r\n"}).items():
        _commit_file(repo, rel, text)
    tav._git(repo, "checkout", "-q", "-b", "feat/x")
    return repo


def _tip(repo):
    return tav._git(repo, "rev-parse", "HEAD")


def test_ac2_docs_only_change_returns_the_base_and_the_sorted_paths(tmp_path):
    repo = _repo(tmp_path)
    base = _tip(repo)
    _commit_file(repo, "tasks/b.md")
    _commit_file(repo, "docs/a.md")
    assert vr.docs_only_change(str(repo), _tip(repo)) == (base, ["docs/a.md", "tasks/b.md"])


def test_ac2_the_diff_is_main_to_tip_so_main_moving_on_changes_nothing(tmp_path):
    repo = _repo(tmp_path)
    base = _tip(repo)
    _commit_file(repo, "tasks/b.md")
    tip = _tip(repo)
    tav._git(repo, "checkout", "-q", "main")
    _commit_file(repo, "src/app.py", "v2\n")  # main moves on with a runtime change
    assert vr.docs_only_change(str(repo), tip) == (base, ["tasks/b.md"])


@pytest.mark.parametrize("rel", ["skills/x/SKILL.md", "site/index.html", ".claude/hooks/foo.py", "AGENTS.md"])
def test_ac3_one_outside_path_among_docs_paths_is_none(tmp_path, rel):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/a.md")
    _commit_file(repo, rel)
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_an_empty_diff_is_none(tmp_path):
    repo = _repo(tmp_path)
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_a_branch_that_adds_then_removes_is_an_empty_diff_and_none(tmp_path):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/a.md")
    tav._git(repo, "rm", "-q", "tasks/a.md")
    tav._git(repo, "commit", "-qm", "remove it again")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_a_missing_base_ref_is_none(tmp_path):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/a.md")
    tav._git(repo, "branch", "-m", "main", "trunk")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


@pytest.mark.parametrize("tip", ["", None, "HEAD", "main", "abc123", "0" * 40, "g" * 40])
def test_ac5_an_unusable_tip_is_none(tmp_path, tip):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/a.md")
    assert vr.docs_only_change(str(repo), tip) is None


def test_ac5_an_unreadable_checkout_is_none(tmp_path):
    assert vr.docs_only_change(str(tmp_path / "nowhere"), "0" * 40) is None
    plain = tmp_path / "plain"
    plain.mkdir()
    assert vr.docs_only_change(str(plain), "0" * 40) is None


def test_ac5_a_rename_out_of_the_list_is_none(tmp_path):
    repo = _repo(tmp_path)
    (repo / "tasks").mkdir()
    tav._git(repo, "mv", "skills/x/SKILL.md", "tasks/skill-moved.md")
    tav._git(repo, "commit", "-qm", "move a skill into tasks")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None  # the old path is in the diff


def test_ac5_a_rename_from_the_list_to_the_outside_is_none(tmp_path):
    repo = _repo(tmp_path, {"tasks/a.md": "doc\n", "src/app.py": "v1\n"})
    tav._git(repo, "mv", "tasks/a.md", "src/a.py")
    tav._git(repo, "commit", "-qm", "move a doc into src")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_deleting_a_runtime_file_is_none(tmp_path):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/a.md")
    tav._git(repo, "rm", "-q", "src/app.py")
    tav._git(repo, "commit", "-qm", "delete the app")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


@pytest.mark.parametrize("link", ["tasks/innocent.md", "docs/innocent.md", "tests/innocent.py"])
def test_ac5_a_symlink_under_a_docs_path_is_none(tmp_path, link):
    repo = _repo(tmp_path)
    (repo / link).parent.mkdir(exist_ok=True)
    os.symlink("../skills/x/SKILL.md", repo / link)
    tav._git(repo, "add", "-A")
    tav._git(repo, "commit", "-qm", "add a link")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_a_submodule_entry_under_a_docs_path_is_none(tmp_path):
    repo = _repo(tmp_path)
    sub_sha = _tip(repo)
    tav._git(repo, "update-index", "--add", "--cacheinfo", f"160000,{sub_sha},tasks/sub")
    tav._git(repo, "commit", "-qm", "add a gitlink")
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


@pytest.mark.parametrize("name", ["tasks/a b.md", "tasks/a;b.md", "tasks/é.md", "tasks/a'b.md", "tasks/a.md\n"])
def test_ac5_an_unusual_path_name_is_none_and_never_reaches_a_row(tmp_path, name):
    repo = _repo(tmp_path)
    _commit_file(repo, name)
    assert vr.docs_only_change(str(repo), _tip(repo)) is None


def test_ac5_two_merge_bases_are_none(tmp_path):
    """A criss-cross history has no single base: the diff range is ambiguous, so no skip-pass."""
    repo = _repo(tmp_path)                       # on feat/x, at the root commit
    _commit_file(repo, "docs/feat.md")
    tav._git(repo, "checkout", "-q", "main")
    _commit_file(repo, "docs/main.md")
    main_before = _tip(repo)
    tav._git(repo, "merge", "-q", "--no-edit", "feat/x")      # main: merge of main and feat/x
    tav._git(repo, "checkout", "-q", "feat/x")
    tav._git(repo, "merge", "-q", "--no-edit", main_before)   # feat/x: merge of feat/x and the old main
    tip = _tip(repo)
    assert len(tav._git(repo, "merge-base", "--all", "main", tip).split()) == 2  # a real criss-cross
    assert vr.docs_only_change(str(repo), tip) is None


# ── the record and the row cells ──────────────────────────────────────────────────────────
def test_the_skip_pass_row_cells_say_pass_for_the_gate_and_skip_for_the_reader():
    result, notes = vr.row_cells("a" * 40, "skip-pass", "s-1", "log.txt", paths=["docs/a.md", "tasks/b.md"])
    assert result == "☑ pass"
    assert notes == ("auto-run by hook, session s-1, commit " + "a" * 40 +
                     ", log log.txt, skip (no runtime surface: docs/a.md, tasks/b.md) — pass")


def test_a_long_path_list_is_cut_in_the_notes_but_never_in_the_check():
    paths = [f"docs/f{i:02d}.md" for i in range(40)]
    _, notes = vr.row_cells("a" * 40, "skip-pass", "s-1", "log.txt", paths=paths)
    assert "docs/f00.md" in notes and "+28 more" in notes and "docs/f39.md" not in notes, notes


def test_the_minimal_track_line_has_the_same_shape():
    line = vr.record_line("a" * 40, "skip-pass", "s-1", "log.txt", paths=["tasks/MINIMAL_LOG.md"])
    assert line == ("verify: ☑ pass — auto-run by hook, session s-1, commit " + "a" * 40 +
                    ", log log.txt, skip (no runtime surface: tasks/MINIMAL_LOG.md)")


def test_a_blocked_or_failed_cell_never_says_pass_even_with_paths():
    for verdict in ("blocked", "fail"):
        assert "pass" not in vr.row_cells("a" * 40, verdict, "s-1", "log.txt", "no single verdict line",
                                          paths=["docs/pass.md"])[1].lower()


# ── AC 1/5/6 at the merge gate ────────────────────────────────────────────────────────────
def skip_verified(fx, extra=(), record_base="main-base", verdict="skip-pass"):
    """T900 with a hook-written skip-pass row and its run record, committed on the branch.
    `extra` files are committed (as runtime changes) before the verified commit. The row always
    claims a skip-pass; the record's `verdict` and `base` vary, because the record decides."""
    for rel in extra:
        _commit_file(fx.wt, rel, run=git)
    after_extra = git(fx.wt, "rev-parse", "HEAD")
    _commit_file(fx.wt, "docs/t900.md", run=git)  # a guide is not docs-only (it steers agents)
    verified = git(fx.wt, "rev-parse", "HEAD")
    base = {"main-base": git(fx.main, "rev-parse", "main"),
            "after-extra": after_extra}.get(record_base, record_base)
    vr.write_record(merge_gate.ROOT, "T900", verified, verdict, "s-1", "log.txt", base=base)
    cells = vr.row_cells(verified, "skip-pass", "s-1", "log.txt", paths=["docs/t900.md"])
    fx.task_file("TASK_REVIEW_T900.md", REVIEW.format(tid="T900", result=cells[0], notes=cells[1]),
                 commit=True)
    publish(fx)
    return verified


def test_ac6_admin_may_merge_a_docs_only_task_with_a_skip_pass_and_no_typed_verify(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    assert reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "merge T900 [admin]")) is None


def test_ac6_admin_may_push_the_branch_and_then_main_after_its_own_merge(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    assert reason(PUSH + " origin feat/t900-x", fx.wt, session(tmp_path, fx, "merge T900 [admin]")) is None
    git(fx.main, "merge", "-q", "--no-ff", "-m", "T900 merge", "feat/t900-x")
    merged = session(tmp_path, fx, "push T900 [admin]",
                     extra=[bash(MERGE + " --no-ff feat/t900-x", fx.main, -200), result()])
    assert reason(PUSH + " origin main", fx.main, merged) is None  # the recorded base stays valid


@pytest.mark.parametrize("command,where", [(MERGE + " feat/t900-x", "main"),
                                           (PUSH + " origin feat/t900-x", "wt")], ids=["merge", "push"])
def test_ac6_auto_alone_with_a_skip_pass_stays_blocked(gate, tmp_path, command, where):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    cwd = fx.main if where == "main" else fx.wt
    assert reason(command, cwd, None) is None  # control: with no tag the normal gate allows it
    text = reason(command, cwd, session(tmp_path, fx, "do it [auto]"))
    assert text is not None and "[auto]" in text, text


def test_ac6_the_normal_gate_accepts_the_skip_pass_row_too(gate):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    assert reason(MERGE + " feat/t900-x", fx.main, None) is None


def test_ac1_the_skip_pass_flow_with_the_hook_row_only_in_the_working_tree_is_not_committed(gate):
    """T210 D4 is unchanged: a skip-pass row counts only when committed on the branch."""
    fx = gate(kanban(ready=("T900",)))
    _commit_file(fx.wt, "docs/t900.md", run=git)
    verified = git(fx.wt, "rev-parse", "HEAD")
    vr.write_record(merge_gate.ROOT, "T900", verified, "skip-pass", "s-1", "log.txt",
                    base=git(fx.main, "rev-parse", "main"))
    cells = vr.row_cells(verified, "skip-pass", "s-1", "log.txt", paths=["docs/t900.md"])
    fx.task_file("TASK_REVIEW_T900.md", REVIEW.format(tid="T900", result=cells[0], notes=cells[1]))
    text = reason(MERGE + " feat/t900-x", fx.main, None)
    assert text is not None and "not committed" in text, text


@pytest.mark.parametrize("extra", [["skills/x/SKILL.md"], [".claude/hooks/foo.py"], ["site/index.html"],
                                   ["AGENTS.md"]])
def test_ac3_the_gate_rechecks_the_paths_a_skip_pass_record_over_a_runtime_change_blocks(gate, tmp_path, extra):
    """The record says skip-pass, but the verified commit changes a runtime file: git decides."""
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, extra=extra)
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None, extra
    text = reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "merge T900 [admin]"))
    assert text is not None and "auto verify" in text, text
    text = reason(PUSH + " origin feat/t900-x", fx.wt, session(tmp_path, fx, "merge T900 [admin]"))
    assert text is not None and "auto verify" in text, text


def test_ac3_a_skip_pass_record_with_no_base_blocks(gate):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, record_base=None)
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None


@pytest.mark.parametrize("bad", ["main", "HEAD", "abc", "z" * 40, "0" * 40])
def test_ac3_a_skip_pass_record_with_an_unusable_base_blocks(gate, bad):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, record_base=bad)
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None, bad


def test_ac3_a_skip_pass_record_whose_base_hides_the_branch_changes_blocks(gate):
    """A base on the branch itself (just after the runtime change) hides that change from the diff
    between base and commit. It is not an ancestor of `main`, so the gate refuses it."""
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, extra=["skills/x/SKILL.md"], record_base="after-extra")
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None


@pytest.mark.parametrize("verdict", ["blocked", "fail"])
def test_ac4_a_blocked_or_fail_record_never_unlocks_the_gate(gate, tmp_path, verdict):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, verdict=verdict)
    text = reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "merge T900 [admin]"))
    assert text is not None and "auto verify" in text, text


def test_ac4_an_unknown_record_verdict_never_unlocks_the_gate(gate):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, verdict="skip")
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None


def test_ac3_a_plain_pass_record_still_needs_no_base(gate):
    """The T182 rule for a `pass` record is unchanged: no `base` is read."""
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx, extra=["skills/x/SKILL.md"], record_base=None, verdict="pass")
    assert reason(MERGE + " feat/t900-x", fx.main, None) is None


# ── the close-out follows the gate's rule (T189 D3 reads the same record) ────────────────────
def test_ac1_a_skip_pass_closes_out_an_auto_mode_task_like_any_pass(tmp_path):
    project, checkout = tav._project(tmp_path, review=tav.COMPLETE, worktree=True)
    tav._trace(project)
    stub_dir, _ = tav._stub(tmp_path, output=SKIP)
    tav._stop(project, tav._env(tmp_path, project, stub_dir))
    log = tav._wait_close(project, tav.TASK, checkout)
    assert "moved to Done" in log, log
    assert [r for r in tav._section_rows(tav._board_text(project), "Done") if tav.TASK in r], log
    section = tav._auto_section(checkout)
    assert "auto verify: ☑ pass, skip (no runtime surface) (session " in section, section
    assert "Closed: row moved to Done" in section and "Paused:" not in section


def test_ac3_a_skip_answer_that_git_refuses_does_not_close_the_task_out(tmp_path):
    project, checkout = tav._project(tmp_path, review=tav.COMPLETE, worktree=True)
    _commit_file(checkout, "skills/x/SKILL.md")
    tav._trace(project)
    stub_dir, _ = tav._stub(tmp_path, output=SKIP)
    tav._stop(project, tav._env(tmp_path, project, stub_dir))
    tav._wait_row(checkout)
    tav._settle(1.5)
    assert tav._row(checkout)[0] == "☐ blocked"
    assert not [r for r in tav._section_rows(tav._board_text(project), "Done") if tav.TASK in r]
    assert "Closed:" not in tav._auto_section(checkout)


# ── the minimal track writes the same pass, one line under `Checked:` ───────────────────────
def test_ac1_the_minimal_track_gets_the_skip_pass_line_and_the_gate_accepts_it(tmp_path):
    project, checkout, env = tav._ran_minimal(tmp_path, output=SKIP, worktree=True)
    line = tav._verify_line(checkout)
    head = tav._git(checkout, "rev-parse", "HEAD")
    assert line.startswith("- verify: ☑ pass — auto-run by hook, session ")
    assert line.endswith(f"commit {head}, log .claude/verify-runs/{tav.MIN_TASK}-{head[:12]}.log, "
                         "skip (no runtime surface: tasks/MINIMAL_LOG.md)"), line
    assert tav._merge(project, env) == ("allow", "")


def test_ac3_the_minimal_track_keeps_a_blocked_line_when_a_path_is_outside_the_list(tmp_path):
    project, checkout = tav._project(tmp_path, rows=(tav.MIN_ROW_WT,), review_file=False,
                                     worktree=True, minimal_log=tav._log())
    _commit_file(checkout, "scripts/x.py")
    stub_dir, _ = tav._stub(tmp_path, output=SKIP)
    tav._stop(project, tav._env(tmp_path, project, stub_dir))
    line = tav._wait_verify_line(checkout)
    assert line.startswith("- verify: ☐ blocked — auto-run by hook") and "pass" not in line.lower(), line


# ── AC 7 — the docs name the new rule and no old fact (LR-0005) ──────────────────────────────
def _section(title):
    text = TRACKS.read_text(encoding="utf-8")
    start = text.index(f"\n### {title}\n")
    return text[start:text.index("\n### ", start + 5)]


def test_ac7_the_auto_verify_section_lists_every_path_of_the_code_list():
    section = " ".join(_section("Auto verify (Stop hook)").split())
    assert "skip (no runtime surface: <paths>)" in section and "`skip-pass`" in section
    for prefix in vr.DOCS_ONLY_PREFIXES:
        assert f"`{prefix.rstrip('/')}/`" in section, prefix
    for name in ("AGENTS.md", "CLAUDE.md", "CLAUDE_LEGACY.md", "PROJECT_KANBAN.md", "PROJECT_SPEC.md",
                 "docs/claude-md/"):
        assert f"`{name}`" in section, name
    assert "repeats the path check from git" in section
    assert "a FAIL never becomes a pass" in section


def test_ac7_the_admin_tag_and_close_out_sections_name_the_rule():
    admin = " ".join(_section("Admin tag").split())
    assert "gets a pass when the run answers `skip`, so it needs no typed `/verify`" in admin
    assert "A `skip-pass` record counts only because the gate repeats the docs-only path check" in admin
    assert "`skip-pass`" in " ".join(_section("Auto close-out").split())


def test_ac7_no_doc_still_says_a_docs_only_task_needs_the_users_verify():
    flat = " ".join(TRACKS.read_text(encoding="utf-8").split())
    assert "A docs-only task answers `skip`; its `/verify` then falls back to you" not in flat
    assert "a SKIP or BLOCKED verdict, no verdict line" not in flat
    assert "On `skip`, `blocked` or `fail` it merges nothing" not in flat
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "on `skip`, `blocked` or `fail` merges nothing" not in agents
    assert "on `blocked` or `fail` merges nothing" in agents
    site = (REPO / "site" / "docs.html").read_text(encoding="utf-8")
    assert "<code>skip</code>, the hook checks the changed paths in git" in site


def test_ac7_the_glossary_says_a_record_may_say_skip_pass():
    spec = " ".join((REPO / "PROJECT_SPEC.md").read_text(encoding="utf-8").split())
    assert "a record may also say `skip-pass`" in spec


# ── Stage 4 round (T289): the list is tighter, and git cannot be shown a fake history ─────────
def test_stage4_a_path_with_a_trailing_newline_is_not_docs_only():
    """`$` would match before a final newline; the safe-name check uses `fullmatch`."""
    assert vr.docs_only_path("tasks/a.md\n") is False
    assert vr.docs_only_path("tasks/a.md") is True


def test_stage4_only_text_files_count_under_tasks_memory_and_docs(tmp_path):
    for rel in ("docs/run.sh", "memory/hook.py", "tasks/x.py", "docs/a.html"):
        (tmp_path / rel.replace("/", "_")).mkdir()
        repo = _repo(tmp_path / rel.replace("/", "_"))
        _commit_file(repo, rel)
        assert vr.docs_only_change(str(repo), _tip(repo)) is None, rel


def test_stage4_the_steering_files_and_conftests_are_not_docs_only(tmp_path):
    for rel in ("memory/MEMORY.md", "tasks/TASK_GUIDE_T9.md", "tests/conftest.py", "tests/lib/x.sh",
                ".claude/hooks/tests/merge_gate_guard.py"):
        (tmp_path / rel.replace("/", "_")).mkdir()
        repo = _repo(tmp_path / rel.replace("/", "_"))
        _commit_file(repo, "tasks/TASK_REVIEW_T9.md")
        _commit_file(repo, rel)
        assert vr.docs_only_change(str(repo), _tip(repo)) is None, rel


def test_stage4_t283_and_t286_style_branches_are_still_skip_passes(tmp_path):
    repo = _repo(tmp_path)
    _commit_file(repo, "tasks/SPIKE_REPORT_T283.md")
    _commit_file(repo, "tasks/TASK_REVIEW_T283.md")
    _commit_file(repo, "tests/test_claude_md_slim.py")
    found = vr.docs_only_change(str(repo), _tip(repo))
    assert found and found[1] == ["tasks/SPIKE_REPORT_T283.md", "tasks/TASK_REVIEW_T283.md",
                                  "tests/test_claude_md_slim.py"]


def test_stage4_git_replace_cannot_show_a_fake_docs_only_history(tmp_path):
    """`git replace <real> <fake>` makes `git diff` read the fake commit. The check switches replace
    refs off, so the real runtime change is seen."""
    repo = _repo(tmp_path)
    base = _tip(repo)
    _commit_file(repo, "skills/x/SKILL.md", "changed\n")
    real = _tip(repo)
    tav._git(repo, "checkout", "-q", "--detach", base)
    _commit_file(repo, "tasks/a.md")
    fake = _tip(repo)
    tav._git(repo, "checkout", "-q", "feat/x")
    tav._git(repo, "replace", real, fake)
    # the control: with replace refs on, git does show the fake docs-only change
    shown = tav._git(repo, "diff", "--name-only", base, real)
    assert shown == "tasks/a.md", shown
    assert vr.docs_only_change(str(repo), real) is None
    assert vr.record_confirms_pass(str(repo), {"verdict": "skip-pass", "base": base, "commit": real}) is False


def test_stage4_an_ignore_all_gitmodules_entry_cannot_hide_a_changed_submodule(tmp_path):
    repo = _repo(tmp_path)
    tav._git(repo, "checkout", "-q", "main")
    (repo / ".gitmodules").write_text('[submodule "s"]\n\tpath = src/sub\n\turl = ./x\n\tignore = all\n')
    tav._git(repo, "add", ".gitmodules")
    tav._git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},src/sub")
    tav._git(repo, "commit", "-qm", "base with a submodule marked ignore=all")
    tav._git(repo, "checkout", "-q", "-B", "feat/x", "main")
    base = _tip(repo)
    tav._git(repo, "update-index", "--cacheinfo", f"160000,{'2' * 40},src/sub")
    (repo / "tasks").mkdir(exist_ok=True)
    (repo / "tasks" / "d.md").write_text("d\n")
    tav._git(repo, "add", "tasks/d.md")
    tav._git(repo, "commit", "-qm", "move the submodule and add a doc")
    tip = _tip(repo)
    hidden = tav._git(repo, "diff", "--raw", "--no-abbrev", base, tip)
    assert "src/sub" not in hidden, hidden  # the control: git's default output hides the submodule
    assert vr.docs_only_change(str(repo), tip) is None


def test_stage4_a_base_that_is_not_an_ancestor_of_the_commit_blocks(gate):
    """`main` holds the same runtime file as the branch (a commit the branch never had). Judged from
    that commit, the branch's runtime change would not show in the diff: the gate refuses the base."""
    fx = gate(kanban(ready=("T900",)))
    (Path(fx.main) / "skills" / "x").mkdir(parents=True)
    (Path(fx.main) / "skills" / "x" / "SKILL.md").write_text("x\n")
    git(fx.main, "add", "skills")
    git(fx.main, "commit", "-qm", "main gets the same runtime file")
    skip_verified(fx, extra=["skills/x/SKILL.md"], record_base=git(fx.main, "rev-parse", "main"))
    assert reason(MERGE + " feat/t900-x", fx.main, None) is not None


def test_stage4_a_base_must_be_a_full_hash(tmp_path):
    repo = _repo(tmp_path)
    base = _tip(repo)
    _commit_file(repo, "tasks/a.md")
    tip = _tip(repo)
    assert vr._raw_diff(str(repo), base, tip) == ["tasks/a.md"]
    for bad in ("main", base[:12], "HEAD", "", None):
        assert vr._raw_diff(str(repo), bad, tip) is None, bad
        assert vr.record_confirms_pass(str(repo), {"verdict": "skip-pass", "base": bad, "commit": tip}) is False


def test_stage4_a_path_with_a_leading_slash_is_never_docs_only():
    for path in ("/tasks/x.md", "/README.md", "//tasks/x.md", "/"):
        assert vr.docs_only_path(path) is False, path


def test_known_limit_a_local_main_ref_moved_onto_the_runtime_change_hides_it(tmp_path):
    """DOCUMENTED, NOT FIXED (`docs/claude-md/tracks.md` `### Known limits`): `refs/heads/main` is a
    mutable local ref. Moving it onto the branch's runtime commit makes the diff look docs-only. That
    needs a model that can run git and also write the record directory, which can already forge a pass
    (the T182 trust root); a push of `main` is tied to the real remote by the gate (`_main_push_refusal`)."""
    repo = _repo(tmp_path)
    _commit_file(repo, "skills/x/SKILL.md", "runtime change\n")
    runtime = _tip(repo)
    _commit_file(repo, "tasks/d.md")
    tip = _tip(repo)
    assert vr.docs_only_change(str(repo), tip) is None  # control: judged against the real main
    tav._git(repo, "update-ref", "refs/heads/main", runtime)
    assert vr.docs_only_change(str(repo), tip) == (runtime, ["tasks/d.md"])  # the repro


def test_known_limit_is_written_down_in_tracks_md():
    limits = " ".join(TRACKS.read_text(encoding="utf-8").split("### Known limits", 1)[1].split())
    for needle in ("git update-ref refs/heads/main", "trust root", "_main_push_refusal", "No network check"):
        assert needle in limits, needle


def test_stage4_tracks_md_states_the_tighter_list_and_the_replace_switch():
    flat = " ".join(TRACKS.read_text(encoding="utf-8").split())
    for needle in ("`memory/MEMORY.md` and `tasks/TASK_GUIDE_*`", "`conftest.py`", "`tests/lib/`",
                   "`merge_gate_guard.py`", "`PROJECT_KANBAN_SITE.md` and `PROJECT_SPEC_SITE.md`",
                   "a `test_*.py` file still runs at the next pytest collection", "GIT_NO_REPLACE_OBJECTS=1",
                   "`.md`, `.txt` and `.gitkeep` files under `tasks/`, `memory/` and `docs/`",
                   "A docs-only skip is `☑ pass` with the Notes", "`PASS`, `FAIL` or `SKIP`"):
        assert needle in flat, needle
