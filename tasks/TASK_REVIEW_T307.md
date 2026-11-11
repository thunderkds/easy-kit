# TASK_REVIEW — T307: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T307.md`. Everything here is **filled by the reviewer at Stage
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
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_t307_admin_end_to_end.py` (locked oracle, qa-expert, commit d63ef09; AC 1–8, frozen-text SHA-256 pins, mutation controls; not edited: `git diff d63ef09..HEAD -- tests/test_t307_admin_end_to_end.py \| wc -l` → `0`). Repointed pins: `.claude/hooks/tests/test_admin_tag.py::test_ac8_ship_is_a_plan_only_under_admin` (was `…ship_stays_the_users_under_admin`), `tests/test_stage_names.py` row 19 (`T307_ROW19_ADD`), `.claude/hooks/tests/test_agent_guide_dedup.py` `T070_BASELINE_REF = "3212718d"`. Output: `87 passed in 4.14s` |
| Verification command run | ☑ pass | `…/scratchpad/venv/bin/python -m pytest tests/test_t307_admin_end_to_end.py -q -p no:cacheprovider` → `........................................................................ [ 82%]` / `...............                                                          [100%]` / `87 passed in 4.14s` |
| Negative cases hold | ☑ pass | Red run against the prior content, at `d63ef09` before any implementation commit (2026-11-11): `64 failed, 23 passed in 0.42s` (last lines: `FAILED tests/test_t307_admin_end_to_end.py::test_mutation_control_skill_pointer_removed[settings-setup]`, `…[to-issues]`). The oracle's mutation controls (each anchor cut, `first two` put back, `### Stops that stay` one byte changed, rows 1–4 changed, `[auto]` list and row 19 changed, cap +8192 bytes) all pass, so each pin goes red on its mutation. Repointed admin pin on the prior `tracks.md` (`git show d63ef09:docs/claude-md/tracks.md`): `base d63ef09: FAIL (red, as expected)` / `now: pass`. Diff (`git diff --stat d63ef09..HEAD`): `14 files changed, 169 insertions(+), 29 deletions(-)` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | `…/scratchpad/venv/bin/python -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` on a clean tree at `152c790` (all T307 code and doc commits in): `FAILED .claude/hooks/tests/test_heredoc_quoted_marker.py::test_round4_premise_the_shell_runs_the_push_and_the_scanner_keeps_it[d-busybox-ash-bash]` / `FAILED …[d-busybox-ash-zsh]` / `2 failed, 7087 passed, 6 skipped, 25 subtests passed in 404.20s (0:06:44)`. The 2 failures are the known busybox-missing pair on this machine. An earlier run also failed `tests/test_claude_md_slim.py::test_agents_md_is_at_most_21724_bytes` (AGENTS.md 21746 bytes: fixed in `3212718`, clause now 26 bytes like the old one) and, once, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository` and `test_auto_verify.py::test_t203_ac2_start_twice_on_one_commit_runs_once` (files were being edited in the worktree during that run; both pass alone and in the clean rerun) |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: docs and skill text. The one `site/docs.html` change replaces one sentence of prose inside an existing `<p>` (no markup, class or layout change); `tests/test_site_content.py` passes |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Same: no style, token or markup change |
| **UI: Responsiveness at target viewports** | ☑ N/A | Same: no layout change |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: verbatim prior content, captured 2026-11-11T12:23:46Z at `d63ef09` (the oracle commit; no
implementation commit yet). Oracle run at that commit: `64 failed, 23 passed` (qa-expert, commit d63ef09).

`docs/claude-md/tracks.md` `### Admin tag` (the two paragraphs this task changes):

> The tag adds one thing: the Supervisor may merge the task branch and push it, after the auto verify run
> passed. The merge gate, `.claude/hooks/pre_bash_block_unsafe_merge.py`, reads the tag at the time of the
> command, from this session's transcript. It allows a `git merge` or `git push` only when all of these hold:

> The gate's other checks then still run, as for every merge. `ship` stays the user's with `[admin]` too.
> With `[auto]` alone, the same gate blocks every merge, push and pull while that request is the latest
> one. A `git rebase` is not part of this rule. A session with no readable transcript has no known request,
> so this rule does not apply and the gate works as before.

(No `### Admin tag` text names Stage 0, `## Readiness`, `docs/legacy/`, the self-given approvals or the
hand-backs.)

`### Every user stop and its auto rule` row 19:

> | 19 | Stage 5 items 3–6: memory update, merge, Done, `ship` | Memory update: the Supervisor runs the diff-driven pass before it stops, and writes the `Memory:` line. Done: after an auto verify pass, the hook moves the row (`### Auto close-out`). Merge, push and `ship`: never in auto mode, except the merge and push that `[admin]` allows (`### Admin tag`). The task waits in Ready for Review until the hook moves it. | `Memory:` / `Closed:` / `Not done:` |

`### Never in auto mode`:

> With `[auto]`, these stay the user's:
>
> - merge;
> - pull;
> - push;
> - `ship`.
>
> With `[admin]`, the Supervisor may also do the first two, only as `### Admin tag` says. `ship` stays the
> user's with both tags. The memory pass and the move to Done are automatic: see `### Final report`
> (`Memory:`) and `### Auto close-out`.

`AGENTS.md` `## Tracks` (the clause):

> The tag `[admin]` runs the same auto mode and also lets the Supervisor merge and push the task's own branch, then push `main` after that merge, only after its auto verify run passed (`### Admin tag`): the Supervisor starts that run itself, waits, and on `blocked` or `fail` merges nothing; `ship` stays the user's.

Skill stop text (no `[admin]` pointer in any of them):

> `skills/grill-with-docs/SKILL.md:47`: If the decision **also clears all three ADR criteria**, flag it **ADR-eligible** and ask the user whether to escalate to a full ADR (`templates/ADR_template.md`, `docs/adr/NNNN-title.md`) instead — a DDR is **never silently auto-upgraded** to an ADR.
>
> `skills/grill-with-docs/SKILL.md:29`: - Notify: "Requirement grilling complete. N FRs validated, M open questions resolved, K items flagged for user. PRD gate: PASS / FAIL."
>
> `skills/brainstorming/SKILL.md:64`: - **To Supervisor**: Report when the `BRAINSTORMING_LOG.md` is ready for user review. Do not advance until the user has selected a "Path."
>
> `skills/to-issues/SKILL.md:13`: - **Ask vs. Guess**: Quiz the user on granularity and dependencies until they approve before generating guides.
>
> `skills/craft-agent/SKILL.md:28`: - If the requirement only needs base-team roles, report "no supplemental role needed" and stop — do not force a draft. The Supervisor then asks nothing in the Agent team step of Stage 1 and goes on with the base team; it asks the user to approve the team only when this skill proposes a role.
>
> `skills/settings-setup/SKILL.md:98-102`: ### Auto mode (`[auto]`/`[admin]`) / Ask no question. Run only Step 1 and the dry run of `high-security`. Write nothing. In the final report, under `Not done:`, put: `settings-setup: recommend high-security (dry run below), not written — yours to approve`, then the dry-run lines.

`skills/resolve-question/SKILL.md` (8183 bytes; no `docs/legacy/`, no `[admin]` Citation order):

> `:10-11`: The user talks only to you: every HITL message goes through your chat.
>
> `:97-98`: The HITL message carries the question, each Scanner's finding, and the decision needed. Never answer from memory in its place.

`site/docs.html:466` (stale reference found by the Edge Case grep):

> A force push or a push of any other branch stays blocked, and <code>ship</code> stays with you.

**AFTER**: verbatim new content (commits `cd71296`, `61c0943`, `3212718`, then the pin/site commit).

`docs/claude-md/tracks.md` `### Admin tag` (new, before the merge rules; the lead-in "The tag adds one thing:" became "**Merge and push.** The Supervisor may merge …", and the sentence "`ship` stays the user's with `[admin]` too." was removed):

> **The whole pipeline (T307).** With `[admin]`, one request runs the task from Stage 0 to Stage 5 with no question to you, except at project start. The Supervisor makes every decision and gives every approval itself. Plain `[auto]` is unchanged: rows 1–4, row 19 and `### Never in auto mode` read as before for it.
>
> Project start: under `[admin]`, Stage 0 step Requirements asks you its questions only on a new project. A new project is one whose `PROJECT_SPEC.md` `## Readiness` has no `Approved by: user <date>` line and no filled `Waived:` line (`user YYYY-MM-DD — reason`); an empty line or a placeholder counts as not filled. A project with either line filled counts as approved: no question goes to you, and rows 1–4 of `### Every user stop and its auto rule` run on their auto rules. The Supervisor reads this from `## Readiness` only, and never guesses it. The Supervisor never writes `Approved by` itself, with either tag: on a new project the line waits for your explicit confirmation of the Project Context Document.
>
> Domain first: the Supervisor decides from the business domain of the project. Under `[admin]`, a decision cites `PRD.md`, the `PROJECT_SPEC.md` glossary and `docs/legacy/` (when that folder exists) first, before code and the kit's own docs (`skills/resolve-question/SKILL.md`). Only when they do not settle the question does it go on to code, the rows of `### Every user stop and its auto rule` and a Debate.
>
> Decisions and approvals the Supervisor gives itself under `[admin]`: rows 2–4, 7–13, 15, 17 and 21 of `### Every user stop and its auto rule`, the Requirement Fidelity Gate, the agent team, the task breakdown, the direction, a `tdd` plan and the fix choice of a finding. Each one is made by its row's auto rule and `### Debate size by Risk`, and logged `RULE`, `FACT`, `SAFER OPTION` or `DEBATED` in the final report.
>
> The Supervisor never ends such a decision with "your decision" or "please approve": it decides, logs the line and goes on. A skill's own "ask the user" text yields to the row named in its `[admin]` pointer.
>
> Stops: the Supervisor stops only for the `### Stops that stay` list, and it says so in one line after the track line: `[admin]: I stop only for the stops that stay`. The only hand-backs left under `[admin]` are the `### Stops that stay` list, `Approved by` on a new project, the settings changes of row 5, a `git pull`, and the second `blocked` verify (T306).
>
> `ship`: after the merge and the push of `main`, the Supervisor runs `Skill({ skill: "ship" })` and writes its plan, as a plan only. It never runs a deploy command, and never tags or publishes a release: `ship` is a planner, not a deployer. It runs `ship` only for a task in Done (Hard-Stop Gate 5); when the hook left `Paused: done not moved`, it skips `ship` and says why. A missing `Deployment target` gives `TODO: confirm with operator` in the plan (`ship`'s own rule): that is not a stop.

Row 19 gains one sentence after T284's clause: "With `[admin]`, the Supervisor also runs `ship` after the merge, as a plan only, never a deploy." (`### Stops that stay`, rows 1–4 and the `[auto]` list: byte-identical, pinned by SHA-256.)

`### Never in auto mode` `[admin]` paragraph:

> With `[admin]`, the Supervisor may also merge and push, only as `### Admin tag` says; a pull stays the user's. With `[admin]`, it also runs `ship`, as a plan only, never a deploy. The memory pass and the move to Done are automatic: see `### Final report` (`Memory:`) and `### Auto close-out`.

`AGENTS.md` `## Tracks`: "… and on `blocked` or `fail` merges nothing; `ship` runs (plan only)." (26 bytes, the length of the old clause, so the 21724-byte cap of `tests/test_claude_md_slim.py` holds)

Skill pointers (one each): `grill-with-docs` "Under `[admin]`, flag no item for the user: decide by `docs/claude-md/tracks.md` row 2." and "Under `[admin]`, do not ask: decide by `docs/claude-md/tracks.md` row 3."; `brainstorming` "Under `[admin]`, do not wait: decide by `docs/claude-md/tracks.md` row 4."; `to-issues` "Under `[admin]`, do not quiz the user: decide by `docs/claude-md/tracks.md` row 12."; `craft-agent` "Under `[admin]`, it does not ask: it decides by `docs/claude-md/tracks.md` row 11."; `settings-setup` "Under `[admin]` too: decide by `docs/claude-md/tracks.md` row 5; writing the settings stays yours."; `resolve-question` step 2 "With `[admin]`, cite `PRD.md`, the glossary and `docs/legacy/` (if any) first, then code." (8191 bytes; trimmed: "The user talks only to you: every HITL message goes through your chat." and "in the repo" after "may follow a lead anywhere"; no pinned string touched).

`site/docs.html:466`: "A force push or a push of any other branch stays blocked. With <code>[admin]</code>, <code>ship</code> runs as a plan only, never a deploy."

**DELTA**: With `[admin]`, a busy user's one request now runs the whole pipeline: the Supervisor asks Stage 0 questions only on a new project, decides and approves everything else itself from `PRD.md`, the glossary and `docs/legacy/`, stops only for the `### Stops that stay` list, and writes the `ship` plan (never a deploy); plain `[auto]` is unchanged.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
