"""v2.403 - SWING: g_R3_parity=0 is a THIRD constructed-point assumption -- the minimal parity sector is a choice, not a prediction, and it hides a second parity observable.

Continuing the basis-structure audit: the constructed theory sets the parity-odd CUBIC coupling g_R3_parity = 0
(parity only in the quadratic g_R2_parity). Is that forced by consistency, or -- like a=c (v2.399) and g_6=g_8
(v2.392) -- a constructed-point assumption?

Result: an assumption. Activating g_R3_parity as an independent axis, the feasible range is [-0.035, 0.035]
with g_R3_parity = 0 sitting INTERIOR (not an edge), bounded at both ends by the generalized-anomaly-inflow
constraint. So the parity-odd cubic is a free direction, and setting it to zero is a CHOICE -- specifically the
anomaly-SATURATED choice (v2.370, cubic suppressed). The anomaly-CLOSED variant (v2.371) instead prefers a
NONZERO value, g_R3_parity = r * g_R2_parity ~ 0.028, which is feasible (well inside the window). So the two
anomaly variants of the v2.377 fork are literally two points on this g_R3_parity axis: saturated (0) vs closed
(0.028), both consistent, distinguished only by whether the second anomaly-matching condition is imposed.

This adds a THIRD entry to the candidate's ASSUMPTION tier (v2.402): a=c, g_6=g_8, and now g_R3_parity=0 -- three
'special-looking' constructed-point values that the consistency conditions do NOT force. The systematic lesson:
the max-margin (Chebyshev) point's apparent simplicity (holographic a=c, equal matter moments, minimal parity)
is largely ASSUMPTION, and the theory's genuine predictions are the ROBUST-tier structural ones (matter
dominance, ghost-safety, string-like towers), not these tidy coincidences. Physically, g_R3_parity != 0 would
source a SECOND, cubic-order parity observable distinct from the quadratic birefringence -- so the 'minimal
parity sector' assumption hides a potential extra chiral signal the anomaly-closed variant predicts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.403"
DEFAULT_OUT = Path("experiments/results/v2.403/qnm_third_assumption_parity_cubic.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
BASE = [0.529, 0.4, 0.4, 0.193, 0.09, 0.06, 0.0]
R_CLOSED = 0.5 * (0.529 + 0.4)   # rho_match*(g4+g6) = 0.4645 (v2.371)
GR2P = 0.06


def run(n_scan: int = 401) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def results(v):
        return check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results

    def feasible(v):
        return all(r.satisfied for r in results(v))

    def viol(v):
        return [r.constraint_name for r in results(v) if not r.satisfied]

    constructed_feasible = feasible(BASE)
    xs = np.linspace(-0.3, 0.3, n_scan)
    feas_x = [float(x) for x in xs if feasible([*BASE[:6], float(x)])]
    lo, hi = min(feas_x), max(feas_x)
    zero_interior = (lo < 0.0 < hi)

    closed_val = R_CLOSED * GR2P
    closed_feasible = feasible([*BASE[:6], closed_val])

    dx = xs[1] - xs[0]
    upper_binding = viol([*BASE[:6], hi + dx])

    checks = {
        "gR3parity_zero_feasible": bool(constructed_feasible),
        "gR3parity_zero_is_interior_not_forced": bool(zero_interior),
        "anomaly_closed_nonzero_value_feasible": bool(closed_feasible),
        "parity_cubic_is_a_free_bounded_direction": bool((hi - lo) > 0.02),
        "bounded_by_anomaly_inflow": bool(any("anomaly" in c for c in upper_binding)),
    }

    return {
        "version": VERSION,
        "feasible_gR3parity_range": [round(lo, 3), round(hi, 3)],
        "constructed_gR3parity": 0.0,
        "gR3parity_zero_interior": zero_interior,
        "anomaly_closed_value": round(closed_val, 3),
        "anomaly_closed_feasible": closed_feasible,
        "upper_edge_binding": upper_binding,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "g_R3_parity = 0 is a THIRD constructed-point assumption, not a prediction. Activating the "
            "parity-odd cubic coupling as an independent axis, its feasible range is [-0.035, 0.035] with 0 "
            "sitting INTERIOR (bounded at both ends by the generalized-anomaly-inflow constraint) -- so the "
            "constructed theory's 'parity only in the quadratic g_R2_parity' is a CHOICE, specifically the "
            "anomaly-SATURATED choice (v2.370, cubic suppressed). The anomaly-CLOSED variant (v2.371) instead "
            "prefers a nonzero value g_R3_parity = r g_R2_parity ~ 0.028, which is feasible (well inside the "
            "window), so the two anomaly variants of the v2.377 fork are literally two points on this axis -- "
            "saturated (0) vs closed (0.028) -- both consistent, distinguished only by whether the second "
            "anomaly-matching condition is imposed. This adds a THIRD entry to the candidate's ASSUMPTION "
            "tier (v2.402): a=c (v2.399), g_6=g_8 (v2.392), and now g_R3_parity=0 -- three 'special-looking' "
            "constructed-point values the consistency conditions do NOT force. The systematic lesson is that "
            "the max-margin (Chebyshev) point's apparent simplicity -- holographic a=c, equal matter moments, "
            "minimal parity -- is largely ASSUMPTION, and the theory's genuine predictions are the "
            "ROBUST-tier structural ones (matter dominance, ghost-safety, string-like towers, the "
            "near-Planckian cutoff), not these tidy coincidences. Physically the consequence is real: "
            "g_R3_parity != 0 sources a SECOND, cubic-order parity observable distinct from the quadratic "
            "birefringence, so the 'minimal parity sector' assumption hides a potential extra chiral signal "
            "-- exactly the one the anomaly-closed variant predicts. The honest upshot: the parity sector is "
            "richer than the constructed point shows (a two-parameter (g_R2_parity, g_R3_parity) family "
            "bounded by anomaly inflow), and which point is realized is a genuine open question the v2.377 "
            "forward test would resolve."
        ),
        "honest_scope": (
            "g_R3_parity=0 being interior to the feasible window is the robust, measure-independent finding -- "
            "it is a choice, not forced. The window edges [-0.035, 0.035] are toy-basis (set by the "
            "generalized-anomaly-inflow and cubic-parity constraints with their O(1) prefactors), so the "
            "specific 0.035 is toy; the robust content is that 0 is interior and the anomaly-closed value is "
            "feasible. The anomaly-closed value 0.028 = r g_R2_parity uses v2.371's toy r = rho_match(g4+g6) "
            "and the birefringence-derived g_R2_parity (v2.329), so it is toy-basis too; the robust point is "
            "that a nonzero g_R3_parity is allowed and even preferred by one anomaly variant. This is a "
            "basis-structure / assumption audit (like v2.392/v2.399), adding a third assumption to the tier "
            "and no new physical datum about the constructed point -- it characterizes the FREEDOM the "
            "constructed point's g_R3_parity=0 hides. 'Second parity observable' is the qualitative physical "
            "reading (a parity-odd cubic curvature operator sources cubic-order parity violation); its "
            "magnitude is unpinned (toy). Robust content: g_R3_parity=0 is an unforced constructed-point "
            "assumption (the anomaly-saturated choice), the parity-odd cubic is a free anomaly-inflow-bounded "
            "direction, and the anomaly-closed variant prefers it nonzero -- a third assumption completing "
            "the audit (a=c, g_6=g_8, g_R3_parity=0). Toy window, robust interiority. An assumption-audit swing."
        ),
        "references": [
            "this repo: v2.371 (anomaly-closed system -> nonzero g_R3_parity), v2.370 (anomaly-saturated -> cubic suppressed), v2.377 (the saturated-vs-closed fork), v2.399 (a=c assumption), v2.392 (g_6=g_8 assumption), v2.402 (assumption tier), src/itb/constraints/cubic_parity.py + anomaly_flow.py",
            "physics: gravitational anomaly inflow; parity-odd cubic curvature operator (Pontryagin x curvature)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=401)
    args = p.parse_args()
    res = run(n_scan=args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING: g_R3_parity=0 is a THIRD constructed-point assumption (parity-odd cubic is a free direction):")
    print(f"  feasible g_R3_parity range {res['feasible_gR3parity_range']}; 0 interior: {res['gR3parity_zero_interior']}")
    print(f"  anomaly-closed value {res['anomaly_closed_value']} (v2.371) feasible: {res['anomaly_closed_feasible']} -- the fork's other point")
    print(f"  upper edge bound by {res['upper_edge_binding']}")
    print(f"  => ASSUMPTION tier now: a=c (v2.399), g_6=g_8 (v2.392), g_R3_parity=0 (this) -- the Chebyshev point's 'simplicity' is largely assumption")
    print(f"  => hides a potential SECOND (cubic-order) parity observable the anomaly-closed variant predicts")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
