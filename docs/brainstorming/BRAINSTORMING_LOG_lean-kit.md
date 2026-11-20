# BRAINSTORMING_LOG — lean kit: unused files, and sub-agents vs. inline work
**Generated**: 2026-11-19
**Task / Context**: User, 2026-11-19: "check the harness kit, brainstorming, propose the removing of unused files … the model can cover the tasks effectively without agent. Agent just make the token burn … let brainstorming about that". Tier: **Deep** (topic 2 changes a Permanent Rule: Hard-Stop Gate 1) and **Standard** (topic 1).
**Skill**: `Skill({ skill: "brainstorming" })`

---

## The Problem Space

Two questions, one theme: the kit costs more than it returns in places.

1. **Unused files.** The repo has 1,068 tracked files. Some are finished experiments, one-off measurement scripts and old reports. They cost reading time, test time and confusion. The kit is a product for *other* projects, so "never used in this repo" does not mean "unused": `migration-safety` only matters in a project with a database.
2. **Sub-agents.** Hard-Stop Gate 1 says the Supervisor never writes implementation code on the extended track; a sub-agent does. At Risk Medium/High, every decision a user would have made is debated by 2–3 Advocate sub-agents. The user's claim: the model can do the tasks itself, and the agents mostly burn tokens.

Non-negotiable: the safety the gates give (no unreviewed merge, no destructive action, a verify run by a separate process) must stay. What is open is *who* does the work, and how many spawns that needs.

---

## Evidence (verified 2026-11-19)

### On sub-agents

| Source | What it shows |
|---|---|
| `docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` (2026-08-07, user ruling) | A spawn that does nothing cost **15,669 tokens**; a real C2 task 81–84k (97.6% cache read). Decision: keep Gate 1, make spawns cheaper, not fewer. Reason: review independence caught real defects; LR-0001/LR-0002 show the Supervisor drifting into code when a task "felt small". |
| This session (T326/T327, 2026-11-18) | Implementers: T326 71.7k tokens (28 tool calls), T327 86.1k (33). **Advocates: 6 spawns, 47.5k–51.6k each, with only 1–2 tool calls each** — about 302k tokens, **~66% of all spawn tokens this session, for 2 decisions**. The floor per spawn is now ~47k, about 3× the August figure (the auto-loaded doctrine and rosters grew). |
| Same session — what the agents bought | Advocates changed one design (T327: list processes, never signal — safer) and found one false docstring claim (T326). The implementers did correct work; the Supervisor's own review found one P2 test gap. Value was real, but small per token. |
| `experiments/kit-arms/results/ANALYSIS.md`, `round2/REPORT-2.md` (2026-10-26, 36 + 36 headless runs, `sonnet`) | A 26-line `AGENTS.md` + 2 hooks ("minimal") scored **12/12**, the same as the full kit with a human answering (12/12), at **43% of the cost** ($1.89 vs $4.39) and 3 vs 7 interruptions. Without a human, the full kit scored 8/12: it stopped on its own gates. The full kit applied Gate 1 inconsistently on identical prompts. Limit: small single-turn tasks; it does not measure long multi-agent work or the audit trail. |
| Counter-evidence | Inline work is not free either: every tool result stays in the Supervisor's context and is re-read (as cache) on every later turn. Isolation keeps the main context small, and lets 2 tasks run in parallel (T326 + T327 ran at the same time). |

### On unused files

| Candidate | Files | Evidence | Verdict |
|---|---|---|---|
| `scripts/measure_agent_guide_tokens.py` | 1 | 0 live references, not in `.github/workflows/ci.yml`; T066 one-off measurement | remove |
| `scripts/test-claude-md-refs.sh` | 1 | 0 live references, not in CI; T039 check of `CLAUDE.md` refs, superseded since T173 moved doctrine to `AGENTS.md` | remove (or wire into CI if still wanted) |
| `experiments/plugin-spike/` + `tests/test_plugin_spike.py` | ~10 | README says "throwaway"; the plugin shipped as `plugin/` | remove both |
| `experiments/self-review-spike/` | 3 | spike done; `self-review` skill shipped | remove (results already in memory/decisions) |
| `experiments/kit-arms/` | ~100 | fixture, 36 patches, runner and raw JSON; the 2 result reports are cited evidence | keep `ANALYSIS.md` + `REPORT-2.md` (move to `docs/experiments/`), remove the rest; git history keeps it |
| `reports/token-audit_2026-07-*.md`, `…08-04.md` | 3 | August token audits, superseded by DDR-0002/0009 | move to `docs/archive/` or remove |
| root `BRAINSTORMING_LOG.md` | 1 | 2026-09-12 install-scripts log left at the root; every other log lives in `docs/brainstorming/` | move to `docs/brainstorming/BRAINSTORMING_LOG_install-scripts.md` |
| skills not seen in any recent review file | — | `blast-radius`, `compound`, `compound-refresh`, `diagnose`, `html-report`, `ideate`, `migration-safety`, `resolve-pr-feedback`, `score`, `strategy`, `teach`, `thinking-report` | **not decided here**: they ship to user projects. Real cut needs a product decision. One drift to fix either way: Stage 4 says `html-report` runs after every review skill, and no recent task ran it. |
| `tasks/` | 459 files, 6.2 MB (263 guides) | Permanent Rule: guides are "stored permanently in tasks/" | keep unless the rule changes; option: move Done tasks older than 60 days to `tasks/archive/` |
| ADRs, DDRs, `docs/brainstorming/*` | — | few references by design: they are decision records | keep |
| `skills/slim-skills` | 1 | absent from the model's skill list because `disable-model-invocation: true` (user-only, by design) | keep |

---

## Questions for the User

Asked one at a time in chat; answers recorded here.

1. Topic 2: may Hard-Stop Gate 1 change, which reverses your DDR-0004 ruling of 2026-08-07?
2. Topic 1: for skills unused in this repo, are they product features to keep, or should the kit's skill list shrink too?

---

## Alternative Paths — topic 2 (sub-agents)

| Option | Name | Summary | Invasiveness | Regression Risk | Recommended? |
|---|---|---|---|---|---|
| A | Keep and trim (DDR-0004 as is) | Agents implement; cut the per-spawn floor (smaller auto-loaded doctrine, cheaper Advocate model) | Low | Low | |
| B | Flip the split | Supervisor implements inline; spawns only where independence or parallel work pays: 1 fresh-context reviewer per extended task, 1 contrarian Advocate (not 3) at Risk High, implementer agents only for parallel or very large tasks | Medium (Gate 1 + `### Debate size by Risk` rewrite) | Medium | ✅ Yes |
| C | No sub-agents | Supervisor does everything; independence comes only from hooks and the headless auto verify run | High (Gate 1, Stage 3, Advocates, agent guides all go) | High | |

### Option A — Keep and trim
**Approach**: keep Gate 1 and 3 Advocates. Shrink what every spawn loads, and run Advocates on a small model.
**Pros**: no rule change; keeps implementer/reviewer separation; parallel work stays.
**Cons**: the floor tripled since DDR-0004 chose this path; trimming was measured worth ~10% of injected tokens (DDR-0004), so the ceiling is low.
**Why it might fail**: it is the path already taken for 3 months, and the floor still grew.

### Option B — Flip the split
**Approach**: on the extended track the Supervisor writes the code itself, in a worktree, test-first, as the minimal track already does. Independence moves to where it pays:
- one **reviewer** spawn per extended task with a fresh context: it gets the diff and the guide, never the Supervisor's reasoning (code-review + security-review in one pass);
- at Risk High, **one contrarian Advocate** that argues against the Supervisor's pick, instead of 3 that each restate the options;
- implementer spawns only when work runs in **parallel** (2+ independent tasks) or a task is too big for one context (C3).
**Pros**: removes ~2 of 3 spawns per task and 2 of 3 Advocates. This session would have used ~4 spawns instead of 8, roughly 200k fewer tokens. Keeps the separation DDR-0004 valued (author ≠ reviewer). Matches the kit-arms result: the model does the work fine; gates and questions cost the most.
**Cons**: reverses a user ruling; the Supervisor's context grows with implementation output; LR-0001/LR-0002 drift risk ("felt small") comes back unless the reviewer spawn is enforced by a hook, not prose.
**Why it might fail**: prose rules bind unreliably (kit-arms: same prompt, different behaviour). If the reviewer spawn is only doctrine, it will be skipped. Mitigation: the merge gate requires a review record written by a spawn whose prompt names the task (the trace already attributes spawns, T196).

### Option C — No sub-agents
**Approach**: delete Stage 3 spawning, Advocates and the 4 agent guides; the Supervisor does all; the hook-run auto verify is the only independent check.
**Pros**: cheapest; simplest doctrine; closest to the kit-arms "minimal" arm.
**Cons**: author reviews own code; auto verify checks that it works, not that it is well-made; loses parallel tasks.
**Why it might fail**: kit-arms tasks were small; on a large diff self-review misses what a fresh reader catches (DDR-0004 lists 3 such catches in one session).

---

## Alternative Paths — topic 1 (unused files)

| Option | Name | Summary | Recommended? |
|---|---|---|---|
| A | Clear dead code only | Remove the 2 scripts, the 2 spikes (+ their test), move the root log and the August reports | ✅ Yes (first step) |
| B | A + slim experiments | Also reduce `experiments/kit-arms/` to its 2 result reports | ✅ Yes (same task) |
| C | B + product cut | Also drop skills not used in practice and archive old `tasks/` guides (needs a Permanent Rule change) | later, after a usage decision |

---

## 50% Rule Check

Topic 2: Option B needs no new mechanism for the inline part — the minimal track already describes inline work (`docs/claude-md/tracks.md` 7 steps). The new code is one gate check (a review record from a spawn) and a shorter `### Debate size by Risk` table. Half the work again: skip the gate check and keep the reviewer as doctrine — rejected, because prose does not bind (kit-arms).
Topic 1: Option A + B are deletes and moves only; no new code.

---

## Recommended Path

**Topic 2 — Option B (flip the split)**, written as a new DDR that supersedes DDR-0004, *only if the user agrees to change Gate 1*. Otherwise Option A with one change that needs no Gate 1 edit: 1 contrarian Advocate at Risk High instead of 3 (the Advocates alone were ~66% of this session's spawn tokens).
**Topic 1 — Options A + B in one C1 task.**

---

## Surgical Scope

Should be touched (topic 1): `scripts/measure_agent_guide_tokens.py`, `scripts/test-claude-md-refs.sh`, `experiments/`, `tests/test_plugin_spike.py`, `reports/`, root `BRAINSTORMING_LOG.md`, any doc that names them.
Should be touched (topic 2, if B): `AGENTS.md` Hard-Stop Gate 1 and `## Stage 0–5` Stage 3 line, `docs/claude-md/pipeline-stages.md` Stage 3–4, `docs/claude-md/tracks.md` `### Debate size by Risk`, `skills/craft-spawn-prompt/`, `skills/code-review/`, a new `docs/ddr/0011-…`, the merge gate (review-record check) with `merge_gate_guard.AUTHORISED_TASKS` sign-off.
Must not be touched: `.claude/hooks/stop_auto_verify.py` (the independent verify run stays), the git guardrails, `.claude/skills` / `.claude/agents` symlinks, ADRs/DDRs.

---

## Edge Case Checklist for TASK_GUIDE

- [ ] A removed file is named by a test that pins file lists or counts (`test_stage_names.py`, MANIFEST tests, `site/` chips, `gen_kit_explorer.py` data)
- [ ] `setup.sh` / `update.sh` removal lists: a file removed from the kit must be removed from installed projects too (`tests/test_update_removals.sh`)
- [ ] Topic 2: the reviewer spawn must not see the Supervisor's reasoning, or it is not independent
- [ ] Topic 2: parallel tasks still need worktree isolation even when the Supervisor implements
- [ ] Topic 2: a C3 task still splits or spawns; the Supervisor's context limit is real

---

## Questions Log

- 2026-11-20 DEBATE Topic 2: option A, B or C for sub-agents? → B, staged (Advocate 1: B in one task, merge-gate reviewer check in the same task as the Gate 1 rewrite, re-run the replay with ≥3 runs per cell; Advocate 2: B, merge-gate reviewer check first, then the Gate 1 rewrite, then the Advocate counts; Advocate 3 (smallest safe thing): B in two steps, the implementer flip plus the reviewer check now, the Advocate counts later after more replays). All three agree on B. Decided by rule 2 (smaller, reversible steps): step 1 = reviewer-record merge-gate check + Gate 1 rewrite + DDR-0011 superseding DDR-0004; step 2 = Advocate counts (High 3→1, Medium 2→0) after more replays. Citations opened: AGENTS.md:171, docs/claude-md/tracks.md:281, .claude/hooks/stop_auto_mode_check.py:128, docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md:93-95, memory/decisions.md:2487, tasks/TASK_REVIEW_T102.md:88. ⚠ Reverses a user ruling (DDR-0004): needs the user's yes.
- 2026-11-20 f6 (August token audits) → keep in reports/: SAFER OPTION, `.claude/hooks/tests/test_token_audit_generator.py` reads `reports/token-audit_2026-07-17.md` and `…07-21.md`.
- 2026-11-20 f7 (root BRAINSTORMING_LOG.md) → move the file only, skill unchanged: SAFER OPTION, a new brainstorming run writes the root file and could overwrite the 2026-09-12 log.
- 2026-11-20 f5 (kit-arms) → wait for machine 2's T328 to merge: FACT, `docs/claude-md/tracks.md:4` cites the experiment.
