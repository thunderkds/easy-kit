# TASK_REVIEW — T286: AGENTS.md byte-size ratchet, and a list of cut candidates

> Sibling of `tasks/TASK_GUIDE_T286.md`. Everything here is **filled by the reviewer at Stage
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

## Auto decisions

Mode: auto
1. Set the byte cap to the size of `AGENTS.md` now (21402 bytes) and leave `AGENTS.md` untouched; after T284 merges, the cap is re-measured at merge time (merge order T284, then T286) — RULE: `tasks/TASK_GUIDE_T286.md` § Approach
2. Listed 18 cut candidates and cut nothing — RULE: `tasks/TASK_GUIDE_T286.md` § Requirement (Out of scope: a cut needs the user's pick)
3. Left the two 32,768-byte Codex-ceiling checks (`tests/test_agents_md_primary.py:216`, `tests/test_auto_mode.py:305`) unchanged — SAFER OPTION: they are a ceiling, not a ratchet ⚠ decided for you — please review
4. Kept the cap number in the test name (`test_agents_md_is_at_most_21402_bytes`), so each future ratchet renames it — RULE: `tasks/TASK_GUIDE_T286.md` § Acceptance Criteria (row 1 names `<N>` in the test name)
Checks: tests `python3 -m pytest tests/test_claude_md_slim.py -q` — 8 passed; full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` — 1 failed, 3445 passed (the one failure is `tests/test_spike_report_t283.py`, expected until T283 merges); reviews code-review — 0 P0, 0 P1, 0 P2, 1 P3 (cap number in the test name, kept); real run `python3 -B -m pytest tests/test_claude_md_slim.py -q` — printed `8 passed` (auto-checked, not /verify)
Memory: memory/decisions.md — T283–T288 Karpathy spikes (four adopted, three dropped) and T284 `[admin]` entries; memory/learnings.md — parallel agents share one step budget, stale `.pyc` in mutation controls, docs-only task SKIP written as blocked
Not done: merge (yours); auto verify: running (T182)

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_claude_md_slim.py` (commit `43c8d814`): `test_agents_md_is_at_most_21402_bytes` (AC 1), `test_byte_cap_fails_one_byte_past_the_cap_with_the_do_this_message` (AC 1, 2), `test_byte_cap_reads_bytes_not_lines` (AC 4), `test_byte_cap_counts_utf8_bytes_not_characters` (edge case). AC 3 = the cut table above; AC 5 = `git diff --stat main -- AGENTS.md` empty; AC 6 = see Cap measurement. |
| Verification command run | ☑ pass | 2026-11-08T00:18:20Z `python3 -m pytest tests/test_claude_md_slim.py -q` -> `8 passed in 0.04s`; `git diff --stat main -- AGENTS.md` -> empty; full suite `python3 -m pytest .claude/hooks/tests/ tests/ -q` -> `1 failed, 3445 passed, 25 subtests passed in 268.95s`. The 1 failure is `tests/test_spike_report_t283.py::test_the_real_report_is_valid` ("tasks/SPIKE_REPORT_T283.md is not written yet"): it fails the same way on the unchanged base (baseline run before my commit: `1 failed, 3441 passed`) because the report lives on branch `feat/t283-karpathy-spikes`; not caused by T286. |
| Negative cases hold | ☑ pass | Four byte-changing controls, each restored after (`PYTHONDONTWRITEBYTECODE=1 python3 -B`; a first attempt reused a stale `.pyc` because `sed` kept size and second, so it was discarded and redone). Real file one byte larger = cap 21401: `git diff -U0` shows `+AGENTS_MD_BYTE_CAP = 21401` -> `FAILED test_agents_md_is_at_most_21402_bytes`, `1 failed, 7 passed`. Cap raised to 21403: `FAILED test_byte_cap_fails_one_byte_past_the_cap_with_the_do_this_message`, `FAILED test_byte_cap_reads_bytes_not_lines`, `2 failed, 6 passed`. Helper counts `data.splitlines()` instead of bytes (`+    if len(data.splitlines()) <= AGENTS_MD_BYTE_CAP:`): 3 failed (`..._fails_one_byte_past...`, `..._reads_bytes_not_lines`, `..._counts_utf8_bytes_not_characters`), `5 passed`. Restored: `8 passed`. The in-test copy `RAW + b"x"` prints: `AGENTS.md is 21403 bytes, cap 21402. Lower the file (cut or move text to docs/claude-md/), or raise AGENTS_MD_BYTE_CAP in tests/test_claude_md_slim.py in the same commit with a recorded reason. A ratchet moves down by default.` |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | Left to the Supervisor (Stage 4). Change set: one test file (+45 lines) and this review file; `AGENTS.md` untouched; no hook, no `memory/`, no `settings.json`. |
| Full smoke suite still green (no regression) | ☑ pass | `3445 passed`; the one failure is pre-existing and unrelated (see Verification row). |
| **Companion score (easy-verifier)** | ☐ pass / ☐ fail / ☐ N/A | [`overall` and `change_risk` as the tool returned them, the scope, the ref, and the absolute path of the verifier report after a literal `report:` label — e.g. "overall 86 (>= 80), change_risk pass, scope changes, ref `main...HEAD`, report: `/home/me/.easy-verifier-reports/kit/score_changes_20261028T0530Z.html`". The gate reads the path that follows `report:` and nothing else, so with no label, or a path that is absent, the row is unscored — write ☑ N/A instead. ☑ N/A with a reason when neither companion tool was run: the merge gate blocks on ☑ fail only, never on an absent or N/A row] |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

---

## Cap measurement (AC 1)

- Cap: **21402 bytes** (`wc -c AGENTS.md` = 21402; 196 lines), a literal in `tests/test_claude_md_slim.py` (`AGENTS_MD_BYTE_CAP`), never computed at test time.
- Measured at: branch base `4c076b6c` (`main` at `8f00098c` has an identical `AGENTS.md`: `git diff HEAD main -- AGENTS.md` empty; the last commit that changed the file is `46c013fc`).
- Note for merge: T284 (the `[admin]` tag, unmerged) also edits `AGENTS.md`; after T284 merges, the Supervisor re-measures this cap at merge time (merge order: T284, then T286).
- Two older byte checks exist and stay unchanged: `tests/test_agents_md_primary.py:216` and `tests/test_auto_mode.py:305` cap `AGENTS.md` at 32768 B (the Codex 32 KiB ceiling). They are a ceiling with 11 KB of slack, not a ratchet. No doc says "the size test caps lines" (grep of README, `site/`, `docs/`, `agents/`, `skills/`, `templates/`): the only such text was the test's own docstring, now naming the byte cap (AC 6). `memory/learnings.md:1970` ("CLAUDE.md is at its 200-line cap") is a dated learning in a Supervisor-only file; not edited.
- Pin-test pre-flight (LR-0004): `AGENTS.md` and its text are untouched, so no pin test needs a repoint. Tests reading `AGENTS.md`: `test_agents_md_primary.py`, `test_auto_mode.py`, `test_tracks.py`, `test_response_standard.py`, `test_writing_principles.py`, `test_stage_names.py`, `test_agent_guide_dedup.py`, `test_vital_slice.py` (196-line cap), `test_memory_channel_and_budget.py`. Any cut below must repoint the ones named in its row.

## Cut candidates (AC 3, for the user to pick; nothing is cut)

Bytes are UTF-8 bytes of the live `AGENTS.md` (21402 B, lines as of `46c013fc`). The 15 text-only rules of the T283 inventory (section 7) are re-checked against the live file: all 15 anchors are present. The 10 hook or partial rows still hold: `settings.json` registers no `SessionStart` hook, and `pre_agent_validate_guide.py`, `stop_review_reminder.py`, `pre_bash_block_unsafe_merge.py`, `stop_auto_mode_check.py`, `stop_auto_verify.py` exist and are registered. `Rec` = recommendation.

| # | Rule (live lines) | Bytes | Rec | Reason |
|---|-------------------|-------|-----|--------|
| 1 | `wake` mandate (135-137) | 349 | keep | No `SessionStart` hook exists, so this text is the only trigger. Pinned by `test_claude_md_slim.py`. A hook is a separate task. |
| 2 | Track line sentences in `## Tracks` (142) | 319 | keep | The entry to the whole pipeline; pinned by `test_tracks.py`, `test_auto_verify.py`. The paragraph is 2143 B: see row 17. |
| 3 | Gate 2 complexity floor (173) | 283 | keep | Restated in `docs/claude-md/tracks.md` and the Cursor adapter, but `## Tracks` cites "a Gate 2 word" by name; a pointer here is the unreachable-channel failure of T103. |
| 4 | Gate 4 one project per KANBAN (177) | 288 | keep | Same as row 3: restated in `tracks.md`, but a Hard-Stop Gate must stay in the channel the Supervisor reads. |
| 5 | `migration-safety` mandatory (163) | 101 | keep | Small. Line 152 names the skill for DB changes but not "mandatory"; the bullet says that. |
| 6 | Task labels C0-C3 / Risk / Priority (161) | 171 | keep | Small; stated nowhere else in the doctrine channel. |
| 7 | Memory writes Supervisor-only (188) | 470 | move (part) | Keep the first sentence ("Supervisor-only writes", ~25 B). Move the hot-tier ratchet, slice and trigger detail (~440 B) to `docs/claude-md/memory-write-protocol.md`, which line 186 already points to. Repoint `test_memory_channel_and_budget.py`, `test_site_content.py`, `test_token_audit_format.py` if they pin "50,000". A hook for the rule is the better lock (`memory/` is not in `.claude/sensitive-paths.txt`). |
| 8 | No implementation code by the Supervisor (sentence in Gate 1, 171) | 62 | keep | Core of Gate 1; too small to matter. |
| 9 | Untrusted content (76-77) | 178 | keep | Security rule; restated in `templates/general-agent-template.md` for sub-agents, which the Supervisor does not read. Pinned by `test_untrusted_content_boundary.py`, `test_provider_adapters.py`. |
| 10 | `.claude/skills`, `.claude/agents` relative symlinks (sentence in 83) | 129 | keep | Load-bearing (AGENTS.md says so itself); `folder-structure.md` repeats it, but one sentence is cheap. |
| 11 | "Strictly follow this order. Never skip or reorder stages." (145) | 57 | cut | `docs/claude-md/pipeline-stages.md` says the same and the line keeps the pointer. Saves 57 B; low value either way. Check `test_stage_names.py` first. |
| 12 | Exact CLI + spawn command (165-166) | 180 | cut (half) | Two bullets say one thing. Merge into the first and cut the second ("Never assume the user knows how to run a particular CLI...", 92 B). `craft-spawn-prompt` and line 87 already cover the CLI list. |
| 13 | Karpathy principles (91-107) | 1909 | keep (table), move (Task Transformation Table, 433 B) | The table is a Permanent Rule that each role guide carries verbatim; pinned by `test_agent_guide_dedup.py`. The Task Transformation Table appears elsewhere only in `skills/tdd/SKILL.md` and is cited as "below" by the Goal-Driven row, so a move needs that row reworded. |
| 14 | Writing Principles ASD-STE100 (109-123) | 1507 | keep | User-approved rule (T169), pinned by `test_writing_principles.py` and `test_agents_md_primary.py`; the Cursor adapter keeps its own copy. |
| 15 | Response Standard (22-32, intro 17-20) | 1130 | keep | The 9 bullets are copied in `templates/general-agent-template.md` for sub-agents, but T103 showed the Supervisor never opened the template and broke the rules; the Supervisor copy must stay. Pinned by `test_response_standard.py`. |
| 16 | Self-monitoring for context overwhelm (34-42; text-only, not in the 25 inventory) | 675 | move | `skills/compact-advisor/SKILL.md` already holds the concrete check and quotes this rule. Move the rule's text into that skill and leave a one-line pointer (~120 B). Net ~550 B. The user must accept that the rule then loads only when the skill is opened (it fires "when noticed", so the trigger needs the line in `AGENTS.md`: keep the one sentence that names the trigger). |
| 17 | `## Tracks` paragraph (142; text-only) | 2143 | move (part) | Largest single paragraph (10% of the file). The `[auto]` and auto-verify sentences (~900 B) duplicate `docs/claude-md/tracks.md` `## Auto mode` and `### Auto verify (Stop hook)`. Pinned by `test_tracks.py`, `test_auto_mode.py`, `test_auto_verify.py`, `test_agent_guide_dedup.py`: a move repoints all four. Highest saving, highest cost. |
| 18 | `## Skills vs Agents` (46-71; text-only) | 2628 | move (part) | The stage index line (66) is 929 B and the role table 5 rows. Candidate: keep the role table and the `subagent_type` rule, move the stage index to `docs/claude-md/pipeline-stages.md`. Pinned by `test_stage_names.py`, `test_agents_md_primary.py`. |

Rows 1-15 are the inventory; 16-18 are paragraphs outside the 25 rules that the spike's four "text-only sections" cover, listed because they carry the bytes. Largest honest saving if the user picks: row 17 (~900 B), row 18 (~900 B), row 16 (~550 B), row 7 (~440 B), row 13's table (~430 B): about 3.2 KB, 15% of the file. Each cut lowers `AGENTS_MD_BYTE_CAP` in the same commit (the ratchet).

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-08T00:14:47Z by common-infrastructure, branch `feat/t286-agents-md-byte-ratchet` at `4c076b6c`, before any implementation commit; no byte test exists, only the line cap):
```
$ python3 -m pytest tests/test_claude_md_slim.py -q
....                                                                     [100%]
4 passed in 0.03s
$ wc -c AGENTS.md
21402 AGENTS.md
$ grep -n "bytes\|byte" tests/test_claude_md_slim.py
(no match: the file has no byte test)
```

**AFTER** (2026-11-08T00:18:20Z, commit `43c8d814`):
```
$ python3 -m pytest tests/test_claude_md_slim.py -q
........                                                                 [100%]
8 passed in 0.04s
$ wc -c AGENTS.md
21402 AGENTS.md
$ git diff --stat main -- AGENTS.md
(empty)
```

**DELTA**: A change that grows `AGENTS.md` by even one byte now fails a test whose message says to lower the file or raise the cap with a reason, and the user has a priced list of what could be cut or moved.

**WITNESS**: common-infrastructure agent (T286 run), 2026-11-08T00:14Z-00:19Z; the Supervisor re-derives it from `memory/event-trace/T286.jsonl` at Stage 4 (the implementing agent alone does not witness).
