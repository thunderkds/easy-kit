"""T340 — remove kit files nothing uses (lean-kit proposal, Part 1: f1-f4, f7).

Gone: two one-off scripts, the plugin spike (and its test), the self-review spike's
working files. Moved: the self-review spike's RESULTS.md, which `docs/prd/PRD_self-review.md`
cites. Not moved (f7): the root BRAINSTORMING_LOG.md stays, by T215's rule (tasks/TASK_GUIDE_T215.md
line 32, pinned by tests/test_repo_layout_t215.py).
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

REMOVED = (
    "scripts/measure_agent_guide_tokens.py",
    "scripts/test-claude-md-refs.sh",
    "experiments/plugin-spike",
    "tests/test_plugin_spike.py",
    "experiments/self-review-spike",
)
SPIKE_RESULTS = "docs/experiments/self-review-spike-RESULTS.md"
PRD = "docs/prd/PRD_self-review.md"


def _exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def test_unused_files_are_removed():
    assert [p for p in REMOVED if _exists(p)] == []


def test_prd_cites_spike_results_at_a_path_that_exists():
    with open(os.path.join(ROOT, PRD), encoding="utf-8") as fh:
        text = fh.read()
    cited = re.findall(r"`([\w./-]*RESULTS\.md)`", text)
    assert cited, "PRD_self-review.md no longer cites the spike results"
    assert all(_exists(p) for p in cited), cited
    assert SPIKE_RESULTS in cited
