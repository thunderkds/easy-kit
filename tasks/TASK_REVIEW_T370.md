# TASK_REVIEW — T370: The default branch is the setting EASY_KIT_DEFAULT_BRANCH

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
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Review verdict

**Verdict: PASS with findings (no P0/P1). Commit 36a1a8073b6e10a81a593975965a9a92c2d7092d, reviewed alone, from the repo only.** Risk High: code-review and the security-reviewer hooks checks applied.

### Findings

| ID | Sev | Conf | Finding | Where |
|----|-----|------|---------|-------|
| P2-1 | P2 | 0.9 | Test gap, proven by a surviving mutant: no test drives a bad setting through `verify_record._base()`. Replacing its `raise OSError` with `return "refs/heads/main"` leaves all 31 new tests green, so the guide's AC 4 "None for a bad value: no docs-only pass" and the edge-case line "`_base()` raises inside its `try`" are pinned only at `base_ref()`, not at `docs_only_change`, `shell_suites_changed` or `record_confirms_pass`. Today the gate refuses first (`_default_branch_refusal`), so no bypass is reachable by the `[admin]` path; the fail-closed layer is unguarded against a later edit. Add one test: bad setting, `docs_only_change(...)` is None and `record_confirms_pass(...)` is False. | `.claude/hooks/lib/verify_record.py` `_base` |
| P3-1 | P3 | 0.9 | Surviving mutant 2: `review_in_scope` with `name = "main"` passes every test; the "bad setting reads the whole history (fail closed)" and the `master` base are untested there. | `.claude/hooks/pre_bash_block_unsafe_merge.py` `review_in_scope` |
| P3-2 | P3 | 0.8 | Stale `main` in docstrings after the change: `verify_record.docs_only_change` ("merge-base of `refs/heads/main`"), `shell_suites_changed` ("left `main`"), `_remote_main`, `_main_push_refusal`, the `main..tip` comments. Refusal texts that say `main` on a `master` repo (`cannot resolve \`main\``, `\`main\` does not hold ...`) are declared out of scope in the guide; only the docstrings are drift. | same files |
| P3-3 | P3 | 0.6 | `default_branch()` accepts a few names git itself rejects (`a/b.lock/c`, `MAIN` on a case-insensitive filesystem) and `refs/heads/x`-style values. All are the user's own setting and fail as a missing ref, never as a wrong ref; fail-closed holds. No change needed. | `.claude/hooks/lib/auto_mode.py` `default_branch` |
| Note | info | 1.0 | Residual exposure, already declared in the guide: the setting sits in `.claude/settings.json`, which an agent can write (same as `EASY_KIT_ADMIN_REMOTE`), and `cleanup_task.py` reads the agent's shell environment. The design is no worse than T321 and better than any git-derived source. Not re-opened here. | guide Cut list |

### Checks done

- Security (hooks): a bad value never reaches a ref or an argv: probed 19 values with the real `default_branch()` (`a\nb`, `feat@{1}`, `-x`, `HEAD`, `a b`, `a~1`, `a^`, `..`, `@`, `a/`, `a.`, `x.lock`, non-ASCII: None; `main`, `master`, `a/b`, `release/1.0`: themselves). No option injection into `git ls-remote` / `merge-base`, which also get `refs/heads/` prefixed.
- Fail closed: `_default_branch_refusal` is the first check in `admin_refusal`, covering `[admin]` and `[ticket]`, merge and push; its message names the setting and the shown value, never `None`.
- A `main` repo with the setting unset: same refs and argv as before; the older suites pass unchanged (680 passed).
- The allowlist change (`AUTHORISED_TASKS` plus its pin test) matches the guide's recorded user sign-off.
- Reader read at call time (not import time), so a session-start setting is honoured.

### Negative cases

| Case | Result |
|------|--------|
| Bad setting (`a..b`, option, `HEAD`, space) refuses merge and push, names the setting | held (mutant `if False:` killed, 4 failed) |
| `master` repo, setting unset: push of `master` refused | held (control test) |
| `master` setting, push of an agent-made `main` refused | held (mutant `branch == "main"` killed, 3 failed) |
| Cleanup on a bad setting removes nothing | held (mutant killed, 1 failed) |
| `verify_record._base` bad value raises | NOT pinned (P2-1) |
| `review_in_scope` on `master` | NOT pinned (P3-1) |

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t370_default_branch.py` (AC 1-4), `tests/test_t370_cleanup_default_branch.py` (AC 5); AC 6 by the older suites. Two paths are not pinned, see P2-1 and P3-1 |
| Verification command run | ☑ pass | the guide's command, run in `/home/thunderkds/workspace/pets/hungnguyen111/wt-t370` at 36a1a807: `680 passed in 120.08s (0:02:00)` |
| Negative cases hold | ☑ pass | 11 mutants on a `git archive` scratch copy (scratchpad `m/`, the worktree untouched), the 2 new test files only: 9 killed (`4 failed`, `5 failed`, `2 failed`, `4 failed`, `1 failed`, `3 failed`, `2 failed`, `2 failed`, `1 failed`); 2 SURVIVED: `verify_record._base` raise replaced by `return "refs/heads/main"` (31 passed) and `review_in_scope` `name = "main"` (31 passed). Pre-change red run: the guide records `27 failed, 4 passed` on `main` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read the whole diff (10 files). Grepped `.claude/hooks`, `.claude/hooks/lib`, `scripts` for any left `main` ref: none remains as code (`auto_mode.DEFAULT_BRANCH` only); the rest are docstrings and the declared-out-of-scope refusal texts. Skipped: `scripts/agent_ws.py` (uses HEAD, not `main`), site, installer |
| Full smoke suite still green (no regression) | ☑ pass | The 9 files of the Verification Command (680 passed) cover every suite that touches the gate, verify record and cleanup. The whole repo suite was not run by this review |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: no companion tool was asked for this review |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI: hook code, a script and doctrine text |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI: no component, token or style changed |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI: nothing renders at a viewport |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: [pasted timestamped command output showing the thing absent/failing, captured before the
first implementation commit] OR [verbatim excerpt of the prior content, for non-executable changes]

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
