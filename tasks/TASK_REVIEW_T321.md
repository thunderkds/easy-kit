# TASK_REVIEW — T321: the `[admin]`/`[ticket]` push remote is a setting (`EASY_KIT_ADMIN_REMOTE`), not the hard-coded `origin`

> Sibling of `tasks/TASK_GUIDE_T321.md`. Evidence is filled by the reviewer at Stage 4/5.

---

## Auto decisions

Mode: auto
1. Ran T321 after T354 under the session `[admin]` — RULE: the user's request "merge T347 [admin], T321 [admin]" and, after the compaction, "T321 [admin]" (`tasks/TASK_GUIDE_T321.md § Requirement`).
2. Track extended — RULE: docs/claude-md/tracks.md § Track rule (Risk High: the merge gate; C2: gate, new test, guard, tracks.md).
3. The Supervisor writes the oracle test and the code itself, test first, in `../wt-t321`; no qa-expert or implementer spawn (the guide's "written first by `qa-expert`" predates DDR-0011) — RULE: `AGENTS.md § Hard-Stop Gates` (Gate 1: "the Supervisor writes the code itself, in the task's worktree, test first").
4. Reader shape and bad-value rule: one call-time `_admin_remote()` (None for a bad value), a refusal naming the value before every other push check, each helper failing closed; valid = `REMOTE_NAME_PATTERN` and no leading `-` or `.` — DEBATED: option (a) (Advocate 1: (a), (b) lets `--heads`/`.` reach `ls-remote` argv, (c) breaks the shared test module load; Advocate 2: (a), (b) fails the guide's own `--x` example and `--upload-pack` would take the next word as its program; Advocate 3: (a), and the bare push falls back to `origin` when no push key is set — taken: the bare-push check also requires git's fallback to equal the set remote). All three rejected (b) the pattern alone and (c) an import-time constant (`tasks/TASK_GUIDE_T321.md:117` "Read the env var at call time"). ⚠ decided for you — please review
5. `merge_gate_guard.py` `AUTHORISED_TASKS` gains T321 with the Supervisor's sign-off — RULE: .claude/hooks/tests/merge_gate_guard.py:22 ("A task that must touch the gate adds its ID to `AUTHORISED_TASKS` with the Supervisor's sign-off").
Checks: tests `python3 -m pytest .claude/hooks/tests/test_t321_admin_remote.py -q -p no:cacheprovider` (the guide's Verification Command) — `51 passed` at 65bb8cfe; gate suites (t321, admin_tag, admin_repo_allowlist, t317 x2, t354, t323, merge_gate_guard) `802 passed`; mutations on a `git archive` copy: M1 no origin fallback `1 failed`, M2 no leading `-`/`.` rule `3 failed`, M3 ls-remote origin `2 failed`, M4 push target origin `2 failed`, M5 URL origin `1 failed`, M7 proxy origin `1 failed`, M8 push URL origin `8 failed`; M6 (drop the upfront refusal) survives as an equivalent mutant (`_admin_push_target_refusal` fails closed with the same text); full suite: `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 65bb8cfe: `58 failed, 7871 passed, 24 skipped`; 57 are the same list as clean `main` in this environment; the 58th, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, ran while the main checkout took commits (as on T354) and passes alone (`9 passed`); no failure comes from the gate change; reviews: Reviewer (fresh context, qa-expert, 65bb8cfe) PASS with findings, P3 only (docstrings and comments still say `origin`; `a..b`/`x.lock` pass the pattern but fail closed at `get-url`); it re-ran the Verification Command `51 passed` and the neighbouring suites `823 passed`; Supervisor `code-review` 0 P0/P1/P2, 3 P3; `security-review` (temporary `origin/HEAD`, removed after; its built-in diff from the main checkout is empty, so the branch diff was read by hand) no findings; real run: the `github` push shape replayed by `test_ac2_admin_may_push_main_to_the_set_remote_after_its_merge` on real throwaway repos (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-25 T321: the `[admin]`/`[ticket]` push remote is `EASY_KIT_ADMIN_REMOTE` (default `origin`)
Not done: merge (admin: after the user's /verify pass); push (the user sets `EASY_KIT_ADMIN_REMOTE=github` in `.claude/settings.json` `"env"`: a settings change stays the user's); auto verify: ☐ blocked (session 91dc3f2b-5ced-463c-bb5f-9651588f3b65, commit 7118dc0e573221b66b7301287986602b1de9f0e9, log .claude/verify-runs/T321-7118dc0e5732.log); /verify (yours): ☑ pass (session a074ce56-6c68-4a4f-b8ca-c467af91efc9, commit 45aaaf7f3c696f4fb44fbc3f97f55477266546c1: the gate run as the harness runs it, in throwaway projects with real `github` and `origin` remotes; see `## Demonstration` WITNESS)
Paused: auto verify blocked twice (the run and its one retry, `### Admin tag` T306): the headless `/verify` would not drive the merge gate's `[admin]` path by hand (it needs a constructed board, transcript and verify pass, which only the test fixtures build) and gave no verdict line; merge nothing — run `/verify T321` yourself

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t321_admin_remote.py` (51): AC1 `test_ac1_unset_or_blank_setting_keeps_origin`; AC2 `test_ac2_*` (branch and `main` to `github` allowed, `origin` refused naming `github`); AC3 `test_ac3_*` (bare-push fallback and keys, push/fetch URL, own-remote, push-target hooks and `updateInstead`, `ls-remote` sha and proxy); AC4 `test_ac4_ticket_*`; AC5 `test_ac5_*` (7 bad values: admin and ticket pushes refused naming them, merge allowed, helpers fail closed); AC6 `test_ac6_*` (tracks.md both sections, `AUTO_MODE_LIMIT`). |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_t321_admin_remote.py -q -p no:cacheprovider` -> `51 passed` (65bb8cfe) |
| Negative cases hold | ☑ pass | Red run before the change: Demonstration BEFORE (`39 failed, 12 passed`). Mutations M1-M8 above (1 file, 1 line each, on a `git archive` copy): 7 killed, M6 equivalent. |
| verify | ☑ pass | /verify by the user, session a074ce56-6c68-4a4f-b8ca-c467af91efc9, commit 45aaaf7f3c696f4fb44fbc3f97f55477266546c1 |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Read: every former `ADMIN_REMOTE` reader (`_admin_push_branch`, `_origin_url`, `_own_origin_refusal`, `_admin_push_target_refusal`, `_remote_main`, `_main_push_refusal`, `admin_refusal` push/ticket branches, `AUTO_MODE_LIMIT`, the allowlist text), the test fixtures, `tracks.md` `### Admin tag` and `### Session tags`. `git diff --stat main...65bb8cfe`: 6 files, 424 insertions, 38 deletions; `.claude/settings.json` untouched. |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest -q -p no:cacheprovider -rf tests .claude/hooks/tests` at 65bb8cfe: `58 failed, 7871 passed, 24 skipped`; 57 are the same list as clean `main` in this environment; the 58th, `test_memory_usage_report.py::test_script_does_not_touch_the_real_repository`, ran while the main checkout took commits (as on T354) and passes alone (`9 passed`); no failure comes from the gate change |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: neither companion tool is installed for this task. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | No UI: hook-only change. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | No UI: hook-only change. |
| **UI: Responsiveness at target viewports** | ☐ N/A | No UI: hook-only change. |

---

## Demonstration

**BEFORE**: captured 2026-11-25T05:12:59Z on `5054139f` (before any implementation commit), `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t321_admin_remote.py`:

```
39 failed, 12 passed in 7.37s
```

Failing: every AC 2–6 case (the `github` push allowed and `origin` refused naming `github`; each `github`-side check; `[ticket]` to `github`; every bad value refused naming it, helpers failing closed; the docs and refusal text). Passing: AC 1 (unset/empty/blank keep `origin`), the AC 3 refusals that hold by accident today (the gate refuses any non-`origin` remote), and AC 5's merge-unaffected cases.

**AFTER**: `python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t321_admin_remote.py` at 65bb8cfe: `51 passed` (the 39 BEFORE failures pass; the 12 that passed still pass).

**DELTA**: with `"EASY_KIT_ADMIN_REMOTE": "github"` in `.claude/settings.json` `"env"`, `[admin]` pushes `main` and the task branch to `github` and refuses `origin`; unset, nothing changes; a bad value refuses every push and names it.

**WITNESS**: the fresh-context Reviewer re-ran the Verification Command; the auto verify run is the independent check (`memory/event-trace/T321.jsonl`). The user's `/verify T321` (2026-11-25, session a074ce56-6c68-4a4f-b8ca-c467af91efc9) drove the hook as a subprocess with one PreToolUse Bash event each, in throwaway kit projects with real bare `github` and `origin` remotes: with `EASY_KIT_ADMIN_REMOTE=github` the gate allowed `git push github feat/t900-x` and, after the merge, `git push github main` (both then pushed for real: the `github` refs moved), and refused `origin`, a bare push with no push key, and `remote.pushDefault=origin`; unset, blank or `origin`: `origin` allowed, `github` refused (as before); `--upload-pack=touch …`, `.`, `-x`, `git hub`: every push refused naming the value, no canary file created, the `[admin]` merge still allowed.

## Supervisor Stage 4 runs

- `code-review` (Supervisor, range `main...65bb8cfe`): P0 none, P1 none, P2 none. P3: under a bad setting the `[ticket]` merge refusal and the direct-call `_main_push_refusal` text read `None` for the remote (still refused); the `_own_origin_refusal` and `_remote_main` docstrings still say `origin`; M6 equivalent mutant. Lane: `lane: C2, 5 files, 412 lines, FITS; unpredicted: (all 5 — the checker does not parse this guide's bullet list)`. Stale-reference sweep: the remaining `origin` wording in `tracks.md` is covered by the new "reads as that name" lines.
- `security-review` (built-in, temporary `origin/HEAD`, removed after; branch diff read by hand, rules `skills/code-review/references/security-reviewer.md`): argv injection through the setting — rejected (no leading `-`/`.`, list argv, no shell); bare-push fallback to `origin` — closed and tested; helper fail-open on direct call — rejected (each fails closed, tested); refusal echo — `_shown()` escapes it. No findings.
- Accepted P3s (follow-ups, not fixed here, so the reviewed commit stands): the `None` wording; the two docstrings.
