# TASK_GUIDE — T355: Split the 4 skills over Codex's 8 KB cap so a Codex install skips none
**Date**: 2026-11-25
**Complexity Level**: C2
**Risk Level**: Medium
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

**User request (verbatim, 2026-11-25)**: "if you can fix all in this session, let do it in this session only [admin], if not, let note the new task" — about the critique list. Point 2: "Skills that exceed Codex's 8 KB limit are simply skipped (with a warning). That is a pragmatic but ugly solution." GitHub #95 (token cost).

**Restated intent**: make each of `bugfix` (10,261 B), `craft-spawn-prompt` (14,946 B), `diagnose` (13,548 B) and `write-better-skill` (15,777 B) fit under the 8,192-byte cap (`lib/harness-fetch.sh` `harness_skill_body_cap`). Move detail the agent needs only at one step into `references/*.md` next to the skill, with a one-line pointer at that step that says when to read it. No rule, gate or step is dropped: only where the text lives changes. A Codex install then skips no kit skill, and a Claude Code activation loads less text.

**Out of scope**: changing the cap or the skip rule (the skip stays for any future oversize skill); rewording kept text; the other critique points (T356–T362).

**Requirement Refs**: GitHub #95; `skills/write-better-skill/SKILL.md` § Progressive-disclosure budgets (resources load on demand).

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the user's request — auto (Supervisor), `[admin]` session tag, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (skill, reference file: no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: none
**Entry point**: Standalone — N/A (skills are found by name; the references are read from the pointer lines)

---

## Acceptance Criteria

1. Each of the 4 `SKILL.md` files is at most 8,192 bytes; no other `skills/*/SKILL.md` grows past it.
2. Every moved block exists verbatim in a `references/*.md` file of the same skill, and the step it left holds a pointer that names the file and when to read it.
3. A Codex install (`setup.sh --harness codex` path, as `tests/test_plugin_names.py` runs it) installs all 4 skills, `references/` included, and prints no oversize warning.
4. README's Codex sentence and the site's Providers section no longer name skipped skills; `tests/test_readme_current.sh` and `tests/test_site_content.py` accept an empty oversize set, and still fail when a skill goes over the cap.
5. Every pin test that read one of these skills passes, either because the pinned line stayed in `SKILL.md` or because the test now reads the reference file that holds it.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | `wc -c skills/*/SKILL.md` | none over 8192 | automated (`tests/test_skill_codex_cap_t355.py`) |
| 2 | each moved block | found verbatim in the skill's `references/` file; pointer line names that file | automated (same test, against `git show main:` text) |
| 3 | Codex projection test | 4 skills installed, no skip | automated (`tests/test_plugin_names.py`) |
| 4 | README + site + their tests | no skipped list; an oversize fixture still fails | automated |
| 5 | the pin tests listed in Test Plan | pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_skill_codex_cap_t355.py tests/test_cli_model_table.py tests/test_craft_spawn_effort.py tests/test_dirty_worktrees.py tests/test_memory_slice.py tests/test_plugin_names.py tests/test_pull_moments.py tests/test_spawn_startup_reads.py tests/test_subagent_sandbox_profile.py tests/test_t303_docs_recent_changes.py tests/test_t347_readme_codex_list.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_stale_reference_sweep.py -q && bash tests/test_readme_current.sh
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T355.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T355.md`. BEFORE: the four sizes above and the Codex skip list.

---

## UI / Design Acceptance Criteria

Text-only change to one existing list item on `site/docs.html`: no new element or style. ☐ N/A with that reason.

---

## Approach

**Pattern reference**: `skills/code-review/SKILL.md` → `references/security-reviewer.md`; `skills/craft-spawn-prompt/references/sandbox.md` (already split this way).

**Vital slice**: move the largest step-scoped blocks, verbatim, with a pointer each:
- `bugfix`: the Step 3 bug task-guide template + its Demonstration block → `references/bug-task-guide.md`
- `craft-spawn-prompt`: the element-by-element detail of step 3 → `references/prompt-elements.md` (the element list and pinned lines stay)
- `diagnose`: Phase 4 instrumentation catalogue and the Stuck-Loop detail → `references/instrument.md`, `references/stuck-loop.md` (the mandatory trigger stays)
- `write-better-skill`: Spec Conformance, Sourcing, Fidelity Gate detail → `references/`

**Cut list**: no rewording of kept text; no new tooling; no change to the cap.

## Edge Case Checklist

- [ ] A pinned phrase moved out of `SKILL.md`: keep the line, or point the test at the reference (only when the pin is about content, not about the activation text)
- [ ] `${CLAUDE_SKILL_DIR}` inside a moved block: the Codex rewrite (`_harness_rewrite_skill_dir`) covers every text file, `references/` included
- [ ] `memory/MEMORY.md` or other files citing `SKILL.md line N` of these skills

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `skills/{bugfix,craft-spawn-prompt,diagnose,write-better-skill}/SKILL.md` | blocks moved out, pointers in |
| `skills/*/references/*.md` (new) | the moved blocks |
| `README.md`, `site/docs.html` | Codex sentence: no skill skipped today |
| `tests/test_readme_current.sh`, `tests/test_site_content.py`, `tests/test_t347_readme_codex_list.py`, `tests/test_plugin_names.py`, `tests/test_site_visual_first.py` | empty oversize set is valid |
| `tests/test_skill_codex_cap_t355.py` (new) | SC 1–2 |
| Other pin tests (`tests/test_memory_slice.py`, `tests/test_spawn_startup_reads.py`, `.claude/hooks/tests/test_diagnose_evidence_loop.py`) | only where a pinned line moved; added at Stage 4 (lane check `unpredicted`) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `lib/harness-fetch.sh` | the cap and skip rule stay |
| `.claude/skills`, `plugin/skills` symlinks | load-bearing |

---

## Test Plan

New `tests/test_skill_codex_cap_t355.py` (sizes; moved text verbatim against `main`; pointers). The pin tests in the Verification Command. Full suite compared with the pre-change baseline (`tests` on `main`, same failures only).

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run (inline if the built-in cannot start)
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T355.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated
- [ ] Board current

---

## Questions Log
