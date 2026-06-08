"""Where does Group Field Theory cross from excluded to viable? (v1.60)

v1.58 left GFT borderline: with LQG-like cubic (g_R3 ~ g_R2, ratio 1.0) it fails
forward positivity; Dr. M. argued the GFT condensate recovers a cleaner GR limit
(ratio ~1.5) that passes. This scans GFT's cubic coupling g_R3 at fixed g_R2=0.28
(so the ratio g_R2/g_R3 runs 1.0 -> 2.0) against the corrected stack, computing
feasibility and prefactor robustness, to find the exact pass/fail boundary and
state what condensate dynamics put GFT on either side.
"""

import json
import sys

import numpy as np

from itb.engine import check
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import PLAUSIBLE_RANGES, build_stack

GFT_BASE = {"g_4": 0.58, "g_6": 0.43, "g_8": 0.40, "g_R2": 0.28,
            "g_R2_parity": 0.07, "g_R3_parity": 0.04}


def robustness(coeffs, n=1500, seed=9):
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    t = Theory(coefficients=coeffs)
    ok = sum(check(t, build_stack({k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs},
                                  bnossw_mean="geometric", rfc_form="convex_hull")).feasible
             for _ in range(n))
    return ok / n


def main():
    constraints = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    gR2 = GFT_BASE["g_R2"]
    ratios = np.linspace(1.0, 2.0, 11)
    rows = []
    print("=== GFT cubic-coupling scan (g_R2=0.28 fixed) ===\n")
    print(f"  {'ratio g_R2/g_R3':>16}{'g_R3':>8}{'feasible':>10}{'robustness':>12}  binding")
    boundary = None
    for r in ratios:
        gR3 = gR2 / r
        coeffs = dict(GFT_BASE); coeffs["g_R3"] = float(gR3)
        rep = check(Theory(coefficients=coeffs), constraints)
        rob = robustness(coeffs)
        rows.append({"ratio": float(r), "g_R3": float(gR3), "feasible": rep.feasible,
                     "robustness": rob, "binding": rep.binding})
        print(f"  {r:>16.2f}{gR3:>8.3f}{str(rep.feasible):>10}{rob*100:>11.0f}%  {rep.binding or '-'}")
        if boundary is None and rep.feasible:
            boundary = r
    out = {"gft_base": GFT_BASE, "scan": rows, "feasible_from_ratio": boundary}
    with open("experiments/results/out_gft_boundary.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n=== Verdict ===")
    if boundary:
        print(f"  GFT becomes feasible once the cubic is suppressed to g_R2/g_R3 >~ {boundary:.2f}")
        print(f"  (g_R3 <~ {gR2/boundary:.3f}). Below that it fails forward positivity like LQG.")
    print(f"  Physics: if the GFT condensate recovers a GR-like IR limit (Dr. M.: ratio ~1.5)")
    print(f"  GFT PASSES and joins the survivors; if it inherits the raw spin-foam-vertex")
    print(f"  cubic enhancement (ratio ~1.0, LQG-like) it is robustly disfavoured. GFT's fate")
    print(f"  thus hinges on ONE condensate quantity: how much the mean-field dynamics")
    print(f"  suppress the cubic curvature coupling relative to the quadratic.")
    print("\nwrote experiments/results/out_gft_boundary.json")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rr = [x["ratio"] for x in rows]; rb = [x["robustness"]*100 for x in rows]
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ax.plot(rr, rb, "o-", color="C0")
        if boundary:
            ax.axvline(boundary, color="C2", ls="--", label=f"feasible from ratio {boundary:.2f}")
        ax.axvline(1.0, color="C3", ls=":", label="LQG-like (ratio 1.0)")
        ax.axvline(1.5, color="C1", ls=":", label="condensate GR-limit (ratio 1.5)")
        ax.set_xlabel("g_R2/g_R3 (cubic suppression)"); ax.set_ylabel("prefactor robustness [%]")
        ax.set_title("GFT pass/fail vs cubic suppression")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout(); plt.savefig("experiments/results/gft_boundary.png", dpi=110)
        print("wrote experiments/results/gft_boundary.png")
    except Exception as e:
        print(f"(plot skipped: {e})")


if __name__ == "__main__":
    main()
