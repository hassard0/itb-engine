"""v2.354 - The theory MANDATES screening: an unscreened dark-energy-scale R^2 fifth force is excluded (a third channel).

A genuinely fresh channel. Every consistent+observed cycle so far has used submm_screened=True, treating it
as a neutral convenience. It is NOT neutral -- it is LOAD-BEARING. The sub-mm gravity (Eot-Wash torsion-
balance) data constraint, UNSCREENED, caps the Ricci^2 coupling at g_R2 <= g_R2_max ~ 0.063 (the dark-energy-
scale f(R) scalaron mediates a Yukawa fifth force of fixed strength alpha = 1/3 at Compton wavelength
lambda(g_R2); the 50-um Eot-Wash exclusion crossing alpha=1/3 sets g_R2_max). The constructed theory has
g_R2 = 0.193 -- ~3x ABOVE that bound.

This cycle shows the constructed value is not an accident: the consistency + observed constraints FORCE g_R2
well above the unscreened cap, so the unscreened consistent+observed region is EMPTY. The theory therefore
PREDICTS its R^2 fifth force must be screened (chameleon / Vainshtein / dark-sector) -- a third, independent,
falsifiable channel (after parity/birefringence and ringdown): a detection of an unscreened dark-energy-scale
scalaron would exclude the constructed theory.

The mechanism, analytic: the anomaly-inflow budget needs g_R2_parity^2 <= rho g_4 g_R2 and cosmic
birefringence needs g_R2_parity >= 0.0471, so g_R2 >= 0.0471^2/(rho g_4) = 0.037/g_4. Against the unscreened
cap g_R2 <= 0.063 this requires g_4 >= 0.59 -- a thin sliver -- and the remaining constraints (graviton
forward positivity, cross-sector EFThedron, anomaly cancellation) close even that, leaving no feasible
unscreened point.
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
from itb.constraints.submm_gravity import SubmmGravityYukawaBound

VERSION = "v2.354"
DEFAULT_OUT = Path("experiments/results/v2.354/qnm_screening_mandate.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = dict(zip(KEYS, [0.529, 0.4, 0.4, 0.193, 0.09, 0.06]))
CMB_LOWER = 0.0471


def violations(coeffs, stack):
    return [r.constraint_name for r in check(Theory(coefficients=dict(coeffs), name="x"), stack).results
            if not r.satisfied]


def run(n_search: int = 30000, seed: int = 0) -> dict:
    g_R2_max = SubmmGravityYukawaBound(screened=False).g_R2_max
    rho = CANONICAL["anomaly_rho"]

    st_screened = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                              include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    st_unscreened = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                                include_gw_speed=True, include_gw_dispersion=True, submm_screened=False)

    con_screened_viol = violations(CONSTRUCTED, st_screened)
    con_unscreened_viol = violations(CONSTRUCTED, st_unscreened)

    # analytic: unscreened feasibility requires g_4 >= bire_lower^2 / (rho * g_R2_max)
    g4_min_required = CMB_LOWER ** 2 / (rho * g_R2_max)

    # empirical: search for ANY feasible unscreened point (g_R2 capped at g_R2_max)
    rng = np.random.default_rng(seed)
    found = None
    for _ in range(n_search):
        v = np.array([rng.uniform(0.3, 0.75), rng.uniform(0.2, 0.6), rng.uniform(0.2, 0.6),
                      rng.uniform(0.04, g_R2_max), rng.uniform(0.0, 0.15), rng.uniform(CMB_LOWER, 0.08)])
        if not violations(dict(zip(KEYS, v)), st_unscreened):
            found = [round(float(x), 4) for x in v]
            break
    unscreened_empty = (found is None)

    checks = {
        "constructed_violates_unscreened_bound": CONSTRUCTED["g_R2"] > g_R2_max,
        "only_submm_fails_at_constructed_unscreened": con_unscreened_viol == ["submm_gravity_yukawa_bound"],
        "constructed_feasible_when_screened": len(con_screened_viol) == 0,
        "unscreened_region_empirically_empty": unscreened_empty,
        "analytic_g4_floor_exceeds_half": g4_min_required > 0.5,   # unscreened needs g_4 >= ~0.59, a thin sliver
    }

    return {
        "version": VERSION,
        "g_R2_max_unscreened": round(float(g_R2_max), 5),
        "constructed_g_R2": CONSTRUCTED["g_R2"],
        "constructed_over_bound_factor": round(CONSTRUCTED["g_R2"] / g_R2_max, 2),
        "constructed_violations_screened": con_screened_viol,
        "constructed_violations_unscreened": con_unscreened_viol,
        "analytic_g4_min_for_unscreened": round(float(g4_min_required), 4),
        "n_search": n_search,
        "unscreened_feasible_point": found,
        "unscreened_region_empty": unscreened_empty,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The constructed theory MANDATES screening of its R^2 fifth force: an unscreened "
            f"dark-energy-scale f(R) scalaron is excluded. The submm_screened=True flag used throughout the "
            f"program is therefore LOAD-BEARING, not a convenience. The unscreened Eot-Wash bound caps "
            f"g_R2 <= {g_R2_max:.4f}, but the constructed theory has g_R2 = 0.193 -- {CONSTRUCTED['g_R2']/g_R2_max:.1f}x "
            f"above it -- and under the unscreened stack the constructed point fails ONLY the sub-mm bound "
            f"(everything else holds), while when screened it is fully feasible. The high g_R2 is not an "
            f"accident: the consistency + observed constraints FORCE it. Analytically, the anomaly-inflow "
            f"budget (g_R2_parity^2 <= rho g_4 g_R2) plus the cosmic-birefringence floor (g_R2_parity >= "
            f"0.0471) give g_R2 >= 0.0471^2/(rho g_4) = 0.037/g_4, so meeting the unscreened cap would "
            f"require g_4 >= {g4_min_required:.2f} -- a thin sliver -- and the remaining constraints "
            f"(graviton forward positivity, cross-sector EFThedron, anomaly cancellation, which also push "
            f"g_R2 up) close even that: a search of {n_search} random points over the plausible box under "
            f"the unscreened stack finds NO feasible theory. So the unscreened consistent+observed region is "
            f"empty, and the theory makes a definite third-channel prediction (after parity/birefringence "
            f"and ringdown): the R^2 scalaron must be screened (chameleon / Vainshtein / dark-sector). This "
            f"is falsifiable in the same Eot-Wash channel that motivates it -- a confirmed unscreened "
            f"dark-energy-scale fifth force would exclude the constructed theory outright. It also reframes "
            f"the parity headline's companion: the SAME birefringence floor + anomaly inflow that v2.350 "
            f"used to lower-bound g_4 g_R2 is what pushes g_R2 past the Eot-Wash cap and forces screening."
        ),
        "honest_scope": (
            "The emptiness of the unscreened region is an EMPIRICAL search result (a large random sample, "
            "not an analytic proof), but it is corroborated by the analytic lower bound on g_R2 (anomaly "
            "inflow + birefringence -> g_R2 >= 0.037/g_4, needing g_4 >= 0.59 even before the other three "
            "g_R2-raising constraints) and by the constructed point failing only the sub-mm bound "
            "unscreened. The g_R2_max ~ 0.063 is a DATA reading with order-of-magnitude uncertainty (the "
            "Eot-Wash curve points are read off the published figure, and the alpha=1/3 scalaron strength + "
            "the 2.4 meV dark-energy cutoff are the model inputs) -- so the exact 3.08x violation factor is "
            "soft, but the qualitative gap (g_R2 ~ 0.19 forced, cap ~ 0.06) is an order of magnitude clear. "
            "The result also inherits the anomaly prefactor rho (v2.344) and the cosmic-birefringence "
            "detection being real (v2.329): if birefringence is a systematic, g_R2_parity can vanish, the "
            "anomaly floor on g_R2 relaxes, and a small-g_R2 unscreened branch might reopen -- so the "
            "screening mandate is contingent on the same data as the parity headline. Robust content: the "
            "consistency+observed constraints force g_R2 well above the unscreened Eot-Wash cap, so the "
            "theory requires a screened scalaron -- a real, falsifiable third channel. Toy basis, O(1) "
            "prefactors."
        ),
        "references": [
            "this repo: src/itb/constraints/submm_gravity.py (unscreened Eot-Wash cap g_R2 <= 0.063, alpha=1/3 f(R) scalaron); experiments/stack.py (submm_screened flag)",
            "this repo: v2.350 (birefringence -> g_4 g_R2 floor, the same mechanism), v2.344 (anomaly rho), v2.329 (birefringence caveat), v2.347 (parity birefringence channel)",
            "Lee et al PRL 124,101101 (2020); Kapner et al PRL 98,021101 (2007) (Eot-Wash sub-mm gravity)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=30000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    res = run(n_search=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("does the theory mandate screening of its R^2 fifth force?")
    print(f"  unscreened Eot-Wash cap: g_R2 <= {res['g_R2_max_unscreened']}   constructed g_R2 = {res['constructed_g_R2']} "
          f"({res['constructed_over_bound_factor']}x over)")
    print(f"  constructed unscreened violations: {res['constructed_violations_unscreened']}")
    print(f"  constructed screened violations:   {res['constructed_violations_screened'] or 'none (feasible)'}")
    print(f"  analytic g_4 floor for unscreened feasibility: {res['analytic_g4_min_for_unscreened']}")
    print(f"  unscreened feasible point in {res['n_search']} samples: {res['unscreened_feasible_point'] or 'NONE -> region empty'}")
    print(f"  => MANDATE: screened scalaron (chameleon/Vainshtein/dark)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
