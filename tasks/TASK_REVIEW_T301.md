# TASK_REVIEW — T[NNN]: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
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

## Auto decisions

Mode: auto
1. Put the rules in one reference file linked from the `security-reviewer` persona and Stage 4 step 2, not in a new skill; the built-in `security-review` stays — RULE: `tasks/TASK_GUIDE_T301.md` § Requirement (the user approved this proposal: "yes, let add it, [auto]")
2. Labelled the task C2 / Risk Medium and ran it on the extended track — RULE: `docs/claude-md/tracks.md` § Track rule
3. Spawned `common-infrastructure` on `sonnet` for a docs-and-tests task — RULE: `skills/craft-spawn-prompt/SKILL.md` § 5. Recommend spawn model (the `claude` C2 cell is `sonnet or opus`: pick per Risk)
4. Cut the coverage ledger, the six phases, the schema, the validators and the eight other attack-class files — RULE: `tasks/TASK_GUIDE_T301.md` § Approach (Cut list)
Checks: tests `python3 -m pytest tests/test_security_reviewer_rules.py .claude/hooks/tests/test_skill_reference_pointers.py tests/test_token_economy_docs.py tests/test_stale_reference_sweep.py -q -p no:cacheprovider` — `45 passed in 0.18s`; full suite `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — `8 failed, 4400 passed` (all 8 in the flaky `test_auto_verify*` files; the same files also fail on the parent commit `e7d3bcba`, so not caused by T301); reviews `code-review` — 0 P0, 0 P1, 2 P2 and 2 P3 fixed in `da278c8b`, `security-review` — no findings; real run `grep -n "security-reviewer.md" skills/code-review/SKILL.md docs/claude-md/pipeline-stages.md` — printed the persona row and the Stage 4 item 2 sentence (auto-checked, not /verify)
Memory: memory/learnings.md — The full suite fills `/tmp` and stops the Bash tool; `test_auto_verify*` is flaky (T301); memory/MEMORY.md — one index line for it
Not done: merge (yours); auto verify: ☑ pass (session 2f6560e9-1924-4573-b3de-b37b660ca587, commit e15a1d066bdea3e6a763f5c4f3a1c3a841125d2c, log .claude/verify-runs/T301-e15a1d066bde.log)
Paused: done not moved — Gate 6: the `UI: Visual regression` row is blank; Gate 6: the `UI: Design-system compliance` row is blank; Gate 6: the `UI: Responsiveness` row is blank

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_security_reviewer_rules.py` (AC1-7 and mutation controls); runs `pass` on `0429c2c7` |
| Verification command run | ☑ pass | `python3 -m pytest tests/test_security_reviewer_rules.py .claude/hooks/tests/test_skill_reference_pointers.py tests/test_token_economy_docs.py tests/test_stale_reference_sweep.py -q -p no:cacheprovider` printed `45 passed in 0.18s` (Supervisor run, branch `feat/t301-security-reviewer-rules` at `0429c2c7`, 2026-11-09). `grep` of the persona row and Stage 4 item 2 shows `security-reviewer.md` in both. |
| Negative cases hold | ☑ pass | Red run before the change: `17 failed, 3 passed in 0.73s` (implementer, new tests, 2026-11-09T05:33Z; pasted in `## Demonstration`). Mutation controls on real bytes, each with a non-empty `git diff --stat`: persona link typo → `4 failed, 27 passed`; `## Needs validation` renamed → `2 failed, 29 passed`; `needs_validation` replaced in the reference file → `2 failed, 29 passed`. The Stage 4 fix round (`da278c8b`) added a test for each new bullet and made the cap mutation control call `cap_problems`. |
| verify | ☑ pass | auto-run by hook, session 2f6560e9-1924-4573-b3de-b37b660ca587, commit e15a1d066bdea3e6a763f5c4f3a1c3a841125d2c, log .claude/verify-runs/T301-e15a1d066bde.log — pass; done not moved: Gate 6: the `UI: Visual regression` row is blank; Gate 6: the `UI: Design-system compliance` row is blank; Gate 6: the `UI: Responsiveness` row is blank |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 5 changed files (`security-reviewer.md`, `code-review/SKILL.md`, `pipeline-stages.md`, the new test, this file), the callers that read them (`test_skill_reference_pointers.py`, `test_token_economy_docs.py`, `test_stale_reference_sweep.py` cap test) and a stale-wording grep of the repo. `code-review`: 0 P0, 0 P1, 2 P2, 2 P3, all fixed in `da278c8b`. `security-review`: no findings. Skipped: the unrelated 1 MB diff of `main` against `github/main` that the built-in `security-review` loaded by default. |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | **Not green, and not caused by T301.** `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider --basetemp=<home volume>` on `0429c2c7` printed `8 failed, 4400 passed, 25 subtests passed in 629.84s`; all 8 are in `tests/test_auto_verify.py` and `.claude/hooks/tests/test_auto_verify_skip_pass.py`. Re-run of those two files alone on `0429c2c7`: `5 failed, 470 passed` (a different set). The same two files on T301's parent `e7d3bcba` (detached worktree, no T301 change): `2 failed, 473 passed` (another set). The failing set changes from run to run, so they are flaky; T301 edits no hook or script they run. The implementer's first full run also failed in `test_auto_verify.py::test_t203_ac3_off_still_runs_a_marked_task[stop]`. A flaky-test follow-up task is not registered. |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: the optional `score` companion was skipped in this auto run (no extra spend); the merge gate blocks on ☑ fail only, never on an N/A row. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: the change is rule text in `skills/` and `docs/`, one new test file and this report. No screen, page or style file changed. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component: no colors, type, spacing or tokens changed (`site/` and `*.css` untouched; `git diff main...HEAD --stat` lists only `skills/`, `docs/`, `tests/` and `tasks/` files). |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component: no layout or viewport behavior changed. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (verbatim prior content, captured 2026-11-09T05:33Z, before any implementation commit; `git status` showed only the untracked `tasks/TASK_REVIEW_T301.md` and `tests/test_security_reviewer_rules.py`):

`skills/code-review/SKILL.md` (8161 bytes) persona row, line 59:
```
| **security-reviewer** | Auth logic, input handling, secrets, permissions, SQL/shell |
```
Phase 2 steps 3-4, lines 110-111:
```
3. **Gate**: remove any P1–P3 finding with confidence < 75 after promotion. Keep P0 at ≥ 50.
4. **Assign model tier**: P0 and security findings → re-verify with top-tier model reasoning before surfacing. All others → mid-tier is sufficient.
```
Phase 3, lines 119-135:
```
Emit findings grouped by severity:

## P0 — Must Fix
| File | Line | Finding | Confidence | Action |
## P1 — Should Fix  (same table header)
## P2 — Recommended (same table header)
## P3 — Optional    (same table header)

If no findings in a severity group: emit "None."
```
(the code fence holds the four groups; no `## Needs validation` group exists.)

`docs/claude-md/pipeline-stages.md` Stage 4 item 2, lines 224-227:
```
2. **Security Review** (if task Risk Level is Medium or High):
   ```
   Skill({ skill: "security-review" })
   ```
```
`skills/code-review/references/security-reviewer.md` and `tests/test_security_reviewer_rules.py`: no prior content (new files).

Red run of the new tests before the change (`python3 -m pytest tests/test_security_reviewer_rules.py -q -p no:cacheprovider`): `17 failed, 3 passed in 0.73s`. The 3 passes are the guards that hold on prior content (the non-security gate text, the 8192-byte cap, and the cap mutation control); the 17 failures include `test_ac1_reference_exists_with_six_rules_and_the_limit` (FileNotFoundError, reference file absent), `test_ac4_persona_row_links_the_reference`, `test_ac5_phase_2_and_3_text` and `test_ac6_stage_4_item_2_names_the_file`.

**AFTER**: persona row now ends `Rules: [security-reviewer.md](references/security-reviewer.md)`; Phase 2 step 3 adds "A security lead that fails the gate stays as `needs_validation` (no severity)"; step 4 adds "by a verifier that did not find them"; Phase 3 has a `## Needs validation` group after P3; Stage 4 item 2 adds "The findings of `security-review` use the verdicts and rules in `skills/code-review/references/security-reviewer.md`."; the new reference file is 47 lines. `SKILL.md` is 8184 bytes (cap 8192). `python3 -m pytest tests/test_security_reviewer_rules.py .claude/hooks/tests/test_skill_reference_pointers.py tests/test_token_economy_docs.py tests/test_stale_reference_sweep.py -q -p no:cacheprovider` printed `41 passed`.

**DELTA**: A `security-reviewer` or `security-review` run now has one short rule file, and a security lead that cannot be proven yet is kept as `needs_validation` instead of being dropped.

**WITNESS**: Derived from `memory/event-trace/T301.jsonl` (71 records: 61 `Bash`, 6 `Read`, 2 `SubagentHandback`, 1 `Write`, 1 `Agent`), not from the implementer alone. The implementer (`common-infrastructure`, spawned 2026-11-09) ran the red and green tests; the Supervisor re-ran the focused tests (`45 passed`) and the full suite (`8 failed, 4400 passed`, flaky `test_auto_verify*`) on `0429c2c7`; the headless auto verify run (session `2f6560e9-1924-4573-b3de-b37b660ca587`, log `.claude/verify-runs/T301-e15a1d066bde.log`) printed `verdict: pass`.
