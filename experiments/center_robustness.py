"""v1.75 - Error bars on the central prediction: does the most-robust EFT survive
the toy O(1) prefactor uncertainty?

The v1.74 island center (and its 93 um sub-mm Yukawa, a/c ~ 0.92, nearest-framework
= string tree-EFT) was computed with the CANONICAL O(1) constraint prefactors. The
realism program asks: which conclusions survive when we only know those prefactors
to within a factor of ~2? Here we draw N prefactor vectors from PLAUSIBLE_RANGES,
rebuild the stack for each, recompute the island center (the SAME optimizer,
island_center.find_center), and report the DISTRIBUTION of the center and its
central-prediction observables.

Run on Vulcan (16 cores):  python experiments/center_robustness.py [N]
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

from stack import build_stack, PLAUSIBLE_RANGES, CANONICAL
from island_center import find_center

YUKAWA_DE_TARGET = 93.0      # v1.44 dark-energy axion sub-mm scale
PKEYS = sorted(PLAUSIBLE_RANGES)


def _one_draw(arg):
    """Build the stack for one prefactor draw and find its island center."""
    idx, draw = arg
    stack = build_stack(prefactors=draw, bnossw_mean="geometric",
                        rfc_form="convex_hull")
    # fewer restarts per draw (centroid start is close); deterministic per idx
    r = find_center(stack, n_starts=12, seed=1000 + idx)
    obs = r["central_prediction_observables"]
    nearest = r["frameworks_by_distance_to_center"][0]
    return {
        "g_R2": r["x"][3], "g_C": r["x"][5],
        "inradius": r["inradius_walls_min_margin"],
        "a_over_c_direct": obs["a_over_c_direct"],
        "eta_over_s_KSS": obs["eta_over_s_KSS"],
        "submm_yukawa_range_um": obs["submm_yukawa_range_um"],
        "nearest_framework": nearest["framework"],
        "nearest_feasible": nearest["feasible"],
        "all_satisfied": r["all_constraints_satisfied"],
    }


def pct(a):
    a = np.array([v for v in a if v is not None], dtype=float)
    return {"median": round(float(np.median(a)), 4),
            "p16": round(float(np.percentile(a, 16)), 4),
            "p84": round(float(np.percentile(a, 84)), 4),
            "min": round(float(a.min()), 4), "max": round(float(a.max()), 4)}


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    rng = np.random.default_rng(20260608)
    draws = []
    for i in range(N):
        d = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in PKEYS}
        draws.append((i, d))

    ncpu = max(1, (os.cpu_count() or 4) - 1)
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_one_draw, draws)

    res = [r for r in res if r["all_satisfied"]]    # keep valid interior centers
    yuk = [r["submm_yukawa_range_um"] for r in res]
    ac = [r["a_over_c_direct"] for r in res]
    eta = [r["eta_over_s_KSS"] for r in res]
    inr = [r["inradius"] for r in res]
    gR2 = [r["g_R2"] for r in res]
    gC = [r["g_C"] for r in res]

    # nearest-framework frequency
    from collections import Counter
    near = Counter(r["nearest_framework"] for r in res)
    near_frac = {k: round(v / len(res), 3) for k, v in near.most_common()}
    string_frac = near_frac.get("string_tree_eft", 0.0)

    # does the 93um yukawa survive? fraction within +/-20% of 93
    yuk_arr = np.array(yuk)
    within20 = float(np.mean(np.abs(yuk_arr - YUKAWA_DE_TARGET) <= 0.2 * YUKAWA_DE_TARGET))

    # ---- figure ----
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.5))
    axes[0].hist(yuk, bins=30, color="#1f77b4", alpha=0.85)
    axes[0].axvline(YUKAWA_DE_TARGET, color="#d62728", ls="--", lw=2,
                    label="v1.44 dark-energy 93 um")
    axes[0].axvline(np.median(yuk), color="black", ls="-", lw=1.5, label="median")
    axes[0].set_xlabel("sub-mm Yukawa range (um)"); axes[0].set_ylabel("draws")
    axes[0].set_title("Central prediction: sub-mm Yukawa"); axes[0].legend(fontsize=8)

    axes[1].hist(ac, bins=30, color="#9467bd", alpha=0.85)
    axes[1].axvline(np.median(ac), color="black", ls="-", lw=1.5)
    axes[1].axvspan(1/3, 31/18, color="#cfe8cf", alpha=0.4, label="HM wedge")
    axes[1].set_xlabel("a/c (direct)"); axes[1].set_title("Central prediction: a/c")
    axes[1].legend(fontsize=8)

    axes[2].hist(eta, bins=30, color="#ff7f0e", alpha=0.85)
    axes[2].axvline(np.median(eta), color="black", ls="-", lw=1.5)
    axes[2].set_xlabel("eta/s (KSS units)"); axes[2].set_title("Central prediction: eta/s")

    items = list(near_frac.items())
    axes[3].barh([k for k, _ in items][::-1], [v for _, v in items][::-1],
                 color="#2ca02c")
    axes[3].set_xlabel("fraction of draws nearest")
    axes[3].set_title("Nearest framework to the center")
    fig.suptitle(f"v1.75  Central prediction under O(1) prefactor uncertainty "
                 f"({len(res)} draws from PLAUSIBLE_RANGES)", fontsize=11)
    fig.tight_layout()
    png = "/tmp/center_robustness.png"
    fig.savefig(png, dpi=140)

    summary = {
        "n_draws_valid": len(res), "n_requested": N,
        "prefactor_keys_varied": PKEYS,
        "submm_yukawa_range_um": pct(yuk),
        "submm_yukawa_target_um": YUKAWA_DE_TARGET,
        "yukawa_fraction_within_20pct_of_93um": round(within20, 3),
        "a_over_c_direct": pct(ac),
        "a_over_c_inside_HM_wedge_fraction": round(
            float(np.mean((np.array(ac) >= 1/3) & (np.array(ac) <= 31/18))), 3),
        "eta_over_s_KSS": pct(eta),
        "inradius": pct(inr),
        "g_R2": pct(gR2), "g_C": pct(gC),
        "nearest_framework_frequency": near_frac,
        "string_tree_eft_nearest_fraction": string_frac,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
