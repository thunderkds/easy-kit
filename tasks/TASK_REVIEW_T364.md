# TASK_REVIEW — T364: sandbox profile denies the hook's protected patterns

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Auto decisions

Mode: auto
1. Took T364 after T366, one task at a time — RULE: `docs/claude-md/tracks.md` `### Admin tag` (one request runs each task Stage 0–5); the user's request "continue your work on the pending tasks, [admin]"
2. Track extended — RULE: `docs/claude-md/tracks.md` § Track rule (Risk Medium row)
3. The Supervisor wrote the code, one fresh `Reviewer: T364` spawn (two rounds) — RULE: `docs/claude-md/pipeline-stages.md:198` "the Supervisor writes the code itself, in the task's worktree, test first"
4. Edit denies only, no Read deny for the protected patterns — FACT: `.claude/settings.json:78` "\"matcher\": \"Edit|Write|Bash\"" (the hook never guards a Read, so the protected patterns guard integrity, not secrecy) and `skills/craft-spawn-prompt/references/sandbox.md:37` "The sandbox write-protects `.claude/`"
5. The generator reads the patterns from the hook — FACT: `.claude/hooks/pre_tool_sensitive_path.py:94` "PROTECTED_PATTERNS = (STATE_PATTERN,) + APPROVALS_NAME_PATTERNS + (LIST_NAME_PATTERN,)" (one source; a copy in the list was the T314/T316 reason against it)
6. Fixed all three reviewer P3 findings (edge shapes, a test that could not fail, the dedup case) and spawned the reviewer again on the new commit — RULE: `docs/claude-md/pipeline-stages.md:198` "one fresh-context reviewer spawn per extended task at Stage 4, which the merge gate requires" (it must have run on the code being merged)
Checks: tests `python3 -m pytest -q tests/test_subagent_sandbox_profile.py tests/test_plugin_names.py tests/test_craft_spawn_effort.py` — 70 passed after the P3 fixes (red first: `2 failed, 16 passed` at 2026-11-25T09:12:29Z, before the change); `python3 scripts/gen_sandbox_profile.py --check` exit 0; full suite `62 failed, 7943 passed` vs `main` `60 failed`: the 2 extra are `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository` (passes alone) and `test_auto_verify.py::test_t189_ac3_a_minimal_record_with_no_new_test_line_keeps_the_row` (fails alone on the clean `main` worktree too); reviews `Reviewer: T364` PASS (P3 only), `code-review` and `security-review` skills in the Supervisor session; real run `python3 scripts/gen_sandbox_profile.py` — printed nothing, rewrote the profile with the 4 new `Edit` denies (auto-checked, not /verify)
Memory: nothing new
Not done: merge (admin: after the auto verify pass); auto verify: running (T182); push (no `origin`; `EASY_KIT_ADMIN_REMOTE` is not set to `github`)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_subagent_sandbox_profile.py::test_t364_hook_protected_patterns_are_denied_for_edit` (AC1, AC3), `::test_t364_generator_reads_protected_patterns_from_the_hook` (AC2); AC4 by `test_ac3_profile_is_exactly_what_the_generator_produces` |
| Verification command run | ☑ pass | `python3 -m pytest -q tests/test_subagent_sandbox_profile.py tests/test_plugin_names.py tests/test_craft_spawn_effort.py` -> `68 passed in 26.35s`; `python3 scripts/gen_sandbox_profile.py --check` -> exit 0 |
| Negative cases hold | ☑ pass | Read-only mutation (no code edited): `build_profile(text, expand_braces, ())` gives `Edit(.claude/state/**)` in deny -> False, so the new tests would go red without the protected patterns. Not run as a red pytest run (a sed mutation of the generator was blocked by the sandbox classifier). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed gen_sandbox_profile.py, the template, the new tests, sandbox.md, the hook's PROTECTED_PATTERNS (read only). Skipped the rest of the repo. Skill tool was not available to the reviewer: code-review and security-review done inline (security-reviewer.md rules), not through the built-in skills. |
| Full smoke suite still green (no regression) | ☑ pass | Not green, no regression (Supervisor, at `462886f9`): `62 failed, 7943 passed, 24 skipped` vs clean `main` worktree `60 failed, 7943 passed, 24 skipped`; the 2 extra: `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository` passes alone, `test_auto_verify.py::test_t189_ac3_a_minimal_record_with_no_new_test_line_keeps_the_row` fails alone on `main` too. Neither reads a changed file |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI: a generator script and a JSON settings template |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no UI |
| **UI: Responsiveness at target viewports** | ☑ N/A | no UI |

---

## Review findings (code-review + security-review, inline)

Verdict: PASS. No P0, P1 or P2. All three P3 fixed by the Supervisor after round 1 (`build_profile` strips `/`, skips `!` and empty patterns; the always-true assert replaced by a no-protected-patterns control; new edge-shape and dedup tests); round 2 below.

| Sev | File:line | Finding | One-line fix |
|-----|-----------|---------|--------------|
| P3 | scripts/gen_sandbox_profile.py (build_profile, `glob = pattern if "/" in pattern ...`) | A future protected pattern with a leading `/`, a trailing `/` or a `!` becomes `Edit(/abs)`, `Edit(a/b/)`, `Edit(**/!neg)`. Today's four patterns are fine. Latent only. | Strip a leading `/` and trailing `/`, and skip `!` patterns, as `sensitive_globs` does for the list. |
| P3 | tests/test_subagent_sandbox_profile.py (last assert of the SC2 test) | Compares the hook's PROTECTED_PATTERNS with a fresh load of the same file, so it cannot fail. | Drop it, or assert `main()` output contains each protected glob. |
| P3 | tests (gap) | No test for the dedup branch (a protected glob already in the list is emitted once). | Add a case with a list line equal to a protected glob. |

Security: Edit-only denies, no Read deny (documented cut). The hook is loaded by path from the repo, as it was already for expand_braces; no new input or execution surface. New denies are additive, so no existing rule is weakened. Order matches AC3 (after terraform, before memory).

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (2026-11-25T09:14:09Z, `main` at `480227da`, before the change): `git show main:templates/subagent-sandbox.settings.json | grep -c 'sensitive-paths.txt\|\.claude/state\|sensitive-approvals'` printed `0`; the red run at 2026-11-25T09:12:29Z: `2 failed, 16 passed` (`AssertionError: Edit(.claude/state/**)`; `module 't364_gen' has no attribute '_hook'`)

**AFTER** (same command on the branch head): printed `4` — `Edit(.claude/state/**)`, `Edit(**/sensitive-approvals.json)`, `Edit(**/sensitive-approvals.json.*)`, `Edit(**/sensitive-paths.txt)`; `tests/test_subagent_sandbox_profile.py` `20 passed`

**DELTA**: a CLI-spawned sub-agent's profile now refuses, at the permission layer, a write to the hook's state folder, the approval file and the pattern list, even where the hook is absent or fails open.

**WITNESS**: Supervisor session acceb8c1, 2026-11-25 (BEFORE, red run, full-suite comparison); `Reviewer: T364` (fresh qa-expert, commit `462886f9`, round 2 on the fix commit).
