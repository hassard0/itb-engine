"""v2.237 - The ISCO and accretion efficiency: the matter-orbit companion to the photon sphere.

A fresh self-contained observable. Where the photon sphere (r = 3M) governs light (ringdown,
shadow), the innermost stable circular orbit (ISCO, r = 6M) governs MATTER: it is the inner edge of
a thin accretion disk (set by where stable circular orbits end) and the binding energy released down
to it fixes the radiative efficiency. The ISCO is doubly observable -- electromagnetically (the inner
disk edge, X-ray continuum fitting / EHT) and gravitationally (the inspiral-to-merger transition
frequency) -- so, like the photon sphere<->shadow link (v2.230), it is a multi-messenger probe; a
non-Kerr / higher-curvature deformation shifts it.

Timelike circular geodesics of a static metric ds^2 = -f dt^2 + f^{-1} dr^2 + r^2 dOmega^2 have
energy per unit mass E(r) = sqrt(2 f^2 / (2f - r f')); the ISCO is the marginally stable orbit, the
MINIMUM of E(r) along the circular sequence. The accretion efficiency is eta = 1 - E_ISCO and the
orbital frequency is Omega = sqrt(f'/(2r)). For Schwarzschild: r_ISCO = 6M, E = sqrt(8/9),
eta = 1 - sqrt(8/9) ~ 5.72%, Omega = 1/(6 sqrt6 M).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

VERSION = "v2.237"
DEFAULT_OUT = Path("experiments/results/v2.237/qnm_isco_accretion.json")


def circular_energy(r: float, eps: float, k: int) -> float:
    """Energy per unit mass of a timelike circular orbit; f = 1 - 2/r + eps/r^k (M=1)."""
    f = 1 - 2 / r + eps / r**k
    fp = 2 / r**2 - k * eps / r**(k + 1)
    denom = 2 * f - r * fp
    if denom <= 0 or f <= 0:
        return math.inf
    return math.sqrt(2 * f**2 / denom)


def isco(eps: float = 0.0, k: int = 3) -> dict:
    """ISCO radius, energy, efficiency, orbital frequency = the minimum of E(r)."""
    res = minimize_scalar(lambda r: circular_energy(r, eps, k), bounds=(3.5, 30.0),
                          method="bounded", options={"xatol": 1e-11})
    r = res.x
    E = circular_energy(r, eps, k)
    fp = 2 / r**2 - k * eps / r**(k + 1)
    return {"r_isco": r, "E_isco": E, "efficiency": 1 - E, "Omega_isco": math.sqrt(fp / (2 * r))}


def run() -> dict:
    base = isco(0.0)
    closed = {"r_isco": 6.0, "E_isco": math.sqrt(8 / 9), "efficiency": 1 - math.sqrt(8 / 9),
              "Omega_isco": 1 / (6 * math.sqrt(6))}
    match = {k: bool(abs(base[k] - closed[k]) < 1e-5) for k in closed}
    # deformation sensitivities
    h = 1e-4
    sens = {}
    for k in (3, 4):
        p, m = isco(h, k), isco(-h, k)
        sens[f"k={k}"] = {q + "_d_eps": (p[q] - m[q]) / (2 * h)
                          for q in ("r_isco", "efficiency", "Omega_isco")}
    return {
        "version": VERSION,
        "method": ("timelike circular-orbit energy E(r)=sqrt(2f^2/(2f-rf')) of a static metric; "
                   "ISCO = argmin E(r); efficiency eta=1-E_ISCO; Omega=sqrt(f'/(2r)); deformation "
                   "f=1-2/r+eps/r^k; M=1"),
        "schwarzschild": base,
        "closed_form": closed,
        "matches_closed_form": match,
        "all_match": all(match.values()),
        "deformation_sensitivity": sens,
        "finding": (
            f"The Schwarzschild ISCO is reproduced exactly from first principles: r_ISCO = "
            f"{base['r_isco']:.4f} (=6M), E_ISCO = {base['E_isco']:.5f} (=sqrt(8/9)), radiative "
            f"efficiency eta = {base['efficiency']:.4f} (~5.72%), Omega_ISCO = "
            f"{base['Omega_isco']:.5f} (=1/(6 sqrt6 M)). A near-horizon / higher-curvature "
            "deformation shifts it: an eps/r^3 bump SHRINKS the ISCO (dr/d eps = -0.53), RAISING "
            "both the accretion efficiency (d eta/d eps = +0.0044) and the orbital frequency "
            "(d Omega/d eps = +0.0076); an eps/r^4 bump does the same but weaker (more localized). "
            "Because the ISCO is the inner accretion-disk edge (EM: X-ray continuum / EHT) AND the "
            "inspiral-to-merger transition frequency (GW), this is a multi-messenger probe -- the "
            "matter-orbit companion to the photon-sphere<->shadow link (v2.230): a deformation "
            "moves the disk efficiency and the merger frequency coherently."
        ),
        "honest_scope": (
            "Schwarzschild baseline (exact) + linear deformation response, equatorial circular "
            "timelike geodesics of a static spherical metric in the g_tt g_rr = -1 gauge. Kerr "
            "(spin) shifts the ISCO strongly (prograde down to r=M, efficiency up to ~42%) and "
            "breaks sphericity -- not included. The deformation profile (eps/r^k) is illustrative, "
            "not a derived QG metric; the efficiency assumes a standard thin disk radiating the "
            "binding energy. This frames a multi-messenger test (a deformation correlates the disk "
            "efficiency and merger frequency), not a coupling bound. Parity-odd g_R4_c3 stays dark "
            "(v2.209)."
        ),
        "references": [
            "Bardeen, Press, Teukolsky, ApJ 178 (1972) 347 -- circular geodesics / ISCO / efficiency",
            "Novikov & Thorne (1973) -- thin-disk radiative efficiency",
            "this repo: v2.230 (photon-sphere<->shadow multi-messenger), v2.231 (deviation null test)",
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
    b = res["schwarzschild"]
    print(f"Schwarzschild ISCO: r={b['r_isco']:.5f} E={b['E_isco']:.6f} "
          f"eta={b['efficiency']:.5f} Omega={b['Omega_isco']:.6f}  all_match={res['all_match']}")
    for k, s in res["deformation_sensitivity"].items():
        print(f"  {k}: dr/deps={s['r_isco_d_eps']:+.4f} deta/deps={s['efficiency_d_eps']:+.5f} "
              f"dOmega/deps={s['Omega_isco_d_eps']:+.5f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
