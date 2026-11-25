#!/usr/bin/env python3
"""T327 - clean up what a task left after it is Done and merged into `main`.

    python3 scripts/cleanup_task.py <ID>      (run from the main checkout)

Removes the task's linked worktree (with its build and test output), deletes its merged branch, and
checks for processes whose working directory is inside that worktree. It sends no signal: it lists
them and refuses while any runs, so you stop them and run again. It also refuses, and
removes nothing, when the board row is not in Done, the branch is not merged into `main`, or the
worktree holds uncommitted or untracked files. It never forces a removal, never deletes an
unmerged branch, never runs git clean. A second run finds nothing left and exits 0.

Exit 0: cleaned, or already clean. Exit 1: refused or failed. One line per action on stdout.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                ".claude", "hooks", "lib"))
import auto_mode as am  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def say(text):
    print(text, flush=True)


def refuse(text):
    say(f"refused: {text}")
    return 1


def linked_worktree(top):
    done = git(top, "rev-parse", "--git-dir", "--git-common-dir")
    lines = done.stdout.splitlines() if done.returncode == 0 else []
    if len(lines) != 2:
        return False
    a, b = (os.path.realpath(os.path.join(top, l.strip())) for l in lines)
    return a != b


def worktrees(root):
    """[(path, branch or None)] for every linked worktree (main checkout excluded)."""
    out, path, branch = [], None, None
    text = git(root, "worktree", "list", "--porcelain").stdout + "\n"
    for line in text.splitlines():
        if line.startswith("worktree "):
            path, branch = line[len("worktree "):], None
        elif line.startswith("branch refs/heads/"):
            branch = line[len("branch refs/heads/"):]
        elif not line.strip() and path:
            if os.path.realpath(path) != os.path.realpath(root):
                out.append((path, branch))
            path = None
    return out


def local_branches(root):
    return git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()


def pick_branch(task_id, row, root, trees):
    """(branch, error). The row's branch; else the one branch naming the task; none -> (None, None)."""
    named = am.row_branch(row)
    if named:
        return named, None
    found = {b for _, b in trees if am.names_task(b, task_id)}
    found |= {b for b in local_branches(root) if am.names_task(b, task_id)}
    if len(found) > 1:
        return None, f"several branches name {task_id}: {', '.join(sorted(found))}"
    return (found.pop() if found else None), None


def ancestors():
    """PIDs of this process and its parents (a shell inside the worktree may start the script)."""
    out, pid = set(), os.getpid()
    while pid > 1 and pid not in out:
        out.add(pid)
        try:
            with open(f"/proc/{pid}/stat") as f:
                pid = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    return out


def processes_in(path):
    """([(pid, command)], unreadable count) for live processes whose cwd is inside `path`;
    None when /proc is not there."""
    if not os.path.isdir("/proc/self"):
        return None
    base = os.path.realpath(path)
    skip = ancestors()
    found, unreadable = [], 0
    for name in os.listdir("/proc"):
        if not name.isdigit() or int(name) in skip:
            continue
        try:
            cwd = os.path.realpath(os.readlink(f"/proc/{name}/cwd"))
        except OSError:
            unreadable += 1
            continue
        if cwd == base or cwd.startswith(base + os.sep):
            try:
                with open(f"/proc/{name}/cmdline", "rb") as f:
                    cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
            except OSError:
                cmd = ""
            found.append((int(name), cmd or "?"))
    return found, unreadable


def running_in(path):
    """Print one line per process inside the worktree; return how many. No signal is ever sent."""
    got = processes_in(path)
    if got is None:
        say("no /proc on this OS: process check skipped")
        return 0
    procs, unreadable = got
    for pid, cmd in procs:
        say(f"running process {pid} (cwd inside the worktree): {cmd}")
    if unreadable:
        say(f"{unreadable} /proc entries could not be read and were skipped")
    return len(procs)


def main(argv):
    if len(argv) != 2 or not re.fullmatch(r"T\d+", argv[1]):
        return refuse("usage: cleanup_task.py T<number>")
    task_id = argv[1]
    top = git(os.getcwd(), "rev-parse", "--show-toplevel").stdout.strip()
    if not top:
        return refuse("not inside a git repository")
    if linked_worktree(top):
        say("this checkout is a linked worktree; run cleanup from the main checkout: nothing removed")
        return 0
    root = top
    main_branch = am.default_branch()  # T370: the setting `EASY_KIT_DEFAULT_BRANCH`, default `main`
    if main_branch is None:
        return refuse(f"`{am.DEFAULT_BRANCH_ENV}` is not a plain branch name: nothing removed")

    try:
        kanban = am.read(os.path.join(root, "PROJECT_KANBAN.md"), root)
    except am.Unreadable as exc:
        return refuse(str(exc))
    row = next((r for t, r in am.board_rows(kanban, ("Done",)) if t == task_id), None)
    if row is None:
        return refuse(f"{task_id} is not in Done on PROJECT_KANBAN.md")

    trees = worktrees(root)
    branch, err = pick_branch(task_id, row, root, trees)
    if err:
        return refuse(err)
    exists = branch in local_branches(root) if branch else False
    wt = next((p for p, b in trees if branch and b == branch), None)
    if branch in (main_branch, git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()):
        return refuse(f"branch {branch} is the main checkout's branch")
    if not exists and not wt:
        say(f"{task_id}: already clean (no worktree, no branch)")
        return 0

    if exists and git(root, "merge-base", "--is-ancestor", branch, f"refs/heads/{main_branch}").returncode != 0:
        return refuse(f"branch {branch} is not merged into {main_branch}")
    if wt and not os.path.isdir(wt):
        return refuse(f"worktree folder {wt} is missing; run `git worktree prune`, then run again")
    if wt:
        dirty = git(wt, "status", "--porcelain").stdout.strip()
        if dirty:
            return refuse(f"worktree {wt} has uncommitted or untracked files:\n{dirty}")
        if running_in(wt):
            return refuse("processes still run inside the worktree; stop them, then run again. "
                          "Nothing removed")
        done = git(root, "worktree", "remove", wt)
        if done.returncode != 0:
            return refuse(f"git worktree remove failed: {done.stderr.strip()}")
        say(f"removed worktree {wt}")
    else:
        say(f"worktree for {branch}: already clean")
    if exists:
        done = git(root, "branch", "-d", branch)
        if done.returncode != 0:
            return refuse(f"git branch -d failed: {done.stderr.strip()}")
        say(f"deleted branch {branch}")
    else:
        say(f"branch {branch}: already clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
