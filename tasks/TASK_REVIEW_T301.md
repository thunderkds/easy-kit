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
Paused: `/tmp` (a 16 GB tmpfs with 1,048,576 inodes) is full again, with 0 free inodes, so Bash and the full test suite fail with ENOSPC. The full suite writes about 10 GB and very many small files into `/tmp`; the Supervisor's last full run (`--basetemp` on the home volume) still hit `OSError: [Errno 28] No space left on device: '/tmp/tmp...'`, so it is not a valid result and no full-suite line is recorded. Deleting files to make room needs the user's go-ahead, so the Supervisor deleted nothing. Stage 4 is done on the change as committed (`da278c8b`): `code-review` found 0 P0, 0 P1, two P2 (any failing security lead stayed `needs_validation`; a vacuous cap mutation control) and two P3 (`needs_validation` never blocks a merge; `rejected` undefined), and the implementer fixed all four; `security-review` found nothing (docs, rule text and one read-only test file). The focused tests pass (`45 passed`: `tests/test_security_reviewer_rules.py`, `test_skill_reference_pointers.py`, `tests/test_token_economy_docs.py`, `tests/test_stale_reference_sweep.py`). Not run: a valid full suite, the auto verify run, the final memory pass.
Memory: nothing new yet (interim; the diff-driven pass runs again before the final stop)

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

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
