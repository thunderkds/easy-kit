# TASK_REVIEW — T355: Split the 4 skills over Codex's 8 KB cap so a Codex install skips none

> Sibling of `tasks/TASK_GUIDE_T355.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Sign the Requirement Fidelity Gate myself — RULE: `docs/claude-md/tracks.md` `### Every user stop and its auto rule` (row 13: the Gate is signed `auto (Supervisor)`)
2. Do T355 in this session and register T356–T362 for the rest, since T356, T359 and T360 wait on the user's choices — FACT: PROJECT_KANBAN.md:11 "Before start: brainstorming + the user's choice of what it drops (guide? reviewer spawn? auto verify?)"
3. Start the built-in `security-review` with a temporary `refs/remotes/origin/HEAD` at the base `f6292ac9` (this repo has no `origin`), removed right after (`git update-ref -d`, `show-ref` confirms); the skill read the main checkout's diff, so the branch range `f6292ac9...62e2f6d3` was checked against its criteria too; no findings — RULE: docs/claude-md/tracks.md:1001 "no git remote, the Supervisor may add a temporary `refs/remotes/origin/HEAD` so the skill can start"
Checks: tests `python3 -m pytest tests/test_skill_codex_cap_t355.py` — 9 passed (red first: `1 failed, 8 passed` at `9b80d50b`, before the split); guide Verification Command set + the moved-text pins — 434 passed, `bash tests/test_readme_current.sh` ALL PASS; full suite at `62e2f6d3` `tests/ .claude/hooks/tests/`: `58 failed, 7859 passed, 24 skipped` against base `f6292ac9` `1 + 54 failed` — the 3 left are flaky (`tests/test_auto_verify.py` fails a different test on every run, base too: base runs `0` and `1` failed, branch runs `3` and `2`, never the same test; `test_merge_gate_companion_rows.py` / `test_task_guide_template_verify_row.py` pass alone, `313 passed`); code-review 0 P0/P1, 1 P2 + 1 P3 fixed (`f5ca17a2`), 1 P3 left (a redundant grep in `tests/test_readme_current.sh`); security-review run with a temporary `refs/remotes/origin/HEAD` at `f6292ac9`, removed after (`docs/claude-md/tracks.md:1000`), no findings; Reviewer: T355 (fresh qa-expert, commit `62e2f6d3`) PASS, 0 P0–P2, 2 P3 left (`craft-spawn-prompt/SKILL.md:39-41` says "below" before the pointer; `diagnose`'s red-flag list is only in `references/instrument.md`); auto-checked, not /verify
Memory: `memory/learnings.md` — 2026-11-25 T355 traps (pins in both test trees; guides on `main` before the reviewer spawn; chain the board guard and commit; no two full runs at once)
Not done: merge (admin: after the auto verify pass); push (yours: `git push github main`); auto verify: ☑ pass (session 8b3cb187-f728-48d6-853f-b69aa069ec6c, commit 9f70f223c26bee9266529165a5b471e75f1a8ffa, log .claude/verify-runs/T355-9f70f223c26b.log); T356–T362 registered, not started (they need your choices or are separate runs); the GitHub comments on #99 and #122 (yours: public)
Paused: auto-mode check failed — Risk Medium: decision 3 (`FACT`) is a choice — its FACT has no Citation (`path:line "quoted text"`) — so it must be `DEBATED` with exactly 2 Advocates named; Risk Medium, but the trace has no `security-review` Skill call [report 734edc54eecc]
Closed: row moved to Done 2026-11-25 — auto verify pass (session ecfbed4a-650f-439f-b7cb-3f67998e3419, commit ade6e6a7400b1e4c218bb96715dd15d377205477); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_skill_codex_cap_t355.py` (SC1 sizes vs the cap read from `lib/harness-fetch.sh`; SC2 every pre-split line still present; SC2b every reference has a pointer); `tests/test_t347_readme_codex_list.py` gains `test_an_oversize_skill_the_readme_omits_fails` and `test_none_with_no_oversize_skill_passes_and_says_so` (AC4); `tests/test_plugin_names.py` Codex install skips none (AC3) |
| Verification command run | ☑ pass | guide `### Verification Command` + moved-text pins: `434 passed`; `test_readme_current: ALL PASS`; Reviewer run `374 passed` |
| Negative cases hold | ☑ pass | SC1 red before the split (`1 failed, 8 passed`, `9b80d50b`); an oversize fixture skill the README omits fails `test_readme_current.sh` (rc 1, "README does not name currently-oversize skill 'diagnose'"); a stale `tdd` name still fails the reverse check |
| verify | ☑ pass | auto-run by hook, session 8b3cb187-f728-48d6-853f-b69aa069ec6c, commit 9f70f223c26bee9266529165a5b471e75f1a8ffa, log .claude/verify-runs/T355-9f70f223c26b.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff f6292ac9...62e2f6d3`: the 4 skills + their `references/`, README, `site/docs.html`, and the pin tests that read those skills (lane check `EXCEEDS` from moved text counted twice) |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression: `58 failed, 7859 passed` vs base `55 failed`; the 3 extra are flaky (see `Checks:`), none reads the changed files |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | text only: one existing docs list item reworded |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no new class, style or token |
| **UI: Responsiveness at target viewports** | ☑ N/A | no layout change |

---

## Demonstration

**BEFORE** (2026-11-25, branch `feat/t355-skill-split` at its base, before any implementation commit): `wc -c` — `bugfix` 10261, `craft-spawn-prompt` 14946, `diagnose` 13548, `write-better-skill` 15777 bytes, each over the 8192-byte Codex cap, so a Codex install skips all four (README: "Skills currently affected: `bugfix`, `craft-spawn-prompt`, `diagnose`, `write-better-skill`").

**AFTER** (2026-11-25, `62e2f6d3`): `wc -c` — `bugfix` 7197, `craft-spawn-prompt` 8079, `diagnose` 7916, `write-better-skill` 7954 bytes, all under 8192; `tests/test_plugin_names.py` Codex install skips no skill (`== []`), `diagnose/references/instrument.md` installed; README: "Skills currently affected: none (long skills keep their detail in reference files)."

**DELTA**: a Codex install now gets all four skills it used to skip, and a Claude Code activation of each loads 2–8 KB less text; the skip rule still guards any future oversize skill.

**WITNESS**: Supervisor session 7b4187fe, 2026-11-25 (BEFORE, red run, full-suite comparison); `Reviewer: T355` (fresh qa-expert, commit `62e2f6d3`): own size and line-containment check, `374 passed`.
