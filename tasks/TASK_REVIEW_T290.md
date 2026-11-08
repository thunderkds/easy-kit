# TASK_REVIEW — T290: Locked oracle: a task guide can lock its oracle test while the task runs

> Sibling of `tasks/TASK_GUIDE_T290.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` or `[admin]` tag; with `[admin]`, the `Not done:` line names `merge (admin: after the auto verify pass)`,
`docs/claude-md/tracks.md` `## Auto mode`). To use it, copy the block below out of this comment, to this
place, and replace every <...>. Keep `Mode: auto` as its first line, exactly as written: T182's hook reads
it. Write it to this file before the run ends; the chat message is a copy, not the report. The same
block is the Supervisor's final chat message. It is not the `delivery-report` page and not
Evidence. A taste decision (what the user wants) also ends with the flag. Write `DEBATED` only when ≥2
Advocate `Agent` calls ran for that question, naming each Advocate's option. A decision with no Advocates is
labelled `RULE`, `FACT` or `SAFER OPTION`, never `DEBATED`. A decision flagged `⚠ decided for you` is a choice, and is never labelled `FACT`. A
safety action a rule requires (for example the backup before a delete) is `RULE` without the flag.
At Risk Medium or High, a `RULE:` counts only when it names a written rule (`path:line`,
`path § <heading>`, or `docs/claude-md/tracks.md` `### <section>`), and a `FACT:` needs a Citation
(`path:line "quoted text"`); without one it is a choice and must be `DEBATED`. Good: `2. backed up the CSV
— RULE: `docs/claude-md/tracks.md` `### Stops that stay``. Bad: `1. kept recurring.csv — RULE: Surgical Changes`.
`Memory:` records the diff-driven memory pass you run before you stop: each entry written, or `nothing new`.
After an auto verify pass the hook, never you, adds `Closed: row moved to Done <date> — …` and moves the row,
or adds `Paused: done not moved — <reason>`. It moves the row only when this block holds `Mode: auto`, a
numbered decision, `Checks:`, `Memory:`, the `Not done:` auto verify slot with its result, and `Not done:`
naming the merge — no `<...>` left (`docs/claude-md/tracks.md` `### Auto close-out`).

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours)>

-->

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T06:42Z, worktree `wt-t290`, branch `feat/t290-locked-oracle`, before any implementation commit; the only change on disk is the untracked red test file):

```
$ ls .claude/hooks/pre_tool_locked_oracle.py
ls: cannot access '.../.claude/hooks/pre_tool_locked_oracle.py': No such file or directory
$ grep -n '^\*\*Locked oracle' <fixture>/tasks/TASK_GUIDE_T066.md     # real T066 guide + lock line, board row T066 In Progress
240:**Locked oracle**: `.claude/hooks/tests/test_agent_guide_dedup.py`
# T082-style Edit ("assert a < b" -> "assert a <= b") by agent_type common-infrastructure, piped to each existing PreToolUse hook that matches Edit
--- pre_tool_sensitive_path.py   exit=0, stdout empty  (no deny: the Edit goes through)
--- pre_agent_step_limit.py      exit=0, stdout empty  (no deny: the Edit goes through)
--- pre_tool_locked_oracle.py    python3: can't open file ... [Errno 2] No such file or directory
$ python3 -B -m pytest .claude/hooks/tests/test_locked_oracle.py -q -p no:cacheprovider
67 failed, 1 passed in 1.36s        # (the 1 pass is the guard "implementer guides do not mention the lock", true on the prior content)
```
Script: scratchpad `before_replay.sh` (fixture built in a temp dir; no repo file touched).

**AFTER** (2026-11-08T06:55Z, same fixture and event, hook present, not yet wired in settings.json): the new hook denies the T082-style Edit.
```
--- the new hook, as a test would call it:
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "[hook:locked-oracle] .claude/hooks/tests/test_agent_guide_dedup.py is the Locked oracle of tasks/TASK_GUIDE_T066.md while T066 is In Progress; agent 'common-infrastructure' may not edit it. Stop and report to the Supervisor. ..."}}
exit=0
$ python3 -B -m pytest .claude/hooks/tests/test_locked_oracle.py -q -p no:cacheprovider
68 passed
```

**DELTA**: A task guide can name its oracle test on a `**Locked oracle**:` line, and while the task is In Progress a sub-agent other than `qa-expert` can no longer edit that file (the T082 `<` to `<=` weakening is denied), yet the lock ends when the row leaves In Progress.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T290.jsonl`, never the
implementing agent alone]

---

## Stage 4 self-review (implementer, common-infrastructure; the Supervisor runs code-review and security-review separately)

**Scope**: `.claude/hooks/pre_tool_locked_oracle.py` (new, 222 lines), `.claude/hooks/tests/test_locked_oracle.py` (new, 80 tests after the review fixes), `plugin/.claude/hooks/pre_tool_locked_oracle.py` (symlink; `tests/test_plugin_source.py:73` requires one per hook), `templates/TASK_GUIDE_template.md` (one sentence, appended to an existing line: `test_vital_slice.py` caps the template at 205 lines), `docs/claude-md/pipeline-stages.md` (one line in Stage 2). `AGENTS.md` unchanged (21732 bytes). `.claude/settings.json`, `hooks/hooks.json`, `plugin/hooks/hooks.json`, `PROJECT_KANBAN.md`, `memory/**` untouched.

**Design choices that go past the spike** (each has a test): path identity by real path with case folded; a path inside any git worktree of the repo compares by its path in that checkout (the T082 incident happened through a worktree path); a session inside a linked worktree reads the guides and board of the main checkout (the row moves there); fail closed on a missing `agent_type`, bad stdin, an edit with no path, an unreadable guide or board, a lock line in a guide with no task ID, a lib import failure (denies bound callers only).

**Mutation controls** (byte-changing, `git diff --stat` non-empty before each verdict, restored afterwards; output in scratchpad `mutate_out.txt`):

| # | Mutation | Result |
|---|----------|--------|
| M1 | lookup never denies (`for ... in locks` -> `in []`) | 34 failed (AC1, AC7, edge, worktree) |
| M2 | row-status check always In Progress (`if True:`) | 10 failed (AC3 x6, edge) |
| M3 | main thread counted as bound | 5 failed (AC2 main, AC7, AC4 x3) |
| M4 | `easy-kit:qa-expert` dropped from JUDGES | 1 failed |
| M5 | `realpath` -> `abspath` | 1 failed (symlink alias) |
| M6 | bad stdin no longer denied | 13 failed |
| M7 | worktree not recognised as same repo | 2 failed |
| M8 | worktree session reads its own board | 1 failed |
| M9 | case folding removed | 1 failed |
| M10 | missing agent_type counted as judge | 3 failed |
| M11 | `Locked oracle` appended to `agents/qa.md` | 1 failed (AC5) |
| M12 | template line made live | 1 failed (AC5) |

**Known limits** (stated, not fixed): `Bash` writes (`sed -i`, `>`) are not parsed; a hard link to the oracle is a different path; a sub-agent can edit the guide (drop the lock line) or the board row, so the lock stops accidents, not an adversary; the plugin copy is not wired until the Supervisor adds the `hooks/hooks.json` entry.

**Pin-test pre-flight** (LR-0004): full suite with this diff, 3927 passed, 0 failed (baseline on `main` before the change: no failures). Wiring the hook later makes 5 pin tests fail until companion edits land (found by applying the wiring to a throwaway copy): `tests/test_plugin_package.py::test_plugin_hooks_equal_settings_hooks` (`len(settings) == 11`; also needs `hooks/hooks.json` and `plugin/hooks/hooks.json` entries), `tests/test_subagent_sandbox_profile.py::test_sc5_supervisor_settings_have_no_permissions_or_sandbox` (names every changed settings line), `tests/test_site_content.py` x3 (`test_every_wired_hook_appears_in_hook_table`, `test_quick_reference_counts_match_source`, `test_quick_reference_strip_has_four_cells_whose_numbers_match_source`: `site/docs.html` needs a hook-table row, and `5 blocking hooks (of 11)` becomes `6 ... (of 12)` in `docs.html` and the `index.html` hero strip, which also moves `tests/test_site_visual_first.py` and `tests/test_site_story.py` hash baselines; the page must not say "In Progress").

### Stage 4 review round 1 (Supervisor code-review + security-review: no P0, no P1) and what was done

| Finding | Action |
|---|---|
| P2-1: a bound sub-agent can remove the lock line, move the row, create a guide or edit the hook | Stated in the hook docstring and in one clause ("It stops accidents, not an adversary") in the template sentence and the `pipeline-stages.md` line. Behaviour unchanged on purpose (implementers tick guide checklists). Test: `test_the_hook_docstring_states_the_adversary_limit_and_the_format`, `test_the_template_and_doctrine_say_the_hook_must_be_wired_and_state_the_limit` |
| P2-2: template and doctrine said the hook denies, but it is not wired yet | Both now say "Once the hook is wired in `.claude/settings.json`"; template still 205 lines (same line extended) |
| P2-3: accepted format undocumented | Documented in the docstring and template (`**Locked oracle**:` at line start, exact paths, backticked or bare, comma-separated, no glob, directory or `:line`). Pinned by `test_format_*`: `**Locked oracle:**`, no bold, indented, quoted, lowercase, a lowercase task ID in the guide name, `:12`, a directory and a glob each lock nothing |
| P3-9: two survivors | New `test_edge_lock_entry_that_is_a_symlink_locks_its_target`; `test_ac4_lock_line_with_no_id_in_the_file_name_is_in_force` now asserts the reason text (`Locked oracle of tasks/TASK_GUIDE_NOTES.md while its task is In Progress`, not `unreadable`) |
| P3-11: ruff | E741 (`l`, two places) and 3 lines over 120 columns fixed; `ruff check --line-length 120` clean on the hook and the test |
| P3 4-8, 10, 12 | Not done; recorded below |

**Mutation controls added in round 1** (`git diff --stat` non-empty, restored, 80 passed after; output `mutate2_out.txt` in the scratchpad):

| # | Mutation | Result |
|---|----------|--------|
| M13 | `realpath` -> `abspath` in `lock_table` (lock entry that is a symlink) | 1 failed: `test_edge_lock_entry_that_is_a_symlink_locks_its_target` |
| M14 | a guide with no task ID raises (denied by the generic error path) instead of by the lock | 1 failed: `test_ac4_lock_line_with_no_id_in_the_file_name_is_in_force` (reason text) |
| M15 | lock-line regex accepts `**Locked oracle:**` | 1 failed: `test_format_malformed_lock_line_locks_nothing[colon-in-bold]` |

**Known limits, not fixed (P3 4-8, 10, 12, one line each; the reviewer's numbering, the wording is the implementer's reading of each)**:
- P3-4: a lock covers only the exact file; a rename or copy of the oracle is a new path.
- P3-5: `Bash` writes (`sed -i`, `>`) and a hard link are not covered.
- P3-6: a sub-agent can edit the guide, the board row, or this hook (see P2-1).
- P3-7: an unreadable guide or board denies every non-judge sub-agent edit until it is readable (fail closed).
- P3-8: the plugin copy and `.claude/settings.json` are not wired until the user approves the entries.
- P3-10: the hook reads every `tasks/TASK_GUIDE_*.md` on each bound edit (about 30 ms at 235 guides).
- P3-12: the lowercase task ID in a guide name matches no board row, so that guide locks nothing.
