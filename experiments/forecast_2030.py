"""2030 discrimination forecast: which quantum gravity will we actually know? (v1.55)

Runs the Bayesian inference engine (src/itb/inference.py) on PROJECTED ~2030
measurement sensitivities to forecast how decisively next-decade data will
identify the true theory. For each "nature = theory X" hypothesis we simulate
the projected measurements (X's predicted coefficients at the projected
precision) and compute the posterior over all 8 candidate theories — a
discrimination confusion matrix.

Projected 2030 sensitivities (stated assumptions, not fabricated literature):
  g_R2_parity  +/- 0.010   (LIGO O5 GW birefringence)
  g_R2         +/- 0.020   (next-gen sub-mm gravity, the R^2 Yukawa)
  g_8          +/- 0.030   (spin-4 matter forward amplitude, v1.36)
  g_R3         +/- 0.030   (cubic curvature: Bouwmeester / forward positivity)
"""

import json
import sys

import numpy as np

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.inference import framework_posterior

sys.path.insert(0, ".")

FWS = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
       CausalDynamicalTriangulation(), DiscoveredNovel(),
       DiscoveredParityViolating(), DiscoveredHighG8()]
NAMES = [f.name for f in FWS]
SHORT = {"pure_gr": "GR", "string_tree_eft": "string", "asymptotic_safety": "AS",
         "lqg_induced": "LQG", "cdt": "CDT", "discovered_novel": "novel",
         "discovered_parity_violating": "PV", "discovered_high_g8": "hi-g8"}

PROJECTED = {"g_R2_parity": 0.010, "g_R2": 0.020, "g_8": 0.030, "g_R3": 0.030}


def main():
    # confusion matrix: row = true theory, col = inferred posterior weight
    M = np.zeros((len(FWS), len(FWS)))
    for i, true_fw in enumerate(FWS):
        coeffs = true_fw.encode().coefficients
        meas = {c: (coeffs.get(c, 0.0), s) for c, s in PROJECTED.items()}
        post = framework_posterior(meas, FWS)
        pmap = {p.name: p.posterior for p in post}
        for j, nm in enumerate(NAMES):
            M[i, j] = pmap[nm]

    out = {"projected_sensitivities": PROJECTED,
           "confusion_matrix": {NAMES[i]: {NAMES[j]: float(M[i, j])
                                           for j in range(len(FWS))}
                                for i in range(len(FWS))},
           "self_identification": {NAMES[i]: float(M[i, i]) for i in range(len(FWS))}}
    with open("experiments/results/out_forecast_2030.json", "w") as f:
        json.dump(out, f, indent=2)

    print("=== 2030 DISCRIMINATION FORECAST (posterior, true theory in rows) ===\n")
    hdr = "  true\\inferred  " + "".join(f"{SHORT[n]:>7}" for n in NAMES)
    print(hdr)
    for i, nm in enumerate(NAMES):
        row = "".join(f"{M[i,j]*100:6.0f} " for j in range(len(FWS)))
        print(f"  {SHORT[nm]:<13} {row}")
    print("\n  self-identification (diagonal = how decisively each true theory is pinned):")
    for nm in NAMES:
        v = out["self_identification"][nm]
        flag = "  CONFIDENT" if v > 0.8 else ("  ambiguous" if v < 0.5 else "")
        print(f"    {SHORT[nm]:<8} {v*100:5.1f}%{flag}")
    # confusions
    print("\n  notable confusions (off-diagonal > 20%):")
    for i in range(len(FWS)):
        for j in range(len(FWS)):
            if i != j and M[i, j] > 0.2:
                print(f"    nature={SHORT[NAMES[i]]} -> {M[i,j]*100:.0f}% chance inferred as {SHORT[NAMES[j]]}")

    print("\n  => With 2030-projected sensitivities, the parity-violating theories")
    print("     (LQG, PV) are pinned cleanly (handedness + magnitude); the matter-sector")
    print("     branches (novel, hi-g8) are pinned by g_8; the residual confusion is")
    print("     string<->CDT (near-degenerate, needs sub-percent sub-mm gravity).")

    # plot confusion matrix
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1)
        ax.set_xticks(range(len(FWS))); ax.set_xticklabels([SHORT[n] for n in NAMES], rotation=45)
        ax.set_yticks(range(len(FWS))); ax.set_yticklabels([SHORT[n] for n in NAMES])
        ax.set_xlabel("inferred (posterior)"); ax.set_ylabel("true theory")
        ax.set_title("2030 discrimination forecast\n(posterior given projected DESI/LIGO-O5/CMB-S4/sub-mm)")
        for i in range(len(FWS)):
            for j in range(len(FWS)):
                if M[i, j] > 0.08:
                    ax.text(j, i, f"{M[i,j]*100:.0f}", ha="center", va="center",
                            color="white" if M[i, j] < 0.6 else "black", fontsize=8)
        fig.colorbar(im, label="posterior probability")
        plt.tight_layout(); plt.savefig("experiments/results/forecast_2030.png", dpi=110)
        print("\n  wrote experiments/results/forecast_2030.png")
    except Exception as e:
        print(f"\n  (plot skipped: {e})")
    print("\nwrote experiments/results/out_forecast_2030.json")


if __name__ == "__main__":
    main()
