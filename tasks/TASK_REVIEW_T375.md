# TASK_REVIEW — T375: The sensitive-path hook dequotes a word before it matches a sensitive path

> Sibling of `tasks/TASK_GUIDE_T375.md`. Filled at Stage 4/5. Round 1 of the fresh reviewer (`Reviewer: T375`) ran on `c4329f12`; the commit under review for the merge is the head of `fix/t375-dequote-sensitive-tokens`.

---

## Auto decisions

Mode: auto
1. Took T375 from the board ("continue your work by picking tasks [admin]") — RULE: `docs/claude-md/tracks.md` `### Admin tag`
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High row)
3. The Supervisor wrote the code, one fresh `Reviewer: T375` spawn per round (eight rounds, on `c4329f12`, `df05f4ca`, `69bed0e6`, `e38eabcd`, `7f2b4fa4`, `fa996ec3`, `d9b4d205`, `6e04f86b`) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. A word the shell still builds (`${x}`, `$x`) next to literal text is read as `*` and globbed; only a real sensitive file asks (the row's "ask on a word the shell still builds when it is next to a sensitive name") — DEBATED: option A, glob (Advocate 1: keep A, record the gaps; Advocate 2: keep A, record the `/` and not-yet-existing-file gaps; Advocate 3: keep A, the smallest safe thing) ⚠ decided for you — please review
5. Fixed every P0-P2 finding of rounds 1-7 and spawned the reviewer again after each; each fix had a test that was red first — RULE: `skills/code-review/SKILL.md:142` "#### Phase 4 — Apply Safe Fixes". The findings: security review (an ANSI-C escape hid `-delete` from `only_reads`); round 1 (P1 data commands blank quoted spans, P2 `$E.env`, brace next to a quote, a vacuous negative test); round 2 (P1 bare `*` token, P2 wholly quoted built word); round 3 (P2 `*-*` piece, backslash-newline); round 4 (P2 `$` in a spaced span, dot-led glob); round 5 (P2 escaped quote ends the pairing, `./.??`); round 6 (P2 quoted `$(…)` is code); round 7 (P2 a spaced span behind `bash -c`/`eval`/`ssh` is code). Round 8: PASS, no P0-P2
6. Dropped `git commit -m "fix .env bug"` from AC 4: a commit message already asks on `main`, unchanged by this task — FACT: .claude/hooks/lib/shell_data.py:371 "The default is **keep**."
7. Left the P3 findings as recorded limits in the hook header (`$(…)` and backtick built parts, short literal prefixes, the folder rule's built parts, `--exclude=".env"`, a comment apostrophe, `${F:-.env}`) — RULE: `skills/code-review/SKILL.md:28` "| **P3** | Style, minor improvement, documentation | Optional |"
Checks: tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t375_dequote_tokens.py` — red first in every round, `25 passed, 95 subtests passed` at the end; the six sensitive-path suites and `test_t342_quoted_glob.py` `119 passed, 299 subtests passed`; full hook tests `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests` on `6e04f86b` — `5 failed, 5785 passed`, the same 5 MEMORY.md budget failures as `main` (`5 failed, 5760 passed`); reviews code-review (Supervisor), security-review (Supervisor, 1 Low fixed), fresh reviewer rounds 1-8 (round 8 PASS)
Memory: nothing new
Not done: merge (admin: after the auto verify pass; the user typed `merge T375 [admin]`); auto verify: ☑ pass (session 577bd72f-75c4-48e2-baca-b85c28f2e10b, commit de74437e97eef5737425407ae1626ddf7d3e3b9d, log .claude/verify-runs/T375-de74437e97ee.log)
Closed: row moved to Done 2026-11-25 — auto verify pass (session 577bd72f-75c4-48e2-baca-b85c28f2e10b, commit de74437e97eef5737425407ae1626ddf7d3e3b9d); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t375_dequote_tokens.py` (AC 1–6, the security pin and one test per review round) |
| Verification command run | ☑ pass | the guide's command plus `test_t342_quoted_glob.py`: `119 passed, 299 subtests passed`; the new file alone at `6e04f86b`: `25 passed, 95 subtests passed` |
| Negative cases hold | ☑ pass | red on `main` before the change: `9 failed, 7 passed, 12 subtests passed in 1.47s`; every later round's tests were red before their fix (security `1 failed`; round 1 `12 failed`; round 2 `17 failed`; round 3 `7 failed`; round 4 `11 failed`; round 5 `8 failed`; round 6 `6 failed`; round 7 `6 failed`); the only-a-variable guard fails 4 tests when removed |
| verify | ☑ pass | auto-run by hook, session 577bd72f-75c4-48e2-baca-b85c28f2e10b, commit de74437e97eef5737425407ae1626ddf7d3e3b9d, log .claude/verify-runs/T375-de74437e97ee.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | the hook, its list header and its tests; the lane check printed `EXCEEDS (lines 304 > 250)` at the first commit, the new test file is most of it |
| Full smoke suite still green (no regression) | ☑ pass | hook tests: `5 failed, 5785 passed`, the same 5 failures as `main` (MEMORY.md budget); root `tests/`: the six files the first run failed give `2 failed, 244 passed` on both `main` and the branch (the 89 failures of one full run were `getcwd() failed` noise) |
| **Companion score (easy-verifier)** | ☐ N/A | tool not used |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: a PreToolUse hook |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI: a PreToolUse hook |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI: a PreToolUse hook |

---

## Demonstration

**BEFORE**: on `main`, `cat .claude/sens''itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt`, `find config -d$'elete'` and `cat .claude/sens${x}itive-paths.txt` printed no decision (the hook stayed silent). Red run: `9 failed, 7 passed, 12 subtests passed in 1.47s` (no timestamp was captured).

**AFTER**: each of those commands asks; `echo "see .env file"` and `cat "$F"` stay silent.

**DELTA**: a quote, a backslash or a built part inside a word no longer hides a sensitive path from the hook.

**WITNESS**: the Supervisor, 2026-11-25; the reviewer rounds are in the event trace.
