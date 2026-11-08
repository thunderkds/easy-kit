# TASK_REVIEW — T289: Docs-only and tests-only tasks get a real pass verdict from the auto verify run

> Sibling of `tasks/TASK_GUIDE_T289.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_auto_verify_skip_pass.py` (163 tests, AC 1-7). Red first against the unchanged code: `126 failed, 29 passed` (the 29 are negative cases that already ended `blocked`; the mutation controls below show they can fail). Green after: `163 passed`. Repointed pins: `tests/test_auto_verify.py` (T208 `skip-word` parse case), `.claude/hooks/tests/test_admin_tag.py` (3 tracks.md / AGENTS.md text pins), `.claude/hooks/tests/test_merge_gate_guard.py` + `merge_gate_guard.py` (allowlist gains T289), `.claude/hooks/tests/test_agent_guide_dedup.py` (AGENTS.md ref `c566b2b6` -> `83ac3e7a`), `tests/test_claude_md_slim.py` (cap 21732 -> 21724) |
| Verification command run | ☑ pass | `python3 -B -m pytest .claude/hooks/tests -q -k "verify or admin or merge" -p no:cacheprovider` -> `892 passed, 1171 deselected in 28.07s`; `python3 -B -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4022 passed, 25 subtests passed in 257.66s` |
| Negative cases hold | ☑ pass | Mutation controls, each a byte-changing edit (`git diff --stat` non-empty), run against the new test file, then restored (`git checkout`): M1 `docs_only_path` returns True first -> 84 failed (`-k "ac2 or ac3 or ac5"`); M2a empty/None diff accepted (`return (bases[0], paths)`) -> 16 failed in the `ac5` subset; M2b unreadable range returns a fake pass -> 4 failed (missing base ref, unreadable checkout, unusable tip x2); M3 a FAIL answer settled like a SKIP (`if verdict in ("skip", "fail")`) -> 1 failed (`test_ac4_a_fail_answer_on_a_docs_only_branch_is_never_a_pass`); M4 gate accepts a skip-pass with no path check (`return True`) -> 4 failed (`test_ac3_the_gate_rechecks_the_paths_...`); M5 symlink/gitlink modes accepted -> 5 failed; M6 unsafe file names accepted -> 10 failed; M7 hook trusts the SKIP without asking git -> 26 failed; M8 `docs/claude-md` not excepted -> 7 failed. Every restore left `git status` clean. Full red output for M1-M8 is in the Supervisor's session transcript (this agent's tool results) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | Left for the Supervisor's Stage 4. Blast radius: `.claude/hooks/lib/verify_record.py` (writer and reader of the run record), `stop_auto_verify.py`, `pre_bash_block_unsafe_merge.py` `_auto_row_confirmed_at`, `lib/auto_closeout.py` `record_gaps` (one line), their tests, `docs/claude-md/tracks.md`, `AGENTS.md`, `PROJECT_SPEC.md` glossary, `site/docs.html` |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -B -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4022 passed, 25 subtests passed in 257.66s (0:04:17)` on commit `T289: lower the AGENTS.md byte cap` (no known failure appeared) |
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

**BEFORE** (captured 2026-11-08T06:39:03+00:00, on branch `feat/t289-docs-only-pass` at `4b8edf8e`, before any implementation commit). Command: `python3 -B <scratchpad>/demo_skip.py /home/hungnguyenhuu/workspace/pets/wt-t289` (builds a temp git project whose task branch changes only a review file, as T283 and T286 did, stubs the headless `claude` to answer `**Verdict:** SKIP`, runs the real `stop_auto_verify.py` Stop hook, prints the `verify` row the hook wrote):
```
date: 2026-11-08T06:39:03+00:00
changed paths: ['tasks/TASK_REVIEW_T951.md']
verify row result: ☐ blocked
verify row notes : auto-run by hook, session bb6500c2-6ee9-4ce9-bc0e-ea2f246f2fd4, commit <head>, log .claude/verify-runs/T951-4b07ca005e52.log — blocked (no single verdict line)
```
The docs-only branch gets `☐ blocked`, so `[admin]` cannot merge it (the same outcome T283 and T286 showed in their `verify` rows before the user typed `/verify`).

**AFTER** (2026-11-08T07:07:09+00:00, same script, commit `83ac3e7a` plus the cap commit):
```
--- docs-only branch (changed paths: ['tasks/TASK_REVIEW_T951.md'])
verify row result: ☑ pass
verify row notes : auto-run by hook, session bb6500c2-6ee9-4ce9-bc0e-ea2f246f2fd4, commit <head>, log .claude/verify-runs/T951-a64827d40e74.log, skip (no runtime surface: tasks/TASK_REVIEW_T951.md) — pass
--- same answer (SKIP), branch also changes src/app.py (changed paths: ['src/app.py', 'tasks/TASK_REVIEW_T951.md'])
verify row result: ☐ blocked
verify row notes : auto-run by hook, session bb6500c2-6ee9-4ce9-bc0e-ea2f246f2fd4, commit <head>, log .claude/verify-runs/T951-f285b2afc242.log — blocked (SKIP, and git does not show a change of docs-only files)
```
Real data check (read-only, `_raw_diff` between the recorded base and the verified commit): T286 `396afdd5` -> `['tasks/TASK_REVIEW_T286.md', 'tests/test_claude_md_slim.py']`; T283 `880e93b7` -> `['tasks/SPIKE_REPORT_T283.md', 'tasks/TASK_REVIEW_T283.md']`. Both would now be a skip-pass.

**DELTA**: With `[admin]`, a task that changes only docs, task files, memory or tests is merged and pushed after the headless auto verify run alone, with no `/verify` typed by the user.

**WITNESS**: [left for the Supervisor: derive from `memory/event-trace/T289.jsonl`; the BEFORE and AFTER above were run by the implementing agent alone]

---

## Stage 4 self-review (implementing agent; the Supervisor runs `code-review` and `security-review` separately)

- Path rule: one literal tuple (`DOCS_ONLY_PREFIXES`, `DOCS_ONLY_EXCEPT`, `ROOT_MD_EXCEPT`) in `.claude/hooks/lib/verify_record.py`; names must match `[A-Za-z0-9._/-]`, no `.`/`..` part, 200 bytes at most; exceptions compared in lower case (case-folding file systems); `git diff --raw -z --no-renames --ignore-submodules=none`, statuses A/M/D only, modes 100644/100755 only (a symlink or gitlink is never docs-only); exactly one merge-base of `refs/heads/main` and the tip; empty diff is `None`.
- **Deliberate narrowing beyond the guide** (AC 2 says "root `*.md` except `AGENTS.md` and `CLAUDE.md`"): `CLAUDE_LEGACY.md` (brownfield twin of `CLAUDE.md`), `PROJECT_KANBAN.md` and `PROJECT_SPEC.md` (the hooks read both as control state) are also out. Remove from `ROOT_MD_EXCEPT` if the Supervisor disagrees.
- Gate: `record_confirms_pass` (used by `auto_row_confirmed` and `_auto_row_confirmed_at`) accepts `pass`, or `skip-pass` only if the record carries a full-hash `base` that is an ancestor of the record's commit and of `refs/heads/main`, and `_raw_diff(base, commit)` is non-empty and all docs-only. `base` is stored in the record (not recomputed from `main`) because after the admin merge `main` contains the branch, and `main...tip` would be empty.
- Close-out: `auto_closeout.record_gaps` accepts `skip-pass` (one line); the gate's own rule (`has_filled_verify_row`) still decides. Not in the guide's Files to Change; flagged for the Supervisor.
- `merge_gate_guard.AUTHORISED_TASKS` gains `T289` (the tripwire says the Supervisor signs this off).
- Stale-text grep (LR-0005) for `skip` + verify wording: fixed `docs/claude-md/tracks.md` (3 places), `AGENTS.md`, `PROJECT_SPEC.md` glossary, `.claude/hooks/stop_auto_verify.py` docstring; added one sentence to `site/docs.html`. `README.md` says only "after its auto verify passes": true still, unchanged. Not mine to edit and still stale: `memory/learnings.md` entry "A docs-only task gets SKIP from auto verify, written as `blocked` (T283)", `memory/decisions.md` T283-T288 status line; `tasks/TASK_GUIDE_T250.md` "SKIP stays `blocked`" is history.
- Open: `memory/**` and `tasks/TASK_GUIDE_*.md` are in the list as the guide says, but `memory/MEMORY.md` is injected into agent prompts and guides steer agents; a docs-only branch can change them. Consider excluding `memory/MEMORY.md` and `tasks/TASK_GUIDE_*.md` (one tuple edit plus one test).
