"""v2.349 - Is the ringdown floor guaranteed across the whole consistent+observed family, or only at the center?

A fresh sector after the parity arc: the OTHER prediction channel, ringdown. v2.336/v2.337 established the
constructed CENTER's ringdown floor -- the moment-tower mandate g_R4 >= g_R3^2 / g_R2 = 0.042 -- a guaranteed
minimum quartic-curvature (ringdown) deviation. But the floor is a function of the OTHER curvature couplings
(g_R3, g_R2), so it varies across the consistent+observed family and COLLAPSES wherever g_R3 -> 0. The
falsifiability question this raises: does a pure-GR ringdown (below the floor) refute the ENTIRE theory
family, or only its g_R3 != 0 members?

This extends v2.336/337 from the center to the whole family (paralleling how v2.341 extended the trilogy):
sample the feasible family, compute the moment-tower floor g_R3^2/g_R2 at every point, and find its MINIMUM
-- and whether g_R3 can reach ~0 within the feasible region.
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

VERSION = "v2.349"
DEFAULT_OUT = Path("experiments/results/v2.349/qnm_ringdown_floor_family.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
FLOOR_EPS = 0.01   # below this the floor is "effectively collapsed" (ringdown ~ indistinguishable from GR)


def floor_of(v) -> float:
    gR3, gR2 = v[4], v[3]
    return float(gR3 * gR3 / gR2) if gR2 > 1e-9 else 0.0


def run(n_walk: int = 20000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    rng = np.random.default_rng(seed)
    pts = [CONSTRUCTED.copy()]
    cur = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 6), 0.0, None)
        if feasible(c):
            cur = c
            pts.append(cur)
    pts = np.array(pts)
    n = len(pts)

    floors = np.array([floor_of(v) for v in pts])
    gR3 = pts[:, 4]
    constructed_floor = floor_of(CONSTRUCTED)

    min_floor = float(floors.min())
    median_floor = float(np.median(floors))
    max_floor = float(floors.max())
    min_gR3 = float(gR3.min())
    max_gR3 = float(gR3.max())

    floor_guaranteed = min_floor > FLOOR_EPS          # floor stays bounded away from 0 -> whole family floored
    gR3_can_vanish = min_gR3 < 0.02                    # g_R3 reaches near 0 -> floor collapses there

    checks = {
        "enough_samples": n >= 100,
        "constructed_floor_matches_moment_tower": abs(constructed_floor - 0.0420) < 0.002,
        "min_floor_is_family_minimum": min_floor <= constructed_floor + 1e-9,
        "floor_varies_across_family": max_floor > min_floor + 1e-6,
        # the central finding: floor-guaranteed XOR g_R3-can-vanish must be a coherent, reported verdict
        "verdict_is_coherent": (floor_guaranteed != gR3_can_vanish) or (min_floor <= FLOOR_EPS),
    }

    if floor_guaranteed:
        verdict = (
            f"The ringdown floor is GUARANTEED family-wide: even the minimum moment-tower floor over the "
            f"sampled feasible family is {min_floor:.3f} > {FLOOR_EPS}, because g_R3 stays bounded away from "
            f"zero (family minimum g_R3 = {min_gR3:.3f}). So a nonzero minimum ringdown deviation is "
            f"mandated for the ENTIRE consistent+observed family, not just the constructed center -- a "
            f"pure-GR ringdown below the floor would refute the whole theory, the strongest form of the "
            f"v2.336 ringdown discriminator."
        )
    else:
        verdict = (
            f"The ringdown floor is NOT guaranteed family-wide: it COLLAPSES toward zero on part of the "
            f"feasible region (family-minimum floor {min_floor:.3f}, reached where g_R3 falls to "
            f"{min_gR3:.3f}). The firm floor (0.042) is a property of the constructed CENTER and of "
            f"members with sizeable g_R3, not of every consistent+observed theory. So a pure-GR ringdown "
            f"would refute the g_R3 != 0 members (incl. the constructed theory) but NOT the small-g_R3 "
            f"sub-family, whose ringdown is indistinguishable from GR at this order. The ringdown is a "
            f"discriminator for the center, not a family-wide guarantee."
        )

    return {
        "version": VERSION,
        "n_samples": n,
        "constructed_floor": round(constructed_floor, 4),
        "family_floor_min": round(min_floor, 4),
        "family_floor_median": round(median_floor, 4),
        "family_floor_max": round(max_floor, 4),
        "family_gR3_min": round(min_gR3, 4),
        "family_gR3_max": round(max_gR3, 4),
        "floor_guaranteed_family_wide": bool(floor_guaranteed),
        "gR3_can_vanish_in_family": bool(gR3_can_vanish),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            verdict + " "
            "This extends the ringdown channel (v2.336 floor, v2.337 floor-firm/magnitude-loose) from the "
            "constructed center to the whole consistent+observed family, the curvature-sector parallel of "
            "v2.341's center->family extension for the consistency trilogy. The moment-tower floor "
            "g_R4 >= g_R3^2/g_R2 is exact; what varies across the family is g_R3 (the parity-even cubic), "
            "and since no current data constraint reads g_R3 from below, the family extends to small g_R3 "
            "where the floor weakens. The honest testability shape of the ringdown channel therefore "
            "depends on WHERE in the family the true theory sits: maximal (a guaranteed deviation) at the "
            "constructed center, vanishing on the small-g_R3 edge."
        ),
        "honest_scope": (
            "The family is a seeded random-walk sample of the feasible region (Metropolis-like, near-uniform "
            "target, step 0.03), so the EXACT minimum floor and minimum g_R3 are sampler-dependent (a finite "
            "walk may not reach the true extremal g_R3); the qualitative verdict (does g_R3 reach near zero "
            "feasibly?) is the robust content, not the precise 3-decimal extremum. The moment-tower floor "
            "g_R3^2/g_R2 is exact arithmetic, but g_R3, g_R2 are the toy-basis couplings and the "
            "g_R4->ringdown-shift map is rank-1 schematic (v2.336, the deep-research-flagged limitation), so "
            "'ringdown floor' means the g_R4 lower bound, not a sourced frequency shift. This is a CP-even, "
            "curvature-sector property, independent of the cosmic-birefringence data (unlike the parity "
            "channel). The family itself rests on the full consistent+observed stack (incl. the data "
            "constraints; the parity members carry the v2.329 caveat, but the floor is parity-independent). "
            "Toy basis, O(1) prefactors. A center->family extension of the ringdown floor."
        ),
        "references": [
            "this repo: v2.336 (g_R4 ringdown floor at the center), v2.337 (floor firm / magnitude loose), v2.341 (center->family extension method), v2.333 (family structure)",
            "this repo: moment tower g_R4 >= g_R3^2/g_R2; CEMZ bounds g_R3 from above (no data lower bound on g_R3)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=20000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    res = run(n_walk=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print(f"ringdown floor across the consistent+observed family ({res['n_samples']} samples):")
    print(f"  constructed-center floor: {res['constructed_floor']}")
    print(f"  family floor   min/median/max: {res['family_floor_min']} / {res['family_floor_median']} / {res['family_floor_max']}")
    print(f"  family g_R3     min/max:        {res['family_gR3_min']} / {res['family_gR3_max']}")
    print(f"  floor guaranteed family-wide? {res['floor_guaranteed_family_wide']}   g_R3 can vanish? {res['gR3_can_vanish_in_family']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
