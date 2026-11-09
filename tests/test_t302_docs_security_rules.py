"""T302: the public docs page says how Stage 4 treats a security finding (T301's rule file).

site/docs.html has a collapsed fold-out under the skill chips that says how `code-review` treats a
security finding: it needs a boundary and a result, and a lead it cannot prove yet stays as
`needs_validation`. The guard is a function of text, so the mutation controls change bytes and show it
turn red (LR-0003).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "site" / "docs.html"
REF = ROOT / "skills" / "code-review" / "references" / "security-reviewer.md"
REF_NAME = "security-reviewer.md"


def foldouts(html):
    return re.findall(r"<details\b[^>]*>(.*?)</details>", html, re.S)


def security_foldouts(html):
    return [b for b in foldouts(html) if "<code>code-review</code>" in b and REF_NAME in b]


def docs_problems(html):
    """The fold-out about `code-review` and security; every problem with it, or one 'missing'.

    It is a fold-out, not a visible lead: the page caps visible lead text at 35 words and each section
    at 150 visible words (tests/test_site_content.py, tests/test_site_visual_first.py).
    """
    hits = security_foldouts(html)
    if len(hits) != 1:
        return [f"expected one code-review security fold-out, found {len(hits)}"]
    block = hits[0]
    out = []
    if not re.match(r"\s*<summary>[^<]+</summary>", block):
        out.append("fold-out does not open with a <summary>")
    for word in ("needs_validation", "boundary"):
        if word not in block:
            out.append(f"fold-out does not mention {word}")
    return out


def test_docs_page_says_how_a_security_finding_is_treated():
    assert docs_problems(DOCS.read_text(encoding="utf-8")) == []


def test_the_file_the_docs_name_exists():
    assert REF.exists(), f"{REF} does not exist"


def test_mutation_needs_validation_removed_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    assert docs_problems(html) == []
    bad = html.replace("needs_validation", "kept")
    assert bad != html and docs_problems(bad)


def test_mutation_the_paragraph_removed_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    hit = security_foldouts(html)[0]
    bad = html.replace(hit, "Nothing here.")
    assert bad != html and docs_problems(bad)
