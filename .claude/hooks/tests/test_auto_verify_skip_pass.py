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
    G, GUIDE_VACATED, MERGE, PUSH, REVIEW, gate, git, kanban, merge_gate)
from test_admin_tag import merged_session, publish, reason, session  # noqa: E402
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
           "setup.sh", "PROJECT_KANBAN.md", "CLAUDE_LEGACY.md", "src/app.py", ".claude/settings.json"]


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
DOCS_ONLY = ["tasks/TASK_REVIEW_T9.md", "tasks/MINIMAL_LOG.md", "tasks/sub/dir/x.txt",
             "memory/decisions.md", "memory/event-trace/T9.jsonl", "docs/ddr/0001-x.md", "docs/main-flow.md",
             "docs/adr/0001-x.md", "tests/test_x.py", "tests/fixtures/auto_verify/verify_pass.json",
             ".claude/hooks/tests/test_x.py", ".claude/hooks/tests/data/x.txt", "README.md", "RUNBOOK.md",
             "PRD.md", "BRAINSTORMING_LOG.md"]
NOT_DOCS_ONLY = ["AGENTS.md", "CLAUDE.md", "agents.md", "Claude.md", "CLAUDE_LEGACY.md", "PROJECT_KANBAN.md",
                 "PROJECT_SPEC.md", "skills/x/SKILL.md", "agents/backend.md", "templates/x.md",
                 "docs/claude-md/tracks.md", "docs/claude-md/x/y.md", "docs/CLAUDE-MD/x.md",
                 "docs/Claude-md/x.md", "docs/claude-mdx.md", "site/index.html", "scripts/x.py", "lib/x.sh",
                 "setup.sh", "MANIFEST", ".claude/hooks/foo.py", ".claude/hooks/lib/verify_record.py",
                 ".claude/settings.json", ".claude/hooks/tests", ".claude/hooks/testsx/x.py",
                 "Tasks/x.md", "TASKS/x.md", "Docs/x.md", "docs", "tasks", "tests", ".md", "x.MD", "x.txt",
                 "tasks/../skills/x.md", "tasks/./x.md", "tasks//x.md", "/tasks/x.md", "tasks/x.md/",
                 "tasks/a b.md", "tasks/a|b.md", "tasks/a\nb.md", "tasks/é.md", "tasks/a\\b.md", "tasks/x;y.md",
                 "", "tasks/" + "a" * 300 + ".md", "src/app.py", "packs/api/PACK.md", "reports/x.md"]


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
                                 "project_spec.md")
    for prefix in vr.DOCS_ONLY_PREFIXES:
        assert vr.docs_only_path(prefix + "x.md") is True, prefix
    for exception in vr.DOCS_ONLY_EXCEPT:
        assert vr.docs_only_path(exception + "/x.md") is False, exception
    for name in vr.ROOT_MD_EXCEPT:
        assert vr.docs_only_path(name) is False and vr.docs_only_path(name.upper()) is False, name
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


@pytest.mark.parametrize("name", ["tasks/a b.md", "tasks/a;b.md", "tasks/é.md", "tasks/a'b.md"])
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
    fx.task_file("TASK_GUIDE_T900.md", GUIDE_VACATED.format(tid="T900"), commit=True)
    verified = git(fx.wt, "rev-parse", "HEAD")
    base = {"main-base": git(fx.main, "rev-parse", "main"),
            "after-extra": after_extra}.get(record_base, record_base)
    vr.write_record(merge_gate.ROOT, "T900", verified, verdict, "s-1", "log.txt", base=base)
    cells = vr.row_cells(verified, "skip-pass", "s-1", "log.txt", paths=["tasks/TASK_GUIDE_T900.md"])
    fx.task_file("TASK_REVIEW_T900.md", REVIEW.format(tid="T900", result=cells[0], notes=cells[1]),
                 commit=True)
    publish(fx)
    return verified


def test_ac6_admin_may_merge_a_docs_only_task_with_a_skip_pass_and_no_typed_verify(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    assert reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "do T-thing [admin]")) is None


def test_ac6_admin_may_push_the_branch_and_then_main_after_its_own_merge(gate, tmp_path):
    fx = gate(kanban(ready=("T900",)))
    skip_verified(fx)
    assert reason(PUSH + " origin feat/t900-x", fx.wt, session(tmp_path, fx, "do it [admin]")) is None
    assert reason(PUSH + " origin main", fx.main, merged_session(tmp_path, fx)) is None  # base stays valid


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
    fx.task_file("TASK_GUIDE_T900.md", GUIDE_VACATED.format(tid="T900"), commit=True)
    verified = git(fx.wt, "rev-parse", "HEAD")
    vr.write_record(merge_gate.ROOT, "T900", verified, "skip-pass", "s-1", "log.txt",
                    base=git(fx.main, "rev-parse", "main"))
    cells = vr.row_cells(verified, "skip-pass", "s-1", "log.txt", paths=["tasks/TASK_GUIDE_T900.md"])
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
    text = reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "do it [admin]"))
    assert text is not None and "auto verify" in text, text
    text = reason(PUSH + " origin feat/t900-x", fx.wt, session(tmp_path, fx, "do it [admin]"))
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
    text = reason(MERGE + " feat/t900-x", fx.main, session(tmp_path, fx, "do it [admin]"))
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
