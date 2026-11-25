# TASK_REVIEW — T206: a bare or extra-arg `stop_auto_verify.py --start` exits 2 with a usage line

> Sibling of `tasks/TASK_GUIDE_T206.md`. Filled by the reviewer at Stage 4/5.

---

## Demonstration

**BEFORE**: (captured 2026-11-25 05:29:01–05:29:08 UTC, before the first implementation commit; the red test was committed before the hook fix)

```
$ date -u
Wed Nov 25 05:29:01 UTC 2026
$ /tmp/claude-1000/-home-thunderkds-workspace-pets-hungnguyen111-easy-kit/a074ce56-6c68-4a4f-b8ca-c467af91efc9/scratchpad/venv/bin/python3 -m pytest .claude/hooks/tests/test_t206_start_usage.py -q -p no:cacheprovider
FFF.                                                                     [100%]
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_bare_start_exits_2_with_usage
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_start_with_two_args_exits_2_with_usage
FAILED .claude/hooks/tests/test_t206_start_usage.py::test_start_with_three_args_exits_2_with_usage
3 failed, 1 passed in 0.17s
$ date -u
Wed Nov 25 05:29:08 UTC 2026
```

Failing assertion: `assert 0 == 2` (bare `--start` and extra-arg forms return 0 with no usage line; they fall through to `stop_hook()` when the child guard is absent).

**AFTER**: [to be filled after the fix]

**DELTA**: [to be filled after the fix]
