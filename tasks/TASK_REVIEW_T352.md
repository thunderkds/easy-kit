# TASK_REVIEW — T352: rename the kit's Stage 5 skill `ship` to `release-plan`

> Sibling of `tasks/TASK_GUIDE_T352.md`. Filled at Stage 4/5.

---

## Auto decisions

Mode: auto
1. The new name is `release-plan` — RULE: `PROJECT_KANBAN.md` § Todo, row T352 (user: "yes, register T352 with release-plan")
2. No compatibility alias named `ship` — RULE: `tasks/TASK_GUIDE_T352.md` § Requirement, Out of scope ("an alias is the clash itself")
3. History keeps the old name (`tasks/`, `memory/`, `docs/archive/`, `docs/brainstorming/`, ADRs/DDRs/PRDs, `CLAUDE_LEGACY.md`, the site's Change log) — RULE: `tests/test_stage_names.py:41` "D7: history stays"
4. The verb *ship* in prose stays; only the skill's name changes — RULE: `AGENTS.md` § Writing Principles (ASD-STE100), One Term, One Meaning
5. The clash is real in interactive sessions, not in headless `claude -p` (probes 1 and 2, headless haiku, $0.008, listed the kit's `ship`) — FACT: tasks/TASK_GUIDE_T352.md:21 "In the interactive session of 2026-11-24 the skill list shows `ship-local (ship)`"
6. `update.sh` is not changed: SC11 pins its existing removal of an untouched `skills/ship/` — FACT: lib/harness-update.sh:500 "removed '$_unit' — upstream no longer ships it and you never edited it."
7. AGENTS.md grew 56 bytes past its byte cap: raise the cap 22414 -> 22470 with a recorded reason, cut no other doctrine — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task"). The Advocates disagreed (Advocate 1: raise the cap, the size change is the rename itself; Advocate 2: cut the duplicate Non-Claude CLIs sentence, 78 bytes, and lower the cap to 22392); the written rule picks Advocate 1, so it is not an unsettled Debate
8. Fix both Reviewer P2s (`scripts/token_audit.py` stage map key; `tests/test_auto_mode.py` `USER_STOP` pin) and the P3 leading-word example; the oracle gains the `"ship":` key form and a stage-map assertion — RULE: docs/claude-md/pipeline-stages.md § Stage 4: Review ("A later code fix needs a new reviewer spawn on the new commit")
Checks: tests `python3 -m pytest -q tests/test_t352_release_plan_rename.py` — 5 passed; supervisor `code-review` + `security-review` Skill runs on `main...abfec0ed` — no finding beyond the Reviewer's; `sh tests/test_update_removals.sh` — 34 passed, 0 failed; full suite before the fix round — 6 failed, 7797 passed (5 known `MEMORY.md` budget failures on `main`, 1 order-dependent flake that passes alone); reviews `code-review` — 0 P0/P1, 2 P2 (fixed), 2 P3 (both fixed in the fix round); round 2 (fresh Reviewer, `abfec0ed`): 0 P0/P1/P2, 2 P3 on this record (fixed); `security-review` — no finding; real run `claude -p` haiku probe in a temp project — printed `release-plan: Post-merge release planning (not Claude Code's \`/ship\`, which` (auto-checked, not /verify)
Memory: `memory/decisions.md` — 2026-11-24 T352: the Stage 5 skill is `release-plan`, not `ship` (trap: a rename oracle must grep every form the old name takes); `memory/codebase-map.md` — `skills/ship` lines → `skills/release-plan`; `memory/MEMORY.md` not touched: already over its 42,000-char budget (43,135), a `/compact-memory` job
Not done: merge (admin: after the auto verify pass); auto verify: running (T182)
Paused: auto-mode check failed — extended track, but the trace has no `code-review` Skill call (Stage 4 runs in auto mode); Risk Medium, but the trace has no `security-review` Skill call [report b0c82861f846]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_t352_release_plan_rename.py` (5 tests: AC 1, 2, 2 stage map, 3, 5) — `5 passed`; `tests/test_update_removals.sh` SC11 (AC 4) — `34 passed, 0 failed` |
| Verification command run | ☑ pass | `python3 -m pytest -q tests/test_t352_release_plan_rename.py` -> `5 passed (4 at round 1, + the stage-map test in the fix round) in 0.11s`; `sh tests/test_update_removals.sh` -> `PASS: sc11: untouched skills/ship removed, skills/release-plan installed` ... `35 passed (4 at round 1, + the stage-map test in the fix round), 0 failed`; `python3 scripts/gen_kit_explorer.py --check` -> rc=0 (site data current). |
| Negative cases hold | ☑ pass | red run 2026-11-24T16:24:41Z at `8083fb78`: 4 failed; the stage-map test and the `"ship":` form failed before the fix (`2 failed, 3 passed`); mutation: deleting "Not in auto mode: `release-plan` runs after the merge." from `docs/claude-md/pipeline-stages.md` makes `test_ac3_every_pipeline_stop_names_its_auto_rule` fail (`1 failed`), restored |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewer: T352, fresh context, `code-review` + `security-review` on `main...11b4aad5`: 38 files; blast radius = every file naming the skill (`git grep` for `` `ship` ``, `skill: "ship"`, `skills/ship`, `"ship"`, `/ship` outside history), the 2 hook docstrings, the 15 repointed pin tests, `plugin/skills` symlink, MANIFEST `skills codex=.codex/skills`, `lib/harness-update.sh` removal path (SC11). Findings below. |
| Full smoke suite still green (no regression) | ☑ pass | Reviewer run `python3 -m pytest -q -p no:cacheprovider tests .claude/hooks/tests` in the worktree: `6 failed, 7797 passed, 5 skipped, 126 subtests passed in 405.06s`. 5 are the known memory-budget failures (`test_memory_channel_and_budget.py` x4, `test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget`). The 6th, `test_merge_gate_companion_rows.py::test_a_tilde_report_path_is_expanded`, passes alone in the worktree and on `main` (`1 passed in 0.07s`): order-dependent flake, not the rename. `sh tests/test_update_removals.sh`: `34 passed, 0 failed`. |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier not run for this task |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | no UI component: the site change is text only (skill name in 6 chips/lines) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | no markup or style change; same classes |
| **UI: Responsiveness at target viewports** | ☑ N/A | text length +8 chars in chips; no layout change |

---

## Demonstration

**BEFORE** (verbatim prior content, `AGENTS.md:153` at `main` `8af7a081`): `merge + close Kanban, \`Skill({ skill: "ship" })\` for release planning.` — and `skills/ship/SKILL.md:2` `name: ship`. Red run 2026-11-24T16:24:41Z: `tests/test_t352_release_plan_rename.py` 4 failed (commit `8083fb78`).

**AFTER**: `merge + close Kanban, \`Skill({ skill: "release-plan" })\` for release planning.`; `skills/release-plan/SKILL.md:2` `name: release-plan`. Headless probe 3 (haiku, $0.0036): `release-plan: Post-merge release planning (not Claude Code's \`/ship\`, which`.

**DELTA**: Stage 5's `Skill({ skill: "release-plan" })` reaches the kit's release planner in an interactive session, where Claude Code's `/ship` used to shadow it.

**WITNESS**: Supervisor session 832e4e7c, 2026-11-24 (red run, probes); `Reviewer: T352` (fresh context) confirmed the AFTER at `11b4aad5`


---

## Stage 4 review (Reviewer: T352, fresh context)

Verdict: **pass with 1 P2 and 1 P2 (test), 2 P3**. No P0/P1. The rename itself is complete and correct; the two P2 items are places the AC 2 regex did not reach.

### Findings

- **P2 — `scripts/token_audit.py:53`** `"ship": "stage-5"` still names the old skill. A live file (`scripts` is in the test's `LIVE` list) that AC 2 / `SKILL_NAME` cannot catch, because the form `"ship":` is not in the regex. Failure: `Skill({ skill: "release-plan" })` trace records are no longer mapped to `stage-5` (`STAGE_MAP` lookup at line ~66 falls through), so the token audit books Stage 5 release-planning cost to no stage. `tests/test_stage_names.py::test_d6_token_audit_tags_use_stage_0_and_stage_1` checks only stage-0/1 keys, so nothing catches it. Fix: rename the key to `"release-plan"`; add `"ship"` quoted-key form (`"ship":`) to `SKILL_NAME` and one assertion `m["release-plan"] == "stage-5"` so the gap stays closed.
- **P2 (vacuous pin) — `tests/test_auto_mode.py:435`** `USER_STOP` still ends `|skill: "ship"`. Before the rename that alternative selected exactly 1 chunk of `docs/claude-md/pipeline-stages.md` (the Stage 5 item 6 block, which says "Not in auto mode"); after the rename it selects 0 (measured: 1 chunk on `main`, 0 now). `test_ac3_every_pipeline_stop_names_its_auto_rule` therefore no longer checks that the release-plan stop names its auto rule: delete the "Not in auto mode" sentence and the test stays green (the `>= 14` count still holds). The repoint in this commit missed this one. Fix: `skill: "release-plan"`.
- **P3 — `memory/codebase-map.md:182-183`** still lists `./skills/ship` and `./skills/ship/SKILL.md`. Outside the guide's scope list (memory is history except the diff-driven pass), so the Supervisor's post-merge memory pass should refresh it; `skills/ship` does not exist after this change.
- **P3 — `skills/write-better-skill/SKILL.md:72` and `site/docs.html:2336`** keep `*ship*` as a leading-word example "(e.g. *wake*, *learn*, *ship*, ...)". Harmless (a concept word, not the skill name) but now points at no skill; swap for `*release-plan*` or another live skill if wanted. Not a gate.
- **Note — SC11 (`tests/test_update_removals.sh`)** builds its own synthetic upstream (adds `skills/ship`, then `git mv` to `release-plan`), so it proves the existing `lib/harness-update.sh:500` removal and warning for this skill pair, and would also pass on `main`. That matches the guide ("pins, does not change") and AC 4 as written; it does not test the real kit tree. Acceptable. Both branches (untouched removed + log line `removed 'skills/ship'`; edited kept + `no longer ships 'skills/ship/SKILL.md'` warning) are asserted.

### Checks asked for

- AC 1-3, 5 each covered by `tests/test_t352_release_plan_rename.py` (4 tests, red on `main` per the Demonstration, `8083fb78`); AC 4 by SC11; AC 6 by the suite run above. AC 2 regex has the gap named in the first P2 (other forms, e.g. `"ship":` keys).
- No live file keeps the skill name: `git grep` outside `tasks/ docs/archive docs/brainstorming docs/ddr docs/adr docs/prd CLAUDE_LEGACY.md PROJECT_KANBAN.md` leaves only the P2/P3 items above, the verb in prose (`README.md:5`, `skills/release-plan/SKILL.md:12,17,62`), the `/ship` mention in the new description, and pin-test text that cites the old name on purpose. No history file is in the diff (`git diff --stat`: only T352's own `tasks/` files).
- Repointed pins still bite: `test_agents_md_primary.py` (explicit old->new pairs), `test_stage_names.py` row 19 (`replace(...).replace("`ship`", ...)` is applied to the expected text only, the live row must still equal it), `test_tracks.py` gates 2-6, `test_t307_admin_end_to_end.py` (`renamed` base keeps the frozen hash on the unrenamed text, then checks the renamed one), `test_site_story.py` (4 hashes added to a whitelist that must still be a subset of the baseline), `test_site_visual_first.py` (hash and prefix repoints), `test_agent_guide_dedup.py` baseline ref `7863a113` (a real merge commit history is used on this repo, so the ref survives the merge), `AGENTS_MD_BYTE_CAP` 22414 -> 22470 (+56 = 7 x 8 bytes, as recorded). The one that went vacuous is `test_auto_mode.py:435` (P2).
- Plugin: `plugin/skills -> ../skills` symlink, `plugin/skills/release-plan/SKILL.md` resolves (AC 5 test). Codex projection: MANIFEST `skills codex=.codex/skills` copies the folder by name; `tests/test_harness_projection.sh` repointed to `release-plan`; the skill stays under the Codex cap (`test_t307` `test_ac8_skill_stays_under_codex_cap` only lists `SKILL_ROWS`; the T352 skill body is unchanged apart from 2 lines). Site data: `scripts/gen_kit_explorer.py --check` rc=0.
- `lib/harness-update.sh`, `.claude/settings.json`, `plugin`, `MANIFEST`, `setup.sh`, `update.sh`: not in the diff, as the guide requires.

### Security review (Risk Medium)

No finding. The diff renames a skill folder and its name in docs, 2 hook docstrings, pin tests and generated site HTML. No hook code, permission, `settings.json` allow/deny entry, input-validation path, network call or secret handling changes; no `Skill(ship)` permission rule exists to go stale (`git grep` of `.claude/settings.json`, `.claude-plugin`, `plugin/hooks`, `commands`: no hit). The update path only removes `skills/ship` when its hash matches the shipped one (existing `lib/harness-update.sh:500` logic, SC11 asserts the edited copy is kept), so a user's own edits are not deleted. SC11 writes only under `$WORK` temp dirs. The removed old skill name leaves no alias, so no shadowed-skill ambiguity remains.


---

## Stage 4 review — Round 2 (Reviewer: T352, fresh context, commit `abfec0ed`)

Scope: fix-round diff `57ec372f...abfec0ed` (8 files: `scripts/token_audit.py`, `tests/test_auto_mode.py`, `tests/test_t352_release_plan_rename.py`, `skills/write-better-skill/SKILL.md`, `site/docs.html`, `memory/codebase-map.md`, `memory/decisions.md`, this record) and the whole task `main...abfec0ed`. Method: the `Skill` tool is not in this reviewer's tool list, so the `code-review` and `security-review` checklists were applied by hand; the review is of the diff, with the commands below run in the worktree.

Verdict: **pass. 0 P0, 0 P1, 0 P2, 2 P3.** All four round 1 findings are fixed.

### Round 1 findings, one by one

| Round 1 finding | State | Evidence |
|---|---|---|
| P2 `scripts/token_audit.py` stage map | Fixed | Line 53 is now `"release-plan": "stage-5"`. `git grep` of `"ship"` in `scripts/` and `.claude/hooks/` code: no hit (only comments and prose verbs). |
| P2 `tests/test_auto_mode.py` `USER_STOP` pin | Fixed | `USER_STOP` now ends `skill: "release-plan"`. Measured: that alternative selects 1 chunk of `pipeline-stages.md` (item 6, "Post-merge release planning"); `USER_STOP` finds 19 chunks in all. Mutation: delete "Not in auto mode: `release-plan` runs after the merge." and `test_ac3_every_pipeline_stop_names_its_auto_rule` fails (`1 failed, 118 passed`); file restored, worktree clean. |
| P3 leading-word example | Fixed | `skills/write-better-skill/SKILL.md:72` and `site/docs.html:2336` now say `*release-plan*`. `python3 scripts/gen_kit_explorer.py --check` -> rc=0 (site data matches the skill text). |
| P3 `memory/codebase-map.md` | Fixed | `./skills/release-plan` and `./skills/release-plan/SKILL.md` replace the two `skills/ship` lines, in sorted position. |

### New oracle test fails without the fix

`test_ac2_token_audit_books_release_plan_to_stage_5` and the `"ship":` alternative in `SKILL_NAME`. Mutation: `sed` the key back to `"ship": "stage-5"` in `scripts/token_audit.py`, run `python3 -m pytest -q tests/test_t352_release_plan_rename.py` -> `2 failed, 3 passed`: `test_ac2_no_live_file_names_the_skill_ship` (regex form) and `test_ac2_token_audit_books_release_plan_to_stage_5` (stage-map assertion) both fail. File restored. Unmutated: `5 passed`.

### Regression runs (reviewer, worktree)

- `tests/test_t352_release_plan_rename.py tests/test_auto_mode.py tests/test_stage_names.py` -> `140 passed in 1.01s`.
- `tests/test_site_story.py tests/test_kit_explorer_data.py tests/test_site_content.py tests/test_claude_md_slim.py tests/test_site_visual_first.py` -> `239 passed in 1.63s`.
- Full suite not re-run: the fix round changed one dict key, one regex, two prose words and generated site text. The round 1 full run (`6 failed, 7797 passed`; 5 known memory-budget failures on `main`, 1 order-dependent flake) stands for everything else.

### Findings

- **P3 — `tasks/TASK_REVIEW_T352.md` Evidence row "Verification command run"** still reads `4 passed in 0.11s`; the test file now has 5 tests (the "New test(s)" row and `Checks:` say `5 passed`). Stale count only; refresh to `5 passed` at close-out. Not a gate.
- **P3 — `tasks/TASK_REVIEW_T352.md` `Checks:` line** says "2 P3 (both fixed in the fix round); round 2 (fresh Reviewer, `abfec0ed`): 0 P0/P1/P2, 2 P3 on this record (fixed)". The `memory/codebase-map.md` P3 is fixed in this commit too (the `Memory:` line says so), so both P3s are fixed. Wording only.
- **Note (not a finding)** — `test_ac2_token_audit_books_release_plan_to_stage_5` finds the map with `next(v for ... v.get("verify") == "stage-5")`. If a later edit drops `verify: stage-5` the test raises `StopIteration` instead of a clean assert; it still fails, so the guard holds.

### Security review (Risk Medium), fix-round diff

No finding. The diff changes one dict key in an audit script (`scripts/token_audit.py`, a read-only trace summariser: no input parsing, network, shell or secret change), a test regex and a test that loads that script by path with `importlib` (path built from the repo `ROOT`, no user input), two prose words, generated site text and memory/record files. No hook, permission, `settings.json`, update-path or file-deletion logic changed. `lib/harness-update.sh`, `MANIFEST`, `plugin` and `.claude/settings.json` are not in the diff. The task as a whole keeps the round 1 security result: no alias named `ship`, so no shadowed-skill ambiguity; an edited `skills/ship/` is kept on update.

Untouched, as asked: `## Auto decisions` and the `verify` row. No code changed.
