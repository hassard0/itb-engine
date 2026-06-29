"""v2.239 - Kerr generalization: how black-hole spin splits and amplifies the strong-field observables.

A fresh thread off the now-capped Schwarzschild strong-field sub-program (v2.229-v2.238). Rotation
(spin a, in units of M) breaks the spherical symmetry: the equatorial circular orbits split into
PROGRADE and RETROGRADE branches, and frame-dragging pulls the prograde orbits toward the horizon.
This re-computes the key observables for Kerr via the Bardeen-Press-Teukolsky equatorial formulas
(M=1), reproducing the Schwarzschild limit (a=0) and the famous extremal amplification.

  ISCO radius (BPT):   r_ISCO = 3 + Z2 -/+ sqrt((3-Z1)(3+Z1+2 Z2)),  -/+ = pro/retro,
                       Z1 = 1 + (1-a^2)^{1/3}[(1+a)^{1/3}+(1-a)^{1/3}],  Z2 = sqrt(3a^2 + Z1^2).
  Circular-orbit energy:  E = (r^2 - 2r +/- a sqrt(r)) / (r sqrt(r^2 - 3r +/- 2a sqrt(r))).
  Accretion efficiency:   eta = 1 - E_ISCO   (5.72% at a=0  ->  1 - 1/sqrt3 ~ 42.3% extremal prograde).
  Equatorial photon orbit: r_ph = 2[1 + cos((2/3) arccos(-/+ a))].

The headline: spin SPLITS the v2.238-locked channels (pro/retro branches) and AMPLIFIES the prograde
accretion efficiency from 5.72% to ~42% -- the rotational energy extraction that makes spinning black
holes the engines of the most luminous AGN / quasars.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.239"
DEFAULT_OUT = Path("experiments/results/v2.239/qnm_kerr_strong_field.json")
SPINS = [0.0, 0.5, 0.9, 0.99, 0.998]      # incl. the Thorne a=0.998 equilibrium limit


def r_isco(a: float, prograde: bool = True) -> float:
    s = -1.0 if prograde else 1.0
    Z1 = 1 + (1 - a**2) ** (1 / 3) * ((1 + a) ** (1 / 3) + (1 - a) ** (1 / 3))
    Z2 = math.sqrt(3 * a**2 + Z1**2)
    return 3 + Z2 + s * math.sqrt((3 - Z1) * (3 + Z1 + 2 * Z2))


def circular_energy(r: float, a: float, prograde: bool = True) -> float:
    sgn = 1.0 if prograde else -1.0       # prograde uses +a
    disc = r**2 - 3 * r + 2 * sgn * a * math.sqrt(r)
    if disc <= 0:
        return math.nan
    return (r**2 - 2 * r + sgn * a * math.sqrt(r)) / (r * math.sqrt(disc))


def photon_radius(a: float, prograde: bool = True) -> float:
    s = -1.0 if prograde else 1.0
    return 2 * (1 + math.cos((2 / 3) * math.acos(s * a)))


def efficiency(a: float, prograde: bool = True) -> float:
    E = circular_energy(r_isco(a, prograde), a, prograde)
    return float("nan") if math.isnan(E) else 1 - E


def run() -> dict:
    rows = []
    for a in SPINS:
        rows.append({
            "a": a,
            "isco_prograde": r_isco(a, True), "isco_retrograde": r_isco(a, False),
            "efficiency_prograde": efficiency(a, True), "efficiency_retrograde": efficiency(a, False),
            "photon_prograde": photon_radius(a, True), "photon_retrograde": photon_radius(a, False),
        })
    extremal = {  # a=1 has a coordinate degeneracy at r=1; report analytic limits
        "isco_prograde_limit": 1.0, "efficiency_prograde_limit": 1 - 1 / math.sqrt(3),
        "isco_retrograde": r_isco(1.0, False), "efficiency_retrograde": efficiency(1.0, False),
        "photon_prograde_limit": 1.0, "photon_retrograde": photon_radius(1.0, False),
    }
    a0 = rows[0]
    schw_ok = (abs(a0["isco_prograde"] - 6) < 1e-9 and abs(a0["efficiency_prograde"] - (1 - math.sqrt(8 / 9))) < 1e-9
               and abs(a0["photon_prograde"] - 3) < 1e-9)
    return {
        "version": VERSION,
        "method": ("Kerr equatorial Bardeen-Press-Teukolsky formulas (M=1): ISCO, circular-orbit "
                   "energy/efficiency, equatorial photon orbit; prograde & retrograde branches"),
        "schwarzschild_limit_reproduced": bool(schw_ok),
        "spin_sequence": rows,
        "extremal_a1": extremal,
        "finding": (
            "Spin SPLITS the v2.238-locked strong-field observables into prograde and retrograde "
            "branches and AMPLIFIES the prograde channel. As a goes 0 -> 1 the prograde ISCO shrinks "
            "6 -> 1 (frame-dragging) while the retrograde ISCO grows 6 -> 9; the equatorial photon "
            "orbit splits 3 -> 1 (pro) and 3 -> 4 (retro); and the prograde accretion efficiency "
            f"climbs from {a0['efficiency_prograde']:.4f} (5.72%) to the extremal limit "
            f"{extremal['efficiency_prograde_limit']:.4f} (1 - 1/sqrt3 ~ 42.3%), while retrograde "
            "DROPS to ~3.77%. Schwarzschild (a=0) is reproduced exactly. The 42% prograde efficiency "
            "-- nearly an order of magnitude above Schwarzschild and ~75x the rest-mass efficiency of "
            "stellar fusion -- is the rotational energy extraction that powers the most luminous AGN "
            "and quasars, and it is the spin-dependent generalization of the single-deformation "
            "fingerprint (v2.238): spin is the one parameter Nature actually varies."
        ),
        "honest_scope": (
            "Equatorial, geodesic (test-particle) circular orbits of the exact Kerr metric, M=1; the "
            "ISCO/efficiency/photon formulas are the standard Bardeen-Press-Teukolsky results (exact, "
            "not deformation-perturbative -- this is real Kerr, not a bump). The a=1 EXTREMAL point "
            "has a coordinate degeneracy at r=1 (the prograde ISCO, photon orbit, and horizon "
            "coincide in Boyer-Lindquist r), so the prograde efficiency/radii there are reported as "
            "analytic LIMITS (1-1/sqrt3, r->1), and astrophysical spins are capped near the Thorne "
            "a=0.998 value (radiation torque) -- included in the sequence. Efficiency assumes a "
            "standard thin disk radiating the binding energy. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Bardeen, Press, Teukolsky, ApJ 178 (1972) 347 -- Kerr equatorial orbits / ISCO / efficiency",
            "Thorne, ApJ 191 (1974) 507 -- a/M = 0.998 spin equilibrium",
            "this repo: v2.237 (Schwarzschild ISCO), v2.238 (unified deformation fingerprint)",
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
    print(" a       ISCO(pro/retro)     eta(pro/retro)        photon(pro/retro)")
    for r in res["spin_sequence"]:
        print(f" {r['a']:.3f}   {r['isco_prograde']:.4f}/{r['isco_retrograde']:.4f}     "
              f"{r['efficiency_prograde']:.4f}/{r['efficiency_retrograde']:.4f}     "
              f"{r['photon_prograde']:.4f}/{r['photon_retrograde']:.4f}")
    e = res["extremal_a1"]
    print(f" 1.000*  {e['isco_prograde_limit']:.4f}/{e['isco_retrograde']:.4f}     "
          f"{e['efficiency_prograde_limit']:.4f}/{e['efficiency_retrograde']:.4f}     "
          f"{e['photon_prograde_limit']:.4f}/{e['photon_retrograde']:.4f}  (*analytic limits)")
    print(f"Schwarzschild limit reproduced = {res['schwarzschild_limit_reproduced']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
