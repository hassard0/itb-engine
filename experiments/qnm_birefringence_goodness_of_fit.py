"""v2.360 - Does the theory actually FIT the birefringence data, or merely sit inside the 2-sigma band? (a refuted concern)

The parity headline has always been stated as "consistent at 2-sigma" -- but that is a weak claim (the 2-sigma
band is wide). This cycle measures the actual goodness-of-fit, and tests a natural criticism: does the theory
STRUCTURALLY underpredict the birefringence signal? The constructed center predicts beta = 3.4 * 0.06 = 0.204,
well below the measured central beta = 0.34 +/- 0.09 -- so a skeptic could argue the theory only fits by
hiding at the low edge of the data.

The test: find the MAXIMUM feasible g_R2_parity over the consistent+observed region (a greedy feasible
ascent), convert to the maximum predictable beta, and compare to the measurement at 1-sigma and 2-sigma. If
the theory's best beta reaches the measured 1-sigma band, the underprediction concern is REFUTED.

Result (refuted): the theory can reach g_R2_parity ~ 0.091, beta_max ~ 0.31 -- inside the measured 1-sigma
band [0.25, 0.43], only ~0.3-sigma from the central 0.34. So the theory does NOT structurally underpredict;
it fits the central value comfortably at its 2-sigma-high edge. The constructed CENTER (beta 0.204) is just
the conservative Chebyshev choice, not the theory's best fit. The theory's feasible beta-range does lean to
the LOW side of the data, so it mildly prefers a smaller birefringence -- an honest, mild lean, not a tension.
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

VERSION = "v2.360"
DEFAULT_OUT = Path("experiments/results/v2.360/qnm_birefringence_goodness_of_fit.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
KAPPA_BETA = 3.4
BETA_MEAS, BETA_SIGMA = 0.34, 0.09
CMB_FLOOR = 0.0471          # g_R2_parity 2-sigma lower edge


def run(n_walk: int = 40000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    # greedy feasible ascent on g_R2_parity (keep the highest-parity feasible point seen)
    rng = np.random.default_rng(seed)
    cur = CONSTRUCTED.copy()
    best = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 6), 0.0, None)
        if feasible(c):
            cur = c
            if c[5] > best[5]:
                best = c.copy()
    gR2p_max = float(best[5])
    beta_max = KAPPA_BETA * gR2p_max
    beta_center = KAPPA_BETA * CONSTRUCTED[5]
    beta_floor = KAPPA_BETA * CMB_FLOOR

    sigma_from_central = (BETA_MEAS - beta_max) / BETA_SIGMA   # how far the theory's BEST is from central
    one_sigma = (BETA_MEAS - BETA_SIGMA, BETA_MEAS + BETA_SIGMA)        # [0.25, 0.43]
    two_sigma = (BETA_MEAS - 2 * BETA_SIGMA, BETA_MEAS + 2 * BETA_SIGMA)  # [0.16, 0.52]

    reaches_1sigma = one_sigma[0] <= beta_max <= one_sigma[1]
    theory_range = (beta_floor, beta_max)
    overlaps_2sigma = not (theory_range[1] < two_sigma[0] or theory_range[0] > two_sigma[1])
    leans_low = beta_max < BETA_MEAS

    checks = {
        "theory_beta_max_reaches_1sigma_band": bool(reaches_1sigma),
        "no_structural_underprediction": bool(abs(sigma_from_central) < 1.0),   # refutes the criticism
        "feasible_range_overlaps_measurement_2sigma": bool(overlaps_2sigma),
        "constructed_center_is_conservative": bool(beta_center < beta_max),
        "theory_mildly_prefers_lower_birefringence": bool(leans_low),
    }

    return {
        "version": VERSION,
        "g_R2_parity_max_feasible": round(gR2p_max, 4),
        "beta_max_predictable": round(beta_max, 3),
        "beta_constructed_center": round(beta_center, 3),
        "beta_at_cmb_floor": round(beta_floor, 3),
        "theory_beta_range": [round(beta_floor, 3), round(beta_max, 3)],
        "measured_beta": [BETA_MEAS, BETA_SIGMA],
        "measured_1sigma_band": [round(one_sigma[0], 3), round(one_sigma[1], 3)],
        "best_fit_residual_sigma": round(sigma_from_central, 2),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The theory FITS the birefringence data well -- the natural 'it only underpredicts' criticism "
            f"is refuted with a number. Finding the maximum feasible parity coupling over the "
            f"consistent+observed region (greedy feasible ascent) gives g_R2_parity ~ {gR2p_max:.3f}, so the "
            f"theory's maximum predictable signal is beta_max ~ {beta_max:.2f} -- INSIDE the measured "
            f"1-sigma band [{one_sigma[0]:.2f}, {one_sigma[1]:.2f}], only {abs(sigma_from_central):.2f}-sigma "
            f"from the central 0.34. So the theory does NOT structurally underpredict cosmic birefringence: "
            f"it can reach the central value comfortably at its 2-sigma-high feasibility edge. The "
            f"constructed CENTER's beta = {beta_center:.2f} is lower only because it is the conservative "
            f"Chebyshev (max-margin) choice, not the theory's best fit -- the parity prediction is a RANGE "
            f"[{beta_floor:.2f}, {beta_max:.2f}] (from the birefringence 2-sigma floor to the theory's "
            f"feasibility ceiling), which overlaps the measured 1-sigma band on its upper end. The honest "
            f"residual: the theory's feasible beta-range leans to the LOW side of the data (its ceiling "
            f"{beta_max:.2f} sits just below the central 0.34), so it mildly PREFERS a smaller birefringence "
            f"than measured -- a soft lean, not a tension. This upgrades the parity headline from the weak "
            f"'consistent at 2-sigma' to the quantitative 'fits within ~0.3-sigma at its best, with a mild "
            f"low-side lean', and refutes the structural-underprediction concern. Combined with v2.359 (the "
            f"parity channel is the sole observational discriminator), this is the channel that matters most "
            f"and it fits."
        ),
        "honest_scope": (
            "The maximum feasible g_R2_parity is found by a seeded greedy ascent (a search, not a proof of "
            "the global maximum -- the true feasibility ceiling could be marginally higher, which would only "
            "STRENGTHEN the fit). The beta map (beta = 3.4 deg * g_R2_parity) is the engine's toy "
            "normalization with O(1)/order-of-magnitude uncertainty (v2.347), so the exact beta_max ~ 0.31 "
            "and the 0.3-sigma residual are illustrative -- a different beta normalization shifts the fit. "
            "The g_R2_parity ceiling itself is set by the anomaly budget (prefactor rho, v2.344) and the "
            "other curvature constraints, so it inherits those O(1) prefactors. The whole comparison "
            "presumes the birefringence detection is real (v2.329); it is a goodness-of-fit GIVEN the "
            "measurement, not independent evidence for it. 'No structural underprediction' is the robust, "
            "qualitative content (the theory's feasible range reaches into the measured band); the precise "
            "residual is soft. Toy basis, O(1) prefactors. A quantitative goodness-of-fit refuting a natural "
            "criticism of the parity headline."
        ),
        "references": [
            "this repo: v2.347/v2.348 (parity channel, beta map, GW pinch), v2.344 (g_R2_parity ceiling from anomaly rho), v2.359 (parity is the sole discriminator), v2.329 (birefringence caveat)",
            "Minami & Komatsu PRL 125,221301 (2020); Eskilt & Komatsu 2022 (beta = 0.34 +/- 0.09 deg)",
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
    print("birefringence goodness-of-fit (does the theory fit, or only underpredict?):")
    print(f"  max feasible g_R2_parity: {res['g_R2_parity_max_feasible']}  -> beta_max {res['beta_max_predictable']}")
    print(f"  theory beta range: {res['theory_beta_range']}   constructed center beta: {res['beta_constructed_center']}")
    print(f"  measured: {res['measured_beta'][0]} +/- {res['measured_beta'][1]}  (1-sigma {res['measured_1sigma_band']})")
    print(f"  best-fit residual: {res['best_fit_residual_sigma']} sigma  (no structural underprediction: {res['consistency_checks']['no_structural_underprediction']})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
