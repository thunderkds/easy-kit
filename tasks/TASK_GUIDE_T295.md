# TASK_GUIDE — T295: `[admin]` merge and push refuse repo config and hooks that can run code (allowlist)
**Date**: 2026-11-08
**Complexity Level**: C3
**Risk Level**: High
**Priority**: P1
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

User, 2026-11-08: *"do all the jobs pls"* (the open follow-ups after T291-T293 were merged). Evidence: `tasks/GATE_HUNT_2026-11-08.md`, an independent hunt of the merge gate and slot 2b. Finding P1-2: the `[admin]` gate refuses repo config and hooks by a deny list (`ADMIN_DENY_CONFIG`, `ADMIN_HOOKS` in `.claude/hooks/pre_bash_block_unsafe_merge.py`), and the list misses keys that run code or send data elsewhere: `merge.<d>.driver`, `filter.<f>.smudge`, `filter.<f>.clean`, `diff.<d>.textconv`, `diff.external`, `gpg.program`, `core.editor`, `credential.helper` set to a path, `http.proxy`, plus the hooks `post-index-change` and `pre-auto-gc`. A merge driver also lets `main` differ from the tree the gate checked, so the `main` push check is defeated. This is the class that T284 round 3 fixed with a longer deny list; a longer deny list fails again, so this task changes the rule to an allowlist.

**Restated intent**:
> For an `[admin]` merge or push, the gate reads the repository config (local and per-worktree) and the hook directory, and allows the command only when every config key is on a short allowlist of keys that cannot run code or reach another host, and no hook file is executable (except `.sample` files). The gate also refuses a repository whose `.gitattributes` or `.git/info/attributes` has a line with `merge=`, `filter=` or `diff=`. A chained read-only git command that can run a textconv, clean filter or external diff (`git status`, `show`, `diff`, `log`) is refused; `cd <dir> &&` stays. Everything the T284 gate already allows with a safe repo still works.

**Out of scope** (what this task explicitly does NOT do):
- Weakening any T284 refusal that exists today (the allowlist must be at least as strict)
- Reading user-global or system git config (they stay trusted and unread, as `### Admin tag` says)
- Changing `[auto]` behaviour: `[auto]` alone still never merges or pushes
- Fixing the hidden-verb, `--message` and slot 2b findings (T296) or the heredoc finding (T294)

**Requirement Refs**: None — kit-internal; follows the T283 spike report.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "let do as your recommend", 2026-11-08, on the T283 report's ranked list)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` and are fully covered by the Acceptance Criteria above (none cited)

---

## Dependencies & Reachability

**Depends on**: None (T294 and T296 edit other lines of the same file; merge in order, resolve by hand)

**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` (`ADMIN_DENY_CONFIG`, `ADMIN_HOOKS`, the repo-state check for an `[admin]` merge or push, `SAFE_GIT_OPTIONS` chain rule)

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The repo-config check is an allowlist: a key not on the list is refused with a message naming the key. The list is written in one constant with a comment per entry saying why that key cannot run code. Start from: `core.repositoryformatversion`, `core.filemode`, `core.bare`, `core.logallrefupdates`, `core.ignorecase`, `core.precomposeunicode`, `core.autocrlf`, `core.safecrlf`, `remote.origin.url` (equals fetch url, as today), `remote.origin.fetch`, `branch.<b>.remote`, `branch.<b>.merge`, `user.name`, `user.email`. The agent may add a key only with a one-line reason and a test; it may not add any key from the list in the finding | Requirement |
| 2 | Negative: each of these planted repo configs makes an `[admin]` merge or push BLOCKED: `merge.<d>.driver`, `filter.<f>.smudge`, `filter.<f>.clean`, `filter.process`, `diff.<d>.textconv`, `diff.external`, `gpg.program`, `commit.gpgsign`, `core.editor`, `core.askPass`, `core.pager`, `sequence.editor`, `credential.helper=/abs/prog`, `credential.helper=cache`, `http.proxy`, `http.sslCAInfo`, `submodule.<n>.update=!cmd`, `merge.defaultToUpstream`, and every key T284 already refuses | Requirement |
| 3 | Hooks: any file in the hooks directory that is executable and not a `.sample` file BLOCKS (all 28 git hook names and any other name); a non-executable file and a `.sample` file do not. The old named list stays as the message text only | Requirement |
| 4 | Attributes: a `.gitattributes` in the worktree or `.git/info/attributes` with a line holding `merge=`, `filter=` or `diff=` BLOCKS an `[admin]` merge; a line with other attributes (for example `text`, `eol=lf`, `binary`, `-diff`) does not | Requirement |
| 5 | Chained commands: `git status`, `git show`, `git diff`, `git log` chained with an `[admin]` merge or push BLOCK (they run textconv, filters or external diff); `cd <dir> &&` alone is allowed; a lone `git merge <branch>` and a lone `git push origin <branch>` in a clean repo stay allowed | Requirement |
| 6 | The `main` push check no longer trusts a merge driver: with the planted `merge.<d>.driver` of the finding the push is BLOCKED by the config rule, and a test also runs `_main_push_refusal` on a tree that a driver changed and shows it is refused | Requirement |
| 7 | `docs/claude-md/tracks.md` `### Admin tag` item 2 states the allowlist rule and its short list, the Known-limits bullet added on 2026-11-08 loses the P1-2 parts, and `AGENTS.md` and `site/` text stay correct (LR-0005) | stale-text rule |
| 8 | `merge_gate_guard.AUTHORISED_TASKS` gains `T295` (the Supervisor signs it off) | tripwire |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

> The agent writes the tests first and sees them fail. The tests must be able to fail: every guard gets one mutation control that changes bytes and turns a test red (LR-0003).

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Planted config (one test per key in the list of row 2) with an otherwise valid admin merge | BLOCKED, message names the key | gate test through the `gate` fixture with a real throwaway repo |
| 2 | Executable `post-index-change`, `pre-auto-gc`, `prepare-commit-msg` and an unnamed executable hook | BLOCKED | gate test |
| 3 | `.gitattributes` with `* merge=x`, `*.png filter=x`, `*.md diff=x`; and one with `* text eol=lf` | first three BLOCKED, last allowed | gate test |
| 4 | Clean repo, `git merge feat/t900-x`, passed verify | ALLOWED (regression) | gate test |
| 5 | Real run in a throwaway repo, bash and zsh: the planted merge driver of the finding runs when the gate does not exist (control), and with the gate the command is refused before it runs | driver marker file absent after the gated attempt | script in the review file |
| 6 | Mutation: the allowlist check replaced by `return True` | Row 2 tests turn red | mutation control that changes bytes |
| 7 | Mutation: one key added to the allowlist that the finding names | its negative test turns red | mutation control that changes bytes |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests -q -k "admin or merge_gate or t284 or t210"
python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T295.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T295.md`.

---

## Approach

**Pattern reference**: the T284 repo-state checks and fixtures in `.claude/hooks/tests/test_admin_tag.py` and the review notes in `tasks/TASK_REVIEW_T284.md` (round 3). Read the config the same way the gate does today (local config and per-worktree config, case-insensitive section and key names, `[Remote "Origin"]` forms, `include.*`). Invert the check: parse every key, refuse unless it is on the list. Debate the one open choice with the three-Advocate rule if you are unsure (whether `core.pager` and `user.*` belong on the list); ask the Supervisor, not the user. Test with real throwaway repos and a bare remote, in both bash and zsh.

**Vital slice**: the allowlist, the hook rule and the attributes rule, with the planted-config negative tests
**Cut list**: no UI, no per-key setting, no change to the user-global config rule

---

## Edge Case Checklist

- [ ] Config keys are case-insensitive in section and key name but not in the subsection: `[Remote "Origin"]` is a different remote from `origin`
- [ ] `include.path` and `includeIf` stay refused (they can pull in any key)
- [ ] A key set twice, or set in the per-worktree config only (`extensions.worktreeConfig`)
- [ ] A symlinked `.git/hooks`, a symlinked hook file and a hooks directory set by `core.hooksPath` stay refused as today
- [ ] The gate reads the repository at hook time; a change between the check and the run stays a documented limit (say so)
- [ ] Pin-test pre-flight: the T284 admin tests, `test_merge_gate_t210.py`, `test_merge_gate_guard.py`, `test_agent_guide_dedup.py` and the tracks.md text pins are found and run before work starts
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: for each fact this task changes (flag, count, path, name, version), grep the repo for the old wording (README, `site/`, `docs/claude-md/`, comments, docstrings, `agents/`, board notes) (LR-0005)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| .claude/hooks/pre_bash_block_unsafe_merge.py | Allowlist, hook rule, attributes rule, chain rule |
| .claude/hooks/tests/test_admin_repo_allowlist.py (new) | Tests |
| .claude/hooks/tests/merge_gate_guard.py | Add T295 to AUTHORISED_TASKS |
| .claude/hooks/tests/test_merge_gate_guard.py | Repoint the pinned tuple |
| docs/claude-md/tracks.md | `### Admin tag` item 2 and Known limits |
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
