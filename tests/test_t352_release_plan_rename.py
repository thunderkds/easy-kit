"""T352 — the kit's Stage 5 skill is `release-plan`, not `ship`.

Claude Code's built-in `/ship` (Claude Ship) shadows a project skill named `ship` in interactive
sessions, so the kit's `Skill({ skill: "ship" })` stopped reaching the kit's release planner.
History (tasks/, memory/, docs/archive, brainstorming logs, ADRs/DDRs/PRDs, CLAUDE_LEGACY.md) keeps the
old name on purpose. The verb "ship" in prose is not the skill and stays.
"""
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LIVE = ("AGENTS.md", "CLAUDE.md", ".cursor/rules", "agents", "packs", "templates", "skills",
        "docs/claude-md", "docs/MULTI_AGENT.md", "README.md", "RUNBOOK.md", "PROJECT_SPEC.md",
        "site", ".claude/hooks", "plugin", "commands", "scripts", "MANIFEST")

# Forms that name the skill (not the verb): a code span, a Skill() call, a path, "ship skill",
# a site chip, and the explorer's JSON name.
SKILL_NAME = re.compile(
    r'`ship`|skill: "ship"|skills/ship\b|\bship/SKILL\.md|`ship` skill|\bship skill\b'
    r'|<code>ship</code>|class="chip">ship<|\bship <span class="visually-hidden">'
    r'|"name": "ship"')


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _live_files():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "--", *LIVE], capture_output=True,
                         text=True, check=True).stdout.split()
    return [p for p in out if not p.startswith(".claude/hooks/tests/")
            and os.path.isfile(os.path.join(ROOT, p))]


def test_ac1_skill_is_release_plan():
    assert not os.path.exists(os.path.join(ROOT, "skills/ship"))
    text = _read("skills/release-plan/SKILL.md")
    front = text.split("---")[1]
    assert re.search(r"^name: release-plan$", front, re.M)
    assert re.search(r"^description: .*not Claude Code's `/ship`", front, re.M)


def test_ac2_no_live_file_names_the_skill_ship():
    hits = []
    for rel in _live_files():
        try:
            text = _read(rel)
        except UnicodeDecodeError:
            continue
        if rel == "site/docs.html":  # the Change log copies past board titles: history
            start = text.index('<section id="changelog">')
            text = text[:start] + "\n" * text[start:text.index("</section>", start)].count("\n") \
                + text[text.index("</section>", start):]
        for n, line in enumerate(text.splitlines(), 1):
            if SKILL_NAME.search(line):
                hits.append(f"{rel}:{n}: {line.strip()[:120]}")
    assert hits == [], "\n".join(hits)


def test_ac3_doctrine_calls_release_plan():
    for rel in ("AGENTS.md", "docs/claude-md/pipeline-stages.md", "docs/claude-md/tracks.md"):
        assert 'Skill({ skill: "release-plan" })' in _read(rel), rel
    agents = _read("AGENTS.md")
    assert "Stage 5 `release-plan` produces the release/rollback plan" in agents
    assert "5=`ship`" not in agents and "`release-plan`,`delivery-report`" in agents
    tracks = _read("docs/claude-md/tracks.md")
    assert "- `release-plan`.\n" in tracks  # `### Never in auto mode`


def test_ac5_plugin_and_site_serve_release_plan():
    assert os.path.isfile(os.path.join(ROOT, "plugin/skills/release-plan/SKILL.md"))
    site = _read("site/docs.html")
    assert '"name": "release-plan"' in site and '"name": "ship"' not in site
