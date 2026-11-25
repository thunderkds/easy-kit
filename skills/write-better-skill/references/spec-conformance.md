# write-better-skill — Agent Skills Spec Conformance

> Moved here verbatim from `SKILL.md` by T355, so the skill body fits Codex's 8 KB cap. Read it when `SKILL.md` points here.

This framework's skills implement the open [Agent Skills specification](https://agentskills.io/specification). The rules below are **normative** — a skill that breaks one is malformed, not merely unpolished. Checked automatically by `.claude/hooks/tests/test_skill_spec_conformance.py` over every directory in `skills/`.

**`name`** (required):
- 1–64 characters
- unicode lowercase alphanumeric (`a-z`, `0-9`) and hyphens (`-`) only — uppercase is invalid
- must not start or end with a hyphen
- must not contain consecutive hyphens (`--`)
- must match the parent directory name

**`description`** (required): non-empty, max 1024 characters. Craft guidance is in *Writing the description* above; this is the hard limit.

**Optional fields:**
- `license` — the licence applied to the skill. Add only when the skill ships under terms different from the repo's; keep it to a licence name or a bundled file name.
- `compatibility` — max 500 characters. Add only when the skill has real environment requirements (intended product, required system packages, network access). Most skills do not need it.
- `metadata` — a map from string keys to string values, for properties the spec does not define. Use unique-ish key names to avoid collisions.
- `allowed-tools` — **out of scope in this framework.** The spec marks it Experimental and states support varies by implementation; no skill here uses it.

**Progressive-disclosure budgets** (spec numbers, not prose):
- metadata (`name` + `description`) ≈ **100 tokens**, loaded at startup for **every** skill — this is why description pruning pays repo-wide
- `SKILL.md`: **≤ 500 lines** and **≤ 5,000 tokens** once the skill activates. The line budget is measured over the **whole file, frontmatter included** — trimming the body to exactly 500 still fails, because the conformance test counts every line in `SKILL.md`.
- resources (`scripts/`, `references/`, `assets/`) load **on demand only**

**Bundled directories** — the spec's conventional layout beside `SKILL.md`:
- `scripts/` — executable code the agent runs; self-contained or with documented dependencies
- `references/` — documentation loaded on demand; keep each file focused
- `assets/` — templates, images, data files

**File references** use relative paths from the skill root (`references/REFERENCE.md`, `scripts/extract.py`) and stay **one level deep**. Avoid deeply nested reference chains.

**Script calls** name the script by `${CLAUDE_SKILL_DIR}`, never by a repo-relative path: the user's project holds none of the kit's files when the kit runs as a plugin (T234). One rule serves the plugin and a `setup.sh` install. Quote the variable, because the folder may hold a space. A skill's own script: `python3 "${CLAUDE_SKILL_DIR}/scripts/x.py"`. A shared script in the kit's `scripts/`: `python3 "${CLAUDE_SKILL_DIR}/../../scripts/x.py"`. Claude Code fills the variable in `SKILL.md`; in a `references/` file read it as the skill's base directory. In a `setup.sh` install the value is `<project>/.claude/skills/<name>`, and `.claude/skills` is a symlink. A script that finds the kit by its own location uses `os.path.realpath(__file__)`, never `abspath`, which drops `..` without following the symlink. The Codex installer rewrites the variable in its copies (`lib/harness-fetch.sh`, `_harness_rewrite_skill_dir`): the source files keep it. A script finds the project by the working directory (`script_project_root()` in `.claude/hooks/lib/project_root.py`), not by its own location. `tests/test_plugin_names.py` runs every command in both layouts and fails on a repo-relative call.
