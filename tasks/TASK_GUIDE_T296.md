# TASK_GUIDE — T296: Merge gate: hidden git verbs, `merge --message`, and slot 2b brace and glob escapes
**Date**: 2026-11-08
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P2
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt. Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Read `memory/codebase-map.md`
6. Read `tasks/GATE_HUNT_2026-11-08.md` (the findings this task fixes) and `docs/claude-md/untrusted-content-boundary.md`
7. Read `memory/learning-records/LR-0003-tests-that-cannot-fail.md`, `LR-0004-pin-tests-hit-later-tasks.md`, `LR-0005-stale-text-after-change.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-08: *"do all the jobs pls"* (the open follow-ups after T291-T293 were merged). Evidence: `tasks/GATE_HUNT_2026-11-08.md`, an independent hunt of the merge gate and slot 2b. Findings P2-1, P2-2, P2-3 and P3-1..P3-4. P2-1: hidden verb forms such as `v=push; git $v origin br`, `g=git; $g push`, `git ${v}sh`, `git {p..p}ush`, `git $'push'`, `$'git' push`, `env -i git "push"`, `timeout 20 git "push"`, `nice git "push"`, `bash -c 'git "push"'` and `git send-pack` are ALLOWED and really push under `[auto]` and `[admin]`. P2-2: `git merge --message feat/t900-x` makes the gate read the message as the branch. P2-3: brace expansion and globs (`> {.,..}/f`, `--output={.,..}/d`, `pytest {..,.}/main/tests`, `pytest mt*`) make slot 2b file a call under a task while it writes or runs outside the worktree.

**Restated intent**:
> (a) Under `[auto]` and `[admin]` the gate refuses any command in which a `git` word or the git verb is not a plain literal word: any `$`, backtick, brace expansion, quote or backslash in the git word, in the verb position, or in a `timeout`, `nice`, `env` or `command` wrapper chain before it; and for an `[admin]` command the only git verbs that may appear are `merge`, `push` and the read-only `cd`-free forms the gate already allows (everything else, including `send-pack`, is refused). (b) The merge option parser knows every `git merge` option that takes a value (`--message`/`-m`, `--file`/`-F`, `-s`/`--strategy`, `-X`/`--strategy-option`, `-S`/`--gpg-sign`, `--cleanup`, `--log`) so no value is read as the branch. (c) Slot 2b refuses to file a Bash call when any token holds `{`, `}` or an unquoted glob character, and it honours a backslash the way the shell does. (d) The doc and message drift of P3-4 is fixed.

**Out of scope** (what this task explicitly does NOT do):
- The heredoc scanner (T294) and the repo config and hook allowlist (T295)
- A full shell parser: an allowlist of literal words is enough, and a doubt means refuse
- Changing what slot 2b files for the shapes the hunt classed as safe or as inside the documented limit

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None (T294 and T295 edit other lines of the same file; merge in order, resolve by hand)

**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` (`OBFUSCATION`, `SHELL_WRAPPERS`, `hidden_git_verb`, `MERGE_OPTIONS_WITH_ARG`, `SAFE_GIT_OPTIONS`, branch-push rule) and `.claude/hooks/lib/task_context.py` (slot 2b `_escapes`, token checks)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Negative: each hidden-verb form of the finding is BLOCKED under `[auto]` and `[admin]` and with no tag unchanged, allowed as before (amended 2026-11-09 by the Supervisor after a 3-Advocate Debate, see `tasks/TASK_REVIEW_T296.md` Auto decisions, item 1) (the force push and plain push are blocked for `[auto]` already): `v=push; git $v origin br`, `g=git; $g push origin br`, `git ${v}sh origin br`, `git {p..p}ush origin br`, `git $'push' origin br`, `$'git' push origin br`, `env -i git "push" origin br`, `timeout 20 git "push" origin br`, `nice git "push" origin br`, `bash -c 'git "push" origin br'`, `git send-pack ../origin.git br` | Requirement |
| 2 | Allowed as today: `git push origin feat/t900-x`, `git -C <dir> merge feat/t900-x`, `git --no-pager merge feat/t900-x`, `cd <dir> && git merge feat/t900-x` in a clean repo with a passed verify under `[admin]` | no regression |
| 3 | Merge parser: `git merge --message feat/t900-x`, `-m feat/t900-x`, `--file feat/t900-x`, `-F feat/t900-x`, `-s ours feat/t900-x`, `-X theirs feat/t900-x`, `--cleanup=strip feat/t900-x` each yields the right branch (or no branch, and then the gate refuses); a test with a real repo and `merge.defaultToUpstream=true` shows `--message feat/t900-x` can no longer make the gate check the wrong branch | Requirement |
| 4 | Slot 2b: calls that hold a brace, `{`, `}` or an unquoted `*`, `?`, `[` in any token are not filed: `echo hi > {.,..}/f`, `git diff --output={.,..}/d`, `pytest {..,.}/main/tests`, `pytest mt*` (symlink to main). Quoted globs (`pytest -k "a*"`) and the normal `cd <dir> && pytest tests/test_x.py` stay filed | Requirement |
| 5 | Slot 2b backslash: `cd WT && echo ok \` + newline + `pytest`, `cd WT && echo done\; pytest` and `cd WT && echo "a\" && pytest && echo \"b"` do not count as a test run (the trace gate and slot 2b read the command the way shlex and the shell do) | Requirement |
| 6 | P3-2: a call that renames a branch (`git branch -m`, `git checkout -b`, `git switch -c`) is not filed under a task by the branch it ends on; a test pins it and `docs/claude-md/tracks.md` Known limits states the rule. P3-3: a branch push to a remote whose URL differs from the repository's `origin` (after `cd <clone>`) is refused for any branch, not only `main` | Requirement |
| 7 | P3-4: `docs/claude-md/tracks.md` `### Admin tag` item 2 no longer says `rev-parse` may stay in a chain unless the code allows it (align text and code, say which), and the refusal message for `git log --output=`, `git diff --output=` and `git show --ext-diff` names the real reason. The Known-limits bullet added on 2026-11-08 loses the parts this task and T294 and T295 fix (LR-0005) | stale-text rule |
| 8 | `merge_gate_guard.AUTHORISED_TASKS` gains `T296` (the Supervisor signs it off); a corpus test over the old gate cases keeps every old result except the shapes of rows 1, 3, 4, 5 | tripwire; no regression |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Hidden-verb forms (11) under no tag, `[auto]`, `[admin]` | BLOCKED under `[auto]` and `[admin]`; with no tag unchanged (allowed as before) — amended 2026-11-09 by the Supervisor after a 3-Advocate Debate (`tasks/TASK_REVIEW_T296.md` Auto decisions, item 1) | gate test through the `gate` fixture |
| 2 | Real run in a throwaway repo with a bare remote, bash and zsh, for three of the forms, with the gate and without it | Without the gate the push lands (control); with the gate it is refused | script in the review file |
| 3 | Merge options with a value | Right branch or refusal | unit test with a real repo |
| 4 | Slot 2b brace and glob shapes (5) and backslash shapes (3) | Not filed / not counted | unit test through `task_context` |
| 5 | Mutation: `hidden_git_verb` returns False | Row 1 tests turn red | mutation control that changes bytes |
| 6 | Mutation: `--message` removed from `MERGE_OPTIONS_WITH_ARG` | Row 3 test turns red | mutation control that changes bytes |
| 7 | Mutation: the brace refusal removed in slot 2b | Row 4 tests turn red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or slot or task_context or hidden"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T296.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T296.md`.

---

## Approach

**Pattern reference**: `hidden_git_verb`, `OBFUSCATION` and `SHELL_WRAPPERS` in `.claude/hooks/pre_bash_block_unsafe_merge.py`, and `_escapes` and the token loop of slot 2b in `.claude/hooks/lib/task_context.py` (T287). The lesson of T287 holds: an allowlist of literal shapes beats a longer list of bad shapes (memory/learnings.md, zsh `chdir`). For the verb, accept only a literal word made of letters and `-`; refuse the command otherwise. Check each shape with a real throwaway repo in both bash and zsh before you pin it.

**Vital slice**: rows 1, 3 and 4 (the three P2 findings) with the real-run script
**Cut list**: P3-1..P3-3 are in scope only as the small tests and one-line rules listed in rows 5 and 6; if one grows past a small change, write it in the review file as a follow-up

---

## Edge Case Checklist

- [ ] `git` inside a quoted argument of `echo` or a commit message must not trigger a refusal that blocks normal use (`git commit -m "git push later"` is not an `[admin]` merge or push command, so the rule applies only to commands that the gate already treats as merge or push or that hold a write verb)
- [ ] `env` with options and assignments (`env -i A=b git push`) is a wrapper; `command`, `exec`, `nohup` too
- [ ] Quoted spans are removed before the verb check today (the cause of the miss): decide the order and pin it with the shapes
- [ ] Pin-test pre-flight: the T284 admin tests, T287 slot 2b tests (`test_stop_attribution_t287.py`, task_context tests), `test_merge_gate_t210.py`, `test_merge_gate_guard.py` and the tracks.md text pins are found and run before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/pre_bash_block_unsafe_merge.py | Verb check, wrappers, merge options, remote rule |
| .claude/hooks/lib/task_context.py | Slot 2b token rules |
| .claude/hooks/tests/test_gate_hidden_verbs.py (new) | Tests |
| .claude/hooks/tests/test_slot2b_brace_glob.py (new) | Tests |
| .claude/hooks/tests/merge_gate_guard.py | Add T296 to AUTHORISED_TASKS |
| .claude/hooks/tests/test_merge_gate_guard.py | Repoint the pinned tuple |
| docs/claude-md/tracks.md | `### Admin tag` and Known limits |
| Pre-existing pin tests | Grep `.claude/hooks/tests/` and `tests/` for the changed strings and paths; always check `test_agent_guide_dedup.py`, `test_vital_slice.py`, the site pins and the memory budget tests. Repoint, narrow or escalate each (LR-0004) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/settings.json` | No wiring change |
| `PROJECT_KANBAN.md`, `memory/**` | Supervisor-only writes |
| The 'only the hook writes the verify row' logic | Security boundary |
| `PROJECT_KANBAN.md`, `memory/**`, `.claude/settings.json` | Supervisor-only writes; hook wiring is unchanged unless this guide says so |

---

## Test Plan

Write the tests for the Acceptance Criteria first and see them fail. Implement. Run the verification command and the full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` (bare `pytest` skips the hidden hook tests). Run each mutation control, paste the red output, restore, and paste the green output.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium/High risk)
- [ ] Lint passes
- [ ] `PROJECT_KANBAN.md` updated by the Supervisor
