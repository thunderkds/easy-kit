# TASK_REVIEW — T320: the merge gate treats `gh pr merge` and the GitHub merge API as merges

Reviewer: fresh-context, commit 8e100d20007c3971d02f06a60416429546cc3695, diff main...8e100d2. Skills: code-review, security-review (Risk High).

## Verdict: PASS WITH FINDINGS (no P0/P1; 1 P2 doc defect, 2 P2/P3 residual bypasses, 2 P3 false positives)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t320_gh_merge_gate.py`; `uv run --with pytest python -m pytest .claude/hooks/tests/test_t320_gh_merge_gate.py -q -p no:cacheprovider` -> `24 passed in 1.88s`. AC1-5 each covered. |
| Verification command run | ☑ pass | Above, plus `test_merge_gate_t210.py test_admin_tag.py` -> `280 passed in 15.73s` (no pin-test regression) |
| Negative cases hold | ☑ pass | Probe of the two regexes on 50 commands (scratchpad `q.py`, patterns copied verbatim, input run through `strip_heredoc_bodies`/`strip_quoted_spans` as the gate does). Results below. |
| verify | ☐ N/A | Left for the auto verify hook |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the 2 patterns, `AUTO_MODE_PATTERNS` derivation (line 1431, only drops the rebase pattern, so both new patterns reach auto mode), the new test, `AUTHORISED_TASKS` pin, tracks.md edit. Not reviewed: unrelated gate code. |
| Full smoke suite still green (no regression) | ☑ pass | `uv run --with pytest --with pytest-xdist python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider -n 4` on `434a863`: `56 failed, 7724 passed, 24 skipped`. The same command on `main` (`a0aefe7`) in this environment: `64 failed`. Branch-only failures: `test_step_limit_agent_scope::test_ac1_two_agents_of_one_task_have_two_counters_and_no_shared_block` and `test_auto_verify::test_ac2_a_second_stop_on_the_same_commit_starts_nothing_on_the_minimal_track` — each `1 passed` run alone (load-flaky, same family as `main`'s failures). No failure comes from the gate change. |
| Companion score (easy-verifier) | ☑ N/A | Not run. |
| UI rows | ☑ N/A | No UI. |

## Findings

### P2-1 tracks.md sentence is broken (docs defect)
`docs/claude-md/tracks.md` line ~754: the T320 text was inserted in the middle of a sentence. It now reads "...while that request is the latest `gh pr merge` and a `gh api` call ... `[admin]` allows no `gh` command." and the next line begins "one. A `git rebase` is not part of this rule." The original sentence ("...is the latest one.") is cut in two and now says something false. Fix: move the new sentence after "...is the latest one." (or after the rebase sentence).

### P2-2 Bypass: quoted or variable verb, same shape as the git "hidden form" the gate refuses
Matched on the quote-stripped command, these still run silently with no gate (probe result False):
- `gh pr "merge" 1`, `gh pr 'merge' 1`, `gh "pr" merge 1`
- `gh pr $(echo merge) 1`, `cmd=merge; gh pr $cmd 1`
- `gh api repos/o/r/pulls/3/'merge' -X PUT`
The gate already blocks such hidden forms for `git` (`hidden_git_verb`, "cannot tell: ... a `$`, brace, glob, quote ... between the git word and its verb"). No equivalent exists for `gh`. The guide's "over-blocks on doubt, like the git patterns" is not true for `gh`. An agent in `[admin]`/`[ticket]` session can use these. Cut list does not name it. Suggest: treat quote/`$`/backtick between `gh` and `merge` like the git hidden-verb rule, or record it as a known cut.

### P2-3 Bypass: other GitHub merge routes (cut list names only `curl`/`hub`/aliases)
Not matched: `gh api graphql -f query='mutation{mergePullRequest(...)}'` (GraphQL merge, the official alternative), `gh api repos/o/r/git/refs/heads/main -X PATCH -f sha=...` (moves main directly), `gh alias set m 'pr merge'; gh m 1` is caught only because the same line holds `pr merge` inside quotes... note: probe flagged it True only because quote stripping is not applied to the alias text in that case; `gh m 1` alone in a later command would pass. `gh pr merge` via `curl`/`hub` also pass (declared cut). graphql and refs PATCH are not in the declared cut list; add them to it or block `mergePullRequest`.

### P3-1 False positive: read-only GET of the merge endpoint
`gh api repos/o/r/pulls/3/merge` (default GET, "is it merged?"), with `--method GET`, `-X GET` or `--jq .merged` is blocked (probe True). Read-only, so by the task's own AC5 spirit it should pass. Cost is small (only blocks when a task is In Progress or in auto mode). Same for `gh pr merge --help` and `gh help pr merge`, and a trailing comment (`# gh pr merge later`).

### P3-2 `merge-base` boundary
`gh pr merge-base` and `.../pulls/3/merge-base` match (`\b` after `merge` accepts `-`). The guide AC5 mentions "`gh pr merge-base-notes` is not a command" but no test pins it. Neither is a real gh route, so impact is nil; either add `(?![-\w])` or drop the claim from AC5.

## Correct as built
- `gh pr merge` with global flags (`-R`, `--repo`), after `cd x &&`, `env`, `GH_TOKEN=x`, absolute path, inside `sh -c`/`eval` quotes (stripped spans kept), after `xargs`: all blocked.
- `gh pr view/list/create/checks/comment`, `gh api .../pulls/3`, `echo "gh pr merge"`, `grep "gh pr merge"`: not blocked.
- ReDoS: both patterns use `[^;&|\n]*?` segments bounded by separators, linear on realistic input. No finding.
- `[admin]` stays git-only; no `.claude/settings.json` or `lib/auto_mode.py` edit (matches "Must NOT touch").
- `AUTHORISED_TASKS` pin updated with sign-off comment, matching prior entries.

## Demonstration
**BEFORE**: neither `gh pr merge` nor the merge API was in `BLOCKED_PATTERNS` (board row T320).
**AFTER**: `test_t320_gh_merge_gate.py` 24 passed.
**DELTA**: `gh pr merge` and the merge API are gated like `git merge`, in auto mode too.
**WITNESS**: reviewer run, this file.

## Round 2

Reviewer: fresh-context, commit 06878ee7b65fe3e6c840710887eaa0cec5174814, diff main...06878ee. Skills: code-review, security-review (Risk High), applied to `GH_MERGE_PATTERNS`, `gh_merge_hit`.

### Verdict: PASS WITH FINDINGS (no P0/P1; all five round 1 P2 findings fixed; 1 new P2 bypass, 3 P3)

### Evidence

| Check | Result | Notes |
|-------|--------|-------|
| Tests | pass | `uv run --with pytest python -m pytest .claude/hooks/tests/test_t320_gh_merge_gate.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider` -> `82 passed in 1.44s` |
| Probe | done | 70 commands run through `gh_merge_hit` (hook source exec'd with the trailing `main()` removed; script in scratchpad `p2.py`). Key results below. |
| Full smoke suite | not run | Scoped to gate tests. |

### Round 1 P2 fixes: all verified
- Quoted and `$` verbs: `gh pr "merge" 1`, `gh pr 'merge' 1`, `gh "pr" merge 1`, `gh pr $(echo merge) 1`, `cmd=merge; gh pr $cmd 1`, `pulls/3/'merge'` all return True.
- GraphQL: `mergePullRequest` in single or double quotes returns True.
- `/git/refs` writes: `-X PATCH`, `--method PATCH`, `-X=PATCH`, `-XPATCH`, `-X patch`, `-X DELETE`, `-X POST`, and a `-f` field all True; plain GET and `--jq` read False.
- `tracks.md`: the T320 sentence now follows the complete rebase sentence; the original sentence is intact. Fixed.
- `merge-base` pin: `gh pr merge-base` and `merge-base-notes` return False. Fixed for the CLI. (Endpoint form: P3-3.)

### New findings

#### P2-1 Bypass: backslash-newline continuation between `gh` words
`gh \<newline>pr merge 1`, `gh pr \<newline>merge 1` and `.../pulls/3/\<newline>merge -X PUT` all return False. The git side blocks a backslash in the verb gap as a hidden form; no `gh` equivalent exists, and `GH_QUOTED_WORD` does not touch it. Same class as round 1 P2-2. Fix: join `\<newline>` before scanning, or treat a backslash between `gh` and the verb as a doubt.

#### P3-1 Bypass: merge mutation or ref write the text cannot show
All return False: `gh api graphql -f query=@merge.gql`, `gh api graphql --input q.json`, `-f query="$Q"`, `gh api graphql --input -` with a piped body, `gh api .../git/refs -X "PATCH"` (quoted method; the ref check reads the raw command), `gh api .../git/refs/heads/x $(echo -X) PATCH`, and `mergePullRequest` split by `${x}`. A body in a file or a variable cannot be read; the sound rule is a doubt on any `gh api graphql` with `@`, `--input` or `$` in a non-data segment. Other write routes also pass: `gh api repos/o/r/contents/f -X PUT -f branch=main` (commits to main), `gh api repos/o/r/merge-upstream -f branch=main`, `gh repo sync o/r`. Add these to the cut list or gate them.

#### P3-2 False positives (cost: a block only when a task is In Progress or in auto mode)
`gh api repos/o/r/pulls/3/merge` as a read (also `-X GET`), `gh pr merge --help`, `echo hi # gh pr merge later`, `gh api repos/o/r/issues -f body="mergePullRequest"` (text in a field), `gh pr $(echo view) 3`. Guide accepts the first as a cut; the rest are the same shape. Acceptable.

#### P3-3 Endpoint `merge-base` still matches
`gh api repos/o/r/pulls/3/merge-base` returns True: `/pulls/[^/\s]+/merge\b` accepts `-`. Not a real route, so impact is nil; add `(?![-\w])` for symmetry with the CLI pattern.

### Security review
- No injection or code execution: the code only runs `re` on the command text. `GH_QUOTED_WORD` is `(["'])([^\s"']*)\1`, linear. `GH_REF_WRITE` has one `.*` after a fixed prefix, no nested quantifiers; the `[^;&|\n]*?` segments in `GH_MERGE_PATTERNS` are bounded by separators. No ReDoS.
- Fail-closed: `gh_merge_hit` returns True on any exception; the call is placed in the `auto_pattern` OR chain, so a hit blocks. Correct.
- `[admin]` and `lib/auto_mode.py` untouched; both new patterns reach auto mode via `BLOCKED_PATTERNS`.
- Residual risk: a determined agent can still merge by P2-1, P3-1 routes, `curl`, `hub` or an alias (last three declared cuts). The gate stops accidents and casual forms, not an adversary; say so in the guide's cut list.

### Demonstration
**BEFORE**: round 1 probe had 6 quoted/variable/GraphQL/ref forms returning False.
**AFTER**: those forms return True; 82 tests pass.
**DELTA**: one new bypass class found (line continuation).
**WITNESS**: reviewer run, this file.

## Round 3

Reviewer: fresh-context, commit 434a863b2933fc87b463b310425e01a9245989b7, diff main...434a863 (delta since round 2: one line in `_gh_merge_hit` plus 3 tests, guide cut list). Skills: code-review, security-review (Risk High).

### Verdict: PASS (no P0/P1/P2; round 2 P2-1 fixed; 1 P3 note)

### Evidence

| Check | Result | Notes |
|-------|--------|-------|
| Tests | pass | `uv run --with pytest python -m pytest .claude/hooks/tests/test_t320_gh_merge_gate.py .claude/hooks/tests/test_merge_gate_guard.py -q -p no:cacheprovider` -> `85 passed in 1.54s` (82 + 3 new) |
| Probe | done | 10 commands through `gh_merge_hit` (hook source exec'd with `main()` removed). |

### Round 2 P2-1: fixed
`command.replace("\\\n", "")` runs first, and the result feeds both the pattern scan and the per-segment loop. Returns True for `gh \<nl>pr merge 1`, `gh pr \<nl>\<nl>merge 1`, `gh pr mer\<nl>ge 1` (split inside the word), `gh pr \<nl>"merge" 1` (continuation plus quote), and the endpoint form `pulls/3/\<nl>merge -X PUT` (new test).

### No new bypass or false positive
- A plain newline (no backslash) still separates commands: `gh pr view 1<nl>gh pr merge 2` True, as before.
- Benign continuations stay False: `gh pr view 1 \<nl> --json x`, `gh pr view \<nl> 1; echo merge`, `gh api repos/o/r/pulls/3 \<nl> -q .merged`.
- `\<CR><LF>` is not joined, and bash does not join it either, so no gap.
- P3 note: `echo hi \<nl> gh pr merge` returns True (joined into one echo line, the pattern still matches). Over-blocks a contrived case only; same class as round 2 P3-2.
- The old remaining round 2 P3-1/P3-2/P3-3 are unchanged by this delta; the guide cut list now records them as accepted limits.

### Security review
The delta is a plain `str.replace` with no regex, so no ReDoS or injection surface. Fail-closed wrapper is unchanged. No other file touched in the code delta.

### Demonstration
**BEFORE**: 3 line-continuation forms returned False (round 2).
**AFTER**: all return True; 85 tests pass.
**DELTA**: round 2 P2-1 closed, no new P2 or above.
**WITNESS**: reviewer run, this file.
