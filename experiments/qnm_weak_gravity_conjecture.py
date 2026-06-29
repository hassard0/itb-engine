"""v2.254 - The Weak Gravity Conjecture: 'gravity is the weakest force' as a QG-consistency test.

A fresh QG-CONSISTENCY (swampland) probe, reconnecting to the engine's distance_conjecture /
eft_validity sector. Quantum gravity is conjectured to forbid stable extremal charged black-hole
remnants: an extremal Reissner-Nordstrom hole has charge equal to mass (Q = M in Planck units, the
two horizons merging at r_+ = M), and for it to DISCHARGE there must exist a particle with
charge-to-mass ratio q/m >= the extremal ratio (= 1, suitably normalized). Equivalently the gauge
repulsion must beat the gravitational attraction -- "gravity is the weakest force":

    z = q g M_Pl / m  >=  1 ,        force ratio  F_gauge / F_grav = z^2 ,

with g = sqrt(4 pi alpha) ~ 0.303 the U(1) coupling. An effective field theory with NO such
super-extremal state is in the SWAMPLAND (not UV-completable in quantum gravity). The complementary
"magnetic" WGC bounds the EFT cutoff, Lambda <~ g M_Pl (the monopole scale).

This cycle verifies that every Standard-Model charged particle satisfies the WGC by enormous margins
(so the SM is comfortably consistent with this QG criterion) and frames the swampland connection.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.254"
DEFAULT_OUT = Path("experiments/results/v2.254/qnm_weak_gravity_conjecture.json")
M_PL_eV = 1.22e28
ALPHA = 1 / 137.036
G_U1 = math.sqrt(4 * math.pi * ALPHA)     # e = sqrt(4 pi alpha) ~ 0.303


def wgc_ratio(m_eV: float, q: float = 1.0) -> float:
    """Super-extremality parameter z = q g M_Pl / m (>= 1 satisfies the WGC)."""
    return q * G_U1 * M_PL_eV / m_eV


def run() -> dict:
    particles = [("electron", 0.511e6), ("muon", 105.7e6), ("tau", 1776.9e6),
                 ("up quark", 2.2e6), ("proton", 938.3e6)]
    rows = []
    for name, m in particles:
        z = wgc_ratio(m)
        rows.append({"particle": name, "mass_eV": m, "wgc_ratio_z": z,
                     "force_ratio_gauge_over_grav": z**2, "satisfies_wgc": bool(z >= 1)})
    cutoff = G_U1 * M_PL_eV
    return {
        "version": VERSION,
        "method": ("WGC super-extremality z = q g M_Pl/m (g=sqrt(4 pi alpha)); extremal RN Q=M; "
                   "magnetic-WGC cutoff Lambda <~ g M_Pl; M_Pl=1.22e28 eV, alpha=1/137"),
        "gauge_coupling_g": G_U1,
        "particles": rows,
        "all_satisfy_wgc": all(r["satisfies_wgc"] for r in rows),
        "magnetic_wgc_cutoff_eV": cutoff,
        "extremal_rn": {"condition": "Q = M (Planck units)", "horizon": "r_+ = M (horizons merge)",
                        "discharge_requires": "a state with q/m > 1 (super-extremal)"},
        "finding": (
            "The Weak Gravity Conjecture -- 'gravity is the weakest force', the requirement that "
            "extremal charged black holes can discharge -- is satisfied by EVERY Standard-Model "
            f"charged particle by enormous margins: the electron has z = q g M_Pl/m = "
            f"{rows[0]['wgc_ratio_z']:.1e}, so its electromagnetic force exceeds its gravity by "
            f"z^2 = {rows[0]['force_ratio_gauge_over_grav']:.1e} (43 orders of magnitude); the "
            f"heaviest, the proton, still has z = {rows[-1]['wgc_ratio_z']:.1e}. So the SM sits "
            "deep in the WGC-allowed region -- comfortably consistent with this quantum-gravity "
            "consistency criterion, and far from the swampland boundary z = 1 where an EFT with no "
            "super-extremal state would be UV-incompletable. The magnetic WGC additionally bounds the "
            f"EFT cutoff Lambda <~ g M_Pl = {cutoff:.1e} eV (near Planck). This is a QG-CONSISTENCY "
            "probe (does the low-energy theory admit a quantum-gravity completion?), complementing "
            "the session's QG-PHENOMENOLOGY probes (what does QG predict observably?) -- and it ties "
            "to the engine's distance_conjecture / eft_validity swampland sector."
        ),
        "honest_scope": (
            "The WGC is a well-motivated CONJECTURE, not a theorem (proven only in special cases / "
            "from black-hole entropy and unitarity arguments). The precise 'extremal' normalization "
            "and the MILD (one super-extremal state) vs STRONG/TOWER/lattice forms differ by O(1) and "
            "in scope; z >= 1 here uses the leading extremal ratio. The SM verification is exact "
            "given the masses and alpha (low-energy alpha used; it runs). Multi-U(1) / dilatonic "
            "convex-hull refinements are not included. Self-contained reconstruction of a real "
            "swampland criterion, not a new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Arkani-Hamed, Motl, Nicolis, Vafa, JHEP 06 (2007) 060 -- the Weak Gravity Conjecture",
            "Harlow, Heidenreich, Reece, Rudelius, Rev. Mod. Phys. 95 (2023) 035003 -- WGC review",
            "this repo: engine distance_conjecture / eft_validity (swampland sector)",
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
    print("particle      q/m (Planck)    force ratio (q/m)^2    WGC?")
    for r in res["particles"]:
        print(f"  {r['particle']:10s}  {r['wgc_ratio_z']:.2e}       {r['force_ratio_gauge_over_grav']:.2e}"
              f"           {'YES' if r['satisfies_wgc'] else 'NO'}")
    print(f"all satisfy WGC = {res['all_satisfy_wgc']}; magnetic cutoff Lambda <~ {res['magnetic_wgc_cutoff_eV']:.1e} eV")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
