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

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]
