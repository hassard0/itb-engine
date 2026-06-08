"""LQG-vs-AS separation via forward-limit graviton positivity (v1.24).

With the corrected convex-hull RFC (so the stack is not RFC-saturated), sweep
the forward-dispersion ratio c in g_R2 >= c*g_R3 across its plausible range and
report, per framework: the graviton_forward_positivity margin, and full-stack
feasibility. Demonstrates that this single physically-derived constraint orders
the frameworks by their g_R2/g_R3 ratio — LQG (ratio 1.0) fails first, AS
(ratio 1.5) is the most robust survivor.
"""

import json
import sys

import numpy as np

from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
from itb.engine import check

sys.path.insert(0, ".")
from experiments.stack import CANONICAL, PLAUSIBLE_RANGES, build_stack, frameworks


def main():
    fws = frameworks()
    lo, hi = PLAUSIBLE_RANGES["graviton_fwd_c"]
    cs = np.linspace(lo, hi, 33)

    print("g_R2/g_R3 ratios (the quantity forward positivity orders by):")
    for fw in fws:
        t = fw.encode()
        r2, r3 = t.coefficients.get("g_R2", 0), t.coefficients.get("g_R3", 0)
        if fw.name != "pure_gr":
            print(f"  {fw.name:<20} g_R2/g_R3 = {r2/r3:.2f}")

    # standalone-constraint failure threshold per framework
    print("\nForward-positivity standalone: c at which each framework first fails:")
    thresholds = {}
    for fw in fws:
        if fw.name == "pure_gr":
            continue
        t = fw.encode()
        fail_c = None
        for c in cs:
            if not GravitonForwardPositivity(c=c).evaluate(t).satisfied:
                fail_c = float(c)
                break
        thresholds[fw.name] = fail_c
        print(f"  {fw.name:<20} fails at c >= {fail_c}")

    # full-stack feasibility across the sweep (corrected RFC)
    print("\nFull-stack feasibility vs c (corrected convex-hull RFC, others canonical):")
    rows = {fw.name: [] for fw in fws if fw.name != "pure_gr"}
    for c in cs:
        pref = dict(CANONICAL)
        pref["graviton_fwd_c"] = float(c)
        constraints = build_stack(pref, rfc_form="convex_hull")
        for fw in fws:
            if fw.name == "pure_gr":
                continue
            rows[fw.name].append(check(fw.encode(), constraints).feasible)
    for name, feas in rows.items():
        states = "".join("o" if f else "." for f in feas)
        frac = float(np.mean(feas))
        print(f"  {name:<20} [{states}]  feasible_fraction={frac:.2f}")

    out = {
        "c_values": [float(c) for c in cs],
        "standalone_fail_thresholds": thresholds,
        "fullstack_feasible": {k: [bool(x) for x in v] for k, v in rows.items()},
    }
    with open("experiments/out_separation.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_separation.json")


if __name__ == "__main__":
    main()
