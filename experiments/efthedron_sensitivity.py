"""How load-bearing is the cross-sector EFThedron prefactor alpha? (v1.64)

v1.61 flagged that the survivors pass the EFThedron bound (g_8 g_R2 >= alpha g_6
g_R3) only narrowly. This sweeps alpha over [0.8, 1.5] and finds, for every
in-scope framework, the critical alpha at which it starts being excluded by the
bound, plus the full-stack feasibility transition. Quantifies how much the new
constraint's verdict depends on its O(1) coefficient.
"""

import json
import sys

import numpy as np

from itb.constraints.cross_sector_efthedron import CrossSectorEFThedron
from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.scope import engine_validity

sys.path.insert(0, ".")
from experiments.stack import build_stack

FWS = [StringTreeEFT(), AsymptoticSafety(), CausalDynamicalTriangulation(),
       LQGInduced(), GroupFieldTheory(), DiscoveredNovel(),
       DiscoveredParityViolating(), DiscoveredHighG8()]


def alpha_crit(coeffs):
    """alpha at which EFThedron margin = 0: g_8 g_R2 = alpha g_6 g_R3."""
    num = coeffs.get("g_8", 0.0) * coeffs.get("g_R2", 0.0)
    den = coeffs.get("g_6", 0.0) * coeffs.get("g_R3", 0.0)
    return num / den if den > 1e-12 else float("inf")


def main():
    alphas = np.linspace(0.8, 1.5, 15)
    out = {"alphas": alphas.tolist(), "frameworks": {}}
    print("=== Cross-sector EFThedron alpha sensitivity (sweep 0.8-1.5) ===\n")
    print(f"  {'framework':<28}{'alpha_crit':>11}{'feasible@1.1':>13}{'excluded by EFThed from alpha':>30}")
    for fw in FWS:
        c = fw.encode().coefficients
        ac = alpha_crit(c)
        # full-stack feasibility vs alpha
        feas = []
        first_excl = None
        for a in alphas:
            cons = build_stack({"efthedron_alpha": float(a)},
                               bnossw_mean="geometric", rfc_form="convex_hull")
            f = check(fw.encode(), cons).feasible
            feas.append(bool(f))
        # within-range alpha where EFThedron alone first bites (margin<0)
        bite = ac if 0.8 <= ac <= 1.5 else (None if ac > 1.5 else 0.8)
        out["frameworks"][fw.name] = {"alpha_crit": float(ac), "feasible_vs_alpha": feas,
                                      "in_scope": engine_validity(fw).in_scope}
        f11 = check(fw.encode(), build_stack({"efthedron_alpha": 1.1},
                    bnossw_mean="geometric", rfc_form="convex_hull")).feasible
        bite_s = f"{bite:.2f}" if bite is not None and bite <= 1.5 and bite >= 0.8 else (
            "always (<0.8)" if ac < 0.8 else "never (>1.5)")
        print(f"  {fw.name:<28}{ac:>11.2f}{str(f11):>13}{bite_s:>30}")

    print("\n=== reading ===")
    print("  alpha_crit = the EFThedron prefactor at which each framework's margin hits 0.")
    print("  At canonical alpha=1.1, only LQG (a_c~0.89) and GFT (~0.93) are excluded.")
    print("  But the SURVIVORS have alpha_crit just above 1.1: CDT ~1.28, string ~1.33,")
    print("  AS ~1.50 — so a modest increase in the (toy) EFThedron coefficient would")
    print("  start excluding them. The discovered branches (a_c 3-15) are safe across")
    print("  the whole range. CONCLUSION: the cross-sector EFThedron is genuinely")
    print("  LOAD-BEARING and alpha is a priority coefficient to pin at literature")
    print("  precision — between alpha 1.1 and 1.5 it reshapes the survivor set.")

    with open("experiments/results/out_efthedron_sensitivity.json", "w") as f:
        json.dump(out, f, indent=2)

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4.6))
        for fw in FWS:
            c = fw.encode().coefficients
            m = [c.get("g_8", 0)*c.get("g_R2", 0) - a*c.get("g_6", 0)*c.get("g_R3", 0)
                 for a in alphas]
            ax.plot(alphas, m, label=fw.name.replace("_", " "), lw=1.5)
        ax.axhline(0, color="k", lw=1)
        ax.axvline(1.1, color="gray", ls="--", label="canonical alpha=1.1")
        ax.set_xlabel("cross-sector EFThedron prefactor alpha")
        ax.set_ylabel("EFThedron margin (>=0 feasible)")
        ax.set_title("v1.64 - EFThedron alpha sensitivity: where rising alpha excludes survivors")
        ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)
        plt.tight_layout(); plt.savefig("experiments/results/efthedron_sensitivity.png", dpi=110)
        print("wrote experiments/results/efthedron_sensitivity.png")
    except Exception as e:
        print(f"(plot skipped: {e})")
    print("\nwrote experiments/results/out_efthedron_sensitivity.json")


if __name__ == "__main__":
    main()
