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


# Summaries copied byte for byte from the real trace (memory/event-trace/<task>.jsonl, line in the key).
REAL = {
    "T173:94": '{"message": "Agent: common-infrastructure\\nTask: T173 \\u2014 AGENTS.md is the primary doctrine file; CLAUDE.md imports it\\nStatus: ready-for-review, with 3 gaps listed below. The `pre_agent_step_limit` hook stopped me at its 90-call limit (\\"Stop and report to the Supervisor\\"). I made one more edit',
    "T189:100": '{"message": "Agent: common-infrastructure\\nTask: T189 \\u2014 option (a), check (7), then the AC 11 rerun\\nStatus: blocked \\u2014 the step-limit hook stopped me before I made any change.\\n\\n**Blocker.** `pre_agent_step_limit` killed my next Bash call with this message: `[hook:pre_agent_step_limit] T1',
    "T223:90": '{"message": "Agent: common-infrastructure\\nTask: T223 \\u2014 Stage 4 review fixes (S1\\u2013S3, C1\\u2013C5)\\nStatus: blocked. All 7 fixes are done and the tests are green, but they are NOT committed and the Evidence rows are NOT updated yet.\\n\\nThe step-limit hook stopped my last call. It ran the Evi',
    "T249:90": '{"message": "Agent: common-infrastructure\\nTask: T249 \\u2014 TokenEconomizer A/B experiment, phase 1 ($0 spent)\\nStatus: blocked (waiting on Supervisor sign-off for phase 2, plus 3 choice questions below). The `pre_agent_step_limit` hook also stopped me at 90 tool calls.\\n\\nChanged files (branch `ex',
    "T250:88": '{"message": "Agent: common-infrastructure\\nTask: T250 \\u2014 Gates judge only this session\'s work; a blocked verify falls back to the user\'s /verify\\nStatus: in-progress (stopped by `pre_agent_step_limit`: \\"T250 has exceeded 90 tool calls without reaching Ready for Review \\u2026 Stop and report to ',
    "T267:91": '{"message": "Agent: common-infrastructure\\nTask: T267 \\u2014 the merge gate reads PowerShell-spelled git writes and the PowerShell tool\\nStatus: blocked. The step-limit hook stopped me, and one new pin test fails.\\n\\n**Done.** I added T267 to the guard, as you decided, in commit `d44284ae` (\\"test(T',
    "T284:92": '{"message": "Agent: common-infrastructure\\nTask: T284 \\u2014 `[admin]` tag: auto mode, plus merge and push of the task branch after a passed auto verify\\nStatus: blocked \\u2014 the step-limit guard (90 tool calls) fired and told me to stop and report. My last commit, `f46a854a` (AC 10), leaves two p',
    "T285:30": '{"message": "Agent: common-infrastructure\\nTask: T285 \\u2014 Step limit counts per sub-agent run (agent_id)\\nStatus: ready-for-review (committed on feat/t285-step-limit-per-agent as e257cd5b; not merged, not pushed)\\n\\nWhat changed\\n- /home/hungnguyenhuu/workspace/pets/wt-t285/.claude/hooks/pre_agen',
    "T285:36": '{"message": "Agent: common-infrastructure\\nTask: T285 \\u2014 Stage 4 fixes\\nStatus: ready-for-review. HEAD is 112c7e3e on feat/t285-step-limit-per-agent. Not merged, not pushed. PROJECT_KANBAN.md, memory/** and .claude/settings.json untouched.\\n\\n1. `skills/resolve-question/SKILL.md` is now 8177 byt',
}


def real(key):
    return {"timestamp": "2026-11-08T00:00:00+00:00", "tool_name": "SubagentHandback",
            "summary": REAL[key]}


def test_fix2_finished_work_on_a_step_limit_branch_is_not_a_stop():
    # The two real T285 handbacks that the first version logged as stops (verify FAIL on c0e1d555).
    assert al.classify(real("T285:30")) is None
    assert al.classify(real("T285:36")) is None


def test_fix2_the_real_stops_are_still_stopped_rows():
    for key in ("T173:94", "T189:100", "T249:90", "T250:88", "T267:91", "T284:92"):
        got = al.classify(real(key))
        assert got is not None and got[0] == "stopped", key


def test_fix2_t223_first_stays_a_blocked_row():
    # Its status line is `blocked.`; the hook is named in the body, which AC 1 does not read.
    got = al.classify(real("T223:90"))
    assert got is not None and got[0] == "blocked"


def test_fix2_a_name_with_step_limit_in_a_done_status_is_not_a_stop():
    for status in (
        "ready-for-review. Branch `feat/t999-step-limit-fix` is committed, not merged.",
        "ready-for-review. HEAD is abc1234 on feat/t999-step-limit-fix.",
        "ready-for-review. I edited `.claude/hooks/pre_agent_step_limit.py` and its tests.",
        "ready-for-review. Worktree /home/me/wt-t999/step-limit-fix is clean.",
        "ready-for-review. Branch t999-step-limit-fix is committed.",
    ):
        assert al.classify(handback(status)) is None, status


def test_fix2_the_same_words_in_a_real_stop_are_a_stopped_row():
    got = al.classify(handback("blocked. The step-limit hook stopped me on feat/t999-step-limit-fix."))
    assert got is not None and got[0] == "stopped"
    got = al.classify(handback("ready-for-review. Edited `pre_agent_step_limit.py`; the hook "
                               "`pre_agent_step_limit` killed a call after 90 tool calls."))
    assert got is not None and got[0] == "stopped"


def test_fix2_a_negated_stop_verb_is_not_a_stop():
    # The verb is there ("stopped"), so only the negation guard keeps it out.
    assert al.classify(handback("ready-for-review. The step-limit hook never stopped me.")) is None
    assert al.classify(handback("ready-for-review. The step-limit hook did not stop me.")) is None


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
    # The em dash still decodes: the half escape is dropped, the rest is not lost.
    assert cell.startswith("blocked \u2014 y")
    assert cell.endswith("(cut at 300)") and "\\u20" not in cell


def test_ac5_a_cut_between_the_halves_of_an_emoji_pair_does_not_crash(tmp_path):
    # The cut leaves a lone high surrogate `\ud83d`: a complete escape that is half a character.
    prefix = '{"message": "Agent: x\\nTask: T999\\nStatus: blocked '
    text = prefix + "y" * (300 - len(prefix) - 6) + "\\ud83d"
    assert len(text) == 300
    rec = {"timestamp": "t", "tool_name": "SubagentHandback", "summary": text}
    trace = write_trace(tmp_path / "T999.jsonl", [rec])
    out = run("derive", trace)  # printing a lone surrogate raises, so run the real command
    assert out.returncode == 0 and "Traceback" not in out.stderr
    cell = out.stdout.splitlines()[0].split("\t")[3]
    assert cell.startswith("blocked yyy") and cell.endswith("(cut at 300)")
    tsv = tmp_path / "attempts.tsv"
    assert run("append", str(tsv), trace).returncode == 0  # writing the file must not raise either
    assert run("append", str(tsv), trace).stdout.strip() == "appended 0 rows"


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


def test_a_carriage_return_inside_the_status_line_becomes_a_space(tmp_path):
    rec = handback("blocked\\rabc", tail="")
    row = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0]
    assert "\r" not in row and row.split("\t")[3] == "blocked abc"


def test_a_newline_escaped_as_unicode_inside_the_status_line_becomes_a_space(tmp_path):
    # `\\n` ends the line, but `\\u000a` does not: it decodes to a real newline in the cell.
    rec = handback("blocked\\u000athen more", tail="")
    row = al.derive([write_trace(tmp_path / "T999.jsonl", [rec])])[0]
    assert "\n" not in row and row.split("\t")[3] == "blocked then more"


def test_ac2_a_status_with_a_splitlines_separator_appends_once(tmp_path):
    # str.splitlines() splits on these too; one row must stay one line, so a rerun finds it.
    for sep in ("\\u000b", "\\u000c", "\\u001c", "\\u001d", "\\u001e", "\\u0085",
                "\\u2028", "\\u2029"):
        trace = write_trace(tmp_path / "T999.jsonl", [handback("blocked" + sep + "fine", tail="")])
        tsv = tmp_path / "attempts.tsv"
        tsv.unlink(missing_ok=True)
        assert run("append", str(tsv), trace).stdout.strip() == "appended 1 rows", sep
        snapshot = tsv.read_bytes()
        assert run("append", str(tsv), trace).stdout.strip() == "appended 0 rows", sep
        assert tsv.read_bytes() == snapshot, sep
        assert len(snapshot.split(b"\n")) == 3, sep  # header, one row, and the empty tail
        assert snapshot.split(b"\n")[1].split(b"\t")[3] == b"blocked fine", sep


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
