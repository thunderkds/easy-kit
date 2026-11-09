# TASK_REVIEW — T296: Merge gate: hidden git verbs, `merge --message`, and slot 2b brace and glob escapes

> Sibling of `tasks/TASK_GUIDE_T296.md`. Everything here is **filled by the reviewer at Stage
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

-->

## Auto decisions

Mode: auto
1. The hidden-verb refusal applies only under `[auto]` and `[admin]`; with no tag the 11 forms stay allowed as before, and a no-tag refusal is a separate task with its own corpus of ordinary commands. The guide's AC row 1 (line 58) and test row 1 (line 77) say "still blocked with no tag", but requirement (a) (line 28) says "Under `[auto]` and `[admin]`" — DEBATED: auto-mode only, amend AC row 1 and test row 1 (Advocate 1: keep auto-only, because a no-tag refusal blocks ordinary `$(…)` and `$var` git commands in every session; Advocate 2: keep auto-only, correct the two guide rows, open a follow-up task with a false-positive corpus if a no-tag refusal is wanted; Advocate 3: keep auto-only as the smallest safe thing, because the hook comment says "Outside auto mode nothing changes" and `docs/claude-md/tracks.md:642` says "Outside auto mode these forms behave as before") ⚠ decided for you — please review
2. The code review and the security review of this branch must report before the task is marked ready — RULE: `docs/claude-md/pipeline-stages.md` § Stage 4 ("Skill({ skill: "code-review" }) always; security-review for Medium/High risk")
Checks: tests (implementer) `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` — 4797 passed; 414 new tests, 19 mutation controls red; real run in bash and zsh, 11 forms, with and without the gate (auto-checked, not /verify); reviews code-review and security-review — pending
Memory: nothing new yet — the pass runs after the reviews
Not done: merge (yours); auto verify: not started, Stage 4 reviews are open

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_gate_hidden_verbs.py` (rows 1, 2, 3, 5, 6, 7, 8) and `.claude/hooks/tests/test_slot2b_brace_glob.py` (rows 4, 5, 6); `merge_gate_guard.py` and `test_merge_gate_guard.py` (row 8, `T296` in `AUTHORISED_TASKS`). Run against the unchanged hooks they gave 114 failed (see Demonstration); now `414 passed in 5.76s`. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or slot or task_context or hidden"` -> `1147 passed, 1690 deselected in 28.33s`. `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4797 passed, 25 subtests passed in 332.50s (0:05:32)` (2026-11-09, HEAD `7503935d`). |
| Negative cases hold | ☑ pass | Red run against the prior content: 114 failed, 268 passed (Demonstration). Mutation controls (19), each one byte change in `pre_bash_block_unsafe_merge.py` or `lib/task_context.py` (`git diff --stat` non-empty), run on the two new test files (414 tests), restored after each; every one turned tests red. The three the guide names: M1 `hidden_git_verb` returns False: `103 failed, 311 passed`; M2 `--message` out of `MERGE_OPTIONS_WITH_ARG`: `6 failed, 408 passed`; M3 brace refusal out of slot 2b: `7 failed, 407 passed`. Diffs and the rest are under the table. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the two hook files and the five test files named in the guide, `docs/claude-md/tracks.md` (`### Admin tag`, Known limits, slot 2b rules). Dependents of `invokes_test_runner` and slot 2b ran in the full suite. Stale-text grep (LR-0005) for `quote inside the word`, `Cheap hidden verbs`, `merge --message <branch>`, `find -exec git`, `cannot tell which branch` over the repo: only history (`TASK_REVIEW_T284`, the hunt, guides) and the new tests remain. Not reviewed: the heredoc scanner (T294) and the repo config and hook allowlist (T295), out of scope. Not run by this agent: `code-review` and `security-review` skills (Stage 4, the Supervisor). |
| Full smoke suite still green (no regression) | ☑ pass | `4797 passed, 25 subtests passed in 332.50s (0:05:32)`. The pin tests the guide names ran in it: `test_admin_tag.py` (T284), `test_stop_attribution_t287.py`, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, the tracks.md text pins, `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. |
| **Companion score (easy-verifier)** | ☑ N/A | Neither companion tool was run for this task; the guide does not require it. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Hook code and docs only; no UI component. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Hook code and docs only; no UI component. |
| **UI: Responsiveness at target viewports** | ☑ N/A | Hook code and docs only; no UI component. |

**Mutation controls** (each applied to the worktree, tests run, file restored with the original bytes; run 2026-11-09):

```
M1  .claude/hooks/pre_bash_block_unsafe_merge.py  | 1 +
+    return False     (first line of the body of hidden_git_verb, before `text = strip_heredoc_bodies(command)`)
    -> 103 failed, 311 passed
M2  .claude/hooks/pre_bash_block_unsafe_merge.py  | 2 +-
-MERGE_OPTIONS_WITH_ARG = frozenset({"-m", "--message", "-F", "--file", ...
+MERGE_OPTIONS_WITH_ARG = frozenset({"-m", "-F", "--file", ...
    -> 6 failed, 408 passed
M3  .claude/hooks/lib/task_context.py  | 2 +-
-    if "{" in command or "}" in command or _unquoted_glob(command):
+    if _unquoted_glob(command):
    -> 7 failed, 407 passed
M4  glob refusal out (`or _unquoted_glob(command)` removed)            -> 5 failed, 409 passed
M5  `send-pack` out of PUBLISH_VERBS                                    -> 5 failed, 409 passed
M6  `_own_origin_refusal` returns None at once                          -> 1 failed, 413 passed
M7  slot 2b `_git_verb_allowed` check removed                           -> 5 failed, 409 passed
M8  backslash + newline joined with a space again                       -> 2 failed, 412 passed
M9  `invokes_test_runner` back to QUOTED_SPAN_PATTERN                   -> 14 failed, 400 passed
M10 `--cleanup` out of MERGE_OPTIONS_WITH_ARG                           -> 2 failed, 412 passed
M11 `--file` out of MERGE_OPTIONS_WITH_ARG                              -> 3 failed, 411 passed
M12 `timeout` out of SHELL_WRAPPERS                                     -> 1 failed, 413 passed
M13 the verb refusal reason back to "cannot tell which branch"         -> 3 failed, 411 passed
M14 abbreviated long option (`--mess`) rule off                         -> 3 failed, 411 passed
M15 short-option run rule (`-qm <x>`) off                               -> 18 failed, 396 passed
M16 nonliteral command word (`$g push`) rule off                        -> 10 failed, 404 passed
M17 `bash -c '...'` recursion off                                       -> 5 failed, 409 passed
M18 depth limit off                                                     -> 1 failed, 413 passed
M19 PLAIN_VERB check off                                                -> 26 failed, 388 passed
```
The first agent run also reached a wrapper-assignment mutation (its M23, pinned by commit `4faf490a`).
Mutation script (outside the repo): `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/53a340c2-ba9d-4416-b11e-5082d9905521/scratchpad/mutate.py`.

**Follow-ups and notes** (cut list, not built): `-S`/`--gpg-sign` and `--log` take an optional attached value only, so they never take the next word (git's own rule; pinned by `(["-S", B], [B])`). `git submodule foreach` and `git rebase --exec` stay unseen and are named in Known limits. The stray root file `corpus_old.json` (a capture artifact, referenced by no test) was removed.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08 at HEAD `bc5ccc34`, before any implementation commit; the unchanged
gate, the repo's own `gate` fixture with a passed auto verify of T900, driven through `main()` with no
tag, a typed `[auto]` request and a typed `[admin]` request; then the same command line run for real
in `bash -c` and `zsh -c` inside a throwaway clone with a throwaway bare remote under pytest's tmp dir,
`HOME` isolated). Script: the Supervisor-scratchpad file `capture_t296.py` (not in the repo). A
`real push landed` of True means `refs/heads/feat/t900-x` exists on the bare remote afterwards. The
last line is the `send-pack` form, run with the bare remote at `../origin.git`:

```
2026-11-08T15:25:31Z  'v=push; git $v origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'g=git; $g push origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'v=pu; git ${v}sh origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'git {p..p}ush origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  "git $'push' origin feat/t900-x"
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  "$'git' push origin feat/t900-x"
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'env -i git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'timeout 20 git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'nice git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'bash -c \'git "push" origin feat/t900-x\''
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
2026-11-08T15:25:31Z  'git send-pack ../origin.git feat/t900-x'
    gate: none=ALLOWED [auto]=ALLOWED [admin]=ALLOWED   real push landed: bash=True zsh=True
```
All 11 forms: ALLOWED by the gate in all three modes, and the push landed in both shells.

Tests written first, run against the unchanged hooks (2026-11-08T15:30:30Z, HEAD `bc5ccc34` plus the
two new test files, no implementation commit):

```
$ python3 -m pytest .claude/hooks/tests/test_gate_hidden_verbs.py .claude/hooks/tests/test_slot2b_brace_glob.py -q -p no:cacheprovider
114 failed, 268 passed
  failed by test (count): hidden form flagged (unit) 34, gate blocks each hidden form in [auto]/[admin] 22,
  block names its reason 3, merge options with a value 8, real repo + merge.defaultToUpstream 1,
  plain branch still the target (--message) 1, slot 2b brace/glob not filed 12, backslash mention
  not a test run (trace gate) 5, backslash mention (slot 2b + gate) 3, continuation joins a word 1,
  continuation cannot glue a path 1, real runs still count (py\<nl>test) 1, branch move not filed 5,
  clone with another origin refused 1, --output/--ext-diff reason 3, rev-parse doc 1, known-limits
  text 2, hidden-verb limit text 1, corpus merge sources 6, corpus test-run answers 4
  passed (the guards that must hold before and after): ordinary [auto]/[admin] commands, [admin]
  push/merge forms, no-tag behaviour, quoted globs and plain runs still filed, the old corpus answers
```

**BEFORE note (resume)**: the capture above was taken by the first agent run on 2026-11-08 against
base commit `bc5ccc34`, before any implementation commit; it is kept as it is. The Supervisor
scratchpad script `capture_t296.py` is gone, so the AFTER run below uses a scratch script of the same
shape (the repo's `gate` fixture, the real `main()`, a throwaway repo with a bare remote `../origin.git`,
`HOME` and git config isolated), kept outside the repo.

**AFTER** (2026-11-09, HEAD `7503935d`; same 11 forms, gate verdict per mode, then the same command
line run for real in `bash -c` and `zsh -c` in the throwaway worktree: first with no gate (control),
then only if the `[admin]` gate allowed it; "landed" means `refs/heads/feat/t900-x` exists on the bare
remote afterwards):

```
2026-11-09T02:28:34Z  'v=push; git $v origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'g=git; $g push origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'v=pu; git ${v}sh origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'git {p..p}ush origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  "git $'push' origin feat/t900-x"
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  "$'git' push origin feat/t900-x"
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:34Z  'env -i git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'timeout 20 git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'nice git "push" origin feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'bash -c \'git "push" origin feat/t900-x\''
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
2026-11-09T02:28:35Z  'git send-pack ../origin.git feat/t900-x'
    gate: none=ALLOWED [auto]=BLOCKED [admin]=BLOCKED   control (no gate) landed: bash=True zsh=True   with gate [admin] landed: bash=False zsh=False
```

Tests that were red now pass (2026-11-09): `python3 -m pytest .claude/hooks/tests/test_gate_hidden_verbs.py .claude/hooks/tests/test_slot2b_brace_glob.py -q -p no:cacheprovider` -> `414 passed in 5.76s`.
With no tag the 11 forms stay ALLOWED on purpose: the hidden-verb check is an auto-mode rule
(`hidden_git_verb`, requirement (a) says "under `[auto]` and `[admin]`"). The guide's AC 1 phrase "still
blocked with no tag" does not match that requirement text or the gate's design; the tests pin "no tag, no
change" (`test_row1_with_no_tag_the_hidden_forms_behave_as_before`). The Supervisor may decide otherwise.

**DELTA**: Under `[auto]` and `[admin]` the gate now refuses all 11 hidden-verb forms that used to push for real, a `git merge` option value is no longer read as the branch, and slot 2b no longer files a call whose brace or glob reaches outside the worktree.

**WITNESS**: `memory/event-trace/T296.jsonl` (hash-chained, written by the trace hook, not by the agent): the first run's spawn at 2026-11-08T15:19:03Z, this resume's Bash calls on 2026-11-09 (the 19 mutation runs, the full suite and the AFTER capture, last record 2026-11-09T02:28:36Z). The Supervisor confirms it from that file at Stage 4.
