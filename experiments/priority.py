"""Experiment-priority re-ranking on the corrected stack (v1.29).

The engine's headline real-world output is: which experiment, run at its forecast
precision, would carve out the most currently-allowed theory space? The published
v1.19 ranking was computed on the *pre-audit* stack (discredited RFC, harmonic
BNOSSW). This recomputes it on the corrected v1.27 stack (convex-hull RFC,
geometric BNOSSW, forward positivity, matter s^3) and adds the two experiments
v1.27 invented (precision g_8; cubic gravitational parity g_R3_parity).

Two 2-D planes are swept so every candidate observable varies on some axis:
  - (g_R2, g_R2_parity): graviton + leading-parity sector
  - (g_R3, g_R3_parity): cubic + cubic-parity sector (covers the invented exp.)
"""

import json
import sys
from pathlib import Path

from itb.experiment_priority import ExperimentForecast, rank_experiments

sys.path.insert(0, ".")
from experiments.stack import build_stack

EXPERIMENTS = [
    ExperimentForecast("LIGO_O5_graviton_mass", "g_R2", 0.0, 0.05),
    ExperimentForecast("LIGO_O5_birefringence", "g_R2_parity", 0.0, 0.005),
    ExperimentForecast("LIGO_O4_birefringence", "g_R2_parity", 0.0, 0.02),
    ExperimentForecast("Eot_Wash_equivalence", "g_R2", 0.0, 0.02),
    ExperimentForecast("CMB_S4_inflationary_EFT", "g_4", 0.5, 0.10),
    ExperimentForecast("CMB_S4_TIGHT", "g_4", 0.0, 0.03),
    ExperimentForecast("Lattice_QCD_g6_bound", "g_6", 0.4, 0.15),
    ExperimentForecast("Atomic_clock_Lorentz", "g_8", 0.4, 0.10),
    ExperimentForecast("Bouwmeester_collapse_test", "g_R2", 0.0, 0.005),
    ExperimentForecast("Bouwmeester_g_R3", "g_R3", 0.0, 0.005),
    # --- v1.27 invented experiments ---
    ExperimentForecast("INVENTED_precision_g8", "g_8", 0.0, 0.05),
    ExperimentForecast("INVENTED_cubic_parity_gR3p", "g_R3_parity", 0.0, 0.005),
]


def _rank(constraints, x, xr, y, yr, fixed):
    return rank_experiments(constraints, EXPERIMENTS, x_param=x, x_range=xr,
                            x_steps=21, y_param=y, y_range=yr, y_steps=21,
                            fixed_coefficients=fixed)


def main():
    corrected = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    fixed = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
             "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0}

    planes = {
        "g_R2 x g_R2_parity": (("g_R2", (0.0, 0.5)), ("g_R2_parity", (-0.2, 0.2)),
                               {k: v for k, v in fixed.items() if k not in ("g_R2", "g_R2_parity")}),
        "g_R3 x g_R3_parity": (("g_R3", (0.0, 0.5)), ("g_R3_parity", (-0.2, 0.2)),
                               {k: v for k, v in fixed.items() if k not in ("g_R3", "g_R3_parity")}),
    }

    out = {}
    for name, ((x, xr), (y, yr), fx) in planes.items():
        rankings = _rank(corrected, x, xr, y, yr, fx)
        out[name] = [{"label": r.label, "observable": r.coefficient_name,
                      "cells_excluded": r.cells_excluded,
                      "fraction": r.fraction_excluded,
                      "baseline": r.baseline_allowed} for r in rankings]
        print(f"\n=== plane {name}  (corrected stack) ===")
        print(f"  baseline allowed cells: {rankings[0].baseline_allowed}")
        for i, r in enumerate(rankings[:7], 1):
            star = "  <-- INVENTED" if r.label.startswith("INVENTED") else ""
            print(f"  {i}. {r.label:<26} ({r.coefficient_name:<12}) "
                  f"excludes {100*r.fraction_excluded:5.1f}%{star}")

    Path("experiments/results").mkdir(parents=True, exist_ok=True)
    with open("experiments/out_priority.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_priority.json")


if __name__ == "__main__":
    main()
