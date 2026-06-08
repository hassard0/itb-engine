"""How much did the v1.23-25 corrections change each framework's verdict? (v1.62)

Cross-checks all 11 frameworks' prefactor robustness on the ORIGINAL stack
(rfc_form="matter_product" — the miscast RFC; bnossw_mean="harmonic") vs the
CORRECTED stack (convex_hull RFC + geometric BNOSSW). Quantifies how much the
realism corrections moved each verdict, and flags out-of-scope frameworks
(Horava-Lifshitz, causal sets) via src/itb/scope.py.
"""

import json
import sys

import numpy as np

from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.causal_set import CausalSet
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.horava_lifshitz import HoravaLifshitz
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.scope import engine_validity

sys.path.insert(0, ".")
from experiments.stack import PLAUSIBLE_RANGES, build_stack

FWS = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
       CausalDynamicalTriangulation(), GroupFieldTheory(), HoravaLifshitz(),
       CausalSet(), DiscoveredNovel(), DiscoveredParityViolating(),
       DiscoveredHighG8()]


def robustness(theory, rfc_form, bnossw_mean, n=1500, seed=3):
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    ok = 0
    for _ in range(n):
        pref = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs}
        cons = build_stack(pref, bnossw_mean=bnossw_mean, rfc_form=rfc_form)
        if check(theory, cons).feasible:
            ok += 1
    return ok / n


def main():
    out = {}
    print("=== Original vs corrected stack: per-framework robustness (%) ===\n")
    print(f"  {'framework':<28}{'ORIGINAL':>10}{'CORRECTED':>11}{'shift':>8}  scope")
    for fw in FWS:
        t = fw.encode()
        orig = robustness(t, "matter_product", "harmonic")
        corr = robustness(t, "convex_hull", "geometric")
        sc = engine_validity(fw)
        out[fw.name] = {"original": orig, "corrected": corr,
                        "shift": corr - orig, "in_scope": sc.in_scope}
        print(f"  {fw.name:<28}{orig*100:>9.0f}%{corr*100:>10.0f}%{(corr-orig)*100:>+7.0f}%"
              f"  {'in' if sc.in_scope else 'OUT'}")

    print("\n=== reading ===")
    print("  The ORIGINAL stack's miscast RFC (g_4*g_6 - g_R2 - g*g_R2^2) excludes")
    print("  essentially every framework for any gamma>0 (the v1.23 F1 artifact), so all")
    print("  read ~0% — a uniform false verdict. The CORRECTED stack reveals the true,")
    print("  spread-out robustness. The 'shift' column is how much each verdict was")
    print("  distorted by the artifacts: the corrections did not tweak the picture, they")
    print("  CREATED it — without them the engine excluded everything indiscriminately.")
    print("  (Horava-Lifshitz and causal sets are OUT OF SCOPE; their numbers are not")
    print("   meaningful regardless of stack — see v1.59.)")

    with open("experiments/results/out_original_vs_corrected.json", "w") as f:
        json.dump(out, f, indent=2)

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        names = [f.name.replace("_", " ") for f in FWS]
        orig = [out[f.name]["original"]*100 for f in FWS]
        corr = [out[f.name]["corrected"]*100 for f in FWS]
        x = np.arange(len(FWS)); w = 0.4
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.bar(x - w/2, orig, w, label="original stack (miscast RFC)", color="C3", alpha=0.8)
        ax.bar(x + w/2, corr, w, label="corrected stack", color="C2", alpha=0.8)
        for i, fw in enumerate(FWS):
            if not out[fw.name]["in_scope"]:
                ax.text(i, 2, "out of\nscope", ha="center", fontsize=7, color="gray")
        ax.set_xticks(x); ax.set_xticklabels(names, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("prefactor robustness [%]")
        ax.set_title("v1.62 — original vs corrected stack: the realism corrections CREATED the picture")
        ax.legend()
        plt.tight_layout(); plt.savefig("experiments/results/original_vs_corrected.png", dpi=110)
        print("wrote experiments/results/original_vs_corrected.png")
    except Exception as e:
        print(f"(plot skipped: {e})")
    print("\nwrote experiments/results/out_original_vs_corrected.json")


if __name__ == "__main__":
    main()
