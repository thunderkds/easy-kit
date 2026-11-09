"""T301: the security-reviewer rule file and the pointers to it.

AC1-3: skills/code-review/references/security-reviewer.md (<= 50 lines, six rules, two kit
       attack-class sections, a source line).
AC4:   the security-reviewer persona row of skills/code-review/SKILL.md links it (one level deep).
AC5:   Phase 2 keeps a failing security lead as needs_validation; Phase 3 prints `## Needs validation`;
       Phase 2 step 4 says a different verifier re-checks a security finding.
AC6:   Stage 4 item 2 of docs/claude-md/pipeline-stages.md names the file.
AC7:   SKILL.md stays inside the 8192-byte Codex skill-body cap.

Every guard is a function of text, so a mutation control can change bytes and show it turn red (LR-0003).
"""
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".claude" / "hooks" / "tests"))

REF = ROOT / "skills" / "code-review" / "references" / "security-reviewer.md"
SKILL = ROOT / "skills" / "code-review" / "SKILL.md"
STAGES = ROOT / "docs" / "claude-md" / "pipeline-stages.md"
CODEX_CAP = 8192
LINK = "references/security-reviewer.md"

RULE_HEADINGS = (
    "Boundary and result",
    "Three outcomes",
    "Severity from impact",
    "A different checker",
    "The fix",
    "Do not guess",
)
ATTACK_HEADINGS = ("Agents and prompts", "Hooks, installer and supply chain")


def _read(path):
    return path.read_text(encoding="utf-8")


def _headings(text):
    return [m.group(1).strip() for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.M)]


# ---- guards: each takes text and returns a list of problems ----------------------------------

def ref_problems(text):
    out = []
    if len(text.splitlines()) > 50:
        out.append("longer than 50 lines")
    heads = _headings(text)
    for h in RULE_HEADINGS + ATTACK_HEADINGS:
        if h not in heads:
            out.append(f"missing heading: {h}")
    return out


def verdict_problems(text):
    out = []
    for w in ("confirmed", "needs_validation", "rejected"):
        if w not in text:
            out.append(f"missing verdict word: {w}")
    for w in ("critical", "high", "medium", "low"):
        if not re.search(rf"\b{w}\b", text, re.I):
            out.append(f"missing severity word: {w}")
    if "hardening note" not in text:
        out.append("missing: hardening note")
    return out


def _section(text, heading):
    m = re.search(rf"^#{{1,6}}\s+{re.escape(heading)}\s*$\n(.*?)(?=^#{{1,6}}\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def outcome_problems(text):
    """T301 fix round: the noise gate, the merge rule and the `rejected` definition."""
    sec = _section(text, "Three outcomes")
    out = []
    if not re.search(r"cannot name its one missing fact.*dropped|dropped.*cannot name its one missing fact", sec, re.S | re.I):
        out.append("no bullet: a lead that cannot name its missing fact is dropped, not parked")
    if "never blocks a merge by itself" not in sec:
        out.append("no bullet: a needs_validation lead never blocks a merge by itself")
    if "disproves" not in sec or "raised again" not in sec:
        out.append("no one-line definition of rejected (disproves the lead; record why)")
    return out


def cap_problems(text):
    size = len(text.encode("utf-8"))
    return [f"{size} bytes is over the {CODEX_CAP}-byte Codex skill-body cap"] if size > CODEX_CAP else []


def source_problems(text):
    last = [l for l in text.splitlines() if l.strip()][-1] if text.strip() else ""
    out = []
    if "cloudflare/security-audit-skill" not in last:
        out.append("last line does not name cloudflare/security-audit-skill")
    if "MIT" not in last:
        out.append("last line does not name the MIT licence")
    if "adapted" not in last or "not copied" not in last:
        out.append("last line does not say adapted, not copied")
    return out


def row_problems(skill_text):
    rows = [l for l in skill_text.splitlines() if l.startswith("|") and "**security-reviewer**" in l]
    if len(rows) != 1:
        return [f"expected one security-reviewer row, found {len(rows)}"]
    return [] if f"({LINK})" in rows[0] else ["persona row does not link " + LINK]


def _phase(skill_text, n):
    m = re.search(rf"#### Phase {n} .*?\n(.*?)(?=\n#### Phase |\Z)", skill_text, re.S)
    return m.group(1) if m else ""


def phase_problems(skill_text):
    out = []
    p2, p3 = _phase(skill_text, 2), _phase(skill_text, 3)
    if "needs_validation" not in p2:
        out.append("Phase 2 does not name needs_validation")
    if not re.search(r"did not find|not the (finder|one that found)", p2):
        out.append("Phase 2 step 4 does not say a different verifier re-checks")
    if "## Needs validation" not in p3:
        out.append("Phase 3 has no `## Needs validation` group")
    elif p3.index("## Needs validation") < p3.index("## P3"):
        out.append("`## Needs validation` is not after P3")
    return out


def stage_problems(stages_text):
    m = re.search(r"2\. \*\*Security Review\*\*.*?(?=\n3\. \*\*)", stages_text, re.S)
    if not m:
        return ["Stage 4 item 2 not found"]
    return [] if "skills/code-review/references/security-reviewer.md" in m.group(0) else [
        "Stage 4 item 2 does not name the reference file"]


# ---- the real files ---------------------------------------------------------------------------

def test_ac1_reference_exists_with_six_rules_and_the_limit():
    assert REF.exists(), f"{REF} does not exist"
    assert ref_problems(_read(REF)) == []


def test_ac1_verdict_and_severity_words():
    assert verdict_problems(_read(REF)) == []


def test_ac2_attack_class_sections_are_present():
    heads = _headings(_read(REF))
    for h in ATTACK_HEADINGS:
        assert h in heads


def test_ac2_kit_surface_is_named():
    text = _read(REF)
    for term in (".claude/hooks/", "setup.sh", "confused", "tool-argument"):
        assert term in text, f"attack-class text does not mention {term!r}"


def test_ac1_outcome_bullets_drop_merge_and_rejected():
    assert outcome_problems(_read(REF)) == []


def test_ac3_source_line():
    assert source_problems(_read(REF)) == []


def test_ac4_persona_row_links_the_reference():
    assert row_problems(_read(SKILL)) == []


def test_ac4_pointer_suite_accepts_the_link():
    import test_skill_reference_pointers as p
    hits = [(s, t) for s, _, t in p.collect_pointers() if s == "code-review"]
    assert ("code-review", LINK) in hits
    assert os.path.exists(ROOT / "skills" / "code-review" / LINK)


def test_ac5_phase_2_and_3_text():
    assert phase_problems(_read(SKILL)) == []


def test_ac5_non_security_gate_is_kept():
    text = _read(SKILL)
    assert "remove any P1–P3 finding with confidence < 75" in text
    assert "Keep P0 at ≥ 50" in text


def test_ac6_stage_4_item_2_names_the_file():
    assert stage_problems(_read(STAGES)) == []


def test_ac7_skill_stays_under_codex_cap():
    assert cap_problems(_read(SKILL)) == []


# ---- mutation controls: change bytes, show the guard turn red -------------------------------

def _mutate(text, old, new):
    assert old in text, f"mutation target {old!r} is not in the text; the control would be vacuous"
    out = text.replace(old, new)
    assert out != text
    return out


def test_mut_verdict_words_deleted_turn_the_verdict_guard_red():
    text = _read(REF)
    assert verdict_problems(text) == []
    assert verdict_problems(text.replace("needs_validation", "")), "guard stayed green"


def test_mut_a_deleted_rule_heading_turns_the_reference_guard_red():
    text = _read(REF)
    bad = re.sub(r"^(#{1,6}\s+)Three outcomes", r"\1Outcomes", text, flags=re.M)
    assert bad != text and ref_problems(bad)


def test_mut_a_51_line_file_turns_the_limit_red():
    text = _read(REF)
    bad = text + "\n" * (51 - len(text.splitlines()) + 1) + "x\n"
    assert len(bad.splitlines()) > 50 and ref_problems(bad)


def test_mut_source_line_removed_turns_red():
    text = _read(REF)
    bad = text.replace("cloudflare/security-audit-skill", "somewhere")
    assert bad != text and source_problems(bad)


def test_mut_persona_link_typo_turns_the_link_guard_red(tmp_path):
    text = _read(SKILL)
    bad = _mutate(text, LINK, "references/security-reviewerr.md")
    assert row_problems(bad)
    # the repo's own pointer suite fails on the same mutation, on a temp copy of the skill tree
    import test_skill_reference_pointers as p
    skills = tmp_path / "skills"
    (skills / "code-review" / "references").mkdir(parents=True)
    (skills / "code-review" / "SKILL.md").write_text(bad, encoding="utf-8")
    (skills / "code-review" / "references" / "security-reviewer.md").write_text("x\n", encoding="utf-8")
    missing = [t for s, _, t in p.collect_pointers(str(skills))
               if not os.path.exists(skills / s / t)]
    assert "references/security-reviewerr.md" in missing


def test_mut_needs_validation_group_deleted_turns_the_phase_3_guard_red():
    text = _read(SKILL)
    bad = _mutate(text, "## Needs validation", "## Other")
    assert any("Phase 3" in p for p in phase_problems(bad))


def test_mut_phase_2_needs_validation_removed_turns_red():
    text = _read(SKILL)
    p2 = _phase(text, 2)
    bad = text.replace(p2, p2.replace("needs_validation", "kept"))
    assert bad != text and any("Phase 2" in p for p in phase_problems(bad))


def test_mut_stage_4_pointer_removed_turns_red():
    text = _read(STAGES)
    bad = _mutate(text, "skills/code-review/references/security-reviewer.md", "skills/code-review/SKILL.md")
    assert stage_problems(bad)


def test_mut_cap_guard_goes_red_on_an_oversize_body():
    text = _read(SKILL)
    assert cap_problems(text) == []
    bad = text + "x" * CODEX_CAP
    assert bad != text and cap_problems(bad), "cap guard stayed green on an oversize body"


@pytest.mark.parametrize("old,new", [
    ("cannot name its one missing fact", "is vague"),
    ("never blocks a merge by itself", "may block a merge"),
    ("disproves", "suggests"),
])
def test_mut_outcome_bullet_changed_turns_the_outcome_guard_red(old, new):
    text = _read(REF)
    assert outcome_problems(text) == []
    bad = _mutate(text, old, new)
    assert outcome_problems(bad), f"outcome guard stayed green after {old!r} -> {new!r}"
