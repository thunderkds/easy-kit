# TASK_REVIEW — T305: Plugin hooks do nothing when setup.sh already wired the same hook

> Sibling of `tasks/TASK_GUIDE_T305.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_plugin_double_install.py` (AC1-6: 12 skip cases, 12 run-unchanged, 12 permission-only, 12 init-copy, per-script, name-prefix, unset dir, mutant, identical files). Red run before the change: `13 failed, 40 passed`. Green: `173 passed in 5.19s` for the 3 files of the Verification Command. |
| Verification command run | ☑ pass | 2026-11-10 10:54:21 UTC: pytest `173 passed in 5.19s` (scratch venv, system python has no pytest); `sh tests/test_update.sh` -> `38 passed, 0 failed`; `claude plugin validate .` -> `Validation passed with warnings` (same as BEFORE). |
| Negative cases hold | ☑ pass | Guard stripped from `hooks/hooks.json` by sed (`git diff --stat`: `hooks/hooks.json 24 ++++----`): `14 failed, 39 passed` (12 AC1 cases, per-script, identical-files). File restored. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | 2026-11-10 Stage 4 `code-review`: scope = `hooks/hooks.json`, `plugin/hooks/hooks.json`, `tests/test_plugin_double_install.py`, `README.md` plus their pin tests (`test_plugin_package.py`, `test_plugin_source.py`, `test_directory_prep.py`, `test_companion_setup.py`, `test_runbook_plugin_check.py`). Result: P0 0, P1 0. P3: the in-file mutant test runs a hand-written unguarded string, so it proves the test can see a missing guard, not that the real guard is present (the agent's sed mutant covers that, 14 failed). P3: the guide's `Pre-existing pin tests` row was left as the template text. Lane check: `C2, 5 files, 375 lines, FITS; unpredicted: tasks/TASK_GUIDE_T305.md` (the guide itself). Startup reads: the three Permanent-Rule reads are on the agent's line. `security-review`: no finding at confidence 8 or above (quoting holds, `grep -F`, both variables double-quoted, fails toward running the gate). Re-run by the Supervisor in a scratch venv: `238 passed` (plugin, directory, companion and runbook tests) and `sh tests/test_update.sh` 38 passed. Real-harness check with `claude` 2.1.322 and a throwaway plugin (`--plugin-dir`): project that wires the hook the `setup.sh` way -> only `project` ran, once; plain project -> only `plugin` ran, once. |
| Full smoke suite still green (no regression) | ☑ pass | `pytest tests/ .claude/hooks/tests -q`: `2 failed, 6967 passed, 6 skipped`; the 2 failures are `test_heredoc_quoted_marker.py ... d-busybox-ash-bash/zsh` and fail the same on a clean stash (busybox-ash not installed). One README cap test (`test_companion_setup.py`, 75 lines) caught a 2-line README edit; the README line was merged into an existing line. |
| **Companion score (easy-verifier)** | ☑ N/A | `score` skill not run: easy-verifier is optional and was not started for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: hook command strings, a test and one README line. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-10 10:53:28 UTC, before any implementation commit; pytest from a scratch venv because the system python has no pytest):

```
$ python3 -m pytest tests/test_plugin_package.py tests/test_hooks_from_plugin.py tests/test_plugin_double_install.py -q
ERROR: file or directory not found: tests/test_plugin_double_install.py
no tests ran in 0.00s
$ sh tests/test_update.sh | tail -2
----- summary: 38 passed, 0 failed -----
$ claude plugin validate . | tail -2
✔ Validation passed with warnings
```

Current command of the Stop hook `stop_auto_verify.py` in `hooks/hooks.json` (no guard, so it runs even when `.claude/settings.json` already wires it):

```
python3 "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/stop_auto_verify.py"
```

**AFTER** (2026-11-10 10:54:21 UTC):

```
$ python3 -m pytest tests/test_plugin_package.py tests/test_hooks_from_plugin.py tests/test_plugin_double_install.py -q
173 passed in 5.19s
$ sh tests/test_update.sh | tail -2
----- summary: 38 passed, 0 failed -----
$ claude plugin validate . | tail -2
✔ Validation passed with warnings
```

Stop hook command now:

```
grep -qsF '$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop_auto_verify.py' "$CLAUDE_PROJECT_DIR/.claude/settings.json" || python3 "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/stop_auto_verify.py"
```

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
