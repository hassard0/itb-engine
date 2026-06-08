"""The engine as a live inference machine: which theory does the data favour? (v1.52)

Runs the Bayesian framework-inference layer over the 8 candidate theories for a
sequence of measurement scenarios — current bounds and hypothetical near-future
results — showing how each measurement reshapes the posterior. This is the
engine's answer to "given what we measure, which quantum gravity survives?"
"""

import json
import sys

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

SCENARIOS = {
    "1. prior (no data)": {},
    "2. + GW birefringence null (LIGO O3: g_R2_parity = 0 +/- 0.05)":
        {"g_R2_parity": (0.0, 0.05)},
    "3. + sub-mm gravity finds Yukawa lambda~90um (g_R2 = 0.20 +/- 0.03)":
        {"g_R2_parity": (0.0, 0.05), "g_R2": (0.20, 0.03)},
    "4. INSTEAD: GW birefringence DETECTED (g_R2_parity = 0.09 +/- 0.02)":
        {"g_R2_parity": (0.09, 0.02)},
    "5. + matter scattering (g_8 = 0.05 +/- 0.03, the low-g8 novel branch)":
        {"g_R2_parity": (0.0, 0.05), "g_8": (0.05, 0.03)},
}


def main():
    out = {}
    for label, meas in SCENARIOS.items():
        post = framework_posterior(meas, FWS)
        out[label] = {p.name: round(p.posterior, 4) for p in post}
        print(f"\n=== {label} ===")
        for p in post:
            if p.posterior > 0.005:
                bar = "#" * int(round(p.posterior * 40))
                print(f"  {p.name:<28} {p.posterior*100:5.1f}%  {bar}")

    with open("experiments/results/out_inference.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\n=== reading ===")
    print("  The same engine, fed different measurements, returns different surviving")
    print("  theories. A GW-birefringence DETECTION (scenario 4) singles out the")
    print("  discovered parity-violating branch; a NULL (2) favours the parity-conserving")
    print("  frameworks; sub-mm Yukawa (3) and matter scattering (5) pick among those.")
    print("  This is the engine as a live measurement -> theory inference machine.")
    print("\nwrote experiments/results/out_inference.json")


if __name__ == "__main__":
    main()
