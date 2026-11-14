"""T307 — `[admin]` runs a task from start to end; it asks only at project start, stops only for
high-impact events.

Locked oracle of `tasks/TASK_GUIDE_T307.md` (AC 1-8), written by QA before the doc edits.

How the pins work:
- Rules are pinned by short anchors (a phrase or a regex) inside one named section of
  `docs/claude-md/tracks.md`, not by whole sentences, so the implementer picks the wording.
  Where an AC binds several facts together, the anchors must share one paragraph (AC 1, 4, 7) or
  one sentence (AC 2, 8).
- Frozen text (`### Stops that stay`, rows 1-4, the `[auto]` list of `### Never in auto mode`)
  is pinned by a SHA-256 of its bytes at base commit `fbdbd62` (T306 merged). A hash, not
  `git show`, so the test runs in a checkout with no history; `test_frozen_hashes_match_base_commit`
  cross-checks the hashes against `git show fbdbd62:...` when git can read that commit.
- Every pin set has a mutation control: the anchor cut out of a copy of the section makes the
  check fail. A mutation control first asserts the check passes on the real text, so it is red
  until the doc edits land.
"""
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ROOT / "docs" / "claude-md" / "tracks.md"
SKILLS = ROOT / "skills"
BASE_COMMIT = "fbdbd62"
CODEX_CAP = 8192  # lib/harness-fetch.sh `harness_skill_body_cap`: a Codex skill body over 8192 bytes is skipped


def _norm(text):
    return " ".join(text.split())


def section(text, heading):
    """Raw `### <heading>` section: from its heading line up to the next `##`/`###` heading."""
    m = re.search(r"^### " + re.escape(heading) + r"[^\n]*\n.*?(?=^##+ |\Z)", text, re.M | re.S)
    return m.group(0) if m else ""


def paragraphs(raw):
    """Blank-line separated blocks, each whitespace-normalised. A list with no blank lines is one block."""
    return [_norm(p) for p in re.split(r"\n\s*\n", raw) if p.strip()]


def sentences(raw):
    """Sentences of a section: split after `.`, `!` or `?` when a capital, backtick or bracket follows."""
    out = []
    for p in paragraphs(raw):
        out.extend(s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`(\[])", p) if s)
    return out


def table_row(text, n):
    rows = [l for l in text.splitlines() if l.startswith(f"| {n} |")]
    assert len(rows) == 1, f"row {n}: {len(rows)} lines"
    return rows[0]


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def tracks():
    return TRACKS.read_text(encoding="utf-8")


def _cut(raw, pattern):
    """Remove every match of `pattern` (a regex) from `raw`; assert it matched."""
    mutated, hits = re.subn(pattern, "", raw)
    assert hits >= 1, f"anchor not in section: {pattern}"
    assert mutated.encode() != raw.encode()
    return mutated


def _need(block, anchors, where):
    for pat in anchors:
        assert re.search(pat, block), f"{where}: missing anchor {pat!r}"


def _block_with(blocks, key, anchors, where):
    """One block (paragraph or sentence) must hold `key` and every anchor."""
    hits = [b for b in blocks if re.search(key, b)]
    assert hits, f"{where}: no block holds {key!r}"
    errors = []
    for b in hits:
        try:
            _need(b, anchors, where)
            return
        except AssertionError as e:
            errors.append(str(e))
    raise AssertionError(f"{where}: no single block holds {key!r} with all anchors: {errors}")


# ── AC 1: Stage 0 questions only on a new project (`## Readiness` has no `Approved by`) ──────
AC1_KEY = r"Approved by: user"
AC1_ANCHORS = (
    r"`## Readiness`",
    r"new project",
    r"rows? 1[–-]4",
    r"Waived",          # Edge Case Checklist: a `Waived:` line counts as approved
)


def check_ac1(text):
    _block_with(paragraphs(section(text, "Admin tag")), AC1_KEY, AC1_ANCHORS, "AC 1 `### Admin tag`")


def test_ac1_admin_asks_stage0_only_on_new_project():
    check_ac1(tracks())


# ── AC 2: business domain first (`PRD.md`, glossary, `docs/legacy/`) before code ────────────
AC2_KEY = r"`docs/legacy/`"
AC2_ANCHORS = (r"`PRD\.md`", r"glossary", r"\bbefore\b|\bfirst\b", r"\bcode\b")


def check_ac2(text):
    _block_with(sentences(section(text, "Admin tag")), AC2_KEY, AC2_ANCHORS, "AC 2 `### Admin tag`")


def test_ac2_admin_tag_cites_business_domain_first():
    check_ac2(tracks())


RQ = SKILLS / "resolve-question" / "SKILL.md"
RQ_ANCHORS = (r"`\[admin\]`", r"`PRD\.md`", r"\bfirst\b|\bbefore\b")


def check_ac2_resolve_question(text):
    _block_with(paragraphs(text), AC2_KEY, RQ_ANCHORS, "AC 2 resolve-question")


def test_ac2_resolve_question_names_domain_documents_first():
    check_ac2_resolve_question(RQ.read_text(encoding="utf-8"))


# ── AC 3: `ship` runs under `[admin]` as a plan only; never a deploy ─────────────────────────
PLAN_ONLY = r"plan only|only (as )?a plan|as a plan, never"
AC3_ADMIN_ANCHORS = (
    r'Skill\(\{ skill: "ship" \}\)',
    PLAN_ONLY,
    r"never runs? (a |any )?deploy",
)
OLD_SHIP_ADMIN = "`ship` stays the user's with `[admin]` too"
OLD_SHIP_BOTH = "`ship` stays the user's with both tags"


def check_ac3_admin(text):
    body = _norm(section(text, "Admin tag"))
    _need(body, AC3_ADMIN_ANCHORS, "AC 3 `### Admin tag`")
    assert OLD_SHIP_ADMIN not in body, "AC 3: `### Admin tag` still says ship stays the user's"


def check_ac3_never(text):
    raw = section(text, "Never in auto mode")
    admin = [p for p in paragraphs(raw) if "`[admin]`" in p]
    assert admin, "AC 3: no `[admin]` paragraph in `### Never in auto mode`"
    joined = " ".join(admin)
    assert re.search(PLAN_ONLY, joined), "AC 3: `### Never in auto mode` lacks ship-as-plan-only for `[admin]`"
    assert "`ship`" in joined
    assert OLD_SHIP_BOTH not in _norm(raw), "AC 3: `### Never in auto mode` still says ship stays the user's with both tags"


def check_ac3_row19(text):
    row = _norm(table_row(text, 19))
    assert "`[admin]`" in row and "`ship`" in row and re.search(PLAN_ONLY, row), \
        "AC 3: row 19 lacks `ship` as a plan only with `[admin]`"


def test_ac3_admin_tag_runs_ship_as_plan_only():
    check_ac3_admin(tracks())


def test_ac3_never_in_auto_mode_allows_ship_plan_with_admin():
    check_ac3_never(tracks())


def test_ac3_row19_allows_ship_plan_with_admin():
    check_ac3_row19(tracks())


# ── AC 4: stops only for `### Stops that stay`, says so in one line; the list is frozen ──────
AC4_KEY = r"`### Stops that stay`"
AC4_ANCHORS = (r"\bonly\b", r"one line")
STOPS_SHA = "d73098dc6936799271e92a480c793e05477f8e24d361c6a8e9df3d2cc658832b"  # base text (BASE_COMMIT)
STOPS_SHA_NOW = "47cc25b7fd1f2be158ee4224210149a78060e5338fe2a808ba9aaa62e782fccf"  # T310: new `[admin]` unsettled-Debate bullet


def check_ac4(text):
    _block_with(paragraphs(section(text, "Admin tag")), AC4_KEY, AC4_ANCHORS, "AC 4 `### Admin tag`")


def check_stops_frozen(text, sha=STOPS_SHA_NOW):
    raw = section(text, "Stops that stay")
    assert raw, "no `### Stops that stay` section"
    assert _sha(raw) == sha, "AC 4: `### Stops that stay` changed (must be byte-for-byte the base text)"


def test_ac4_admin_stops_only_for_stops_that_stay():
    check_ac4(tracks())


def test_ac4_stops_that_stay_is_byte_for_byte_unchanged():
    check_stops_frozen(tracks())


# ── AC 5: plain `[auto]` reads as today (negative control) ──────────────────────────────────
ROW_SHA = {
    1: "9a4edd379a35a4ffd0c9b51d4b764923af0d7a51422381cd3a109a166f52b2d8",
    2: "12bb2cf5e9266c60af0d3f7af46b3c22804a718fdccca2299e93893a582cae4a",
    3: "8287e283ace7d0f58130cae1c28d607d85dbcf889307ebe13a3e379f95cc689c",
    4: "913e95e2e68d637d5bce8d13daff8bd496f28e2c8b4d9d878d14bb7773b8d658",
}
AUTO_LIST = "With `[auto]`, these stay the user's:\n\n- merge;\n- pull;\n- push;\n- `ship`.\n"
ROW19_KEEP = (
    "| 19 | Stage 5 items 3–6: memory update, merge, Done, `ship` |",
    "Memory update: the Supervisor runs the diff-driven pass before it stops, and writes the `Memory:` line.",
    "Done: after an auto verify pass, the hook moves the row (`### Auto close-out`).",
    "The task waits in Ready for Review until the hook moves it.",
    "| `Memory:` / `Closed:` / `Not done:` |",
)


def check_rows_frozen(text):
    for n, sha in ROW_SHA.items():
        assert _sha(table_row(text, n)) == sha, f"AC 5: row {n} changed (plain `[auto]` must read as today)"


def check_never_auto_list(text):
    assert AUTO_LIST in section(text, "Never in auto mode"), "AC 5: the `[auto]` list of `### Never in auto mode` changed"


def check_row19_auto(text):
    row = table_row(text, 19)
    for keep in ROW19_KEEP:
        assert keep in row, f"AC 5: row 19 lost {keep!r}"
    # With `[auto]` alone, `ship` is still never run: a clause pairs `ship` with "never".
    assert re.search(r"`ship`[^.|]*never|never[^.|]*`ship`", row), "AC 5: row 19 no longer says `ship` is never run in auto mode"


def test_ac5_rows_1_to_4_unchanged():
    check_rows_frozen(tracks())


def test_ac5_never_in_auto_mode_auto_list_unchanged():
    check_never_auto_list(tracks())


def test_ac5_row19_auto_clauses_unchanged():
    check_row19_auto(tracks())


# ── AC 6: `git pull` stays blocked; `Approved by` never written by the Supervisor ────────────
AC6_PULL = r"a `git pull`[^.]*stay blocked"      # today's item 2 wording; a regression guard
AC6_APPROVED = (r"Approved by", r"\bnever\b")


def check_ac6_admin(text):
    raw = section(text, "Admin tag")
    assert re.search(AC6_PULL, _norm(raw)), "AC 6: `### Admin tag` no longer keeps `git pull` blocked"
    _block_with(sentences(raw), r"Approved by", AC6_APPROVED[1:], "AC 6 `### Admin tag` (Approved by never written)")


def check_ac6_never(text):
    """`### Never in auto mode` `[admin]` paragraph: pull stays the user's.

    Base text says "the Supervisor may also do the first two" of merge; pull; push; `ship` — that
    reads as merge and pull, which contradicts AC 6 (the gate allows merge and push, never pull)."""
    admin = " ".join(p for p in paragraphs(section(text, "Never in auto mode")) if "`[admin]`" in p)
    assert "first two" not in admin, "AC 6: `the first two` reads as merge and pull"
    assert re.search(r"pull[^.]*(stays?|blocked|never|user's)|never[^.]*pull", admin), \
        "AC 6: `### Never in auto mode` does not keep pull with the user under `[admin]`"


def test_ac6_admin_tag_keeps_pull_blocked_and_approved_by_user_only():
    check_ac6_admin(tracks())


def test_ac6_never_in_auto_mode_keeps_pull_for_admin():
    check_ac6_never(tracks())


# ── AC 7: one list of self-given approvals and decisions, each logged; no "please approve" ───
AC7_KEY = r"Requirement Fidelity Gate"
AC7_ANCHORS = (
    r"rows? 2[–-]4",
    r"7[–-]13",
    r"\b15\b",
    r"\b17\b",
    r"\b21\b",
    r"agent team",
    r"task breakdown",
    r"direction",
    r"`tdd` plan",
    r"fix choice",
    r"`RULE`",
    r"`FACT`",
    r"`SAFER OPTION`",
    r"`DEBATED`",
)
AC7_NEVER = (r"your decision", r"please approve", r"\bnever\b")


def check_ac7(text):
    raw = section(text, "Admin tag")
    blocks = paragraphs(raw)
    _block_with(blocks, AC7_KEY, AC7_ANCHORS, "AC 7 `### Admin tag` list")
    _block_with(blocks, r"your decision", AC7_NEVER[1:], "AC 7 `### Admin tag` never asks")


def test_ac7_admin_tag_lists_self_given_approvals():
    check_ac7(tracks())


# ── AC 8a: the hand-backs left under `[admin]`, in one sentence ─────────────────────────────
AC8_KEY = r"`### Stops that stay`"
AC8_ANCHORS = (r"Approved by", r"row 5", r"`git pull`", r"second `?blocked`?")


def check_ac8_sentence(text):
    _block_with(sentences(section(text, "Admin tag")), AC8_KEY, AC8_ANCHORS, "AC 8 `### Admin tag` hand-back sentence")


def test_ac8_hand_backs_named_in_one_sentence():
    check_ac8_sentence(tracks())


# ── AC 8b: each stage skill points to `tracks.md` row N under `[admin]`; skills stay under cap ─
SKILL_ROWS = {
    "grill-with-docs": (2, 3),
    "brainstorming": (4,),
    "to-issues": (12,),
    "craft-agent": (11,),
    "settings-setup": (5,),
}


def check_skill_pointer(text, name):
    rows = SKILL_ROWS[name]
    row_re = r"\brows? (" + "|".join(str(r) for r in rows) + r")\b"
    _block_with(paragraphs(text), r"`\[admin\]`", (r"docs/claude-md/tracks\.md", row_re),
                f"AC 8 {name} pointer")


@pytest.mark.parametrize("name", sorted(SKILL_ROWS))
def test_ac8_skill_has_admin_pointer(name):
    check_skill_pointer((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"), name)


def check_cap(path):
    # Same measure as tests/test_resolve_question.py and tests/test_settings_setup.py (bytes on disk).
    assert path.stat().st_size <= CODEX_CAP, f"{path} is over the {CODEX_CAP}-byte Codex cap"


@pytest.mark.parametrize("name", sorted(SKILL_ROWS) + ["resolve-question"])
def test_ac8_skill_stays_under_codex_cap(name):
    check_cap(SKILLS / name / "SKILL.md")


# ── Frozen hashes really are the base text ──────────────────────────────────────────────────
def test_frozen_hashes_match_base_commit():
    try:
        base = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE_COMMIT}:docs/claude-md/tracks.md"],
                              capture_output=True, text=True, timeout=30, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        pytest.skip(f"git cannot read {BASE_COMMIT} here (shallow clone?)")
    check_stops_frozen(base, STOPS_SHA)  # T310: the base text keeps the base hash
    check_rows_frozen(base)
    check_never_auto_list(base)
    check_row19_auto(base)


# ── Mutation controls ───────────────────────────────────────────────────────────────────────
def _mutate_section(text, heading, pattern):
    raw = section(text, heading)
    assert raw, heading
    return text.replace(raw, _cut(raw, pattern), 1)


ADMIN_PINS = (
    [("ac1", check_ac1, p) for p in (AC1_KEY,) + AC1_ANCHORS]
    + [("ac2", check_ac2, p) for p in (AC2_KEY,) + AC2_ANCHORS[:2]]
    + [("ac3", check_ac3_admin, p) for p in AC3_ADMIN_ANCHORS]
    + [("ac4", check_ac4, p) for p in (AC4_KEY,) + AC4_ANCHORS]
    + [("ac6", check_ac6_admin, p) for p in (AC6_PULL, r"Approved by")]
    + [("ac7", check_ac7, p) for p in (AC7_KEY,) + AC7_ANCHORS + AC7_NEVER[:2]]
    + [("ac8", check_ac8_sentence, p) for p in (AC8_KEY,) + AC8_ANCHORS]
)


@pytest.mark.parametrize("check, pattern", [(c, p) for _, c, p in ADMIN_PINS],
                         ids=[f"{a}:{p}" for a, _, p in ADMIN_PINS])
def test_mutation_control_admin_tag_anchor_removed(check, pattern):
    original = tracks()
    check(original)
    with pytest.raises(AssertionError):
        check(_mutate_section(original, "Admin tag", pattern))


@pytest.mark.parametrize("pattern", [PLAN_ONLY, r"`\[admin\]`"])
def test_mutation_control_never_in_auto_mode(pattern):
    original = tracks()
    check_ac3_never(original)
    with pytest.raises(AssertionError):
        check_ac3_never(_mutate_section(original, "Never in auto mode", pattern))


def test_mutation_control_never_in_auto_mode_first_two_back():
    original = tracks()
    check_ac6_never(original)
    raw = section(original, "Never in auto mode")
    mutated = raw.replace("`[admin]`", "`[admin]` the Supervisor may also do the first two;", 1)
    with pytest.raises(AssertionError):
        check_ac6_never(original.replace(raw, mutated, 1))


def test_mutation_control_row19_plan_only_removed():
    original = tracks()
    check_ac3_row19(original)
    row = table_row(original, 19)
    with pytest.raises(AssertionError):
        check_ac3_row19(original.replace(row, re.sub(PLAN_ONLY, "", row), 1))


def test_mutation_control_resolve_question_anchor_removed():
    original = RQ.read_text(encoding="utf-8")
    check_ac2_resolve_question(original)
    with pytest.raises(AssertionError):
        check_ac2_resolve_question(_cut(original, AC2_KEY))


@pytest.mark.parametrize("name", sorted(SKILL_ROWS))
def test_mutation_control_skill_pointer_removed(name):
    original = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    check_skill_pointer(original, name)
    with pytest.raises(AssertionError):
        check_skill_pointer(_cut(original, r"docs/claude-md/tracks\.md"), name)


def test_mutation_control_stops_that_stay_one_byte():
    original = tracks()
    raw = section(original, "Stops that stay")
    check_stops_frozen(original)
    with pytest.raises(AssertionError):
        check_stops_frozen(original.replace(raw, raw.replace("the 4th Debate", "the 5th Debate", 1), 1))


@pytest.mark.parametrize("n", sorted(ROW_SHA))
def test_mutation_control_auto_row_changed(n):
    original = tracks()
    row = table_row(original, n)
    check_rows_frozen(original)
    with pytest.raises(AssertionError):
        check_rows_frozen(original.replace(row, row.replace("|", "| [admin]", 2), 1))


def test_mutation_control_auto_list_and_row19():
    original = tracks()
    check_never_auto_list(original)
    check_row19_auto(original)
    with pytest.raises(AssertionError):
        check_never_auto_list(original.replace("- pull;\n", "", 1))
    row = table_row(original, 19)
    with pytest.raises(AssertionError):
        check_row19_auto(original.replace(row, row.replace("The task waits in Ready for Review", "The task waits", 1), 1))


@pytest.mark.parametrize("name", sorted(SKILL_ROWS) + ["resolve-question"])
def test_mutation_control_cap_measure(name, tmp_path):
    big = tmp_path / "SKILL.md"
    big.write_bytes((SKILLS / name / "SKILL.md").read_bytes() + b"x" * CODEX_CAP)
    with pytest.raises(AssertionError):
        check_cap(big)
    exact = tmp_path / "exact.md"
    exact.write_bytes(b"x" * CODEX_CAP)
    check_cap(exact)  # boundary: exactly 8192 bytes is still installed
