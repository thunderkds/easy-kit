"""T297 — a `## CLI Effort Table` sits beside the `## CLI Model Table`: one row per CLI, one
column per Complexity level, a cell is an effort level or empty. Text-check drift guard, in the
style of test_cli_model_table.py.

  AC1 — templates/PROJECT_SPEC_template.md has `## CLI Effort Table` right after
        `## CLI Model Table`, header `CLI | Run command | C0 | C1 | C2 | C3`, claude row
        low / low / medium / high.
  AC2 — this repo's PROJECT_SPEC.md has the same section and claude row; the codex row exists
        with four empty cells.
  AC3 — every non-empty cell is one of low, medium, high, xhigh, max; a claude cell is never empty.
  AC4 — pipeline-stages.md Stage 1 item 2 asks for the effort per level, says an empty cell means
        no effort is passed, and names `## CLI Effort Table`.
  AC5 — the `## CLI Model Table` section keeps its header and cells.

Each guard has a mutation control: the check runs on a mutated copy of the text and must report.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = ("templates", "PROJECT_SPEC_template.md")
SPEC = ("PROJECT_SPEC.md",)
PIPELINE = ("docs", "claude-md", "pipeline-stages.md")
HEADER = ["CLI", "Run command", "C0", "C1", "C2", "C3"]
ALLOWED = {"low", "medium", "high", "xhigh", "max"}
CLAUDE_ROW = ["low", "low", "medium", "high"]


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _section(text, heading):
    """Body of `## heading`, up to the next `## ` heading."""
    assert "\n## %s\n" % heading in "\n" + text, "missing section: ## %s" % heading
    body = ("\n" + text).split("\n## %s\n" % heading, 1)[1]
    return re.split(r"\n## ", body, maxsplit=1)[0]


def _rows(text, heading):
    """(header cells, {cli: [cells C0..C3]}) of the table in `## heading`."""
    lines = [l.strip() for l in _section(text, heading).splitlines() if l.strip().startswith("|")]
    cells = [[c.strip() for c in l.strip("|").split("|")] for l in lines]
    header, body = cells[0], cells[2:]  # cells[1] is the |---| rule
    return header, {r[0]: r[2:] for r in body}


def _problems(text):
    """Everything wrong with the effort table in `text`; an empty list means it is sound."""
    out = []
    header, rows = _rows(text, "CLI Effort Table")
    if header != HEADER:
        out.append("header %r" % header)
    for cli, cells in rows.items():
        if len(cells) != 4:
            out.append("%s: %d level cells" % (cli, len(cells)))
        for level, cell in zip(("C0", "C1", "C2", "C3"), cells):
            if cell and cell not in ALLOWED:
                out.append("%s %s: bad effort %r" % (cli, level, cell))
            if cli == "claude" and not cell:
                out.append("claude %s: empty" % level)
    if "claude" not in rows:
        out.append("no claude row")
    return out


def _headings(text):
    return re.findall(r"^## (.+)$", text, re.MULTILINE)


def test_ac1_template_has_effort_table_after_model_table():
    tpl = _read(*TEMPLATE)
    heads = _headings(tpl)
    assert heads[heads.index("CLI Model Table") + 1] == "CLI Effort Table"
    header, rows = _rows(tpl, "CLI Effort Table")
    assert header == HEADER
    assert rows["claude"] == CLAUDE_ROW
    other = [cli for cli in rows if cli != "claude"]
    assert other, "expected a placeholder row for another CLI"
    for cli in other:
        assert rows[cli] == ["", "", "", ""], (cli, rows[cli])
    assert _problems(tpl) == []


def test_ac2_project_spec_has_claude_row_and_empty_codex_row():
    spec = _read(*SPEC)
    heads = _headings(spec)
    assert heads[heads.index("CLI Model Table") + 1] == "CLI Effort Table"
    header, rows = _rows(spec, "CLI Effort Table")
    assert header == HEADER
    assert rows["claude"] == CLAUDE_ROW
    assert rows["codex"] == ["", "", "", ""], rows["codex"]
    assert _problems(spec) == []


def test_ac3_values_are_effort_levels_and_claude_cells_filled():
    for path in (TEMPLATE, SPEC):
        assert _problems(_read(*path)) == [], path


def test_ac3_control_bad_value_is_reported():
    mutated = _read(*TEMPLATE).replace("| claude | `claude` | low | low | medium | high |",
                                       "| claude | `claude` | low | low | mediumm | high |")
    assert mutated != _read(*TEMPLATE)
    assert any("bad effort 'mediumm'" in p for p in _problems(mutated))


def test_ac3_control_empty_claude_cell_is_reported():
    mutated = _read(*SPEC).replace("| claude | `claude` | low | low | medium | high |",
                                   "| claude | `claude` | | low | medium | high |")
    assert mutated != _read(*SPEC)
    assert "claude C0: empty" in _problems(mutated)


def _stage1_item2(doc):
    return doc.split("2. **Multi-CLI Authentication**", 1)[1].split("3. **", 1)[0]


def _stage1_problems(doc):
    item2 = " ".join(_stage1_item2(doc).split())
    out = []
    if "`## CLI Effort Table`" not in item2:
        out.append("does not name ## CLI Effort Table")
    if not re.search(r"ask for the effort at each level", item2):
        out.append("does not ask for the effort per level")
    if not re.search(r"empty (effort )?cell[^.]*no effort[^.]*not a STOP", item2):
        out.append("does not say an empty cell passes no effort and is not a STOP")
    return out


def test_ac4_pipeline_stage1_asks_for_effort():
    assert _stage1_problems(_read(*PIPELINE)) == []


def test_ac4_control_heading_removed_is_reported():
    doc = _read(*PIPELINE)
    mutated = doc.replace("`## CLI Effort Table`", "the effort table")
    assert mutated != doc
    assert "does not name ## CLI Effort Table" in _stage1_problems(mutated)


def test_ac4_control_effort_per_level_removed_is_reported():
    doc = _read(*PIPELINE)
    mutated = doc.replace("Also ask for\n   the effort at each level", "Also ask for\n   the effort")
    assert mutated != doc
    assert _stage1_problems(mutated) == ["does not ask for the effort per level"]


def test_ac4_control_no_effort_not_a_stop_removed_is_reported():
    doc = _read(*PIPELINE)
    mutated = doc.replace("An empty effort cell means no effort is\n   passed; it is not a STOP.", "An empty effort cell is fine.")
    assert mutated != doc
    assert _stage1_problems(mutated) == ["does not say an empty cell passes no effort and is not a STOP"]


def test_ac5_model_table_keeps_header_and_cells():
    for path in (TEMPLATE, SPEC):
        header, rows = _rows(_read(*path), "CLI Model Table")
        assert header == HEADER
        assert rows["claude"] == ["haiku", "sonnet", "sonnet or opus", "opus"]
