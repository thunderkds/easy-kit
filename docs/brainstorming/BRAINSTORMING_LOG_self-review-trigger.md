# BRAINSTORMING_LOG.md — self-review trigger
**Generated**: 2026-11-07
**Task / Context**: Stage 0 step Direction for T281 (planned). Supersedes FR-001 of `docs/prd/PRD_self-review.md`. Earlier log: `docs/brainstorming/BRAINSTORMING_LOG_self-review.md` (Path B, 2026-11-05).
**Skill**: `Skill({ skill: "brainstorming" })` — tier **Deep** (a safety rule of the doctrine changes; Risk Medium)

---

## The Problem Space

User, 2026-11-07: *"why I should call the step to review. You should thinking, brainstorming, or debate to make decision to improve or not, I will approve following your proposal"*.

Today the loop runs only when the user types `/self-review`. The user should not have to remember. The Supervisor should decide when an improvement is worth proposing, test the idea with a Debate, and bring a proposal. The user approves or rejects.

Kept as non-negotiable (from the earlier design): reviews-only input (FR-002); nothing new means no agent call (FR-003); at most 3 proposals (FR-006); citations checked by script (FR-004); the Supervisor never edits kit files, commits to `main`, merges or pushes for this (FR-008); nothing leaves the repo (NFR-003).

**Verified facts** (each checked against the file, 2026-11-07):
1. `skills/self-review/SKILL.md:4` has `disable-model-invocation: true`. The Supervisor cannot start the skill with the `Skill` tool until that line goes.
2. `docs/prd/PRD_self-review.md:46` FR-001 forbids any start but the user's `/self-review`. It must be amended; its "no hook, Stop hook or schedule" half stays.
3. Precedent: `learn` and `compact-advisor` are started by the Supervisor on its own judgment (`skills/learn/SKILL.md:3`, `skills/compact-advisor/SKILL.md:3`). No hook starts them.
4. `skills/self-review/scripts/self_review.py` (docstring, lines 8–9) counts only review files changed on `main`'s first-parent line since the watermark. New data therefore appears only when something merges.
5. `skills/resolve-question/SKILL.md:120` makes the Debate "auto mode only". Outside auto mode a Choice question goes to the user. The user now wants a Debate here in normal mode too.
6. `docs/claude-md/pipeline-stages.md` Stage 5 item 4 is the diff-driven memory pass, run right after a merge. That is when new review files reach `main`.
7. The earlier log ruled out unattended runs (Path C, headless child). A run the Supervisor starts inside a live session the user watches is not unattended.

## Questions for the User

1. Which path do you pick? (asked with the recommendation below.)

---

## Alternative Paths

### Option A — Supervisor starts it after a merge, with a cheap gate and a Debate (Recommended)
At Stage 5, right after the memory pass (item 4), the Supervisor runs `self_review.py pre`. Three gates stop it before any model call: nothing new; fewer than 3 new review files (a pattern needs 3 distinct tasks, FR-004); or the session is in auto mode. Otherwise: one miner, then `post`. For each proposal the Supervisor decides by Risk: a change that touches guardrails or hooks gets a Debate (2 Advocates); a low-risk wording change it decides alone and logs why. The user then sees at most 3 proposals, each with a recommendation, and answers approve or reject. Approved ones become a Kanban task as today.
- **Pros**: copies the `learn` / `compact-advisor` pattern; costs nothing on most merges (two cheap gates); keeps every deterministic guard; the user never types a command.
- **Cons**: changes a rule the earlier design set on purpose; adds Debate cost (about 2 sub-agent calls per guardrail proposal); the Supervisor's judgment now decides the start, so a gate must be in the script, not only in text.
- **Adversarial — why it might fail**: the Supervisor runs it after every merge and the user feels nagged (mitigated by the 3-file gate and by `rejected` = never again); a fix task's own review feeds the next run (the register's `task_id` exclusion, edge case 1, already handles it); the Debate rubber-stamps (Advocates work alone, the third favours the smallest change at Risk High, and the user still approves).

### Option B — A hook counts new reviews and reminds the Supervisor
`post_bash` merge hook prints one line, "N new review files since the watermark; consider self-review". The Supervisor reads it and decides.
- **Pros**: deterministic trigger; nothing is forgotten.
- **Cons**: FR-001 forbids a hook from starting it (a reminder is not a start, but it touches `.claude/hooks/`, listed as "must not touch" in the earlier log); the hook runs on every git operation, so its cost and test surface grow; the start is still the Supervisor's judgment, so it adds a part without adding safety.
- **Adversarial**: a hook that reads git history on every merge can slow the merge gate; an error in it blocks a merge (the gate family fails closed).

### Option C — Keep `/self-review` manual, and the Supervisor only reminds
After a merge the Supervisor says "4 new reviews; run /self-review if you want".
- **Pros**: smallest change (one doctrine line, no skill change); keeps the old guard exactly.
- **Cons**: the user still has to call it. It does not meet the request.
- **Adversarial**: a reminder is ignored; the loop is never run; the recurring defects stay unfixed.

---

## 50% Rule Check
- Option A with the least code: remove one frontmatter line, add one doctrine rule in Stage 5, add one script status (`too-few`) and one Debate rule in `SKILL.md`. No new script, no hook, no new file format.
- The 3-file gate is free: FR-004 already needs 3 distinct tasks, so a run with fewer cannot produce a pattern.
- Cut: a threshold setting (fixed at 3), a scheduler, a report format change, a new register state.

## Recommended Path
**Option A.** The Supervisor starts self-review after a merge, only when the script says at least 3 new review files exist and the session is not in auto mode. It runs one miner, debates guardrail-touching proposals, and brings at most 3 proposals with its recommendation. The user approves or rejects. It never edits kit files itself.

Auto mode: the Supervisor does not start it (it cannot ask you). It names the waiting count under `Not done:`.

## Surgical Scope
**Should touch**: `skills/self-review/SKILL.md` (remove `disable-model-invocation`; add "who starts"; add the Debate rule), `skills/self-review/scripts/self_review.py` (a `too-few` status; no watermark change on it), `tests/test_self_review.py` (the new status, mutation controls), `docs/prd/PRD_self-review.md` (amend FR-001, add US-004), `docs/claude-md/pipeline-stages.md` (Stage 5 item 4: one line), `docs/claude-md/tracks.md` (auto mode row 19 or a new row: not started in auto mode), `skills/resolve-question/SKILL.md` (a note that `self-review` may call the Debate in normal mode; Debate cap counted per run), the pins that reference these files.
**Must not touch**: `.claude/hooks/**`, `hooks/hooks.json`, `.claude/settings.json`, `memory/event-trace/`, `memory/self-review/register.md` (written by runs only).

## Edge Case Checklist for TASK_GUIDE
1. Fewer than 3 new review files: status `too-few`, no miner, watermark unchanged, so the files keep counting for the next run.
2. Auto mode: no start; one line under `Not done:`; never ask.
3. The merge that carries the fix task of an approved proposal: its review is excluded by the register `task_id` rule (earlier edge case 1).
4. Debate output is not a review record and is never read by `pre` (FR-002).
5. User rejects: the row is `rejected`, never proposed again; the Supervisor must not re-run to re-ask.
6. User ignores or says nothing: the row stays `open` and is listed in one line next run; it is not proposed again as new.
7. Two sessions merge at once: the register write stays atomic (existing); a second `pre` sees the first run's watermark.
8. The Supervisor tries to start it from a hook or a schedule: still forbidden; FR-001's second half stays and a test pins it.
9. Debate cost: at most 1 Debate per proposal and at most 3 per run; a 4th question goes to the user (existing cap).
10. `SKILL.md` stays under the Codex 8 KB cap (prompt text stays in `references/`).
11. Site and docs text: after this lands, the docs diagram (T278) and the home step (T280) change from "You start it" to "The Supervisor proposes, you approve". Stale-reference grep for `/self-review`, "You start it", "Optional".

## Next Actions
- Stage 0 step Grilling: `grill-with-docs` `mode=requirement` on the amended PRD (FR-001 reworded, US-004, an FR for the `too-few` gate and one for auto mode).
- Stage 2: two tasks. T281-a: script `too-few` status and tests (C1, Low). T281-b: skill, PRD, Stage 5 and auto-mode text, Debate rule (C2, Medium — a safety rule changes; Debate required at Risk Medium).
- After both land and verify: rewrite the T278 docs diagram and release the held T280 with matching text.

## User Selection
**Selected 2026-11-07: Option C** (user, in the question dialog: "C: Keep /self-review, Supervisor only reminds"). Option A (recommended) was not chosen. Consequences: FR-001 stands (the user starts the loop); `disable-model-invocation` stays; no Debate, no script change. The reminder is one doctrine line: after the Stage 5 memory pass the Supervisor runs `self_review.py pre` (no model call; its only write is to mark register rows `fixed` once their fix task has merged) and, when it says `ready` with at least 3 files, tells the user in one line to run `/self-review`. The held T280 home step and the T278 docs diagram stay true. Option A can come later as its own task.
