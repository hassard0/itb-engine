"""v2.257 - Black-hole thermodynamics: entropy, Hawking temperature, evaporation, and the Page time.

A fresh fundamental-QG thread, reconnecting to the engine's entropy constraints (bh_entropy_positivity,
generalized_second_law, holographic_entropy) and the information paradox touched by the echoes
(v2.247). The defining quantum-gravity facts about a black hole are thermodynamic:

    Bekenstein-Hawking entropy   S = A / (4 l_p^2) = 4 pi (M/M_Pl)^2   (HOLOGRAPHIC: ~ AREA, not volume)
    Hawking temperature          T_H = T_Pl / (8 pi (M/M_Pl))         (~ 1/M -- bigger holes are colder)
    evaporation time             t_evap = 5120 pi (M/M_Pl)^3 t_Pl     (~ M^3)
    Page time                    t_Page ~ t_evap / 2                  (info-recovery turnover)

The entropy being proportional to the horizon AREA (not the enclosed volume) is the holographic
principle -- the deepest hint that quantum gravity is fewer degrees of freedom than a local field
theory. The M^3 evaporation law makes a primordial black hole of a specific mass evaporate exactly
NOW (its final gamma-ray burst a cosmological signal), and the Page time is when the radiated
information must start coming back out -- the quantitative heart of the information paradox.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.257"
DEFAULT_OUT = Path("experiments/results/v2.257/qnm_black_hole_thermodynamics.json")
M_PL_KG = 2.176e-8
T_PL_K = 1.417e32
T_PL_S = 5.391e-44
MSUN_KG = 1.989e30
LN2 = math.log(2)
YR_S = 3.156e7
AGE_YR = 1.38e10
T_CMB_K = 2.725


def entropy_bits(M_kg: float) -> float:
    n = M_kg / M_PL_KG
    return 4 * math.pi * n**2 / LN2


def hawking_temperature_K(M_kg: float) -> float:
    return T_PL_K / (8 * math.pi * (M_kg / M_PL_KG))


def evaporation_time_yr(M_kg: float) -> float:
    n = M_kg / M_PL_KG
    return 5120 * math.pi * n**3 * T_PL_S / YR_S


def mass_evaporating_now_kg() -> float:
    n = (AGE_YR * YR_S / (5120 * math.pi * T_PL_S)) ** (1 / 3)
    return n * M_PL_KG


def run() -> dict:
    objects = [(MSUN_KG, "1 Msun"), (30 * MSUN_KG, "30 Msun (LIGO)"),
               (1e6 * MSUN_KG, "SMBH 1e6 Msun"), (1.73e11, "PBH evaporating now")]
    rows = []
    for M, label in objects:
        rows.append({"object": label, "mass_kg": M, "entropy_bits": entropy_bits(M),
                     "hawking_T_K": hawking_temperature_K(M),
                     "evap_time_yr": evaporation_time_yr(M),
                     "page_time_yr": evaporation_time_yr(M) / 2,
                     "colder_than_cmb": bool(hawking_temperature_K(M) < T_CMB_K)})
    return {
        "version": VERSION,
        "method": ("Bekenstein-Hawking S=4pi(M/M_Pl)^2, T_H=T_Pl/(8pi M/M_Pl), "
                   "t_evap=5120pi(M/M_Pl)^3 t_Pl, Page time ~ t_evap/2; Planck units"),
        "black_holes": rows,
        "mass_evaporating_now_kg": mass_evaporating_now_kg(),
        "holographic": "S ~ horizon AREA (not volume) -- the holographic principle",
        "finding": (
            "Black holes are the most entropic objects in nature: a solar-mass hole stores "
            f"S ~ {entropy_bits(MSUN_KG):.0e} bits (its horizon area in Planck units / 4) and "
            f"evaporates in ~{evaporation_time_yr(MSUN_KG):.0e} years at a Hawking temperature of "
            f"{hawking_temperature_K(MSUN_KG):.0e} K -- far colder than the 2.7 K CMB, so stellar "
            "and larger holes ABSORB more than they radiate today and are not yet evaporating. The "
            "entropy scales as the horizon AREA, not the volume: the holographic principle, the "
            "deepest hint that quantum gravity has far fewer degrees of freedom than a local field "
            "theory. The M^3 evaporation law makes a primordial black hole of M ~ "
            f"{mass_evaporating_now_kg():.1e} kg evaporate exactly now -- its final gamma-ray burst a "
            "cosmological signal (and PBH abundance bound). The Page time (~t_evap/2) is when the "
            "radiated information must start re-emerging to preserve unitarity -- the quantitative "
            "core of the information paradox, the same physics whose horizon-structure resolutions "
            "(echoes, v2.247) the session probed observationally."
        ),
        "honest_scope": (
            "Schwarzschild (non-rotating, uncharged) thermodynamics; the entropy and temperature are "
            "EXACT (Bekenstein-Hawking / Hawking), the evaporation coefficient (5120 pi) is the "
            "single-massless-field greybody result -- the real lifetime depends on the number of "
            "particle species radiated at each temperature (more species -> faster, an O(1-10) "
            "factor), so the PBH-evaporating-now mass is order-of-magnitude (the standard value is a "
            "few 1e11 kg). The Page time / information-recovery is the standard unitary expectation; "
            "the actual mechanism (islands, replica wormholes, firewalls, ECO structure) is "
            "unresolved. Self-contained reconstruction of the standard black-hole thermodynamics, "
            "not a new result. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Bekenstein, PRD 7 (1973) 2333; Hawking, CMP 43 (1975) 199 -- entropy / temperature",
            "Page, PRL 71 (1993) 3743 -- the Page curve / information recovery",
            "'t Hooft (1993); Susskind (1995); Bousso, Rev. Mod. Phys. 74 (2002) 825 -- holography",
            "this repo: v2.247 (black-hole echoes / information paradox); engine entropy constraints",
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
    print("object                  S (bits)     T_H (K)      t_evap (yr)   <CMB?")
    for r in res["black_holes"]:
        print(f"  {r['object']:22s} {r['entropy_bits']:.2e}   {r['hawking_T_K']:.2e}   "
              f"{r['evap_time_yr']:.2e}   {r['colder_than_cmb']}")
    print(f"\nPBH evaporating now: M ~ {res['mass_evaporating_now_kg']:.2e} kg; {res['holographic']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
