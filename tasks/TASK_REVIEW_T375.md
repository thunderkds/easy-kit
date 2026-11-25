# TASK_REVIEW — T375: The sensitive-path hook dequotes a word before it matches a sensitive path

> Sibling of `tasks/TASK_GUIDE_T375.md`. Filled at Stage 4/5. Round 1 of the fresh reviewer (`Reviewer: T375`) ran on `c4329f12`; the commit under review for the merge is the head of `fix/t375-dequote-sensitive-tokens`.

---

## Auto decisions

Mode: auto
1. Took T375 from the board ("continue your work by picking tasks [admin]") — RULE: `docs/claude-md/tracks.md` `### Admin tag`
2. Track extended — RULE: `docs/claude-md/tracks.md` `## Track rule`
3. The Supervisor wrote the code, one fresh `Reviewer: T375` spawn per round — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. A word the shell still builds (`${x}`, `$x`) next to literal text is read as `*` and globbed; only a real sensitive file asks (the row's "ask on a word the shell still builds when it is next to a sensitive name") — DEBATED: option A, glob (Advocate 1: keep A, record the gaps; Advocate 2: keep A, record the `/` and not-yet-existing-file gaps; Advocate 3: keep A, the smallest safe thing) ⚠ decided for you — please review
5. Fixed the security finding (an ANSI-C escape in a word hid `find -delete` from `only_reads`, so an `[admin]` call went unlogged) and named the two glob gaps in the header — RULE: `skills/code-review/SKILL.md:142` "#### Phase 4 — Apply Safe Fixes"
6. Dropped `git commit -m "fix .env bug"` from AC 4: a commit message already asks on `main`, unchanged by this task — FACT: `.claude/hooks/lib/shell_data.py:371` "The default is **keep**."
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t375_dequote_tokens.py` — red first (`9 failed, 7 passed`), then green; the six sensitive-path suites `93 passed, 186 subtests passed`; reviews code-review (Supervisor, no P0/P1), security-review (1 Low, fixed in `efff9e8a`); fresh reviewer round 1 running on `c4329f12`
Memory: nothing new
Not done: merge (admin: after the auto verify pass and the reviewer's last round); auto verify: not run yet

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t375_dequote_tokens.py` (AC 1–6 and the security pin) |
| Verification command run | ☑ pass | the guide's six suites: `93 passed, 186 subtests passed in 21.41s` (before the security fix); the new file after it: `9 passed, 21 subtests passed` |
| Negative cases hold | ☑ pass | red run on `main` before the change: `9 failed, 7 passed, 12 subtests passed in 1.47s`; the security pin was red before its fix (`1 failed, 8 passed`) |
| verify | ☐ pass / ☐ fail / ☐ N/A | the auto verify hook writes this row |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | the hook, its list header and its tests; the lane check printed `EXCEEDS (lines 304 > 250)`, the new test file is most of it |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | hook tests: `6 failed, 5768 passed`; the MEMORY.md budget failure fails on `main` too; the other five are not yet compared with `main`. The root `tests/` run: `89 failed` in one full run, all with `getcwd() failed`; the same six files run alone give `2 failed, 244 passed` on both `main` and the branch |
| **Companion score (easy-verifier)** | ☐ N/A | tool not used |

---

## Demonstration

**BEFORE**: on `main`, `cat .claude/sens''itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt`, `find config -d$'elete'` and `cat .claude/sens${x}itive-paths.txt` printed no decision (the hook stayed silent). Red run: `9 failed, 7 passed, 12 subtests passed in 1.47s` (no timestamp was captured).

**AFTER**: each of those commands asks; `echo "see .env file"` and `cat "$F"` stay silent.

**DELTA**: a quote, a backslash or a built part inside a word no longer hides a sensitive path from the hook.

**WITNESS**: the Supervisor, 2026-11-25; the reviewer rounds are in the event trace.
