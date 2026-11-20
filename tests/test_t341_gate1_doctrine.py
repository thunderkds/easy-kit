#!/usr/bin/env python3
"""T341 — the doctrine side: Gate 1, DDR-0011, the reviewer spawn's shape, the sign-off, the limits.

AC 1  — `AGENTS.md` Hard-Stop Gate 1 keeps its title; the Supervisor writes the code on the extended
        track; implementer spawns only for parallel or oversized C3 work; one fresh reviewer spawn,
        required by the merge gate. The Stage 3 and Stage 4 lines match.
AC 2  — DDR-0011 supersedes DDR-0004 and records the evidence and the user's choice.
AC 3  — `pipeline-stages.md` gives the reviewer spawn's exact shape, and that shape fits the trace
        record's 300-character summary as the merge gate reads it.
AC 7  — `merge_gate_guard.AUTHORISED_TASKS` names T341; every gate commit names an authorised task.
AC 8  — `tracks.md` names the merge-gate condition and the limit (not a proof).
AC 10 — no live doc still says the Supervisor never writes implementation code.

Run with: python3 -m pytest tests/test_t341_gate1_doctrine.py -v
"""
import json
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / ".claude" / "hooks"
AGENTS_MD = ROOT / "AGENTS.md"
LEGACY_MD = ROOT / "CLAUDE_LEGACY.md"
PIPELINE_MD = ROOT / "docs" / "claude-md" / "pipeline-stages.md"
TRACKS_MD = ROOT / "docs" / "claude-md" / "tracks.md"
DDR_0004 = ROOT / "docs" / "ddr" / "0004-uphold-hard-stop-gate-1-over-spawn-elimination.md"
DDR_0011 = ROOT / "docs" / "ddr" / "0011-supervisor-implements-reviewer-spawn-gated.md"
GATE_BASE = "62b45ec"  # T341's branch base: the gate as T341 found it

sys.path.insert(0, str(HOOKS / "tests"))
import merge_gate_guard as guard  # noqa: E402


def _read(path):
    return Path(path).read_text(encoding="utf-8")


def _norm(text):
    return re.sub(r"\s+", " ", text)


def _gate():
    """The merge gate module, loaded without running its bottom-of-file `main()`."""
    path = HOOKS / "pre_bash_block_unsafe_merge.py"
    source = _read(path)
    assert "\nmain()" in source
    module = types.ModuleType("merge_gate_t341_doctrine")
    module.__file__ = str(path)
    exec(compile(source.replace("\nmain()", "\n"), str(path), "exec"), module.__dict__)
    return module


def _section(text, heading):
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


# ---- AC 1 ------------------------------------------------------------------------------------

def _gate1():
    m = re.search(r"^1\. \*\*.+$", _read(AGENTS_MD), re.M)
    assert m, "Hard-Stop Gate 1 not found"
    return m.group(0)


def test_ac1_gate1_keeps_its_title_and_the_guide_first_rule():
    gate1 = _gate1()
    assert gate1.startswith("1. **No TASK_GUIDE = no work.**")
    assert "must create one through Stage 2 before any code is written" in gate1


def test_ac1_gate1_no_longer_forbids_the_supervisor_to_write_code():
    gate1 = _gate1()
    assert "must never write implementation code" not in gate1
    assert ("On the extended track the Supervisor writes the code itself, in the task's worktree, "
            "test first") in gate1
    assert "only for 2+ independent tasks at once, or for a C3 task too big for one context" in gate1
    assert "one fresh-context reviewer spawn (`Reviewer: <ID>`)" in gate1
    assert "the merge gate refuses the merge" in gate1 and "DDR-0011" in gate1
    assert "On the minimal track the Supervisor writes the code itself" in gate1  # T178 kept


def test_ac1_the_stage_3_and_stage_4_lines_match():
    text = _read(AGENTS_MD)
    stage3 = re.search(r"^- \*\*Stage 3\*\*.+$", text, re.M).group(0)
    stage4 = re.search(r"^- \*\*Stage 4\*\*.+$", text, re.M).group(0)
    assert "the Supervisor implements" in stage3 and "implementer spawn only" in stage3
    assert 'description: "Reviewer: <ID>"' in stage4 and "required by the merge gate" in stage4


# ---- AC 2 ------------------------------------------------------------------------------------

def test_ac2_ddr_0011_supersedes_ddr_0004_with_its_evidence():
    ddr = _norm(_read(DDR_0011))
    assert ddr.startswith("# 0011.")
    assert "**Status**: Accepted" in ddr and "supersedes DDR-0004" in ddr
    for evidence in ("15,669", "~47k", "kit-arms", "2026-11-20 replay"):
        assert evidence in ddr, evidence
    assert "should start the enhance now" in ddr and "[admin]" in ddr  # the user's choice
    for heading in ("## Context", "## Decision", "## Alternatives Considered", "## Consequences"):
        assert heading in ddr


def test_ac2_ddr_0004_status_reads_superseded():
    assert re.search(r"^\*\*Status\*\*: Superseded by DDR-0011$", _read(DDR_0004), re.M)


# ---- AC 3 ------------------------------------------------------------------------------------

def test_ac3_stage_3_says_who_implements():
    stage3 = _norm(_section(_read(PIPELINE_MD), "## Stage 3:"))
    assert "on the extended track the Supervisor writes the code itself" in stage3
    assert "An implementer spawn only for 2+ independent tasks at once" in stage3


def test_ac3_stage_4_gives_the_reviewer_spawns_exact_shape():
    stage4 = _norm(_section(_read(PIPELINE_MD), "## Stage 4:"))
    gate = _gate()
    assert 'Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: ' in stage4
    assert f"`{gate.REVIEWER_PROMPT_PREFIX}`" in stage4
    assert f'prompt: "{gate.REVIEWER_PROMPT_PREFIX}\\nTask ID: <ID>\\nCommit: <40-hex>' in stage4
    assert "first 300 characters" in stage4 and "MAX_SUMMARY_LEN" in stage4
    assert "never the Supervisor's reasoning" in stage4
    assert "`security-review`" in stage4 and "`tasks/TASK_REVIEW_<ID>.md`" in stage4
    assert "in the foreground" in stage4


def test_ac3_the_documented_prompt_fits_the_summary_the_gate_reads():
    """Fill the documented example the way a Supervisor would, record it the way
    `post_tool_trace.summarize` does (`json.dumps(tool_input)[:300]`), and read it back."""
    gate = _gate()
    trace_hook = _read(HOOKS / "post_tool_trace.py")
    limit = int(re.search(r"^MAX_SUMMARY_LEN = (\d+)$", trace_hook, re.M).group(1))
    example = re.search(r'prompt: "([^"]+)" \}\)', _read(PIPELINE_MD)).group(1)
    tid, sha = "PROJ-12345", "c" * 40
    prompt = (example.replace("\\n", "\n").replace("<ID>", tid).replace("<40-hex>", sha)
              .replace("…", "Run code-review and security-review. " * 20))
    tool_input = {"subagent_type": "easy-kit:qa-expert", "description": f"Reviewer: {tid}",
                  "prompt": prompt}
    record = {"tool_name": "Agent", "summary": json.dumps(tool_input)[:limit]}
    assert len(json.dumps(tool_input)) > limit  # the cut really happens
    assert gate.reviewer_commit(record, tid) == sha


# ---- AC 7 ------------------------------------------------------------------------------------

def test_ac7_t341_is_authorised_with_its_rule_and_sign_off():
    assert "T341" in guard.AUTHORISED_TASKS
    source = _read(HOOKS / "tests" / "merge_gate_guard.py")
    entry = source[source.index("#   T341"):source.index("AUTHORISED_TASKS =")]
    assert "trace_shows_review" in entry and "`[admin]`" in entry and "2026-11-20" in entry


def test_ac7_every_gate_commit_since_the_base_names_an_authorised_task():
    assert guard.unauthorised_gate_commits(ROOT, GATE_BASE) == []


# ---- AC 8 ------------------------------------------------------------------------------------

def test_ac8_tracks_names_the_merge_gate_condition():
    text = _norm(_read(TRACKS_MD))
    assert "**The merge gate requires it**" in text and "`trace_shows_review`" in text
    assert "A minimal-track task has no guide, so the gate does not check it." in text


def test_ac8_known_limits_say_the_record_is_not_a_proof():
    limits = _norm(_section(_read(TRACKS_MD), "### Known limits"))
    assert "**The reviewer record raises the bar; it is not a proof (T341).**" in limits
    assert "an agent's own Python can still write a matching record, as for T148 and T182" in limits


# ---- AC 10 -----------------------------------------------------------------------------------

LIVE = [AGENTS_MD, LEGACY_MD, ROOT / ".cursor" / "rules" / "agent-base.mdc", ROOT / "README.md",
        ROOT / "site" / "docs.html", ROOT / "site" / "index.html"]
LIVE_DIRS = ["docs/claude-md", "agents", "templates", "skills"]
STALE = re.compile(r"never write implementation code|Implementation = sub-agent|"
                   r"sub-agents? implements?\b", re.I)


def test_ac10_no_live_doc_says_the_supervisor_never_writes_implementation_code():
    paths = list(LIVE)
    for rel in LIVE_DIRS:
        paths += [p for p in (ROOT / rel).rglob("*") if p.suffix in (".md", ".mdc", ".html")]
    stale = [(str(p.relative_to(ROOT)), m.group(0)) for p in paths if p.is_file()
             for m in [STALE.search(_read(p))] if m]
    assert not stale, stale
