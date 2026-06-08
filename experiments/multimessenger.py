"""Multimessenger parity: correlated GW+EM birefringence from one source (v1.56).

A single high-z source emits both GW and EM. If a common dark-energy axion (v1.46)
sources both the gravitational parity (g_R2_parity, Chern-Simons R Rtilde) and the
photon parity (axion-photon F Ftilde), then both the GW and EM polarizations
rotate as they cross the same axion field history along the line of sight.

Goal: assess whether the RATIO beta_GW/beta_EM is a clean, distance-independent
test of the common origin. Computes beta_EM(z) (the field-roll fraction along the
path, from the thawing axion) and confronts the GW side honestly.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

BETA_EM_ASYMPTOTIC_DEG = 0.34   # cosmic-birefringence value (full path, CMB)


def field_roll_fraction(z):
    """Fraction of the total axion field excursion accumulated between redshift z
    and today, for a thawing field that rolls only once dark energy dominates
    (a_DE ~ 0.6, i.e. z_DE ~ 0.67). Approximation: phi(a) - phi(a_i) ~ integral of
    the thawing growth; we use a smooth late-time roll ~ (a - a_DE)_+^2 normalized."""
    a = 1.0 / (1.0 + np.asarray(z, dtype=float))
    a_de = 0.6
    def roll(a_):  # cumulative roll from a=0 to a_
        x = np.maximum(a_ - a_de, 0.0)
        return x**2
    total = roll(1.0)                       # 0 -> today
    return (total - roll(a)) / total        # fraction accumulated between z and now


def main():
    zs = np.array([0.05, 0.1, 0.5, 1.0, 2.0, 5.0])
    frac = field_roll_fraction(zs)
    beta_em = BETA_EM_ASYMPTOTIC_DEG * frac

    print("=== Multimessenger parity: GW + EM birefringence from one source ===\n")
    print("  EM (photon) birefringence vs source redshift (axion rolls at z<~0.7):")
    print(f"  {'z':>6}{'roll fraction':>16}{'beta_EM (deg)':>16}")
    for z, f, b in zip(zs, frac, beta_em):
        print(f"  {z:>6.2f}{f:>16.2f}{b:>16.3f}")
    print(f"\n  => SOURCE REQUIREMENT: most of the birefringence accumulates at z<~1")
    print(f"     (the axion only rolls once dark energy dominates). A NEARBY source")
    print(f"     (GW170817 at z=0.0099) sees ~{field_roll_fraction(0.0099)*100:.1f}% of the effect —")
    print(f"     essentially nothing. You need z >~ 0.5-1 for either messenger to")
    print(f"     accumulate a detectable rotation.")

    print("\n=== Is the ratio beta_GW/beta_EM a clean, distance-independent test? ===")
    print("  HONEST FINDING: NO, not cleanly. The two effects are structurally different:")
    print("   - EM birefringence: a FREQUENCY-INDEPENDENT (achromatic) polarization-")
    print("     ANGLE rotation, beta_EM = (1/2) g_phi_gamma * Delta_phi, with")
    print("     g_phi_gamma = (alpha/2pi)(c_gamma/f) -- carries the EM fine-structure alpha.")
    print("   - GW birefringence (gravitational Chern-Simons): an AMPLITUDE asymmetry")
    print("     between L/R circular GW modes that is FREQUENCY-DEPENDENT and grows with")
    print("     the GW wavenumber; no alpha factor.")
    print("  So beta_GW/beta_EM ~ (c_grav/c_gamma)(2pi/alpha) x (k-dependent structural")
    print("  factor) -- it depends on the GW frequency and the coupling structure, and")
    print("  does NOT cleanly cancel to a pure anomaly-coefficient ratio. The naive")
    print("  'distance cancels' argument holds for the PATH (both share it), but the")
    print("  observables themselves are an angle vs an amplitude-asymmetry.")

    print("\n=== What IS a real multimessenger test ===")
    print("  JOINT DETECTION from one high-z (z>~0.5) source: both messengers show")
    print("  parity violation tracking the SAME axion field history. The correlation")
    print("  (both present, both scaling with the same Delta_phi(z) along the path)")
    print("  confirms the common dark-energy-axion origin -- even though the precise")
    print("  ratio is structural, not a clean constant. Experiment: next-gen GW")
    print("  detectors (ET/CE) + GRB/kilonova polarimetry of high-z multimessenger events.")

    out = {"beta_em_asymptotic_deg": BETA_EM_ASYMPTOTIC_DEG,
           "z": zs.tolist(), "roll_fraction": frac.tolist(),
           "beta_em_deg": beta_em.tolist(),
           "ratio_is_clean": False,
           "reason": "EM=achromatic angle (carries alpha); GW=chromatic amplitude asymmetry; ratio is structural+frequency-dependent",
           "real_test": "joint GW+EM parity detection from a z>~0.5 source tracking the same axion history"}
    with open("experiments/results/out_multimessenger.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/results/out_multimessenger.json")


if __name__ == "__main__":
    main()
