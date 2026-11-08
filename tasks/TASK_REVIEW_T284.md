# TASK_REVIEW — T284: `[admin]` tag — auto mode plus merge and push after a passed verify

> Sibling of `tasks/TASK_GUIDE_T284.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` tag,
`docs/claude-md/tracks.md` `## Auto mode`). To use it, copy the block below out of this comment, to this
place, and replace every <...>. Keep `Mode: auto` as its first line, exactly as written: T182's hook reads
it. Write it to this file before the run ends; the chat message is a copy, not the report. The same
block is the Supervisor's final chat message. It is not the `delivery-report` page and not
Evidence. A taste decision (what the user wants) also ends with the flag. Write `DEBATED` only when ≥2
Advocate `Agent` calls ran for that question, naming each Advocate's option. A decision with no Advocates is
labelled `RULE`, `FACT` or `SAFER OPTION`, never `DEBATED`. A decision flagged `⚠ decided for you` is a choice, and is never labelled `FACT`. A
safety action a rule requires (for example the backup before a delete) is `RULE` without the flag.
At Risk Medium or High, a `RULE:` counts only when it names a written rule (`path:line`,
`path § <heading>`, or `docs/claude-md/tracks.md` `### <section>`), and a `FACT:` needs a Citation
(`path:line "quoted text"`); without one it is a choice and must be `DEBATED`. Good: `2. backed up the CSV
— RULE: `docs/claude-md/tracks.md` `### Stops that stay``. Bad: `1. kept recurring.csv — RULE: Surgical Changes`.
`Memory:` records the diff-driven memory pass you run before you stop: each entry written, or `nothing new`.
After an auto verify pass the hook, never you, adds `Closed: row moved to Done <date> — …` and moves the row,
or adds `Paused: done not moved — <reason>`. It moves the row only when this block holds `Mode: auto`, a
numbered decision, `Checks:`, `Memory:`, the `Not done:` auto verify slot with its result, and `Not done:`
naming the merge — no `<...>` left (`docs/claude-md/tracks.md` `### Auto close-out`).

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours)>

-->

## Stage 4 fix round (2026-11-08)

By common-infrastructure on `feat/t284-admin-tag`. Code commit `affa1881`, docs commit `c566b2b6`, pin repoint `5ec5ea4a`. Every
fix was tested first: 22 new tests red at 2026-11-08T00:28:59Z (HEAD `d895d202`), then green. The attack
experiments in `scratchpad/t284sec/test_t284_attacks.py` are reused as red tests in
`.claude/hooks/tests/test_admin_tag.py` (`test_p0_*`, `test_p1_*`, `test_p2_*`).

| Finding | What was done |
|---|---|
| P0 — `main` push publishes unverified commits | Fixed. `_main_extra_commits`: `git rev-list origin/main..main --not <tip>` must be empty (fast-forward) or exactly one merge commit with parents `origin/main` and the tip; else blocked with "`main` carries commits besides the merge of <branch>: <shas>". No `origin/main` ref means blocked. Tests: commit after the merge, commit before the merge, cherry-pick copies, reset after a merge that never ran, no remote ref; fast-forward allowed. Mutation M5 (check off): 2 P0 tests red. |
| P1 — any write/touch/spawn binds a task (AC 7) | Fixed. Binding is now only (a) a task ID the request names with no negation before it in its clause (`_named_tasks`), or (b) exactly one task whose `tasks/TASK_GUIDE_<ID>.md` was first added (any ref) after the request (`_guides_added_since`). The `worked_on` binding is gone. Tests: touch in worktree, touch/Write of the guide, `Agent` spawn do not bind; one guide added after the request binds; two bind neither; "do NOT merge T900" / "don't merge T900" do not bind; "merge T900 and T950" binds. M6 (negation off): 2 red; M7 (any number of new guides): 1 red. |
| P3 — negated mention | Fixed for the plain forms above; the limit (a plain clause reading, not a parser) is documented in `### Admin tag` Known limits. |
| P1 — forged transcript line | Documented in `### Admin tag` Known limits, in the same wording and trust root as the `/verify` transcript limit. No code fix. |
| P2 — any remote name | Fixed. A named remote must be `origin`; a bare push needs `branch.<b>.pushRemote`, `remote.pushDefault` and `branch.<b>.remote` unset or `origin`. M8: 2 red; M9: 3 red. |
| P2 — blocked/failed merge counts as the merge | Fixed. `session_work.merge_calls` pairs each `Bash` call with its `tool_result`; only a call whose result is present and not an error counts. Tests: error result, no result. M10: 3 red. |
| P2 — originless / sidechain entry ends the `[auto]` window | Fixed. `request_text` skips `isSidechain`; for the gate `latest_request` reads only `origin.kind` "human" entries (decision pinned by `test_p2_decision_an_originless_auto_request_is_not_read_by_the_gate`). M11: 2 red; M12: 2 red. |
| Code-review — 7 surviving mutants (a)-(g) | Fixed: one test each (`test_mutant_a_*` … `test_mutant_g_*`). They pass on the real code; each targets the named mutant. |
| AC 10 mutation test could not fail | Fixed: `check_ac10(text)`; the real text passes, the mutated text must raise (`pytest.raises`). |
| `pull` missing from `### Never in auto mode` | Fixed in `tracks.md` and the AGENTS.md never-list (`never merges, pulls, pushes, …`, +7 bytes); pins in `tests/test_auto_mode.py` and `tests/test_auto_verify.py` repointed. `pipeline-stages.md` has no such list. |
| Stale text (LR-0005) | Fixed: `site/docs.html` lane label "Stays yours with [auto]"; `PROJECT_SPEC.md` Auto verify and Auto close-out rows; both templates name `[admin]` and its `Not done: merge (admin: after the auto verify pass)`; `companion-setup`, `settings-setup`, `dotfiles` headings and `commands/init.md` write `[auto]`/`[admin]` (skills 2959 / 4865 / 5128 bytes, all under 8192); `tracks.md` lead "**Merge is automatic only under `[admin]`.**" (pin in `tests/test_tracks.py` repointed). `lib/auto_closeout.py:30` left: it says the close-out module never merges or pushes, which stays true. `site/index.html` lines 66 and 105 left unchanged on purpose: default-mode claims, and the page is at its 300-word cap. |
| Docs — `main` rule and limits | Fixed in `### Admin tag`: names `main` only, `origin` only, the merge-only shape, the binding rule, and four known limits. |
| P3 cheap ones | Fixed: `AUTO_MODE_PATTERNS` derived from `BLOCKED_PATTERNS` minus rebase; `ADMIN_MAIN_BRANCH` and `ADMIN_REMOTE` beside it; the two over-long docstring lines re-wrapped; `auto_tagged` docstring explains why `request_tagged` keeps the plain substring rule. |
| P3 follow-ups (skipped) | `parse_ts` consolidation across `auto_mode` / `session_work` / `stop_auto_mode_check`; `git -c core.hooksPath=… merge` under `[admin]` (the `-c` before `merge` is still accepted, as T211 allows). Recorded here, not done. |

Mutation controls M5-M12 ran in a scratch copy (each byte-changing, `bytes changed=True`), 2026-11-08T00:33:25Z.
In that copy `test_ac1_the_stop_check_*` also failed under every mutation, because the copy has no
`skills/` (the Advocate template the stop-check fixture reads). That is unrelated to the mutations.

## Stage 4 fix round 2 (2026-11-08)

By common-infrastructure on `feat/t284-admin-tag`. Code commit `cf034be7`, docs commit `83b889b3`, test commits
`f87ae711` (final HEAD). The reviewer's experiments (`scratchpad/t284sec2/test_r2_bypass.py`, B1-B11) are now
red-first tests `test_r2_*` in `.claude/hooks/tests/test_admin_tag.py`: 27 red at 2026-11-08T00:52:09Z (HEAD
`f46a72d3`), then green. The test fixture's `origin` is now a real local bare repo (`publish()`), so `ls-remote`
reads an honest remote.

| Finding | What was done |
|---|---|
| P0-a (B1, B1b) — local `origin/main` can be moved | Fixed. `_remote_main` reads `git ls-remote origin refs/heads/main` (argv list, no shell, 10 s timeout, `GIT_TERMINAL_PROMPT=0`); no local-ref fallback. Failure, timeout or no answer blocks with "cannot read the remote's real `main` …". Tests: `update-ref` and `fetch . +scratch:refs/remotes/origin/main` now blocked; honest no-ff merge against the bare remote allowed; empty remote blocked. M13 (local ref instead): 3 red. |
| P0-b (B3, B3b, B3c) — merge tree never checked | Fixed. `_main_push_refusal`: a merge commit must have parents [remote `main`, tip] and a tree equal to `git merge-tree --write-tree <remote main> <tip>` (git 2.53 here); a failed or conflicting merge-tree blocks. A fast-forward needs `main` == tip and the remote `main` an ancestor of it. Only a merge call that ran with `main` checked out counts. Tests: `--no-commit` + added file, `--amend`, `commit-tree` + no-op merge in the worktree, a merge call from the worktree; honest merge and fast-forward allowed. M14 (tree check off): 2 red; M15 (main checkout not required): 1 red. |
| P2 (1) — URL rewrites (B7) | Fixed. The push URL of `origin` must equal its fetch URL; `_push_config_is_plain` is reused with `ADMIN_PUSH_CONFIG_KEYS`, which adds `url.*.insteadOf`, `url.*.pushInsteadOf`, `remote.*.pushurl`, `remote.*.receivepack`, `push.followTags`, `core.hooksPath` (T197's narrowing keeps its own keys, unchanged). Tests: 6 keys × task-branch and `main` push, each with a passing control. M17 (T197 keys only): 8 red. M16 (URL equality off) first survived, because every URL change is also a refused key; added `test_r2_b7_the_push_url_check_holds_on_its_own` (config check stubbed open): M16 then 1 red. `remote set-url origin <attacker>` (both URLs changed) cannot be told apart and is a documented limit. |
| P2 (2) — negation after the ID (B9) | Fixed: a negation after the ID in the same clause also leaves it out; `hold`, `wait`, `later`, `postpone` join the word list. Tests: the 5 English cases. M18: 3 red (the "hold off" and "skip" cases are also caught by the before-ID check). Other languages stay a documented limit. |
| P2 (3) — forward-dated guide commit (B11) | Fixed: a commit dated later than now + 60 s is ignored when finding "first added after the request"; the docs say the date is git's own record. Test with `GIT_COMMITTER_DATE=2030-…`. M19: 1 red. |
| P2 (4) — `git -c` before merge/push | Fixed: any `-c` or `--config-env` before the verb is refused under `[admin]`. Tests: `-c core.hooksPath`, `-c user.name`, `-c push.default` before push. M20: 3 red. Repo-config `core.hooksPath` run by other git commands and scripts that call git are documented as out of reach. |
| P3 / docs | Fixed: stale comments in the gate's auto-mode block and `test_admin_tag.py` docstring; `### Admin tag` item 2 now states ls-remote, merge-tree, the `main` checkout and the URL/config/`-c` rules; Known limits add the run-record trust root (`verify_record.py`), git through `python3 -c` or a script (T211), `-s ours`, a `tool_result` with no `is_error`, and a trusted `origin` URL. AGENTS.md unchanged (zero bytes added this round). |
| B10 — `tool_result` without `is_error` | Documented (Known limits); not changed. |

Mutation controls M13-M20 ran in a scratch copy, each byte-changing (`bytes changed=True`), at 2026-11-08T01:50:31Z;
M16 again at 01:50:57Z after the isolating test was added.

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_admin_tag.py` (AC 1-10, SC 1-7b, Stage 4 P0-P2 and mutants (a)-(g)); repointed/narrowed pins: `.claude/hooks/tests/test_merge_gate_guard.py`, `.claude/hooks/tests/test_agent_guide_dedup.py`, `tests/test_stage_names.py`, `tests/test_site_story.py`, `tests/test_auto_mode.py`, `tests/test_auto_verify.py`, `tests/test_tracks.py`. HEAD `5ec5ea4a`, 2026-11-08T00:37:12Z: `python3 -B -m pytest .claude/hooks/tests -q -k "admin or auto or merge"` → `680 passed, 979 deselected in 19.72s` Round 2: `test_r2_*` (B1, B1b, B3, B3b, B3c, merge-on-main, B7 × 12 + URL isolation, B9 × 5, B11, `-c` × 3); final HEAD `f87ae711`: `test_admin_tag.py` `166 passed`. |
| Verification command run | ☑ pass | HEAD `f87ae711c420fe62c17e0e022d6848d70bc7ae96`. `python3 -B -m pytest .claude/hooks/tests -q -k "admin or auto or merge"` → `709 passed, 979 deselected in 21.42s` (2026-11-08T03:30:59Z). `python3 -B -m pytest .claude/hooks/tests/ tests/ -q` → `FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid` / `1 failed, 3608 passed, 25 subtests passed in 194.51s (0:03:14)` (2026-11-08T03:34:14Z). The one failure is T283's own report test and failed before any T284 change. |
| Negative cases hold | ☑ pass | Red before the change: `55 failed, 15 passed` (BEFORE, 2026-11-07T23:34:41Z). Mutations in a scratch copy, each byte-changing (`diff`/`cmp` exit 1): M1 passed-verify check → `if False` (2026-11-07T23:55:17Z): `3 failed` (all sc3 tests); M2 push-shape check → T197 resolver (23:55:34Z): `6 failed` (sc7 force, f, lease, plus, dst-other, no-verify); M3 tracks.md AC 10 sentence removed (23:59:45Z): `1 failed` (`test_ac10_admin_tag_section_states_...`); M4 merge-happened check removed for the `main` push (2026-11-08T00:05:28Z): `2 failed` (`test_sc7b_main_push_without_a_merge_in_this_session_is_blocked`, `test_sc7b_a_merge_only_in_the_transcript_is_not_a_merge`). Not done by the Supervisor yet (Stage 4 own mutant). Stage 4 round: M5 P0 shape off → 2 red; M6 negation off → 2; M7 guide count off → 1; M8 remote off → 2; M9 bare-push remote config off → 3; M10 merge result off → 3; M11 originless request → 2; M12 sidechain request → 2 (2026-11-08T00:33:25Z, scratch copy, bytes changed). Round 2 (scratch copy, bytes changed): M13 ls-remote → local ref: 3 red; M14 tree check off: 2; M15 main checkout not required: 1; M16 URL equality off: 1 (after the isolating test); M17 admin config keys off: 8; M18 after-ID negation off: 3; M19 future dates trusted: 1; M20 `-c` refusal off: 3. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | Final HEAD `f87ae711`: `1 failed, 3608 passed, 25 subtests passed`; the failure is pre-existing (T283). `sh tests/test_readme_current.sh` → `FAIL: AC2: could not parse any skill names from README's Codex-skip bullet list` on this branch and on `main` `4c076b6c` (read-only run in the main checkout): pre-existing. |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component: the site change is two text sentences and one list item in `site/docs.html`, no layout, style or component change; site tests `218 passed`. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured by common-infrastructure in `/home/hungnguyenhuu/workspace/pets/wt-t284` at
HEAD `faa5180f` (no implementation commit yet; only the new test file existed, uncommitted).

The guide's verification commands, before any change:

```
$ date -u; python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"
2026-11-07T23:27:33Z
542 passed, 979 deselected in 20.19s
$ python3 -m pytest tests -q
1 failed, 1920 passed in 169.77s (0:02:49)
FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid   <- pre-existing, T283's own report (not this task)
2026-11-07T23:30:44Z
```

The new tests for AC 1-9, written first, before any implementation:

```
$ date -u; python3 -m pytest .claude/hooks/tests/test_admin_tag.py -q
2026-11-07T23:34:41Z   (HEAD faa5180f)
55 failed, 15 passed in 1.40s
```

The core of the red run: with a passed, hook-written auto verify and the request `do it [auto]`,
today's gate returns no block (`None`) for `git merge`, `git push` and `git pull` of the task branch.
"Never in auto mode: merge, push" was doctrine only; the gate did not read the tag at all:

```
$ date -u; python3 -m pytest ".../test_admin_tag.py::test_sc4_auto_only_with_a_passed_verify_stays_blocked" -q
2026-11-07T23:34:49Z
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[merge] _________
E       AssertionError: None
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[push] __________
E       AssertionError: None
_________ test_sc4_auto_only_with_a_passed_verify_stays_blocked[pull] __________
E       AssertionError: None
```

The 15 that passed before are the controls and negative cases that hold today (an exact-tag miss
such as `[Admin]` is trivially not admin when nothing reads the tag; a hand-typed `☑ pass` row
passes the plain gate; a rebase is not blocked).

**BEFORE refresh (2026-11-08)**: AC 10 (Supervisor starts the auto verify run, merges only on a pass) and the
AC 8 change (`[admin]` may push `main` after its own merge) came after the capture above. Their tests were
written first and seen red before the code: the 7b allowed case failed `4 failed` at 2026-11-08T00:04:45Z
(`main names no single task`); AC 10 is a docs statement, and its tests failed until the `tracks.md` text existed.

**AFTER**: HEAD `2a7d4545`, run by common-infrastructure:

```
$ date -u; python3 -m pytest .claude/hooks/tests -q -k "admin or auto or merge"
2026-11-08T00:07:49Z
644 passed, 979 deselected in 24.92s
$ python3 -m pytest .claude/hooks/tests/ tests/ -q
FAILED tests/test_spike_report_t283.py::test_the_real_report_is_valid - Asser...
1 failed, 3543 passed, 25 subtests passed in 238.38s (0:03:58)
2026-11-08T00:15:00Z
```

`test_sc4_auto_only_with_a_passed_verify_stays_blocked[merge|push|pull]`, red in the BEFORE, now pass: with
`[auto]` the gate blocks with `Auto-mode gate — cannot push/merge`.

**DELTA**: The user can write `[admin]` so the Supervisor runs the task in auto mode, starts its auto verify run, and only after a hook-proven pass merges and pushes the task branch and then `main`; with `[auto]` alone the gate now actually blocks merge, push and pull.

**WITNESS**: Not yet witnessed. The runs above are by common-infrastructure (the implementing agent),
2026-11-07T23:27Z to 2026-11-08T00:15Z, attributed to T284 in `memory/event-trace/T284.jsonl`. The implementing
agent alone does not witness: the Supervisor's Stage 4 rerun, or the headless auto verify run, fills this.
