"""T283 oracle: structure of tasks/SPIKE_REPORT_T283.md (written by the Supervisor, not the implementer).

Report format. One section per idea, in this order, with the exact heading text:

    ### 1. Locked judge
    - **Hypothesis:** ...
    - **Baseline:** ... (names a real task ID, commit or review file)
    - **Spike:** ...
    - **Command:** `...`
    - **Output:**
    ```
    pasted output
    ```
    - **Verdict:** adopt | adapt | drop | no evidence — one reason

The report ends with `## Recommendation` (ranked list) and `## Proposed adoption tasks` (titles only).
"""
import re
from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "tasks" / "SPIKE_REPORT_T283.md"

IDEAS = [
    "Locked judge",
    "Keep-or-revert ratchet",
    "Simplicity rule",
    "Time budget",
    "Attempt log",
    "No check-ins",
    "Steering file",
]
LABELS = ["Hypothesis", "Baseline", "Spike", "Command", "Output", "Verdict"]
VERDICT = re.compile(r"^(adopt|adapt|drop|no evidence)\s*[—-]\s*\S.+", re.IGNORECASE)
# A real-work reference: a task ID, a 7+ hex commit, or a tasks/ or memory/ file path.
REAL_WORK = re.compile(r"\bT\d{2,3}\b|\b[0-9a-f]{7,40}\b|\b(?:tasks|memory)/[\w./-]+")


def _sections(text):
    """Return {n: (idea_name, body)} for each `### n. Name` heading."""
    out = {}
    parts = re.split(r"^### (\d+)\. (.+)$", text, flags=re.MULTILINE)
    for i in range(1, len(parts), 3):
        out[int(parts[i])] = (parts[i + 1].strip(), parts[i + 2])
    return out


def _field(body, label):
    """Text of `- **Label:**` up to the next label or heading; '' when missing."""
    m = re.search(
        rf"^- \*\*{label}:\*\*(.*?)(?=^- \*\*\w[\w ]*:\*\*|^#{{2,3}} |\Z)",
        body, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def validate(text):
    """Return a list of problems; empty means the report structure is valid."""
    problems = []
    secs = _sections(text)
    for n, name in enumerate(IDEAS, 1):
        if n not in secs:
            problems.append(f"missing section {n}. {name}")
            continue
        got, body = secs[n]
        if got != name:
            problems.append(f"section {n} is '{got}', expected '{name}'")
        for label in LABELS:
            if not _field(body, label):
                problems.append(f"{n}. {name}: empty or missing {label}")
        verdict = _field(body, "Verdict")
        if verdict and not VERDICT.match(verdict):
            problems.append(f"{n}. {name}: verdict needs adopt/adapt/drop/no evidence and a reason")
        baseline = _field(body, "Baseline")
        if baseline and not REAL_WORK.search(baseline) and not verdict.lower().startswith("no evidence"):
            problems.append(f"{n}. {name}: baseline names no real task, commit or file")
    if len(secs) != len(IDEAS):
        problems.append(f"expected {len(IDEAS)} idea sections, found {len(secs)}")
    if "## Recommendation" not in text:
        problems.append("missing ## Recommendation")
    if "## Proposed adoption tasks" not in text:
        problems.append("missing ## Proposed adoption tasks")
    return problems


def _valid_report():
    parts = ["# Spike report T283\n"]
    for n, name in enumerate(IDEAS, 1):
        parts.append(
            f"### {n}. {name}\n"
            "- **Hypothesis:** a change helps.\n"
            "- **Baseline:** measured on T250 (tasks/TASK_REVIEW_T250.md).\n"
            "- **Spike:** the spike measure.\n"
            "- **Command:** `pytest -q`\n"
            "- **Output:**\n```\n3 passed\n```\n"
            "- **Verdict:** adopt — it caught the known case.\n"
        )
    parts.append("## Recommendation\n1. Locked judge\n\n## Proposed adoption tasks\n- Locked judge hook\n")
    return "\n".join(parts)


def test_validator_accepts_a_complete_report():
    assert validate(_valid_report()) == []


def test_validator_fails_when_a_field_is_blanked():
    """Mutation control: the check must turn red when a required field is emptied."""
    text = _valid_report()
    mutated = text.replace("- **Spike:** the spike measure.", "- **Spike:**", 1)
    assert mutated != text
    assert any("empty or missing Spike" in p for p in validate(mutated))


def test_validator_fails_on_a_toy_baseline():
    text = _valid_report()
    mutated = text.replace("measured on T250 (tasks/TASK_REVIEW_T250.md).", "measured on a toy example.", 1)
    assert mutated != text
    assert any("baseline names no real task" in p for p in validate(mutated))


def test_validator_fails_on_a_bad_verdict():
    text = _valid_report()
    mutated = text.replace("adopt — it caught the known case.", "maybe", 1)
    assert mutated != text
    assert any("verdict needs" in p for p in validate(mutated))


def test_validator_fails_when_an_idea_is_missing():
    text = _valid_report()
    mutated = text.replace("### 7. Steering file", "### 7. Something else", 1)
    assert mutated != text
    assert any("expected 'Steering file'" in p for p in validate(mutated))


def test_the_real_report_is_valid():
    assert REPORT.exists(), "tasks/SPIKE_REPORT_T283.md is not written yet"
    assert validate(REPORT.read_text(encoding="utf-8")) == []
