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
| Full smoke suite still green (no regression) | ☑ pass (scoped) | Gate tests above only; full repo suite not run. |
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
