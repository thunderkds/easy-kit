"""T169 scope extension: CLAUDE.md stays at or under 200 lines and keeps the rules the cuts must not lose.

REPOINTED by T173 (`CLAUDE.md` -> `AGENTS.md`): the doctrine moved to AGENTS.md and CLAUDE.md is
the one-line import `@AGENTS.md`, so the cap and the kept rules apply to AGENTS.md (T173 AC 7).

T286: the line cap tripped 0 times while AGENTS.md grew 17% in 18 commits (T283 spike report, section 7),
so a BYTE cap now sits beside it. A growth past the byte cap is a decision, not a drift.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
RAW = (ROOT / "AGENTS.md").read_bytes()

# T286: a literal, never computed from the file at test time (a cap read from the file passes forever, LR-0003).
# Measured at commit 46c013fc (the last commit that changed AGENTS.md; branch base 4c076b6c, main 8f00098c).
# T284 (the `[admin]` tag, unmerged) also edits AGENTS.md; after T284 merges, the Supervisor re-measures this
# cap at merge time (merge order: T284, then T286).
# T289: lowered 21732 -> 21724 (ratchet down): the Tracks sentence lost "`skip`, " (8 bytes) because a
# docs-only SKIP is now a pass. Measured at commit 83ac3e7a.
AGENTS_MD_BYTE_CAP = 21724


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", t)


def test_claude_md_is_at_most_200_lines():
    assert len(TEXT.splitlines()) <= 200


def _byte_cap_problem(data: bytes):
    """None when `data` fits the cap; else the message that tells the author what to do."""
    if len(data) <= AGENTS_MD_BYTE_CAP:
        return None
    return (
        f"AGENTS.md is {len(data)} bytes, cap {AGENTS_MD_BYTE_CAP}. "
        "Lower the file (cut or move text to docs/claude-md/), or raise AGENTS_MD_BYTE_CAP in "
        "tests/test_claude_md_slim.py in the same commit with a recorded reason. "
        "A ratchet moves down by default."
    )


def test_agents_md_is_at_most_21724_bytes():
    assert _byte_cap_problem(RAW) is None, _byte_cap_problem(RAW)


def test_byte_cap_fails_one_byte_past_the_cap_with_the_do_this_message():
    # The file must sit at the cap. After a deliberate cut, lower the cap to the new size (a ratchet).
    msg = _byte_cap_problem(RAW + b"x")
    assert msg is not None, "AGENTS.md has slack under the cap: lower AGENTS_MD_BYTE_CAP to its size"
    assert "Lower the file" in msg and "raise AGENTS_MD_BYTE_CAP" in msg and "recorded reason" in msg


def test_byte_cap_reads_bytes_not_lines():
    # Same byte count on one long line: the line cap is happy (1 line), the byte cap is not.
    one_line_plus_one = RAW.replace(b"\n", b" ") + b"x"
    assert len(one_line_plus_one.splitlines()) <= 200
    assert _byte_cap_problem(one_line_plus_one) is not None


def test_byte_cap_counts_utf8_bytes_not_characters():
    assert len(TEXT) < len(RAW), "AGENTS.md holds multi-byte characters; the cap must count bytes"
    assert _byte_cap_problem(("x" * (AGENTS_MD_BYTE_CAP - 1) + "é").encode("utf-8")) is not None


def test_wake_mandate_kept():
    n = _norm(TEXT)
    assert 'Skill({ skill: "wake" })' in n
    assert "not optional" in n
    assert "user jumps straight to a task" in n


def test_agent_template_pointer_and_base_rules_kept():
    n = _norm(TEXT)
    assert "templates/general-agent-template.md" in n
    assert "docs/claude-md/untrusted-content-boundary.md" in n
    assert "Complexity Level (C0–C3)" in n
    assert "Risk Level" in n


def test_phase0_trigger_kept_after_final_instruction_cut():
    assert "Start new project supervision" in TEXT
