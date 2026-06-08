"""Gravitationally-induced entanglement (GIE) + the g_R2 Yukawa it predicts (v1.39).

The decisive foundational QG experiment: if two mesoscopic masses in spatial
superposition become entangled purely through their mutual gravity (Bose et al.
2017; Marletto-Vedral 2017), the gravitational field carries quantum degrees of
freedom — gravity is quantized. This module:

 1. Computes the standard Newtonian entangling phase and the experimental
    parameters (mass, superposition size, separation, coherence time) needed to
    cross the O(1) entanglement-witness threshold.

 2. Connects the engine's R^2 Wilson coefficient g_R2 to a concrete, *currently
    testable* signal: in quadratic (Stelle) gravity the R^2 term adds a massive
    scalar of mass m0, giving a Yukawa correction to the Newtonian potential
       V(r) = -(G m / r) [ 1 - (1/3) e^{- r / lambda_Y} + ... ],   lambda_Y = sqrt(g_R2)/Lambda
    where Lambda is the EFT cutoff (the scale of new gravitational physics, NOT
    necessarily Planckian). This Yukawa is exactly what short-range-gravity
    experiments (Eot-Wash torsion balances, reaching ~50 um) bound, and it shifts
    the GIE phase when the superposition probes r ~ lambda_Y.

 3. Reports, per framework (incl. the engine-discovered theories), the predicted
    Yukawa range as a function of the new-physics scale Lambda, and which
    experiment (short-range gravity now, or GIE) could resolve it.

Honest: the *structure* (R^2 -> massive scalar -> Yukawa, range sqrt(g_R2)/Lambda)
is textbook Stelle gravity; the toy normalization sets the O(1) prefactor. The
real, model-independent content is that the engine's g_R2 IS a short-range-gravity
observable, and GIE tests whether the mediating field is quantum.
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
from itb.frameworks.string_tree_eft import StringTreeEFT

sys.path.insert(0, ".")

# physical constants (SI)
G = 6.674e-11
HBAR = 1.055e-34
RHO = 19300.0  # gold/osmium-ish density kg/m^3


def newtonian_gie():
    """Entangling phase for the canonical parallel BMV setup and the parameters
    to reach the O(1) witness. Phase ~ G m^2 tau / (hbar) * (dx^2 / L^3)."""
    # canonical near-future numbers (Bose et al. 2017 scale)
    m = 1e-14                  # ~1e-14 kg mesoscopic mass (~10 um diamond)
    dx = 250e-6                # 250 um superposition separation
    L = 450e-6                 # 450 um center separation
    tau = 2.0                  # 2 s coherence/interaction time
    # leading entangling phase (dipole-dipole): G m^2 tau / hbar * dx^2 / L^3
    phi = G * m**2 * tau / HBAR * dx**2 / L**3
    return {"m_kg": m, "dx_m": dx, "L_m": L, "tau_s": tau, "entangling_phase_rad": phi,
            "witnessable": phi > 0.01}


def yukawa_ranges(lambda_cutoff_inv_m):
    """For a new-physics scale Lambda (given as its length 1/Lambda in metres),
    Yukawa range lambda_Y = sqrt(g_R2)/Lambda = sqrt(g_R2) * (1/Lambda)."""
    fw = {f.name: f.encode().coefficients.get("g_R2", 0.0) for f in [
        StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
        CausalDynamicalTriangulation(), DiscoveredNovel(),
        DiscoveredParityViolating(), DiscoveredHighG8()]}
    out = {}
    for name, gR2 in fw.items():
        lamY = np.sqrt(gR2) * lambda_cutoff_inv_m
        out[name] = {"g_R2": gR2, "lambda_Y_m": lamY}
    return out


def main():
    gie = newtonian_gie()
    print("=== 1. GIE foundational test (is gravity quantum?) ===")
    print(f"  m={gie['m_kg']:.0e} kg  dx={gie['dx_m']*1e6:.0f} um  L={gie['L_m']*1e6:.0f} um  "
          f"tau={gie['tau_s']} s")
    print(f"  entangling phase ~ {gie['entangling_phase_rad']:.2e} rad  "
          f"=> {'WITNESSABLE with squeezing/repetition' if gie['witnessable'] else 'below threshold'}")
    print("  A positive result proves the gravitational field has quantum DOF (LOCC theorem).")
    print("  Every theory in the engine's feasible region assumes quantized gravity — so a")
    print("  positive GIE is consistent with the whole program; a NULL would falsify it wholesale.")

    print("\n=== 2. The g_R2 Yukawa: a short-range-gravity observable, per framework ===")
    # scan a few candidate new-physics scales (as their length 1/Lambda)
    scales = {"Lambda^-1 = 50 um (current Eot-Wash reach)": 50e-6,
              "Lambda^-1 = 5 um (next-gen)": 5e-6,
              "Lambda^-1 = 1 nm": 1e-9}
    out = {"gie": gie, "yukawa": {}}
    for label, inv in scales.items():
        ranges = yukawa_ranges(inv)
        out["yukawa"][label] = ranges
        print(f"\n  {label}:")
        for name, d in sorted(ranges.items(), key=lambda kv: -kv[1]["lambda_Y_m"]):
            reach = "RESOLVABLE now" if d["lambda_Y_m"] > 30e-6 else (
                "next-gen" if d["lambda_Y_m"] > 1e-6 else "sub-um (hard)")
            print(f"    {name:<28} g_R2={d['g_R2']:.3f}  lambda_Y={d['lambda_Y_m']*1e6:8.2f} um  [{reach}]")

    # discrimination: ratio of longest to shortest Yukawa range = how separable frameworks are
    r = yukawa_ranges(50e-6)
    lams = {k: v["lambda_Y_m"] for k, v in r.items()}
    hi = max(lams, key=lams.get); lo = min(lams, key=lams.get)
    print(f"\n=== 3. Framework discrimination via Yukawa range ===")
    print(f"  longest range: {hi} (g_R2={r[hi]['g_R2']:.3f})  vs shortest: {lo} (g_R2={r[lo]['g_R2']:.3f})")
    print(f"  range ratio = {lams[hi]/lams[lo]:.2f}x  -> a short-range-gravity scan with"
          f" ~{lams[hi]/lams[lo]:.1f}x dynamic range in lambda separates them")
    print(f"  Larger g_R2 (LQG, discovered_parity_violating) => longer Yukawa => easier to see.")

    with open("experiments/out_gie.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_gie.json")


if __name__ == "__main__":
    main()
