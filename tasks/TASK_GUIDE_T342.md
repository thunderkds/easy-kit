# TASK_GUIDE — T342: a glob inside a quoted span is not a path (sensitive-path hook false positive)
**Date**: 2026-11-20
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. Read `memory/codebase-map.md` (C2, multi-file)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-20: "let check why I use [admin] tag, but got the ask for the sensitive path command … why don't you do that in [admin] tag", then "with admin mode, you have all right, one stop point is the problem that you can solve like the question about the technical doubt, biz change the app direction, or something break the flow and need my approve on that", then "yes, start [admin]".

Diagnosis (Supervisor, replayed through the hook): the T341 session's test command
`cd …/wt-t341; uv run --with pytest python -m pytest .claude/hooks/tests tests -q … | sed 's/ - .*//' > …/branch.txt`
got `[hook:sensitive-path] This Bash call touches a sensitive path: …/easy-kit/.claude/ (pattern `.claude/state/**`)`.
`strip_quoted_spans` keeps the `sed` script (sed is not a data command, correctly). `command_tokens` (`.claude/hooks/pre_tool_sensitive_path.py:258`) then splits it into tokens, sees `.*` carries a glob character and expands it with `glob.iglob` against the project root, which yields `.claude`. The command holds `cd`, so rule S2 (`sensitive_hits`, `STATE_PARENTS`) asks. Bisect: `cd <wt>; pytest x | sed 's/ - .*//'` asks; `cd <wt>; pytest x > /tmp/a.txt` and `cd <wt>; pytest .claude/hooks/tests -q` are silent.

**Restated intent**:
> A glob character inside a quoted span is never expanded as a file path unless that span runs in a shell, because the outer shell does not expand quoted text. Ordinary test runs that pipe through `sed`/`awk`/`grep -E` with a `.*` pattern no longer stop an `[admin]` run, and every write or read of a real sensitive path still asks.

**Out of scope**:
- Expanding globs against the `cd` target instead of the project root (a separate known limit; record it, do not fix it).
- Any change to which commands count as data (`DATA_COMMAND_PATTERN`) — `sed` stays code: it can write (`w`) and run (`e`) files.
- Any `[admin]` bypass of the hook. The hook keeps asking in every mode for a real sensitive path.
- The merge-gate binding and the stop list (T343).

**Requirement Refs**: none in `PRD.md` (kit hook fix); source is the user's request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed — Supervisor, 2026-11-20, under `[admin]` (user: "yes, start [admin]")
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (sensitive path, quoted span, data command, executor)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] No `PRD.md` refs (kit hook fix); the AC cover the restated intent in full

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `command_tokens`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The two commands from the T341 session, verbatim (with the worktree path pointed at a temp dir), are silent: `cd <dir>; uv run --with pytest python -m pytest .claude/hooks/tests tests -q -p no:cacheprovider -n0 2>/dev/null \| grep -E "^FAILED\|passed\|failed" \| sed 's/ - .*//' > <tmp>/branch.txt; tail -1 <tmp>/branch.txt` and the second (`… > $SP/branch_full.txt 2>&1; tail -1 …; grep ^FAILED … \| sed 's/ - .*//' \| sort > …`). The temp project root holds a `.claude/` folder and a `.env`. | the false positive |
| 2 | A glob character inside a single- or double-quoted span is not expanded against the filesystem when the span's segment has no executor (`SPAN_EXECUTOR_PATTERN` in `.claude/hooks/lib/shell_data.py`): `sed 's/a.*//' f`, `awk '/x.*/' f`, `cd d; grep -E '.*' f`, `cd d && sed "s/.*//" f`, `find . -name '*.py'` are silent with `.claude/` and `.env` present. | quoted text is not a path |
| 3 | A glob in a span that runs in a shell is still expanded and still asks: `bash -c 'cat .env*'` (with `.env.prod` present), `cd d; bash -c 'rm -rf .c*'`, `eval "cat .env*"`. | still asks for a real path |
| 4 | Unquoted globs keep today's behaviour: `cat .env*` asks (existing `test_bash_glob_is_expanded`), `cd d; rm -rf .c*` asks (expands to `.claude`, S2), `cd d; rm -rf .claude/sta*` asks. | still asks |
| 5 | Literal sensitive paths inside a kept quoted span still ask: `sed -i 's/x/y/' .env`, `sed 'w .claude/state/x' f`, `cd d; sed 's/x/y/' .claude/state/a`. | still asks |
| 6 | Every existing test in `.claude/hooks/tests/test_pre_tool_sensitive_path.py`, `test_t314_*.py` and `test_quoted_spans_t099.py` passes unchanged. | no regression |
| 7 | Anti-vacuity: reverting only the new "no expansion inside a non-executor quoted span" rule turns AC 1 and AC 2 red (a test that applies the revert, as `test_sc8a_dropping_the_quoted_span_keep_rule_turns_sc4_red` does). | the test proves the fix |
| 8 | The hook's module docstring `Recorded limitations` names the rule and the remaining limit: globs are expanded against the project root, not the `cd` target. | honest limits |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | T341 session test command, project with `.claude/` and `.env` | no output from the hook (allow) | automated test |
| 2 | `cd d; bash -c 'rm -rf .c*'` | `ask`, reason names `.claude` | automated test |
| 3 | `sed -i 's/x/y/' .env` | `ask`, reason names `.env` | automated test |
| 4 | the new rule reverted | AC 1/2 tests fail | automated test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t342_quoted_glob.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_quoted_spans_t099.py .claude/hooks/tests/test_t314_online_approval.py .claude/hooks/tests/test_t314_fix_round.py .claude/hooks/tests/test_t314_security_round.py .claude/hooks/tests/test_t314_backslash_key.py -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T342.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T342.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/lib/shell_data.py` `strip_quoted_spans` and `SPAN_EXECUTOR_PATTERN` — the existing data/code split for quoted spans; `.claude/hooks/tests/test_pre_tool_sensitive_path.py` `test_sc8a_dropping_the_quoted_span_keep_rule_turns_sc4_red` — the anti-vacuity revert pattern; `.claude/hooks/tests/test_pre_tool_sensitive_path.py` `bash()` / `assert_ask` / `assert_silent` helpers — the fixture shape.

**Vital slice**: in `command_tokens`, tell tokens from a kept quoted span (without an executor in its segment) apart from unquoted tokens, and skip `glob.iglob` for the first kind only. Literal checks of every token stay.

**Cut list**:
- Expanding globs against the `cd` target (recorded limit, AC 8).
- A per-command allowlist (`sed`, `awk` …) — rejected: the fix is shell quoting semantics, not a command list.

Decision (FACT, logged in `tasks/TASK_REVIEW_T342.md` `## Auto decisions`): the outer shell does not expand globs in quoted words (bash(1) `QUOTING`: "Enclosing characters in single quotes preserves the literal value of each character"; pathname expansion does not apply to quoted characters); only a span run by an inner shell is expanded there.

---

## Edge Case Checklist

- [ ] Mixed word: `'.c'*` — the `*` is unquoted, so the shell expands it; treat a token that has any unquoted glob character as unquoted (over-asking is the safe side).
- [ ] Unterminated quote: `strip_quoted_spans` leaves the rest as it arrived; keep expansion as today for that tail (safe side).
- [ ] Quoted redirect targets (`QUOTED_REDIRECT_TARGET_PATTERN`) are collected before stripping; their behaviour must not change.
- [ ] Heredoc bodies are stripped first, unchanged.
- [ ] Executor detection is per segment, the same way `strip_quoted_spans` decides it — reuse, do not write a new regex.
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for "glob" in the hook docstring, `docs/claude-md/`, `.claude/sensitive-paths.txt` comments

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | `command_tokens`: no glob expansion for tokens from a non-executor quoted span; docstring `Recorded limitations` (AC 8) |
| `.claude/hooks/lib/shell_data.py` | only if a small helper is needed to expose which spans are kept and why; no behaviour change for the merge hook |
| `.claude/hooks/tests/test_t342_quoted_glob.py` | new: AC 1-5, 7 |
| Pre-existing pin tests | `.claude/hooks/tests/test_quoted_spans_t099.py` (pins `strip_quoted_spans` direction — must stay green, do not edit); `test_pre_tool_sensitive_path.py` (`test_bash_glob_is_expanded`, `test_sc4_*`, `test_sc8a_*` — must stay green, do not edit); `test_t314_*.py`. If `shell_data.py` changes, also run `.claude/hooks/tests/test_merge_gate*.py` (the merge hook imports it). Escalate if any of these needs an edit. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | T341 is changing it now; T343 owns the merge-gate change |
| `docs/claude-md/tracks.md` | T341 is changing it now; T343 owns the stop list |
| `.claude/sensitive-paths.txt` | the pattern list is not the bug |
| `.claude/settings.json` | no permission change |

---

## Test Plan

TDD: write `.claude/hooks/tests/test_t342_quoted_glob.py` first with the existing test file's fixture shape (temp project with `.claude/`, `.env`, `.env.prod`), see AC 1-2 fail for the reason above (the ask names `.claude/` or `.env`), then change `command_tokens`. Run the Verification Command, then the full suite (`python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider`); on this machine some tests fail on unchanged `main` for missing shells (`busybox`, `zsh`): compare the failing set against `main`, do not fix them.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (if Medium/High risk)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T342.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run — feature confirmed working in running app
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review
