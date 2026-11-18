# TASK_REVIEW — T326: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T326.md`. Everything here is **filled by the reviewer at Stage
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
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. Track extended, Risk High, C2 (merge gate change) — RULE: `docs/claude-md/tracks.md` `### Debate size by Risk` and AGENTS.md `## Tracks` ("Risk Medium or High" → extended)
2. Supervisor sign-off: `T326` added to `AUTHORISED_TASKS` for the old-git main-push rule only — RULE: `.claude/hooks/tests/merge_gate_guard.py` "Adding a task is the record" (Supervisor sign-off under `[admin]`)
3. On git < 2.38, compute the clean-merge tree with `read-tree -i -m --aggressive` + `write-tree` in a temp index (option A), not "refuse with an upgrade message" (B) or "require git 2.38 at install" (C) — DEBATED: A (Advocate 1: A, no false accept found, B/C leave 2.34 users without the gate; Advocate 2: B or narrowed A, write-tree adds objects, env scrub partial; Advocate 3: B, smallest safe thing, A refuses often on shared files). Decided A by the requirement: `tasks/TASK_GUIDE_T326.md` Restated intent "the `[admin]` push of `main` ... is decided exactly as on new git" — B and C do not meet it; every Advocate found A fail-closed (refuses only, never a false accept). ⚠ decided for you — please review
4. Debate findings taken: docstring no longer says "read-only" (write-tree adds tree objects, as merge-tree --write-tree does); test for an identical change on both sides added — SAFER OPTION: test-only and comment-only changes ⚠ decided for you — please review
5. Stage 4 P2 fixed: `_git_has_write_tree` version boundary pinned by tests (2.37/2.38/3.x/unreadable/failed) — SAFER OPTION: test-only ⚠ decided for you — please review
6. Security review done by hand: the built-in `security-review` skill fails here (`git log origin/HEAD...`: this repo has no `origin` remote) — FACT: `git remote -v` "github	git@github.com:thunderkds/easy-kit.git (fetch)" ⚠ decided for you — please review
Checks: tests `uv run --with pytest python -m pytest -q .claude/hooks/tests/test_t326_old_git_main_push.py .claude/hooks/tests/test_admin_tag.py .claude/hooks/tests/test_merge_gate_guard.py .claude/hooks/tests/test_stop_auto_mode_check.py tests/test_auto_mode.py` — 482 passed (BEFORE: test_admin_tag.py 20 failed); full suites: 49 failures, the same 49 fail on `main` (test_stop_attribution_t287, test_slot2b_brace_glob, test_heredoc_quoted_marker, test_gate_hidden_verbs); reviews code-review — 0 P0, 0 P1, 1 P2 (fixed); security-review (by hand) — no findings: fallback runs only merge-base/read-tree/write-tree into a temp index, `_admin_repo_refusal` (config allowlist, hooks, merge/filter/diff attributes) runs first, a trivial merge cannot add content from neither side; real run: on git 2.34.1 `_main_push_refusal` returns None for a clean merge and refuses an extra change (auto-checked, not /verify)
Memory: memory/learnings.md — "2026-11-18 — `[admin]` with two new guides, a repo without `origin`, and git 2.34"; memory/MEMORY.md — `[admin]` binds line extended
Not done: merge (admin: after the auto verify pass); push of `main` (yours: the gate pushes only to `origin`, this repo's remote is `github`); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t326_old_git_main_push.py` (clean merge, extra change, conflict, index/refs untouched, git failure, criss-cross; each on real git 2.34.1 and a forced-fallback path) | [test file path(s) — required before Done] |
| Verification command run | ☑ pass | `pytest -q test_admin_tag.py test_t326_old_git_main_push.py test_merge_gate_guard.py` -> 267 passed (BEFORE: 20 failed in test_admin_tag.py). Full suites `.claude/hooks/tests tests`: 7504 passed, 50 failed: 49 pre-existing (test_stop_attribution_t287, test_slot2b_brace_glob, test_heredoc_quoted_marker, test_gate_hidden_verbs: identical 49 failed on a detached `main` worktree) + 1 flake (test_auto_verify_skip_pass tracks.md param, 222 passed alone) | [paste actual output] |
| Negative cases hold | ☑ pass | red run before the change: forced-old tests ERROR/FAIL (`_git_has_write_tree` absent); test_admin_tag.py 20 failed | [paste the red run against the prior content, or the mutation diff (`git diff --stat`, non-empty) before each verdict] |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `pre_bash_block_unsafe_merge.py` `_main_push_refusal` + new helpers, its callers (`admin_refusal`), the new and pinned tests, the tracks.md line; rest of the gate not re-reviewed (unchanged) |
| Full smoke suite still green (no regression) | ☑ pass | no new failure vs `main`; see Verification row | |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: easy-verifier not installed in this session |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured 2026-11-18T15:35:15Z, git 2.34.1, before any implementation commit, `uv run --with pytest python -m pytest -q .claude/hooks/tests/test_admin_tag.py` (tail):

```
2026-11-18T15:35:15Z
git version 2.34.1
FAILED .claude/hooks/tests/test_admin_tag.py::test_r3_n4_harmless_values_of_those_keys_stay_allowed[core.autocrlf-input]
FAILED .claude/hooks/tests/test_admin_tag.py::test_r3_n4_harmless_values_of_those_keys_stay_allowed[user.name-T]
FAILED .claude/hooks/tests/test_admin_tag.py::test_r3_n4_harmless_values_of_those_keys_stay_allowed[branch.main.merge-refs/heads/main]
20 failed, 211 passed in 13.71s
```

Cause: `` `[admin]` does not allow this command: `git merge-tree --wri... `` (`git merge-tree --write-tree` needs git >= 2.38).

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
