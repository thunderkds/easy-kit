# TASK_GUIDE — T294: A quoted heredoc marker no longer hides later lines from the merge gate
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read `tasks/GATE_HUNT_2026-11-08.md` (the findings this task fixes) and `docs/claude-md/untrusted-content-boundary.md`
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"do all the jobs pls"* (the open follow-ups after T291-T293 were merged). Evidence: `tasks/GATE_HUNT_2026-11-08.md`, an independent hunt of the merge gate and slot 2b. Finding P1-1: `echo "<<EOF"` on one line, then `git push --force origin main`, then `EOF`, is ALLOWED by the gate in every mode (no tag, `[auto]`, `[admin]`), and bash and zsh really push. Cause: `HEREDOC_HEADER_PATTERN` in `.claude/hooks/lib/shell_data.py` (lines 108-157) treats a `<<WORD` inside quotes, after `#`, or after a backslash as a real heredoc and strips the lines after it. The gate uses the stripped text at three call sites.

**Restated intent**:
> A `<<WORD` that the shell would not read as a heredoc (inside single or double quotes, after an unquoted `#`, or escaped with a backslash) does not make the hook strip the lines after it. The hook then sees those lines as commands, so `git push --force` after such a marker is blocked as it is without the marker. A real heredoc (unquoted `<<`) keeps today's behaviour: its body is data and is stripped. When the hook cannot tell, it keeps the text (it sees more, never less).

**Out of scope** (what this task explicitly does NOT do):
- Changing which commands the gate blocks or allows once the text is visible
- Writing a full shell parser: a small scanner for quotes, `#` and backslash is enough, and a doubt means keep the text
- Changing the other users of `strip_heredoc_bodies` beyond what the scanner needs (list them in the review file)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None

**Entry point**: `.claude/hooks/lib/shell_data.py` (`HEREDOC_HEADER_PATTERN`, `strip_heredoc_bodies`), read by `.claude/hooks/pre_bash_block_unsafe_merge.py` and other hooks

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Negative (the fix): the four hidden shapes from the finding are not stripped, so the gate blocks the force push: `echo "<<EOF"`, `echo '<<EOF'`, `true # <<EOF` and `echo \<<EOF`, each followed by a line `git push --force origin main` and a line `EOF`. Each is blocked in no-tag, `[auto]` and `[admin]` mode | Requirement |
| 2 | A real heredoc is still stripped: `cat <<EOF` / `git push --force origin main` / `EOF` (body is data) stays allowed as today; so do `<<-EOF`, `<<'EOF'`, `<<"EOF"` and `<<EOF` with a tab-indented end | no regression |
| 3 | A corpus test over the old behaviour: every command in the existing shell_data tests and the merge-gate heredoc tests keeps its result, except the hidden shapes of row 1 | no regression |
| 4 | Fail toward seeing more: a `<<` whose quote state the scanner cannot settle (unbalanced quote, a `$(...)` or backtick that opens before it) keeps the text. A test pins one such command | fail closed |
| 5 | Every other caller of `strip_heredoc_bodies` under `.claude/hooks` is listed in the review file with a note on whether it gets safer or looser; none gets looser | blast radius |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Hidden shapes (4) with `git push --force origin main` after the marker | Gate BLOCKS in no-tag, `[auto]`, `[admin]` mode | gate test through the repo's `gate` fixture |
| 2 | Real heredoc with the same body | Body stripped, allowed as today | unit test |
| 3 | Mutation: the quote check always says `not quoted` | The four hidden-shape tests turn red | mutation control that changes bytes |
| 4 | Mutation: the scanner strips every `<<` | The real-heredoc-keeps-data test or the hidden-shape tests turn red as expected; paste the red output | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "heredoc or shell_data or merge"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T294.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T294.md`.

---

## Approach

**Pattern reference**: `strip_heredoc_bodies` in `.claude/hooks/lib/shell_data.py` and the existing heredoc tests (grep `heredoc` in `.claude/hooks/tests`). Replace the regex-only header test with a left-to-right scan of the command that tracks single quotes, double quotes, backslash and `#` comments, then applies the existing header rule only at an unquoted position. Zsh and bash both run the tool shell: check both for each shape with a real throwaway repo (a bare remote under a temp dir), not only by reading.

**Vital slice**: the scanner plus the four hidden shapes and the real-heredoc regression set
**Cut list**: no parser for `$(...)`, `case`, here-strings or process substitution; those keep the text

---

## Edge Case Checklist

- [ ] A `<<` inside a `$(...)` or a backtick: keep the text (doubt means keep)
- [ ] `<<<` is a here-string, not a heredoc: keep today's behaviour
- [ ] A quote opened and closed before the `<<` on the same line: the `<<` is unquoted and real
- [ ] Several heredocs on one line
- [ ] The command text of a `bash -c '...'` or `python3 -c '...'` argument is out of scope: the existing documented limit stays
- [ ] Pin-test pre-flight: grep `.claude/hooks/tests` and `tests` for `strip_heredoc_bodies`, `HEREDOC_HEADER_PATTERN` and the gate heredoc cases; run them before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/lib/shell_data.py | The scanner |
| .claude/hooks/tests/test_heredoc_quoted_marker.py (new) | Tests |
| .claude/hooks/tests/merge_gate_guard.py | Add T294 to AUTHORISED_TASKS only if `pre_bash_block_unsafe_merge.py` changes (the Supervisor signs it off) |
| docs/claude-md/tracks.md | Remove the open-gap sentence for P1-1 from the Admin tag Known limits and state the rule (LR-0005) |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | No wiring change |
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |
| `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes; hook wiring is unchanged unless this guide says so |

---

## Test Plan

Write the tests for the Acceptance Criteria first and see them fail. Implement. Run the verification command and the full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` (bare `pytest` skips the hidden hook tests). Run each mutation control, paste the red output, restore, and paste the green output.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium/High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
