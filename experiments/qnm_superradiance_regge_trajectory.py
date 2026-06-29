"""v2.246 - The superradiance spin-down endpoint: the Regge trajectory observed spins test.

v2.243/v2.244/v2.245 gave the superradiance condition, the growth-time exclusion, and the cloud's
direct GW signal. This cycle computes the SPIN-DOWN ENDPOINT -- the physical mechanism behind the
bound and the line that observed black-hole spins are actually compared against.

Superradiance transfers the hole's angular momentum to the boson cloud until the instability
saturates, i.e. until the horizon angular velocity drops to the boson frequency: Omega_H(a*_f) =
mu / m. For a boson of gravitational coupling alpha = M mu and the dominant m=1 level this is

    Omega_H(a*_f) = alpha ,

so a*_f(alpha) is the MAXIMUM spin a black hole can retain in the presence of that boson. A hole
observed with a* > a*_f(alpha) could not have kept its spin -- the boson would have spun it down --
so it EXCLUDES that boson. The curve a*_f(alpha) is the "Regge trajectory": observed high-spin black
holes sit above it for a band of alpha, carving the gaps that constrain ultralight bosons.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scipy.optimize import brentq

VERSION = "v2.246"
DEFAULT_OUT = Path("experiments/results/v2.246/qnm_superradiance_regge_trajectory.json")


def omega_h(astar: float) -> float:
    return astar / (2 * (1 + math.sqrt(1 - astar**2)))


def a_final(alpha: float, m: int = 1) -> float:
    """Spin-down endpoint: solve Omega_H(a*_f) = alpha/m for the max retained spin."""
    target = alpha / m
    if target >= 0.5:                      # even extremal Omega_H=1/2 cannot superradiate
        return 1.0
    return float(brentq(lambda a: omega_h(a) - target, 1e-8, 1 - 1e-9))


def run() -> dict:
    grid = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4]
    traj = [{"alpha": a, "a_final_max_spin": a_final(a)} for a in grid]
    # spin extracted from a near-extremal (a*=0.99) hole
    a_init = 0.99
    extraction = [{"alpha": a, "delta_a_star": a_init - a_final(a)} for a in grid]
    # observed high-spin systems -> which alpha they exclude (alpha < Omega_H(a*_obs))
    observed = [
        {"system": "Cygnus X-1 (a* ~ 0.95)", "a_star": 0.95},
        {"system": "GRS 1915+105 (a* ~ 0.98)", "a_star": 0.98},
        {"system": "M87* (a* ~ 0.9, EHT-favoured)", "a_star": 0.9},
    ]
    for o in observed:
        o["excludes_alpha_below"] = omega_h(o["a_star"])
    return {
        "version": VERSION,
        "method": ("spin-down saturation Omega_H(a*_f) = alpha (m=1) -> the maximum retained spin "
                   "a_final(alpha); observed a* > a_final excludes the boson; M=1, G=c=1"),
        "regge_trajectory": traj,
        "spin_extracted_from_near_extremal": extraction,
        "observed_high_spin_systems": observed,
        "consistency_check_Omega_H_at_a_final": omega_h(a_final(0.1)),  # == 0.1
        "finding": (
            "The Regge trajectory a_final(alpha) is the maximum spin a black hole keeps in the "
            "presence of a boson of coupling alpha: Omega_H(a_final) = alpha. A boson alpha=0.1 spins "
            f"a near-extremal (a*=0.99) hole down to a*={a_final(0.1):.3f} (extracting "
            f"Delta a*={0.99 - a_final(0.1):.2f} of spin); alpha=0.3 only down to "
            f"a*={a_final(0.3):.3f}. So a measured high spin EXCLUDES every boson with "
            "alpha < Omega_H(a*_obs): the well-measured spins of Cygnus X-1 (a*~0.95) and GRS "
            f"1915+105 (a*~0.98) exclude bosons up to alpha ~ {omega_h(0.95):.2f}-{omega_h(0.98):.2f}, "
            "and the EHT-favoured high spin of M87* extends the same logic to ~1e-21 eV bosons. The "
            "observed black holes sitting ABOVE the Regge trajectory are the actual data that turn "
            "superradiance into an ultralight-boson constraint -- the spin-extraction endpoint "
            "completing the v2.243-v2.245 thread (condition -> exclusion -> GW signal -> spin gaps)."
        ),
        "honest_scope": (
            "Exact-Kerr saturation condition Omega_H(a*_f) = alpha (verified: Omega_H(a_final(0.1)) "
            "= 0.1), the EXACT endpoint of an idealized adiabatic spin-down. The real Regge boundary "
            "also requires the growth to complete within the BH age (the v2.244 timescale) and folds "
            "in the measured spin POSTERIORS and their systematics (X-ray continuum/iron-line vs EHT "
            "methods differ); the cloud also re-deposits some angular momentum via GW emission. m=1 "
            "dominant level only (higher m saturate at higher spin). Order-of-magnitude reconstruction "
            "of a real BSM probe, not a published exclusion. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Arvanitaki & Dubovsky, PRD 83 (2011) 044026 -- Regge trajectories / spin gaps",
            "Brito, Cardoso, Pani, Lect. Notes Phys. 906 (2015) -- superradiance review",
            "Stott & Marsh, PRD 98 (2018) 083006 -- BH-spin bounds on ultralight bosons",
            "this repo: v2.243-v2.245 (superradiance condition / exclusion / GW signal)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("alpha   a_final (max retained spin)")
    for t in res["regge_trajectory"]:
        print(f"  {t['alpha']:.2f}    {t['a_final_max_spin']:.4f}")
    print("\nobserved high-spin systems -> exclude bosons with alpha below:")
    for o in res["observed_high_spin_systems"]:
        print(f"  {o['system']:34s} alpha < {o['excludes_alpha_below']:.3f}")
    print(f"\ncheck Omega_H(a_final(0.1)) = {res['consistency_check_Omega_H_at_a_final']:.5f} (=0.1)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
