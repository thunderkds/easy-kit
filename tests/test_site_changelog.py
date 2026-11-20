#!/usr/bin/env python3
"""T344 — `site/docs.html` has a Change log section listing every release (`tasks/TASK_GUIDE_T344.md`).

AC 1 — `<section id="changelog">` with `<h2>Change log</h2>`, after `#options`, before `<footer>`; the
       sidebar's `// reference` group ends with the `#changelog` link.
AC 2 — one `<details>` per release, newest first (Unreleased, v2.2.0, v2.1.0, v2.0.0, v1); each summary
       names the release and its task count; only Unreleased is open.
AC 4 — each task is `<li><title></li>`: the board title HTML-escaped, backtick spans as `<code>`; no task ID
       and no board word on the page (T083 rule kept, user 2026-11-20), so such titles use `REWRITES`.
AC 5 — every `- [x]` task on `PROJECT_KANBAN.md`, and every RUNBOOK-named task with only a guide, appears
       exactly once (T344's set is the floor).
AC 3 — the section copies no email address.

Run with: python3 -m pytest tests/test_site_changelog.py -v
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "site" / "docs.html"
BOARD = ROOT / "PROJECT_KANBAN.md"
RELEASES = ["Unreleased", "v2.2.0", "v2.1.0", "v2.0.0", "v1"]
RUNBOOK = ROOT / "RUNBOOK.md"
GUIDES = ROOT / "tasks"
# The tasks at T344's start (2026-11-20): 255 Done on the board + 8 named only by the RUNBOOK.
FLOOR_COUNT = 263

# The page shows no task ID and no board words (T083 rule, `test_no_project_state_on_page`; the user kept it
# for the change log, 2026-11-20: "No IDs at all"). Titles that carry one are shown in this plain wording.
REWRITES = {
    "T019": "Reconcile the task board's rows (metadata fixed, two removed tasks dropped)",
    "T021": "Clean dangling references to two removed tasks in cold memory",
    "T036": "Fix `scripts/smoke-install.sh` for the direct-repo model: CI had been red unnoticed; one P1 code-review fix (a vacuous assertion)",
    "T038": "Fix the piped `curl | sh` install: the main documented install command was broken for 2 days until a real user hit it; verified against the live repo",
    "T046": "Advisory `Pattern reference:` field added to the TASK_GUIDE template's `## Approach`",
    "T057": "A sub-agent inherits its parent's `session_id`, so the session-scoped step counter did not separate them",
    "T063": "Establish whether injected memory is actually used, before compressing it",
    "T069": "An earlier fix depended on a file that is not guaranteed to reach the agent",
    "T099": "Quoted-span twin of an earlier hook defect: a hook still read a command's quoted data as command text",
    "T101": "README and site still described the layout from before the canon move, in four places",
    "T103": "The Response Standard never reached the Supervisor: `CLAUDE.md` pointed at a file the harness does not auto-inject",
    "T120": "Reinstall's closing summary under-reported which CLIs the run touched: it listed the picked CLIs, not the ones actually refreshed",
    "T123": "CI still red: a shell suite shells out to pytest and CI never installed pytest",
    "T130": "The site describes the agent-focus work and stops contradicting it",
    "T151": "The docs and site describe what four earlier tasks changed",
    "T153": "Task IDs come from board config, so hooks accept kit IDs and tracker IDs such as `ENG-170` side by side",
    "T156": "Push + outbox: milestone comments and review-ready status reach the board; offline writes arrive later exactly once",
    "T157": "Pull moments wired in, and only my own open tasks block my push",
    "T161": "Online mode: a teammate's task awaiting review no longer blocks my push (assignee filter)",
    "T180": "Auto mode: with `[auto]` either track runs to review without stopping and ends with a final report of every decision",
    "T186": "Auto-mode check follow-up: a paused task stops re-blocking every later stop, new pause reasons are written, and `tracks.md` documents the auto-mode limits",
    "T203": "Auto verify for every task: the Supervisor starts the headless `/verify` (`stop_auto_verify.py --start <ID>`) when a task is ready for review; a Stop hook is the backstop",
    "T208": "Auto verify reads a PASS written in bold (`Verdict: PASS …`): a real pass is no longer recorded as blocked",
    "T212": "Landing page takes the neon Graphite Mint accent with glow, per the updated design canvas",
    "T215": "Tidy the repo root (logs into `docs/`) and shorten Done/Closed board rows to one line, full text in `docs/archive/`",
    "T220": "Drop the stale `setup.sh --pack` install lines: packs are activated by the approved `select-packs` copy; list `tech-lead` in folder-structure",
    "T229": "Auto-mode check false positive: any task touched after an `[auto]` request in the same session counted as an auto task; a hand-added board row also duplicated the registered one",
    "T230": "`dotfiles` follow-up: refuse a target inside the source, refuse skill folder names with unprintable text, report a wrong source shape",
    "T242": "Smaller plugin source: a git install copied ~28 MB while the plugin runs from ~2–2.5 MB",
    "T244": "Auto close-out wrote `Closed:` inside the review file's HTML comment, hidden when rendered; it now anchors on the first uncommented `## Auto decisions` block",
    "T246": "RUNBOOK names the `plugin/` file copies (`plugin.json`, `hooks/hooks.json`, `icon.png`) and the `cp` commands to refresh them after a root edit",
    "T248": "`ux-evaluate` follow-up: tap targets measured by `skills/ux-evaluate/scripts/tap_probe.py`; the scratch dir must be an absolute `mktemp -d` path",
    "T250": "Minimal-track deadlock after a blocked auto verify: the user's own `/verify` now satisfies the merge gate, another session's open task no longer blocks every merge, and the stop check attributes tasks by session, not file time",
    "T251": "`.claude/settings.json` denies agent writes to session transcripts, so the user's `/verify` proof gets the harness-anchors trust level; a custom `CLAUDE_CONFIG_DIR` is not covered",
    "T252": "Stop check: a parallel session's task already marked `Mode: auto` no longer blocks this session's stop",
    "T285": "Step limit counts per sub-agent run (`agent_id`), not per session and task",
    "T290": "Locked oracle: a task guide can lock its oracle test while the task runs",
    "T302": "The docs page says how Stage 4 treats a security finding (a fold-out on `site/docs.html`)",
    "T303": "The docs page describes the effort fold-out, the step-limit row, the `[admin]` config refusal and `tasks/attempts.tsv`",
}
BANNED = re.compile(r"\bT\d{3}\b|KANBAN|In Progress|Ready for Review|#[0-9a-fA-F]{6}\b|\*\*")

TASK_LI = re.compile(r"<li>(.*?)</li>")


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


def _runbook_only_titles():
    """Tasks a RUNBOOK Release Log scope names (before "Not in scope") with no board row but a guide:
    {task: guide title}."""
    rows = set(re.findall(r"^- \[.\] \*\*(T\d{3})\*\*", BOARD.read_text(encoding="utf-8"), re.M))
    log = RUNBOOK.read_text(encoding="utf-8").split("## Release Log", 1)[1]
    found = {}
    for scope in re.findall(r"^\| v[0-9.]+ \| [0-9-]+ \| ([^|]*)", log, re.M):
        for a, b in re.findall(r"T(\d{3})(?:\s*[–-]\s*T(\d{3}))?", scope.split("Not in scope")[0]):
            for n in range(int(a), int(b or a) + 1):
                tid = "T%03d" % n
                guide = GUIDES / f"TASK_GUIDE_{tid}.md"
                if tid not in rows and guide.exists():
                    first = guide.read_text(encoding="utf-8").splitlines()[0]
                    found[tid] = re.sub(r"^# TASK_GUIDE — T\d{3}: ", "", first).strip()
    return found


def _expected_titles():
    """{task: the title as the page must show it}, rewrites applied."""
    titles = {**_runbook_only_titles(), **_done_titles()}
    return {t: REWRITES.get(t, title) for t, title in titles.items()}


def _shown():
    """The page's task lines, rendered back to {rendered title: count}."""
    from collections import Counter
    return Counter(TASK_LI.findall(_section()))


def render_title(title):
    """The board title as the section shows it: escaped, then backtick spans as `<code>`, with a `<wbr>`
    break hint after each `/` and `_` so a long path wraps at 375px (T199 precedent; no new CSS)."""
    return re.sub(r"`([^`]+)`", lambda m: "<code>" + re.sub(r"([/_])", r"\1<wbr>", m.group(1)) + "</code>",
                  html.escape(title, quote=False))


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

def test_ac4_rewrites_cover_exactly_the_titles_that_break_the_page_rule():
    titles = {**_runbook_only_titles(), **_done_titles()}
    assert sorted(t for t, title in titles.items() if BANNED.search(title)) == sorted(REWRITES)


def test_ac5_runbook_named_tasks_without_a_board_row_are_the_known_eight():
    assert sorted(_runbook_only_titles()) == ["T083", "T084", "T087", "T089", "T181", "T183", "T185", "T187"]


def test_ac5_every_done_task_on_the_board_appears_exactly_once():
    expected = {t: render_title(title) for t, title in _expected_titles().items()}
    assert len(expected) >= FLOOR_COUNT
    shown = _shown()
    assert len(set(expected.values())) == len(expected), "two tasks share a title"
    missing = sorted(t for t, title in expected.items() if shown[title] == 0)
    assert not missing, f"Done on the board but not in the change log: {missing}"
    dupes = sorted(t for t, title in expected.items() if shown[title] > 1)
    assert not dupes, f"listed more than once: {dupes}"
    extra = sorted(set(shown) - set(expected.values()))
    assert not extra, f"in the change log but not a Done task: {extra[:5]}"

def test_ac5_tasks_are_in_id_order_inside_each_entry():
    by_title = {render_title(title): t for t, title in _expected_titles().items()}
    for _, _, body in _entries():
        ids = [by_title[title] for title in TASK_LI.findall(body)]
        assert ids == sorted(ids)

def test_ac4_the_page_shows_no_task_id_and_no_board_word():
    for title in TASK_LI.findall(_section()):
        assert not BANNED.search(title), title
    for t, title in REWRITES.items():
        assert not BANNED.search(title), t

def test_ac4_render_title_escapes_and_keeps_code_spans():
    assert render_title("a < b & `x<y>` c") == "a &lt; b &amp; <code>x&lt;y&gt;</code> c"
    assert render_title("`docs/a_b.md`") == "<code>docs/<wbr>a_<wbr>b.md</code>"


# ---- AC 3 ------------------------------------------------------------------------------------

def test_ac3_the_section_copies_no_email_address():
    # `@AGENTS.md` (T173's title) is a file import, not an address.
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", _section())
