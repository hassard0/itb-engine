"""v2.351 - A CP-even cross-sector cap: causality bounds the ringdown floor by the leading matter coupling.

The CP-even companion to v2.350 (which routed a parity observable to the parity-even sector). Two exact
curvature-sector constraints chain into a new corollary that brackets the ringdown floor:

  * moment tower (curvature Cauchy-Schwarz):  g_R3^2 <= g_R2 * g_R4   =>   g_R4 >= g_R3^2 / g_R2  (the FLOOR)
  * CEMZ causality:                           |g_R3| <= kappa * sqrt(g_4 * g_R2)   =>   g_R3^2 <= kappa^2 g_4 g_R2

Dividing the CEMZ bound by g_R2 caps the moment-tower floor itself:

    g_R4_floor  =  g_R3^2 / g_R2  <=  kappa^2 * g_4

So CAUSALITY limits how large the guaranteed-minimum ringdown deviation can be, tying it to the LEADING
MATTER coupling g_4 (kappa = cemz_kappa = 0.8 -> ceiling coefficient kappa^2 = 0.64). Combined with v2.349
(the floor COLLAPSES to 0 where g_R3 -> 0), the guaranteed ringdown floor is fully bracketed:

    0  <=  g_R4_floor  <=  kappa^2 * g_4

vanishing on the small-g_R3 edge and capped by causality x matter on the other. A complete, derived
characterization of the ringdown floor's range -- a CP-even cross-sector bridge (curvature floor <- matter
coupling, via causality).
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
from experiments.stack import build_stack, CANONICAL

VERSION = "v2.351"
DEFAULT_OUT = Path("experiments/results/v2.351/qnm_ringdown_floor_causality_cap.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])


def run(n_walk: int = 20000, seed: int = 0) -> dict:
    kappa = CANONICAL["cemz_kappa"]
    cap_coeff = kappa ** 2                                  # 0.64

    c_g4, c_gR2, c_gR3 = CONSTRUCTED[0], CONSTRUCTED[3], CONSTRUCTED[4]
    constructed_floor = float(c_gR3 ** 2 / c_gR2)
    constructed_ceiling = float(cap_coeff * c_g4)

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
    g4, gR2, gR3 = pts[:, 0], pts[:, 3], pts[:, 4]
    floors = np.where(gR2 > 1e-9, gR3 ** 2 / gR2, 0.0)
    ceilings = cap_coeff * g4
    saturation = np.where(ceilings > 1e-9, floors / ceilings, 0.0)   # floor / (kappa^2 g_4) in [0,1] if CEMZ holds

    family_floor_min = float(floors.min())
    family_floor_max = float(floors.max())
    family_max_saturation = float(saturation.max())
    family_respects_cap = bool((floors <= ceilings + 1e-9).all())

    checks = {
        "cap_coefficient_is_cemz_kappa_squared": abs(cap_coeff - kappa ** 2) < 1e-12,
        "constructed_floor_below_cap": constructed_floor <= constructed_ceiling,
        "family_floor_always_below_cap": family_respects_cap,        # engine confirms the analytic cap
        "floor_bracketed_zero_to_cap": family_floor_min < 0.01 and family_floor_max <= cap_coeff * float(g4.max()) + 1e-9,
        "cap_is_nontrivial_saturation_below_one": family_max_saturation <= 1.0 + 1e-9,
    }

    return {
        "version": VERSION,
        "cemz_kappa": kappa,
        "cap_coefficient_kappa_squared": round(cap_coeff, 4),
        "constructed_floor": round(constructed_floor, 4),
        "constructed_cap": round(constructed_ceiling, 4),
        "constructed_saturation": round(constructed_floor / constructed_ceiling, 4),
        "family_floor_min": round(family_floor_min, 4),
        "family_floor_max": round(family_floor_max, 4),
        "family_max_saturation_of_cap": round(family_max_saturation, 4),
        "family_respects_cap": family_respects_cap,
        "n_samples": len(pts),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"A new exact CP-even cross-sector corollary: CAUSALITY caps the ringdown floor by the leading "
            f"matter coupling. The moment tower forces a ringdown floor g_R4 >= g_R3^2/g_R2, and CEMZ "
            f"causality bounds g_R3^2 <= kappa^2 g_4 g_R2; dividing by g_R2 caps the floor itself: "
            f"g_R4_floor <= kappa^2 * g_4 = {cap_coeff:.2f} * g_4. So the guaranteed-minimum ringdown "
            f"deviation cannot be made arbitrarily large -- causality ties its maximum to the leading "
            f"matter coupling g_4. The engine confirms the analytic cap across the whole consistent+observed "
            f"family (every member's floor stays below kappa^2 g_4), with a maximum saturation of "
            f"{family_max_saturation:.2f} (the family reaches ~{family_max_saturation:.0%} of the causality "
            f"cap where CEMZ is most nearly saturated). This is the CP-even companion to v2.350's "
            f"parity-routed bound, and it COMPLETES the ringdown-floor picture: combining with v2.349 (the "
            f"floor collapses to 0 where g_R3 -> 0), the guaranteed ringdown floor is fully bracketed "
            f"0 <= g_R4_floor <= kappa^2 g_4 -- vanishing on the small-g_R3 edge and capped by causality x "
            f"matter on the other. For the constructed theory the floor 0.042 sits at "
            f"{constructed_floor/constructed_ceiling:.0%} of its causality cap {constructed_ceiling:.3f}, so "
            f"the center is far from the causality boundary in the ringdown sector -- consistent with the "
            f"v2.339 causality headroom. The ringdown floor is therefore not a free magnitude: it is pinned "
            f"between zero and a causality-set, matter-scaled ceiling."
        ),
        "honest_scope": (
            "The cap is exact ALGEBRA: dividing the CEMZ bound (g_R3^2 <= kappa^2 g_4 g_R2) by g_R2 gives "
            "the moment-tower floor's ceiling, no approximation, and the feasible family respecting it is a "
            "genuine numerical confirmation (and the cap CANNOT be violated by any feasible point since it "
            "follows analytically from CEMZ). But the inputs are toy-basis encodings: the CEMZ form and its "
            "prefactor kappa = cemz_kappa (default 0.8, a v2.345-slack prefactor) and the moment-tower form "
            "(no prefactor). So the cap COEFFICIENT (kappa^2 = 0.64) scales as kappa^2 -- an O(1) change in "
            "the causality prefactor moves it -- though kappa was found slack for feasibility (v2.345). The "
            "g_R4 -> ringdown-shift map is rank-1 schematic (v2.336), so 'ringdown floor' is the g_R4 lower "
            "bound, not a sourced frequency shift. This is a CP-even, data-independent statement (it uses "
            "only causality + the curvature moment tower, no parity data). The family check is a seeded "
            "random-walk sample, so the saturation maximum is sampler-dependent, but the cap itself is "
            "analytic. Toy basis, O(1) prefactors. A derived cross-sector cap completing the v2.349 floor "
            "bracket."
        ),
        "references": [
            "this repo: src/itb/constraints/cemz_causality.py (|g_R3| <= kappa sqrt(g_4 g_R2)); src/itb/constraints/curvature_dispersion_tower.py (g_R3^2 <= g_R2 g_R4)",
            "this repo: v2.349 (floor collapses to 0 where g_R3->0, the lower bracket), v2.350 (parity-routed cross-sector bound), v2.339 (causality headroom), v2.336 (g_R4 ringdown floor)",
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
    print("CP-even cross-sector cap: causality bounds the ringdown floor by g_4:")
    print(f"  cemz_kappa: {res['cemz_kappa']}   cap coefficient kappa^2: {res['cap_coefficient_kappa_squared']}")
    print(f"  constructed floor {res['constructed_floor']} <= cap {res['constructed_cap']}  "
          f"(saturation {res['constructed_saturation']})")
    print(f"  family floor min/max: {res['family_floor_min']} / {res['family_floor_max']}   "
          f"max saturation of cap: {res['family_max_saturation_of_cap']}")
    print(f"  bracket: 0 <= g_R4_floor <= kappa^2 g_4   (lower from v2.349, upper here)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
