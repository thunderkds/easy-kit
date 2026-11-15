#!/usr/bin/env python3
"""
PostToolUse recorder (T314) — fires after every Edit, Write and Bash tool call.

In board mode `online` with an active task, it records each sensitive path the call
touched in `.claude/state/sensitive-approvals.json` as `{"<task_id>": ["<path>", ...]}`.
A PostToolUse event means the call ran, so for a call that
`pre_tool_sensitive_path.py` asked about, the user said yes: that yes is the only
trust source (NFR-005 stays — board text approves nothing). The PreToolUse hook then
stays silent on later calls in the same task that touch only approved paths.

Path parsing is the PreToolUse hook's own code (imported, not copied), so both
hooks agree on what a call touches. The approval file itself is never recorded.

Never breaks the session: local mode, no active task, or any error -> exit 0, no output.
"""
import json
import os
import sys


def record(event):
    hooks_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, hooks_dir)
    import pre_tool_sensitive_path as hook  # exits 0 itself outside a kit project

    if hook.IMPORT_ERROR is not None:
        return
    tool_name = event["tool_name"]
    tool_input = event["tool_input"]
    if tool_name not in ("Edit", "Write", "Bash") or not isinstance(tool_input, dict):
        return

    root = hook.project_dir()
    cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else None
    cwd = cwd or os.getcwd()
    roots = [root, cwd]
    if not hook.is_online(roots):
        return
    task_id = hook.resolve_task_id(event)
    if not task_id:
        return

    patterns = hook.load_patterns(hook.pattern_file_path(root))
    new = [key
           for _, forms, pattern in hook.sensitive_hits(tool_name, tool_input, cwd, roots, patterns)
           if pattern != hook.APPROVALS_RELPATH
           for key in hook.approval_keys(forms)]
    if not new:
        return

    data = hook.read_approvals(root)
    approved = data.setdefault(task_id, [])
    added = [key for key in dict.fromkeys(new) if key not in approved]
    if not added:
        return
    approved.extend(added)

    path = hook.approvals_file(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def main():
    try:
        record(json.load(sys.stdin))
    except BaseException:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
