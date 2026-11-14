#!/usr/bin/env python3
"""Write the kit's agent and skill data into site/docs.html (T311).

Reads agents/*.md, skills/*/SKILL.md and the `**Stage index**` line of AGENTS.md, and rewrites
the JSON block between the two kit-explorer-data marker comments in site/docs.html.
    python3 scripts/gen_kit_explorer.py          write the block
    python3 scripts/gen_kit_explorer.py --check  write nothing; exit 1 and print `stale: ...` when
                                                 the block no longer matches the kit
Exit 2 (one line on stderr, nothing written): a marker is missing or the stage index is unreadable.
Standard library only. The root is the parent of this script's folder.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- kit-explorer-data:start -->"
END = "<!-- kit-explorer-data:end -->"
OPEN = '<script type="application/json" id="kit-explorer-data">'
STEP_HEADS = r"(?:Workflow|Process|Steps|Protocol|Procedure)\b"
SKIP_HEADS = re.compile(r"^(Role|Karpathy|Communication|Edge Cases?|Failure Modes)", re.I)
CHECKLISTS = ("Implementation checklist", "Evaluation checklist",
              "Environment Health Checklist", "Responsibilities")

# The built-ins have no definition file, so AGENTS.md names them but cannot describe them.
# Stage and one line each; a built-in missing here still appears (stage "any").
BUILTINS = {
    "security-review": ("4", "Reviews a change for security risk; mandatory at Medium and High risk."),
    "verify": ("5", "Runs the app and checks the change works before a merge."),
    "run": ("any", "Launches the app to confirm the environment serves it."),
    "update-config": ("1", "Configures hooks and settings, for example an automated hook."),
    "fewer-permission-prompts": ("1", "Scans transcripts and allows common read and bash operations."),
}


class Unreadable(Exception):
    pass


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline=None) as f:  # CRLF -> LF
        return f.read()


def clean(s):
    s = re.sub(r"\*\*|`", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def trim(s, n):
    s = clean(s)
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0] + "…"


def title_of(heading):
    t = re.sub(r"^(?:(?:Step|Phase|Stage)\s*)?\d+[a-z]?(?=[\s.):—–-]|$)[.):—–-]*\s*", "", clean(heading), flags=re.I)
    return trim(re.sub(r"^[\s—–-]+", "", t) or clean(heading), 80)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).split("\n"):
            key, _, value = line.partition(":")
            if key.strip() in ("description", "tools"):
                meta[key.strip()] = clean(value.strip().strip('"'))
    return meta, text[m.end():] if m else text


def first_line(text):
    """The first non-blank line after a heading, without its bullet or quote mark."""
    line = next((l for l in text.split("\n") if l.strip()), "")
    return "" if line.lstrip().startswith("#") else re.sub(r"^[-*>\s]+", "", line)


def sections(body, level="## "):
    parts = re.split(rf"^{level}(.+)$", body, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def skill_steps(body):
    flow = next((t for h, t in sections(body) if re.match(STEP_HEADS, h)), "")
    start = re.search(rf"^## {STEP_HEADS}.*$", body, re.M)  # step headings may follow the section
    steps = []
    for h, t in sections(body[start.start():] if start else body, "#{3,4} "):
        if re.match(r"(?:Step|Phase|Stage)\b|\d", h, re.I):
            steps.append({"title": title_of(h), "note": trim(first_line(t), 260)})
    if len(steps) < 2:
        steps = []
        for item in re.findall(r"^\d+\. +(.+)$", flow, re.M):
            head, _, rest = item.partition(" — ")
            steps.append({"title": title_of(head), "note": trim(rest, 260)})
    if len(steps) >= 2:
        return steps[:12], "steps"
    steps = [{"title": title_of(re.sub(r"^Role: ", "", h)), "note": trim(first_line(t), 260)}
             for h, t in sections(body, "#{2,3} ") if not SKIP_HEADS.match(clean(h))]
    return steps[:12], "sections"


def skill_entry(name, stage):
    meta, body = frontmatter(read("skills", name, "SKILL.md"))
    role = re.search(r"^## Role: (.+)$", body, re.M)
    steps, kind = skill_steps(body)
    return {"name": name, "description": meta.get("description", ""),
            "role": clean(role.group(1)) if role else "",
            "kind": kind, "steps": steps, "stage": stage}


def items(text):
    """Bullets and numbered items; an indented line continues the item above."""
    found = re.findall(r"^(?:\d+\.|-) +(.*(?:\n[ \t]+\S.*)*)", text, re.M)
    return [clean(re.sub(r"^\[[ x]\] ", "", i)) for i in found]


def rows(text):
    table = [[clean(c) for c in l.strip().strip("|").split("|")]
             for l in text.split("\n") if l.strip().startswith("|")]
    sep = next((i for i, r in enumerate(table) if all(re.fullmatch(r":?-+:?", c) for c in r)), None)
    return [r for i, r in enumerate(table) if sep is None or i not in (sep - 1, sep)]


def agent_entry(name):
    meta, body = frontmatter(read("agents", name + ".md"))
    secs = sections(body)

    def under(*prefixes):
        return next((t for p in prefixes for h, t in secs if h.startswith(p)), "")

    comms = under("Communication Protocol").strip().split("\n\n")[0]
    return {"name": name, "description": meta.get("description", ""), "tools": meta.get("tools", ""),
            "startup": items(under("Mandatory Startup")),
            "checklist": next((i for i in (items(under(c)) for c in CHECKLISTS) if i), []),
            "escalation": rows(under("Complexity & escalation")),
            "skills": rows(under("Available skills")),
            "boundaries": items(under("Scope boundaries")) or items(under("Constraints")),
            "comms": clean(comms)}


def stage_index():
    """{skill name: stage} from the `**Stage index**` line of AGENTS.md, and the built-in names."""
    line = next((l for l in read("AGENTS.md").split("\n") if l.startswith("**Stage index**")), "")
    stages_part, _, tail = line.partition("Built-ins (no definition file):")
    builtins = re.findall(r"`([a-z0-9-]+)`", tail.partition("Cross-cutting")[0])
    stages = {n: s for s, group in re.findall(r"(\d)=((?:`[^`]+`,?)+)", stages_part)
              for n in re.findall(r"`([^`]+)`", group)}
    if not stages or not builtins or {str(i) for i in range(6)} - set(re.findall(r"(\d)=", stages_part)):
        raise Unreadable("cannot read the **Stage index** line of AGENTS.md")
    return stages, builtins


def build():
    stages, builtin_names = stage_index()
    skill_dirs = sorted(d for d in os.listdir(os.path.join(ROOT, "skills"))
                        if os.path.isfile(os.path.join(ROOT, "skills", d, "SKILL.md")))
    agent_files = sorted(f[:-3] for f in os.listdir(os.path.join(ROOT, "agents"))
                         if f.endswith(".md") and f != "general-agent-template.md")
    return {"agents": [agent_entry(n) for n in agent_files],
            "skills": [skill_entry(n, stages.get(n, "any")) for n in skill_dirs],
            "builtins": [{"name": n, "stage": BUILTINS.get(n, ("any",))[0],
                          "description": BUILTINS.get(n, ("", "Built-in skill, no definition file."))[1]}
                         for n in sorted(builtin_names)]}


def render(data):
    text = json.dumps(data, ensure_ascii=False, indent=1)
    text = text.replace("<!--", "\\u003c!--").replace("</", "<\\/")  # the text cannot close the block
    return f"\n{OPEN}\n{text}\n</script>\n"


def first_difference(old, new):
    """One line naming the first item that differs between two decoded blocks."""
    for kind in ("agents", "skills", "builtins"):
        a = {x["name"]: x for x in old.get(kind, [])}
        b = {x["name"]: x for x in new[kind]}
        for name in sorted(set(a) | set(b)):
            if name not in a:
                return f"{kind[:-1]} {name} is new"
            if name not in b:
                return f"{kind[:-1]} {name} was removed"
            field = next((k for k in sorted(set(a[name]) | set(b[name])) if a[name].get(k) != b[name].get(k)), None)
            if field:
                return f"{kind[:-1]} {name} changed: {field}"
    return "block text differs"


def main(argv):
    check = "--check" in argv
    path = os.path.join(ROOT, "site", "docs.html")
    with open(path, "rb") as f:
        page = f.read().decode("utf-8")
    if page.count(START) != 1 or page.count(END) != 1 or page.index(START) > page.index(END):
        print("cannot find the kit-explorer-data markers in site/docs.html", file=sys.stderr)
        return 2
    head, rest = page.split(START, 1)
    old_block, tail = rest.split(END, 1)
    try:
        data = build()
    except Unreadable as err:
        if check:
            print(f"stale: {err}")
            return 1
        print(err, file=sys.stderr)
        return 2
    block = render(data)
    if check:
        if block == old_block:
            return 0
        m = re.search(r'id="kit-explorer-data">(.*)</script>', old_block, re.S)
        try:
            old = json.loads(m.group(1)) if m else {}
        except ValueError:
            old = {}
        print(f"stale: {first_difference(old, data)}")
        return 1
    if block != old_block:
        with open(path, "wb") as f:
            f.write((head + START + block + END + tail).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
