#!/usr/bin/env python3
"""T291 — the merge gate counts `python3 [harmless interpreter flags] -m pytest|unittest`.

`invokes_test_runner` (`.claude/hooks/pre_bash_block_unsafe_merge.py`) did not count
`python3 -B -m pytest`, although the kit tells agents to run mutation controls with `-B`. Two merges
(T289, T290) were blocked with "evidence row present but no verified tool call". The fix is one
optional flag group on the `python` alternative of `TEST_INVOCATION_PATTERN`; nothing else that
counts as a test run changes.

The flag list is fixed: `-B -u -O -s -E -I` (single letters, or a run of them such as `-uB`).
Every other flag (`-X dev`, `-W error`, `-c`, `-m other`) stays out, so the gate fails closed.

Every command here is a constructed string; no git, no shell, no real hook run.

Run with: python3 -m pytest .claude/hooks/tests/test_invokes_test_runner_flags.py -v
"""
import json
import os
import types

import pytest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py")


def load_hook_module(path, name):
    """Load the hook without running its bottom-of-file `main()` (see test_merge_gate_t210)."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


gate = load_hook_module(HOOK_PATH, "merge_gate_t291")


def trace_record(command):
    return json.dumps({"timestamp": "2026-11-08T00:00:00+00:00", "tool_name": "Bash",
                       "summary": json.dumps({"command": command})[:300], "is_error": False})


# ---------------------------------------------------------------------------
# AC 1 — a run with harmless interpreter flags counts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    "python3 -B -m pytest x.py",
    "python3 -B -m pytest x.py -q",
    "python3 -u -B -m unittest",
    "python -I -m pytest",
    "py -B -m pytest",
    "python3 -O -m pytest",
    "python3 -s -m pytest",
    "python3 -E -m unittest discover",
    "python3 -uB -m pytest",
    "python3 -B -u -O -s -E -I -m pytest",
    "cd /x && python3 -B -m pytest -q",
    "CLAUDE_ACTIVE_TASK=T291 python3 -B -m pytest -q",
    "timeout 900 python3 -B -m pytest -q",
    "(python3 -B -m pytest)",
    "python3 -B -m pytest x.py | tail -5",
])
def test_ac1_a_run_with_harmless_interpreter_flags_counts(command):
    assert gate.invokes_test_runner(command)


def test_ac1_a_trace_whose_only_run_has_the_flag_verifies(tmp_path, monkeypatch):
    os.makedirs(tmp_path, exist_ok=True)
    (tmp_path / "T900.jsonl").write_text(trace_record("python3 -B -m pytest x.py -q") + "\n")
    monkeypatch.setattr(gate, "TRACE_DIR", str(tmp_path))
    assert gate.trace_shows_verification("T900")


# ---------------------------------------------------------------------------
# AC 2 — everything else still does not count
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", [
    'python3 -c "import pytest"',
    "python3 -B script.py",
    "python3 -B -m json.tool",
    "python3 -X dev -m pytest",
    "python3 -W error -m pytest",
    "python3 -B -X dev -m pytest",
    "python3 -b -m pytest",          # lower-case twin of -B is not on the list
    "python3 -S -m pytest",          # upper-case twin of -s is not on the list
    "python3 -i -m pytest",
    "python3 -Bx -m pytest",
    "python3 -B -c 'x' -m pytest",
    "python3 -B -m json.tool -m pytest",
    "python3 -m json.tool -B -m pytest",
    "python3 -B pytest",
    "python3 -B -m pytestx",
    "python3 -B-m pytest",           # no space before -m
    "python3-m pytest",
    "python3-B -m pytest",           # no space before a flag
    "python3 -B-B -m pytest",
    "/usr/bin/python3 -B -m pytest", # only the bare interpreter names count
    "python3.12 -B -m pytest",
    "python3 -B -m pytest_cov_report",
    "python3 -B -mpytest",
    "python3 - -m pytest",
    "python3 -- -m pytest",
    'echo "python3 -B -m pytest"',
    "echo 'python3 -B -m pytest'",
    "echo python3 -B -m pytest",
    "grep 'python3 -B -m pytest' log.txt",
    "cat python3 -B -m pytest",
    "python3 -B ./run.py -m pytest",
    'bash -c "python3 -B -m pytest"',
])
def test_ac2_a_command_that_is_not_a_flagged_runner_does_not_count(command):
    assert not gate.invokes_test_runner(command)


@pytest.mark.parametrize("letter", sorted(set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
                                           - set("BuOsEI")))
def test_ac2_no_other_single_letter_flag_is_on_the_list(letter):
    assert not gate.invokes_test_runner(f"python3 -{letter} -m pytest")
    assert not gate.invokes_test_runner(f"python3 -B -{letter} -m pytest")


def test_ac2_a_trace_whose_only_command_is_a_mention_does_not_verify(tmp_path, monkeypatch):
    (tmp_path / "T901.jsonl").write_text(
        trace_record('echo "python3 -B -m pytest"') + "\n"
        + trace_record("python3 -B -X dev -m pytest") + "\n")
    monkeypatch.setattr(gate, "TRACE_DIR", str(tmp_path))
    assert not gate.trace_shows_verification("T901")


def test_ac2_a_failed_flagged_run_does_not_verify(tmp_path, monkeypatch):
    record = json.loads(trace_record("python3 -B -m pytest"))
    record["is_error"] = True
    (tmp_path / "T902.jsonl").write_text(json.dumps(record) + "\n")
    monkeypatch.setattr(gate, "TRACE_DIR", str(tmp_path))
    assert not gate.trace_shows_verification("T902")


# ---------------------------------------------------------------------------
# AC 3 — the old cases keep their result
# ---------------------------------------------------------------------------

OLD_COUNTS = [
    "python3 -m pytest", "python3 -m pytest .claude/hooks/tests/ -q", "python -m unittest discover",
    "py -m pytest", "pytest", "pytest -q x", "jest", "tox", "npm test", "npm run test", "yarn test",
    "pnpm test", "go test ./...", "cargo test", "bash tests/run.sh", "sh scripts/verify.sh",
    "./smoke.sh", "../x/test.sh", "cd /x && python3 -m pytest", "a; python3 -m pytest",
    "CLAUDE_ACTIVE_TASK=T1 python3 -m pytest", "timeout 900 python3 -m pytest -q",
    "timeout -k 5 60s pytest", "(timeout 300 python3 -m pytest .claude/hooks/tests -q)",
    "uv run python3 -m pytest", "echo hi\npython3 -m pytest",
]
OLD_DOES_NOT_COUNT = [
    "echo pytest", 'echo "python3 -m pytest"', "grep pytest log.txt", "python3 script.py",
    'python3 -c "import pytest"', "python3 -m json.tool", "cat pytest.ini",
    'git commit -m "run pytest"', "timeout pytest", "timeout 900 echo pytest",
    "echo timeout 900 pytest", "python3 -m pytestx", "ls", "", "python3 -m",
    "python3  pytest", "python3 -mpytest",
]


@pytest.mark.parametrize("command", OLD_COUNTS)
def test_ac3_an_old_positive_case_still_counts(command):
    assert gate.invokes_test_runner(command)


@pytest.mark.parametrize("command", OLD_DOES_NOT_COUNT)
def test_ac3_an_old_negative_case_still_does_not_count(command):
    assert not gate.invokes_test_runner(command)


def test_ac3_a_non_string_still_does_not_count():
    assert gate.invokes_test_runner(None) is False
    assert gate.invokes_test_runner(["python3", "-B", "-m", "pytest"]) is False


# ---------------------------------------------------------------------------
# The pattern carries the flag list as written, not widened by IGNORECASE
# ---------------------------------------------------------------------------

def test_the_flag_group_is_case_exact_while_the_rest_of_the_pattern_stays_case_blind():
    assert gate.invokes_test_runner("PYTHON3 -B -m PYTEST")
    assert not gate.invokes_test_runner("PYTHON3 -b -m PYTEST")
