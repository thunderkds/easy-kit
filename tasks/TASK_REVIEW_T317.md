# TASK_REVIEW — T317: session-wide `[admin]` and `[ticket]` tags; Autonomous setup profile

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
With `/verify (yours)`, your pass goes in the `verify` row below: Result `☑ pass`, Notes `/verify by the user, session <id>, commit <sha>`.

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
7. Site settings-tool parity tests exclude `autonomous` (opt-in Stage 1 skill profile; the site tool and its `defaultMode` ban stay unchanged) — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task"); no UI change keeps Hard-Stop Gate 6 out of scope
8. G1 binding narrowed: the loop binding also needs the hook's pass record written after the tag request, so the T284 P1 "work that merely names a task does not bind it" tests pass unchanged — RULE: `.claude/hooks/lib/auto_mode.py:91` "Any doubt is \"not admin\""
9. Remaining build steps go to a fresh implementer run after the first hit the step limit — RULE: docs/claude-md/tracks.md § Stops that stay ("the same sub-agent hitting the step limit twice"): first hit, different run
10. `T317` added to `AUTHORISED_TASKS` in `.claude/hooks/tests/merge_gate_guard.py` after Claude Code's classifier blocked the agent's edit — RULE: the user's answer, 2026-11-15 "yes [admin]" — RULE: tasks/TASK_REVIEW_T317.md § Auto decisions (pause on the safety-hook block, answered by the user)
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. T317 starts in parallel with T314; T315 and T316 wait for T314 — FACT: tasks/TASK_GUIDE_T315.md:126 "- `.claude/hooks/pre_tool_sensitive_path.py`" (T315 edits the same hook as T314; T317's Files to Change do not include it)
2. A session tag survives `/compact` (including auto-compact) and ends at any resume, continue or fork; the user types it again after a resume; while a tag is on, the Supervisor's first reply line names it — DEBATED: survive compact, end at resume (Advocate 1: `[ticket]` survives compact and same-id resume, `[admin]` ends at both; Advocate 2: survive both, plus a first-line guard; Advocate 3: survive compact, end at resume via a `SessionStart` resume marker). Picked by RULE: `.claude/hooks/lib/auto_mode.py:91` "Any doubt is \"not admin\"" — the raw typed tag is still in the same transcript after a compact (no doubt); a resume is a new moment of intent (doubt) ⚠ decided for you — please review
3. Oracle gap G1: under a session tag the merge gate binds to the branch's task, the only one this session holds open, with a passed auto verify — RULE: tasks/TASK_GUIDE_T317.md § Out of scope ("the loop is one ticket at a time inside one session")
4. Oracle gap G2: a `[ticket]` push needs a passed auto verify — RULE: tasks/TASK_GUIDE_T317.md § Requirement ("run it Stage 0–5 in auto mode, push its feature branch")
5. Oracle gap G3: a later `[auto]` ends a session tag — RULE: tasks/TASK_GUIDE_T317.md § Requirement ("until the user types `[stop]` (or a different tag)")
6. Oracle gap G4: update the five-profile-id test — RULE: AGENTS.md § Karpathy Engineering Principles (Goal-Driven Execution)
11. Code-review fix round R1-R6 applied as the guide records them; R2 moves the resume mark under the anchors base, and the older AC8 helpers are re-locked to it by qa-expert (631da7a7) — RULE: tasks/TASK_GUIDE_T317.md § Approach (decision 3, fix round R1-R6)
12. Two AC8 checks that could no longer fail after R2 (unsafe session id, bad stdin) re-locked to the anchors base by qa-expert (d7bfd5ae), with a scratch mutation run showing 6 failures — RULE: tasks/TASK_GUIDE_T317.md § Evaluation & Acceptance ("written first by `qa-expert` ... The implementer may not edit them")
Checks: tests `python3 -m pytest .claude/hooks/tests/test_t317_session_tags.py .claude/hooks/tests/test_t317_fix_round.py -q -p no:cacheprovider` — 165 passed; full `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` — 7410 passed, 5 skipped; reviews code-review (re-review after R1-R6) — P0 0 / P1 0 / P2 0 / P3 1; security-review — no findings; real run: the Demonstration AFTER driver above — printed the blocked and allowed lines shown (auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t317_session_tags.py` (AC1-AC8), `.claude/hooks/tests/test_t317_fix_round.py` (R1-R6), `.claude/hooks/tests/test_t317_loop_binding.py`, `tests/test_settings_setup.py` (autonomous profile). `python3 -m pytest .claude/hooks/tests/test_t317_session_tags.py .claude/hooks/tests/test_t317_fix_round.py -q -p no:cacheprovider` → `165 passed in 6.52s` at d7bfd5ae |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q -p no:cacheprovider` at d7bfd5ae → `7410 passed, 5 skipped, 25 subtests passed in 360.26s (0:06:00)` |
| Negative cases hold | ☑ pass | Red run of the locked oracle on unchanged code fc1e69c8: `118 failed, 19 passed` (Demonstration BEFORE). Fix-round oracle at 1a56fafb: `4 failed, 161 passed` (the 4 R2 tests). AC8 re-lock mutation (scratch copy, hook writes `$CLAUDE_TRACE_ANCHOR_DIR/x/mark` on every call): `6 failed, 131 deselected` on the new lines 730 and 742 |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff main...HEAD` on feat/t317-session-tags: `lib/auto_mode.py`, `lib/session_work.py`, `pre_bash_block_unsafe_merge.py`, `session_start_resume_mark.py`, `stop_auto_mode_check.py`, the three hook wirings, `settings-setup` profile and SKILL, tracks.md, AGENTS.md; callers `lib/verify_record.py` (record_dir) and `board_rows`. Skipped: hooks the diff does not touch |
| Full smoke suite still green (no regression) | ☑ pass | `7410 passed, 5 skipped, 25 subtests passed in 360.26s` at d7bfd5ae |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier MCP server failed to connect (ECONNREFUSED) this session; neither companion tool was run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: hook, docs and skill-data change |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI: hook, docs and skill-data change |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI: hook, docs and skill-data change |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured by `qa-expert` on the unchanged code (branch `feat/t317-session-tags` at `fc1e69c8`; `git diff --stat e76d0e44..HEAD` touches only `tasks/TASK_GUIDE_T317.md` and `tasks/TASK_REVIEW_T317.md`, so no implementation commit exists). Driver: the gate's real `main()` with constructed boards, repos and transcripts, through the oracle's own fixtures (`tagged_session`, `not_passed`, `auto_verified` in `.claude/hooks/tests/test_t317_session_tags.py`). Today an `[admin]` request followed by one untagged request falls back to the gate with no tag: the `[admin]` rule is gone, both its allowance and its limits. The merge with no auto verify is blocked, but by the normal `Pipeline gate`, not by `[admin]`. With a passed verify, a force push and a push to `main` go through; `[ticket]` is not read at all.

```
captured 2026-11-15T10:21:16Z on fc1e69c8 (feat/t317-session-tags, no implementation commit)
$ python3 -c 'import auto_mode; auto_mode.session_tag(...)'
AttributeError: module 'auto_mode' has no attribute 'session_tag'
transcript: human 'run the board [admin]' (-900s), then 'thanks', 'go on', 'and the next one' (no tag)
latest request: 'and the next one' | admin_request: None
[no auto verify]  git merge feat/t900-x  -> BLOCKED: [hook:pre_bash] Pipeline gate failed — cannot push/merge: | • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
[no auto verify]  git push origin feat/t900-x  -> BLOCKED: [hook:pre_bash] Pipeline gate failed — cannot push/merge: | • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
[no auto verify]  git push --force origin feat/t900-x  -> BLOCKED: [hook:pre_bash] Pipeline gate failed — cannot push/merge: | • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
transcript: human 'work the tickets [ticket]' (-900s), then 3 untagged requests; T900 auto verify passed
[ticket]  git merge feat/t900-x  -> ALLOWED (no block)
captured 2026-11-15T10:21:29Z on fc1e69c8
transcript: same [admin]-then-3-untagged session; T900 auto verify passed
[admin earlier]  git push --force origin feat/t900-x  -> ALLOWED (no block)
[admin earlier]  git push origin feat/t900-x:main  -> ALLOWED (no block)
[admin earlier]  git push --tags  -> ALLOWED (no block)
captured 2026-11-15T10:21:39Z on fc1e69c8
$ python3 -m pytest .claude/hooks/tests/test_t317_session_tags.py -q -p no:cacheprovider
118 failed, 19 passed in 26.45s
```

**AFTER**: same driver, through the oracle's fixtures, on the T317 implementation (`5c12c7fb`). Now an `[admin]` request holds for the later untagged requests (`session_tag` returns `admin`), and with it every `[admin]` limit: no auto verify blocks with the `[admin]` reason, and a force push, a push to `main` from the task branch and `--tags` are blocked. `[ticket]` allows only the plain push of the task branch to `origin`, never a merge. After the session's own merge, a plain `git push origin main` goes through; a force push of `main` does not.

```
captured 2026-11-15T11:14:16Z on 5c12c7fb (feat/t317-session-tags, T317 implementation)
$ python3 -m pytest .../scratchpad/test_demo_after.py -s -q -p no:cacheprovider
transcript: human 'run the board [admin]' (-900s), then 'thanks', 'go on', 'and the next one' (no tag)
session_tag: 'admin' | admin_request: None
[no auto verify]  git merge feat/t900-x  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: T900 has no passed auto verify committed on feat/t900-x (a hook-written `auto-run by hook` row with its run record for that commit)
[no auto verify]  git push origin feat/t900-x  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: T900 has no passed auto verify committed on feat/t900-x (a hook-written `auto-run by hook` row with its run record for that commit)
[no auto verify]  git push --force origin feat/t900-x  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: `[admin]` allows only a plain push of the task branch, or of `main` after the task's own merge, to the same branch: no force, no other destination
transcript: human 'work the tickets [ticket]' (-900s), then 3 untagged requests; T900 auto verify passed
[ticket]  git merge feat/t900-x  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[ticket]` does not allow this command: `[ticket]` allows no merge: only a plain push of the task branch to `origin`
[ticket]  git push origin feat/t900-x  -> ALLOWED (no block)
transcript: same [admin]-then-3-untagged session; T900 auto verify passed
[admin earlier]  git push --force origin feat/t900-x  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: `[admin]` allows only a plain push of the task branch, or of `main` after the task's own merge, to the same branch: no force, no other destination
[admin earlier]  git push origin feat/t900-x:main  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: `[admin]` allows only a plain push of the task branch, or of `main` after the task's own merge, to the same branch: no force, no other destination
[admin earlier]  git push --tags  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: `[admin]` allows only a plain push of the task branch, or of `main` after the task's own merge, to the same branch: no force, no other destination
transcript: same [admin] session, then this session's own merge of feat/t900-x into main and one more untagged request; T900 auto verify passed
[admin earlier]  git push origin main  -> ALLOWED (no block)
[admin earlier]  git push --force origin main  -> BLOCKED: [hook:pre_bash] Auto-mode gate — cannot push/merge: | • `[admin]` does not allow this command: `[admin]` allows only a plain push of the task branch, or of `main` after the task's own merge, to the same branch: no force, no other destination
4 passed in 0.38s
$ python3 -m pytest .claude/hooks/tests/test_t317_session_tags.py -q -p no:cacheprovider
137 passed in 3.33s
```

**DELTA**: The user can now type `[admin]` or `[ticket]` once and have it hold for the whole session, with `[ticket]` limited to a plain push of the task branch and `[admin]` to the task's own merge and `main` push after a passed auto verify.

**WITNESS**: BEFORE by qa-expert at 2026-11-15T10:21Z on fc1e69c8; AFTER by the implementer at 2026-11-15T11:14Z on 5c12c7fb; re-checked by the Supervisor's full suite run at d7bfd5ae (7410 passed) and by the hook's auto verify run that follows Ready for Review.
