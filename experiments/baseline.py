"""Baseline: reproduce the full-stack intersection + per-framework status.

Confirms the realism stack reproduces the documented v1.20 result before any
prefactor is changed. Run on Vulcan.
"""

import json
import sys

from itb.engine import check
from itb.intersection_search import search_intersection

sys.path.insert(0, ".")
from experiments.stack import build_stack, frameworks, INTERSECTION_INITIAL


def main() -> None:
    constraints = build_stack()
    fws = frameworks()
    print(f"Full stack: {len(constraints)} constraints, {len(fws)} frameworks\n")

    framework_status = {}
    for fw in fws:
        report = check(fw.encode(), constraints)
        framework_status[fw.name] = {
            "feasible": report.feasible,
            "binding": report.binding,
            "binding_class": report.binding_class,
        }
        print(f"  {fw.name:<22} feasible={str(report.feasible):<5} "
              f"binding={report.binding or '—'}")

    print("\nIntersection search (Nelder-Mead, 2000 iters)...")
    res = search_intersection(constraints, INTERSECTION_INITIAL, max_iters=2000)
    print(f"  feasible:          {res.feasible}")
    print(f"  worst-case margin: {res.worst_case_margin:.6f}")
    if res.feasible:
        for k, v in sorted(res.coefficients.items()):
            print(f"    {k}: {v:.4f}")

    out = {
        "n_constraints": len(constraints),
        "framework_status": framework_status,
        "intersection": {
            "feasible": res.feasible,
            "worst_case_margin": res.worst_case_margin,
            "coefficients": res.coefficients,
            "constraints_violated": res.constraints_violated,
        },
    }
    with open("experiments/out_baseline.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_baseline.json")


if __name__ == "__main__":
    main()
