# 0011. The Supervisor implements on the extended track; one fresh reviewer spawn, required by the merge gate

**Status**: Accepted
**Date**: 2026-11-20
**Deciders**: hungnh1110@gmail.com (ruling: "should start the enhance now", then "run by automate, [admin]"), Supervisor (Debate of 3 Advocates, options and measurement)
**Related**: T341 (implements this decision) · supersedes DDR-0004 · `docs/brainstorming/BRAINSTORMING_LOG_lean-kit.md` (option B, "flip the split", step 1 of the staged rollout) · T148 (trace chain and anchor) · T196 (spawn attribution) · T309 (typed text counts for nothing at the merge gate)

---

## Context

DDR-0004 (2026-08-07) kept Hard-Stop Gate 1 — "The Supervisor must never write implementation code
directly" — and chose *cheaper* spawns over *fewer* spawns. Its reason was review independence: the
implementer must never be its own sole oracle. Its own **Revisit if** clause named two triggers: the
floor per spawn turns out materially larger than 15.7k tokens, or a mechanism appears that keeps the
implementer/reviewer separation without a second full spawn per task. Both now hold.

| Evidence | What it shows |
|---|---|
| DDR-0004 probe, 2026-08-07 | A spawn that does nothing cost **15,669 tokens**. |
| T326/T327 session, 2026-11-18 (`BRAINSTORMING_LOG_lean-kit.md` `## Evidence`) | Advocates: 6 spawns at 47.5k–51.6k tokens each with 1–2 tool calls each. **The floor per spawn is now ~47k, about 3× the August figure**: the auto-loaded doctrine and rosters grew. The path DDR-0004 chose (trim the content) did not hold the floor. |
| `experiments/kit-arms/` (2026-10-26, 36 + 36 headless runs) | A 26-line `AGENTS.md` + 2 hooks scored 12/12, the same as the full kit with a human answering, at 43% of the cost. The full kit applied Gate 1 inconsistently on identical prompts: **prose rules bind unreliably**. Limit: small single-turn tasks. |
| The 2026-11-20 replay named by the Debate | Advocate 1 asks to re-run it with ≥3 runs per cell before the Advocate counts change (rollout step 2). No result file is committed; this DDR cites it by the Debate line in `BRAINSTORMING_LOG_lean-kit.md` `## Questions Log` only. |

The mechanism DDR-0004 waited for exists: the trace hook (`post_tool_trace.py`) writes a hash-chained,
anchored record of every `Agent` call (T148), and the merge gate can read it. A reviewer spawn can
therefore be *required by a hook*, not asked for in prose.

**Gate criteria**: 3-of-3 hold. Hard to reverse in practice (every extended task after it runs the new
way); surprising without context (it reverses a user ruling and a Permanent Rule); a genuine trade-off
(see Consequences).

---

## Decision

On the extended track the Supervisor writes the code itself, in the task's worktree, test first, as
the minimal track already does. An implementer spawn is used only for 2+ independent tasks at once, or
for a C3 task too big for one context. Independence moves to **one fresh-context reviewer spawn per
extended task**: `Agent({ subagent_type: "qa-expert", description: "Reviewer: <ID>", prompt: … })`, a
prompt whose first three lines are the fixed `REVIEWER_PROMPT_PREFIX`, `Task ID: <ID>` and
`Commit: <40-hex>`, carrying the diff range and the guide path and never the Supervisor's reasoning.

The merge gate (`.claude/hooks/pre_bash_block_unsafe_merge.py`, `trace_shows_review`) refuses the merge
of an extended-track task branch, and the narrowed push of one, until a `ReviewerDone` trace record
proves that reviewer ran on the exact code being merged: chain hash and anchor intact, the named
commit an ancestor of the tip, and only the review file, the board,
`tasks/MINIMAL_LOG.md` or `memory/*.md` (not `memory/MEMORY.md`) changed since. No date cutoff: every
extended-track task merged from now on is checked.

The `SubagentStop` hook (`.claude/hooks/subagent_stop_reviewer_done.py`) writes the `ReviewerDone`
record when the reviewer ends. It reads the task ID and the commit from the reviewer's own spawn
prompt. The gate counts only that record, not the `Agent` spawn record, so the spawn may run in the
background.

Rollout step 2 (a later task, after more replays): the Advocate counts (`### Debate size by Risk`).

---

## Alternatives Considered

**A — Keep DDR-0004 and trim further.** **Rejected**: the floor tripled on the path DDR-0004 chose,
and trimming was measured worth ~10% of injected tokens.

**B — Flip the split, reviewer as prose only.** **Rejected**: kit-arms showed prose rules bind
unreliably; LR-0001/LR-0002 show the drift ("it felt small") the gate must stop.

**C — No sub-agents at all, self-review.** **Rejected**: on a large diff self-review misses what a
fresh reader catches (DDR-0004 lists 3 such catches in one session).

**Proof shape (Debate, `tasks/TASK_REVIEW_T341.md` `## Auto decisions` 3).** A committed
`Reviewed:` line was rejected: since T309 typed text counts for nothing at the merge gate. The
trace record, bound to a commit, with the anchor check and a scan of every trace file, was chosen.

**Which record (user, 2026-11-20: "so B").** Stage 4 found that every `Agent()` spawn here is
recorded `spawn.status: async_launched`, at launch, before the review runs. The Agent tool has no
foreground option, so a gate that counts only a `completed` spawn record could never pass. Options:
A — count the `async_launched` spawn record; B — a `SubagentStop` hook writes a `ReviewerDone`
record when the reviewer ends; C — keep the rule and run reviewers from a CLI. The user chose B. A
was rejected because a reviewer that dies mid-run (as a sub-agent did that day, on an API rate limit)
would count.

---

## Consequences

**Gained**: about 2 of 3 spawns per extended task removed (one reviewer instead of an implementer, a
QA agent and a review pass). Review independence is kept and now enforced by the gate, not prose.

**Accepted, stated not hidden**: the Supervisor's context grows with implementation output; a C3 task
still splits or spawns. The trace and anchor raise the bar and are not a proof: an agent's own Python
can write a matching record (as for T148 and T182). The gate proves a review ran, not what it found:
findings stay in `tasks/TASK_REVIEW_<ID>.md`. The reviewer spawn may run in the background: the gate
counts the `ReviewerDone` record that the `SubagentStop` hook writes when the reviewer ends. The event
does not say how the reviewer ended. A reviewer that ends on an API error fires `StopFailure`, not
`SubagentStop`, so it leaves no record. A reviewer that is stopped or crashes can still leave one.

**Revisit if**: reviewer spawns are routinely skipped by a route the gate does not see (a merge the
resolver cannot read is already refused); or replays show the Supervisor-implemented tasks fail
review materially more often than sub-agent-implemented ones.
