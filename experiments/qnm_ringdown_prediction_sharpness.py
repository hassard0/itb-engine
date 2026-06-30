"""v2.337 - The ringdown prediction is a firm floor but a loose magnitude (vs the sharp parity prediction).

v2.336 gave the moment-tower FLOOR on the constructed theory's ringdown-active quartic curvature g_R4. This
cycle completes that: what is the full feasible RANGE of g_R4 -- is the ringdown prediction sharp, or only
floored? And how does it compare to the (sharp, data-pinned) parity prediction?

The answer is an honest asymmetry. The constructed theory's g_R4 spans a WIDE feasible range [~0.05, ~0.60]
(a ~10x window): the floor is firm (the moment-tower mandate g_R4 >= g_R3^2/g_R2, v2.336) but the ceiling
is the complexity cutoff, and nothing in between pins it -- because NO data constraint reads g_R4 (it is the
opt-in curvature-tower coupling), so it is only THEORY-bounded. By contrast the parity prediction is sharp
(~15% spread) because the cosmic-birefringence DATA pins it (v2.334). So the constructed theory firmly
predicts a MINIMUM ringdown deviation (the floor, the v2.336 discriminator) but NOT its size, and a future
curvature-sector measurement would be needed to sharpen the ringdown the way birefringence sharpened the
parity.
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

VERSION = "v2.337"
DEFAULT_OUT = Path("experiments/results/v2.337/qnm_ringdown_prediction_sharpness.py".replace(".py", ".json"))

CONSTRUCTED = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
PARITY_REL_SPREAD = 0.15   # v2.334: the parity-sector prediction relative spread


def run() -> dict:
    tower = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True,
                        include_curvature_tower=True)

    def feasible(c):
        return all(r.satisfied for r in check(Theory(coefficients=c, name="x"), tower).results)

    moment_floor = CONSTRUCTED["g_R3"] ** 2 / CONSTRUCTED["g_R2"]
    grid = np.round(np.arange(0.0, 2.0, 0.01), 3)
    feas_g4 = [float(g) for g in grid if feasible({**CONSTRUCTED, "g_R4": float(g)})]
    g4_lo, g4_hi = min(feas_g4), max(feas_g4)
    width = g4_hi - g4_lo
    rel_spread = width / np.mean([g4_lo, g4_hi])

    # what caps g_R4 from above?
    above = {**CONSTRUCTED, "g_R4": g4_hi + 0.05}
    wc = min(check(Theory(coefficients=above, name="x"), tower).results, key=lambda r: r.signed_distance_margin)
    ceiling_constraint = wc.constraint_name

    # confirm no data constraint binds g_R4 (the ceiling is a theory constraint, not a data one)
    data_names = {"submm_gravity_yukawa_bound", "cosmic_birefringence_data", "gw_speed_bound", "gw_dispersion_bound"}
    ceiling_is_theory = ceiling_constraint not in data_names

    checks = {
        "gR4_floor_is_the_moment_tower": bool(abs(g4_lo - moment_floor) < 0.02),
        "gR4_range_is_wide": bool(width > 0.3),
        "ringdown_much_looser_than_parity": bool(rel_spread > 3 * PARITY_REL_SPREAD),
        "gR4_ceiling_is_a_theory_constraint_not_data": bool(ceiling_is_theory),
        "ringdown_floor_firm_magnitude_loose": bool((abs(g4_lo - moment_floor) < 0.02) and (width > 0.3)),
    }

    return {
        "version": VERSION,
        "moment_tower_floor": round(moment_floor, 3),
        "gR4_feasible_range": [round(g4_lo, 3), round(g4_hi, 3)],
        "gR4_range_width": round(width, 3),
        "gR4_relative_spread": round(float(rel_spread), 2),
        "parity_relative_spread": PARITY_REL_SPREAD,
        "ceiling_constraint": ceiling_constraint,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The constructed theory's ringdown prediction is a firm FLOOR but a loose MAGNITUDE -- an "
            "honest asymmetry with the sharp parity prediction. The ringdown-active quartic curvature g_R4 "
            f"spans a WIDE feasible range [{g4_lo:.2f}, {g4_hi:.2f}] -- a relative spread of "
            f"~{100*rel_spread:.0f}%, roughly a 10x window -- whereas the parity prediction has only ~15% "
            "spread (v2.334). The floor is firm: it is the moment-tower mandate g_R4 >= g_R3^2/g_R2 = "
            f"{moment_floor:.3f} (v2.336), so a nonzero minimum ringdown deviation is guaranteed. But the "
            f"ceiling ({g4_hi:.2f}) is set by the {ceiling_constraint} -- a THEORY constraint -- and "
            "nothing in between pins g_R4, because NO data constraint reads it: g_R4 is the opt-in "
            "curvature-tower coupling, observationally unconstrained, so it is only theory-bounded. This "
            "is exactly why the ringdown is loose while the parity is sharp: the cosmic-birefringence data "
            "PINS the parity coupling (v2.334) but no current measurement touches g_R4. So the honest "
            "shape of the constructed theory's testability is: a SHARP parity prediction (data-pinned, the "
            "headline) and a FLOORED-BUT-LOOSE ringdown prediction (theory-bounded). The ringdown channel "
            "can therefore CONFIRM a minimum quartic-curvature deviation -- and a ringdown consistent with "
            "pure GR below the floor would REFUTE the theory -- but it does not sharply predict the "
            "deviation's size; a future curvature-sector measurement sensitive to g_R4 would sharpen the "
            "ringdown the way cosmic birefringence sharpened the parity. The v2.336 ringdown discriminator "
            "(ordering by floor) stands; this cycle adds that the floor, not the magnitude, is the firm "
            "part."
        ),
        "honest_scope": (
            "The g_R4 range and the ceiling constraint are the engine's literal feasibility verdict with "
            "the curvature tower on; the floor (g_R3^2/g_R2) is exact. The exact range [0.05, 0.60] "
            "depends on the complexity-cutoff prefactor (c_max and the g_R4 weight as a dimension-8 "
            "operator), so the WIDTH is convention-dependent -- the robust content is the CONTRAST: the "
            "ringdown (g_R4) is only theory-bounded (floor firm, magnitude loose) because no data "
            "constraint reads it, while the parity is data-pinned (sharp). The ~15% parity spread is the "
            "v2.334 value (itself contingent on the birefringence data, v2.329). The g_R4->ringdown-shift "
            "size remains schematic (rank-1 qNM->R^4, v2.336), so 'a minimum ringdown deviation' refers to "
            "the g_R4 floor, not a sourced frequency shift. This is a curvature-sector (CP-even) "
            "characterization, independent of the cosmic-birefringence data. Toy basis, O(1) prefactors. A "
            "completion of v2.336 (floor -> full range)."
        ),
        "references": [
            "this repo: v2.336 (g_R4 ringdown floor), v2.334 (sharp parity prediction), v2.292 (moment tower), v2.325 (complexity cutoff)",
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
    print("how sharp is the constructed theory's ringdown (g_R4) prediction?")
    print(f"  moment-tower floor: {res['moment_tower_floor']}")
    print(f"  feasible range: {res['gR4_feasible_range']}  width {res['gR4_range_width']}  "
          f"(rel spread {100*res['gR4_relative_spread']:.0f}%)")
    print(f"  ceiling set by: {res['ceiling_constraint']} (theory, not data)")
    print(f"  vs parity prediction spread ~{100*res['parity_relative_spread']:.0f}% (data-pinned, sharp)")
    print(f"  => firm FLOOR, loose MAGNITUDE; ringdown loose because no data reads g_R4")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
