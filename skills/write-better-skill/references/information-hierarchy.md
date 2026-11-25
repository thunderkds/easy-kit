# write-better-skill — Information Hierarchy

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

A skill is built from **steps** (ordered actions) and **reference** (rules, definitions, facts). The hierarchy ranks by how immediately the agent needs the material:

1. **In-skill step** — an ordered action in SKILL.md. Each step ends on a **completion criterion**: checkable (can the agent tell done from not-done?) and exhaustive ("every modified file accounted for", not "produce a change list"). Vague criteria invite **premature completion**.
2. **In-skill reference** — definitions and rules consulted on demand. A legitimately flat peer-set is fine (not a smell). This skill is all reference.
3. **External reference** — pushed out of SKILL.md into a sibling file (e.g. `GLOSSARY.md`), reached via a **context pointer**. Loaded only when the pointer fires.

**Progressive disclosure** is the move down the ladder — out of SKILL.md into a linked file — so the top stays legible. A **context pointer** must name the *trigger condition* for loading the file, not just its existence, and must be written as a **Markdown link** — the two pointers in this file are the worked examples: each names when to load its target, and each is a link. Never a bare "see `references/` for details", and never a path in plain backticks: `.claude/hooks/tests/test_skill_reference_pointers.py` resolves links only, so a backticked path is a pointer nothing checks — it can rot to a missing file and the suite stays green. A pointer without a trigger condition is a pointer the agent cannot decide to follow; a pointer without link syntax is one nothing can verify.

**Co-location**: keep a concept's definition, rules, and caveats under one heading so reading one part brings its neighbours.

Split signal: inline what every branch needs; push behind a pointer what only some branches reach.

