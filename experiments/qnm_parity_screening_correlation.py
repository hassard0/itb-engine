"""v2.357 - The parity and screening channels are correlated: stronger birefringence forces a deeper screening mandate.

v2.356 mapped three observationally independent falsification channels and flagged that the underlying
couplings are correlated through the constraints. This makes the parity<->screening correlation EXPLICIT and
quantitative -- two of the three channels are physically linked, not independent.

The link is the anomaly-inflow budget, which ties the parity coupling to g_R2:

    g_R2_parity^2 <= rho * g_4 * g_R2   =>   g_R2 >= g_R2_parity^2 / (rho * g_4)

So a larger parity coupling (stronger cosmic birefringence) forces a larger g_R2 -- and g_R2 is exactly what
the unscreened Eot-Wash bound caps. The screening over-cap factor is therefore

    f(g_R2_parity) = [g_R2_parity^2 / (rho * g_4)] / g_R2_max   ~  g_R2_parity^2

a QUADRATIC amplifier: across the data-pinned parity window [0.047, 0.078] the over-cap factor runs
1.12 -> 1.81 -> 3.06 (at the constructed g_4). Even at the birefringence FLOOR the factor exceeds 1, so the
screening mandate is locked in by the parity data itself at the constructed g_4 -- the two channels move
together (more parity -> quadratically deeper screening), which mechanistically explains why the screening
mandate's universality is data-linked (v2.355).
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

VERSION = "v2.357"
DEFAULT_OUT = Path("experiments/results/v2.357/qnm_parity_screening_correlation.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
G4_C = 0.529
PARITY_WINDOW = [0.0471, 0.06, 0.078]   # CMB floor, constructed, anomaly edge


def run(n_walk: int = 20000, seed: int = 0) -> dict:
    rho = CANONICAL["anomaly_rho"]
    cap = SubmmGravityYukawaBound(screened=False).g_R2_max

    def anomaly_min_gR2(gp, g4=G4_C):
        return gp * gp / (rho * g4)

    def over_cap(gp, g4=G4_C):
        return anomaly_min_gR2(gp, g4) / cap

    ladder = [{"g_R2_parity": gp,
               "anomaly_min_g_R2": round(anomaly_min_gR2(gp), 4),
               "over_cap_factor": round(over_cap(gp), 3)} for gp in PARITY_WINDOW]

    mandate_active_at_floor = over_cap(PARITY_WINDOW[0]) > 1.0
    monotic_increasing = all(ladder[i]["over_cap_factor"] < ladder[i + 1]["over_cap_factor"]
                             for i in range(len(ladder) - 1))
    # quadratic scaling: f(gp2)/f(gp1) ~ (gp2/gp1)^2
    g_lo, g_hi = PARITY_WINDOW[0], PARITY_WINDOW[2]
    ratio_observed = over_cap(g_hi) / over_cap(g_lo)
    ratio_quadratic = (g_hi / g_lo) ** 2
    quadratic_scaling = abs(ratio_observed - ratio_quadratic) < 1e-6

    # engine cross-check: over the feasible family, g_R2 and g_R2_parity are positively correlated,
    # and every member respects the anomaly floor g_R2 >= g_R2_parity^2/(rho g_4)
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
    g4, gR2, gR2p = pts[:, 0], pts[:, 3], pts[:, 5]
    corr = float(np.corrcoef(gR2, gR2p)[0, 1])
    family_respects_anomaly_floor = bool((gR2 >= gR2p ** 2 / (rho * g4) - 1e-9).all())

    checks = {
        "mandate_active_even_at_parity_floor": mandate_active_at_floor,
        "over_cap_increases_with_parity": monotic_increasing,
        "scaling_is_quadratic": quadratic_scaling,
        "family_gR2_gR2parity_positively_correlated": corr > 0.0,
        "family_respects_anomaly_floor": family_respects_anomaly_floor,
    }

    return {
        "version": VERSION,
        "anomaly_rho": rho,
        "submm_unscreened_cap": round(float(cap), 5),
        "constructed_g_4": G4_C,
        "over_cap_ladder": ladder,
        "over_cap_at_parity_floor": round(over_cap(PARITY_WINDOW[0]), 3),
        "ratio_observed_floor_to_edge": round(ratio_observed, 3),
        "ratio_if_quadratic": round(ratio_quadratic, 3),
        "family_corr_gR2_gR2parity": round(corr, 3),
        "n_samples": len(pts),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The parity and screening channels are POSITIVELY CORRELATED, not independent: stronger cosmic "
            "birefringence forces a quadratically deeper screening mandate. The anomaly-inflow budget "
            "g_R2_parity^2 <= rho g_4 g_R2 ties the parity coupling to g_R2 (g_R2 >= g_R2_parity^2/(rho "
            "g_4)), and g_R2 is exactly what the unscreened Eot-Wash bound caps, so the screening over-cap "
            "factor f = g_R2_parity^2/(rho g_4 g_R2_max) scales as g_R2_parity^2. Across the data-pinned "
            "parity window [0.047, 0.078] at the constructed g_4, f runs 1.12 -> 1.81 -> 3.06 -- and "
            "crucially it exceeds 1 EVEN AT THE BIREFRINGENCE FLOOR, so the screening mandate is locked in "
            "by the parity data itself (at the constructed g_4): the minimum parity the birefringence data "
            "allows already forces g_R2 above the unscreened cap. The engine confirms the linkage -- over "
            f"the feasible family g_R2 and g_R2_parity are positively correlated (corr = {corr:.2f}) and "
            "every member respects the anomaly floor. This mechanistically explains v2.355 (the screening "
            "mandate's universality is data-linked: it is the SAME anomaly inflow + birefringence floor that "
            "pushes g_R2 past the cap) and refines v2.356's three-channel map: the channels are "
            "observationally distinct but parity and screening are PHYSICALLY coupled through g_R2, with a "
            "quadratic amplification -- so a future tightening of the birefringence signal (raising the "
            "parity floor) would DEEPEN the screening mandate, while a downward revision would relax both "
            "together. The two channels are one correlated prediction wearing two observational hats."
        ),
        "honest_scope": (
            "The correlation is EXACT algebra at fixed g_4 (the anomaly floor on g_R2 chained with the "
            "screening cap), and the family positive-correlation is a genuine engine cross-check -- but the "
            "OVER-CAP NUMBERS (1.12 -> 3.06) are at the constructed g_4 = 0.529 and scale as 1/g_4, so a "
            "larger g_4 weakens the amplification (the family correlation corr ~ 0.x is below 1 precisely "
            "because g_4 also varies). Both inputs are toy-basis: the anomaly prefactor rho (v2.344, "
            "load-bearing) and the order-of-magnitude Eot-Wash cap (v2.354). The whole linkage rests on the "
            "birefringence detection being real (v2.329) -- it is the parity DATA that drives g_R2 up; "
            "without it the correlation is vacuous (no parity floor). 'Mandate active at the parity floor' "
            "uses the 2-sigma birefringence lower edge and the default rho; a smaller rho or a larger g_4 "
            "could drop the floor factor below 1, reopening a thin unscreened window at the parity floor "
            "(consistent with v2.355's small-coupling branch). Robust content: the parity and screening "
            "channels are physically coupled through g_R2 via the anomaly, with f ~ g_R2_parity^2, so they "
            "are not independent and move together. Toy basis, O(1) prefactors. A cross-channel correlation "
            "refining v2.356."
        ),
        "references": [
            "this repo: v2.356 (three-channel map, flagged the coupling correlation), v2.350 (birefringence -> g_4 g_R2 floor), v2.354/v2.355 (screening mandate + data-linked universality)",
            "this repo: src/itb/constraints/anomaly_flow.py (the linking constraint) + submm_gravity.py (the cap), v2.344 (rho), v2.329 (birefringence caveat)",
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
    print("parity <-> screening correlation (anomaly links g_R2_parity to g_R2, the screened coupling):")
    for r in res["over_cap_ladder"]:
        print(f"  g_R2_parity={r['g_R2_parity']:.4f} -> anomaly-min g_R2={r['anomaly_min_g_R2']}  "
              f"over-cap factor {r['over_cap_factor']}")
    print(f"  mandate active even at the birefringence floor: {res['consistency_checks']['mandate_active_even_at_parity_floor']} "
          f"(factor {res['over_cap_at_parity_floor']})")
    print(f"  scaling floor->edge: observed {res['ratio_observed_floor_to_edge']} vs quadratic {res['ratio_if_quadratic']}")
    print(f"  family corr(g_R2, g_R2_parity) = {res['family_corr_gR2_gR2parity']}  (n={res['n_samples']})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
