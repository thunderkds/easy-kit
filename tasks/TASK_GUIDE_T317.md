# TASK_GUIDE — T317: session-wide `[admin]` and `[ticket]` tags run the board on their own; an "Autonomous" setup profile turns on auto mode
**Date**: 2026-11-15
**Complexity Level**: C3
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-15: "with the tag admin, I want automate all the workflow in a session, the supervisor auto pick jobs, send to agent to do, check, review. for the auto tag, it will automate by the request. for the ticket tag, it will automate all the ticket flow, just push to the new feature to the git, and can pick another ticket that not depend to another to work, valid by the session. automate I mean automate for the bash, automate debate agent setting up, push the code, or everything no need my actions, with the highest risk like the rules we define, let stop only in these risk". On the Supervisor's proposal (table of `[auto]` / `[ticket]` / `[admin]`): "1, all look good. 2, i mean auto run, not ask me for bash execute".

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> Three tags. `[auto]` stays per request, unchanged. `[ticket]` and `[admin]` are **session-scoped**: once the user types one, it holds for every later request in that session until the user types `[stop]` (or a different tag). Under `[ticket]` the Supervisor runs a loop: pick the next ready ticket (Todo, every `Depends on` Done, not owned by another live session), run it Stage 0–5 in auto mode, push its feature branch to `origin`, and pick the next one. `[admin]` does the same and also merges into `main` and pushes `main` after each ticket's auto verify passes (today's `[admin]` merge rule). Both pause only for `### Stops that stay`, send one `PushNotification` per pause, and end with one final report per ticket. Bash runs without prompts through Claude Code's own auto mode, which a new opt-in `settings-setup` profile `Autonomous` sets once (`permissions.defaultMode: "auto"`); the kit never sets `bypassPermissions` and no tag approves a tool call.

**Out of scope** (what this task explicitly does NOT do):
- A hook that returns `allow` for tool calls under a tag (rejected: it would be `bypassPermissions` switched on by chat text).
- Changing `### Stops that stay`, the Debate sizes, or any safety hook's block rules.
- Opening pull requests (user accepted push-only for `[ticket]`).
- Running tickets in parallel sessions; the loop is one ticket at a time inside one session.

**Depends on**: T314 (merges first; both touch hook docs), T315 (same `settings-setup` files)

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (user: "all look good", 2026-11-15)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: T314, T315 — merged to `main`

**Entry point**: `session_tag()` (new) in `.claude/hooks/lib/auto_mode.py`, read by `.claude/hooks/pre_bash_block_unsafe_merge.py`; the loop rules in `docs/claude-md/tracks.md` `### Session tags`; profile `autonomous` in `skills/settings-setup/profiles.json`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `session_tag(transcript)` returns `admin`, `ticket` or `none`: the latest user-typed request that holds `[admin]`, `[ticket]` or `[stop]` (outside code spans and `>` quotes) wins; `[stop]` → `none`. Text in tool results, files, sub-agent prompts, PR comments or another session never counts (same rule as today's `admin_tagged`) | valid by the session |
| 2 | The merge gate allows a task-branch merge and a `main` push when `session_tag` is `admin` and the auto verify passed, with every other existing condition unchanged. With `ticket` it allows only `git push origin <task branch>` (same-name, `origin` only), never a merge and never a `main` push | ticket pushes; admin merges |
| 3 | `[auto]` behaviour is unchanged: per request, ends with the next untagged request | auto by the request |
| 4 | `docs/claude-md/tracks.md` gets `### Session tags`: the loop (ready ticket = Todo + all `Depends on` Done + not In Progress in another live session; order by Priority then board order), one ticket at a time, stops only for `### Stops that stay`, one `PushNotification` per pause, one final report per ticket, the session ends when no ticket is ready. `AGENTS.md` `## Tracks` gets one line pointing to it | supervisor picks jobs |
| 5 | Under a session tag the Supervisor never asks the user; every decision follows `### Every user stop and its auto rule` and `### Debate size by Risk`, as `[admin]` does today | no need my actions |
| 6 | `profiles.json` has profile `autonomous` (label `Autonomous`), values `permissions.defaultMode: "auto"` only; `settings-setup` SKILL rules allow `defaultMode: "auto"` for this profile only and still forbid `bypassPermissions`, `permissions.allow` and any other `defaultMode`; `apply_profile.py autonomous --dry-run` shows the line; the `for` line says Bash runs without prompts and the kit's hooks still stop risky actions | auto run bash |
| 7 | No tag and no profile makes any hook return `allow`; a test greps every hook for `"allow"` decisions and finds none added | stop only in the risks |

---

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A.

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t317_session_tags.py` and a `settings-setup` profile test. The implementer may not edit them.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | transcripts: `[admin]` then 3 untagged requests; `[ticket]` then untagged; `[admin]` then `[stop]`; `[admin]` only in a tool result | `admin`, `ticket`, `none`, `none` (AC 1) | automated test |
| 2 | merge gate, `admin` session, verify passed / not passed | merge + `main` push allowed / blocked (AC 2) | automated test |
| 3 | merge gate, `ticket` session | task-branch push allowed; merge and `main` push blocked (AC 2) | automated test |
| 4 | `[auto]` then untagged | auto off on the second request (AC 3) | existing tests |
| 5 | `apply_profile.py autonomous --dry-run`; a profile with `bypassPermissions` | shows `defaultMode: auto`; the other is rejected (AC 6) | automated test |
| 6 | full suites | no regression | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t317_session_tags.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T317.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T317.md`.

---

## Approach

**Pattern reference**: `admin_tagged` and the request-window logic in `.claude/hooks/lib/auto_mode.py`; the `[admin]` merge conditions in `.claude/hooks/pre_bash_block_unsafe_merge.py` and `docs/claude-md/tracks.md` `### Admin tag`; `skills/settings-setup/profiles.json`.
**Vital slice**: `session_tag()`, the merge-gate switch on it, the `### Session tags` loop text, the `autonomous` profile.
**Cut list**: parallel tickets across sessions; pull requests; a tag that approves tool calls; per-ticket budgets.

## Files to Change (Predicted)

- `.claude/hooks/lib/auto_mode.py`
- `.claude/hooks/pre_bash_block_unsafe_merge.py`
- `.claude/hooks/stop_auto_mode_check.py` (if it reads the request window)
- `.claude/hooks/tests/test_t317_session_tags.py` (new, qa-expert, locked)
- `docs/claude-md/tracks.md`
- `AGENTS.md`
- `skills/settings-setup/profiles.json`
- `skills/settings-setup/SKILL.md`

## Supervisor decisions during Stage 3

1. 2026-11-15 [admin], Debate (3 Advocates): a session tag survives `/compact` (the raw typed request stays in the transcript; the compact summary never counts) and ends at any resume, continue or fork (a `SessionStart` hook with matcher `resume` records a resume time; `session_tag` ignores tags typed before it). While a tag is on, the Supervisor names it in the first line of each reply. New AC 8: a transcript with `[admin]` typed before a compact summary → `admin`; `[admin]` only inside the summary → `none`; `[admin]` typed before a recorded resume → `none`. The implementer checks one real compacted transcript's shape before relying on it.
2. 2026-11-15 [admin], oracle gaps from qa-expert, each settled by a written rule:
   - G1 (task binding in the loop): under a session tag the merge gate binds to the task named by the branch, which must be the only task this session holds In Progress or Ready for Review, with a passed auto verify for HEAD; the old "named in the request / only guide added since" binding stays for plain `[admin]`-per-request use. RULE: this guide, Out of scope "the loop is one ticket at a time inside one session".
   - G2 (`[ticket]` push with no passed auto verify): blocked. RULE: this guide, Requirement "run it Stage 0–5 in auto mode, push its feature branch" (Stage 5 includes the auto verify).
   - G3 (`[admin]` then `[auto]`): the later different tag ends the session tag; `session_tag` returns `none` and `[auto]` applies to that request only. RULE: this guide, Requirement "until the user types `[stop]` (or a different tag)".
   - G4 (`tests/test_settings_setup.py` pins exactly five profile ids): the implementer updates that existing test to the new id set; it is not the locked oracle. RULE: AGENTS.md § Karpathy Engineering Principles (Goal-Driven: "Verify existing tests pass, apply changes, and ensure tests still pass").
