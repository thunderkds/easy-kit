# write-better-skill — Fidelity Gate (Hallucination Check)

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

Consulted by `teach` and `craft-agent` immediately before they emit a draft — a drafted skill/agent is *durable*: unlike a bad code change caught by Stage 4 review for one task, a hallucinated or over-scoped draft lives in `skills/` or `agents/` and silently affects every future session until someone notices.

Check every claim in the draft against a source, not against plausibility:

1. **Traceability** — every capability the draft claims (each Workflow step, each Karpathy override, each "Required skills/expertise" line) must trace to `PRD.md`, `PROJECT_SPEC.md`, or the user's literal words in the current session. An untraceable claim is a hallucination — cut it, don't soften it.
2. **Reference resolution** — every `Skill({ skill: "..." })` or `Agent({ subagent_type: "..." })` call written inside the draft must resolve to a name that actually exists (check `skills/*/SKILL.md` and `agents/*.md` frontmatter). If it doesn't, don't drop the draft — flag the line inline as `[UNRESOLVED: references "<name>" — does not exist yet, draft separately]` and still emit.
3. **Scope containment** — the draft must not claim authority the Permanent Rules reserve elsewhere (e.g. an agent writing to `memory/` directly, when only the Supervisor writes memory). Flag any such overreach rather than emitting it silently.

**Completion criterion**: every claim traces to a source or is cut; every internal `Skill()`/`Agent()` reference resolves or is flagged `[UNRESOLVED: ...]`; no unflagged Permanent-Rules overreach. State "Fidelity gate: PASS" or list the cuts/flags immediately before the Registration checklist.
