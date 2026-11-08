#!/usr/bin/env python3
"""T288: tasks/attempts.tsv - blocked and stopped runs, derived from the event trace.

One row per sub-agent handback that reports a blocked or stopped run:
    time <TAB> task <TAB> kind <TAB> status line
- kind `blocked`: the handback's `Status:` line starts with "blocked".
- kind `stopped`: the `Status:` line names the step limit (the `pre_agent_step_limit` hook) as the
  cause, with a stopping verb in the same sentence ("hook stopped me", "killed a call", "stopped by
  `pre_agent_step_limit`"). A branch, path or file name that holds the words is cut out first, and
  a negated mention ("did not stop me") is no stop.
A done handback that only contains the word "blocked" ("Nothing is blocked") is not a row.
The time is the trace's own UTC stamp. The task is the `Task:` line of the handback, else the
trace file name. The trace cuts every handback summary at 300 characters; a status line that
the cut reaches ends in "(cut at 300)".

Usage:
    attempt_log.py derive [<trace.jsonl | trace folder> ...]          # print the rows, write nothing
    attempt_log.py append <attempts.tsv> [<trace.jsonl | folder> ...] # add only rows the file lacks

The file is append-only: `append` never changes an existing row, and a second run adds nothing.
It adds no hook; only the Supervisor runs it (docs/claude-md/memory-write-protocol.md).
A missing or empty trace folder gives no rows and exit 0. A malformed trace line is skipped
and counted on stderr.

Known limit: only the `Status:` line is read. A handback with no `Status:` line that the step
limit stopped (a reviewer's, such as T266, trace T266.jsonl line 90) is not logged.
"""
import glob
import json
import os
import re
import sys

HEADER = "time\ttask\tkind\tstatus"
TRACE_CAP = 300  # post_tool_trace.py cuts every summary at this many characters

# The summary is a JSON-text fragment: newlines are the two characters `\n`.
STATUS = re.compile(r'(?:\\n|")\s*\**Status:\**\s*(.*?)(\\n|$)')
TASK = re.compile(r'(?:\\n|")\s*\**Task:\**\s*\**([A-Z][A-Z0-9]*-?\d+)')
# Names that merely contain the words: a branch or path (has a slash), a file name, a hyphenated
# compound such as `t285-step-limit-per-agent`. They are cut out before the step limit is looked for.
NAME_TOKENS = re.compile(
    r"\S*[/\\]\S*"                                     # branch or path
    r"|\S+\.(?:py|md|json|jsonl|sh|ps1|tsv|txt|html)\b\S*"  # file name
    r"|[\w]+-step[-_]limit\S*|\S*step[-_]limit-[\w-]+",    # hyphenated compound name
    re.I)
# The step limit as the CAUSE: the hook named with a stopping verb in the same sentence.
STEP_LIMIT = re.compile(
    r"step[-_ ]limit[^.]{0,60}?\b(?:stopped|killed|fired|halted|cut me off|exceeded)\b"
    r"|\b(?:stopped|killed|halted|cut off)\b[^.]{0,40}?step[-_ ]limit",
    re.I)
# "the step-limit hook did not stop me": the hook is named only to say it did not fire.
STEP_LIMIT_NEGATED = re.compile(
    r"step[-_ ]limit[^.]{0,60}?\b(?:did not|didn't|never|does not|doesn't|not (?:stop|hit|fire))", re.I)
BLOCKED = re.compile(r"^\W*blocked\b", re.I)
PARTIAL_ESCAPE = re.compile(r"\\(?:u[0-9a-fA-F]{0,3})?$")
# Every character that must not stay in a cell: the TSV separators and all that str.splitlines()
# splits on (VT, FF, FS, GS, RS, NEL, LS, PS). A `\u000a` escape decodes to one of them.
LINE_BREAKS = re.compile("[\t\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]")


def _flat(text):
    """One TSV cell: no line break or tab, no lone surrogate (it cannot be printed or written)."""
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")
    return LINE_BREAKS.sub(" ", text).strip()


def _decode(raw):
    """Turn the JSON-escaped text (`\\u2014`, `\\"`) into plain text; never raise."""
    for text in (raw, PARTIAL_ESCAPE.sub("", raw)):
        try:
            return json.loads('"' + text + '"')
        except ValueError:
            continue
    return raw


def _status_line(summary):
    """The full status line of a handback summary, or None when there is no `Status:` line."""
    m = STATUS.search(summary)
    if not m:
        return None
    raw, ended = m.group(1), m.group(2)
    cut = not ended and len(summary) >= TRACE_CAP
    if not ended and not cut:
        raw = re.sub(r'"\s*\}?\s*$', "", raw)  # the closing of the JSON text
    text = _flat(_decode(raw))
    return text + " (cut at 300)" if cut else text


def classify(record):
    """One trace record -> (kind, status line) or None."""
    if record.get("tool_name") != "SubagentHandback":
        return None
    status = _status_line(record.get("summary") or "")
    if status is None:
        return None
    named_out = NAME_TOKENS.sub(" ", status)
    if STEP_LIMIT.search(named_out) and not STEP_LIMIT_NEGATED.search(named_out):
        return "stopped", status
    if BLOCKED.search(status):
        return "blocked", status
    return None


def _trace_files(paths):
    files = []
    for path in paths:
        if os.path.isdir(path):
            files.extend(sorted(glob.glob(os.path.join(path, "*.jsonl"))))
        elif os.path.isfile(path):
            files.append(path)
    return files


def derive(paths, stats=None):
    """Rows `time<TAB>task<TAB>kind<TAB>status`, oldest first, each once."""
    seen, rows = set(), []
    for path in _trace_files(paths):
        stem = os.path.basename(path).rsplit(".", 1)[0]
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if not isinstance(rec, dict):
                        raise ValueError("not an object")
                except ValueError:
                    if stats is not None:
                        stats["skipped"] = stats.get("skipped", 0) + 1
                    continue
                got = classify(rec)
                if not got:
                    continue
                m = TASK.search(rec.get("summary") or "")
                row = "\t".join([_flat(str(rec.get("timestamp", ""))), m.group(1) if m else stem, *got])
                if row not in seen:
                    seen.add(row)
                    rows.append(row)
    return sorted(rows, key=lambda r: r.split("\t")[:2])


def append(tsv, rows):
    """Append-only: add the rows the file lacks, create it with a header, return the count."""
    have, exists = set(), os.path.isfile(tsv) and os.path.getsize(tsv) > 0
    if exists:
        with open(tsv, encoding="utf-8") as fh:
            text = fh.read()
        have = set(text.split("\n"))  # not splitlines(): it also splits on VT, FF, NEL, LS, PS ...
    new = [r for r in rows if r not in have]
    if not new:
        return 0
    with open(tsv, "a", encoding="utf-8") as fh:
        if not exists:
            fh.write(HEADER + "\n")
        elif not text.endswith("\n"):
            fh.write("\n")
        for r in new:
            fh.write(r + "\n")
    return len(new)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    stats = {}
    if cmd == "derive":
        for r in derive(argv[2:], stats):
            print(r)
    elif cmd == "append" and len(argv) > 2:
        print(f"appended {append(argv[2], derive(argv[3:], stats))} rows")
    else:
        print(__doc__.split("Usage:")[1].split("The file is")[0].rstrip(), file=sys.stderr)
        return 2
    if stats.get("skipped"):
        print(f"skipped {stats['skipped']} malformed trace line(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
