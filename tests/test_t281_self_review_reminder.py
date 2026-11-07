"""
T281 - Stage 5 item 4 tells the Supervisor to remind the user about /self-review, and never to start it.
Spec: docs/brainstorming/BRAINSTORMING_LOG_self-review-trigger.md (Option C, chosen by the user 2026-11-07).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGES = os.path.join(ROOT, "docs", "claude-md", "pipeline-stages.md")
SKILL = os.path.join(ROOT, "skills", "self-review", "SKILL.md")
PRD = os.path.join(ROOT, "docs", "prd", "PRD_self-review.md")
SCRIPT = "skills/self-review/scripts/self_review.py"


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _reminder():
    """The reminder bullet, inside Stage 5 item 4 (the memory update), whitespace-normalised."""
    doc = _read(STAGES)
    item4 = doc.split("4. **Memory update**", 1)[1].split("5. Merge the worktree", 1)[0]
    m = re.search(r"- \*\*Self-review reminder\*\*.*?(?=\n   - |\n\n|\Z)", item4, re.DOTALL)
    assert m, "Stage 5 item 4 has no 'Self-review reminder' bullet"
    return re.sub(r"\s+", " ", m.group(0))


def test_reminder_runs_pre_and_tells_the_user_when_ready_with_three_files():
    text = _reminder()
    assert f"python3 {SCRIPT} pre" in text
    assert '"status": "ready"' in text and "at least 3" in text
    assert "`/self-review`" in text and "in one line" in text


def test_reminder_never_starts_the_loop_or_the_miner():
    text = _reminder()
    assert "Never run `/self-review` or its miner yourself" in text
    assert "you never start the loop" in text


def test_reminder_is_honest_about_the_one_write_of_pre():
    """`pre` marks register rows `fixed` (self_review.py cmd_pre / mark_fixed), so it is not read-only."""
    text = _reminder()
    assert "read-only" not in text
    assert "`fixed`" in text and "memory/self-review/register.md" in text and "commit" in text


def test_reminder_covers_other_statuses_and_auto_mode_and_stays_short():
    text = _reminder()
    assert "Any other status, or an error: say nothing" in text
    assert "auto mode" in text and "`Not done:`" in text
    assert len(text.split()) <= 110, f"{len(text.split())} words"


def test_the_script_named_exists_and_the_user_still_owns_the_start():
    assert os.path.isfile(os.path.join(ROOT, SCRIPT))
    assert "disable-model-invocation: true" in _read(SKILL).split("---", 2)[1]
    assert "must start only on the user's `/self-review`" in _read(PRD)
