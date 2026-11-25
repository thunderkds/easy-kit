"""T353 - lib/merge-settings.py: the agent-ws overlay and its narrow ownership rule.

The installer passes lib/agent-ws-hooks.json as a 4th argument only when the project opted in.
The kit then owns entries whose command names exactly "$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py:
it adds them once, keeps them on every run, and drops them when the overlay is not passed (turned
off) or when the script is missing. A hand-wired absolute path stays the user's.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE = os.path.join(ROOT, "lib", "merge-settings.py")
KIT = os.path.join(ROOT, ".claude", "settings.json")
OVERLAY = os.path.join(ROOT, "lib", "agent-ws-hooks.json")
OWNED = '"$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py'


def project(tmp_path, settings=None, script=True):
    root = tmp_path / "p"
    (root / ".claude" / "hooks").mkdir(parents=True)
    for event in json.load(open(KIT))["hooks"].values():
        for group in event:
            for hook in group["hooks"]:
                name = hook["command"].split(".claude/hooks/")[1].split()[0].strip('"')
                (root / ".claude" / "hooks" / name).write_text("#\n")
    if script:
        (root / "scripts").mkdir()
        (root / "scripts" / "agent_ws.py").write_text("#\n")
    (root / ".claude" / "settings.json").write_text(json.dumps(settings or {}, indent=2) + "\n")
    return root


def merge(root, overlay=True):
    args = [sys.executable, MERGE, KIT, str(root / ".claude" / "settings.json"), str(root)]
    if overlay:
        args.append(OVERLAY)
    return subprocess.run(args, capture_output=True, text=True)


def agent_ws_commands(root):
    hooks = json.load(open(root / ".claude" / "settings.json")).get("hooks", {})
    return sorted((event, h["command"]) for event, groups in hooks.items() for g in groups
                  for h in g["hooks"] if "agent_ws.py" in h["command"])


def test_overlay_file_names_the_three_hooks_in_the_owned_form():
    data = json.load(open(OVERLAY))
    found = sorted((e, h["command"]) for e, gs in data["hooks"].items() for g in gs for h in g["hooks"])
    assert found == [("SessionStart", f"python3 {OWNED} hook-env"),
                     ("WorktreeCreate", f"python3 {OWNED} hook-create"),
                     ("WorktreeRemove", f"python3 {OWNED} hook-remove")]
    assert set(data) == {"hooks"}  # no permissions or other keys ride along


def test_overlay_adds_the_entries_once_and_a_second_run_changes_nothing(tmp_path):
    root = project(tmp_path)
    assert merge(root).returncode == 0
    assert [e for e, _ in agent_ws_commands(root)] == ["SessionStart", "WorktreeCreate", "WorktreeRemove"]
    first = (root / ".claude" / "settings.json").read_bytes()
    assert merge(root).returncode == 0
    assert (root / ".claude" / "settings.json").read_bytes() == first


def test_without_the_overlay_the_owned_entries_are_dropped(tmp_path):  # turning it off
    root = project(tmp_path)
    merge(root)
    assert merge(root, overlay=False).returncode == 0
    assert agent_ws_commands(root) == []


def test_kit_session_start_hook_stays_beside_hook_env(tmp_path):
    root = project(tmp_path)
    merge(root)
    starts = json.load(open(root / ".claude" / "settings.json"))["hooks"]["SessionStart"]
    commands = [h["command"] for g in starts for h in g["hooks"]]
    assert any("session_start_resume_mark.py" in c for c in commands)
    assert any("agent_ws.py hook-env" in c for c in commands)


def test_a_hand_wired_absolute_path_stays_the_users(tmp_path):
    hand = {"hooks": {"WorktreeCreate": [{"hooks": [
        {"type": "command", "command": "python3 /home/u/easy-kit/scripts/agent_ws.py hook-create"}]}]}}
    root = project(tmp_path, hand)
    for overlay in (False, True):
        assert merge(root, overlay=overlay).returncode == 0
        assert ("WorktreeCreate", "python3 /home/u/easy-kit/scripts/agent_ws.py hook-create") \
            in agent_ws_commands(root)


def test_a_longer_path_that_only_starts_like_the_script_is_not_taken_over(tmp_path):
    other = {"hooks": {"WorktreeCreate": [{"hooks": [
        {"type": "command", "command": 'python3 "$CLAUDE_PROJECT_DIR"/scripts/agent_ws.py.bak hook-create'}]}]}}
    root = project(tmp_path, other)
    assert merge(root, overlay=False).returncode == 0
    assert len(agent_ws_commands(root)) == 1


def test_a_missing_script_drops_the_entries_so_worktree_creation_still_works(tmp_path):
    root = project(tmp_path, script=False)
    r = merge(root)
    assert r.returncode == 0 and "missing file" in r.stderr
    assert agent_ws_commands(root) == []


def test_three_arguments_still_work_and_a_bad_overlay_refuses(tmp_path):
    root = project(tmp_path)
    assert merge(root, overlay=False).returncode == 0
    bad = tmp_path / "bad.json"
    bad.write_text("[]")
    r = subprocess.run([sys.executable, MERGE, KIT, str(root / ".claude" / "settings.json"),
                        str(root), str(bad)], capture_output=True, text=True)
    assert r.returncode == 2
