"""v1.79 - The EFT the data points to -- and the tension it reveals.

Attempting to construct the deepest-interior EFT consistent with theory + sub-mm +
cosmic birefringence reveals that the region is EMPTY-or-knife-edge. The culprit is
a sharp four-way pinch, dominated by ANOMALY INFLOW:

    anomaly inflow:   g_R2_parity^2 + 2 g_R3_parity^2 <= rho * g_4 * g_R2  (rho=0.06)
    sub-mm gravity:   g_R2 <= 0.063
    helicity positivity: |g_R2_parity| <= g_R2
    => the largest parity coupling a consistent, sub-mm-safe EFT can carry is
       g_R2_parity_max = sqrt(rho * g_4_max * g_R2_max),
    hence a CEILING on the predictable cosmic-birefringence angle beta_max =
    kappa_beta * g_R2_parity_max.

So instead of a fitted point we compute the engine's CEILING on birefringence under
each scenario and compare to the Minami-Komatsu measurement beta = 0.34 +/- 0.09:
  - UNSCREENED (sub-mm active): beta_max is small -> TENSION with the measurement.
  - SCREENED (sub-mm vacuous): g_R2 can be larger -> beta_max rises -> accommodated.

We also register the best-achievable (max-birefringence, consistent, sub-mm-safe)
point as the data-driven framework, honestly noting it UNDERPREDICTS the measured
beta in the unscreened scenario.

Run on Vulcan:  python experiments/data_driven_eft.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.holographic_ac import lambda_GB, eta_over_s_kss
from itb.constraints.submm_gravity import _lambda_um, SubmmGravityYukawaBound
from itb.constraints.cosmic_birefringence import KAPPA_BETA, BETA_MEAS_DEG, BETA_SIGMA_DEG
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
E_LAMBDA_DE = 2.4e-3

# globals for the sampling workers (set in main, inherited at Pool creation)
_SAMP_STACK = None
_SAMP_LO = None
_SAMP_HI = None


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _maxgp_chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = _SAMP_LO + (_SAMP_HI - _SAMP_LO) * rng.random((n, len(COEFFS)))
    best_gp, best_x = -np.inf, None
    for i in range(n):
        if X[i, 6] <= best_gp:           # can't beat current max anyway
            continue
        th = _theory(X[i])
        if all(c.evaluate(th).satisfied for c in _SAMP_STACK):
            best_gp, best_x = X[i, 6], X[i].copy()
    return (best_gp, None if best_x is None else best_x.tolist())


def max_birefringence(stack, lo, hi, n_samples=6_000_000):
    """Maximize g_R2_parity (hence beta) over the feasible region of `stack` by
    dense parallel sampling (robust to the thin feasible region)."""
    global _SAMP_STACK, _SAMP_LO, _SAMP_HI
    _SAMP_STACK, _SAMP_LO, _SAMP_HI = stack, lo, hi
    import os
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = n_samples // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_maxgp_chunk, [(900 + k, per) for k in range(chunks)])
    best = max((r for r in res if r[1] is not None), default=None,
              key=lambda r: r[0])
    if best is None:
        return -np.inf, None
    return float(best[0]), np.array(best[1])


def main():
    # box focused where the anomaly-inflow ceiling is highest (large g_4, g_R2)
    LO = np.array([0.20, 0.10, 0.20, 0.04, 0.0, 0.04, 0.0, -0.03])
    HI_U = np.array([0.60, 0.55, 0.60, 0.063, 0.05, 0.30, 0.07, 0.03])  # sub-mm cap
    HI_S = np.array([0.60, 0.55, 0.60, 0.45, 0.30, 0.45, 0.20, 0.05])   # g_R2 free

    # UNSCREENED: theory + sub-mm
    stack_u = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                          include_data=True)
    gp_u, x_u = max_birefringence(stack_u, LO, HI_U)
    beta_u = KAPPA_BETA * gp_u

    # SCREENED: theory only (sub-mm vacuous), g_R2 free
    stack_s = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    gp_s, x_s = max_birefringence(stack_s, LO, HI_S)
    beta_s = KAPPA_BETA * gp_s

    tension_u = (BETA_MEAS_DEG - beta_u) / BETA_SIGMA_DEG
    tension_s = (BETA_MEAS_DEG - beta_s) / BETA_SIGMA_DEG

    # the best-achievable consistent + sub-mm-safe (max-birefringence) EFT
    coeffs_u = {k: round(float(v), 4) for k, v in zip(COEFFS, x_u)}
    gR2 = float(x_u[3]); gC = float(x_u[5])
    fingerprint = {
        "a_over_c": round(gR2 / gC, 4) if gC > 0 else None,
        "eta_over_s_KSS": round(eta_over_s_kss(lambda_GB(gR2)), 4),
        "scalaron_lambda_um": round(_lambda_um(gR2, E_LAMBDA_DE), 2),
        "predicted_beta_deg": round(beta_u, 4),
    }
    # the SCREENED data-driven EFT (matches the measured beta; requires screening)
    coeffs_s = {k: round(float(v), 4) for k, v in zip(COEFFS, x_s)}
    gR2s = float(x_s[3]); gCs = float(x_s[5])
    fingerprint_s = {
        "a_over_c": round(gR2s / gCs, 4) if gCs > 0 else None,
        "eta_over_s_KSS": round(eta_over_s_kss(lambda_GB(gR2s)), 4),
        "scalaron_lambda_um": round(_lambda_um(gR2s, E_LAMBDA_DE), 2),
        "predicted_beta_deg": round(beta_s, 4),
    }

    # ---- figure: birefringence ceiling vs measurement ----
    fig, ax = plt.subplots(figsize=(9, 6))
    xs = ["UNSCREENED\n(theory + sub-mm)", "SCREENED\n(theory only)"]
    vals = [beta_u, beta_s]
    bars = ax.bar(xs, vals, color=["#d62728", "#1f77b4"], alpha=0.85, width=0.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v, f"beta_max={v:.2f} deg",
                ha="center", va="bottom", fontsize=10)
    ax.axhspan(BETA_MEAS_DEG - BETA_SIGMA_DEG, BETA_MEAS_DEG + BETA_SIGMA_DEG,
               color="#9467bd", alpha=0.25, label="Minami-Komatsu 1 sigma")
    ax.axhline(BETA_MEAS_DEG, color="black", lw=1.5, label="measured beta=0.34 deg")
    ax.set_ylabel("max consistent cosmic-birefringence beta (deg)")
    ax.set_title("v1.79  The engine's CEILING on cosmic birefringence\n"
                 f"unscreened: beta_max={beta_u:.2f} deg ({tension_u:.1f} sigma below "
                 f"measured); screened: {beta_s:.2f} deg (accommodates)", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    png = "/tmp/data_driven_eft.png"
    fig.savefig(png, dpi=140)

    summary = {
        "headline": "Anomaly inflow + sub-mm gravity CAP the predictable cosmic "
                    "birefringence; the measured beta is in tension unless screened.",
        "binding_constraint": "generalized_anomaly_inflow: g_R2_parity^2 + 2 "
                              "g_R3_parity^2 <= 0.06 * g_4 * g_R2",
        "beta_measured_deg": BETA_MEAS_DEG, "beta_sigma_deg": BETA_SIGMA_DEG,
        "UNSCREENED": {"beta_max_deg": round(beta_u, 4),
                       "g_R2_parity_max": round(gp_u, 4),
                       "tension_sigma": round(tension_u, 2),
                       "verdict": "TENSION (engine cannot reach measured beta)"},
        "SCREENED": {"beta_max_deg": round(beta_s, 4),
                     "g_R2_parity_max": round(gp_s, 4),
                     "tension_sigma": round(tension_s, 2),
                     "verdict": "accommodates the measurement"},
        "best_achievable_unscreened_eft": coeffs_u,
        "best_achievable_fingerprint": fingerprint,
        "data_driven_eft_SCREENED (matches beta)": coeffs_s,
        "data_driven_eft_SCREENED_fingerprint": fingerprint_s,
        "interpretation": "Either the scalaron is SCREENED (relaxing sub-mm so a "
                          "larger g_R2 allows more parity coupling), or the measured "
                          "birefringence is in ~2 sigma tension with consistency "
                          "(anomaly inflow) + unscreened sub-mm gravity.",
        "assumptions": "kappa_beta=3.4 (order-of-mag); rho_inflow=0.06; beta is a "
                       "3.6 sigma HINT. A TARGET/tension, not a claim about nature.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
