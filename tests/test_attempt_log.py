"""T288 - scripts/attempt_log.py: tasks/attempts.tsv, derived from the event trace (AC 1-5).

Every test uses a fixture trace written in tmp_path, never the real memory/event-trace/.
A handback record has the shape of the real trace: `summary` is a JSON-text fragment of the
message, cut at 300 characters, with escaped newlines (`\\n`) and escaped unicode (`\\u2014`).
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "attempt_log.py"
_spec = importlib.util.spec_from_file_location("attempt_log", SCRIPT)
al = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(al)

HEADER = "time\ttask\tkind\tstatus"


def handback(status, task="T999", ts="2026-11-05T07:33:44.215988+00:00", tail="\\n\\nmore text"):
    """A SubagentHandback record cut at 300 characters, like the real trace."""
    text = ('{"message": "Agent: common-infrastructure\\nTask: ' + task
            + ' \\u2014 title\\nStatus: ' + status + tail)
    return {"timestamp": ts, "tool_name": "SubagentHandback", "summary": text[:300]}


def write_trace(path, records, raw_lines=()):
    lines = [json.dumps(r) for r in records] + list(raw_lines)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def fixture_trace(tmp_path):
    spawn = {"timestamp": "2026-11-05T07:00:00+00:00", "tool_name": "Agent",
             "summary": '{"description": "Implement T999", "prompt": "x'}
    recs = [
        spawn,
        handback("blocked \\u2014 the question is open.", ts="2026-11-05T07:10:00+00:00"),
        handback("blocked. The step-limit hook stopped me.", ts="2026-11-05T07:20:00+00:00"),
        # T188's second handback in the spike: done, only contains the word 'blocked'.
        handback("ready-for-review \\u2014 all four corrections made. Nothing is blocked.",
                 ts="2026-11-05T07:30:00+00:00"),
        handback("ready-for-review", ts="2026-11-05T07:40:00+00:00"),
    ]
    return write_trace(tmp_path / "T999.jsonl", recs)


def test_ac1_blocked_and_step_limit_rows_only(tmp_path):
    rows = al.derive([fixture_trace(tmp_path)])
    cells = [r.split("\t") for r in rows]
    assert [c[2] for c in cells] == ["blocked", "stopped"]
    assert all(len(c) == 4 for c in cells)
    assert cells[0][0] == "2026-11-05T07:10:00+00:00"  # UTC time exactly as the trace has it
    assert cells[0][1] == "T999"
    assert cells[0][3] == "blocked — the question is open."
    assert "step-limit" in cells[1][3]


def test_ac1_cli_derive_prints_the_rows(tmp_path):
    out = run("derive", fixture_trace(tmp_path))
    assert out.returncode == 0
    lines = out.stdout.splitlines()
    assert len(lines) == 2 and lines[0].split("\t")[2] == "blocked"


def test_ac1_step_limit_in_a_done_status_is_a_stopped_row():
    # The spike found T173 and T223: a done status that names the step-limit hook.
    got = al.classify(handback("ready-for-review, but the `pre_agent_step_limit` hook cut me off"))
    assert got is not None and got[0] == "stopped"


def test_ac4_a_done_status_that_says_the_step_limit_did_not_stop_it_is_not_a_row():
    # T223's second handback in the real trace: it names the hook only to say it did not fire.
    rec = handback("ready-for-review. The fixes are committed in 1 tool call. "
                   "The step-limit hook did not stop me this time.")
    assert al.classify(rec) is None
    # The same words without the negation are a stop.
    assert al.classify(handback("ready-for-review. The step-limit hook stopped me."))[0] == "stopped"


def test_ac1_a_status_line_that_starts_with_bold_blocked_is_blocked():
    got = al.classify(handback("**blocked** on a question"))
    assert got is not None and got[0] == "blocked"


def test_ac2_append_adds_only_missing_rows_and_twice_adds_nothing(tmp_path):
    trace = fixture_trace(tmp_path)
    tsv = tmp_path / "attempts.tsv"
    old = HEADER + "\n2026-01-01T00:00:00+00:00\tT001\tblocked\told row kept as is\n"
    tsv.write_text(old, encoding="utf-8")
    assert al.append(str(tsv), al.derive([trace])) == 2
    after_first = tsv.read_text(encoding="utf-8")
    assert after_first.startswith(old)  # existing rows are never changed
    assert al.append(str(tsv), al.derive([trace])) == 0
    assert tsv.read_text(encoding="utf-8") == after_first


def test_ac2_cli_append_twice_leaves_the_file_unchanged(tmp_path):
    trace = fixture_trace(tmp_path)
    tsv = tmp_path / "attempts.tsv"
    first = run("append", str(tsv), trace)
    assert first.returncode == 0 and "appended 2" in first.stdout
    snapshot = tsv.read_bytes()
    second = run("append", str(tsv), trace)
    assert second.returncode == 0 and "appended 0" in second.stdout
    assert tsv.read_bytes() == snapshot


def test_ac2_absent_file_is_created_with_a_header_row(tmp_path):
    tsv = tmp_path / "attempts.tsv"
    al.append(str(tsv), al.derive([fixture_trace(tmp_path)]))
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert lines[0] == HEADER and len(lines) == 3


def test_ac2_file_without_final_newline_keeps_one_row_per_line(tmp_path):
    tsv = tmp_path / "attempts.tsv"
    tsv.write_bytes((HEADER + "\nold\trow\tblocked\tno newline at end").encode())
    al.append(str(tsv), al.derive([fixture_trace(tmp_path)]))
    lines = tsv.read_text(encoding="utf-8").splitlines()
    assert lines[1] == "old\trow\tblocked\tno newline at end" and len(lines) == 4


def test_ac3_status_line_is_kept_whole_when_the_handback_text_has_it(tmp_path):
    status = "blocked \\u2014 " + "long reason " * 12 + "end"  # 150+ characters, then a newline
    rows = al.derive([write_trace(tmp_path / "T999.jsonl", [handback(status)])])
    cell = rows[0].split("\t")[3]
    assert cell.endswith("long reason end") and "(cut at 300)" not in cell
    assert len(cell) > 140


def test_ac3_a_short_handback_without_a_newline_is_whole_and_not_cut(tmp_path):
    rec = {"timestamp": "t", "tool_name": "SubagentHandback",
           "summary": '{"message": "Status: blocked on a question"}'}
    cell = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0].split("\t")[3]
    assert cell == "blocked on a question"


def test_ac3_a_status_line_cut_at_300_says_so(tmp_path):
    rec = handback("blocked \\u2014 " + "x" * 400, tail="")
    assert len(rec["summary"]) == 300
    cell = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0].split("\t")[3]
    assert cell.endswith("(cut at 300)")


def test_ac3_a_cut_in_the_middle_of_an_escape_does_not_crash(tmp_path):
    # Cut so that the text ends in `\u20` - a half unicode escape.
    prefix = '{"message": "Agent: x\\nTask: T999\\nStatus: blocked \\u2014 '
    text = prefix + "y" * (300 - len(prefix) - 4) + "\\u20"
    assert len(text) == 300
    rec = {"timestamp": "t", "tool_name": "SubagentHandback", "summary": text}
    cell = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0].split("\t")[3]
    assert cell.endswith("(cut at 300)")


def test_ac4_ready_for_review_that_only_says_blocked_is_not_a_row():
    rec = handback("ready-for-review \\u2014 all four corrections made, **AC 8 is now green**. "
                   "Nothing is blocked.")
    assert al.classify(rec) is None


def test_ac4_other_handbacks_and_non_handbacks_are_not_rows():
    answer = {"timestamp": "t", "tool_name": "SubagentHandback",
              "summary": '{"message": "ANSWER: milestones started, blocked, question'}
    review = {"timestamp": "t", "tool_name": "SubagentHandback",
              "summary": '{"message": "No security findings. The row is blocked by nothing.'}
    other = {"timestamp": "t", "tool_name": "Bash", "summary": "Status: blocked"}
    for rec in (answer, review, other):
        assert al.classify(rec) is None


def test_task_comes_from_the_handback_text_and_falls_back_to_the_file_name(tmp_path):
    named = handback("blocked", task="T190")
    unnamed = {"timestamp": "2026-11-05T08:00:00+00:00", "tool_name": "SubagentHandback",
               "summary": '{"message": "Status: blocked'}
    rows = al.derive([write_trace(tmp_path / "T188.jsonl", [named, unnamed])])
    assert sorted(r.split("\t")[1] for r in rows) == ["T188", "T190"]


def test_a_tab_or_newline_in_the_status_line_becomes_a_space(tmp_path):
    rec = handback("blocked\\tbecause\\r\\nof this", tail="")
    # `\\r\\n` is an escaped newline in the trace text: the status line ends there.
    row = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0]
    assert row.count("\t") == 3 and "\n" not in row
    assert row.split("\t")[3].startswith("blocked because")


def test_the_same_handback_twice_gives_one_row(tmp_path):
    rec = handback("blocked")
    trace = write_trace(tmp_path / "T999.jsonl", [rec, rec])
    assert len(al.derive([trace])) == 1
    assert len(al.derive([trace, trace])) == 1


def test_ac5_missing_or_empty_trace_folder_gives_no_rows_and_exit_0(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    for target in (str(empty), str(tmp_path / "does-not-exist")):
        out = run("derive", target)
        assert out.returncode == 0 and out.stdout == ""
    assert run("derive").returncode == 0  # no argument at all, e.g. an empty shell glob
    tsv = tmp_path / "attempts.tsv"
    out = run("append", str(tsv), str(empty))
    assert out.returncode == 0 and "appended 0" in out.stdout


def test_ac5_a_trace_folder_argument_reads_every_jsonl_file_in_it(tmp_path):
    folder = tmp_path / "trace"
    folder.mkdir()
    write_trace(folder / "T1.jsonl", [handback("blocked", task="T1")])
    write_trace(folder / "T2.jsonl", [handback("blocked", task="T2")])
    (folder / "notes.txt").write_text("Status: blocked\n")
    out = run("derive", str(folder))
    assert out.returncode == 0 and len(out.stdout.splitlines()) == 2


def test_ac5_a_malformed_trace_line_is_skipped_and_counted_on_stderr(tmp_path):
    trace = write_trace(tmp_path / "T999.jsonl", [handback("blocked")],
                        raw_lines=["{not json", "[1, 2]"])
    out = run("derive", trace)
    assert out.returncode == 0
    assert len(out.stdout.splitlines()) == 1
    assert "skipped 2 malformed" in out.stderr


def test_derive_writes_nothing(tmp_path):
    trace = fixture_trace(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    run("derive", trace)
    assert sorted(p.name for p in tmp_path.iterdir()) == before
