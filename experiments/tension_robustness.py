"""v1.80 - Is the v1.79 birefringence-vs-gravity tension robust to its toy mappings?

The v1.79 result -- anomaly inflow + unscreened sub-mm gravity cap cosmic
birefringence at beta_max ~ 0.09 deg, 2.8 sigma below the measured 0.34 +/- 0.09 --
hinges on TWO order-of-magnitude toy numbers:
  - rho_inflow: the anomaly-inflow strength (g_R2_parity^2 + 2 g_R3_parity^2 <=
    rho * g_4 * g_R2), plausible [0.03, 0.12];
  - kappa_beta: the parity-coupling -> birefringence-angle map (beta = kappa *
    g_R2_parity), plausible ~[2.0, 5.0] deg/unit (an O(0.1) coupling -> 0.2-0.5 deg).

Key factorization: beta_max = kappa * g_R2_parity_max(rho). g_R2_parity_max (the
largest parity coupling a consistent, sub-mm-safe EFT can carry) depends on rho but
NOT on kappa. So we compute g_R2_parity_max once per rho (parallel sampling), then
the whole (rho, kappa) plane is a multiplication.

Run on Vulcan (16 cores):  python experiments/tension_robustness.py
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
# box focused where the anomaly-inflow ceiling is highest (large g_4, g_R2<=submm)
BLO = np.array([0.30, 0.10, 0.20, 0.045, 0.0, 0.04, 0.0, -0.015])
BHI = np.array([0.60, 0.50, 0.60, 0.063, 0.045, 0.30, 0.055, 0.015])

BETA_MEAS, BETA_SIG = 0.34, 0.09
RHOS = np.round(np.linspace(0.03, 0.12, 10), 4)
KAPPAS = np.round(np.linspace(2.0, 5.0, 13), 3)


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _maxgp_task(arg):
    """For one (rho, seed): sample n points against theory+submm with anomaly_rho
    = rho, return the max feasible g_R2_parity."""
    rho, seed, n = arg
    stack = build_stack(prefactors={"anomaly_rho": rho}, bnossw_mean="geometric",
                        rfc_form="convex_hull", include_data=True)
    rng = np.random.default_rng(seed)
    X = BLO + (BHI - BLO) * rng.random((n, len(COEFFS)))
    best = -np.inf
    for i in range(n):
        if X[i, 6] <= best:
            continue
        th = _theory(X[i])
        if all(c.evaluate(th).satisfied for c in stack):
            best = X[i, 6]
    return (rho, best)


def main():
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks_per_rho = 16
    per = 220_000
    tasks = [(float(rho), 100 + ri * 100 + k, per)
             for ri, rho in enumerate(RHOS) for k in range(chunks_per_rho)]

    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_maxgp_task, tasks)

    gp_max = {float(rho): -np.inf for rho in RHOS}
    for rho, gp in res:
        if gp > gp_max[rho]:
            gp_max[rho] = gp
    gp_arr = np.array([gp_max[float(r)] for r in RHOS])
    # graceful fill for any sampling miss (-inf): interpolate from found values
    # (gp_max is monotone increasing in rho, so linear fill is conservative)
    found = np.isfinite(gp_arr)
    if not found.all() and found.sum() >= 2:
        gp_arr = np.interp(RHOS, RHOS[found], gp_arr[found])

    # tension grid: rows=kappa, cols=rho
    T = np.zeros((len(KAPPAS), len(RHOS)))
    for ki, kap in enumerate(KAPPAS):
        for ri, rho in enumerate(RHOS):
            beta_max = kap * gp_arr[ri]
            T[ki, ri] = (BETA_MEAS - beta_max) / BETA_SIG

    frac_gt2 = float(np.mean(T > 2.0))
    frac_gt1 = float(np.mean(T > 1.0))
    frac_lt1 = float(np.mean(T < 1.0))
    any_reach = bool(np.any(T < 1.0))
    beta_max_grid = np.outer(KAPPAS, gp_arr)

    # canonical point
    rho_c, kap_c = 0.06, 3.4
    gp_c = float(np.interp(rho_c, RHOS, gp_arr))
    beta_c = kap_c * gp_c
    tension_c = (BETA_MEAS - beta_c) / BETA_SIG

    # ---- heatmap ----
    fig, ax = plt.subplots(figsize=(9, 6.5))
    im = ax.imshow(T, origin="lower", aspect="auto", cmap="RdBu_r",
                   vmin=-1, vmax=4,
                   extent=[RHOS[0], RHOS[-1], KAPPAS[0], KAPPAS[-1]])
    cs = ax.contour(RHOS, KAPPAS, T, levels=[1, 2, 3], colors="black",
                    linewidths=1.2)
    ax.clabel(cs, fmt=lambda v: f"{int(v)} sigma", fontsize=9)
    fig.colorbar(im, ax=ax, label="tension (sigma): (0.34 - beta_max)/0.09")
    ax.scatter([rho_c], [kap_c], s=140, marker="*", color="yellow",
               edgecolor="black", zorder=5,
               label=f"canonical (rho=0.06, kappa=3.4): {tension_c:.1f} sigma")
    ax.set_xlabel("rho_inflow (anomaly-inflow strength)")
    ax.set_ylabel("kappa_beta (deg per unit g_R2_parity)")
    ax.set_title("v1.80  Is the birefringence-vs-unscreened-gravity tension robust?\n"
                 f"unscreened in >2sigma tension over {frac_gt2*100:.0f}% of the "
                 f"plausible (rho,kappa) box", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    png = "/tmp/tension_robustness.png"
    fig.savefig(png, dpi=140)

    summary = {
        "rho_range": [float(RHOS[0]), float(RHOS[-1])],
        "kappa_range": [float(KAPPAS[0]), float(KAPPAS[-1])],
        "g_R2_parity_max_per_rho": {float(r): round(float(g), 4)
                                    for r, g in zip(RHOS, gp_arr)},
        "beta_max_deg_range_over_box": [round(float(beta_max_grid.min()), 3),
                                        round(float(beta_max_grid.max()), 3)],
        "tension_sigma_range": [round(float(T.min()), 2), round(float(T.max()), 2)],
        "fraction_box_tension_gt_2sigma": round(frac_gt2, 3),
        "fraction_box_tension_gt_1sigma": round(frac_gt1, 3),
        "fraction_box_reaches_measured_lt_1sigma": round(frac_lt1, 3),
        "any_corner_reaches_measured_beta": any_reach,
        "canonical_tension_sigma": round(tension_c, 2),
        "verdict": ("ROBUST: unscreened in tension across the whole plausible box"
                    if not any_reach else
                    "MAPPING-DEPENDENT: some corners reach the measured beta"),
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
