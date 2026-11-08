# TASK_REVIEW — T292: One `parse_ts` for the hooks

> Sibling of `tasks/TASK_GUIDE_T292.md`. Everything here is **filled by the reviewer at Stage
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

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | pass | `.claude/hooks/tests/test_parse_ts_single.py` (43 tests, 23 red on the old code, green after) |
| Verification command run | pass | `python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider` -> `4205 passed, 25 subtests passed` (see Demonstration AFTER) |
| Negative cases hold | pass | M1 `lib/auto_mode.py` +2 lines -> `4 failed, 39 passed`; M2 `lib/session_work.py` +9/-1 lines -> `2 failed, 41 passed`; independent reviewer ran 5 more mutations, each red (4, 8, 10, 2, 1 failed) |
| verify | ☑ pass | auto-run by hook, session 1b260f90-5dfc-4408-8d11-2547c8125473, commit 417b92bf17837853542e94b2ffcfa05e829d3fc7, log .claude/verify-runs/T292-417b92bf1783.log — pass |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | pass | Independent Stage 4 code-review (read-only): 36 inputs through old copies (`git show main:`) and new `parse_ts`, identical; fail-closed import paths tested; no P0, P1 or P2; two P3 notes, no change needed. Reviewed: the 3 changed hook files, the 2 callers, `pre_bash_block_unsafe_merge.py` import guard. Skipped: unrelated hooks |
| Full smoke suite still green (no regression) | pass | `4205 passed, 25 subtests passed in 256.11s` |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: Low-risk refactor of one helper; the independent code-review and the 36-input comparison cover it |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**:

```
# captured 2026-11-08T08:46:47Z in wt-t292 at eb85573c, before any implementation commit
$ grep -rn "def parse_ts" .claude/hooks
.claude/hooks/stop_auto_mode_check.py:150:def parse_ts(value):
.claude/hooks/lib/session_work.py:33:def parse_ts(value):
$ python3 -B char.py   (stop copy loaded with ast, session_work imported; 20 inputs)
'2026-11-04T06:05:12+00:00'                stop=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)
'2026-11-04T06:05:12+07:00'                stop=datetime(2026, 11, 4, 6, 5, 12, tzinfo=timezone(timedelta(seconds=25200)))  session_work=datetime(2026, 11, 4, 6, 5, 12, tzinfo=timezone(timedelta(seconds=25200)))
'2026-11-04T06:05:12'                      stop=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)
'2026-11-04T06:05:12Z'                     stop=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)
'2026-11-04T06:05:12.123456Z'              stop=datetime(2026, 11, 4, 6, 5, 12, 123456, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, 123456, tzinfo=utc)
'2026-11-04T06:05:12.5'                    stop=datetime(2026, 11, 4, 6, 5, 12, 500000, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, 500000, tzinfo=utc)
'2026-11-04'                               stop=datetime(2026, 11, 4, 0, 0, tzinfo=utc)  session_work=datetime(2026, 11, 4, 0, 0, tzinfo=utc)
'2026-11-04T06:05:12z'                     stop=None  session_work=None
' 2026-11-04T06:05:12Z'                    stop=None  session_work=None
''                                         stop=None  session_work=None
None                                       stop=None  session_work=None
0                                          stop=None  session_work=None
1.5                                        stop=None  session_work=None
[]                                         stop=None  session_work=None
{}                                         stop=None  session_work=None
b'2026-11-04T06:05:12Z'                    stop=None  session_work=None
'not a time'                               stop=None  session_work=None
'2026-13-45T00:00:00Z'                     stop=None  session_work=None
datetime(2026, 11, 4, 6, 5, 12)   stop=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)  session_work=datetime(2026, 11, 4, 6, 5, 12, tzinfo=utc)
datetime(2026, 11, 4, 0, 0, tzinfo=utc) stop=datetime(2026, 11, 4, 0, 0, tzinfo=utc)  session_work=datetime(2026, 11, 4, 0, 0, tzinfo=utc)
AGREE
```

**AFTER**: captured 2026-11-08 in wt-t292 after the implementation commit.

```
$ grep -rn "def parse_ts" .claude/hooks
.claude/hooks/lib/auto_mode.py:67:def parse_ts(value):
$ python3 -m pytest .claude/hooks/tests/test_parse_ts_single.py -q -p no:cacheprovider
43 passed in 0.05s
$ python3 -m pytest .claude/hooks/tests -q -k "parse_ts or session_work or stop_auto" -p no:cacheprovider
132 passed, 2113 deselected in 10.64s
$ python3 -m pytest .claude/hooks/tests tests -q -p no:cacheprovider
4205 passed, 25 subtests passed in 256.11s (0:04:16)
```

**DELTA**: A fix to the timestamp parser now lands in every hook at once, because `stop_auto_mode_check.py` and `lib/session_work.py` bind the one `parse_ts` in `lib/auto_mode.py`.

**WITNESS**: `memory/event-trace/T292.jsonl` holds the implementer's 30 Bash calls and the Stage 4 reviewer's hand-back (2026-11-08T10:04Z). The full suite ran in `wt-t292`: `4205 passed`. The hook-written verify row follows from the auto verify run.

---

## Stage 4 self-review (implementer, T292)

**Characterization (AC 1)**: the two old copies agreed on all 20 inputs of the table (aware `+00:00` and `+07:00`, naive, `Z`, lowercase `z`, fractional seconds, date only, leading space, empty, `None`, `0`, `1.5`, `[]`, `{}`, bytes, garbage, month 13, naive and aware `datetime` objects). No difference to list. The stop copy kept the aware-or-UTC step inside its `try`, the session_work copy outside it; that step cannot raise, so the outputs are the same. Naive input: both read it as UTC, so no "stricter" pick was needed.

**Where the copy lives**: `.claude/hooks/lib/auto_mode.py`. Both callers already import it inside their fail-closed `try` (`stop_auto_mode_check.py` via `import auto_mode as am`, `session_work.py` via `import auto_mode`, `pre_bash_block_unsafe_merge.py` imports both). So there is no new import, no new failure mode, no cycle, no MANIFEST change (`.claude/hooks` is copied whole) and no change to the tests that copy lib files into temporary projects (AC 3). The existing broken-import tests (`tests/test_hooks_from_plugin.py` `test_d4_*`) passed in the full run.

**Changes**: `lib/auto_mode.py` (+`parse_ts`), `lib/session_work.py` (`parse_ts = auto_mode.parse_ts`; unused `from datetime import datetime, timezone` removed), `stop_auto_mode_check.py` (`parse_ts = am.parse_ts`; its `datetime`, `timedelta`, `timezone` import is still used elsewhere), new `.claude/hooks/tests/test_parse_ts_single.py` (43 tests).

**Red first**: the single-copy tests failed on the old code: `23 failed, 20 passed` (20 table cases through `auto_mode.parse_ts`, plus the three structure tests; the 20 session_work table cases passed because that copy already existed). Green after the change: `43 passed`.

**Mutation controls (bytes changed, `-B`)**:
- M1 `git diff --stat`: `.claude/hooks/lib/auto_mode.py | 2 ++`. The shared copy returns None when the input holds ".". Result: `4 failed, 39 passed` (fractional-second cases, through `auto_mode.parse_ts` and through `session_work.parse_ts`). Restored with `git checkout`; green `43 passed`.
- M2 `git diff --stat`: `.claude/hooks/lib/session_work.py | 10 +++++++++-`. session_work gets its own `parse_ts` back. Result: `2 failed, 41 passed` (`test_ac2_session_work_uses_the_one_copy_not_its_own`, `test_ac2_ac4_exactly_one_parse_ts_def_under_the_hooks`). Restored; green.

**Pin-test pre-flight (LR-0004)**: `grep -rn parse_ts` over `.claude/hooks/tests` and `tests` found one user, `test_t250_session_ownership.py:109` (`sw.parse_ts`), which still works because `session_work` keeps the name. No dedup, vital-slice, site or memory-budget test reads the changed text. Full suite `4205 passed, 25 subtests passed`.

**Stale text (LR-0005)**: `grep -rn parse_ts` outside tests: only `tasks/` files (the guide's evidence lines `stop_auto_mode_check.py:150` and `session_work.py:33` describe the state before the task; the T250 and T284 reviews name the duplicate as a follow-up). No doc, site or map line states the old location. Nothing to fix.

**Cut list (not done, out of scope)**: `lib/auto_mode.py` has a third inline copy of the same parse (`datetime.fromisoformat(str(entry.get("timestamp")).replace("Z", "+00:00"))` in the `[admin]` latest-request reader, about line 170) that could call `parse_ts`; `stop_auto_mode_check.py` line ~265 `_session_files` mirrors `session_work._session_files` by comment ("keep in step with"). Both left alone per "Touching other duplicated helpers".

**Open risks**: none known. P3 only: the fully-qualified name `session_work.parse_ts` is now an alias, so `inspect.getsource` on it points at `auto_mode.py`.
