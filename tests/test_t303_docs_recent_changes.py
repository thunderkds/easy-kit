"""T303: the public docs page says what T285, T288, T295 and T297-T299 changed.

site/docs.html must say:
- T297-T299: a fold-out in #agent-roles about the `## CLI Effort Table` beside the `## CLI Model Table`,
  that `craft-spawn-prompt` passes the effort at spawn, and the one-step raise on a move up or a `verify`
  fail;
- T285: the step-limit hook row counts per sub-agent run, not per task;
- T295: the `[admin]` text says the merge and push refuse a repo config key that can run code;
- T288: the repository layout lists `tasks/attempts.tsv`.
The guards are functions of text, so the mutation controls change bytes and show them turn red (LR-0003).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "site" / "docs.html"


def section(html, sid):
    m = re.search(rf'<section id="{sid}">(.*?)</section>', html, re.S)
    return m.group(1) if m else ""


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text.replace("<wbr>", "")))


def effort_problems(html):
    blocks = [b for b in re.findall(r"<details\b[^>]*>(.*?)</details>", section(html, "agent-roles"), re.S)
              if "CLI Effort Table" in b]
    if len(blocks) != 1:
        return [f"expected one #agent-roles fold-out about the CLI Effort Table, found {len(blocks)}"]
    block = blocks[0]
    out = []
    if not re.match(r"\s*<summary>[^<]+</summary>", block):
        out.append("fold-out does not open with a <summary>")
    text = plain(block)
    for word in ("CLI Model Table", "craft-spawn-prompt", "one step", "verify", "moves up"):
        if word not in text:
            out.append(f"effort fold-out does not mention {word!r}")
    return out


def step_limit_problems(html):
    rows = [r for r in re.findall(r"<tr>(.*?)</tr>", section(html, "hooks"), re.S)
            if "pre_agent_step_limit.py" in plain(r)]
    if len(rows) != 1:
        return [f"expected one step-limit hook row, found {len(rows)}"]
    text = plain(rows[0])
    out = []
    if "a task's tool call" in text:
        out.append("step-limit row still counts per task (T285 counts per sub-agent run)")
    if "sub-agent run" not in text:
        out.append("step-limit row does not say it counts per sub-agent run")
    return out


def admin_problems(html):
    text = plain(section(html, "tracks"))
    if "[admin]" not in text:
        return ["#tracks does not mention [admin]"]
    if not re.search(r"\[admin\][^.]*\..*?repo config[^.]*run code", text, re.S):
        return ["#tracks does not say [admin] merge and push refuse repo config that can run code"]
    return []


def layout_problems(html):
    text = plain(section(html, "repository-layout"))
    return [] if "tasks/attempts.tsv" in text else ["repository layout does not list tasks/attempts.tsv"]


def all_problems(html):
    return effort_problems(html) + step_limit_problems(html) + admin_problems(html) + layout_problems(html)


def test_docs_page_says_what_t285_t288_t295_and_t297_t299_changed():
    assert all_problems(DOCS.read_text(encoding="utf-8")) == []


def test_the_files_the_docs_name_exist():
    for rel in ("skills/craft-spawn-prompt/SKILL.md", ".claude/hooks/pre_agent_step_limit.py",
                "scripts/attempt_log.py"):
        assert (ROOT / rel).exists(), rel


def test_mutation_effort_table_removed_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    bad = html.replace("CLI Effort Table", "CLI Table")
    assert bad != html and effort_problems(bad)


def test_mutation_old_step_limit_wording_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    bad = html.replace("sub-agent run", "task")
    assert bad != html and step_limit_problems(bad)


def test_mutation_admin_refusal_removed_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    bad = html.replace("repo config", "settings")
    assert bad != html and admin_problems(bad)


def test_mutation_attempts_row_removed_turns_the_guard_red():
    html = DOCS.read_text(encoding="utf-8")
    bad = html.replace("attempts.tsv", "")
    assert bad != html and layout_problems(bad)
