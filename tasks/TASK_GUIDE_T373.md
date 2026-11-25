# TASK_GUIDE — T373: the docs page tells users how to set the `[admin]` push remote, and says what T368 changed
**Date**: 2026-11-25
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`
**Track**: minimal — Record: `tasks/MINIMAL_LOG.md`

## Requirement

User (2026-11-25), about the `EASY_KIT_ADMIN_REMOTE` command: "with this, do we need to add the guide for that". Only `docs/claude-md/tracks.md` (agent doctrine) names the setting; `site/docs.html` and `README.md` do not, so a user whose remote is not `origin` sees `[admin]` refuse every push with no user-facing explanation. The same `#tracks` text still says a tests-only change skips and that a `fail` ends the loop, which T368 changed.

## Acceptance Criteria

1. `site/docs.html` `#tracks` (inside its `details.more`) says `[admin]` and `[ticket]` push to `origin` unless `EASY_KIT_ADMIN_REMOTE` in `.claude/settings.local.json` `"env"` names another remote, then restart Claude Code.
2. The same text says a changed `tests/**/test_*.sh` suite gets a real run (PASS or FAIL), and that under `[admin]` a `fail` starts a fix round, at most 2 (T368).
3. The site's paragraph pins (`tests/test_site_story.py`, `tests/test_site_visual_first.py`) name the changed paragraphs as changed by T373; the site suites pass.

## Dependencies & Reachability

**Depends on**: T321, T368
**Entry point**: Standalone — N/A

## Verification Command

```bash
python3 -m pytest tests/test_site_story.py tests/test_site_visual_first.py tests/test_site_content.py -q
```

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/docs.html` | two `#tracks` paragraphs |
| `tests/test_site_story.py`, `tests/test_site_visual_first.py` | the changed paragraph hashes |
| `tasks/MINIMAL_LOG.md` | the Decision record |
