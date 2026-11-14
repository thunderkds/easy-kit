"""
T312 oracle - the "Explorer" section of site/docs.html.
Spec: tasks/TASK_GUIDE_T312.md (AC 1-9, Success Criteria 1-6).

Written first by qa-expert; the implementer may not edit it. Static checks parse the real page.
Browser checks run headless Chrome on TEMP COPIES of site/ (the real folder is only read): a probe
script is injected, clicks every chip and writes what it saw into <pre id="probe"> in the dumped DOM.
They skip, never fail, when Chrome is missing.

Run with: python3 -m pytest tests/test_site_explorer.py -q -p no:cacheprovider
"""
import html as _html
import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PAGE = os.path.join(SITE, "docs.html")
THEME = os.path.join(SITE, "theme.css")
CHROME = next((p for p in (os.environ.get("CHROME"), "/usr/bin/google-chrome", "/usr/bin/chromium",
                           "/usr/bin/chromium-browser", "/snap/bin/chromium") if p and os.path.exists(p)), None)
needs_chrome = pytest.mark.skipif(CHROME is None, reason="no Chrome binary found (set CHROME=/path/to/chrome)")

MISSING_LINE = "The explorer data is missing. The lists above show the same names."
PICK_LINE = "Pick an agent or a skill to see its steps."
STATE = re.compile(r"KANBAN|In Progress|Phase \d|\bT\d{3}\b")  # Supervisor decision: never shown by the section
DATA_RE = re.compile(r'(<!-- kit-explorer-data:start -->\s*<script type="application/json" id="kit-explorer-data">)(.*?)(</script>\s*<!-- kit-explorer-data:end -->)', re.S)
LABELS = {"agents": r"agent", "skills": r"skill", "builtins": r"built-?in"}


def _page():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


def _data(page=None):
    return json.loads(DATA_RE.search(page or _page()).group(2))


def _section_html(page=None):
    m = re.search(r'<section id="explorer">(.*?)</section>', page or _page(), re.S)
    assert m, 'site/docs.html has no <section id="explorer">'
    return m.group(1)


def _norm(s):
    return " ".join(s.split())


# ---------------------------------------------------------------- static checks (AC 1, 5, 6, 7, 9)

def test_explorer_section_follows_skills_and_has_one_h2():
    ids = re.findall(r'<section id="([^"]+)">', _page())
    assert "explorer" in ids, 'no <section id="explorer">'
    assert ids.index("explorer") == ids.index("skills") + 1, f"explorer must follow skills, order is {ids}"
    assert len(re.findall(r"<h2\b", _section_html())) == 1


def test_sidebar_lists_explorer_right_after_skills_under_the_team():
    m = re.search(r"// the team</p>\s*<ul>(.*?)</ul>", _page(), re.S)
    links = re.findall(r'<a href="(#[^"]+)">([^<]*)</a>', m.group(1))
    hrefs = [h for h, _ in links]
    assert "#explorer" in hrefs, f"no #explorer link in the team group {hrefs}"
    assert hrefs.index("#explorer") == hrefs.index("#skills") + 1
    assert ("#explorer", "Explorer") in links


def test_section_holds_no_http_asset_no_img_no_colour_value():
    body = re.sub(r"<!--.*?-->", "", _section_html(), flags=re.S)
    assert "http" not in body, "http reference inside #explorer"
    assert not re.search(r"<img\b", body)
    assert not re.search(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b(?![\w-])", body), "hex colour in #explorer"
    assert not re.search(r"\b(rgba?|hsla?)\(", body), "rgb/hsl colour in #explorer"


def test_noscript_holds_the_missing_data_line():
    ns = re.findall(r"<noscript>(.*?)</noscript>", _section_html(), re.S)
    assert any(MISSING_LINE in _html.unescape(re.sub(r"<[^>]+>", "", n)) for n in ns), "no <noscript> with the missing-data line"


def _explorer_scripts(page=None):
    page = page or _page()
    scripts = re.findall(r"<script(?![^>]*\btype=\"application/json\")(?![^>]*\bsrc=)[^>]*>(.*?)</script>", _section_html(page), re.S)
    for body in re.findall(r"<script(?![^>]*\btype=\"application/json\")(?![^>]*\bsrc=)[^>]*>(.*?)</script>", page, re.S):
        if "kit-explorer-data" in body and body not in scripts:
            scripts.append(body)
    return scripts


def test_script_inserts_strings_with_textcontent_never_innerhtml():
    scripts = _explorer_scripts()
    assert scripts, "no inline script of the explorer (one that names kit-explorer-data)"
    code = "\n".join(scripts)
    assert "kit-explorer-data" in code
    assert not re.search(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write", code), "unsafe HTML sink in the explorer script"
    assert re.search(r"textContent|createTextNode", code), "the explorer script never uses textContent/createTextNode"
    assert not re.search(r"<script[^>]*\bsrc=", _section_html()), "explorer must not load a second script file"


def test_css_has_no_transition_animation_gradient_or_blur_and_styles_the_section():
    with open(THEME, encoding="utf-8") as f:
        css = re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)
    css += "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", _page(), re.S))
    assert not re.search(r"transition|animation|@keyframes|gradient|blur\(", css)
    assert re.search(r"#explorer|\.ex-|\.explorer", css), "no CSS rule for #explorer, .ex-* or .explorer* was added"


# ---------------------------------------------------------------- browser harness

PRE = ("<script>window.__errs=[];window.addEventListener('error',function(e){__errs.push(String(e.message))});"
       "window.addEventListener('unhandledrejection',function(e){__errs.push('rejection '+e.reason)});"
       "window.__alerts=0;window.alert=function(){window.__alerts++};"
       "window.__parses=0;var __p=JSON.parse;JSON.parse=function(s){if(typeof s==='string'&&s.indexOf('\"agents\"')>=0&&"
       "s.indexOf('\"builtins\"')>=0){window.__parses++}return __p.apply(this,arguments)};</script>")

PROBE = r"""<script>
window.addEventListener('load',function(){setTimeout(function(){
var out={errs:window.__errs},sec=document.getElementById('explorer');
try{
 out.hasSection=!!sec;
 if(sec){
  var panel=sec.querySelector('[aria-live]');
  out.loadText=sec.innerText; out.parsesOnLoad=window.__parses;
  out.panelAttrs=panel?{live:panel.getAttribute('aria-live'),label:panel.getAttribute('aria-label')||panel.getAttribute('aria-labelledby'),role:panel.getAttribute('role')||panel.tagName.toLowerCase()}:null;
  var chips=[].slice.call(sec.querySelectorAll('button'));
  function ctx(b){var p=b.parentElement,c=p.cloneNode(true);[].forEach.call(c.querySelectorAll('button'),function(x){x.remove()});
   return b.innerText+' '+c.innerText+' '+(p.previousElementSibling?p.previousElementSibling.innerText:'')}
  out.loadPressed=chips.filter(function(b){return b.getAttribute('aria-pressed')==='true'}).length;
  out.allHavePressedAttr=chips.every(function(b){return b.hasAttribute('aria-pressed')});
  out.chips=chips.map(function(b){var r=b.getBoundingClientRect();return {text:b.innerText.trim(),ctx:ctx(b),w:r.width,h:r.height,type:b.type,tabindex:b.getAttribute('tabindex')}});
  out.clicks=chips.map(function(b){b.click();var q=sec.querySelector('[aria-live]');
   return {text:b.innerText.trim(),pressedSelf:b.getAttribute('aria-pressed'),pressedCount:chips.filter(function(x){return x.getAttribute('aria-pressed')==='true'}).length,
    html:q?q.innerHTML:null,text2:q?q.textContent:null}});
  if(chips.length){chips[chips.length-1].click();out.pressedAfterSecondClick=chips[chips.length-1].getAttribute('aria-pressed')}
  out.parsesAfterClicks=window.__parses; out.alerts=window.__alerts;
  var tdd=chips.filter(function(b){return /(^|[^\w-])tdd([^\w-]|$)/.test(b.innerText)})[0];
  if(tdd){tdd.click();tdd.focus();var cs=getComputedStyle(tdd);out.focus={style:cs.outlineStyle,width:cs.outlineWidth};
   var q=sec.querySelector('[aria-live]'),last=chips[chips.length-1].getBoundingClientRect(),pr=q.getBoundingClientRect();
   out.layout={panelTop:pr.top+scrollY,chipsBottom:Math.max.apply(null,chips.map(function(b){return b.getBoundingClientRect().bottom+scrollY})),
    docW:document.documentElement.scrollWidth,winW:document.documentElement.clientWidth}}
 }
}catch(e){out.probeError=String(e)}
var pre=document.createElement('pre');pre.id='probe';pre.textContent=JSON.stringify(out);document.body.appendChild(pre);
},50)});
</script>"""


def run_chrome(tmp_path, page_html, width=1280):
    """Dump the DOM of a temp copy of site/ holding page_html; return the probe's JSON."""
    work = tmp_path / ("site%d" % abs(hash(page_html + str(width))))
    shutil.copytree(SITE, work)
    head_at = page_html.index("<head>") + len("<head>")
    page_html = page_html[:head_at] + PRE + page_html[head_at:]
    end = page_html.rindex("</body>")
    (work / "docs.html").write_text(page_html[:end] + PROBE + page_html[end:], encoding="utf-8")
    proc = subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                           f"--window-size={width},900", "--virtual-time-budget=5000",
                           f"--user-data-dir={tmp_path / 'profile'}", "--dump-dom", (work / "docs.html").as_uri()],
                          capture_output=True, text=True, timeout=90)
    m = re.search(r'<pre id="probe">(.*?)</pre>', proc.stdout, re.S)
    assert m, f"probe wrote nothing; chrome stderr tail: {proc.stderr[-400:]}"
    return Probe(json.loads(_html.unescape(m.group(1))))


class Probe(dict):
    """The probe's JSON; a key the probe never wrote means #explorer does not exist, say so."""
    def __missing__(self, key):
        raise AssertionError(f"probe has no {key!r}: the #explorer section is absent or its script failed ({dict(self)})")


def with_data(page, mutate):
    data = _data(page)
    mutate(data)
    return DATA_RE.sub(lambda m: m.group(1) + "\n" + json.dumps(data, indent=1) + "\n" + m.group(3), page, count=1)


class Panel(HTMLParser):
    """Lists (tag, [item texts]) and the tag names of one panel's innerHTML."""
    def __init__(self, markup):
        super().__init__()
        self.lists, self.tags, self._open, self._li = [], [], [], None
        self.feed(markup or "")

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag in ("ol", "ul"):
            self._open.append((tag, []))
        elif tag == "li" and self._open:
            self._li = []

    def handle_endtag(self, tag):
        if tag == "li" and self._open and self._li is not None:
            self._open[-1][1].append(_norm("".join(self._li)))
            self._li = None
        elif tag in ("ol", "ul") and self._open:
            self.lists.append(self._open.pop())

    def handle_data(self, data):
        if self._li is not None:
            self._li.append(data)


def chip_index(probe, kind, name):
    """Index of the one chip that names the item (agent files carry a '-suffix' role name)."""
    assert probe["hasSection"], "no #explorer in the loaded page"
    suffix = r"(-[a-z]+)?" if kind == "agents" else ""
    pat = re.compile(r"(?<![\w-])%s%s(?![\w-])" % (re.escape(name), suffix))
    hits = [i for i, c in enumerate(probe["chips"]) if pat.search(c["text"])]
    assert len(hits) == 1, f"{kind[:-1]} {name!r}: {len(hits)} chips match, expected 1"
    return hits[0]


@pytest.fixture(scope="module")
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp("explorer")


@pytest.fixture(scope="module")
def real(tmp):
    return run_chrome(tmp, _page())


# ---------------------------------------------------------------- browser: real data (AC 2, 3, 4, 7, 8)

@needs_chrome
def test_one_button_chip_per_agent_skill_and_builtin_of_the_block(real):
    data = _data()
    assert real["hasSection"], "no #explorer in the loaded page"
    assert not real.get("probeError"), real.get("probeError")
    total = sum(len(data[k]) for k in ("agents", "skills", "builtins"))
    assert len(real["chips"]) == total, f"{len(real['chips'])} chips for {total} items"
    assert all(c["type"] == "button" and c["tabindex"] != "-1" for c in real["chips"])
    for kind in data:
        for item in data[kind]:
            c = real["chips"][chip_index(real, kind, item["name"])]
            assert re.search(LABELS[kind], c["ctx"], re.I), f"{item['name']}: no visible {kind[:-1]} label (chip + its group)"


@needs_chrome
def test_first_load_is_complete_at_rest_in_at_most_150_words(real):
    assert PICK_LINE in real["loadText"]
    assert len(real["loadText"].split()) <= 150, f"{len(real['loadText'].split())} words on first load"
    assert real["loadPressed"] == 0
    for name in ("Stage 0", "Stage 5", "Any stage"):
        assert name in real["loadText"], f"group {name!r} missing on first load"


@needs_chrome
def test_tdd_shows_an_ordered_list_of_its_steps_in_order(real):
    tdd = next(s for s in _data()["skills"] if s["name"] == "tdd")
    click = real["clicks"][chip_index(real, "skills", "tdd")]
    panel = Panel(click["html"])
    ols = [items for tag, items in panel.lists if tag == "ol"]
    assert len(ols) == 1, "tdd panel needs one <ol>"
    assert len(ols[0]) == len(tdd["steps"]) == 5
    for li, step in zip(ols[0], tdd["steps"]):
        assert step["title"] in li
    assert tdd["description"] in _norm(click["text2"])


@needs_chrome
def test_every_skill_shows_its_steps_or_sections_from_the_data(real):
    for s in _data()["skills"]:
        click = real["clicks"][chip_index(real, "skills", s["name"])]
        panel = Panel(click["html"])
        text = _norm(click["text2"])
        want = "ol" if s["kind"] == "steps" else "ul"
        lists = [items for tag, items in panel.lists if tag == want]
        assert len(lists) == 1, f"{s['name']}: expected one <{want}>, got {panel.lists}"
        assert len(lists[0]) == len(s["steps"]), s["name"]
        for li, step in zip(lists[0], s["steps"]):
            assert step["title"] in li, f"{s['name']}: step title missing or out of order"
            if not STATE.search(step["note"]):
                assert _norm(step["note"]) in li, f"{s['name']}: note of {step['title']!r} missing"
        if s["kind"] == "sections":
            assert re.search(r"sections?", text, re.I), f"{s['name']}: list not labelled as sections"


@needs_chrome
def test_every_agent_shows_startup_ordered_then_checklist(real):
    for a in _data()["agents"]:
        click = real["clicks"][chip_index(real, "agents", a["name"])]
        panel = Panel(click["html"])
        text = _norm(click["text2"])
        ols = [items for tag, items in panel.lists if tag == "ol"]
        assert ols and len(ols[0]) == len(a["startup"]), f"{a['name']}: startup <ol> wrong"
        for li, step in zip(ols[0], a["startup"]):
            assert _norm(step) in li
        at = -1
        for item in a["checklist"]:
            pos = text.find(_norm(item), at + 1)
            assert pos > at, f"{a['name']}: checklist item missing or out of order: {item[:40]!r}"
            at = pos
        assert re.search(r"startup", text, re.I) and re.search(r"checklist", text, re.I)


@needs_chrome
def test_builtin_shows_one_line_saying_the_kit_has_no_file(real):
    for b in _data()["builtins"]:
        click = real["clicks"][chip_index(real, "builtins", b["name"])]
        assert re.search(r"no file", click["text2"], re.I), f"{b['name']}: no 'no file' line"
        assert not Panel(click["html"]).lists, f"{b['name']}: a built-in has no steps to list"


@needs_chrome
def test_no_panel_shows_board_words_or_task_ids(real):
    for kind, items in _data().items():
        for it in items:
            click = real["clicks"][chip_index(real, kind, it["name"])]
            assert not STATE.search(click["text2"]), f"{it['name']}: panel shows {STATE.findall(click['text2'])}"


@needs_chrome
def test_aria_pressed_live_region_and_repeat_click(real):
    assert real["allHavePressedAttr"]
    for c in real["clicks"]:
        assert c["pressedSelf"] == "true" and c["pressedCount"] == 1, f"{c['text']}: exactly the clicked chip is pressed"
    assert real["pressedAfterSecondClick"] == "true", "a second click on a pressed chip must keep it pressed"
    p = real["panelAttrs"]
    assert p and p["live"] == "polite" and p["label"] and p["role"] in ("region", "section")


@needs_chrome
def test_focus_ring_is_visible_on_a_chip(real):
    assert real["focus"]["style"] != "none" and real["focus"]["width"] not in ("0px", "")


@needs_chrome
def test_the_77kb_block_is_parsed_once_however_many_chips_are_clicked(real):
    # The guide wants the read on first selection, not on load, but the chips (AC 2, 4) need the names
    # at load, so "not on load" cannot be pinned without forcing static or scraped chips. Pin "once".
    assert real["parsesAfterClicks"] == 1, f"block parsed {real['parsesAfterClicks']} times over {len(real['chips'])}+ clicks"


@needs_chrome
def test_no_script_error_and_no_alert_on_the_real_page(real):
    assert real["errs"] == [] and real["alerts"] == 0


@needs_chrome
@pytest.mark.parametrize("width", [768, 375])
def test_panel_goes_below_the_map_without_sideways_scroll_and_taps_reach_44px(tmp, width):
    r = run_chrome(tmp, _page(), width=width)
    lay = r["layout"]
    assert lay["panelTop"] >= lay["chipsBottom"] - 1, f"panel not below the chips at {width}px: {lay}"
    assert lay["docW"] <= lay["winW"], f"sideways scroll at {width}px: {lay}"
    if width == 375:
        small = [c["text"] for c in r["chips"] if c["h"] < 44 or c["w"] < 44]
        assert not small, f"chips under the 44px tap rule on phones: {small[:5]}"


# ---------------------------------------------------------------- browser: missing, invalid, hostile, filtered data (AC 6, 9)

@needs_chrome
@pytest.mark.parametrize("how", ["removed", "invalid"])
def test_missing_or_invalid_data_shows_one_line_and_no_script_error(tmp, how):
    page = _page()
    if how == "removed":
        page = DATA_RE.sub("", page, count=1)
    else:
        page = DATA_RE.sub(lambda m: m.group(1) + "{not json" + m.group(3), page, count=1)
    r = run_chrome(tmp, page)
    assert r["hasSection"], "no #explorer in the loaded page"
    assert not r.get("probeError"), r.get("probeError")
    assert MISSING_LINE in r["loadText"]
    assert r["errs"] == [], f"script error with {how} data: {r['errs']}"


@pytest.fixture(scope="module")
def mutated(tmp):
    if CHROME is None:
        pytest.skip("no Chrome binary found")

    def mutate(data):
        tdd = next(s for s in data["skills"] if s["name"] == "tdd")
        tdd["steps"][0]["note"] = "<img src=x onerror=alert(1)>"
        tdd["steps"][1]["note"] = "Read PROJECT_KANBAN.md and move T123 to In Progress"
        next(s for s in data["skills"] if s["name"] == "learn")["steps"] = []
    return run_chrome(tmp, with_data(_page(), mutate))


@needs_chrome
def test_hostile_step_note_renders_as_text_with_no_img(mutated):
    click = mutated["clicks"][chip_index(mutated, "skills", "tdd")]
    assert "<img src=x onerror=alert(1)>" in click["text2"]
    assert "img" not in Panel(click["html"]).tags
    assert mutated["alerts"] == 0 and mutated["errs"] == []


@needs_chrome
def test_a_step_note_naming_the_board_is_shown_as_its_title_alone(mutated):
    click = mutated["clicks"][chip_index(mutated, "skills", "tdd")]
    assert "Tracer Bullet" in click["text2"]
    for bad in ("KANBAN", "T123", "In Progress"):
        assert bad not in click["text2"]


@needs_chrome
def test_a_skill_with_no_steps_shows_its_description_and_no_empty_list(mutated):
    learn = next(s for s in _data()["skills"] if s["name"] == "learn")
    click = mutated["clicks"][chip_index(mutated, "skills", "learn")]
    assert _norm(learn["description"])[:60] in _norm(click["text2"])
    assert not Panel(click["html"]).lists
