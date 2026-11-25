# TASK_REVIEW — T371: Under `[admin]` the sensitive-path hook approves and logs instead of asking

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_t371_admin_approval.py` (11 tests, 23 subtests) |
| Verification command run | ☑ pass | 181 passed, 152 subtests passed in 22.23s (the guide's Verification Command, run in the worktree at 3b41a1d1) |
| Negative cases hold | ☑ pass (with gaps) | Mutations on a scratch copy (no repo edit): 18 of 25 turn a test red; survivors: drop `[stop]` check (M3), `[ticket]` as admin (M4), no session-tag read (M23), `git push` in READ_ONLY_GIT (M20), dir/file mode (M21/M22), origin check in lib (M18, double-guarded). See Findings F1, F3. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [leave it: the auto verify hook writes this row, with its run record. If you ran /verify yourself, tick pass and make the whole Notes cell "/verify by the user, session <id>, commit <sha>" (the full 40-character commit). The merge gate counts no other row, even with the word "pass" in it] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Range fix/t374-folder-rule-followups...3b41a1d1: hook, test, tracks.md; read lib/auto_mode.py tag readers and the merge gate's reading (pre_bash_block_unsafe_merge.py:2754-2785). Skipped: unrelated hooks. |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | Not run: a full run is in progress in the worktree (per the Supervisor). |
| **Companion score (easy-verifier)** | ☑ N/A | Not run. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI. |


## Review findings (code-review, P0-P3, confidence >= 75)

Verdict: **FAIL** (one P1).

| # | Sev | Conf | Where | Finding | One-line fix |
|---|-----|------|-------|---------|--------------|
| F1 | P1 | 90 | `.claude/hooks/pre_tool_sensitive_path.py` `admin_in_force` (the fallback after `session_request`) | A stale `[admin]` holds after a resume. `session_request` returns None when the tag was typed before the resume mark (or the mark is unreadable: "trust no tag"), but the fallback `latest_request`/`admin_request` has no resume check, so the old request still counts. Probed with the real hook: a resume mark written after the tag, then a Write of `.env` -> `[admin] approved ... logged`; a mark holding `garbage` -> same. Every request that carries `[admin]` is already a session tag, so the fallback only ever adds the resume / unreadable-mark cases. | Drop the fallback: `s = auto_mode.session_request(t); return s is not None and s[0] == "admin"`; add a resume-mark test. |
| F2 | P2 | 85 | same file, `only_reads` | A call that runs code is read as a read (no log line): `GIT_EXTERNAL_DIFF=rm git diff --ext-diff config/.env` asks outside `[admin]` and passes silent under it; `git diff/log --ext-diff|--textconv` and `rg --pre CMD` likewise. `_segment_command` skips `VAR=` prefixes, so the verb is `git`. | In `only_reads`: a segment whose first word is `VAR=...` is a write; add `--ext-diff`, `--textconv`, `--pre`, `--pre-glob` to the write flags. |
| F3 | P2 | 80 | `test_t371_admin_approval.py` | Gaps (mutations that stay green): `[ticket]` as admin (M4), `[stop]` in the same request as `[admin]` (M3), the tag held over a later plain request (M23), `git push` counted as a read (M20), resume (F1), folder/file modes (M21/M22). | Add one test each (the `[ticket]`, `[stop]` + `[admin]` in one request, resume mark, `git push config/.env`, mode 0700/0600). |
| F4 | P3 | 78 | `log_admin_approval` | `os.makedirs(mode=0o700)` sets the leaf only and leaves an existing folder as is; `O_NOFOLLOW` covers the final component only, so a symlinked slug folder is followed. Agents are denied writes there only by string rules in `.claude/settings.json:162-163` (`Bash(*harness-anchors*)`), which a glob or a variable evades; the log is append-only by convention, not tamper-evident. | `os.lstat` the folder (owner = us, mode & 0o077 == 0, not a symlink) before the open; say in tracks.md that the log is advisory. |
| F5 | P3 | 75 | hook / tracks.md | "No decision" keeps the normal permission flow, so the user may still be prompted or deny; the log line says "approved" and is written before that. | Word it "not asked by the hook" or log the PostToolUse result. |

Checked and held (no finding): the hook never emits `allow` (grep: only comments; M16 turns a test red); no change outside `[admin]` (the new branch sits behind `admin_in_force`; the earlier suites pass); a tag in a tool result, a sub-agent (sidechain) prompt, a code span or a `>` quoted line asks (probed: code span, quoted line, `[ticket]`, `[auto]` after `[admin]`, `[stop]`); a write to `PROTECTED_PATTERNS` asks (M11 red, 4 tests); log failure asks (M15 red); log lines cannot be forged by a command: `json.dumps` escapes newlines, target is cut at 2000; `cat "$(rm -rf config)"`, backtick and `$()` forms, `;`, `&&`, `||`, newline, `&`, subshell and heredoc forms are all logged, not read.

## Test-by-test: the change that turns it red (scratch copy, real hook as a subprocess)

| Test | Turns red when |
|------|----------------|
| OutsideAdmin.test_ac1 | `admin_in_force` returns True (M1) |
| OutsideAdmin.test_ac6_a_later_stop | M1 (not the removal of the `[stop]` check: M3 stays green, F3) |
| UnderAdmin.test_ac2_a_write_passes_and_is_logged | `admin_in_force` False (M2); no log write (M12); `allow` emitted (M16); note without the log path (M17); `session` field dropped (M19); only_reads true for Edit/Write (M10) |
| UnderAdmin.test_ac2_destructive_bash | M2, M5 (only_reads always True), M12, M14 (O_TRUNC) |
| UnderAdmin.test_ac3_a_read_passes_with_no_log | `only_reads` always False (M6); the read check removed (M24); a read of a protected file asks (M25) |
| UnderAdmin.test_ac3_a_read_with_a_write_in_it | redirect/tee check dropped (M7); find flags (M8); `git --output` (M9); M5; M2; M12 |
| UnderAdmin.test_ac4_guards_own_files | PROTECTED check removed (M11, 4 failed) |
| UnderAdmin.test_ac5_a_log_that_cannot_be_written | log error swallowed (M15) |
| UnderAdmin.test_ac5_a_symlinked_log | `O_NOFOLLOW` dropped (M13); M15; M2; M12; M16 |
| UnderAdmin.test_ac7_the_log_only_grows | `O_APPEND` -> `O_TRUNC` (M14); M2; M5; M12; M16 |
| AdminInAToolResult.test_ac6_an_untyped_tag | M1 (the lib origin check alone, M18, stays green: `latest_request` also requires "human") |

Commands: `python3 -I /tmp/claude-1000/.../scratchpad/mut.py` (mutations), `probe.py`, `probe2.py`, `probe3.py` (read classes, resume, tags); all on scratch copies.

---

## Demonstration

Not filled by the reviewer.
