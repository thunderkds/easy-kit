# TASK_GUIDE — T315: a setup choice makes the sensitive-path hook warn instead of ask
**Date**: 2026-11-15
**Complexity Level**: C2
**Risk Level**: High
**Priority**: P1
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read the memory slice in your spawn prompt (`<!-- memory-slice -->`). Read `memory/MEMORY.md` in full only if your work reaches a file, hook, skill or decision the slice does not cover
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. **C2/C3 or multi-file tasks only**: read `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

User, 2026-11-15, after the sensitive-path hook asked in an `[admin]` run: "the hook come from the setup time, so the admin tag seem like does not like the bypass, right? we should add admin tag in the initial time, or provide any options to remove the hooks following the tag or any idea about that". The Supervisor recommended: keep every hook; do not let a message tag switch a hook off; offer an explicit, visible setup choice that makes the sensitive-path hook warn and log instead of ask. User: "yes, start and continue".

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> At setup, `settings-setup` can offer one opt-in profile for a solo developer who trusts their agents. With it, `pre_tool_sensitive_path.py` does not stop a call that touches a sensitive path: it lets the normal permission flow run, shows a one-line warning naming the path, and logs it. The default stays `ask`. No message tag (`[admin]`, `[auto]`) changes the mode. The merge gate, git guardrails and every other hook are untouched.

**Design decisions (Supervisor, logged here):**
1. The mode is the env var `EASY_KIT_SENSITIVE_PATH_MODE` in `.claude/settings.json` `"env"` (a supported settings key; the hook process inherits it). Values: `ask` (default) and `warn`. Any other value, or unset → `ask` (fail toward the human).
2. `warn` output: no `permissionDecision` (never `allow`), exit 0, a `systemMessage` / additional-context line `[hook:sensitive-path] warn mode: <tool> touches <path> (pattern <pat>)`, and one trace line, so the user sees it and the audit trail keeps it.
3. The T314 approval file stays protected in both modes: a call touching `.claude/state/sensitive-approvals.json` always asks. The pattern-list file `.claude/sensitive-paths.txt` and a hook-import or parse failure also always ask (they are the hook's own integrity, not user data).
4. A new profile, not a change to `solo-engineer`: id `solo-trusted`, label `Solo, trusted agents`. It holds the `solo-engineer` values plus `env.EASY_KIT_SENSITIVE_PATH_MODE = "warn"`. `settings-setup` keeps its rules: it shows the dry run, writes only after the user says yes, and in `[auto]`/`[admin]` writes nothing.

**Out of scope** (what this task explicitly does NOT do):
- Any tag-aware hook; any change to the merge gate, `git-guardrails`, step limit, locked-oracle or auto-verify hooks.
- Removing or disabling any hook.
- Changing the default (`ask`) or any existing profile's values.
- The approve-once logic (T314).

**Depends on**: T314 — the same hook file and the approval file. Start T315 from `main` after T314 merges.

**Requirement Refs**: None — kit maintenance; source is the request above.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (by Supervisor; user: "yes, start and continue" on 2026-11-15)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] All Requirement Refs exist in `PRD.md` (none)

---

## Dependencies & Reachability

**Depends on**: T314 — `.claude/hooks/post_tool_sensitive_approval.py` and `.claude/state/sensitive-approvals.json` exist on `main`

**Entry point**: `EASY_KIT_SENSITIVE_PATH_MODE` read by `.claude/hooks/pre_tool_sensitive_path.py`; profile `solo-trusted` in `skills/settings-setup/profiles.json`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | Mode unset, `ask`, empty, `WARN`, `off`, or any other value → every existing sensitive-path test result is unchanged (asks) | default stays ask |
| 2 | Mode `warn`, call touches sensitive `.env` → no `permissionDecision` in the output, exit 0, a visible warning line naming the path and pattern, and one trace record | warn and log |
| 3 | Mode `warn`, call touches the approval file or `.claude/sensitive-paths.txt` → asks | integrity stays |
| 4 | Mode `warn`, malformed stdin / unreadable pattern list / import failure → asks, as today | fail toward the human |
| 5 | No tag changes the mode: a transcript whose latest request holds `[admin]` or `[auto]` gives the same output as one without, in both modes | no tag bypass |
| 6 | `profiles.json` has profile `solo-trusted` (label `Solo, trusted agents`, a `for` line that says protected files are warned, not asked); its values are the `solo-engineer` values plus `env.EASY_KIT_SENSITIVE_PATH_MODE: "warn"`; `apply_profile.py solo-trusted --dry-run` shows that env line; existing profiles unchanged | setup choice |
| 7 | `skills/settings-setup/SKILL.md` lists the new profile and says, in one line, what it weakens and how to undo it (delete the env line); the hook docstring and the doc that states the sensitive-path rule say the same | the user knows |

---

## UI / Design Acceptance Criteria

Not applicable — no UI. All three UI Evidence rows are ☐ N/A: hook and skill-data change.

---

## Evaluation & Acceptance (How we know the agent worked correctly)

**Locked oracle**: written first by `qa-expert` in `.claude/hooks/tests/test_t315_warn_mode.py` (and, for AC 6, a test beside the existing settings-setup tests). The implementer may not edit it.

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | each non-`warn` mode value, `.env` Write | `ask` (AC 1) | automated test (subprocess, env set) |
| 2 | `warn`, `.env` Write / Edit / Bash | exit 0, no decision, warning line, trace record (AC 2) | automated test |
| 3 | `warn`, approval file / pattern list | `ask` (AC 3) | automated test |
| 4 | `warn`, bad stdin / unreadable list / no `lib/` | `ask` (AC 4) | automated test |
| 5 | `[admin]` and `[auto]` transcripts, both modes | outputs equal to the no-tag runs (AC 5) | automated test |
| 6 | `apply_profile.py solo-trusted --dry-run` on a temp project | shows the env line; other profiles' dry runs unchanged (AC 6) | automated test |
| 7 | full suites | no regression | `python3 -m pytest .claude/hooks/tests/ tests/ -q` |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/test_t315_warn_mode.py .claude/hooks/tests/test_pre_tool_sensitive_path.py -q -p no:cacheprovider
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T315.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T315.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/pre_tool_sensitive_path.py` `ask()` for the output shape; `skills/settings-setup/profiles.json` and `scripts/apply_profile.py` for how a profile adds an `env` key (add-only). Residual (accepted, recorded): an agent that edits `.claude/settings.json` could add the env line; it takes effect only in a new session, and the warning line names every warned path.
**Vital slice**: the mode read, the warn output, the integrity exceptions, the profile and its one-line doc.
**Cut list**: per-pattern modes; a `deny` mode; a slash command to flip the mode; tag-aware behaviour.

## Files to Change (Predicted)

- `.claude/hooks/pre_tool_sensitive_path.py`
- `.claude/hooks/tests/test_t315_warn_mode.py` (new, qa-expert, locked)
- `skills/settings-setup/profiles.json`
- `skills/settings-setup/SKILL.md`
- `tests/` settings-setup profile test (new or extended, qa-expert)
- the doc that states the sensitive-path rule
