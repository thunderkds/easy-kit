# TASK_GUIDE — T363: The sensitive-path hook asks when a destructive command targets a folder that holds a sensitive path
**Date**: 2026-11-25
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure (the Supervisor writes the code, DDR-0011)
**Agent guide**: `agents/common-infrastructure.md`

> Read relevant files from `docs/legacy/` before making any code changes. (This repo has no `docs/legacy/`: `PROJECT_SPEC.md` and `docs/claude-md/` are the source of truth.)

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "T363 go with C [admin]". This chooses option C of the T363 Debate (3 Advocates, 2026-11-25). The board row, from the T316 review (P2), says the hook "matches tokens only, so a folder-level call (`rm -rf .claude`, `git checkout HEAD~1 -- .claude`, `git restore .`, `find .claude -delete`) or a shell-built name (`{a,b}` braces, `${f}itive-paths.txt`, `python3 -c …`) touches a sensitive path with no ask".

**Option C, restated**:
1. **Folder rule.** A Bash segment asks when both of these hold:
   - Its command is a destructive one: `rm` with `-r`/`-R`/`--recursive`, `find` with `-delete`/`-exec`/`-execdir`/`-ok`/`-okdir`, `mv`, or `git checkout`/`git restore`.
   - One of its arguments is an existing folder under the project root or the call's cwd that holds a sensitive path.

   A folder holds one when a bounded walk of it finds a file the list or the protected patterns mark sensitive. When the walk hits its cap, the folder counts as holding one (fail toward the human). `pytest .`, `ls .claude` and `cat .claude/x` never reach this rule, so they cost no new prompts. A folder outside both roots is skipped (`rm -rf ../wt-t364`), because every worktree holds `.claude/sensitive-paths.txt`.
2. **Braces.** A Bash token holding `{…,…}` is expanded with the hook's own `expand_braces`, and each expansion is checked as a path.
3. **Written down, not built.** `$VAR`/`${…}`-built names, `eval` and `python3 -c` code stay unresolved. They are recorded in the hook header's "Recorded limitations".

**Out of scope**: options A and B (not chosen); read-only commands that name a protected folder (T371); `git reset --hard`, `git clean`, `git stash`, `cp -r`, `rsync`, `tar` (C's verb list — a recorded limitation, see Cut list).

**Requirement Refs**: T363 Debate (Advocates 1–3, 2026-11-25), `tasks/TASK_REVIEW_T363.md` `## Auto decisions`; T146/T314/T316 (`.claude/hooks/pre_tool_sensitive_path.py` header).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — the user chose option C, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (sensitive path, protected pattern: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T316 (merged)
**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` (PreToolUse hook on `Edit|Write|Bash`) — a Bash call.

---

## Acceptance Criteria

1. `rm -rf .claude`, `rm -r .claude`, `find .claude -delete`, `find . -name x -exec rm {} +`, `mv .claude old`, `git checkout HEAD~1 -- .claude` and `git restore .` ask, run from the project root. So do `rm -rf secrets` and `rm -rf config` when the folder holds `config/.env`.
2. These stay silent: `ls .claude`, `cat .claude/x.md`, `python3 -m pytest .`, `grep -rn x .claude`, `rm -rf build` (no sensitive file inside), `rm notes.txt`, `git checkout main`, `git restore src/app.py`, and `rm -rf ../elsewhere` (outside both roots).
3. A brace token is expanded: `cp x .claude/{sensitive-paths.txt,y}` and `rm .{env,bak}` ask; `cp a.{txt,md} out` stays silent.
4. A walk that reaches its cap counts as holding a sensitive path (ask).
5. Every existing sensitive-path test passes unchanged, and the hook header's "Recorded limitations" names the still-open cases (variable-built names, `eval`, `python -c`, the verbs outside C's list).

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | each AC 1 command | ask, naming the folder | automated (`.claude/hooks/tests/test_t363_folder_level.py`) |
| 2 | each AC 2 command | silent | automated (same file) |
| 3 | brace tokens | ask / silent as AC 3 | automated (same file) |
| 4 | walk cap set to 1 | ask | automated (same file) |
| 5 | the existing sensitive-path tests | unchanged, pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py .claude/hooks/tests/test_t314_fix_round.py
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T363.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T363.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a PreToolUse hook.

---

## Approach

**Pattern reference**: the hook's own `changes_dir` / `STATE_PARENTS` rule in `sensitive_hits` (a parent folder asks only in a verb context), and `command_tokens` (heredoc bodies and data spans removed with `lib/shell_data.py` first).

**Vital slice**: `folder_hits(command, cwd, roots, patterns)`. It removes heredoc bodies and data spans as `command_tokens` does, then splits the rest on `SEGMENT_BOUNDARY_PATTERN`. For each segment it finds the command word, past `VAR=value`, `sudo`, `env`, `command` and a path prefix. When the command is destructive, it treats every non-option token as a path: if that path is an existing folder under a root, it walks the folder (skipping `.git`, capped) and returns the first sensitive file it finds. `sensitive_hits` adds those hits, so predictions, approvals and the ask text work as for any other hit. `command_tokens` also adds each token's `expand_braces` expansions.

**Cut list** (option C): no ask for the verbs outside the list (`git reset --hard`, `git clean`, `git stash`, `cp -r`, `rsync --delete`, `tar -x`, `ln -sf`, a script or alias); no resolution of `$VAR`, `${…}`, `eval` or `python -c` code; no read-only allowance (T371).

---

## Edge Case Checklist

- [x] The walk is bounded (`MAX_FOLDER_WALK` files) and a hit at the cap asks; `.git` is skipped
- [x] A folder outside both roots (a sibling worktree) is skipped
- [x] `rm` without `-r` on a folder: rm refuses it, no walk needed; a file argument is already checked by the token rule
- [x] `find` with no path argument acts on `.`
- [x] A destructive verb behind `sudo`, `env`, `command`, `VAR=` or a path (`/bin/rm`) is still found
- [x] The predicted-path exemption: a guide that predicts `.claude/sensitive-paths.txt` does not pre-authorise `rm -rf .claude` (the hit's path is the folder)
- [x] Pin-test pre-flight: `.claude/hooks/tests/test_pre_tool_sensitive_path.py`, `test_t316_list_self_protect.py` (`ls -la` silent), `test_t314_fix_round.py` (and `test_pre_tool_sensitive_path.py::test_directory_lookalikes_stay_silent`) — none pins the hook's line count or text
- [x] Stale references: the hook header's "Recorded limitations"; `docs/claude-md/` text on what the hook covers (grep `sensitive-paths` there)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | `folder_hits`, brace expansion in `command_tokens`, header limits |
| `.claude/hooks/tests/test_t363_folder_level.py` (new) | AC 1–4 |
| Pre-existing pin tests | listed above: unchanged, must pass |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/sensitive-paths.txt` | the list is unchanged |
| `.claude/hooks/lib/shell_data.py` | shared by the merge gate; option C needs no change there |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | not this task |

---

## Test Plan

Test first: the new file fails on `main`. Then the change, the Verification Command, and the full suite compared with the `main` baseline (60 failures).

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T363.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log
