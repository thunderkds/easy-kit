# TASK_REVIEW — T280: The home page journey flow gets a sixth step, Improve it (self-review)

> Sibling of `tasks/TASK_GUIDE_T280.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

<!-- Optional: the final report, only for a task run in auto mode (the user's `[auto]` tag,
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_t280_home_improve_step.py` (AC 1, 2, 4, 5: 4 tests); `tests/test_site_story.py` three edited pins (AC 7). Red first: before the `index.html` edit, `6 failed, 51 passed` (4 new + 2 edited pins; the merge-step pin is title-based so it stayed green on both trees). |
| Verification command run | ☑ pass | 2026-11-07T12:03:44Z `python3 -m pytest tests/test_t280_home_improve_step.py tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_t151.py -q` -> `223 passed in 0.61s` (after the Stage 4 fixes). `<main>` words: 300 of 300 (`WORD_CAP` untouched). Full `tests/` run `1910 passed` was taken before the two Stage 4 fixes (see smoke row). |
| Negative cases hold | ☑ pass | Re-run after the Stage 4 fixes. Mutation: removed the sixth `li` (`git diff --stat site/index.html` vs the commit -> `1 file changed, 5 deletions(-)`); run gave `6 failed, 51 passed`: 4 in `test_t280_home_improve_step.py` and `test_journey_is_an_ordered_list_of_six_steps_each_linking_into_the_docs`, `test_journey_marks_the_users_three_steps_with_a_text_label` in `test_site_story.py`. Restored from a saved copy (`git diff --stat` back to `1 insertion(+), 1 deletion(-)`, the P3 edit only); suite `223 passed in 0.60s`. Red first for the P3 edit: with the new fullmatch and the old `Optional:` markup, `1 failed, 3 passed`. |
| verify | ☑ N/A | Not run by the frontend agent: only the Supervisor's headless auto verify run writes this row. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Blast radius: `site/index.html` and the site pin tests. Stale-reference grep of `README.md`, `RUNBOOK.md`, `docs/claude-md/`, `agents/` for "five steps" / "5 steps": no hit. Two text-only hits in `tests/test_site_story.py` left unedited by scope: docstring line 244 ("the five steps are the full journey") and assert message line 693 ("the five-step journey stacks at 1100px"). code-review skill not run (no Skill tool). |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest tests -q -x` -> `1910 passed in 154.37s (0:02:34)`. |
| **Companion score (easy-verifier)** | ☑ N/A | Not run: no companion tool is available to the frontend agent; the merge gate blocks on fail only. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | Screenshots read: `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-375-full.png`, `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-768-full.png`, `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-1280.png`, `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-1280-v2.png` (after the P3 fix). Six nodes in order; "Your step" on 1, 5 and 6; green outcome stays on "You merge"; "Skills by stage" follows unchanged. ux-evaluate table below. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | The new node reuses existing classes `flow-node is-yours is-link` (same as "You ask"); `git status` shows `site/theme.css` untouched; no new class, colour or image. |
| **UI: Responsiveness at target viewports** | ☑ pass | 375px (iframe; headless Chrome cannot open a window under 500px): inside a 375px iframe `documentElement.scrollWidth=360 clientWidth=360` (15px scrollbar), `ol scrollWidth=328 clientWidth=328`, 6 nodes all `left=16 width=328`, stacked: no sideways scroll. 768px: stacked. 1280px: one row of six, no clipped text. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-11-07T09:56:36Z on the unchanged tree, HEAD `f60e63ab`, before any implementation commit):

(a) Prior `#journey` section of `site/index.html` (lines 78-109) and the four `#deeper` cards (lines 201-204), verbatim:

```html
<section id="journey">
<h2>The full journey</h2>
<div class="flow-visual">
  <ol class="flow flow-row is-long" aria-label="From your request to the merge, in order">
    <li class="flow-node is-yours is-link">
      <span class="flow-key">Your step</span>
      <span class="flow-title"><a href="docs.html#quick-reference">You ask</a></span>
      <span class="flow-desc">Say what you want.</span>
    </li>
    <li class="flow-node is-link">
      <span class="flow-key">Easy Kit</span>
      <span class="flow-title"><a href="docs.html#what-you-get">It plans</a></span>
      <span class="flow-desc">A written plan comes first.</span>
    </li>
    <li class="flow-node is-link">
      <span class="flow-key">Easy Kit</span>
      <span class="flow-title"><a href="docs.html#agent-roles">Agents build</a></span>
      <span class="flow-desc">Agents work in separate copies.</span>
    </li>
    <li class="flow-node is-link">
      <span class="flow-key">Easy Kit</span>
      <span class="flow-title"><a href="docs.html#hooks">It checks</a></span>
      <span class="flow-desc">Tests and review run before shipping.</span>
    </li>
    <li class="flow-node is-yours is-link is-outcome">
      <span class="flow-key">Your step</span>
      <span class="flow-title"><a href="docs.html#tracks">You merge</a></span>
      <span class="flow-desc">You review. Easy Kit merges only when you ask.</span>
    </li>
  </ol>
</div>
</section>
```
```html
  <li class="card"><h3><a href="docs.html#agent-roles">Agents</a></h3><p>Backend, frontend, infrastructure and QA roles.</p></li>
  <li class="card"><h3><a href="docs.html#skills">Skills</a></h3><p>Ready-made steps for each part of the journey.</p></li>
  <li class="card"><h3><a href="docs.html#memory-system">Memory</a></h3><p>Notes that carry decisions forward.</p></li>
  <li class="card"><h3><a href="docs.html#packs">Add-ons</a></h3><p>Optional domain packs and <a href="docs.html#mcps">MCP tools</a>.</p></li>
```

(b) Existing tests on the unchanged tree (`tests/test_t280_home_improve_step.py` does not exist yet):

```
$ date -u; python3 -m pytest tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_t151.py -q
2026-11-07T09:56:36Z
219 passed in 0.79s
$ <main> visible-word count of index.html (test_site_story.visible_words)
main words 300      (cap WORD_CAP = 300)
```

**AFTER** (2026-11-07T09:58:10Z, same commands, post-change):

```html
    <li class="flow-node is-yours is-link is-outcome">   <!-- You merge: unchanged -->
      ...
    </li>
    <li class="flow-node is-yours is-link">
      <span class="flow-key">Your step</span>
      <span class="flow-title"><a href="docs.html#skills">You improve it</a></span>
      <span class="flow-desc"><code>/self-review</code> (optional)</span>
    </li>
  </ol>
...
  <li class="card"><h3><a href="docs.html#agent-roles">Agents</a></h3><p>Backend, frontend, infrastructure, QA.</p></li>
  <li class="card"><h3><a href="docs.html#skills">Skills</a></h3><p>Ready-made steps for the journey.</p></li>
  <li class="card"><h3><a href="docs.html#memory-system">Memory</a></h3><p>Notes carry decisions forward.</p></li>
  <li class="card"><h3><a href="docs.html#packs">Add-ons</a></h3><p>Optional domain packs and <a href="docs.html#mcps">MCP tools</a>.</p></li>   <!-- unchanged -->
```

```
$ python3 -m pytest tests/test_t280_home_improve_step.py tests/test_site_story.py tests/test_site_content.py tests/test_site_visual_first.py tests/test_docs_t151.py -q
223 passed in 0.57s            (219 before + 4 new)
$ <main> words: 300 of 300     (cap unchanged)
```

**DELTA**: A visitor to the home page now sees, in "The full journey", an optional sixth step "You improve it / /self-review (optional)" that links to the docs diagram.

**WITNESS**: frontend-developer ran it 2026-11-07 (the implementing agent alone; the Supervisor adds the witness from `memory/event-trace/T280.jsonl`). [template note: derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

---

## ux-evaluate verdict (frontend-developer, 2026-11-07)

Screenshots (scratch, not committed): `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-375-full.png`, `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-768-full.png`, `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-1280.png`. 375px was a 375px iframe inside a 500px headless window (Chrome cannot open a window under 500px); widths were measured in the iframe, not with `--dump-dom`.

| # | User story | Flow / state | Width | Verdict | Screenshot | Reason |
|---|------------|--------------|-------|---------|------------|--------|
| 1 | "should show the overview flow in the home" | Home, "The full journey" | 375 / 1280 | pass | journey-375-full.png, journey-1280.png | Sixth node "Your step / You improve it / /self-review (optional)" shows without a click at both widths; its title is a link to `docs.html#skills` (checked by the new test) |
| B-a | baseline | default | 375 / 1280 | pass | same | Task adds no action; the install Copy button is unchanged and in view at 1280 |
| B-b | baseline | default | 375 / 1280 | pass | same | Heading, six nodes, next section in one reading order |
| B-c | baseline | default | 375 / 1280 | pass | same | Same gaps and arrows as the other nodes. At 1280 `/self-review` first wrapped at its hyphen; after the Stage 4 fix (`<code>/self-review</code> (optional)`) `journey-1280-v2.png` was read and the command stays on one line, "(optional)" below it |
| B-d | baseline | default | 375 | pass | journey-375-full.png | `.story .flow-title a::after` stretches the link over the whole node (`site/theme.css:438`), about 328x92px; `tap_probe.py` ran (page `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/tap/index-probe.html`, not shot) |
| B-e | baseline | default | 375 / 1280 | pass | same | Node text is the existing flow-desc size; readable on the dark ground |
| B-f | baseline | default | 375 / 1280 | not checkable | n/a | The guide names no empty, loading, error or success state |
| B-g | baseline | default | 375 / 1280 | not checkable | n/a | No action with feedback in this change |
| B-h | baseline | default | 375 | pass | journey-375-full.png | Steps stack one per row; iframe `scrollWidth=360 clientWidth=360`, `ol scrollWidth=328 clientWidth=328` |
| B-h | baseline | default | 1280 | pass | journey-1280.png | One row of six, last node not green; the green outcome stays on "You merge" |
| B-i | baseline | default | 375 / 1280 | pass | same | Same accent, border and radius as the other nodes |

ux-evaluate: 9 pass, 0 fail, 0 not checked, 2 not checkable. Overall: pass (the two `not checkable` rows name no state or action in this change).

Stage 4 re-check (2026-11-07): `/tmp/claude-1000/-home-hungnguyenhuu-workspace-pets-personal-agentic-claude/bb743e7c-a3c3-44e9-972e-46e28295830d/scratchpad/journey-1280-v2.png` read at 1280px: six nodes in one row, `/self-review` on one line with "(optional)" under it, green outcome still on "You merge". B-c pass, no `not checkable` change.
