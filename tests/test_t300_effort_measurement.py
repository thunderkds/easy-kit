"""T300 - the effort-table trial is recorded in DDR-0010 and the verdict follows the rule.

  AC1 - docs/ddr/data/t300-effort-trial.json holds 12 records (6 tasks x 2 arms) and the prices per arm.
  AC2 - the DDR holds the per-trial table, the totals per arm and per Complexity level, the verdict,
        the known limits and what follows.
  AC3 - the DDR verdict equals the rule applied to the JSON: `keep` only if the total cost of arm B
        is lower than arm A and no task passed in A and failed in B.
  AC4 - every number in the DDR table equals the JSON; totals are recomputed here.
  AC5 - the DDR says the tables in PROJECT_SPEC.md and the template are unchanged.
Mutation controls run the same checks on a changed copy and expect them to report a problem.
"""
import copy
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "ddr", "data", "t300-effort-trial.json")
DDR = os.path.join(ROOT, "docs", "ddr", "0010-effort-table-measured-on-replayed-tasks.md")

TASKS = ["T152", "T164", "T104", "T292", "T252", "T042"]
ARM_MODEL = {"A": ("haiku", "sonnet"), "B": ("opus", "opus")}  # (C0, C1)


def _load():
    with open(DATA) as f:
        return json.load(f)


def _ddr():
    with open(DDR) as f:
        return f.read()


def verdict(trials):
    """The rule from the guide (AC3), applied to the records."""
    cost = {"A": 0.0, "B": 0.0}
    passed = {}
    for t in trials:
        cost[t["arm"]] += t["cost_usd"]
        passed[(t["task"], t["arm"])] = t["oracle_exit"] == 0
    lost = [k[0] for k, ok in passed.items() if k[1] == "A" and ok and not passed[(k[0], "B")]]
    return "keep" if cost["B"] < cost["A"] and not lost else "do not keep"


def check_data(data):
    errs = []
    trials = data["trials"]
    if len(trials) != 12:
        errs.append("need 12 records")
    if sorted({t["task"] for t in trials}) != sorted(TASKS):
        errs.append("task set differs")
    for t in trials:
        lvl = 0 if t["complexity"] == "C0" else 1
        if t["model"] != ARM_MODEL[t["arm"]][lvl] or t["effort"] != "low":
            errs.append("arm table mismatch " + t["task"] + t["arm"])
        p = data["prices_per_mtok"][t["model"]]
        if (t["price_in_per_mtok"], t["price_out_per_mtok"]) != (p["in"], p["out"]):
            errs.append("price mismatch " + t["task"] + t["arm"])
    return errs


def check_table(data, text):
    """Each trial has a DDR row with the same model, effort, cost and oracle result."""
    errs = []
    for t in data["trials"]:
        pat = (r"^\| %s \| %s \| %s \| %s \| %s \| \$%.6f \| (pass|fail) \|"
               % (t["task"], t["complexity"], t["arm"], t["model"], t["effort"], t["cost_usd"]))
        m = re.search(pat, text, re.M)
        if not m:
            errs.append("row missing or differs: %s %s" % (t["task"], t["arm"]))
        elif (m.group(1) == "pass") != (t["oracle_exit"] == 0):
            errs.append("oracle result differs: %s %s" % (t["task"], t["arm"]))
    return errs


def totals(data):
    out = {}
    for level in ("C0", "C1", "All"):
        a = sum(t["cost_usd"] for t in data["trials"] if t["arm"] == "A" and level in (t["complexity"], "All"))
        b = sum(t["cost_usd"] for t in data["trials"] if t["arm"] == "B" and level in (t["complexity"], "All"))
        out[level] = (a, b)
    return out


def check_totals(data, text):
    errs = []
    for level, (a, b) in totals(data).items():
        row = "| %s | $%.4f | $%.4f | %.2f |" % (level, a, b, b / a)
        if row not in text:
            errs.append("totals row missing: " + row)
    return errs


def check_verdict(data, text):
    m = re.search(r"^\*\*Verdict\*\*: (keep|do not keep)\b", text, re.M)
    if not m:
        return ["no verdict line"]
    return [] if m.group(1) == verdict(data["trials"]) else ["verdict differs from the rule"]


def test_data_file_has_12_records_and_prices():  # AC1
    assert check_data(_load()) == []


def test_ddr_table_matches_json():  # AC2, AC4
    assert check_table(_load(), _ddr()) == []


def test_ddr_totals_match_json():  # AC2, AC4
    assert check_totals(_load(), _ddr()) == []


def test_ddr_verdict_equals_the_rule():  # AC3
    assert check_verdict(_load(), _ddr()) == []


def test_ddr_states_limits_and_follow_up():  # AC2, AC5
    text = _ddr()
    for needle in ("one run per cell", "10-line floor", "advisor", "test_merge_gate_is_untouched",
                   "lib/timestamps.py", "PROJECT_SPEC.md", "unchanged"):
        assert needle in text, needle


def test_rule_on_real_data_is_do_not_keep():
    d = _load()["trials"]
    assert verdict(d) == "do not keep"
    a = {t["task"]: t["oracle_exit"] for t in d if t["arm"] == "A"}
    b = {t["task"]: t["oracle_exit"] for t in d if t["arm"] == "B"}
    assert a["T292"] == 0 and b["T292"] != 0          # lost pass
    assert a["T252"] != 0 and b["T252"] != 0          # both failed: not a lost pass


# --- mutation controls: change bytes, the check must report a problem --------------------------

def test_mutation_cost_change_turns_table_red():
    d = copy.deepcopy(_load())
    d["trials"][0]["cost_usd"] += 0.000001
    assert check_table(d, _ddr()) != []


def test_mutation_flipped_verdict_turns_verdict_red():
    text = _ddr()
    flipped = re.sub(r"^(\*\*Verdict\*\*: )do not keep", r"\1keep", text, flags=re.M)
    assert flipped != text
    assert check_verdict(_load(), flipped) != []


def test_mutation_cheaper_failing_arm_b_is_do_not_keep():
    d = copy.deepcopy(_load())
    for t in d["trials"]:
        if t["arm"] == "B":
            t["cost_usd"] = 0.0  # B cheaper than A everywhere
    assert verdict(d["trials"]) == "do not keep"  # T292 still lost
    for t in d["trials"]:
        if t["task"] == "T292" and t["arm"] == "B":
            t["oracle_exit"] = 0
    assert verdict(d["trials"]) == "keep"  # control: with no lost pass and lower cost, rule says keep
