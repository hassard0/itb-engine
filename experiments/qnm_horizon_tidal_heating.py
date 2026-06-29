"""v2.249 - Horizon tidal heating: the absorption channel of the 'is it a black hole?' test.

A black hole exchanges energy with an inspiralling companion through its HORIZON (tidal heating):
the horizon flux is proportional to (Omega_orbit - Omega_H) for the dominant l=m=2 tidal coupling,
so its SIGN is the SAME superradiance condition as v2.243-v2.246 -- when Omega_orbit < Omega_H the
hole LOSES energy to the orbit (a superradiant tidal torque that spins the hole down), and when
Omega_orbit > Omega_H it ABSORBS. A horizonless exotic compact object (ECO) has NO horizon and hence
NO such flux, so the gravitational-wave inspiral phase carries a horizon-heating term whose
presence -- and sign -- distinguishes a black hole from a horizonless object. This is the ABSORPTION
channel of the horizon test, complementing the static tidal Love number (v2.235/v2.236) and the
ringdown echoes (v2.247/v2.248), and it unifies the horizon-test and superradiance suites through the
shared Omega_H.

Prograde Kerr circular orbit (M=1): Omega_orbit = 1/(r^{3/2} + a); horizon angular velocity
Omega_H = a/(2(1 + sqrt(1-a^2))). The flux flips sign at the critical radius where
Omega_orbit = Omega_H, r_crit = (1/Omega_H - a)^{2/3}.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_kerr_strong_field import r_isco

VERSION = "v2.249"
DEFAULT_OUT = Path("experiments/results/v2.249/qnm_horizon_tidal_heating.json")
SPINS = [0.1, 0.3, 0.5, 0.7, 0.9, 0.99]


def omega_orbit(r: float, a: float) -> float:
    return 1.0 / (r**1.5 + a)


def omega_h(a: float) -> float:
    return a / (2 * (1 + math.sqrt(1 - a**2)))


def r_crit(a: float) -> float | None:
    inv = 1.0 / omega_h(a) - a if a > 0 else math.inf
    return inv ** (2.0 / 3.0) if inv and inv > 0 else None


def run() -> dict:
    rows = []
    for a in SPINS:
        ris = r_isco(a, True)
        oi = omega_orbit(ris, a)
        rc = r_crit(a)
        superradiant = oi < omega_h(a)
        rows.append({"a_star": a, "Omega_H": omega_h(a), "r_crit": rc,
                     "r_isco_prograde": ris, "Omega_orbit_isco": oi,
                     "regime_at_isco": "superradiant (hole->orbit)" if superradiant
                     else "absorbing (orbit->hole)"})
    # crossover spin: where the ISCO regime flips (between a where r_crit crosses r_isco)
    flips = [rows[i]["a_star"] for i in range(1, len(rows))
             if (rows[i]["regime_at_isco"] != rows[i - 1]["regime_at_isco"])]
    return {
        "version": VERSION,
        "method": ("horizon tidal-heating flux sign = sign(Omega_orbit - Omega_H); prograde Kerr "
                   "circular orbit Omega_orbit=1/(r^{3/2}+a); flux flips at r_crit=(1/Omega_H-a)^{2/3}; "
                   "compared to the prograde ISCO; M=1"),
        "spin_sequence": rows,
        "regime_crossover_near_spin": flips[0] if flips else None,
        "finding": (
            "The horizon tidal-heating flux has the SAME sign condition as superradiance: it is "
            "superradiant (the hole gives energy to the orbit, spinning down) when Omega_orbit < "
            "Omega_H and absorbing otherwise. The flux flips at r_crit = (1/Omega_H - a)^{2/3}. For "
            "SLOWLY-spinning holes the inspiral is ABSORBING at the ISCO (standard tidal heating "
            "that drains orbital energy into the hole), but for FAST-spinning holes (a* >~ 0.4) "
            "r_crit drops BELOW the ISCO, so the ENTIRE stable inspiral is SUPERRADIANT -- the hole "
            "feeds energy to the orbit (e.g. a*=0.9: r_crit=1.74 < ISCO=2.32, Omega_orbit=0.225 < "
            "Omega_H=0.313). A horizonless ECO has NO horizon flux of either sign, so the inspiral "
            "gravitational-wave phase differs: horizon tidal heating is the ABSORPTION channel of the "
            "'is it a black hole?' test, complementing the static Love number (v2.235) and the "
            "ringdown echoes (v2.247), and it ties the horizon-test and superradiance suites together "
            "through the shared Omega_H."
        ),
        "honest_scope": (
            "The flux SIGN and the critical radius (Omega_orbit vs Omega_H) are exact-Kerr geodesic "
            "results (verified). The flux MAGNITUDE and the actual GW PHASE shift (the observable that "
            "distinguishes BH from ECO in an inspiral) require the full Teukolsky horizon flux and its "
            "post-Newtonian expansion -- horizon absorption enters the phase at 2.5PN for "
            "Schwarzschild and 1.5PN (spin-enhanced) for Kerr -- not computed here. Equatorial, "
            "adiabatic circular inspiral; the l=m=2 dominant tidal coupling. ECO absorption is set to "
            "zero (a perfectly reflecting surface); partial reflectivity interpolates. Reconstruction "
            "of a real horizon observable, not a detection forecast. Parity-odd g_R4_c3 stays dark "
            "(v2.209)."
        ),
        "references": [
            "Hartle (1973); Poisson & Sasaki (1995) -- tidal heating of a Kerr horizon",
            "Hughes, PRD 64 (2001) 064004 -- horizon flux and the inspiral",
            "Maselli et al., PRL 120 (2018) 081101 -- tidal heating as a horizon test (BH vs ECO)",
            "this repo: v2.243-v2.246 (superradiance / Omega_H), v2.235 (tidal Love number)",
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
    print(" a*     Omega_H   r_crit   r_ISCO   Omega_orb(ISCO)   regime at ISCO")
    for r in res["spin_sequence"]:
        print(f" {r['a_star']:.2f}   {r['Omega_H']:.4f}   {r['r_crit']:.3f}   "
              f"{r['r_isco_prograde']:.3f}   {r['Omega_orbit_isco']:.4f}          {r['regime_at_isco']}")
    print(f"regime crossover near a* = {res['regime_crossover_near_spin']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
