"""Experimental spec sheet: precision needed to discriminate the theories (v1.41).

Turns the decisive program (v1.39-40) into apparatus requirements. For the three
engine observables, compute the measurement precision needed to tell the
candidate theories apart, and compare to current experimental reach.

  1. SUB-MM GRAVITY (Dr. M.'s decisive test): the R^2 scalar gives a Yukawa
     deviation from Newton, delta(r) = -(1/3) exp(-r/lambda_Y), with lambda_Y
     from g_R2 at the dark-energy cutoff (v1.40). Find the separation that best
     separates the theories and the fractional-force precision required.
  2. GRAVITATIONAL BIREFRINGENCE (parity): signal ~ |g_R2_parity| + (omega-
     weighted) |g_R3_parity|; precision vs LIGO's current ~0.1 bound on g_R2_parity.
  3. GIE: foundational existence threshold (phase > 1).
"""

import json
import sys
from itertools import combinations

import numpy as np

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT

sys.path.insert(0, ".")

HBARC_eV_m = 1.973e-7
E_LAMBDA_eV = 2.4e-3          # dark-energy cutoff (v1.40)
SCALAR_AMP = 1.0 / 3.0        # Stelle scalar Yukawa amplitude

FRAMEWORKS = [StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
              CausalDynamicalTriangulation(), DiscoveredNovel(),
              DiscoveredParityViolating(), DiscoveredHighG8()]
NAMES = [f.name for f in FRAMEWORKS]
COEF = {f.name: f.encode().coefficients for f in FRAMEWORKS}


def lambda_Y(name):
    g = COEF[name].get("g_R2", 0.0)
    m0 = E_LAMBDA_eV / np.sqrt(6.0 * g)
    return HBARC_eV_m / m0           # metres


def yukawa_delta(name, r):
    return -SCALAR_AMP * np.exp(-r / lambda_Y(name))


def submm_spec():
    lams = {n: lambda_Y(n) for n in NAMES}
    rs = np.linspace(20e-6, 300e-6, 200)
    # best separation = maximize the minimum pairwise |delta_i - delta_j|
    best_r, best_minsep = None, -1
    for r in rs:
        d = np.array([yukawa_delta(n, r) for n in NAMES])
        pair_gaps = [abs(d[i] - d[j]) for i, j in combinations(range(len(NAMES)), 2)]
        m = min(pair_gaps)
        if m > best_minsep:
            best_minsep, best_r = m, r
    # at best_r, the deltas and the precision needed to resolve all pairs
    d_at = {n: yukawa_delta(n, best_r) for n in NAMES}
    # required fractional-force precision = half the smallest pairwise gap
    req_prec = best_minsep / 2.0
    # how many pairs resolvable at current (~1%) and next-gen (~0.1%) precision
    def resolvable(prec):
        return sum(1 for i, j in combinations(range(len(NAMES)), 2)
                   if abs(d_at[NAMES[i]] - d_at[NAMES[j]]) > 2 * prec)
    return {"best_separation_um": best_r * 1e6,
            "lambda_Y_um": {n: lams[n] * 1e6 for n in NAMES},
            "delta_at_best": d_at,
            "required_precision_all_pairs": req_prec,
            "pairs_total": len(list(combinations(NAMES, 2))),
            "pairs_resolvable_at_1pct": resolvable(0.01),
            "pairs_resolvable_at_0p1pct": resolvable(0.001)}


def birefringence_spec():
    # signal proxy: leading parity coupling (LIGO bounds |g_R2_parity| ~ 0.1 at O3)
    sig = {n: abs(COEF[n].get("g_R2_parity", 0.0)) for n in NAMES}
    parity_fw = {n: s for n, s in sig.items() if s > 1e-6}
    return {"g_R2_parity": sig, "ligo_o3_bound": 0.1,
            "parity_violating_frameworks": parity_fw,
            "needed_sensitivity": (min(parity_fw.values()) / 2 if parity_fw else None)}


def main():
    sm = submm_spec()
    bf = birefringence_spec()

    print("=== 1. SUB-MM GRAVITY SPEC (decisive discriminator) ===")
    print(f"  best discriminating separation: r* = {sm['best_separation_um']:.0f} um")
    print(f"  Yukawa ranges & fractional-force deviation at r*:")
    for n in sorted(NAMES, key=lambda n: sm['delta_at_best'][n]):
        print(f"    {n:<28} lambda_Y={sm['lambda_Y_um'][n]:6.1f} um   "
              f"delta(r*)={sm['delta_at_best'][n]*100:+6.2f}% of Newton")
    print(f"  precision to resolve ALL {sm['pairs_total']} pairs: "
          f"{sm['required_precision_all_pairs']*100:.2f}% fractional force")
    print(f"  pairs resolvable at 1% precision (current torsion balance): "
          f"{sm['pairs_resolvable_at_1pct']}/{sm['pairs_total']}")
    print(f"  pairs resolvable at 0.1% precision (next-gen): "
          f"{sm['pairs_resolvable_at_0p1pct']}/{sm['pairs_total']}")

    print("\n=== 2. GRAVITATIONAL BIREFRINGENCE SPEC (parity sector) ===")
    print(f"  LIGO O3 bound on |g_R2_parity| ~ {bf['ligo_o3_bound']}")
    for n, s in sorted(bf['g_R2_parity'].items(), key=lambda kv: -kv[1]):
        tag = "  parity-violating" if s > 1e-6 else ""
        print(f"    {n:<28} |g_R2_parity|={s:.3f}{tag}")
    if bf["needed_sensitivity"]:
        print(f"  birefringence sensitivity to flag the parity branch: "
              f"|g_R2_parity| ~ {bf['needed_sensitivity']:.3f} "
              f"({bf['ligo_o3_bound']/bf['needed_sensitivity']:.0f}x below LIGO O3)")

    print("\n=== 3. GIE (foundational) ===")
    print("  existence threshold (phase>1): ug masses, ~10um superposition, ~1s,")
    print("  P<1e-17 Torr, T<100 mK (Dr. M.). Answers 'is gravity quantum', not 'which'.")

    out = {"submm": sm, "birefringence": bf}
    with open("experiments/out_spec_sheet.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_spec_sheet.json")


if __name__ == "__main__":
    main()
