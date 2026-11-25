# TASK_GUIDE — T367: CI fails on `main`: `tests/test_pack_catalog.sh` gives no answer to the agent-ws question
**Date**: 2026-11-25
**Complexity Level**: C0
**Risk Level**: Low
**Priority**: P0
**Assigned agent**: common-infrastructure
**Agent guide**: `agents/common-infrastructure.md`
**Track**: minimal — Record: `tasks/MINIMAL_LOG.md`

## Requirement

User (2026-11-25): "seem like the Ci is fail also". CI run 45570715182 on `d733a6a7` (v2.3.0) fails at step "Pack catalog test suite (T116)": `10 passed, 6 failed` ("FAIL: Claude Code + Codex were not both set up"). Cause: T353 added the Linux-only agent-ws question before `Proceed?`; `install_both` in `tests/test_pack_catalog.sh` still sends `'1\n1 2\n1\n\n'`, so its last Enter answers agent-ws and `Proceed?` gets none. Every other CI step passes locally (`shellcheck`, `validate.sh`, every `tests/*.sh` step, the drift guard).

## Acceptance Criteria

1. `bash tests/test_pack_catalog.sh` passes on Linux; on a non-Linux machine (no agent-ws question) it sends the old answers.
2. No other test or file changes.

## Dependencies & Reachability

**Depends on**: T353
**Entry point**: Standalone — N/A

## Verification Command

```bash
bash tests/test_pack_catalog.sh && bash tests/test_agent_ws_installer_t353.sh && bash tests/test_one_command_menu.sh
```

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `tests/test_pack_catalog.sh` | `install_both`: one Enter for the agent-ws question on Linux |
| `tasks/MINIMAL_LOG.md` | the Decision record |
