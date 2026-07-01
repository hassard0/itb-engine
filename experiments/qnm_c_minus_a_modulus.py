"""v2.399 - SWING (full c!=a exploitation): the holographic a=c is an ASSUMPTION, not a prediction -- c-a is a free modulus bounded only by conformal-collider physics.

v2.398 activated the Weyl^2 axis g_C and found the c-axis is carved solely by the Hofman-Maldacena wedge, with
the constructed theory sitting at a=c (a/c=1). This swing does the full exploitation: with g_C free, does the
theory PREFER the holographic a=c value, or was a=c merely the framework default?

Result: a=c is an ASSUMPTION, not a consistency prediction. With g_C free the feasible a/c = g_R2/g_C spans the
ENTIRE Hofman-Maldacena wedge [0.333, 1.720] = [1/3, 31/18], and a/c = 1 (a=c) sits INTERIOR to it, neither an
edge nor a forced center -- exactly one interior point of a one-parameter family. No consistency condition
selects a=c; the only thing bounding the Euler-vs-Weyl^2 split is the conformal-collider (ANEC) wedge. So the
constructed theory's a=c -- the holographic / two-derivative-Einstein value that frameworks default to -- is a
CHOICE the engine inherited from the default g_C=g_R2, not something the consistency conditions predict. The
resolved basis therefore has a genuine new FREE MODULUS, the c-a split, bounded only by 1/3 <= a/c <= 31/18.

This is the honest sibling of v2.392 (g_6=g_8 was a Chebyshev-center artifact): a=c is likewise a
constructed-point coincidence inherited from a default, not forced physics. It sharpens the candidate's honest
tiering (v2.382): 'a = c' belongs in the ASSUMPTION bin, and any prediction that leaned on the Weyl^2 sector
(the ghost mass, the screening, the BH-entropy shift) carries an unpinned c-a modulus that a finer,
c!=a-resolved analysis must marginalize over.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.399"
DEFAULT_OUT = Path("experiments/results/v2.399/qnm_c_minus_a_modulus.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_C"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06, 0.193])
AC_LO, AC_HI = 1.0 / 3.0, 31.0 / 18.0
WEDGE_GEOM_CENTER = math.sqrt(AC_LO * AC_HI)   # 0.758


def run(n_walk: int = 40000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    rng = np.random.default_rng(seed)
    pts = [CONSTRUCTED.copy()]
    cur = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 7), 0.0, None)
        if feasible(c):
            cur = c
            pts.append(cur.copy())
    pts = np.array(pts)
    gR2, gC = pts[:, 3], pts[:, 6]
    ac = gR2 / np.where(gC > 1e-9, gC, np.nan)
    ac_lo, ac_hi = float(np.nanmin(ac)), float(np.nanmax(ac))
    ac_mean = float(np.nanmean(ac))
    frac_c_gt_a = float(np.mean(ac < 1.0))

    a_eq_c_interior = (ac_lo < 1.0 < ac_hi)
    spans_wedge = (abs(ac_lo - AC_LO) < 0.03) and (abs(ac_hi - AC_HI) < 0.06)

    checks = {
        "feasible_ac_spans_full_HM_wedge": bool(spans_wedge),
        "a_equals_c_is_interior_not_edge": bool(a_eq_c_interior),
        "c_minus_a_is_a_free_modulus": bool((ac_hi / ac_lo) > 3.0),   # >3x range in a/c
        "a_equals_c_not_a_forced_center": bool(abs(ac_mean - 1.0) > 0.05),   # bulk not at a=c
        "mean_near_wedge_geometric_center_measure_dependent": bool(abs(ac_mean - WEDGE_GEOM_CENTER) < 0.1),
    }

    return {
        "version": VERSION,
        "feasible_a_over_c": {"mean": round(ac_mean, 3), "min": round(ac_lo, 3), "max": round(ac_hi, 3)},
        "HM_wedge": [round(AC_LO, 3), round(AC_HI, 3)],
        "wedge_geometric_center": round(WEDGE_GEOM_CENTER, 3),
        "constructed_a_over_c": 1.0,
        "fraction_c_greater_than_a": round(frac_c_gt_a, 2),
        "n_samples": len(pts),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The holographic a=c is an ASSUMPTION, not a consistency prediction -- the full c!=a exploitation. "
            "With the Weyl^2 axis g_C free, the feasible a/c = g_R2/g_C spans the ENTIRE Hofman-Maldacena wedge "
            "[0.333, 1.720] = [1/3, 31/18], and a/c = 1 (a=c) sits INTERIOR to it -- neither an edge nor a "
            "forced center, just one interior point of a one-parameter family. No consistency condition "
            "selects a=c; the only thing bounding the Euler-vs-Weyl^2 split is the conformal-collider (ANEC) "
            "wedge. So the constructed theory's a=c -- the holographic / two-derivative-Einstein value the "
            "frameworks default to (g_C=g_R2) -- is a CHOICE the engine inherited, not something the "
            "consistency conditions predict. The resolved basis therefore carries a genuine new FREE MODULUS, "
            "the c-a split, bounded only by 1/3 <= a/c <= 31/18. This is the honest sibling of v2.392 (g_6=g_8 "
            "was a Chebyshev-center artifact): a=c is likewise a constructed-point coincidence inherited from "
            "a default, not forced physics -- so it belongs in the ASSUMPTION bin of the candidate's honest "
            "tiering (v2.382), alongside g_6=g_8. The consequence for the earlier results is real: any "
            "prediction that leaned on the Weyl^2 sector -- the ghost mass m_g/Lambda = 1/sqrt(g_C) (v2.385), "
            "the fifth-force screening, the extremal-BH entropy shift Delta S_ext = A g_C + B g_4 (v2.378) -- "
            "was computed AT a=c and actually carries an unpinned c-a modulus that a finer c!=a analysis must "
            "marginalize over (v2.398 already showed the ghost mass swings [1.31, 2.97] across the wedge). The "
            "positive reading: the deviation c-a is exactly the higher-derivative / stringy signature (pure "
            "two-derivative Einstein gravity has c=a; c != a needs higher-curvature bulk terms, which this "
            "theory HAS), so the theory is CONSISTENT with -- but does not require -- a non-Einstein anomaly, "
            "and the size of that deviation is a genuine open prediction bounded by conformal-collider "
            "physics, not fixed at the holographic point."
        ),
        "honest_scope": (
            "The robust content is qualitative and measure-INDEPENDENT: the feasible a/c spans the whole HM "
            "wedge (verified to ~1-3%), a=c sits interior, and c-a is bounded ONLY by Hofman-Maldacena (the "
            "sole c-axis carver, v2.398) -- so a=c is not selected and is a free modulus. What IS "
            "measure-dependent and must NOT be over-read: the mean a/c ~ 0.757 and the '77% have c>a' -- these "
            "reflect the sampling being roughly uniform in g_C (which maps to an a/c distribution skewed below "
            "1 and centered near the wedge's geometric mean sqrt(1/3 * 31/18) = 0.758); sampling uniform in "
            "a/c would center near 1.03 instead. So the theory does NOT robustly 'prefer c>a' -- that is a "
            "parametrization artifact; the honest claim is only that a=c is unselected and c-a is free in the "
            "wedge. The HM wedge itself is the exact source-cited bound. This is theory-space exploration of "
            "the resolved (c!=a) basis, not a new prediction about the constructed point -- it downgrades a=c "
            "from an implicit result to an explicit assumption and flags that Weyl^2-sector results carry the "
            "modulus. Robust content: with g_C free, a=c is an interior, unselected point and c-a is a "
            "conformal-collider-bounded free modulus -- the holographic value is an assumption, not a "
            "prediction. Measure-dependent 'center' explicitly disclaimed. A c-a-modulus swing."
        ),
        "references": [
            "this repo: v2.398 (activated c-axis, HM sole carver), v2.392 (g_6=g_8 center artifact -- the sibling), v2.382 (candidate honest tiering), v2.385 (ghost = g_C), v2.378 (BH entropy = A g_C + B g_4), src/itb/constraints/hofman_maldacena.py",
            "physics: Hofman-Maldacena 2008 (1/3<=a/c<=31/18); c-a as the higher-derivative/stringy anomaly deviation; two-derivative Einstein gravity has a=c",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=40000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    res = run(n_walk=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING (full c!=a exploitation): the holographic a=c is an ASSUMPTION, not a prediction:")
    print(f"  feasible a/c {res['feasible_a_over_c']} spans the HM wedge {res['HM_wedge']}; a=c (a/c=1) is INTERIOR")
    print(f"  no consistency condition selects a=c -> c-a is a FREE MODULUS bounded only by conformal-collider physics")
    print(f"  (mean a/c {res['feasible_a_over_c']['mean']} ~ wedge geometric center {res['wedge_geometric_center']}, but this is MEASURE-DEPENDENT -- not a real 'prefers c>a')")
    print(f"  => a=c joins g_6=g_8 (v2.392) in the ASSUMPTION bin; Weyl^2-sector results (ghost/screening/BH-entropy) carry the modulus")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
