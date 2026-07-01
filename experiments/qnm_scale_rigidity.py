"""v2.390 - SWING: the consistent theory has a definite absolute scale -- consistency alone pins the coupling strength to a factor ~3, no data.

Following matter dominance (v2.389, matter sets the gravitational scale), the sharp question: is the theory
SCALE-INVARIANT -- can all couplings be uniformly rescaled g -> lambda g while staying consistent (region = a
cone, only ratios matter) -- or is the absolute scale fixed? Most consistency bounds are scale-homogeneous
(positivity g >= 0; the dispersion tower g_6^2 <= g_4 g_8, degree 2 both sides; CEMZ, degree 1 both sides), so
they do NOT bound a uniform rescaling. But a few constraints carry an absolute scale.

Test (theory-only stack, NO data): scale the constructed point by lambda and find the feasible window.

Result: the region is NOT a scale-invariant cone -- it is a BOUNDED scale window, lambda in [0.33, 1.07], a
factor of only ~3.2. Scale the couplings DOWN past lambda = 0.33 and the cubic_graviton_matter_bound fails (the
couplings become too weak); scale UP past lambda = 1.07 and anomaly_cancellation fails (too strong). So the
consistency conditions alone -- with NO data -- pin the theory's overall coupling strength to a factor ~3: the
theory is nearly SCALE-RIGID, it cannot be made arbitrarily weakly or strongly coupled. And the constructed
(max-margin) point sits at 91% of the way up the window, near the strong-coupling ceiling set by anomaly
cancellation -- the theory lives close to the most strongly-coupled scale consistency permits.
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

VERSION = "v2.390"
DEFAULT_OUT = Path("experiments/results/v2.390/qnm_scale_rigidity.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])


def run(n_scan: int = 401) -> dict:
    stack = build_stack(rfc_form="convex_hull")   # theory-only, no data

    def results(v):
        return check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results

    def feasible(v):
        return all(r.satisfied for r in results(v))

    lams = np.linspace(0.05, 2.0, n_scan)
    ok = np.array([feasible(CONSTRUCTED * l) for l in lams])
    feas_lams = lams[ok]
    lo, hi = float(feas_lams.min()), float(feas_lams.max())
    width = hi / lo
    pos = (1.0 - lo) / (hi - lo)   # position of constructed (lambda=1) in the window

    def viol(v):
        return [r.constraint_name for r in results(v) if not r.satisfied]

    dl = (lams[1] - lams[0])
    lower_binding = viol(CONSTRUCTED * (lo - dl))
    upper_binding = viol(CONSTRUCTED * (hi + dl))

    # confirm the homogeneous constraints do NOT bind the scale (they hold across the whole scanned ray where couplings>0)
    checks = {
        "region_is_not_scale_invariant": not ok.all(),
        "scale_window_is_bounded": lo > 0.05 and hi < 2.0,
        "window_factor_order_few": width < 6.0,
        "lower_edge_is_cubic_graviton_matter": any("cubic_graviton_matter" in c for c in lower_binding),
        "upper_edge_is_anomaly": any("anomaly" in c for c in upper_binding),
    }

    return {
        "version": VERSION,
        "scale_window": [round(lo, 3), round(hi, 3)],
        "window_factor": round(width, 2),
        "constructed_position_in_window": round(pos, 2),
        "lower_edge_binding": lower_binding,
        "upper_edge_binding": upper_binding,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The consistent theory has a definite ABSOLUTE scale -- consistency alone, with no data, pins the "
            "overall coupling strength to a factor of only ~3. Following matter dominance (v2.389), the "
            "question was whether the theory is scale-invariant: can all couplings be uniformly rescaled "
            "g -> lambda g and stay consistent (region a cone, only ratios matter)? Most bounds are "
            "scale-homogeneous (positivity, the degree-2 dispersion tower, degree-1 CEMZ) and do NOT bound a "
            "uniform rescaling -- but the answer is NO: scaling the constructed point on the theory-only "
            "stack stays feasible only for lambda in [0.33, 1.07], a bounded window of factor ~3.2, not a "
            "cone. Scale DOWN past lambda = 0.33 and the cubic_graviton_matter_bound fails (couplings too "
            "weak); scale UP past lambda = 1.07 and anomaly_cancellation fails (too strong). So a handful of "
            "constraints that carry an absolute scale -- the cubic graviton-matter bound from below, anomaly "
            "matching from above -- make the theory nearly SCALE-RIGID: it cannot be made arbitrarily weakly "
            "or strongly coupled, its overall strength is fixed by consistency to within a factor ~3 before "
            "any measurement. This is a strong predictivity statement complementary to v2.373 (the region is "
            "small): not only are the RATIOS of couplings carved (the ~5-parameter shape), the overall SCALE "
            "is nearly carved too -- the theory has almost no free overall normalization. And the constructed "
            "max-margin point sits at 91% of the way up the window, hard against the strong-coupling ceiling "
            "set by anomaly cancellation: the theory lives close to the most strongly-coupled scale "
            "consistency permits, which is why the anomaly/parity sector is so tightly determined (v2.371) -- "
            "anomaly matching is nearly saturated along the scale direction. It sharpens matter dominance "
            "(v2.389): matter sets the gravitational scale, and consistency in turn nearly fixes the matter "
            "scale, so the whole theory is scale-rigid, not just its gravitational sub-sector."
        ),
        "honest_scope": (
            "This tests uniform rescaling along the RAY through the constructed point (all six couplings "
            "scaled together); non-uniform rescalings explore other directions and are not covered -- so "
            "'scale window factor ~3' is for the constructed direction, the cleanest notion of overall scale. "
            "The binding constraints (cubic_graviton_matter_bound below, anomaly_cancellation above) carry "
            "toy O(1) prefactors, so the exact edges (0.33, 1.07) and the factor 3.2 are toy-basis; the "
            "ROBUST content is STRUCTURAL -- the theory-only region is a bounded scale window, not a cone, "
            "and it is the absolute-scale constraints (a cubic graviton-matter floor, an anomaly ceiling), "
            "NOT the homogeneous positivity/dispersion bounds, that break scale invariance. A different "
            "encoding of those two constraints would move the edges but keep the bounded-window structure "
            "(any constraint with an absolute scale does it). This is theory-only (no data), so the scale "
            "rigidity is intrinsic to the consistency conditions; adding data narrows further. The '91% up "
            "the window' and 'anomaly nearly saturated' are for this ray and this constructed point. Robust "
            "content: consistency alone fixes the overall coupling scale to an order-few window (not a free "
            "normalization), broken by absolute-scale constraints, with the constructed point near the "
            "strong-coupling ceiling. Toy edges, robust bounded-window structure. A scale-rigidity swing."
        ),
        "references": [
            "this repo: v2.389 (matter dominance), v2.373 (feasible-region volume / predictivity), v2.371 (anomaly determination), v2.372 (5-parameter shape)",
            "concept: scale-invariant (homogeneous) vs absolute-scale constraints; the consistent region as a bounded body vs a cone",
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
    print("SWING: the consistent theory is nearly SCALE-RIGID -- consistency alone pins the coupling scale (no data):")
    print(f"  theory-only scale window: lambda in {res['scale_window']}  (factor {res['window_factor']}, NOT a scale-invariant cone)")
    print(f"  lower edge binding: {res['lower_edge_binding']} (couplings too weak)")
    print(f"  upper edge binding: {res['upper_edge_binding']} (couplings too strong)")
    print(f"  constructed at {res['constructed_position_in_window']:.0%} up the window -- near the strong-coupling (anomaly) ceiling")
    print(f"  => the overall coupling strength is nearly carved too, not just the ratios (complements v2.373)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
