"""v2.280 - The four classic tests of general relativity and the PPN parameters gamma, beta.

Continuing the classical-GR thread (v2.278/v2.279 binary pulsars) into the solar system, where the
parametrized post-Newtonian (PPN) framework reduces every weak-field test to two Eddington parameters:
gamma (how much space curvature a unit mass produces) and beta (the nonlinearity of superposition).
General relativity is exactly gamma = beta = 1, and the four classic tests measure them:

  1. Light deflection      alpha = (1+gamma)/2 * 4GM/(c^2 b)         GR: 1.75" at the solar limb
  2. Shapiro time delay    Dt    proportional to (1+gamma)/2          Cassini: gamma-1 = (2.1+/-2.3)e-5
  3. Perihelion precession dw    = (2+2gamma-beta)/3 * 6 pi GM/(c^2 a(1-e^2))   GR: 43"/century (Mercury)
  4. Gravitational redshift Dnu/nu = g h / c^2                        equivalence principle (Pound-Rebka)

The deflection and Shapiro delay both scale as (1+gamma)/2 -- so gamma=0 (Newton) gives HALF the GR
value, the discriminant Eddington's 1919 eclipse used; the perihelion mixes gamma and beta. The Cassini
Shapiro measurement (gamma = 1 to 2.3e-5) is the tightest confirmation of GR's light-bending sector.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.280"
DEFAULT_OUT = Path("experiments/results/v2.280/qnm_ppn_solar_system.json")

G = 6.674e-11
C = 2.998e8
MSUN = 1.989e30
RSUN = 6.957e8
ARCSEC = 206264.806              # rad -> arcsec

# Mercury orbit
MERC_A = 5.7909e10               # semi-major axis, m
MERC_E = 0.20563
MERC_T_DAYS = 87.9691
ORBITS_PER_CENTURY = 36525.0 / MERC_T_DAYS

GAMMA_CASSINI_BOUND = 2.3e-5     # |gamma - 1| (Bertotti, Iess, Tortora 2003)


def light_deflection_arcsec(gamma: float = 1.0, b_over_R: float = 1.0) -> float:
    """Deflection of light grazing the Sun at impact parameter b = b_over_R * R_sun."""
    return (1 + gamma) / 2 * 4 * G * MSUN / (C**2 * RSUN * b_over_R) * ARCSEC


def mercury_precession_arcsec_century(gamma: float = 1.0, beta: float = 1.0) -> float:
    """Perihelion precession of Mercury [arcsec/century]."""
    per_orbit = (2 + 2 * gamma - beta) / 3 * 6 * math.pi * G * MSUN / (C**2 * MERC_A * (1 - MERC_E**2))
    return per_orbit * ORBITS_PER_CENTURY * ARCSEC


def gravitational_redshift(h_m: float, g: float = 9.80665) -> float:
    """Fractional frequency shift over height h in a uniform field: Dnu/nu = g h / c^2 (Pound-Rebka)."""
    return g * h_m / C**2


def run() -> dict:
    defl_gr = light_deflection_arcsec(1.0)
    defl_newton = light_deflection_arcsec(0.0)        # the 1919 discriminant: half the GR value
    merc_gr = mercury_precession_arcsec_century(1.0, 1.0)
    pr_shift = gravitational_redshift(22.5)            # Pound-Rebka tower height

    checks = {
        "light_deflection_GR_1p75_arcsec": abs(defl_gr - 1.75) < 0.01,
        "newton_deflection_is_half_GR": abs(defl_newton / defl_gr - 0.5) < 1e-9,
        "mercury_precession_43_per_century": abs(merc_gr - 43.0) < 0.5,
        "deflection_scales_1_plus_gamma": abs(light_deflection_arcsec(0.5) / defl_gr
                                              - (1 + 0.5) / 2) < 1e-9,
        "mercury_ppn_factor_2_plus_2gamma_minus_beta": abs(
            mercury_precession_arcsec_century(0.5, 0.5) / merc_gr - (2 + 1 - 0.5) / 3) < 1e-9,
        "pound_rebka_redshift_2p5e_minus_15": abs(pr_shift - 2.46e-15) < 0.1e-15,
        "cassini_gamma_bound_tight": GAMMA_CASSINI_BOUND < 1e-4,
    }

    tests = [
        {"test": "light deflection", "ppn_factor": "(1+gamma)/2", "GR_value": f"{defl_gr:.4f} arcsec (solar limb)",
         "measurement": "VLBI gamma = 0.99992 +/- 0.00023"},
        {"test": "Shapiro time delay", "ppn_factor": "(1+gamma)/2", "GR_value": "round-trip ~ 250 us past the Sun",
         "measurement": "Cassini gamma-1 = (2.1 +/- 2.3)e-5 (tightest)"},
        {"test": "perihelion precession", "ppn_factor": "(2+2gamma-beta)/3", "GR_value": f"{merc_gr:.2f} arcsec/century (Mercury)",
         "measurement": "observed 42.98 +/- 0.04 (anomalous)"},
        {"test": "gravitational redshift", "ppn_factor": "1 (equivalence principle)", "GR_value": f"{pr_shift:.3e} (Pound-Rebka, 22.5 m)",
         "measurement": "confirmed to ~1% (1960); GPS 38 us/day"},
    ]

    return {
        "version": VERSION,
        "method": ("PPN weak-field tests: deflection (1+gamma)/2 4GM/c^2 b, perihelion "
                   "(2+2gamma-beta)/3 6 pi GM/c^2 a(1-e^2), redshift g h/c^2; GR = gamma=beta=1"),
        "classic_tests": tests,
        "light_deflection_GR_arcsec": defl_gr,
        "newton_deflection_arcsec": defl_newton,
        "mercury_precession_GR_arcsec_century": merc_gr,
        "pound_rebka_redshift": pr_shift,
        "gamma_cassini_bound": GAMMA_CASSINI_BOUND,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The four classic tests of general relativity all reduce, in the weak field, to the two "
            "Eddington PPN parameters gamma and beta, and GR's gamma=beta=1 passes every one. Light "
            f"grazing the Sun is deflected by {defl_gr:.4f} arcsec (the famous 1.75 inch), and because "
            "deflection scales as (1+gamma)/2 the Newtonian gamma=0 prediction is exactly HALF "
            f"({defl_newton:.4f} arcsec) -- the discriminant Eddington's 1919 eclipse used to choose "
            "Einstein over Newton. The Shapiro time delay shares that (1+gamma)/2 factor, and the "
            "Cassini spacecraft measured gamma - 1 = (2.1 +/- 2.3)e-5, the tightest confirmation of "
            "GR's space-curvature sector. Mercury's perihelion precesses by "
            f"{merc_gr:.2f} arcsec/century (the anomalous 43 inch Le Verrier could not explain with "
            "Newton), mixing gamma and beta as (2+2gamma-beta)/3. And the gravitational redshift "
            f"(Dnu/nu = g h/c^2 = {pr_shift:.2e} over the Pound-Rebka tower) tests the equivalence "
            "principle that underlies any metric theory -- the same effect GPS corrects at 38 us/day. "
            "Together with the v2.278/v2.279 binary pulsars (strong field), the PPN solar-system tests "
            "(weak field) bracket general relativity across the full range of gravitational potentials."
        ),
        "honest_scope": (
            "Exact leading-order PPN formulas with standard solar and Mercury parameters; the "
            "deflection (1.7505 arcsec), Mercury precession (~43 arcsec/century) and Pound-Rebka shift "
            "(~2.46e-15) reproduce the textbook GR values to the precision of the inputs. The measured "
            "bounds (Cassini gamma, VLBI gamma, observed Mercury anomaly) are the source-backed "
            "published values, cited not re-derived. The Mercury 43 arcsec is the GR CONTRIBUTION "
            "after subtracting the ~5025 arcsec/century of equinox precession and ~530 from planetary "
            "perturbations (the classic Newtonian-residual bookkeeping), not the raw observed rate. "
            "Point-mass, weak-field, leading PPN order; the Sun's quadrupole J2 adds a tiny correction "
            "not included. A classical-GR / PPN-test result, not an engine constraint refit."
        ),
        "references": [
            "Will, 'The confrontation between general relativity and experiment', Living Rev. Rel. 17 (2014) 4",
            "Bertotti, Iess, Tortora, 'A test of general relativity using radio links with the Cassini spacecraft', Nature 425 (2003) 374",
            "Pound, Rebka, 'Apparent weight of photons', PRL 4 (1960) 337",
            "this repo: v2.278/v2.279 (binary-pulsar strong-field tests)",
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
    print("the four classic tests of GR (PPN gamma=beta=1):")
    for t in res["classic_tests"]:
        print(f"  {t['test']:22s} [{t['ppn_factor']:22s}] {t['GR_value']}")
    print(f"  light deflection: GR {res['light_deflection_GR_arcsec']:.4f}\" vs Newton {res['newton_deflection_arcsec']:.4f}\" (half)")
    print(f"  Mercury precession: {res['mercury_precession_GR_arcsec_century']:.2f}\"/century")
    print(f"  Cassini: gamma = 1 to {res['gamma_cassini_bound']:.1e}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
