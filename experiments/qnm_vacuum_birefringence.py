"""v2.252 - Vacuum birefringence: the energy-dependent parity-violation probe (vs the CMB hint).

Continues the spacetime-structure thread (v2.251) into the PARITY-odd sector, reconnecting to the
engine's cosmic_birefringence / parity_violation constraints. A parity-violating quantum-gravity
term -- the dimension-5 Myers-Pospelov / gravitational-Chern-Simons coupling -- makes the two
CIRCULAR photon polarizations propagate at slightly different speeds, so the linear polarization
plane ROTATES as the wave travels, by an ENERGY-DEPENDENT angle

    Delta chi = xi E^2 D / (2 M_Planck)        (dimension-5, ~E^2) .

If that rotation varies by more than ~1 rad across a source's observed energy band, the net
polarization is washed out -- so MEASURING polarization in a distant source bounds xi:

    xi < 2 M_Planck / [ (E_hi^2 - E_lo^2) D ] .

High-energy gamma-ray-burst polarimetry over Gpc distances gives xi < ~1e-17, a very tight exclusion
of Planck-suppressed energy-dependent parity violation. This is the COMPLEMENT of the engine's
cosmic_birefringence constraint, which is the ENERGY-INDEPENDENT constant CMB rotation beta = 0.34
deg (a ~3.6 sigma HINT of a dimension-4 Chern-Simons coupling, the engine's g_R2_parity): the
parity-odd sector hosts a small constant-rotation HINT AND a strong energy-dependent EXCLUSION --
consistent, because they are different operators.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.252"
DEFAULT_OUT = Path("experiments/results/v2.252/qnm_vacuum_birefringence.json")
M_PL_eV = 1.22e28
HBARC_eV_m = 1.97327e-7
GPC_m = 3.086e25


def xi_bound(E1_eV: float, E2_eV: float, D_m: float) -> float:
    """Depolarization bound on the dim-5 parity-violating coupling xi."""
    D_inv_eV = D_m / HBARC_eV_m
    return 2 * M_PL_eV / ((E2_eV**2 - E1_eV**2) * D_inv_eV)


def rotation_angle(xi: float, E_eV: float, D_m: float) -> float:
    """Vacuum-birefringence rotation Delta chi = xi E^2 D/(2 M_Pl) (radians)."""
    return xi * E_eV**2 * (D_m / HBARC_eV_m) / (2 * M_PL_eV)


def run() -> dict:
    sources = [
        {"label": "GRB polarimetry 0.1-1 MeV, z~1", "E1": 1e5, "E2": 1e6, "D": 3.3 * GPC_m},
        {"label": "GRB polarimetry 0.1-10 MeV, z~1", "E1": 1e5, "E2": 1e7, "D": 3.3 * GPC_m},
        {"label": "AGN/radio keV, z~0.3", "E1": 1e3, "E2": 1e4, "D": 1.0 * GPC_m},
    ]
    rows = [{**s, "xi_bound": xi_bound(s["E1"], s["E2"], s["D"])} for s in sources]
    beta_cmb_rad = 0.34 * math.pi / 180
    return {
        "version": VERSION,
        "method": ("dim-5 Myers-Pospelov vacuum birefringence Delta chi = xi E^2 D/(2 M_Pl); "
                   "depolarization bound xi < 2 M_Pl/((E_hi^2-E_lo^2) D) from polarized sources"),
        "xi_bounds": rows,
        "best_xi_bound": min(r["xi_bound"] for r in rows),
        "cosmic_birefringence_contrast": {
            "beta_deg": 0.34, "beta_rad": beta_cmb_rad,
            "character": "ENERGY-INDEPENDENT constant rotation (dim-4 Chern-Simons, engine g_R2_parity)",
            "status": "~3.6 sigma HINT of nonzero parity violation (Minami-Komatsu / Eskilt-Komatsu)",
        },
        "finding": (
            "The parity-odd sector is probed two complementary ways. (1) ENERGY-DEPENDENT vacuum "
            "birefringence (dim-5 Myers-Pospelov, Delta chi ~ E^2): high-energy GRB polarimetry over "
            f"Gpc distances excludes it at xi < {min(r['xi_bound'] for r in rows):.1e} -- a strong "
            "bound on Planck-suppressed energy-dependent parity violation, and TIGHTER for wider/"
            "higher-energy bands (the E^2 makes 0.1-10 MeV ~100x stronger than 0.1-1 MeV). (2) "
            "ENERGY-INDEPENDENT cosmic birefringence (dim-4 Chern-Simons): a constant CMB rotation "
            "beta = 0.34 deg, a ~3.6 sigma HINT of nonzero parity violation (the engine's "
            "cosmic_birefringence -> g_R2_parity). These are CONSISTENT because they are DIFFERENT "
            "operators: the data permits a small CONSTANT parity violation (the CMB hint) while "
            "EXCLUDING the energy-dependent one (the GRB bound). So 'is parity violated by quantum "
            "gravity?' splits into a constant-rotation hint and an energy-dependent exclusion -- the "
            "energy dependence is the discriminant, and only the high-energy birefringence channel "
            "reaches the Planck-suppressed dimension-5 operator."
        ),
        "honest_scope": (
            "Order-of-magnitude: the depolarization criterion (rotation spread < ~1 rad) and the "
            "light-/comoving-distance approximation set the SCALE; the precise bounds fold in the "
            "cosmological distance integral with (1+z) factors, the source-intrinsic polarization and "
            "its energy dependence, and the detailed polarimetry (GRB polarization measurements are "
            "themselves debated). Dimension-5 (~E^2) leading; the sign of xi is not fixed. The "
            "cosmic-birefringence beta is the published ~3.6 sigma HINT (dominant systematic: "
            "polarization-angle miscalibration), not a discovery, exactly as the engine's "
            "cosmic_birefringence constraint records. Self-contained reconstruction of real "
            "parity-sector probes, not new bounds. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Myers & Pospelov, PRL 90 (2003) 211601 -- dim-5 LIV / vacuum birefringence",
            "Gleiser & Kozameh, PRD 64 (2001) 083007 -- GRB birefringence bound",
            "Minami & Komatsu, PRL 125 (2020) 221301; Eskilt & Komatsu (2022) -- cosmic birefringence beta",
            "this repo: v2.251 (LIV dispersion), engine cosmic_birefringence / parity_violation",
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
    print("source                             xi bound (dim-5 parity LIV)")
    for r in res["xi_bounds"]:
        print(f"  {r['label']:32s} xi < {r['xi_bound']:.2e}")
    cb = res["cosmic_birefringence_contrast"]
    print(f"\ncontrast: cosmic birefringence beta = {cb['beta_deg']} deg ({cb['beta_rad']:.4f} rad), "
          f"{cb['character']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
