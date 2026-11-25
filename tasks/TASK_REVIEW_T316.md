# TASK_REVIEW — T316: the sensitive-path hook treats its own pattern list as always sensitive

> Sibling of `tasks/TASK_GUIDE_T316.md`. Evidence is filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Ran T316 with T304 and T247 in parallel under the session `[admin]` — RULE: the user's request "continue the tasks as parallel [admin]" (`tasks/TASK_GUIDE_T316.md § Requirement`).
2. Track extended — RULE: docs/claude-md/tracks.md § Track rule (Risk High: a security control, the sensitive-path hook).
3. The Supervisor writes the oracle test and the code itself, test first, in `../wt-t316` — RULE: `AGENTS.md § Hard-Stop Gates` (Gate 1: "the Supervisor writes the code itself, in the task's worktree, test first").
4. The list is a protected pattern, like `.claude/state/**`: always asks, not pre-authorisable by a guide, not approvable online, matched by name in any directory — DEBATED: option (a) (Advocate 1: (a), (b) lets one approved Edit or a predicting guide wipe every protection with no later prompt, (c) misses `cd .claude && sed -i … sensitive-paths.txt`; Advocate 2: (a), an agent writes the predicted-files table (`predicted_paths` trusts any backticked path), so (b) self-authorises the root of trust; Advocate 3: (a), the cost to honest work is small — the Read tool and `scripts/gen_sandbox_profile.py` never pass the hook, a Bash `cat` asks as for every sensitive path; (c) also misses a `cd` through a variable path). All three rejected (b) approvable and (c) root-anchored only (`PROJECT_KANBAN.md:95` "make the hook treat its own pattern list as always sensitive (like the T314 approval dir)"). ⚠ decided for you — please review
5. Matched by its name in any directory (`sensitive-paths.txt`, no `/`), not by the root path only — RULE: `.claude/hooks/pre_tool_sensitive_path.py:87` "S2: the approval file's name is sensitive in any directory (a `cd .claude` call can write it under a relative path no root-anchored pattern sees)".
Checks: tests `python3 -m pytest -q -p no:cacheprovider` on the guide's Verification Command — `119 passed, 95 subtests passed` at 83311fe2; neighbours (sandbox profile, plugin hooks, plugin init, pull moments) `181 passed`; full suite: `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 83311fe2: `58 failed, 7837 passed, 24 skipped`; 57 are the same list as clean `main` in this environment; the 58th, `test_task_guide_template_verify_row.py::test_fixed_row_present_in_template_file`, ran while the main checkout took commits and passes alone (`4 passed`); no failure comes from the hook change; reviews: Reviewer (fresh context, qa-expert, e539b6a0) PASS with findings — P2 folder-level calls (`rm -rf .claude`, `git checkout HEAD~1 -- .claude`) and shell-built names skip the token match, the same for `.env` since T146 (known limitation, not new), P3 Bash reads of the list ask, P3 the sandbox profile does not deny the list; it re-ran the Verification Command `119 passed`; Supervisor `code-review` 0 P0/P1, 1 P2 fixed (83311fe2, `tracks.md` names the list), 2 P3; `security-review` (temporary `origin/HEAD`, removed after; its built-in diff from the main checkout is empty, so the branch diff was read by hand) no findings; real run: the hook run as the harness runs it, on throwaway projects, by every oracle case (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T316: the sensitive-path list is a protected pattern (always asks, never predicted or approved)
Not done: merge (admin: after the auto verify pass); auto verify: ☑ pass (session 06fdb20e-5e49-4b35-9586-0e5df7c070b7, commit 68ee295454895e6d60fac61e1f005e7c68559310, log .claude/verify-runs/T316-68ee29545489.log)
Closed: row moved to Done 2026-11-25 — auto verify pass (session 06fdb20e-5e49-4b35-9586-0e5df7c070b7, commit 68ee295454895e6d60fac61e1f005e7c68559310); Gates 5 and 6 checked

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t316_list_self_protect.py` (9 tests): AC1 `test_ac1_edit_and_write_ask`, `test_ac1_online_edit_asks`; AC2 `test_ac2_bash_naming_the_list_asks`; AC3 `test_ac3_a_negation_line_does_not_unmark_it`; AC4 `test_ac4_a_predicting_guide_does_not_pre_authorise_it`; AC5 `test_ac5_a_recorded_approval_does_not_cover_it`, `test_ac5_a_yes_records_no_approval_for_it`; AC6 `test_ac6_relative_name_after_cd_claude_asks`; AC7 `test_ac7_unrelated_calls_stay_silent`. |
| Verification command run | ☑ pass | The guide's Verification Command at e539b6a0: `119 passed, 95 subtests passed` |
| Negative cases hold | ☑ pass | Red run before the change: Demonstration BEFORE (`13 failed, 3 passed`). |
| verify | ☑ pass | auto-run by hook, session 06fdb20e-5e49-4b35-9586-0e5df7c070b7, commit 68ee295454895e6d60fac61e1f005e7c68559310, log .claude/verify-runs/T316-68ee29545489.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read: `PROTECTED_PATTERNS`, `sensitive_hits`, `file_key`, `is_state_key`, `main`, `pattern_file_path` (plugin fallback), `scripts/gen_sandbox_profile.py`, the `plugin/.claude/sensitive-paths.txt` symlink, `tracks.md` approvals text. `git diff --stat main...83311fe2`: 4 files. |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 83311fe2: `58 failed, 7837 passed, 24 skipped`; 57 are the same list as clean `main` in this environment; the 58th, `test_task_guide_template_verify_row.py::test_fixed_row_present_in_template_file`, ran while the main checkout took commits and passes alone (`4 passed`); no failure comes from the hook change |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: neither companion tool is installed for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | No UI: hook-only change. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | No UI: hook-only change. |
| **UI: Responsiveness at target viewports** | ☐ N/A | No UI: hook-only change. |

---

## Demonstration

**BEFORE**: captured 2026-11-25T07:30:04Z on `881d0f50` (before any implementation commit), `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t316_list_self_protect.py`:

```
SUBFAILED(tool='Edit', target='.claude/sensitive-paths.txt') ...::OfflineList::test_ac1_edit_and_write_ask
SUBFAILED(command='rm .claude/sensitive-paths.txt') ...::OfflineList::test_ac2_bash_naming_the_list_asks
FAILED ...::OfflineList::test_ac3_a_negation_line_does_not_unmark_it
FAILED ...::OfflineList::test_ac4_a_predicting_guide_does_not_pre_authorise_it
FAILED ...::OfflineList::test_ac6_relative_name_after_cd_claude_asks
FAILED ...::OnlineList::test_ac5_a_recorded_approval_does_not_cover_it
13 failed, 3 passed, 1 subtests passed in 0.78s
```

Passing before: `test_ac7_unrelated_calls_stay_silent`, and the `sed -i '/infra/d' …` Bash case (it asked already, because its `/infra/d` token matches `infra/**`).

**AFTER**: `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t316_list_self_protect.py` at 83311fe2: `9 passed, 8 subtests passed` (the 13 BEFORE failures pass; the 3 that passed still pass).

**DELTA**: an Edit, Write or Bash call that names `.claude/sensitive-paths.txt` now asks the human, and no list line, guide or approval can turn that off. Known limitation (all sensitive paths, since T146): a folder-level call or a shell-built name is not matched.

**WITNESS**: the fresh-context Reviewer re-ran the Verification Command and probed bypasses; the auto verify run is the independent check (`memory/event-trace/T316.jsonl`).

## Supervisor Stage 4 runs

- `code-review` (Supervisor, range `main...e539b6a0`): P0 none, P1 none. P2: `docs/claude-md/tracks.md:168` did not name the list as always sensitive — fixed in 83311fe2. P3: a Bash read of the list now asks (as for `.env`); `scripts/gen_sandbox_profile.py` carries only the list's lines, not the hard-coded protected patterns (older than T316). Lane: `lane: C1, 3 files, 117 lines, FITS; unpredicted: (all 3 — the checker does not parse this guide's bullet list)`.
- `security-review` (built-in, temporary `origin/HEAD`, removed after; branch diff read by hand): the change only adds a protected pattern, so it can only add asks; symlink (`path_forms` real path), `!` line, predicted path, approval key and `cd .claude` all checked. No findings.
- Follow-up (not fixed here): folder-level and shell-built-name calls skip the token match for every sensitive path.
