"""
T305 — a repo with both the setup.sh install and the plugin runs each gate once.

Runs each command of hooks/hooks.json with `sh -c`, a temp project and a stub plugin root.
"""
import json
import os
import re
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_FILES = (os.path.join(ROOT, "hooks", "hooks.json"), os.path.join(ROOT, "plugin", "hooks", "hooks.json"))
SCRIPT = re.compile(r"/\.claude/hooks/([\w.-]+\.py)")
# The command form setup.sh writes into .claude/settings.json.
SETUP_FORM = 'python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/%s'


def commands(path=HOOK_FILES[0]):
    with open(path) as f:
        doc = json.load(f)
    return [h["command"] for groups in doc["hooks"].values() for g in groups for h in g["hooks"]]


def script_of(command):
    return SCRIPT.search(command).group(1)


ALL = [(c, script_of(c)) for c in commands()]


def make_stub(plugin_root, script, exit_code=0):
    hooks = plugin_root / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / script).write_text(
        "import os, sys\n"
        "data = sys.stdin.read()\n"
        "open(os.path.join(os.path.dirname(__file__), %r), 'w').write(data)\n"
        "print('stub-out:' + data)\n"
        "sys.exit(%d)\n" % (script + ".marker", exit_code)
    )
    return hooks / (script + ".marker")


def wire(project, *scripts, permission_only=False):
    (project / ".claude").mkdir(parents=True, exist_ok=True)
    if permission_only:
        doc = {"permissions": {"allow": ["Bash(python3 .claude/hooks/%s:*)" % s for s in scripts]}}
    else:
        doc = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": SETUP_FORM % s}
                                             for s in scripts]}]}}
    (project / ".claude" / "settings.json").write_text(json.dumps(doc, indent=2))


def run(command, project, plugin_root, stdin="{}"):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT")}
    env["CLAUDE_PROJECT_DIR"] = str(project)
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    return subprocess.run(["sh", "-c", command], input=stdin, capture_output=True, text=True,
                          env=env, timeout=30)


@pytest.fixture
def dirs(tmp_path):
    project = tmp_path / "my project"  # a space: quoting must hold
    project.mkdir()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    return project, plugin


@pytest.mark.parametrize("command,script", ALL)
def test_ac1_wired_in_settings_skips_the_plugin_hook(dirs, command, script):
    project, plugin = dirs
    marker = make_stub(plugin, script)
    wire(project, script)
    result = run(command, project, plugin)
    assert result.returncode == 0 and result.stdout == "" and result.stderr == ""
    assert not marker.exists()


@pytest.mark.parametrize("command,script", ALL)
def test_ac2_no_settings_runs_the_plugin_hook_unchanged(dirs, command, script):
    project, plugin = dirs
    marker = make_stub(plugin, script, exit_code=2)
    result = run(command, project, plugin, stdin='{"x": 1}')
    assert result.returncode == 2
    assert result.stdout == 'stub-out:{"x": 1}\n'
    assert marker.read_text() == '{"x": 1}'  # AC6: the stub received the event JSON


@pytest.mark.parametrize("command,script", ALL)
def test_ac3_permission_rule_only_does_not_skip(dirs, command, script):
    project, plugin = dirs
    marker = make_stub(plugin, script)
    wire(project, script, permission_only=True)
    assert run(command, project, plugin).returncode == 0
    assert marker.exists()


@pytest.mark.parametrize("command,script", ALL)
def test_ac4_init_copy_without_wiring_does_not_skip(dirs, command, script):
    project, plugin = dirs
    marker = make_stub(plugin, script)
    (project / ".claude" / "hooks").mkdir(parents=True)
    (project / ".claude" / "hooks" / script).write_text("raise SystemExit(0)\n")
    (project / ".claude" / "settings.json").write_text("{}")
    assert run(command, project, plugin).returncode == 0
    assert marker.exists()


def test_ac5_skip_is_per_script(dirs):
    project, plugin = dirs
    (a, sa), (b, sb) = ALL[0], ALL[1]
    ma, mb = make_stub(plugin, sa), make_stub(plugin, sb)
    wire(project, sa)
    run(a, project, plugin)
    run(b, project, plugin)
    assert not ma.exists() and mb.exists()


def test_a_script_name_that_prefixes_another_does_not_match(dirs):
    project, plugin = dirs
    command, script = ALL[0]
    marker = make_stub(plugin, script)
    wire(project, script[:-3] + "_longer.py")
    run(command, project, plugin)
    assert marker.exists()


def test_unset_project_dir_falls_through_to_the_script(dirs):
    project, plugin = dirs
    command, script = ALL[0]
    marker = make_stub(plugin, script)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin)
    subprocess.run(["sh", "-c", command], input="{}", capture_output=True, text=True, env=env, timeout=30)
    assert marker.exists()


def test_mutant_without_the_guard_fails_case_1(dirs):
    project, plugin = dirs
    command, script = ALL[0]
    unguarded = 'python3 "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/%s"' % script
    marker = make_stub(plugin, script)
    wire(project, script)
    run(unguarded, project, plugin)
    assert marker.exists()  # the unguarded command runs although settings wire it


def test_ac6_both_hook_files_are_identical():
    assert commands(HOOK_FILES[0]) == commands(HOOK_FILES[1])
    with open(HOOK_FILES[0]) as a, open(HOOK_FILES[1]) as b:
        assert a.read() == b.read()
