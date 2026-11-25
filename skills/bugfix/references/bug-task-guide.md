# bugfix — Step 3 reference

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

## Step 3 — the bug task-guide skeleton

```
## Bug Fix Task Guide — T[NNN]

### Mental Model (confirmed by user)
- Observed: <what is happening>
- Expected: <what should happen — testable definition>
- Likely divergence point: <area identified in Step 2c>
- Recent context: <relevant git changes or decisions found in Step 2a>

### Intake
- Trigger: <exact steps / inputs>
- Severity: <P0 / P1 / P2>
- Affected area: <files / endpoints / feature — from Step 2 investigation>

### Complexity & Risk
- Complexity: <C0–C3> (floor C1 for any bug touching >1 file)
- Risk: <Low / Medium / High> (P0 floors at Medium)

### Diagnosis Gates (Pillar 1 — must pass before any fix)
- [ ] Phase 1 feedback loop built and running
- [ ] Bug reproduces deterministically on the loop
- [ ] 3–5 ranked falsifiable hypotheses listed (consistent with confirmed mental model)
- [ ] Correct hypothesis identified via Phase 4 instrumentation

### Attempts Log (filled live during diagnosis — required if >1 hypothesis tested)
| # | Hypothesis | Predicted signal | Actual result | Verdict |
|---|---|---|---|---|

**Stuck checkpoint** (if 2 consecutive hypotheses disproven):
- [ ] 3 options presented (next hypothesis / widen scope / abandon+escalate)
- [ ] Chosen option: ___
- [ ] User's explicit go-ahead: ___

### Fix Gates (Pillar 2)
- [ ] Regression test written before the fix (or no-seam documented)
- [ ] Fix applied; regression test passes
- [ ] Phase 1 loop no longer reproduces the bug
- [ ] Fix matches the "correct behaviour" definition from the mental model

### Cleanup Checklist (Pillar 3)
- [ ] All [DEBUG-...] instrumentation removed (grep verified)
- [ ] Throwaway prototypes deleted
- [ ] Correct hypothesis stated in commit message
- [ ] Post-mortem: what would have prevented this?

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_Txxx.md`.

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_Txxx.md`.
```

## Step 3 — the review file's bugfix rows and Demonstration fill

```markdown
| Repro loop | ☐ pass / ☐ fail | [command/observation that reproduced the bug before the fix] |
| Regression test | ☐ pass / ☐ fail | [test file path(s) added to lock the fix in] |
| Smoke suite | ☐ pass / ☐ fail | [bug-specific smoke check beyond the full suite row above] |
```

Fill the review file's Demonstration block this way for a bugfix:

```markdown
**BEFORE**: same command as the Phase 1 repro loop above, captured before any fix commit exists —
do not restate it here as a second copy; point at it by name (e.g. "see Phase 1 repro loop") so
the two cannot drift out of sync.

**AFTER**: the same Phase 1 repro loop, re-run post-fix, showing the bug no longer reproduces.

**DELTA**: <one sentence — what now behaves correctly that did not before>

**WITNESS**: <who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone>
```

Both flavors split the same two sections into the same sibling file, keeping their field names and
ordering identical — that is the property `delivery-report` depends on to need no flavor branch
(T053, preserved by T064). The three UI rows default to `☐ N/A` for a pure-backend bugfix — but a
bugfix that touches a UI component must fill them with real evidence before Hard-Stop Gate 6 is
satisfied; defaulting to N/A on a UI-affecting bugfix is not a valid shortcut.
