"""v2.243 - Black-hole superradiance: observed spins as an ultralight-boson detector.

A fresh BSM-relevant thread (reconnecting to the repo's new-physics-constraint purpose). A massive
bosonic field around a SPINNING black hole is amplified -- superradiance -- when its frequency
satisfies the condition omega < m Omega_H, with Omega_H the horizon angular velocity. The amplified
field forms a bound "gravitational atom" cloud that extracts the hole's spin. So an observed,
rapidly-spinning black hole that has NOT been spun down EXCLUDES the ultralight bosons that would
have grown a cloud -- turning black-hole spin measurements into a detector for QCD axions, fuzzy
dark matter, and dark photons in mass windows no laboratory reaches.

Kerr horizon angular velocity (G=c=1, a* = a/M): r_+ = M(1 + sqrt(1 - a*^2)),
    Omega_H = a* / (2 r_+ / M) = a* / (2(1 + sqrt(1-a*^2)))   (in units of 1/M).
Superradiance condition (a bound boson cloud has omega ~ mu, the boson mass): mu < m Omega_H / M,
so the maximum superradiant boson mass corresponds to the gravitational fine-structure constant
    alpha_max = M mu_max = m Omega_H   (geometric),
and the physical boson mass is mu = alpha * (hbar c) / (G M / c^2).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.243"
DEFAULT_OUT = Path("experiments/results/v2.243/qnm_superradiance_boson_bound.json")
HBARC_eV_m = 1.97327e-7          # hbar c in eV*m
GM_SUN_OVER_C2_m = 1476.6        # G M_sun / c^2 in metres


def horizon_angular_velocity(astar: float) -> float:
    """Omega_H in units of 1/M for dimensionless spin a* = a/M."""
    return astar / (2 * (1 + math.sqrt(1 - astar**2)))


def alpha_max(astar: float, m: int = 1) -> float:
    """Max gravitational fine-structure constant alpha = M*mu that superradiates in mode m."""
    return m * horizon_angular_velocity(astar)


def boson_mass_eV(alpha: float, mass_solar: float) -> float:
    """Physical boson mass mu = alpha * hbar c / (G M / c^2)."""
    return alpha * HBARC_eV_m / (mass_solar * GM_SUN_OVER_C2_m)


def run() -> dict:
    # horizon angular velocity sequence (verify limits)
    omega_h = [{"a_star": a, "Omega_H": horizon_angular_velocity(a), "alpha_max_m1": alpha_max(a)}
               for a in (0.0, 0.5, 0.9, 0.998, 1.0)]
    # boson-mass exclusion windows: a fast-spinning (a*=0.9) hole excludes up to alpha ~ Omega_H(0.9)
    a_obs = 0.9
    amax = alpha_max(a_obs)
    targets = [(10.0, "stellar-mass (10 Msun)"), (62.0, "GW150914 remnant (~62 Msun)"),
               (1e6, "SMBH 1e6 Msun"), (6.5e9, "M87* (6.5e9 Msun)")]
    windows = [{"system": label, "mass_solar": M, "mu_max_eV": boson_mass_eV(amax, M)}
               for M, label in targets]
    return {
        "version": VERSION,
        "method": ("Kerr horizon angular velocity Omega_H(a*) -> superradiance condition mu < m "
                   "Omega_H/M -> max superradiant alpha = m Omega_H -> physical boson mass via "
                   "hbar c/(G M/c^2); G=c=1"),
        "horizon_angular_velocity": omega_h,
        "extremal_Omega_H": horizon_angular_velocity(1.0),
        "observed_spin_for_windows": a_obs,
        "alpha_max_at_observed_spin": amax,
        "boson_mass_windows": windows,
        "finding": (
            "Black-hole spin is an ultralight-boson detector. The Kerr horizon angular velocity "
            "Omega_H rises from 0 (Schwarzschild) to the extremal 1/2 (a*=1), and the superradiance "
            "condition mu < m Omega_H/M means a fast-spinning hole (a* = 0.9, Omega_H = 0.313) "
            f"amplifies and spins down on bosons up to alpha = M mu = {amax:.2f} (m=1). Converting to "
            "physical mass, observed rapidly-spinning black holes across the mass spectrum exclude "
            "ultralight bosons in windows no laboratory reaches: a stellar-mass hole probes "
            f"mu ~ {boson_mass_eV(amax,10):.1e} eV, a GW150914-like remnant similar, and a "
            f"supermassive hole down to mu ~ {boson_mass_eV(amax,6.5e9):.1e} eV -- spanning the QCD "
            "axion, fuzzy-dark-matter (~1e-22 eV), and dark-photon windows. A measured high spin "
            "where superradiance WOULD have spun the hole down excludes that boson mass: the "
            "'Regge-plane' gap."
        ),
        "honest_scope": (
            "The superradiance CONDITION (mu < m Omega_H/M) and Omega_H(a*) are EXACT Kerr results "
            "(verified: Omega_H -> 1/2 extremal). The actual EXCLUSION additionally requires the "
            "instability GROWTH TIME to be shorter than the hole's spin-down/age timescale -- the "
            "Detweiler rate scales as alpha^{4l+5} (~alpha^9 for the dominant l=m=1 mode) and peaks "
            "near alpha ~ 0.4, so the real bound is a window in (mass, spin), not the full "
            "condition; that timescale calculation (and the cloud's GW signature) is the "
            "detailed step, not done here. The mass estimates use a representative a*=0.9 and "
            "alpha~Omega_H; published bounds (e.g. from GW/X-ray spin measurements) fold in the "
            "measured spin posteriors and ages. Self-contained order-of-magnitude reconstruction of "
            "a real BSM probe, not a new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Zel'dovich (1971); Press & Teukolsky, Nature 238 (1972) 211 -- superradiance / BH bomb",
            "Detweiler, PRD 22 (1980) 2323 -- massive-scalar superradiant growth rate",
            "Arvanitaki & Dubovsky, PRD 83 (2011) 044026 -- black-hole superradiance / axiverse",
            "this repo: v2.239 (Kerr horizon / spin)",
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
    print(" a*     Omega_H    alpha_max(m=1)")
    for r in res["horizon_angular_velocity"]:
        print(f" {r['a_star']:.3f}  {r['Omega_H']:.5f}    {r['alpha_max_m1']:.5f}")
    print(f"\nboson-mass windows at a*={res['observed_spin_for_windows']} (alpha_max={res['alpha_max_at_observed_spin']:.2f}):")
    for w in res["boson_mass_windows"]:
        print(f"  {w['system']:28s} mu_max ~ {w['mu_max_eV']:.2e} eV")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
