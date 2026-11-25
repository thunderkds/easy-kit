# diagnose — Phase 4 — Instrument: the nine steps, backward tracing, the no-seam fallback, red flags

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here. *The Checkpoint below* and *the Stuck-Loop Checkpoint below* name the `### Stuck-Loop Checkpoint` section of `SKILL.md`.

1. **Sink** — write to one local NDJSON log file (e.g. under the system temp dir), one per diagnosis
   session. Never *write* debug output to `memory/event-trace/` — that channel records tool calls,
   not program values. *Reading* `memory/event-trace/*.jsonl` at analysis time, as a correlation
   source for the sub-agent tier, is permitted; writing to it is not.
2. **Budget** — at least 1 probe, never more than 10, typically 2–6. If more than 10 seem necessary
   the hypothesis set is too broad: narrow it in Phase 3 rather than exceeding the ceiling. The
   ceiling is global: no boundary, and no inventory entry below, earns a probe budget of its own.
3. **Tag** — every probe carries the `hypothesisId` of the Phase 3 hypothesis it tests. A probe that
   maps to no hypothesis is not inserted.
4. **Boundary inventory** — when the suspect data crosses a tier, first list the boundaries it could
   cross: HTTP route/handler definitions; outbound HTTP client call sites (`fetch`/`axios`/`requests`
   or the language's equivalent); queue or job publish/consume points; sub-agent spawn sites. This
   step is **discovery-only**: it answers *where could I probe*, never *where do I probe*. Building
   the inventory does not authorise a probe — step 3's hypothesis gate still decides which inventory
   entries get instrumented, and an entry no hypothesis reaches stays uninstrumented. A module shared
   by both sides of one tree is one boundary, not two. An empty inventory (single-process project) is
   a normal result: proceed through the steps below unchanged.
5. **Placement** — choose from: function entry with parameters; function exit with return values;
   values immediately before/after a critical operation; which branch executed; state mutations. At a
   boundary the hypothesis gate did select, probe both sides of the hop — sending and receiving.
6. **Correlate** — probes on either side of a hop must be provably about the same request. Carry a
   W3C Trace Context `traceparent`-shaped value: one **trace-id** shared by every probe belonging to
   one request, and a **span-id** unique to each probe. This is a naming and shape convention only —
   adopt the `traceparent` header name and the ID shape, never an SDK, library, or dependency. Where
   the hop carries headers, propagate it as the `traceparent` header; where it cannot — a queue
   message, a background job, a sub-agent spawn — the correlation value must ride **in the payload**
   instead. A hop that drops the value produces a **fragmented trace**: the downstream side starts a
   new trace-id and the two sides no longer join. A probe pair with mismatched trace-ids is evidence
   about that hop, not about the hypothesis.
7. **Payload** — append one JSON object per line (NDJSON), fields
   `hypothesisId`, `location`, `message`, `data`, `timestamp`, `traceparent` — so the log is parsed
   programmatically, not read by eye. `traceparent` belongs on any probe sitting at a boundary; omit
   it when the inventory is empty, since a single-process run has no hop for it to join. Never log
   secrets, tokens, API keys, or PII in `data`; the correlation value is not `data` for that rule's
   purposes, but must never embed a session token. A probe may also capture a **stack trace** to
   identify its caller — the secrets/PII rule above is unchanged and applies to it, since a stack
   embeds paths and may embed argument values. Under test, write the probe output somewhere test
   output actually surfaces (the runner's captured stdout/stderr, or the NDJSON file read back
   afterwards); a project logger may be suppressed by the test harness and swallow every probe.
8. **Wrap** — every probe sits between `#region debug log` and `#endregion` markers in
   language-appropriate comment syntax (`//`, `#`, `--`, `/* */`); they need only be greppable.
9. **Run** — clear the log file first so runs do not mix, run the Phase 1 feedback loop, then read
   the file back and resolve each hypothesis at the Checkpoint below.

**Backward tracing** — use this to pick probe *sites* when the bug has the shape *a value is already
invalid when it arrives*. It does not apply to a perf regression or a flaky test, and it replaces
none of step 5's Placement options, which still decide what each probe records. In order:
observe the symptom; identify the code that directly produced it; identify that code's caller;
continue up the call chain recording the value passed at each level; and locate where the invalid
value originated — that origin, not the site that surfaced it, is where the fix belongs.

If no seam exists for a probe (compiled dependency, third-party binary), fall back to the Phase 1
ladder's differential and bisection rungs. For perf: measure a baseline first (profiler/timing/query
plan), then bisect.

**Red flags — the method has already been abandoned.** Any one of these returns you to **Phase 1**:
proposing a fix before tracing to an origin; changing more than one variable at a time; asserting a
cause without evidence from the loop; reaching for a quick fix under time pressure. These fire
*before* the Stuck-Loop Checkpoint below and do not replace it — the Checkpoint counts disproven
hypotheses and offers a choice of three options, while red flags catch the behaviour earlier and
offer no choice at all.
