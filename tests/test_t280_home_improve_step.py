"""
T280 - the home page journey gets a sixth step, "You improve it" (self-review).
Spec: tasks/TASK_GUIDE_T280.md (AC 1, 2, 4, 5).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import test_site_story as story  # noqa: E402

FORBIDDEN = ("autonomous", "self-improving", "automatic", "automatically")


def _steps():
    return re.findall(r"<li\b([^>]*)>(.*?)</li>", _journey_list(), re.DOTALL)


def _journey_list():
    body = story.section(story.index_html(), "journey")
    return re.search(r"<ol\b[^>]*>(.*?)</ol>", body, re.DOTALL).group(1)


def _improve_step():
    steps = _steps()
    assert len(steps) == 6, f"journey has {len(steps)} steps, want 6"
    return steps[5]


def _span(inner, cls):
    return re.search(rf'<span class="{cls}">(.*?)</span>', inner, re.DOTALL).group(1)


def test_sixth_step_is_an_easy_kit_step_linking_to_the_docs_diagram():
    _, inner = _improve_step()
    assert _span(inner, "flow-key").strip() == "Easy Kit"
    title = _span(inner, "flow-title")
    assert re.fullmatch(r'\s*<a href="docs\.html#skills">It proposes fixes</a>\s*', title), title
    assert re.fullmatch(r"\s*<code>/self-review</code> \(optional\)\s*", _span(inner, "flow-desc"))
    assert 'id="skills"' in story.docs_html(), "the link target must exist in docs.html"


def test_sixth_step_is_linked_but_neither_yours_nor_the_outcome():
    classes = _improve_step()[0]
    names = re.search(r'class="([^"]*)"', classes).group(1).split()
    assert names == ["flow-node", "is-link"], names


def test_the_outcome_stays_on_you_merge_and_steps_one_to_five_are_unchanged():
    steps = _steps()
    outcomes = [i for i, (attrs, _) in enumerate(steps) if "is-outcome" in attrs]
    assert outcomes == [4], outcomes
    titles = [" ".join(story.visible_words(_span(inner, "flow-title"))) for _, inner in steps]
    assert titles[:5] == ["You ask", "It plans", "Agents build", "It checks", "You merge"], titles
    keys = [_span(inner, "flow-key") for _, inner in steps]
    assert keys == ["Your step", "Easy Kit", "Easy Kit", "Easy Kit", "Your step", "Easy Kit"], keys


def test_step_text_claims_nothing_the_skill_does_not_do():
    _, inner = _improve_step()
    text = story.heard_text(inner).lower()
    for word in FORBIDDEN:
        assert word not in text, f"{word!r} in the improve step"
    assert "approve" not in text and "reject" not in text and "up to 3" not in text
