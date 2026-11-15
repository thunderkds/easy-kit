# TASK_REVIEW — T[NNN]: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` or `[admin]` tag; with `[admin]`, the `Not done:` line names `merge (admin: after the auto verify pass)`,
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
numbered decision, `5. security-review re-check (Skill `security-review`, cf180bc4): 1 Medium, confirmed by an independent false-positive check (confidence 8) — a `\` in an Edit/Write path collapses onto an approved key; fix: build the approval key from the path as the OS sees it — RULE: skills/code-review/SKILL.md § Finding Classification (security finding, must fix before merge)
6. The same `\` gap in local mode (`path_forms` → `is_predicted`) is on `main` and outside this task — RULE: tasks/TASK_GUIDE_T314.md § Out of scope ("Any change to local board mode"); registered as T319
Checks:`, `Memory:`, the `Not done:` auto verify slot with its result, and `Not done:`
naming the merge — no `<...>` left (`docs/claude-md/tracks.md` `### Auto close-out`).
With `/verify (yours)`, your pass goes in the `verify` row below: Result `☑ pass`, Notes `/verify by the user, session <id>, commit <sha>`.

## Auto decisions

Mode: auto
1. <what was decided> — RULE: <the rule>
2. <what was decided> — FACT: <path>:<line> "<quoted text>"
3. <what was decided> — DEBATED: <option> (Advocate 1: <its proposal>; Advocate 2: <its proposal>) ⚠ decided for you — please review
4. <what was decided> — SAFER OPTION: <why> ⚠ decided for you — please review
Paused: <only when a stop that stays paused the task: which one, and why>
Checks: tests `<command>` — <result>; reviews <skill — result>; real run `<command>` — printed `<what it printed>` (auto-checked, not /verify)
Memory: <each entry the memory pass wrote, as `file — entry` | nothing new>
Not done: merge (yours); <auto verify: running (T182) | auto verify: <result> | /verify (yours), with [admin] only after the one retry also ended blocked>

-->

## Auto decisions

Mode: auto
1. AC6 vs AC8: the approval file is protected inside the hook, not by a pattern-list line — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes)
2. Stage 4 code-review fixes F1–F6 (record only what Pre asked, by `tool_use_id`; record only in `default`/`auto` permission mode; canonical keys; `.claude/state/**` protected; file keys only) — RULE: skills/code-review/SKILL.md § Finding Classification ("| **P1** | Logic error, broken contract, test gap for critical path | Yes |"; P2 "Recommended"): each fix closes a confirmed finding, applied as the review directs
3. Approvals are recorded and honoured for Edit and Write only; every Bash call that touches a sensitive path asks, as on `main`; S1's directory-change list and S3 are dropped; S2's basename guard and S4 stay — DEBATED: Edit/Write only (Advocate 1: Edit/Write only, still record Bash yes; Advocate 2: Edit/Write only, still record Bash yes; Advocate 3: Edit/Write only, record from Edit/Write only, because a Bash yes can store the wrong key after `cd`). All three agree on honouring; recording from Edit/Write only is the SAFER OPTION from Advocate 3's evidence ⚠ decided for you — please review
4. Residuals kept out of this task (a programmatic permission host answering the ask; task switching via the active-task state file; interpreter strings) — RULE: AGENTS.md § Karpathy Engineering Principles (Surgical Changes: "Touch only code required by the task"); each exists on `main` or outside the kit and is recorded in the guide, decision 3
Checks: tests pending (security-round fix in progress); reviews code-review — P0 0 / P1 1 / P2 4 / P3 2, fixed in d778e406; security-review — P1 2 / P3 2, fix in progress
Memory: nothing new yet (pass runs at merge)
Not done: security-review re-check (Skill `security-review`, after the decision-4 fix); auto verify: not started; merge (admin: after the auto verify pass)
Paused: auto-mode check failed — Risk High, but the trace has no `security-review` Skill call [report daed3491afef]

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t314_online_approval.py`, `test_t314_fix_round.py`, `test_t314_security_round.py`, `test_t314_backslash_key.py` (locked oracles by qa-expert: 16fea0bb, 524efaa5, 8fb26c53, 61151dfe); run at e5ad4a5c: `110 passed, 87 subtests passed in 14.32s` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/test_t314_backslash_key.py .claude/hooks/tests/test_t314_online_approval.py .claude/hooks/tests/test_t314_fix_round.py .claude/hooks/tests/test_t314_security_round.py .claude/hooks/tests/test_pre_tool_sensitive_path.py -q -p no:cacheprovider` → `110 passed, 87 subtests passed in 14.32s`; `python3 -m pytest .claude/hooks/tests/ -q` → `5031 passed, 5 skipped, 87 subtests passed in 195.73s` |
| Negative cases hold | ☑ pass | Red runs before each fix: oracle 1 `41 failed, 9 passed` (at 92daec34); fix round `27 failed, 5 passed` (7e5a6824); decision-4 re-lock `27 failed, 53 passed` (58d4c46c); backslash `10 failed, 7 passed` (cf180bc4). Each red set went green only after its fix commit (541c456b, d778e406, cf180bc4, e5ad4a5c) |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | `git diff main...HEAD`: the two sensitive-path hooks, their wiring (`.claude/settings.json`, `hooks/hooks.json`, `plugin/hooks/hooks.json`), `.gitignore`, the tracks.md paragraph, site hook row and count pins. code-review (P0 0 / P1 1 / P2 4 / P3 2, fixed d778e406); security-review agent (P1 2 / P3 2, fixed per decision 4 in cf180bc4); Skill `security-review` re-check (1 Medium, confirmed 8/10, fixed e5ad4a5c). Local-mode backslash gap out of scope → T319 |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **Companion score (easy-verifier)** | ☑ N/A | easy-verifier MCP server failed to connect this session (ECONNREFUSED); not run |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | hook-only change, no UI (guide: UI section not applicable) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | hook-only change, no UI (guide: UI section not applicable) |
| **UI: Responsiveness at target viewports** | ☑ N/A | hook-only change, no UI (guide: UI section not applicable) |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured by qa-expert on the unchanged hook (worktree `wt-t314`, HEAD `1b477ba5c219eedb158f795c31d710ef56383960`, before any implementation commit). Temp project `$S` = `.claude/sensitive-paths.txt` (shipped copy) + `PROJECT_KANBAN.md` + an online `.claude/board.json` (`{"board": "fake", "fake_board": "board.json", "id_pattern": "ENG-\\d+"}`). The same event is fed twice:

```
$ EV='{"tool_name":"Bash","cwd":"'$S'","tool_input":{"command":"cat tests/fixtures/secrets/x.json"}}'
$ for i in 1 2; do echo "--- call $i $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "$EV" | CLAUDE_PROJECT_DIR=$S CLAUDE_ACTIVE_TASK=T314 python3 .claude/hooks/pre_tool_sensitive_path.py; echo "exit=$?"; done
--- call 1 2026-11-15T06:12:22Z
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Bash call touches a sensitive path: tests/fixtures/secrets/x.json (pattern `**/secrets/**`). Listed in .claude/sensitive-paths.txt and board mode is online, where guides come from the board and cannot pre-authorise a sensitive path."}}
exit=0
--- call 2 2026-11-15T06:12:22Z
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Bash call touches a sensitive path: tests/fixtures/secrets/x.json (pattern `**/secrets/**`). Listed in .claude/sensitive-paths.txt and board mode is online, where guides come from the board and cannot pre-authorise a sensitive path."}}
exit=0
```

Both calls print `ask`: in board mode `online` there is no way to approve the path once for T314.

**AFTER**: captured by common-infrastructure after the decision-4 round (worktree `wt-t314`, working tree on `92835beb` plus the decision-4 fix, before its commit). Same temp project `$S` (shipped `.claude/sensitive-paths.txt`, `PROJECT_KANBAN.md`, online `.claude/board.json` `{"board": "fake", "fake_board": "board.json", "id_pattern": "ENG-\\d+"}`). A Write of `tests/fixtures/secrets/x.json` asks. Then the PostToolUse recorder gets the same call with the same `tool_use_id` and `permission_mode` `default`, which stands in for "the user said yes and the call ran". Then the same Write is silent, and a Bash `cat` of the file still asks (approvals are Edit/Write only):

```
$ cat run3.sh
W1='{"tool_name":"Write","hook_event_name":"PreToolUse","tool_use_id":"toolu_demo1","permission_mode":"default","cwd":"'$S'","tool_input":{"file_path":"tests/fixtures/secrets/x.json","content":"{}"}}'
P1='{"tool_name":"Write","hook_event_name":"PostToolUse","tool_use_id":"toolu_demo1","permission_mode":"default","cwd":"'$S'","tool_input":{"file_path":"tests/fixtures/secrets/x.json","content":"{}"},"tool_response":{"success":true}}'
W2='{"tool_name":"Write","hook_event_name":"PreToolUse","tool_use_id":"toolu_demo2","permission_mode":"default","cwd":"'$S'","tool_input":{"file_path":"tests/fixtures/secrets/x.json","content":"{}"}}'
B3='{"tool_name":"Bash","hook_event_name":"PreToolUse","tool_use_id":"toolu_demo3","permission_mode":"default","cwd":"'$S'","tool_input":{"command":"cat tests/fixtures/secrets/x.json"}}'
run() { echo "$2" | CLAUDE_PROJECT_DIR=$S CLAUDE_ACTIVE_TASK=T314 python3 .claude/hooks/$1; echo "exit=$?"; }
echo "--- Write, call 1 $(date -u +%Y-%m-%dT%H:%M:%SZ)"; run pre_tool_sensitive_path.py "$W1"
echo "--- recorder (PostToolUse, same tool_use_id, permission_mode default: the user said yes)"; run post_tool_sensitive_approval.py "$P1"; cat $S/.claude/state/sensitive-approvals.json
echo "--- Write, call 2 $(date -u +%Y-%m-%dT%H:%M:%SZ)"; run pre_tool_sensitive_path.py "$W2"
echo "--- Bash cat of the same file $(date -u +%Y-%m-%dT%H:%M:%SZ)"; run pre_tool_sensitive_path.py "$B3"
$ bash run3.sh
--- Write, call 1 2026-11-15T10:20:29Z
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Write call touches a sensitive path: tests/fixtures/secrets/x.json (pattern `**/secrets/**`). Listed in .claude/sensitive-paths.txt and board mode is online, where guides come from the board and cannot pre-authorise a sensitive path. After you approve, a later Edit or Write of these files in T314 will not ask again."}}
exit=0
--- recorder (PostToolUse, same tool_use_id, permission_mode default: the user said yes)
exit=0
{
  "T314": [
    "tests/fixtures/secrets/x.json"
  ]
}
--- Write, call 2 2026-11-15T10:20:30Z
exit=0
--- Bash cat of the same file 2026-11-15T10:20:30Z
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[hook:sensitive-path] This Bash call touches a sensitive path: tests/fixtures/secrets/x.json (pattern `**/secrets/**`). Listed in .claude/sensitive-paths.txt and board mode is online, where guides come from the board and cannot pre-authorise a sensitive path. A Bash call always asks; after you approve an Edit or Write of these files in T314, a later Edit or Write of them will not ask again."}}
exit=0
```

The first Write asks, with the Edit-or-Write sentence. The recorder records the file under T314. The second Write prints nothing (no decision, not `allow`). The Bash `cat` of the approved file still asks.

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T314.jsonl`, never the
implementing agent alone]
