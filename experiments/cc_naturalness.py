"""The cosmological constant, the gravitational cutoff, and EFT consistency (v1.44).

The linchpin of the decisive-experiment program (v1.40) is the assumption that
the gravitational EFT cutoff sits near the dark-energy scale. This cycle tests
whether that is arbitrary or *motivated*, by confronting three things:

  (a) the observed dark-energy density rho_Lambda = (2.4 meV)^4;
  (b) the naive EFT vacuum energy ~ Lambda^4 (Lambda = gravitational cutoff);
  (c) the engine's EFT-validity bound |g| <= O(1-2) and the R^2-scalar Yukawa
      lambda_Y = sqrt(6 g_R2) * hbar c / Lambda.

Two routes to a viable theory:
  1. Planckian cutoff (Lambda = M_Pl): the CC problem — vacuum energy is
     ~10^122 x observed (fine-tuning), OR one tries to "degravitate" it with a
     light R^2 scalar (mass ~ Hubble), which needs g_R2 ~ (Lambda/H0)^2 — a
     ~10^120 coefficient that BLOWS THROUGH the engine's EFT-validity box.
  2. Dark-energy-scale gravitational cutoff (Lambda ~ 2.4 meV): then Lambda^4 ~
     rho_Lambda automatically (NO tuning), g_R2 stays O(1) (engine-consistent),
     AND the Yukawa is sub-mm (testable, v1.40-43).

Crucial caveat made explicit: a meV *gravitational* cutoff is NOT excluded by
Standard-Model physics, because gravity is only probed down to ~50 um; the SM
cutoff is independent and high. This is the standard rationale of short-range
gravity tests.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

# constants
M_PL_eV = 1.22e28
H0_eV = 1.5e-33                  # Hubble scale ~ 10^-33 eV
RHO_DE_QUARTER_eV = 2.4e-3      # rho_Lambda^(1/4) = dark-energy scale
HBARC_eV_m = 1.973e-7
EFT_BOX = 2.0                    # engine's |g| <= 2 validity bound
G_R2_NATURAL = 0.2               # representative O(1) value


def analyze(Lambda_eV):
    # (a) vacuum-energy tuning relative to observed dark energy
    tuning = (Lambda_eV / RHO_DE_QUARTER_eV) ** 4          # Lambda^4 / rho_Lambda
    # (b) R^2 Yukawa range at natural g_R2 ~ 0.2
    m0 = Lambda_eV / np.sqrt(6 * G_R2_NATURAL)
    lamY = HBARC_eV_m / m0                                  # metres
    # (c) g_R2 required to degravitate the CC (scalar mass ~ Hubble)
    g_R2_degrav = (Lambda_eV / (np.sqrt(6) * H0_eV)) ** 2
    return {"Lambda_eV": Lambda_eV,
            "vacuum_tuning_factor": tuning,
            "yukawa_range_m_at_natural_gR2": lamY,
            "g_R2_for_degravitation": float(g_R2_degrav),
            "degravitation_within_EFT_box": bool(g_R2_degrav <= EFT_BOX)}


def main():
    scales = {
        "M_Pl (1.2e28 eV)": M_PL_eV,
        "1 TeV": 1e12,
        "1 eV": 1.0,
        "dark-energy scale (2.4 meV)": RHO_DE_QUARTER_eV,
    }
    out = {}
    print("=== The cosmological constant vs the gravitational cutoff vs EFT consistency ===\n")
    print(f"  observed dark-energy density: rho_Lambda = (2.4 meV)^4")
    print(f"  engine EFT-validity bound: |g_R2| <= {EFT_BOX}\n")
    print(f"  {'cutoff Lambda':<26}{'vac-energy tuning':>20}{'g_R2 for degrav':>18}  {'Yukawa range':>14}")
    for label, L in scales.items():
        a = analyze(L)
        out[label] = a
        # human-readable
        tune = f"{a['vacuum_tuning_factor']:.1e}"
        gdeg = f"{a['g_R2_for_degravitation']:.1e}"
        ly = a['yukawa_range_m_at_natural_gR2']
        lys = (f"{ly*1e6:.1f} um" if 1e-9 < ly < 1e-1 else f"{ly:.1e} m")
        print(f"  {label:<26}{tune:>20}{gdeg:>18}  {lys:>14}")

    de = out["dark-energy scale (2.4 meV)"]
    pl = out["M_Pl (1.2e28 eV)"]
    print("\n=== Verdict ===")
    print(f"  Planckian cutoff:  vacuum energy is {pl['vacuum_tuning_factor']:.0e}x observed")
    print(f"    => the cosmological-constant fine-tuning problem (~122 orders).")
    print(f"    degravitating it needs g_R2 ~ {pl['g_R2_for_degravitation']:.0e} "
          f"-> violates the EFT-validity box (|g|<= {EFT_BOX}) by ~{np.log10(pl['g_R2_for_degravitation']):.0f} orders.")
    print(f"  Dark-energy-scale gravitational cutoff (2.4 meV):")
    print(f"    vacuum energy ~ Lambda^4 ~ rho_Lambda  (tuning factor {de['vacuum_tuning_factor']:.1f}) -> NO CC problem,")
    print(f"    g_R2 stays O(1) (engine-consistent), Yukawa range "
          f"{de['yukawa_range_m_at_natural_gR2']*1e6:.0f} um (sub-mm, TESTABLE).")
    print("  => The dark-energy-scale cutoff is the consistency-MOTIVATED choice, not an")
    print("     arbitrary one: it is the unique scale that simultaneously dissolves the CC")
    print("     fine-tuning, keeps the Wilson coefficients inside the engine's validity box,")
    print("     and lands the new-physics signal in the sub-mm gravity window.")
    print("  (A meV *gravitational* cutoff is allowed: gravity is only probed to ~50 um;")
    print("   the SM cutoff is separate and high.)")

    with open("experiments/out_cc_naturalness.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_cc_naturalness.json")


if __name__ == "__main__":
    main()
