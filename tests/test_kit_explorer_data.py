"""
T311 oracle - the generator that writes the kit's agent and skill data into site/docs.html.
Spec: tasks/TASK_GUIDE_T311.md (AC 1-6, Success Criteria 1-6).

Written first by qa-expert; the implementer may not edit it. Every write runs in a temp copy
of the repo (agents/, skills/, AGENTS.md, site/docs.html, the script). The real checkout is
only ever read, or run with --check, which never writes.

Run with: python3 -m pytest tests/test_kit_explorer_data.py -q -p no:cacheprovider
"""
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_REL = os.path.join("scripts", "gen_kit_explorer.py")
START = "<!-- kit-explorer-data:start -->"
END = "<!-- kit-explorer-data:end -->"
BUILTINS = {"security-review", "verify", "run", "update-config", "fewer-permission-prompts"}


def run(repo, *args):
    return subprocess.run([sys.executable, os.path.join(repo, SCRIPT_REL), *args],
                          cwd=repo, capture_output=True, text=True)


def read(repo, rel):
    with open(os.path.join(repo, rel), "rb") as f:
        return f.read()


def write(repo, rel, data):
    with open(os.path.join(repo, rel), "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def block_of(page):
    """The text between the two marker comments (page is str)."""
    assert page.count(START) == 1 and page.count(END) == 1
    return page.split(START, 1)[1].split(END, 1)[0]


def data_of(repo):
    block = block_of(read(repo, "site/docs.html").decode("utf-8"))
    m = re.fullmatch(r'\s*<script type="application/json" id="kit-explorer-data">(.*)</script>\s*',
                     block, re.S)
    assert m, "the block is not exactly one kit-explorer-data script"
    return json.loads(m.group(1))


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def make_copy(dest):
    for rel in ("agents", "skills"):
        shutil.copytree(os.path.join(ROOT, rel), os.path.join(dest, rel))
    os.makedirs(os.path.join(dest, "site"))
    os.makedirs(os.path.join(dest, "scripts"))
    shutil.copy(os.path.join(ROOT, "AGENTS.md"), dest)
    shutil.copy(os.path.join(ROOT, "site", "docs.html"), os.path.join(dest, "site"))
    script = os.path.join(ROOT, SCRIPT_REL)
    if os.path.exists(script):
        shutil.copy(script, os.path.join(dest, "scripts"))
    return str(dest)


@pytest.fixture
def repo(tmp_path):
    """A temp copy of the repo with the block freshly generated."""
    dest = make_copy(tmp_path / "repo")
    done = run(dest)
    assert done.returncode == 0, done.stdout + done.stderr
    return dest


def new_skill(repo, name, front, body=""):
    os.makedirs(os.path.join(repo, "skills", name))
    write(repo, f"skills/{name}/SKILL.md", f"---\nname: {name}\n{front}\n---\n\n{body}")


# --- Success Criterion 1: markers, check mode, idempotence (AC 1, 5, 6) -------------------

def test_real_page_has_one_json_block_between_markers():
    page = open(os.path.join(ROOT, "site", "docs.html"), encoding="utf-8").read()
    assert page.count(START) == 1 and page.count(END) == 1
    assert page.index(START) < page.index(END)
    data = data_of(ROOT)
    assert {"agents", "skills", "builtins"} <= set(data)


def test_check_passes_silently_on_the_repo():
    done = run(ROOT, "--check")
    assert (done.returncode, done.stdout, done.stderr) == (0, "", "")


def test_generator_is_idempotent_and_touches_only_the_block(tmp_path):
    dest = make_copy(tmp_path / "repo")
    original = read(dest, "site/docs.html")
    assert run(dest).returncode == 0
    once = read(dest, "site/docs.html")
    assert run(dest).returncode == 0
    assert read(dest, "site/docs.html") == once
    head, tail = original.split(START.encode(), 1)[0], original.split(END.encode(), 1)[1]
    assert once.startswith(head + START.encode()) and once.endswith(END.encode() + tail)


def test_check_never_writes(tmp_path):
    dest = make_copy(tmp_path / "repo")
    before = read(dest, "site/docs.html")
    assert run(dest, "--check").returncode == 0
    assert read(dest, "site/docs.html") == before


# --- Success Criteria 2, 3: --check goes stale (AC 5) ------------------------------------

def test_changed_description_is_stale_and_names_the_skill(repo):
    path = "skills/tdd/SKILL.md"
    text = read(repo, path).decode("utf-8")
    text, n = re.subn(r"^description: .*$", "description: A completely different line.", text,
                      count=1, flags=re.M)
    assert n == 1
    write(repo, path, text)
    done = run(repo, "--check")
    lines = done.stdout.splitlines()
    assert done.returncode == 1 and len(lines) == 1
    assert lines[0].startswith("stale:") and "tdd" in lines[0]


def test_new_skill_is_stale(repo):
    new_skill(repo, "zz-new-skill", "description: A new skill.")
    done = run(repo, "--check")
    assert done.returncode == 1 and done.stdout.startswith("stale:")


def test_removed_skill_is_stale(repo):
    shutil.rmtree(os.path.join(repo, "skills", "tdd"))
    done = run(repo, "--check")
    assert done.returncode == 1 and done.stdout.startswith("stale:")


def test_changed_stage_index_line_is_stale_and_unreadable_index_exits_2(repo):
    text = read(repo, "AGENTS.md").decode("utf-8")
    broken = text.replace("**Stage index**", "**Stage list**")
    assert broken != text
    write(repo, "AGENTS.md", broken)
    assert run(repo, "--check").returncode == 1
    assert run(repo, "--check").stdout.startswith("stale:")
    before = read(repo, "site/docs.html")
    done = run(repo)
    assert done.returncode == 2 and (done.stdout + done.stderr).strip()
    assert read(repo, "site/docs.html") == before


def test_crlf_source_gives_the_same_output(repo):
    path = "skills/tdd/SKILL.md"
    text = read(repo, path).decode("utf-8")
    write(repo, path, text.replace("\r\n", "\n").replace("\n", "\r\n"))
    done = run(repo, "--check")
    assert (done.returncode, done.stdout) == (0, "")


@pytest.mark.parametrize("marker", [START, END])
def test_missing_marker_exits_2_and_writes_nothing(repo, marker):
    page = read(repo, "site/docs.html").decode("utf-8")
    write(repo, "site/docs.html", page.replace(marker, ""))
    before = read(repo, "site/docs.html")
    done = run(repo)
    assert done.returncode == 2
    assert read(repo, "site/docs.html") == before


# --- Success Criterion 4: content (AC 2, 3, 4) -------------------------------------------

def test_every_skill_and_agent_appears_once_sorted():
    data = data_of(ROOT)
    skills = sorted(d for d in os.listdir(os.path.join(ROOT, "skills"))
                    if os.path.isfile(os.path.join(ROOT, "skills", d, "SKILL.md")))
    agents = sorted(f[:-3] for f in os.listdir(os.path.join(ROOT, "agents"))
                    if f.endswith(".md") and f != "general-agent-template.md")
    assert [s["name"] for s in data["skills"]] == skills
    assert [a["name"] for a in data["agents"]] == agents


def test_field_shapes():
    data = data_of(ROOT)
    for s in data["skills"]:
        assert {"name", "description", "role", "kind", "steps", "stage"} <= set(s)
        assert s["kind"] in ("steps", "sections") and len(s["steps"]) <= 12
        assert str(s["stage"]) in {"0", "1", "2", "3", "4", "5", "any"}
        for step in s["steps"]:
            assert set(step) >= {"title", "note"}
            assert not re.match(r"^\s*[-–—]|^\s*\d+[.)]", step["title"])
    for a in data["agents"]:
        assert {"name", "description", "tools", "startup", "checklist", "escalation",
                "skills", "boundaries", "comms"} <= set(a)


def test_stage_follows_the_agents_md_index_and_unlisted_goes_to_any():
    by_name = {s["name"]: str(s["stage"]) for s in data_of(ROOT)["skills"]}
    assert by_name["brainstorming"] == "0" and by_name["tdd"] == "3"
    assert by_name["code-review"] == "4" and by_name["ship"] == "5"
    assert by_name["compact-memory"] == "any"


def test_unindexed_skill_lands_in_any_and_no_front_matter_keeps_empty_role(repo):
    new_skill(repo, "zz-unlisted", "description: Not in the stage index.")
    os.makedirs(os.path.join(repo, "skills", "zz-bare"))
    write(repo, "skills/zz-bare/SKILL.md", "Just text, no front matter.\n")
    assert run(repo).returncode == 0
    by_name = {s["name"]: s for s in data_of(repo)["skills"]}
    assert str(by_name["zz-unlisted"]["stage"]) == "any"
    assert str(by_name["zz-bare"]["stage"]) == "any" and by_name["zz-bare"]["role"] == ""


def test_builtins_listed_with_stage_and_no_steps():
    data = data_of(ROOT)
    assert {b["name"] for b in data["builtins"]} == BUILTINS
    for b in data["builtins"]:
        assert b.get("description") and "stage" in b and not b.get("steps")
    assert BUILTINS.isdisjoint(s["name"] for s in data["skills"])


def test_block_is_deterministic_and_safe_to_embed():
    page = open(os.path.join(ROOT, "site", "docs.html"), encoding="utf-8").read()
    raw = block_of(page)
    inner = raw.split(">", 1)[1].rsplit("</script>", 1)[0]
    assert "</" not in inner
    for s in strings(json.loads(inner)):
        assert "/home/" not in s
        assert not re.search(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", s)
    assert not re.search(r'"(bytes|size|generated|timestamp)"', inner)


# --- Success Criterion 5: hostile text stays text (AC 4) ---------------------------------

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.ids.append(dict(attrs).get("id"))


def test_hostile_text_cannot_close_the_block(repo):
    hostile = "Evil </script><b>x</b> and --> end"
    new_skill(repo, "zz-hostile", f'description: "{hostile}"',
              f"## Role: Hostile\n\n## Workflow\n\n### Step 1: One\n{hostile}\n\n### Step 2: Two\nok\n")
    assert run(repo).returncode == 0
    page = read(repo, "site/docs.html").decode("utf-8")
    block = block_of(page)
    assert block.count("</script>") == 1
    parser = Scripts()
    parser.feed(page)
    assert parser.ids.count("kit-explorer-data") == 1
    entry = {s["name"]: s for s in data_of(repo)["skills"]}["zz-hostile"]
    assert "</script><b>x</b>" in entry["description"] and "-->" in entry["description"]
    assert "</script><b>x</b>" in json.dumps(entry["steps"], ensure_ascii=False)
    assert run(repo, "--check").returncode == 0
