# TASK_REVIEW — T284: `[admin]` tag — auto mode plus merge and push after a passed verify

> Sibling of `tasks/TASK_GUIDE_T284.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` tag,
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_admin_tag.py` (new, 100+ cases: AC 1-10, SC 1-7b); repointed/narrowed pins: `.claude/hooks/tests/test_merge_gate_guard.py`, `.claude/hooks/tests/test_agent_guide_dedup.py`, `tests/test_stage_names.py`, `tests/test_site_story.py`. Run by common-infrastructure on HEAD `2a7d4545`, 2026-11-08T00:07:49Z: `python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"` → `644 passed, 979 deselected in 24.92s` |
| Verification command run | ☑ pass | HEAD `2a7d4545849f68d49adb79e34b49403eea479d28`. `python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"` → `644 passed, 979 deselected in 24.92s` (2026-11-08T00:11:01Z). `python3 -m pytest .claude/hooks/tests/ tests/ -q` → `FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid` / `1 failed, 3543 passed, 25 subtests passed in 238.38s (0:03:58)` (2026-11-08T00:15:00Z). The one failure is T283's own report test and also failed before any T284 change (BEFORE). |
| Negative cases hold | ☑ pass | Red before the change: `55 failed, 15 passed` (BEFORE, 2026-11-07T23:34:41Z). Mutations in a scratch copy, each byte-changing (`diff`/`cmp` exit 1): M1 passed-verify check → `if False` (2026-11-07T23:55:17Z): `3 failed` (all sc3 tests); M2 push-shape check → T197 resolver (23:55:34Z): `6 failed` (sc7 force, f, lease, plus, dst-other, no-verify); M3 tracks.md AC 10 sentence removed (23:59:45Z): `1 failed` (`test_ac10_admin_tag_section_states_...`); M4 merge-happened check removed for the `main` push (2026-11-08T00:05:28Z): `2 failed` (`test_sc7b_main_push_without_a_merge_in_this_session_is_blocked`, `test_sc7b_a_merge_only_in_the_transcript_is_not_a_merge`). Not done by the Supervisor yet (Stage 4 own mutant). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | Same full run as above: `1 failed, 3543 passed`; the failure is pre-existing (T283). `sh tests/test_readme_current.sh` → `FAIL: AC2: could not parse any skill names from README's Codex-skip bullet list` on this branch AND on `main` `4c076b6c` (run read-only in the main checkout), so pre-existing, not T284. |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured by common-infrastructure in `/home/hungnguyenhuu/workspace/pets/wt-t284` at
HEAD `faa5180f` (no implementation commit yet; only the new test file existed, uncommitted).

The guide's verification commands, before any change:

```
$ date -u; python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"
2026-11-07T23:27:33Z
542 passed, 979 deselected in 20.19s
$ python3 -m pytest tests -q
1 failed, 1920 passed in 169.77s (0:02:49)
FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid   <- pre-existing, T283's own report (not this task)
2026-11-07T23:30:44Z
```

The new tests for AC 1-9, written first, before any implementation:

```
$ date -u; python3 -m pytest .claude/hooks/tests/test_admin_tag.py -q
2026-11-07T23:34:41Z   (HEAD faa5180f)
55 failed, 15 passed in 1.40s
```

The core of the red run: with a passed, hook-written auto verify and the request `do it [auto]`,
today's gate returns no block (`None`) for `git merge`, `git push` and `git pull` of the task branch.
"Never in auto mode: merge, push" was doctrine only; the gate did not read the tag at all:

```
$ date -u; python3 -m pytest ".../test_admin_tag.py::test_sc4_auto_only_with_a_passed_verify_stays_blocked" -q
2026-11-07T23:34:49Z
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[merge] _________
E       AssertionError: None
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[push] __________
E       AssertionError: None
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[pull] __________
E       AssertionError: None
```

The 15 that passed before are the controls and negative cases that hold today (an exact-tag miss
such as `[Admin]` is trivially not admin when nothing reads the tag; a hand-typed `☑ pass` row
passes the plain gate; a rebase is not blocked).

**BEFORE refresh (2026-11-08)**: AC 10 (Supervisor starts the auto verify run, merges only on a pass) and the
AC 8 change (`[admin]` may push `main` after its own merge) came after the capture above. Their tests were
written first and seen red before the code: the 7b allowed case failed `4 failed` at 2026-11-08T00:04:45Z
(`main names no single task`); AC 10 is a docs statement, and its tests failed until the `tracks.md` text existed.

**AFTER**: HEAD `2a7d4545`, run by common-infrastructure:

```
$ date -u; python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"
2026-11-08T00:07:49Z
644 passed, 979 deselected in 24.92s
$ python3 -m pytest .claude/hooks/tests/ tests/ -q
FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid - Asser...
1 failed, 3543 passed, 25 subtests passed in 238.38s (0:03:58)
2026-11-08T00:15:00Z
```

`test_sc4_auto_only_with_a_passed_verify_stays_blocked[merge|push|pull]`, red in the BEFORE, now pass: with
`[auto]` the gate blocks with `Auto-mode gate — cannot push/merge`.

**DELTA**: The user can write `[admin]` so the Supervisor runs the task in auto mode, starts its auto verify run, and only after a hook-proven pass merges and pushes the task branch and then `main`; with `[auto]` alone the gate now actually blocks merge, push and pull.

**WITNESS**: Not yet witnessed. The runs above are by common-infrastructure (the implementing agent),
2026-11-07T23:27Z to 2026-11-08T00:15Z, attributed to T284 in `memory/event-trace/T284.jsonl`. The implementing
agent alone does not witness: the Supervisor's Stage 4 rerun, or the headless auto verify run, fills this.
