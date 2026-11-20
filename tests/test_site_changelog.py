#!/usr/bin/env python3
"""T344 — `site/docs.html` has a Change log section listing every release (`tasks/TASK_GUIDE_T344.md`).

AC 1 — `<section id="changelog">` with `<h2>Change log</h2>`, after `#options`, before `<footer>`; the
       sidebar's `// reference` group ends with the `#changelog` link.
AC 2 — one `<details>` per release, newest first (Unreleased, v2.2.0, v2.1.0, v2.0.0, v1); each summary
       names the release and its task count; only Unreleased is open.
AC 4 — each task is `<li><code>Txxx</code> — <title></li>`, the board title HTML-escaped, backtick spans
       as `<code>`.
AC 5 — every `- [x]` task on `PROJECT_KANBAN.md` appears exactly once (T344's Done set is the floor).
AC 3 — the section copies no email address (no `@`).

Run with: python3 -m pytest tests/test_site_changelog.py -v
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "site" / "docs.html"
BOARD = ROOT / "PROJECT_KANBAN.md"
RELEASES = ["Unreleased", "v2.2.0", "v2.1.0", "v2.0.0", "v1"]
# The Done tasks at T344's start (2026-11-20): the section may grow, never lose one.
FLOOR_COUNT = 255

TASK_LI = re.compile(r"<li><code>(T\d{3})</code> — (.*?)</li>")


def _docs():
    return DOCS.read_text(encoding="utf-8")


def _section():
    text = _docs()
    m = re.search(r'<section id="changelog">.*?</section>', text, re.S)
    assert m, 'no <section id="changelog"> in site/docs.html'
    return m.group(0)


def _done_titles():
    board = BOARD.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in
            re.finditer(r"^- \[x\] \*\*(T\d{3})\*\* — (.+?)(?= \| |$)", board, re.M)}


def render_title(title):
    """The board title as the section shows it: escaped, then backtick spans as `<code>`."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(title, quote=False))


# ---- AC 1 ------------------------------------------------------------------------------------

def test_ac1_the_section_has_its_heading_after_options_and_before_the_footer():
    text = _docs()
    section = _section()
    assert "<h2>Change log</h2>" in section
    assert text.index('<section id="options">') < text.index('<section id="changelog">') < text.index("<footer>")


def test_ac1_the_reference_nav_group_ends_with_the_changelog_link():
    text = _docs()
    group = re.search(r'<p class="nav-group-title">// reference</p>\s*<ul>(.*?)</ul>', text, re.S)
    assert group, "no // reference nav group"
    links = re.findall(r'<li><a href="#([^"]+)">([^<]+)</a></li>', group.group(1))
    assert links[-1] == ("changelog", "Change log")


# ---- AC 2 ------------------------------------------------------------------------------------

def _entries():
    return re.findall(r"<details( open)?>\s*<summary>(.*?)</summary>(.*?)</details>", _section(), re.S)


def test_ac2_one_entry_per_release_newest_first_only_unreleased_open():
    entries = _entries()
    names = [re.match(r"\s*(\S+)", summary).group(1) for _, summary, _ in entries]
    assert names == RELEASES
    assert [bool(is_open) for is_open, _, _ in entries] == [True, False, False, False, False]


def test_ac2_each_summary_gives_its_task_count():
    for _, summary, body in _entries():
        count = len(TASK_LI.findall(body))
        assert f"{count} tasks" in summary, (summary, count)


def test_ac2_each_released_summary_gives_a_date():
    for _, summary, _ in _entries()[1:]:
        assert re.search(r"\d{4}-\d{2}-\d{2}", summary), summary


# ---- AC 5 ------------------------------------------------------------------------------------

def test_ac5_every_done_task_on_the_board_appears_exactly_once():
    listed = [tid for tid, _ in TASK_LI.findall(_section())]
    done = _done_titles()
    assert len(done) >= FLOOR_COUNT
    dupes = sorted({t for t in listed if listed.count(t) > 1})
    assert not dupes, f"listed more than once: {dupes}"
    missing = sorted(set(done) - set(listed))
    assert not missing, f"Done on the board but not in the change log: {missing}"
    extra = sorted(set(listed) - set(done))
    assert not extra, f"in the change log but not Done on the board: {extra}"


def test_ac5_tasks_are_in_id_order_inside_each_entry():
    for _, _, body in _entries():
        ids = [tid for tid, _ in TASK_LI.findall(body)]
        assert ids == sorted(ids)


# ---- AC 4 ------------------------------------------------------------------------------------

def test_ac4_each_task_shows_its_board_title_escaped_with_code_spans():
    done = _done_titles()
    shown = dict(TASK_LI.findall(_section()))
    wrong = [tid for tid, title in done.items() if tid in shown and shown[tid] != render_title(title)]
    assert not wrong, f"title differs from the board: {wrong[:10]}"


def test_ac4_render_title_escapes_and_keeps_code_spans():
    assert render_title("a < b & `x<y>` c") == "a &lt; b &amp; <code>x&lt;y&gt;</code> c"


# ---- AC 3 ------------------------------------------------------------------------------------

def test_ac3_the_section_copies_no_email_address():
    assert "@" not in _section()
