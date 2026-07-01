"""v2.393 - SWING: matter SOURCES the leading gravitational correction -- the anomaly forbids matter without curvature (converse of matter dominance).

Matter dominance (v2.389/391) bounds the gravitational sector from ABOVE (matter caps every gravitational
coupling). This swing finds the converse from below: matter FORCES a nonzero leading gravitational correction.

Direct feasibility test (theory-only stack): pure GR (all couplings zero) is consistent, but a theory with a
MATTER sector and ZERO higher-curvature gravity (g_4,g_6,g_8 != 0, g_R2=g_R3=g_R2_parity=0) is INCONSISTENT --
it violates anomaly cancellation. The engine's 4D gravitational-anomaly-cancellation constraint is a slab
|g_4 g_6 - c_anom g_R2^2| <= tol (c_anom=1, tol=0.2), so given the matter product g_4 g_6 it forces the leading
curvature coupling g_R2 into a BAND around sqrt(g_4 g_6):

    g_R2 in [ sqrt(g_4 g_6 - tol),  sqrt(g_4 g_6 + tol) ].

For the constructed matter sector g_4 g_6 = 0.212, that lower edge is sqrt(0.012) = 0.108 > 0 -- so g_R2 = 0 is
FORBIDDEN. Matter cannot exist without a nonzero leading gravitational correction. Combined with matter
dominance, the leading curvature coupling g_R2 is LOCKED to matter from BOTH sides: the anomaly floors it
(g_R2 >= 0.108) and the WGC/screening caps it -- with only g_R2 turned on, the feasible band is [0.108, 0.226],
nonzero at both ends. So the higher-curvature gravitational sector is neither absent nor free: it is SOURCED
into existence by matter (anomaly, from below) and bounded in size by matter (positivity/WGC, from above).
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

VERSION = "v2.393"
DEFAULT_OUT = Path("experiments/results/v2.393/qnm_matter_sources_gravity.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
MATTER = [0.529, 0.4, 0.4]


def run() -> dict:
    stack = build_stack(rfc_form="convex_hull")   # theory-only

    def viol(v):
        return [r.constraint_name for r in check(Theory(coefficients=dict(zip(KEYS, np.array(v, float))), name="x"), stack).results if not r.satisfied]

    def feasible(v):
        return len(viol(v)) == 0

    anom = [c for c in stack if getattr(c, "name", "") == "anomaly_cancellation"][0]
    c_anom, tol = float(anom.c_anom), float(anom.tolerance)

    pure_gr_feasible = feasible([0, 0, 0, 0, 0, 0])
    matter_only_viol = viol(MATTER + [0, 0, 0])
    matter_only_feasible = len(matter_only_viol) == 0
    matter_plus_r2_feasible = feasible(MATTER + [0.193, 0, 0])

    g4g6 = MATTER[0] * MATTER[1]
    band_lo = float(np.sqrt(max(0.0, (g4g6 - tol) / c_anom)))
    band_hi = float(np.sqrt((g4g6 + tol) / c_anom))

    # feasible g_R2 range with only g_R2 turned on (other constraints may cap tighter than the anomaly band)
    grid = np.linspace(0.0, 0.7, 351)
    feas_gr2 = [float(g) for g in grid if feasible(MATTER + [g, 0.0, 0.0])]
    gr2_min, gr2_max = (min(feas_gr2), max(feas_gr2)) if feas_gr2 else (None, None)

    checks = {
        "pure_gr_is_consistent": pure_gr_feasible,
        "matter_without_curvature_forbidden": (not matter_only_feasible) and ("anomaly_cancellation" in matter_only_viol),
        "matter_plus_leading_curvature_ok": matter_plus_r2_feasible,
        "anomaly_forces_gR2_floor_above_zero": band_lo > 0.0,
        "gR2_zero_forbidden_given_matter": (gr2_min is not None) and (gr2_min > 1e-6),
    }

    return {
        "version": VERSION,
        "anomaly_c_anom": c_anom, "anomaly_tolerance": tol,
        "pure_gr_feasible": pure_gr_feasible,
        "matter_only_feasible": matter_only_feasible,
        "matter_only_violations": matter_only_viol,
        "matter_g4g6": round(g4g6, 3),
        "anomaly_forced_gR2_band": [round(band_lo, 3), round(band_hi, 3)],
        "feasible_gR2_with_matter_only": [round(gr2_min, 3), round(gr2_max, 3)] if gr2_min is not None else None,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Matter SOURCES the leading gravitational correction -- the converse of matter dominance. Matter "
            "dominance (v2.389/391) bounds the gravitational sector from above; this finds the bound from "
            "below. A direct feasibility test shows pure GR (all couplings zero) is consistent, but a theory "
            "with a matter sector and ZERO higher-curvature gravity is INCONSISTENT -- it violates anomaly "
            "cancellation. The engine's 4D gravitational-anomaly constraint is a slab |g_4 g_6 - g_R2^2| <= "
            "0.2, so given the matter product g_4 g_6 = 0.212 it forces the leading curvature coupling g_R2 "
            "into a band [0.108, 0.642] around sqrt(g_4 g_6); the lower edge 0.108 > 0 means g_R2 = 0 is "
            "FORBIDDEN. Matter cannot exist without a nonzero leading gravitational correction: the anomaly "
            "locks g_R2 to matter. Combined with matter dominance, the leading curvature coupling is pinned "
            "from BOTH sides -- the anomaly floors it (>= 0.108) and the WGC/screening cap it, so with only "
            "g_R2 turned on the feasible band is [0.108, 0.226], nonzero at both ends. So the higher-curvature "
            "gravitational sector is neither absent nor free: it is SOURCED into existence by matter (from "
            "below, via the anomaly) and bounded in size by matter (from above, via positivity/WGC). This "
            "completes the matter-gravity locking picture -- (i) matter forces the leading gravitational "
            "correction to exist (this swing), (ii) matter sets its scale and caps its strength at <=40% of "
            "matter's (v2.389/391), (iii) the moment tower organizes the higher curvature couplings among "
            "themselves (v2.375) -- and re-reads 'quantum gravity is not general relativity' concretely: GR "
            "with matter is inconsistent in this engine; consistency demands the higher-curvature completion, "
            "and demands it be matter-sized. Pure GR survives only in the empty (no-matter) limit."
        ),
        "honest_scope": (
            "The 4D gravitational-anomaly-cancellation constraint is the engine's TOY simplification "
            "(Alvarez-Gaume-Witten representative, c_anom=1, tolerance=0.2) -- and physically 4D gravity has "
            "no perturbative gravitational anomaly for the graviton alone (the AGW anomaly is for chiral "
            "matter in 4k+2 dimensions), so 'matter sources g_R2' is a statement WITHIN this toy encoding of "
            "anomaly matching, not a first-principles 4D theorem; the robust structural content is that an "
            "anomaly-MATCHING (equality/slab) condition between the matter product and the leading curvature "
            "coupling forbids the g_R2 = 0 corner, which is the generic consequence of ANY matching condition "
            "of this shape. The band edges (0.108, 0.642) and the feasible [0.108, 0.226] scale with the toy "
            "tolerance (0.2) and c_anom (1) -- toy-basis numbers; the ROBUST facts are qualitative: pure GR "
            "feasible, matter-only forbidden by the anomaly, g_R2=0 forbidden given matter, g_R2 forced into a "
            "nonzero band. This is theory-only (no data); data narrows the band further. The wide tolerance "
            "(0.2 vs g_4 g_6 = 0.212) means the anomaly is a loose band, not a sharp locking -- it forbids "
            "zero and far values but permits a range, so 'matter determines g_R2' overstates it; 'matter "
            "forces g_R2 nonzero and into a band' is exact. Robust content: consistency (anomaly matching) "
            "forbids matter without a nonzero leading gravitational correction -- matter sources gravity from "
            "below, complementing matter dominance from above. Toy anomaly encoding, robust "
            "forbid-the-zero-corner structure. A matter-sources-gravity swing."
        ),
        "references": [
            "this repo: v2.389/391 (matter dominance, gravity bounded above by matter), src/itb/constraints/anomaly.py (4D anomaly slab), v2.371 (anomaly determines parity), v2.375 (moment tower organizes curvature), v2.322 (feasibility)",
            "physics: Alvarez-Gaume-Witten 1984 (gravitational anomalies), Bardeen-Zumino; 't Hooft anomaly matching",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING: matter SOURCES the leading gravitational correction (converse of matter dominance):")
    print(f"  pure GR (all zero) feasible: {res['pure_gr_feasible']}")
    print(f"  matter WITHOUT curvature gravity feasible: {res['matter_only_feasible']}  (viol: {res['matter_only_violations']})")
    print(f"  anomaly forces g_R2 band {res['anomaly_forced_gR2_band']} around sqrt(g4 g6); g_R2=0 FORBIDDEN (lower edge > 0)")
    print(f"  with only g_R2 on, feasible g_R2: {res['feasible_gR2_with_matter_only']} -- nonzero at both ends")
    print(f"  => matter forces gravity from below (anomaly), matter dominance caps it from above -> g_R2 locked to matter")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
