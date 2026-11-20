# TASK_GUIDE — T341: Extended track: the Supervisor writes the code, a fresh reviewer spawn is required at merge
**Date**: 2026-11-20
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
6. Read `memory/codebase-map.md` (C3, multi-file)

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-20, on the lean-kit proposal (`docs/brainstorming/BRAINSTORMING_LOG_lean-kit.md`, option B "flip the split", step 1 of the staged rollout the Debate chose): "should start the enhance now" — then "run by automate, [admin]".

**Restated intent**:
> On the extended track the Supervisor writes the code itself (worktree, test first), as the minimal track already does. Independence moves to one fresh-context reviewer spawn per extended task, and the merge gate — not prose — refuses the merge until a hook-written trace record proves that reviewer ran on the exact code being merged.

**Out of scope** (step 2 of the rollout, a later task):
- Advocate counts (`### Debate size by Risk`, `ADVOCATES_BY_RISK`, the `DEBATED` ≥2 rule, D9/D10) stay as they are.
- `experiments/kit-arms/` and any other lean-kit Part 1 item.
- Codex/Cursor projections beyond keeping `AGENTS.md` correct.
- A verdict check: the gate proves a review ran, not what it found (findings stay in `TASK_REVIEW_<ID>.md`).

**Requirement Refs**: none in `PRD.md` (kit doctrine change); source is the brainstorming log above and DDR-0004's own "Revisit if" clause (`docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md:93-96`).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed — Supervisor, 2026-11-20, under session `[admin]` (user's lean-kit Part 2 choice; Debate of 3 Advocates, `docs/brainstorming/BRAINSTORMING_LOG_lean-kit.md` `## Questions Log`)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary (extended track, minimal track, merge gate, trace, anchor, Advocate)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] No `PRD.md` refs (kit doctrine); the AC cover the restated intent in full

---

## Dependencies & Reachability

**Depends on**: None
**Entry point**: `trace_shows_review`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `AGENTS.md` Hard-Stop Gate 1 keeps its title `1. **No TASK_GUIDE = no work.**` and the "guide before any code" rule; its last sentence no longer forbids the Supervisor to write code. It says: on the extended track the Supervisor writes the code itself in the task's worktree, test first; an implementer spawn only for 2+ independent tasks at once or a C3 task too big for one context; one fresh-context reviewer spawn per extended task, required by the merge gate. The `## Stage 0–5` Stage 3 and Stage 4 lines match. | Supervisor writes the code; reviewer spawn |
| 2 | `docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md` exists (DDR format of 0004), supersedes DDR-0004, records the evidence (floor ~47k vs 15.7k, the 2026-11-20 replay, kit-arms) and the user's choice; DDR-0004's `**Status**` reads `Superseded by DDR-0011`. | reverses DDR-0004 |
| 3 | `docs/claude-md/pipeline-stages.md` Stage 3 and Stage 4 describe the new split and the reviewer spawn's exact shape: `Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: … })`, prompt first line the fixed `REVIEWER_PROMPT_PREFIX`, then `Task ID: <ID>`, then `Commit: <40-hex>` (the commit reviewed), all within the first 300 characters (`post_tool_trace.py` `MAX_SUMMARY_LEN`); the prompt carries the diff range and the guide path only, never the Supervisor's reasoning; the reviewer runs code-review and, at Risk Medium/High, security-review, and writes its findings to `tasks/TASK_REVIEW_<ID>.md`. | reviewer spawn, fresh context |
| 4 | The merge gate refuses `git merge <task branch>` (and the narrowed task-branch push it already judges per task) of a task that is extended track and in scope (AC 6), unless `trace_shows_review(<ID>, <tip>, <dir>)` is true. The block line names the task and gives the remedy (spawn `Reviewer: <ID>` on the tip commit, with the session's active-task state set to `<ID>`). | merge gate, not prose |
| 5 | `trace_shows_review` is true only when some trace record in `memory/event-trace/*.jsonl` (the task's own file first; a record is the task's by its description, not by its file) satisfies all of: `is_reviewer_call(record, <ID>)` (tool `Agent`, description exactly `Reviewer: <ID>`, prompt starts with `REVIEWER_PROMPT_PREFIX` and holds `Task ID: <ID>` and `Commit: <40-hex>` inside the summary); not an error, and completed as far as the record tells (spike the real record shape first: see Edge cases); its chain hash and anchor check out, read the way `scripts/verify_trace.py` reads them; the named commit is an ancestor of the tip, and `git diff --name-only <commit> <tip>` lists only `tasks/TASK_REVIEW_<ID>.md`, `PROJECT_KANBAN.md`, `tasks/MINIMAL_LOG.md` and `memory/*.md` other than `memory/MEMORY.md`. Any doubt (git error, unreadable trace, bad hash, missing anchor, unknown commit) is false. | exact code being merged; hook-written proof |
| 6 | Scope: a task is extended track when `tasks/TASK_GUIDE_<ID>.md` exists at the branch tip, in the main checkout, or in any commit of `main..tip`. A task with no guide anywhere (minimal track) is never checked. No date cutoff and no exemption list: every extended-track task merged from now on is checked (Debate 2026-11-20, `## Questions Log`). The check runs per merged or pushed target (the branch the command merges or pushes), never inside the board-wide Ready-for-Review loop (`pre_bash_block_unsafe_merge.py` L2873), so a Ready-for-Review row of an already-merged task (T326, T327) blocks nothing new. | minimal track exempt; old tasks |
| 7 | `.claude/hooks/tests/merge_gate_guard.py` `AUTHORISED_TASKS` gains `T341` with a comment naming the rule (Supervisor sign-off under session `[admin]`, 2026-11-20); the gate commit subject names T341. | gate sign-off rule |
| 8 | `docs/claude-md/tracks.md` names the new merge-gate condition, and its `### Known limits` adds: the trace and anchor raise the bar and are not a proof (an agent's own Python can write a matching record, as for T148/T182). | honest limits |
| 9 | Negative: a merge is refused for each of — no reviewer record; description `Reviewer: T999` for task T998; prompt without the prefix; a commit not in the tip's history; a code file changed after the reviewed commit; a record whose hash does not match its anchor. Allowed for — the reviewed commit equals the tip; only a board, review-file or memory commit after it; a minimal-track branch with no guide; a merge of task A's branch while task B (already merged, no reviewer record) still sits in Ready for Review. Refused also for — a guide committed with a backdated `GIT_COMMITTER_DATE` (no date is trusted). | negative / boundary |
| 11 | Option B (user, 2026-11-20: "so B"): a new `SubagentStop` hook `.claude/hooks/subagent_stop_reviewer_done.py`, registered in `.claude/settings.json`, writes one record to the trace when a sub-agent ends whose spawn prompt (first line of its own transcript, read the way `.claude/hooks/lib/task_context.py` `_spawn_prompt` reads it) starts with `REVIEWER_PROMPT_PREFIX`, then `Task ID: <ID>`, then `Commit: <40-hex>`. The record: `tool_name` `"ReviewerDone"`, the task ID, the commit, the agent ID, filed in `memory/event-trace/<ID>.jsonl`, hash-chained and anchored the way `post_tool_trace.py` appends (`trace_chain`). Spike first: capture one real `SubagentStop` event (its field names) before writing the hook; do not guess. Never raises; exits 0; writes nothing for any other sub-agent. | the reviewer finished, not only started |
| 12 | `trace_shows_review` counts only a hook-written `ReviewerDone` record for the task and the commit (chain hash, link, anchor intact; commit an ancestor of the tip; only review-free files after it). An `Agent` spawn record alone, `async_launched` or `completed`, no longer counts. The block line's remedy names the spawn shape and says the record is written when the reviewer ends; it no longer asks for a foreground spawn. | finished review proven |
| 13 | Negative: refused for — a spawn record with no `ReviewerDone`; a `ReviewerDone` for another task or another commit; one with a bad hash or no anchor; one typed into the trace by hand (`echo >>`); a sub-agent that ends with a non-reviewer prompt writes nothing. Allowed for — a `ReviewerDone` on the tip, or on a commit followed only by review-free files. | negative / boundary |
| 14 | `docs/claude-md/pipeline-stages.md` Stage 4 step 0, `docs/claude-md/tracks.md` and DDR-0011 say: the spawn may run in the background; the merge gate counts the record the `SubagentStop` hook writes when the reviewer ends. `.claude/settings.json` gains only the `SubagentStop` entry (no other key changes). | doctrine matches the gate |
| 10 | Stale references: every live doc that says the Supervisor never writes implementation code on the extended track is updated (`AGENTS.md`, `docs/claude-md/pipeline-stages.md`, `docs/claude-md/tracks.md`, `agents/*.md`, `templates/`, `skills/*/SKILL.md`, `site/`), or listed in the review with the reason it stays (dated records under `tasks/`, `memory/`, `docs/ddr/`, `docs/archive/`, `docs/brainstorming/`, `experiments/` stay). | one rule, one wording |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Extended task branch in Ready for Review, hook verify pass committed, no reviewer record | `git merge` blocked, message names the task and the remedy | automated test |
| 2 | Same, plus a valid chained+anchored `Reviewer: <ID>` record naming the tip commit | merge allowed | automated test |
| 3 | Valid record naming commit X; a later commit changes a `.py` file | blocked | automated test |
| 4 | Valid record naming X; later commits change only `PROJECT_KANBAN.md` and `tasks/TASK_REVIEW_<ID>.md` | allowed | automated test |
| 5 | Minimal-track branch (no guide anywhere) | the review check does not apply | automated test |
| 6 | Record line edited after anchoring | blocked | automated test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t341_reviewer_gate.py tests/test_t341_gate1_doctrine.py .claude/hooks/tests/test_merge_gate_guard.py tests/test_tracks.py tests/test_agents_md_primary.py -q -p no:cacheprovider
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T341.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T341.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/stop_auto_mode_check.py` `is_advocate_call` (L244) and its `field()` helper — exact description plus fixed prompt prefix, fail closed (copy, do not import: that module runs `main()` at import); `.claude/hooks/lib/verify_record.py` `same_code` (L247) — tree diff against an allowlist; `scripts/verify_trace.py` + `.claude/hooks/lib/trace_chain.py` — chain hash and anchor reading; `pre_bash_block_unsafe_merge.py` `trace_shows_verification` (L312) and the Ready-for-Review per-target loop (L2864-2888) — where the new check plugs in; `_guides_added_since` (L2366) — the rule-start cutoff.

**Vital slice**: the gate check (AC 4-6, 9) plus the Gate 1 sentence (AC 1). Doctrine edits beyond the lines that state the rule are secondary.

**Cut list**:
- No verdict capture from `tool_response` (Advocate 3's option 3): the gate proves a review ran, not its result.
- No committed `Reviewed:` line as proof (T309: typed text counts for nothing); the review file keeps findings for humans only.
- No change to Advocate counts (rollout step 2).

Decisions (`tasks/TASK_REVIEW_T341.md` `## Auto decisions`): the proof is a trace record bound to a commit, with a tree-diff freshness check and the anchor check, not a committed text line (decision 3); no cutoff for older tasks, check per merged target (decision 4, DEBATED).

---

## Edge Case Checklist

- [ ] Spike first: spawn one throwaway `Agent` in a scratch session or read an existing record in `memory/event-trace/*.jsonl` to learn the real record shape (`summary` JSON, `is_error`, any status field) before writing `is_reviewer_call`; do not guess field names.
- [ ] The 300-char summary cut: description + prefix + `Task ID:` + `Commit:` must fit; a cut record fails closed.
- [ ] Misfiled record: a main-session `Agent` call is filed by the session's active-task state (slot 3) before its prompt (slot 5) — scanning all trace files by description covers it.
- [ ] `[admin]` path: the same check applies on the `hook_only` merge path.
- [ ] T326 and T327 sit in Ready for Review but are already merged (`git branch --merged main`): the per-target check never sees them; the board-wide loop must not gain the check.
- [ ] Untracked `tasks/TASK_REVIEW_*` on `main` makes `git merge` abort (learning, T309) — tests must not depend on that.
- [ ] Pin-test pre-flight: the `Pre-existing pin tests` row below is filled before work starts
- [ ] Stale references: grep for "never write implementation code", "Implementation = sub-agent", "sub-agent implements" and similar across the live docs (AC 10)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | `REVIEWER_PROMPT_PREFIX`, `is_reviewer_call`, `trace_shows_review`, wired per merged/pushed target (ordinary and `[admin]` paths), not into the board-wide loop |
| `.claude/hooks/tests/merge_gate_guard.py` | `AUTHORISED_TASKS` += `T341` |
| `.claude/hooks/subagent_stop_reviewer_done.py` | new (AC 11): the `ReviewerDone` record writer |
| `.claude/hooks/tests/test_t341_reviewer_done.py` | new: AC 11, 13 (hook side) |
| `.claude/settings.json` | the `SubagentStop` entry only (AC 11, 14) |
| `.claude/hooks/tests/hook_verify_row.py` and the older gate tests | their reviewer fixture becomes a `ReviewerDone` record (AC 12) |
| `.claude/hooks/tests/test_t341_reviewer_gate.py` | new: AC 4-6, 9 |
| `tests/test_t341_gate1_doctrine.py` | new: AC 1-3, 7, 8, 10 |
| `AGENTS.md` | Gate 1 last sentence; Stage 3/4 lines |
| `docs/ddr/0011-supervisor-implements-reviewer-spawn-gated.md` | new DDR |
| `docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` | Status line only |
| `docs/claude-md/pipeline-stages.md` | Stage 3, Stage 4 |
| `docs/claude-md/tracks.md` | merge-gate condition, Known limits |
| `skills/craft-spawn-prompt/`, `skills/code-review/` | only where they state who implements / who reviews; `skills/code-review/SKILL.md` is at the 8 KB Codex cap — put new text in `references/` |
| `agents/*.md`, `site/docs.html` | only lines that state the old rule (AC 10) |
| Pre-existing pin tests | `tests/test_tracks.py:320` (Gate 1 title must stay literal — keep it); `tests/test_agents_md_primary.py`; `.claude/hooks/tests/test_agent_guide_dedup.py` (mentions Gate 1); `tests/test_site_*.py` baseline hashes if `site/docs.html` changes (pattern: `CHANGED_BY_<ID>` in `tests/test_site_story.py`); memory budget tests. Repoint or narrow each; escalate if one pins the old rule's meaning. |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/stop_auto_verify.py` | the independent verify run stays as is |
| `.claude/hooks/stop_auto_mode_check.py` | Advocate counts are rollout step 2 |
| `.claude/skills`, `.claude/agents` symlinks | load-bearing |
| `.claude/settings.json` | only the one `SubagentStop` hook entry of AC 11 (user's choice of option B, 2026-11-20); no permission or other change |

---

## Test Plan

TDD per AC: write `.claude/hooks/tests/test_t341_reviewer_gate.py` first (temp git repos, temp trace + anchor dir via `CLAUDE_TRACE_ANCHOR_DIR`, the way existing gate tests build fixtures), see each case fail for the right reason, then implement. Doctrine tests read the real files. Run the Verification Command, then the full suite (`python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider`); on this machine 52 tests fail on unchanged `main` for missing shells (`busybox`, `zsh`) and must be compared, not fixed.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (if Medium/High risk)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T341.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run — feature confirmed working in running app
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review

---

## Questions Log

- 2026-11-20 USER After Stage 4 found that every `Agent()` spawn here is recorded `async_launched` (so the gate could never pass), options A (accept a started record) / B (a `SubagentStop` record when the reviewer ends) / C (keep it, run reviewers from a CLI). Supervisor recommended B (a reviewer that dies mid-run, as the fixture sub-agent did on a rate limit today, must not count). User: "so B". → AC 11-14.
- 2026-11-20 DEBATE Which tasks does the reviewer check cover? → (C) no cutoff, no exemption list; check per merged/pushed target (Advocate 1: C, the date helper trusts backdated `%ct` and T309/Readiness rollouts grandfathered nothing; Advocate 2: C, `_guides_added_since` turns absent-means-block into absent-means-skip; Advocate 3: C, plus wire per target, not in the board-wide loop at L2873) — all three agree.
