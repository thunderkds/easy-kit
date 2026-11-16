"""T322: site/docs.html explains [ticket], [admin], [stop] inside the #tracks Details block."""
import html as _html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "site", "docs.html")


def _para():
    src = open(PAGE, encoding="utf-8").read()
    sec = src[src.index('<section id="tracks"'):]
    sec = sec[:sec.index("</section>")]
    det = sec[sec.index('<details class="more">'):sec.index("</details>")]
    m = re.search(r"<p>\s*<strong>Session tags</strong>.*?</p>", det, re.S)
    assert m, "no Session tags <p> inside the #tracks details block"
    return m.group(0)


def _text():
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", "", _para())).split())


def test_three_tags_in_code():
    p = _para()
    for t in ("[ticket]", "[admin]", "[stop]"):
        assert f"<code>{t}</code>" in p


def test_scope_and_end():
    t = _text()
    assert "whole session" in t and "one request" in t
    assert "[stop]" in t and "resume" in t and "/compact" in t


def test_loop_and_push():
    t = _text()
    for w in ("one ready ticket", "auto verify", "origin", "main", "blocked", "pull request"):
        assert w in t


def test_permissions():
    t = _text()
    assert "autonomous" in t and "bypassPermissions" in t and "settings-setup" in t
