# TASK_REVIEW — T342: a glob inside a quoted span is not a path (sensitive-path hook false positive)

> Sibling of `tasks/TASK_GUIDE_T342.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Auto decisions

Mode: auto
1. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk High: changes a safety hook; C2).
2. Split the user's "[admin] has all rights" change into T342 (this hook fix, no shared file with T341) and T343 (merge-gate binding of every task the session started + `### Stops that stay` list; waits for T341, which edits `.claude/hooks/pre_bash_block_unsafe_merge.py` and `docs/claude-md/tracks.md` now) — RULE: `AGENTS.md` § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task").
3. Fix shape: A, default direction "expand" — a glob in a quoted span is not expanded only when the span's segment command is on a short allowlist of commands that neither glob nor run a shell (`grep`/`egrep`/`fgrep`/`rg`, `sed` without an `e` command, `sort`, `cut`, `tr`); every other quoted span (unknown wrappers such as `su -c`, `xargs`, `watch`, self-globbing `git`/`rsync`/`tar`) still expands; literal checks of every token stay; `sed`/`awk` stay out of `DATA_COMMAND_PATTERN` — DEBATED: A (Advocate 1: A, skip only for known non-executing commands so an unknown wrapper still expands; Advocate 2: A, keyed on `SPAN_EXECUTOR_PATTERN`, plus expand for self-globbing `git`/`rsync`/`tar`; Advocate 3: A, keyed on the segment's command, skip only for a short known list) — all three reject B (`cd .cl*` lands in `.claude` and stops being caught) and C (`sed e`/`w`, `awk system()` execute). The direction split is settled by RULE: `.claude/hooks/lib/shell_data.py:384` "Unknown must resolve toward **code**".
4. No `[admin]` bypass of the sensitive-path hook; a planned path is already silent in every mode (guide `## Files to Change (Predicted)`) — RULE: `.claude/hooks/pre_tool_sensitive_path.py:7` "unless the active task's guide predicted that exact path".
5. Implementer: a `common-infrastructure` sub-agent, not the Supervisor — RULE: `AGENTS.md:171` "The Supervisor must never write implementation code directly." (Hard-Stop Gate 1; T341 has not merged).
6. code-review P1 (escaped quote `\"` opened a span and hid an unquoted glob: `cd d; sed -i -e "s/a/b/" \" .cl* \"` asked on main, silent on e505762) fixed by the implementer in 78b76f2 — RULE: `AGENTS.md` § Permanent Rules ("Stage 4 (code-review) is mandatory for every extended-track task"); the fix is the unterminated-quote safe side, `.claude/hooks/lib/shell_data.py:384` "Unknown must resolve toward **code**".
7. Security review by hand: the built-in `security-review` skill fails (`git diff origin/HEAD...`: "fatal: ambiguous argument 'origin/HEAD...': unknown revision") — RULE: precedent `tasks/TASK_REVIEW_T326.md:55` "Security review done by hand: the built-in `security-review` skill fails here". Result: 0 open P0/P1; recorded limit (not new): output piped into a shell (`sed -n '1i rm -rf .c*' /dev/null | sh`) is not seen, as `printf 'rm -rf .c*' | sh` is not seen on main.
Checks: code-review 0 P0 / 1 P1 (fixed, 78b76f2) / 0 P2 / 1 P3 (codebase-map read in full in the fix round); security-review by hand, 0 P0/P1; probe of 11 bypass shapes, each hook on its own checkout: branch 78b76f2 asks wherever main 85f2006 asks, and the T341 test command is silent; Verification Command by the Supervisor on 78b76f2 2026-11-20T11:20:18Z: `158 passed, 126 subtests passed in 13.35s`; full suite 54 failed (strict subset of main's 55); real run: auto-checked, not /verify.
Memory: `memory/decisions.md` entry "2026-11-20 — T342: a glob in a quoted span of grep/rg/sed/sort/cut/tr is not a path" (rule, P1 fix, recorded limits, `uv run --with` not counted as a test run)
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass — auto-run by hook, commit 771406884d2c, log `.claude/verify-runs/T342-771406884d2c.log`

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t342_quoted_glob.py` (new, AC 1-5, 7; AC 3 holds the Stage 4 escaped-quote cases). Red on 85f2006 parent of fix: `7 failed, 8 passed, 24 subtests passed in 1.19s`; P1 red on e505762: `2 failed, 10 passed, 37 subtests passed in 1.50s` |
| Verification command run | ☑ pass | Supervisor, 78b76f2, 2026-11-20T11:20:18Z, via `uv run -q --with pytest` (python3 has no pytest here): `158 passed, 126 subtests passed in 13.35s` |
| Negative cases hold | ☑ pass | AC 3/4/5 ask before and after; AC 7 revert test turns AC 1/2 red; Supervisor probe, each hook on its own checkout: `cd d; sed \" .c* \" f`, `cd d; sed -i -e "s/a/b/" \" .cl* \"`, `sed "s/x/$(cat .cl*)/"`, backtick, `sed 's/x/y/' .c*` ask on 78b76f2 as on main |
| verify | ☑ pass | auto-run by hook, session 7f126e61-7978-4e2d-a257-8418c26342d8, commit 771406884d2c734c95e2554e2debed6e63ed5d14, log .claude/verify-runs/T342-771406884d2c.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `.claude/hooks/pre_tool_sensitive_path.py` diff, its imports from `.claude/hooks/lib/shell_data.py` (unchanged), its tests; `TOKEN_SPLIT_PATTERN` has no other user (grep). Merge hook not touched |
| Full smoke suite still green (no regression) | ☑ pass | 78b76f2: `54 failed, 7530 passed, 24 skipped, 126 subtests passed in 389.04s`; main 85f2006: `55 failed, 7519 passed`; branch failures a strict subset of main's (missing shells, MEMORY.md budget, gate hunt tests) |
| **Companion score (easy-verifier)** | ☑ N/A | neither companion tool was run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: hook-only change |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI: hook-only change |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI: hook-only change |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**:
```
captured 2026-11-20T15:46:14 hook at <kit> HEAD 62b45ec
$ cd <tmp>/wt; uv run --with pytest python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider -n0 2>/dev/null | grep -E "^FAILED|passed|failed" | sed 's/ - .*//' > <tmp>/branch.txt; tail -1 <tmp>/branch.txt
-> {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Bash call touches a sensitive path: <kit>/.claude/ (pattern `.claude/st
$ cd <tmp>/wt; pytest x > /tmp/a.txt
-> (no output: allow)
```

**AFTER**:
```
captured 2026-11-20T18:20:59 hook at <wt-t342> HEAD 78b76f2
$ cd <tmp>/wt; uv run --with pytest python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider -n0 2>/dev/null | grep -E "^FAILED|passed|failed" | sed 's/ - .*//' > <tmp>/branch.txt; tail -1 <tmp>/branch.txt
-> (no output: allow)
$ cd <tmp>/wt; pytest x > /tmp/a.txt
-> (no output: allow)
```

**DELTA**: a test run piped through `sed 's/ - .*//'` after a `cd` no longer stops an `[admin]` run with a sensitive-path ask; every case that asked on main still asks.

**WITNESS**: the Supervisor ran BEFORE (main 62b45ec, 2026-11-20T15:46:14 local) and AFTER (78b76f2) with `replay.py`, and the Verification Command at 2026-11-20T11:20:18Z, in session trace `memory/event-trace/T342.jsonl`; not the implementing agent.
