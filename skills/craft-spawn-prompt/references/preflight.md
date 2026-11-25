# craft-spawn-prompt — Step 4 — the pre-flight structural-reference check

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

Read `extract_structural_task_ids()` directly from `.claude/hooks/pre_agent_validate_guide.py` — do not re-derive or approximate the pattern, it must stay byte-for-byte in sync with what the hook enforces. Run it against the assembled prompt text:
- For every extracted task ID, confirm `tasks/TASK_GUIDE_T<id>.md` exists on disk.
- If the prompt names a `TASK_GUIDE_Txxx.md` but has no `<!-- memory-slice:` marker, **flag** it as "memory slice missing — element 4 not run"; likewise flag one with no line starting `**Startup reads**` as "startup reads missing — element 8 not run". The spawn hook warns on both conditions; it never blocks.
- If any extracted ID has no matching file, **flag** it in the output as "would be rejected by the spawn hook" — do not alter the prompt to work around it.
- Prose-only `Txxx` mentions (e.g. in an orienting-content excerpt) that don't match either structural marker (a `TASK_GUIDE_Txxx.md` reference, or a `Task ID:` declaration line) are correctly ignored by the hook and must not be flagged here.
