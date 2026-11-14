#!/usr/bin/env python3
"""T310 oracle — `[admin]` stops when a Debate does not settle a choice.

Written by qa-expert before the change (Pillar 3); the implementer may not edit it.

  Doc text (AC 1, 2, 3, 4, 7) — `docs/claude-md/tracks.md` and `skills/resolve-question/SKILL.md`:
    * `### Stops that stay` has a bullet naming `[admin]`, defining the "unsettled Debate" and saying
      `[auto]` alone is unchanged; the same section gives one example that is "not a stop" (the
      Advocates disagree but a written rule picks one);
    * the same section holds the line shape `Paused: unsure — <question>; options: <A> / <B> [/ <C>]`,
      the `PushNotification` rule (200 characters, "not sent" is no error) and the label of the
      user's answer (`RULE`, see below);
    * `### Admin tag` (its `Stops:` paragraph), `### Debate size by Risk` and `### Known limits`
      name the "unsettled Debate"; nothing says `[admin]` stops "only for the six";
    * `SKILL.md` names the stop and stays at or below 8,192 bytes (the Codex skill cap).
  Hook (AC 5, 6) — `stop_auto_mode_check.py`, run as a subprocess in a temp project (fixtures of
  `test_stop_auto_mode_check.py`). The hook stays unchanged, so these may be green before the change:
    * an `[admin]` report with a Supervisor-written `Paused: unsure — …` line and no decision line for
      that question is not blocked, not rewritten, not double-stamped, at Risk Medium and High;
    * a `DEBATED` line under `[admin]` is judged as today (the hook cannot know Advocates disagreed);
    * AC 6 label: the user's answer is logged as `N. <answer> — RULE: <path> § <heading>` — a
      numbered line with a `RULE` that cites a written rule. The hook accepts it at Medium and High;
      a `RULE:` with no citation, or a `⚠` line, is still a choice and is blocked.

Run with: python3 -m pytest .claude/hooks/tests/test_t310_admin_unsure_stop.py -q -p no:cacheprovider
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_stop_auto_mode_check import (  # noqa: E402
    EXT_ROW, FLAG, ROOT, _blocked, _good_decisions, _project, _report, _run, _trace, _user,
    _wrote_report,
)

TRACKS = ROOT / "docs" / "claude-md" / "tracks.md"
SKILL = ROOT / "skills" / "resolve-question" / "SKILL.md"
SKILL_CAP = 8192
PAUSED_SHAPE = "Paused: unsure — <question>; options: <A> / <B> [/ <C>]"
PAUSED = "Paused: unsure — convert recurring.csv too, or leave it?; options: convert it / leave it"


def section(name):
    """The text of `### <name>` in tracks.md, up to the next `### ` or `## ` heading."""
    text = TRACKS.read_text(encoding="utf-8")
    m = re.search(rf"^### {re.escape(name)}\s*$(.*?)(?=^#{{2,3}} |\Z)", text, re.S | re.M)
    assert m, f"no `### {name}` section in tracks.md"
    return m.group(1)


# ── Doc text ──────────────────────────────────────────────────────────────────────────────────
def test_ac1_stops_that_stay_has_an_admin_bullet_defining_the_unsettled_debate():
    bullets = [b for b in re.split(r"\n(?=- )", section("Stops that stay"))
               if b.startswith("- ") and "unsettled Debate" in b]
    assert bullets, "no bullet under `### Stops that stay` mentions the unsettled Debate"
    bullet = bullets[0]
    assert "[admin]" in bullet and "Advocates" in bullet and "written rule" in bullet, bullet
    assert "[auto]" in bullet and "unchanged" in bullet, "the bullet must say `[auto]` alone is unchanged"


def test_ac7_one_example_of_a_debate_that_is_not_a_stop():
    text = section("Stops that stay")
    assert re.search(r"not a stop", text, re.I), "no example of a Debate that is not a stop"
    assert "disagree" in text, "the example must say the Advocates disagree"


def test_ac3_the_paused_line_shape_and_the_push_notification_rule_are_written():
    text = section("Stops that stay")
    assert PAUSED_SHAPE in text, f"the line shape `{PAUSED_SHAPE}` is not written"
    assert "PushNotification" in text and "200" in text, "the push rule (one line, under 200) is missing"
    assert re.search(r"not sent", text, re.I), "a `not sent` result must be said to never block the pause"


def test_ac6_the_users_answer_is_logged_with_a_named_existing_label():
    text = section("Stops that stay")
    m = re.search(r"answer[^\n]*\n?[^\n]*`RULE`|`RULE`[^\n]*\n?[^\n]*answer", text, re.I)
    assert m, "tracks.md must say the user's answer is logged with the `RULE` label"


@pytest.mark.parametrize("name", ["Debate size by Risk", "Known limits"])
def test_ac2_other_sections_name_the_unsettled_debate(name):
    assert "unsettled Debate" in section(name)


def test_ac2_the_admin_tag_stops_paragraph_names_the_new_stop():
    paragraphs = [p for p in section("Admin tag").split("\n\n") if p.startswith("Stops:")]
    assert paragraphs, "no `Stops:` paragraph in `### Admin tag`"
    assert "unsettled Debate" in paragraphs[0], paragraphs[0]


def test_ac2_no_sentence_says_admin_stops_only_for_the_old_six():
    text = TRACKS.read_text(encoding="utf-8")
    assert not re.search(r"\bonly for the (six|old)\b", text, re.I)
    for para in section("Admin tag").split("\n\n"):
        if re.search(r"stops? only for the `### Stops that stay` list", para):
            assert "unsettled Debate" in para, f"stale `only` sentence: {para}"


def test_ac4_the_skill_names_the_admin_stop_and_stays_within_the_codex_cap():
    text = SKILL.read_text(encoding="utf-8")
    assert "Paused: unsure" in text and "unsettled Debate" in text, \
        "SKILL.md does not name the `[admin]` unsettled-Debate stop (`Paused: unsure`)"
    size = len(text.encode("utf-8"))
    assert size <= SKILL_CAP, f"SKILL.md is {size} bytes, over {SKILL_CAP}"


# ── Hook behaviour (AC 5, 6) ─────────────────────────────────────────────────────────────────
def admin_project(tmp_path, risk, decisions, n_advocates, paused=True):
    """An `[admin]` task at `risk`, report built from `decisions`, with the Supervisor's own
    `Paused: unsure` line (before `Checks:`) when `paused`."""
    report = _report(decisions)
    if paused:
        report = report.replace("Checks:", f"{PAUSED}\nChecks:", 1)
    project = _project(tmp_path, [EXT_ROW.replace("High", risk)], risk=risk, review=report,
                       untagged=_trace(n_advocates),
                       transcript=[_user("move the data [admin]"), _wrote_report(tmp_path / "proj", "T951"),
                                   _wrote_report(tmp_path / "proj", "T952"),
                                   _wrote_report(tmp_path / "proj", "T953")])
    return project


@pytest.mark.parametrize("risk,n", [("Medium", 2), ("High", 3)])
def test_ac5_a_supervisor_paused_unsure_line_is_not_flagged_rewritten_or_double_stamped(tmp_path, risk, n):
    # The Debate on the unsettled question ran (n Advocates) but is NOT logged as a decision;
    # the one logged decision is a cited RULE (a DEBATED line is kept at High: D10).
    decisions = _good_decisions(n)
    project = admin_project(tmp_path, risk, decisions, n)
    review = project / "tasks" / "TASK_REVIEW_T951.md"
    before = review.read_text(encoding="utf-8")
    assert before.count("Paused: unsure") == 1 and "convert recurring.csv too" not in "".join(decisions)
    for active in (False, True):  # first fire, then the second fire (`stop_hook_active`)
        result, out = _run(project, active=active)
        assert result.returncode == 0 and out == {}, (active, out, result.stderr)
        assert review.read_text(encoding="utf-8") == before, "the hook rewrote or stamped the report"
    assert "auto-mode check failed" not in before


@pytest.mark.parametrize("risk,n", [("Medium", 2), ("High", 3)])
def test_ac5_a_report_that_holds_only_the_paused_line_for_the_question_passes(tmp_path, risk, n):
    """No decision line at all for the stopped question: the `Paused:` line is the record."""
    project = admin_project(tmp_path, risk, [_good_decisions(n)[1]], n if risk == "High" else 0)
    review = project / "tasks" / "TASK_REVIEW_T951.md"
    before = review.read_text(encoding="utf-8")
    result, out = _run(project)
    if risk == "High":  # D10 needs one 3-Advocate DEBATED line at High; the Paused line does not stand in
        assert _blocked(out) and "DEBATED" in out["reason"], out
    else:
        assert result.returncode == 0 and out == {}, (out, result.stderr)
        assert review.read_text(encoding="utf-8") == before


def test_ac5_a_debated_line_under_admin_is_judged_as_today(tmp_path):
    """The hook cannot know the Advocates disagreed: a DEBATED line with its calls passes; one
    whose Advocate calls are missing from the trace is still blocked."""
    ok = admin_project(tmp_path / "ok", "Medium", _good_decisions(2), 2, paused=False)
    _, out = _run(ok)
    assert out == {}, out
    bad = admin_project(tmp_path / "bad", "Medium", _good_decisions(2), 0, paused=False)
    _, out = _run(bad)
    assert _blocked(out) and "Advocate" in out["reason"], out


@pytest.mark.parametrize("risk,n", [("Medium", 2), ("High", 3)])
def test_ac6_the_users_answer_logged_as_a_cited_rule_passes(tmp_path, risk, n):
    answer = ("3. converted recurring.csv too (your answer) — RULE: "
              "`tasks/TASK_REVIEW_T951.md` § Auto decisions")
    project = admin_project(tmp_path, risk, _good_decisions(n) + [answer], n, paused=False)
    result, out = _run(project)
    assert result.returncode == 0 and out == {}, (out, result.stderr)


@pytest.mark.parametrize("answer", [
    "3. converted recurring.csv too (your answer) — RULE: the user said so",
    f"3. converted recurring.csv too (your answer) — RULE: tasks/TASK_REVIEW_T951.md § Auto decisions {FLAG}",
], ids=["rule-without-citation", "flagged"])
def test_ac6_an_uncited_or_flagged_answer_line_is_still_a_choice(tmp_path, answer):
    project = admin_project(tmp_path, "Medium", _good_decisions(2) + [answer], 2, paused=False)
    _, out = _run(project)
    assert _blocked(out) and "decision 3" in out["reason"], out
