# TASK_GUIDE — T375: The sensitive-path hook dequotes a word before it matches a sensitive path
**Date**: 2026-11-25
**Complexity Level**: C1
**Risk Level**: High
**Priority**: P2
**Assigned agent**: common-infrastructure (the Supervisor writes the code, DDR-0011)
**Agent guide**: `agents/common-infrastructure.md`

> Read relevant files from `docs/legacy/` before making any code changes. (This repo has no `docs/legacy/`: `PROJECT_SPEC.md` and `docs/claude-md/` are the source of truth.)

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide

---

## Requirement (Pillar 1 — Adapt the requirement)

**User request (verbatim, 2026-11-25)**: "continue your work by picking tasks [admin]". The Supervisor picked T375 from the board. Its row comes from the T371 round-2 review (F8, P3) and the T371 decision 8.

**Restated intent**:
1. The shell drops quotes and backslashes inside a word. `cat .claude/sens''itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt` and `find config -d$'elete'` name a sensitive path or a destructive flag that the shell sees and the hook does not. They pass outside `[admin]` too. The hook must read the word as the shell does.
2. A word the shell still builds (`${x}`, `$x`) next to literal text is read with the built part as a glob `*`. `cat .claude/sens${x}itive-paths.txt` then asks when a sensitive file matches. A word that is only a variable (`"$F"`) stays a recorded limit.
3. The T371 round-3 pins (decision 8) go in: `find config/.env -exec rm x ;` and `-ok rm x ;` with no `{}` are writes under `[admin]`; an empty Bash command is not a read; the `[admin]` note asks for a line in the "final report"; the header of `.claude/sensitive-paths.txt` (line 2) names the `[admin]` exception.

**Out of scope**: `eval`, `python -c`, and any word built from a variable alone (they stay recorded limits); ANSI-C escapes inside `$'…'` (`$'\x65'`).

**Requirement Refs**: `tasks/TASK_REVIEW_T371.md` (round 2 F8; decision 8); board row T375.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent matches the row — auto (Supervisor), `[admin]`, 2026-11-25
- [x] Domain terms align with the `PROJECT_SPEC.md` glossary (no new term)
- [x] Every Acceptance Criterion traces to a line of the Requirement

---

## Dependencies & Reachability

**Depends on**: T371 (merged)
**Entry point**: `.claude/hooks/pre_tool_sensitive_path.py` (PreToolUse hook on `Edit|Write|Bash`) — a Bash call.

---

## Acceptance Criteria

In a project whose `config/` holds `.env` and whose `.claude/` holds `sensitive-paths.txt`, outside `[admin]`:

1. These ask: `cat .claude/sens''itive-paths.txt`, `cat .claude/sens""itive-paths.txt`, `cat .claude/sensitive-pa\ths.txt`, `cat .claude/"sensitive-paths.txt"`, `cat conf''ig/.env`.
2. `find config -d$'elete'` and `find config -d$"elete"` ask (folder rule). `find config -name x` stays silent.
3. `cat .claude/sens${x}itive-paths.txt` and `cat .claude/sens$xitive-paths.txt` ask when the glob finds the file. A built part is also read as empty: `cat $E.env` and `cat config/${E}.env` ask. `cat "$F"`, `echo $HOME` and `ls $D/$E` stay silent, even when the project has a folder a `*` would match.
4. A word that mixes quotes with plain text is read behind `echo`, `printf`, `grep` and `rg` too: `echo x > .e"n"v` and `grep KEY .e''nv` ask. A brace next to a quote is expanded: `cat .claude/sens''{itive,x}-paths.txt` asks. Text in a quoted span with a space stays data, and so does a wholly quoted word behind a data command (`grep -n ".env" .gitignore`): `echo "see .env file"` and `echo 'a b .env c'` stay silent. (A `git commit -m` message is already scanned on `main`; unchanged.)
5. Under `[admin]`: `find config/.env -exec rm x ;` and `find config/.env -ok rm x ;` (no `{}`) are writes (logged, not read-only). An empty Bash command is not a read. The note holds the words "final report".
6. Line 2 of `.claude/sensitive-paths.txt` names the `[admin]` exception ("or the session tag `[admin]` holds (T371)").
7. Every other sensitive-path test passes unchanged.

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1-5 | each AC command | ask / silent / logged | automated (`.claude/hooks/tests/test_t375_dequote_tokens.py`) |
| 6 | the list header | names `[admin]` | automated (same file) |
| 7 | the sensitive-path suites | pass | automated |

### Verification Command (exact, runnable)

```bash
python3 -m pytest -q -p no:cacheprovider .claude/hooks/tests/test_t375_dequote_tokens.py .claude/hooks/tests/test_t371_admin_approval.py .claude/hooks/tests/test_t374_folder_rule_followups.py .claude/hooks/tests/test_t363_folder_level.py .claude/hooks/tests/test_pre_tool_sensitive_path.py .claude/hooks/tests/test_t316_list_self_protect.py
```

**Real-run scope (the first auto verify stopped here).** Run AC 1, 2 (the path-form cases), 3 and 4 against the hook, on `main` and on the branch. The folder-rule cases (`find config -d$'elete'`, `find config -d$"elete"`) need a sensitive folder inside the project, and a headless run cannot create one: the guard asks on the `.env` it would write, and a split name routes around the guard. The unit tests (`test_t375_dequote_tokens.py`, `test_t363_folder_level.py`) drive the real hook as a subprocess in a temp project that holds `config/.env`; they are the evidence for those cases. Do not stop for a fixture.

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled in `tasks/TASK_REVIEW_T375.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T375.md`.

---

## UI / Design Acceptance Criteria

No UI. ☐ N/A: a PreToolUse hook.

---

## Approach

**Pattern reference**: the dequote in `folder_hits` and `only_reads` (T363, T371): `re.sub(r"[\"'\\()]", "", word)`.

**Vital slice**:
- `dequoted_tokens(command, cwd)`, called from `command_tokens`: scan the heredoc-stripped text for words made of plain characters, `\x` pairs, `$'…'`, `$"…"` and quoted spans with no space. A word with a quote, a backslash or a `$` is dequoted (drop `$` before a quote, then quotes and backslashes). A built part (`${…}`, `$name`) becomes `*` when the word keeps literal text; a word with a glob character is expanded like any other token (same cap).
- `$` before a quote is dropped in the dequote of `folder_hits` and `only_reads`.
- Tests, plus one header edit in `.claude/sensitive-paths.txt`.

**Cut list**: no ANSI-C escape decoding; no `eval`; no variable-only words.

---

## Edge Case Checklist

- [ ] A quoted span with a space is data (AC 4), not a token source
- [ ] A word that is only a variable never becomes `*`
- [ ] Glob expansion shares `MAX_GLOB_MATCHES`
- [ ] Pin-test pre-flight: `test_pre_tool_sensitive_path.py` and `test_t342*` (quoted globs) — unchanged, must pass
- [ ] Stale references: the hook header ("words dequoted", the limits list); the `sensitive-paths.txt` header; any test that pins that header's text

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_tool_sensitive_path.py` | `dequoted_tokens`, `command_tokens`, the `$'` dequote in two places, header lines |
| `.claude/sensitive-paths.txt` | line 2 names `[admin]` |
| `.claude/hooks/tests/test_t375_dequote_tokens.py` (new) | AC 1–6 |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/lib/shell_data.py` | shared by the merge gate |
| `.claude/settings.json` | no hook wiring changes |

---

## Test Plan

Test first: the new file fails on `main` for AC 1–3 and 6 (AC 4, 5 pin behaviour that already holds). Then the change, the Verification Command, and the full suite compared with the `main` baseline.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `code-review` run; `security-review` run
- [ ] Tests written AND pass — output in `tasks/TASK_REVIEW_T375.md` Evidence
- [ ] Auto verify pass
- [ ] `memory/` updated (if new patterns)
- [ ] Board current

---

## Questions Log

- Row clause "ask on a word the shell still builds when it is next to a sensitive name": read as a glob on the built part (Restated intent 2), so only a real sensitive file asks. Decided by the Supervisor, `[admin]`, 2026-11-25.
