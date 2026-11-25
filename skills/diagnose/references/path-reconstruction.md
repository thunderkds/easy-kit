# diagnose — Stuck-Loop Checkpoint — path reconstruction

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

**Path reconstruction — before assigning any verdict.** Group Phase 4's probes by trace-id, order
each group by timestamp, and walk it comparing the observed value at each boundary against the value
Phase 3 predicted. Report the **first boundary at which the observed value diverged from the
predicted value** — that boundary, not the end-of-path symptom, is where diagnosis continues. Group
by trace-id; never merge two trace-ids into one path. Two spans at the same location within one
trace (a retry or a redirect) are distinct spans, not a contradiction. If a trace-id has probes on
only one side of a boundary, report `path incomplete` for that boundary and name the missing side —
never infer what the missing side saw. `path incomplete` is a finding about the instrumentation,
exactly as INCONCLUSIVE is below; it is not licence to conclude.
