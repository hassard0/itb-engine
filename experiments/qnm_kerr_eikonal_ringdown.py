"""v2.240 - The eikonal Kerr ringdown from the photon orbit: how spin sets the QNM frequency.

Connects the Kerr strong-field thread (v2.239) back to ringdown. In the eikonal (large-l) limit, a
Kerr quasinormal mode is governed by the corresponding spherical photon orbit (Yang, Zimmerman,
Zhang, Berti, Chen 2012, the Kerr generalization of v2.229): for the dominant co-rotating l=m modes
the relevant orbit is the EQUATORIAL photon orbit, and

    omega_R  ~  (l + 1/2) * Omega_ph(a) ,     Omega_ph(a) = 1 / (r_ph(a)^{3/2} +/- a)   (M=1),

with +a for the prograde orbit and -a for the retrograde one (r_ph from v2.239). So the ringdown
frequency tracks the photon-orbit orbital frequency, which RISES with prograde spin and FALLS
retrograde -- the physics by which LIGO/Virgo infers the FINAL black hole's spin from the ringdown.
The v2.238 Schwarzschild shadow<->ringdown locking (Omega_c = 1/b_c, a single value) is fully SPLIT
by spin into distinct prograde and retrograde ringdown frequencies.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_kerr_strong_field import photon_radius

VERSION = "v2.240"
DEFAULT_OUT = Path("experiments/results/v2.240/qnm_kerr_eikonal_ringdown.json")
SPINS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.998]


def omega_ph(a: float, prograde: bool = True) -> float:
    """Equatorial photon-orbit angular velocity = the eikonal ringdown frequency per (l+1/2)."""
    r = photon_radius(a, prograde)
    return 1.0 / (r**1.5 + a) if prograde else 1.0 / (r**1.5 - a)


def run() -> dict:
    rows = []
    for a in SPINS:
        op, orr = omega_ph(a, True), omega_ph(a, False)
        rows.append({"a": a, "Omega_ph_prograde": op, "Omega_ph_retrograde": orr,
                     "eikonal_omegaR_l2_prograde": 2.5 * op,       # (l+1/2)=2.5 for l=2
                     "eikonal_omegaR_l2_retrograde": 2.5 * orr})
    a0 = rows[0]
    schw_ok = abs(a0["Omega_ph_prograde"] - 1 / (3 * math.sqrt(3))) < 1e-9
    pro = [r["Omega_ph_prograde"] for r in rows]
    retro = [r["Omega_ph_retrograde"] for r in rows]
    pro_monotone = all(pro[i + 1] > pro[i] for i in range(len(pro) - 1))
    retro_monotone = all(retro[i + 1] < retro[i] for i in range(len(retro) - 1))
    return {
        "version": VERSION,
        "method": ("eikonal Kerr QNM frequency from the equatorial photon orbit (Yang et al. 2012, "
                   "Kerr generalization of v2.229): omega_R ~ (l+1/2) Omega_ph, "
                   "Omega_ph = 1/(r_ph^{3/2} +/- a); M=1"),
        "schwarzschild_limit_ok": bool(schw_ok),
        "spin_sequence": rows,
        "prograde_frequency_rises_with_spin": bool(pro_monotone),
        "retrograde_frequency_falls_with_spin": bool(retro_monotone),
        "extremal_prograde_Omega_ph": omega_ph(1.0, True),
        "finding": (
            "The eikonal ringdown frequency tracks the equatorial photon-orbit frequency, which "
            f"reproduces Schwarzschild at a=0 (Omega_ph = {a0['Omega_ph_prograde']:.5f} = 1/(3 "
            "sqrt3)) and SPLITS under spin: the prograde branch RISES monotonically to the extremal "
            f"Omega_ph = {omega_ph(1.0, True):.3f} (the per-(l+1/2) ringdown frequency ~2.6x the "
            "Schwarzschild value), while the retrograde branch FALLS to ~0.143. So a higher-spin "
            "(prograde) remnant rings at a HIGHER frequency -- this is the spin dependence LIGO/Virgo "
            "fits to measure the final black hole's spin from the dominant ringdown mode, and it is "
            "the photon-orbit origin (v2.239) of that measurement. The single Schwarzschild "
            "shadow<->ringdown locking (v2.238) is now two distinct prograde/retrograde frequencies."
        ),
        "honest_scope": (
            "Eikonal (large-l), equatorial co-rotating (l=m) modes, exact Kerr photon orbits. The "
            "eikonal OVERESTIMATES the l=2 frequency by the usual O(1/l) (~22% at a=0, v2.229) -- the "
            "value is the large-l LIMIT and the SPIN TREND, not a precise omega_220(a) (that needs "
            "the Teukolsky/Leaver solver, the deferred effort). The damping follows the same orbit's "
            "Lyapunov rate (computed for Schwarzschild in v2.229; the Kerr equatorial Lyapunov "
            "exponent is the natural extension, not done here). This connects v2.239's photon orbits "
            "to the ringdown frequency; it is not a new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Yang, Zimmerman, Zhang, Berti, Chen, PRD 86 (2012) 104006 -- eikonal Kerr QNM / photon orbits",
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- Kerr QNM spin dependence",
            "this repo: v2.239 (Kerr photon orbits / ISCO), v2.229 (Schwarzschild eikonal correspondence)",
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
    print(" a       Omega_ph(pro/retro)    eikonal omega_R l=2 (pro/retro)")
    for r in res["spin_sequence"]:
        print(f" {r['a']:.3f}   {r['Omega_ph_prograde']:.5f}/{r['Omega_ph_retrograde']:.5f}     "
              f"{r['eikonal_omegaR_l2_prograde']:.4f}/{r['eikonal_omegaR_l2_retrograde']:.4f}")
    print(f"Schwarzschild limit OK = {res['schwarzschild_limit_ok']}; "
          f"prograde rises = {res['prograde_frequency_rises_with_spin']}; "
          f"retrograde falls = {res['retrograde_frequency_falls_with_spin']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
