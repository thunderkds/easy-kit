#!/usr/bin/env python3
"""T294 — a seeded differential fuzz: real bash and zsh against `strip_heredoc_bodies`.

Each random command holds canary lines (`echo CAN""ARY<k>`: the shell prints `CANARY<k>`, the command
text never holds that word) mixed with the tokens that make the scanner's job hard: `$(`, backticks,
`${`, `((`, `$[`, `[`, `<(`, `x=(`, quotes, `#`, backslash, plain, quoted and partly quoted tags, and body
lines that start with the tag. When a shell prints a canary, the scanner's output must still hold the
canary line: a line a shell runs must stay visible to the gate. The seed is fixed, so a failure
reproduces; `FUZZ_RUNS` and `FUZZ_SEED` change the size and the seed for a longer hunt.

Every command runs in an empty throwaway dir with no stdin, and uses only `cat`, `echo` and `true`.
Run with: python3 -m pytest .claude/hooks/tests/test_heredoc_fuzz.py -q
"""
import os
import random
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
from shell_data import strip_heredoc_bodies  # noqa: E402  (the hook's lib/ is on sys.path)

SHELLS = [s for s in ("bash", "zsh") if shutil.which(s)]
RUNS = int(os.environ.get("FUZZ_RUNS", "1500"))
SEED = int(os.environ.get("FUZZ_SEED", "20261109"))
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

# Pieces of a command line. `\n` joins lines, so a heredoc header usually has a body to find.
HEADS = ["cat", "echo x", "true", "cat <<EOF", "cat <<-EOF", "cat <<'EOF'", 'cat <<"EOF"', "cat << EOF",
         'cat <<E"O"F', "cat <<E\\OF", "cat <<E'O'F", 'cat <<EOF"x"', 'cat <<"EOF"x', "cat <<1", "cat <<A",
         "cat <<B", "cat <<EOF)", "cat <<EOF;", "cat <<EOF &&", "cat <<<EOF", "cat <<", "echo <<EOF",
         "bash <<'EOF'", "cat <<EOF | bash", "cat <<'EOF' |", "sh <<-EOF", "source /dev/stdin <<'EOF'", "cat <<\rA",
         "cat <<\x0bA", "cat <<\xa0A", "cat <<-\u2003A", "cat > f <<'EOF'", "cat 2>&1 <<EOF", "cat &> f <<EOF"]
OPENERS = ["$(", "`", "${x:-", "${x:-'", "((", "$((", "$[", "[", "[[", "<(", ">(", "x=(", "x+=(", "(", '"', "'",
           "$'", "#", "\\", '"$(', '"${x:-', "$(( $(", "$( (", "case x in x) ", "{ ", "${x- #'", "\\\n", "x=( (", "${x:-(",
           "$(case 1 in 1) ;; esac\n", "<\\\n", "bash ", "eval ", "$\\\n{x- #'", ": <(case x in x) :;; esac; "]
CLOSERS = [")", "`", "}", "))", "]", "]]", '"', "'", ") ;", ")\"", "}\"", ")]", "; }", ";;", "esac", "fi", "done", " ;; esac"]
BODY = ["x", "A", "B", "EOF", "EOF)", "EOFx", "EOF x)", "EOF2case x in x) ", "E", " EOF", "\tEOF", "EOF ", "1",
        ")", "`", "$(", "a ) b", "cat <<B", "cat <<A", "<<EOF", "#", "'", '"', "EOF`", "EOF}", "EOF]", "\rA", "\x0bA", "E\\", "OF", "A) ; ", "'}", "}"]
JOINERS = ["\n", "\n", "\n", " ", " ; ", " && ", " | "]


TEMPLATES = None  # filled on first use: importing the regression tests is slow


def canary(k):
    return f'echo CAN""ARY{k}'


MARKERS = ["<<EOF", "<<A", "<<B", "<<E", "<<EOF)", "<<'EOF'", '<<"EOF"', "<<-EOF", "<< EOF", "<<1", "<<",
           'E"O"F', "<<E\\OF", "<<E'O'F", '<<EOF"x"', '<<"EOF"x', "<<<EOF"]
TAIL = ["EOF", "A", "B", "E", ")", "EOF)", "`", "}", "]", "EOFx", "EOF x)"]


OPEN = ["$(", "`", "<(", ">(", "x=(", "x+=(", "(", "${x:-$(", "$[", "[", '"$(', "((", "$(( $(", "echo $( ("]
SMALL = ["A", "B", ")", "`", "cat <<B", "cat <<A", "A)", "B)", "}", "]", '"', ')"', "x", "EOF", "A x)", "Ax)"]


def make_nested(rng):
    """A small vocabulary of two tags and closers, so a context opens, a heredoc starts inside it and
    its lines look like terminators of the other heredoc: the shapes that need several lines to go wrong."""
    first = rng.choice(OPEN) + rng.choice(["cat <<A", "cat <<A", "cat <<-A", "cat <<'A'", "cat <<B"])
    lines = [first] + [rng.choice(SMALL) for _ in range(rng.randint(2, 6))]
    canaries = []
    for _ in range(rng.choice([1, 1, 2])):
        canaries.append(len(canaries))
        lines.insert(rng.randrange(1, len(lines) + 1), canary(len(canaries) - 1))
    return "\n".join(lines), canaries


def known_templates():
    """The shapes the regression tests pin (hidden, real, over-blocked, doubtful), as `{push}` templates."""
    sys.path.insert(0, HERE)
    import test_heredoc_quoted_marker as known
    out = []
    for table in (known.ALL_HIDDEN, known.REAL, known.OVERBLOCK, known.DOUBT, known.SUB_HIDDEN):
        out += list(table.values())
    for table in (known.BYPASS, known.ROUND3):
        out += [template for template, _ in table.values()]
    return out


MUTATION_TOKENS = HEADS + OPENERS + CLOSERS + BODY + ["\n", " ", "\t", "#", "'", '"', "\\", "<<", "<", ">", "|", "&&", ";",
                                                      "\x0b", "\x0c", "\x85", "\u3000", "\x1c", "\r", "\xa0", "\u2003"]
SENTINEL = "\x01"  # stands for the canary line while a template is mutated


def make_mutated(rng, templates):
    """Start from one known shape and change it a little: a token inserted, a character deleted or
    replaced, a line swapped or doubled. The canary line is never touched."""
    text = rng.choice(templates).format(push=SENTINEL)
    for _ in range(rng.randint(1, 3)):
        op = rng.randrange(5)
        pieces = text.split(SENTINEL)
        side = rng.randrange(len(pieces))
        part = pieces[side]
        at = rng.randint(0, len(part))
        if op == 0:
            part = part[:at] + rng.choice(MUTATION_TOKENS) + part[at:]
        elif op == 1:
            part = part[:at] + part[at + rng.randint(1, 3):]
        elif op == 2 and part:
            at = min(at, len(part) - 1)
            part = part[:at] + rng.choice(MUTATION_TOKENS)[:1] + part[at + 1:]
        elif op == 3:
            lines = part.split("\n")
            if len(lines) > 1:
                a, b = rng.sample(range(len(lines)), 2)
                lines[a], lines[b] = lines[b], lines[a]
            part = "\n".join(lines)
        else:
            lines = part.split("\n")
            k = rng.randrange(len(lines))
            lines.insert(k, lines[k])
            part = "\n".join(lines)
        pieces[side] = part
        text = SENTINEL.join(pieces)
    if text.count(SENTINEL) != 1:
        text = rng.choice(templates).format(push=SENTINEL)
    return text.replace(SENTINEL, canary(0)), [0]


def make(rng):
    """One random command and the canary numbers it holds: a header line (openers, a command word, a
    marker, a closer), 2-5 further lines of body-like text and terminators, and 1-2 canary lines."""
    roll = rng.random()
    if roll < 0.4:
        return make_mutated(rng, TEMPLATES)
    if roll < 0.7:
        return make_nested(rng)
    head = [rng.choice(OPENERS) for _ in range(rng.choice([0, 1, 1, 2]))]
    head += [rng.choice(["cat", "echo", "true", "echo x", ""]), rng.choice(MARKERS)]
    head += [rng.choice(CLOSERS + OPENERS) for _ in range(rng.choice([0, 0, 1]))]
    lines = [rng.choice([" ", ""]).join(head)]
    for _ in range(rng.randint(2, 5)):
        lines.append(rng.choice([rng.choice(BODY), rng.choice(TAIL), rng.choice(CLOSERS),
                                 rng.choice(HEADS), rng.choice(TAIL) + " ; " + rng.choice(HEADS)]))
    canaries = []
    for _ in range(rng.choice([1, 1, 2])):
        canaries.append(len(canaries))
        lines.insert(rng.randrange(1, len(lines) + 1), canary(len(canaries) - 1))
    return "\n".join(lines), canaries


def run(shell, command, cwd):
    try:
        done = subprocess.run([shell, "-c", command], cwd=cwd, env=ENV, capture_output=True, text=True, errors="replace",
                              timeout=5, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return ""
    return done.stdout


def hidden_lines(shell, command, canaries, cwd, strip=strip_heredoc_bodies):
    """Canaries the shell ran that the scanner's output no longer holds."""
    printed = run(shell, command, cwd)
    stripped = strip(command)
    return [k for k in canaries if f"CANARY{k}" in printed and canary(k) not in stripped]


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
def test_fuzz_no_line_a_shell_runs_is_hidden_by_the_scanner(shell, tmp_path):
    global TEMPLATES
    TEMPLATES = TEMPLATES or known_templates()
    rng = random.Random(SEED)
    failures = []
    for _ in range(RUNS):
        command, canaries = make(rng)
        hidden = hidden_lines(shell, command, canaries, str(tmp_path))
        if hidden:
            failures.append((command, hidden))
    assert not failures, f"{len(failures)} of {RUNS} hid a line {shell} ran, first: {failures[0]!r}"


def strip_everything_after_a_marker(command):
    """A stand-in for the pre-T294 scanner: every `<<WORD` line starts a heredoc, quoted or not."""
    head, marker, rest = command.partition("<<EOF")
    return head + marker + "\n " if marker else command


@pytest.mark.skipif(not SHELLS, reason="no bash or zsh")
@pytest.mark.parametrize("shell", SHELLS)
def test_fuzz_control_the_oracle_finds_a_line_a_broken_scanner_hides(shell, tmp_path):
    """Mutation control: a scanner that strips after every `<<EOF` hides the canary of a quoted marker,
    and the oracle must report it (a fuzz that cannot go red proves nothing, LR-0003)."""
    command = 'echo "<<EOF"\n' + canary(0) + "\nEOF"
    assert hidden_lines(shell, command, [0], str(tmp_path), strip=strip_everything_after_a_marker) == [0]
    assert hidden_lines(shell, command, [0], str(tmp_path)) == []
