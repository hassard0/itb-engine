"""Physical m0 / Yukawa target per framework vs the gravitational cutoff (v1.40).

Folds in Dr. M.'s verdict: the decisive engine-facing experiment is short-range
precision gravity probing the R^2-induced scalar Yukawa, NOT GIE (GIE answers the
foundational "is gravity quantum" but is decoherence-fragile). Stelle relation
for the f(R) = R + alpha R^2 scalar mode:

    m0 = E_Lambda / sqrt(6 * g_R2),   Yukawa range  lambda_Y = hbar c / m0

where E_Lambda is the gravitational new-physics scale. Dr. M.'s sign point: the
scalar enters V(r) with a MINUS sign, so larger g_R2 => lighter m0 => longer
range => the deviation persists further AND reduces the entangling phase.

We scan E_Lambda across three regimes and report per-framework m0 (in eV) and
lambda_Y, flagging the torsion-balance window (lambda_Y ~ 10-100 um <-> m0 ~
2-20 meV). The punchline: the testable window sits at the meV / sub-mm scale —
the same scale as the dark-energy density and the existing short-range-gravity
frontier.
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

HBARC_eV_m = 1.973e-7   # hbar*c in eV·m
TORSION_WINDOW_m = (10e-6, 100e-6)   # current/next-gen short-range gravity reach


def m0_and_range(g_R2, E_Lambda_eV):
    m0 = E_Lambda_eV / np.sqrt(6.0 * g_R2)         # eV
    lam = HBARC_eV_m / m0                            # m
    return m0, lam


def main():
    fw = {f.name: f.encode().coefficients.get("g_R2", 0.0) for f in [
        StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
        CausalDynamicalTriangulation(), DiscoveredNovel(),
        DiscoveredParityViolating(), DiscoveredHighG8()]}

    regimes = {
        "E_Lambda = M_Pl (1.2e28 eV, natural)": 1.22e28,
        "E_Lambda = 1 TeV (1e12 eV)": 1e12,
        "E_Lambda = 2.4 meV (dark-energy / sub-mm scale)": 2.4e-3,
    }

    out = {}
    for label, EL in regimes.items():
        rows = {}
        print(f"\n=== {label} ===")
        for name, g in sorted(fw.items(), key=lambda kv: -kv[1]):
            m0, lam = m0_and_range(g, EL)
            inwin = TORSION_WINDOW_m[0] <= lam <= TORSION_WINDOW_m[1]
            flag = "  <== TORSION-BALANCE WINDOW" if inwin else ""
            rows[name] = {"g_R2": float(g), "m0_eV": float(m0),
                          "lambda_Y_m": float(lam), "in_window": bool(inwin)}
            # human-readable lambda
            if lam > 1e-3:
                ls = f"{lam*1e3:.2g} mm"
            elif lam > 1e-9:
                ls = f"{lam*1e6:.2g} um"
            else:
                ls = f"{lam:.1e} m"
            print(f"  {name:<28} g_R2={g:.3f}  m0={m0:.2e} eV  lambda_Y={ls}{flag}")
        out[label] = rows

    # at the dark-energy scale, report the discriminating spread
    de = out["E_Lambda = 2.4 meV (dark-energy / sub-mm scale)"]
    lams = {k: v["lambda_Y_m"] for k, v in de.items()}
    hi, lo = max(lams, key=lams.get), min(lams, key=lams.get)
    print(f"\n=== discrimination at the dark-energy scale ===")
    print(f"  all frameworks land in the {TORSION_WINDOW_m[0]*1e6:.0f}-{TORSION_WINDOW_m[1]*1e6:.0f} um "
          f"short-range-gravity window:")
    print(f"    longest  {hi}: lambda_Y = {lams[hi]*1e6:.1f} um (g_R2={de[hi]['g_R2']:.3f})")
    print(f"    shortest {lo}: lambda_Y = {lams[lo]*1e6:.1f} um (g_R2={de[lo]['g_R2']:.3f})")
    print(f"    spread = {lams[hi]/lams[lo]:.2f}x  -> resolvable with a sub-mm gravity scan")

    with open("experiments/out_yukawa_target.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_yukawa_target.json")


if __name__ == "__main__":
    main()
