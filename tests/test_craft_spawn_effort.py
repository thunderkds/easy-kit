"""T298 — craft-spawn-prompt passes the effort from `## CLI Effort Table` at spawn.
Text-check drift guard, in the style of test_cli_model_table.py. The skill is text, so the
tests read it and `references/sandbox.md` as text; the fixture table below stands in for the
project table (T297 adds the real one).

  AC1 — step 5 looks the Complexity up in the CLI's row of `## CLI Effort Table` too.
  AC2 — an empty effort cell / no effort row passes no effort and does not stop the spawn;
        the model STOP sentences are unchanged.
  AC3 — step 5 names the allowlist; a cell outside it is never used (security control:
        the value reaches a shell command line).
  AC4 — step 6 and the Default Notification read `<cli> · <Cn> → <model> · effort <level|none>`.
  AC5 — step 6: the level is the `Agent()` `effort` parameter and `--effort <level>` in the
        sandboxed command.
  AC6 — sandbox.md: `--effort <level>` after `--model <model>`, allowed value only, and the
        command without it for `none`.
  AC7 — no hard-coded effort map or new model name.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED = {"low", "medium", "high", "xhigh", "max"}

FIXTURE_TABLE = """\
## CLI Effort Table

| CLI | Run command | C0 | C1 | C2 | C3 |
|---|---|---|---|---|---|
| claude | `claude` | low | low | medium | high |
| codex | `codex` | | | | |
| evil | `evil` | high; rm -rf ~ | | | |
"""


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _skill():
    return _read("skills", "craft-spawn-prompt", "SKILL.md")


def _sandbox():
    return _read("skills", "craft-spawn-prompt", "references", "sandbox.md")


def _step5(skill):
    return skill.split("#### 5.", 1)[1].split("#### 6.", 1)[0]


def _step6(skill):
    return skill.split("#### 6.", 1)[1].split("### Communication Protocol", 1)[0]


def _notification(skill):
    return [l for l in skill.splitlines() if l.startswith("- **Default Notification**")][0]


def _flat(text):
    return re.sub(r"\s+", " ", text)


def _fixture_row(cli):
    for line in FIXTURE_TABLE.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == cli:
            return dict(zip(["cli", "run", "C0", "C1", "C2", "C3"], cells))
    return None


def _allowlist_in(step5):
    """The values the skill's allowlist sentence names, read from the skill text."""
    m = re.search(r"[^.\n]*allowlist[^.]*\.", _flat(step5), re.IGNORECASE)
    if not m:
        return set()
    return set(re.findall(r"`(\w+)`", m.group(0)))


def _effort_for(step5, cli, level):
    """What the skill's allowlist lets through for a fixture cell: the level, or None."""
    row = _fixture_row(cli)
    cell = row[level] if row else ""
    return cell if cell in _allowlist_in(step5) else None


# -- AC1 ---------------------------------------------------------------------------------

def test_ac1_step5_reads_effort_from_the_effort_table():
    step5 = _step5(_skill())
    assert "## CLI Effort Table" in step5
    assert "CLI Model Table" in step5  # the model lookup stays in the same step
    assert "Complexity" in step5


def test_ac1_fixture_matches_the_shared_table_contract():
    header = FIXTURE_TABLE.splitlines()[2]
    assert header == "| CLI | Run command | C0 | C1 | C2 | C3 |"
    assert _fixture_row("claude")["C2"] == "medium"
    assert _fixture_row("codex")["C3"] == ""


# -- AC2 ---------------------------------------------------------------------------------

def test_ac2_empty_effort_cell_passes_no_effort_and_does_not_stop():
    step5 = _flat(_step5(_skill()))
    m = re.search(r"empty effort cell[^.]*\.", step5, re.IGNORECASE)
    assert m, "step 5 must say what an empty effort cell does"
    sentence = m.group(0).lower()
    assert "no effort" in sentence
    assert "not stop" in sentence


def test_ac2_model_stop_rules_are_unchanged():
    step5 = _flat(_step5(_skill()))
    for phrase in (
        "No row/empty cell → **STOP and ask the user** (suggest `templates/PROJECT_SPEC_template.md`); "
        "never fall back to another CLI's model, never invent one.",
        "A two-model cell (`sonnet or opus`) isn't ambiguity — pick per Risk.",
        "**No CLI named** by the caller at all → **STOP and ask which CLI will run the task**; "
        "never assume `claude` or any other CLI as a default.",
    ):
        assert phrase in step5, "model STOP sentence changed: %r" % phrase


# -- AC3 (the security control) -----------------------------------------------------------

def test_ac3_step5_names_the_allowlist():
    assert _allowlist_in(_step5(_skill())) == ALLOWED


def test_ac3_a_cell_outside_the_allowlist_is_never_used():
    step5 = _step5(_skill())
    assert _effort_for(step5, "claude", "C2") == "medium"
    assert _effort_for(step5, "evil", "C0") is None  # shell metacharacters stay out
    assert _effort_for(step5, "codex", "C3") is None  # empty cell


def test_ac3_output_form_for_a_cell_that_is_not_allowed():
    assert 'effort none (cell "<value>" not allowed)' in _step5(_skill())


def test_ac3_mutation_without_the_allowlist_sentence_fails():
    mutated = re.sub(r"[^.\n]*allowlist[^.]*\.", "", _step5(_skill()), flags=re.IGNORECASE)
    assert _allowlist_in(mutated) == set()
    assert _effort_for(mutated, "claude", "C2") is None  # nothing is allowed without it


# -- AC4 ---------------------------------------------------------------------------------

def test_ac4_output_and_notification_report_effort():
    skill = _skill()
    form = "<cli> · <Cn> → <model> · effort <level|none>"
    assert form in _step6(skill)
    notification = _notification(skill)
    assert form in notification
    # the notification keeps its STOP forms
    assert "STOP: no row/cell for <cli>" in notification
    assert "STOP: no CLI named — ask which CLI runs <Task ID>" in notification


# -- AC5 ---------------------------------------------------------------------------------

def test_ac5_step6_passes_effort_to_agent_and_to_the_sandboxed_command():
    step6 = _flat(_step6(_skill()))
    assert re.search(r"`Agent\(\)`[^.]*`effort` parameter", step6)
    assert "--effort <level>" in step6
    assert "none" in step6 and "no effort" in step6.lower()


# -- AC6 ---------------------------------------------------------------------------------

def test_ac6_sandbox_command_has_effort_after_model():
    text = _sandbox()
    commands = re.findall(r"^claude .*$", text, re.MULTILINE)
    assert len(commands) >= 2, "expect the command with effort and the command without it"
    with_effort = commands[0]
    assert "--model <model> --effort <level> -p" in with_effort
    assert "--settings templates/subagent-sandbox.settings.json" in with_effort
    assert "--add-dir <main-checkout>/.claude/hooks/.state" in with_effort
    without = [c for c in commands[1:] if "--effort" not in c]
    assert without and "--model <model> -p" in without[0]


def test_ac6_sandbox_says_allowed_value_only():
    text = _flat(_sandbox())
    m = re.search(r"[^.]*only for an allowed value[^.]*\.", text)
    assert m
    assert "--effort" in m.group(0)


# -- AC7 ---------------------------------------------------------------------------------

def test_ac7_no_hardcoded_effort_map():
    pattern = re.compile(r"C[0-3]\s*(?:→|->|=|:)\s*`?(?:low|medium|high|xhigh|max)\b")
    for text in (_skill(), _sandbox()):
        assert not pattern.search(text)


def test_ac7_effort_text_adds_no_model_name():
    step5 = _step5(_skill())
    effort_part = step5.split("CLI Effort Table", 1)[1]
    assert not re.search(r"\b(haiku|sonnet|opus)\b", effort_part, re.IGNORECASE)


def test_ac7_mutation_adding_an_effort_map_is_caught():
    pattern = re.compile(r"C[0-3]\s*(?:→|->|=|:)\s*`?(?:low|medium|high|xhigh|max)\b")
    assert pattern.search(_step5(_skill()) + "\nC0 → low\n")
