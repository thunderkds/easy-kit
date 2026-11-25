# write-better-skill — Sourcing

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

**Start from real expertise.** A skill drafted from the model's general training knowledge produces generic filler — "handle errors appropriately", "follow best practices" — instead of the specific conventions, edge cases, and commands that make a skill worth loading. The model already knows the generic version; the skill exists for what it does not know.

Source material must be **project-specific**: execution traces (`memory/event-trace/`), corrections the user made mid-task, git history — especially fixes, which show what actually went wrong — review comments, and real failure cases (`memory/learnings.md`).

Two routes to it:
- **Extract from a completed hands-on task.** Run the real task with an agent, then lift the reusable pattern: the sequence that worked, each correction you made, the input/output shapes, and the project facts you had to supply.
- **Synthesize from existing project artifacts.** Feed the body of knowledge you already have — runbooks, specs, schemas, configs, incident write-ups — and draft from it. A skill built from this repo's own hook failures beats one built from an article about writing hooks.

Then refine against real execution: run the draft on real tasks and feed back *all* results, not just the failures. Read the traces, not only the final output — an agent trying several approaches signals instructions that are too vague; an agent following an instruction that does not apply signals one that should be conditional or cut.
