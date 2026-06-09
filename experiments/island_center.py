"""v1.74 - The center of the consistent-QG island: the most robustly-consistent EFT.

We find the CHEBYSHEV / deepest-interior point of the island: the coefficient
vector that MAXIMIZES THE MINIMUM signed-distance margin across all 36
constraints - the point furthest inside every wall simultaneously. Its achieved
min-margin is the island's "inradius" (how much slack the most robust EFT has);
the constraints tight there are the "active set" that pins the center.

Metric: we maximize min_i signed_distance_margin_i (the margin normalized by the
constraint-gradient norm), so "deepest" is in a gradient-consistent metric. The
raw-margin choice would weight constraints by their arbitrary coefficient scale;
the signed-distance choice is the defensible one. The ACTIVE SET (which walls are
tight) is the robust, normalization-light content.

Parity-even slice (g_R2_parity = g_R3_parity = 0), 6 free coeffs.

Run on Vulcan:  python experiments/island_center.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.predict import FRAMEWORKS
from itb.holographic_ac import gC_from_gR2, lambda_GB, ac_ratio, eta_over_s_kss
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C"]
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
HI = np.array([1.0, 1.0, 1.0, 0.5, 0.5, 0.7])

HBARC_eV_m = 1.973e-7
E_LAMBDA_DE = 2.4e-3

_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_NAMES = [c.name for c in _STACK]

# Two-sided narrow-BAND (equality-like) constraints define a thin slab the island
# must live IN; their signed-distance margin is capped at the band half-width, so
# they would trivially pin any max-min center. The Chebyshev "deepest inside the
# walls" notion is about the one-sided positivity/causality/swampland inequalities.
# We require the bands SATISFIED (feasibility) but exclude them from the max-min
# objective. (anomaly matching slack 0.02; anomaly cancellation tolerance 0.2.)
_BANDS = {"t_hooft_anomaly_matching", "anomaly_cancellation"}
_WALL_IDX = [i for i, n in enumerate(_NAMES) if n not in _BANDS]


def _theory(x):
    d = {k: float(v) for k, v in zip(COEFFS, x)}
    d["g_R2_parity"] = 0.0
    d["g_R3_parity"] = 0.0
    return Theory(coefficients=d)


def _margins(x):
    """signed-distance margins for all constraints at x."""
    th = _theory(x)
    return np.array([c.evaluate(th).signed_distance_margin for c in _STACK])


def _neg_min_margin(x):
    if np.any(x < LO - 1e-9) or np.any(x > HI + 1e-9):
        return 1e6                       # box penalty
    m = _margins(x)
    # require the equality-like bands satisfied; if violated, penalize
    band_ok = all(_STACK[i].evaluate(_theory(x)).satisfied
                  for i, n in enumerate(_NAMES) if n in _BANDS)
    pen = 0.0 if band_ok else 1e3
    return -float(np.min(m[_WALL_IDX])) + pen


def main():
    # multi-start Nelder-Mead maximizing the min signed-distance margin
    rng = np.random.default_rng(7)
    starts = [np.array([0.44, 0.29, 0.39, 0.18, 0.08, 0.28])]   # v1.73 centroid
    for _ in range(40):
        starts.append(LO + (HI - LO) * rng.random(len(COEFFS)))

    best_x, best_val = None, -np.inf
    for s in starts:
        res = minimize(_neg_min_margin, s, method="Nelder-Mead",
                       options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
        val = -res.fun
        if val > best_val and np.all(res.x >= LO - 1e-6) and np.all(res.x <= HI + 1e-6):
            best_val, best_x = val, np.clip(res.x, LO, HI)

    x = best_x
    m = _margins(x)
    wall_margins = m[_WALL_IDX]
    inradius = float(np.min(wall_margins))        # inradius w.r.t. the one-sided walls
    th = _theory(x)
    full = [(c.name, c.evaluate(th)) for c in _STACK]
    all_satisfied = all(r.satisfied for _, r in full)
    band_margins = {_NAMES[i]: round(float(m[i]), 4)
                    for i, n in enumerate(_NAMES) if n in _BANDS}
    # active set: WALLS within a small band of the wall-inradius (the tight walls)
    band = 0.02
    active = sorted([(_NAMES[i], round(float(m[i]), 4)) for i in _WALL_IDX
                     if m[i] <= inradius + band], key=lambda kv: kv[1])

    # center coefficients
    center = {k: round(float(v), 4) for k, v in zip(COEFFS, x)}

    # central prediction: observables at the center
    gR2 = float(x[3]); gC = float(x[5])
    lam = lambda_GB(gR2)
    a_over_c_direct = gR2 / gC if gC > 0 else None
    obs = {
        "a_over_c_direct (g_R2/g_C)": round(a_over_c_direct, 4) if a_over_c_direct else None,
        "a_over_c_portrait (lambda=0.22 g_R2)": round(ac_ratio(lam), 4),
        "eta_over_s_KSS (1-4 lambda)": round(eta_over_s_kss(lam), 4),
        "lambda_GB": round(lam, 4),
        "submm_yukawa_range_um": round(float(np.sqrt(6 * gR2) * HBARC_eV_m
                                              / E_LAMBDA_DE * 1e6), 2) if gR2 > 0 else None,
    }

    # distance from center to each framework (raw Euclidean, parity-even coords,
    # framework g_C from the GB portrait)
    fw_rows = []
    for name, fw in FRAMEWORKS.items():
        c = fw.encode().coefficients
        g = c.get("g_R2", 0.0)
        vec = np.array([c.get("g_4", 0.0), c.get("g_6", 0.0), c.get("g_8", 0.0),
                        g, c.get("g_R3", 0.0), gC_from_gR2(g)])
        feas = all(cc.evaluate(_theory(vec)).satisfied for cc in _STACK)
        # use the framework's OWN g_C only for the wedge; distance uses portrait
        fw_rows.append({"framework": name,
                        "dist_to_center": round(float(np.linalg.norm(vec - x)), 3),
                        "feasible": bool(feas)})
    fw_rows.sort(key=lambda r: r["dist_to_center"])

    # ---- figure: per-constraint margins at the center, active set highlighted ----
    order = np.argsort(m)

    def _bar_color(i):
        if _NAMES[i] in _BANDS:
            return "#ff7f0e"                          # equality-like band
        if m[i] <= inradius + band:
            return "#d62728"                          # active wall
        return "#1f77b4"

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [_bar_color(i) for i in order]
    ax.barh([_NAMES[i] for i in order], [m[i] for i in order], color=colors)
    ax.axvline(inradius, color="#d62728", ls="--", lw=1.5,
               label=f"wall inradius (min wall margin) = {inradius:.3f}")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("signed-distance margin at the island center", fontsize=11)
    ax.set_title("v1.74  The most robustly-consistent EFT: per-constraint slack at "
                 "the island center\n(red = active set pinning the center)", fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.tick_params(axis="y", labelsize=6.5)
    fig.tight_layout()
    png = "/tmp/island_center.png"
    fig.savefig(png, dpi=140)

    summary = {
        "metric": "max-min signed_distance_margin (Chebyshev center, gradient-normalized)",
        "box": {k: [float(LO[i]), float(HI[i])] for i, k in enumerate(COEFFS)},
        "center_coefficients": center,
        "inradius_walls_min_margin": round(inradius, 4),
        "band_margins (equality-like, satisfied not maximized)": band_margins,
        "all_constraints_satisfied": bool(all_satisfied),
        "active_set_walls": active,
        "central_prediction_observables": obs,
        "frameworks_by_distance_to_center": fw_rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
