"""T306 — with `[admin]`, a `blocked` auto verify run gets one retry, then the user's `/verify`.

Locked oracle of `tasks/TASK_GUIDE_T306.md`. Text pins on `### Admin tag` of
`docs/claude-md/tracks.md` (not the whole file), on the pointer lines elsewhere, and on the
`Not done:` slot of both report templates. Each pin set has a byte-changing mutation control.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ROOT / "docs" / "claude-md" / "tracks.md"
PIPELINE = ROOT / "docs" / "claude-md" / "pipeline-stages.md"
REVIEW_TEMPLATE = ROOT / "templates" / "TASK_REVIEW_template.md"
MINIMAL_TEMPLATE = ROOT / "templates" / "MINIMAL_LOG_template.md"
SECTION = re.compile(r"^### Admin tag[^\n]*\n(.*?)(?=^##+ |\Z)", re.M | re.S)
# A copy of `SLOT_UNWRITTEN[0]` in `.claude/hooks/stop_auto_verify.py` (not imported: the module
# computes its project root at import). The template slot must stay one `<auto verify: …>` line.
SLOT_PLACEHOLDER = re.compile(r"<[ \t]*auto verify:[^\n]*>")


def _norm(text):
    return " ".join(text.split())


def admin_tag(text):
    m = SECTION.search(text)
    return _norm(m.group(1)) if m else ""


# ── AC 1–6: the retry rule inside `### Admin tag` ──────────────────────────────────────────
RETRY_NEEDLES = (
    # AC 1 — once, same task, same request, no question; "once" sits in the sentence that opens the steps
    "the Supervisor re-runs the auto verify once, on the same task, in the same `[admin]` request, "
    "without asking, in these steps:",
    # AC 2 — the steps that make `--start` accept the retry
    "`--start` refuses while the result is filled for this code or the run's log exists",
    "Reset the hook's `blocked` result to the unwritten state",
    "`| verify | ☐ pass / ☐ fail / ☐ N/A |`",
    "delete only the hook's `- verify: ☐ blocked` line",
    "a line you wrote stays",
    "commit `e5c0e26`",
    "Delete that run's log, `.claude/verify-runs/<ID>-<commit>.log`",
    "Run `python3 .claude/hooks/stop_auto_verify.py --start <ID>` again",
    "The retry costs up to `CLAUDE_AUTO_VERIFY_BUDGET_USD` again",
    # AC 3 — the second `blocked` goes to the user; no third run
    "If the second run is also `blocked`, the Supervisor stops: it merges nothing, says why in one line "
    "and asks you to run `/verify <ID>`",
    "It never starts a third run",
    # AC 4 — a `fail` is never retried
    "A `fail` is never retried",
    # AC 5 — the gate keeps its rule
    "Only a hook-written pass unlocks the merge",
    "never edits a `pass` row",
    "never writes the reset row as anything but the unwritten state",
    # AC 6 — `[auto]` alone is unchanged
    "With `[auto]` alone there is no retry",
)


def check_retry(text):
    body = admin_tag(text)
    assert body, "no `### Admin tag` section"
    for needle in RETRY_NEEDLES:
        assert needle in body, needle


def test_ac1_to_ac6_admin_tag_states_the_retry_rule():
    check_retry(TRACKS.read_text(encoding="utf-8"))


def test_ac1_once_is_said_once_and_the_steps_are_numbered():
    body = admin_tag(TRACKS.read_text(encoding="utf-8"))
    assert body.count("re-runs the auto verify once") == 1
    steps = body.split("in these steps:", 1)[1]
    for n in ("1.", "2.", "3.", "4."):
        assert f" {n} " in f" {steps}", n


@pytest.mark.parametrize("cut", RETRY_NEEDLES)
def test_mutation_control_dropping_a_retry_statement_is_caught(cut):
    original = TRACKS.read_text(encoding="utf-8")
    raw = SECTION.search(original).group(0)
    words = r"\s+".join(re.escape(w) for w in cut.split())
    mutated_section, hits = re.subn(words, "", raw)
    assert hits == 1, f"needle not exactly once: {cut}"
    mutated = original.replace(raw, mutated_section)
    assert mutated.encode() != original.encode()
    check_retry(original)
    with pytest.raises(AssertionError):
        check_retry(mutated)


@pytest.mark.parametrize("cut, replacement", [
    ("re-runs the auto verify once,", "re-runs the auto verify,"),  # SC 3: delete the "once"
    ("A `fail` is never retried", ""),                               # SC 3: delete the "fail" sentence
])
def test_sc3_mutation_control_once_and_fail(cut, replacement):
    original = TRACKS.read_text(encoding="utf-8")
    raw = SECTION.search(original).group(0)
    words = r"\s+".join(re.escape(w) for w in cut.split())
    mutated_section, hits = re.subn(words, replacement, raw)
    assert hits == 1
    with pytest.raises(AssertionError):
        check_retry(original.replace(raw, mutated_section))


# ── AC 6: no retry outside `### Admin tag` except pointers to it ───────────────────────────
def test_ac6_retry_words_outside_admin_tag_are_only_admin_pointers():
    text = TRACKS.read_text(encoding="utf-8")
    m = SECTION.search(text)
    outside = text[:m.start()] + text[m.end():]
    paragraphs = [p for p in re.split(r"\n\s*\n|\n(?=- |\| )", outside) if re.search(r"\bretry\b", p)]
    assert paragraphs, "no pointer to the retry outside `### Admin tag`"
    for para in paragraphs:
        flat = _norm(para)
        assert "`[admin]`" in flat and "`### Admin tag`" in flat, flat[:200]


def test_ac6_auto_alone_keeps_verify_yours():
    lines = TRACKS.read_text(encoding="utf-8").splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith("- `Not done: merge (yours)`"))
    item = _norm(" ".join(lines[i:i + 2]))
    assert "`/verify (yours)` when the hook is not installed, its run was blocked" in item
    assert "with `[admin]`: after its one retry was blocked too, `### Admin tag`" in item


# ── AC 7: both templates keep `/verify (yours)` and name the retry ─────────────────────────
TEMPLATE_SLOT = "/verify (yours), with [admin] only after the one retry also ended blocked>"


def check_template(text, label):
    line = next((l for l in text.splitlines() if "Not done:" in l and "auto verify: running (T182)" in l),
                None)
    assert line, f"{label}: no `Not done:` slot line"
    assert "/verify (yours)" in line, label
    assert TEMPLATE_SLOT in line, label
    assert SLOT_PLACEHOLDER.search(line), f"{label}: slot no longer one `<auto verify: …>` placeholder"


@pytest.mark.parametrize("path", [REVIEW_TEMPLATE, MINIMAL_TEMPLATE], ids=["review", "minimal"])
def test_ac7_templates_keep_verify_yours_and_name_the_retry(path):
    check_template(path.read_text(encoding="utf-8"), path.name)


@pytest.mark.parametrize("path", [REVIEW_TEMPLATE, MINIMAL_TEMPLATE], ids=["review", "minimal"])
def test_ac7_mutation_control_template_without_retry_wording(path):
    original = path.read_text(encoding="utf-8")
    mutated = original.replace(", with [admin] only after the one retry also ended blocked>", ">", 1)
    assert mutated.encode() != original.encode()
    with pytest.raises(AssertionError):
        check_template(mutated, path.name)


# ── AC 8: the other places agree ───────────────────────────────────────────────────────────
POINTERS = (
    (TRACKS, "You must run it when that run is blocked (with `[admin]`, after its one retry is blocked "
             "too: `### Admin tag`) or `CLAUDE_AUTO_VERIFY=off`"),
    (TRACKS, "when the run is blocked, you must (with `[admin]`, only after its one retry is blocked too: "
             "`### Admin tag`)"),
    (TRACKS, "a blocked run falls back to `/verify (yours)` (with `[admin]`, after its one retry: "
             "`### Admin tag`)"),
    (TRACKS, "the one exception is the reset of a hook-written `blocked` result to the unwritten state, "
             "before the one `[admin]` retry (`### Admin tag`)"),
    (PIPELINE, "and does when the run is blocked (with `[admin]`, after its one retry: "
               "`docs/claude-md/tracks.md` `### Admin tag`) or `CLAUDE_AUTO_VERIFY=off`"),
)


@pytest.mark.parametrize("path, needle", POINTERS, ids=[f"p{i}" for i in range(len(POINTERS))])
def test_ac8_pointers_agree(path, needle):
    assert needle in _norm(path.read_text(encoding="utf-8")), needle


def test_ac8_old_wording_is_gone_and_agents_md_still_agrees():
    body = admin_tag(TRACKS.read_text(encoding="utf-8"))
    assert "merges nothing and reports why" not in body
    # AGENTS.md is a pinned hub (`test_agent_guide_dedup.py`); its sentence stays true: a blocked run
    # merges nothing, retry or not.
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "on `blocked` or `fail` merges nothing" in agents
