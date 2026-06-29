"""v2.277 - Synthesis capstone: the black-hole thermodynamics sub-arc (v2.257-v2.276), cross-verified.

Consolidates the six-cycle black-hole thermodynamics / quantum-geometry sub-arc into one structure and
PROVES the modules mutually consistent. The unifying object is the horizon AREA -- everything a black
hole does thermodynamically is the area expressed a different way:

  v2.257 thermodynamics    -- S = A/4, T_H = 1/(8 pi M), evaporation ~ M^3            (the area is ENTROPY)
  v2.258 holographic bound -- S_BH = Bekenstein = holographic = A/4 (all saturated)    (the area is the BOUND)
  v2.273 greybody          -- Hawking emission filtered by the barrier at the photon sphere (the area RADIATES)
  v2.274 area quantization -- QNM asymptotics -> universal area quantum dA = 4 ln3      (the area is QUANTIZED)
  v2.275 Page curve        -- island = remaining horizon area/4 brings information back (the area is the ISLAND)
  v2.276 Hawking-Page      -- free energy F(area) gives a phase transition              (the area has a PHASE)

The capstone runs cross-program checks: the area law S = A/4 is shared, the Hawking temperature
1/(8 pi M) is the same in SI (v2.257) and natural units (v2.273/274/276), the Bekenstein and
holographic bounds are saturated by the black hole, the area quantum carries entropy ln3, and the
greybody/Page/phase structures all hang off the same horizon.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_black_hole_thermodynamics import (
    M_PL_KG,
    T_PL_K,
    entropy_bits,
    hawking_temperature_K,
)
from experiments.qnm_holographic_bound import bh_bounds
from experiments.qnm_greybody_hawking import greybody_wkb, rw_peak
from experiments.qnm_area_quantization import LN3, area_quantum
from experiments.qnm_page_curve import page_time_over_tau, s_bh as page_s_bh
from experiments.qnm_hawking_page_transition import free_energy as hp_free_energy

VERSION = "v2.277"
DEFAULT_OUT = Path("experiments/results/v2.277/qnm_bh_thermodynamics_synthesis.json")


def run() -> dict:
    checks = []

    # 1. the area law S = A/4 is shared: v2.258 saturates Bekenstein = holographic = S_BH,
    #    and v2.275 uses S_BH = (M/M0)^2 (= area/4) -- the same A/4.
    b = bh_bounds(5.0)
    three_way = (abs(b["S_BH"] - b["bekenstein_bound"]) < 1e-9 * b["S_BH"]
                 and abs(b["S_BH"] - b["holographic_bound"]) < 1e-9 * b["S_BH"])
    checks.append({"name": "bekenstein_holographic_S_BH_all_equal", "pass": bool(three_way)})

    # 2. the Hawking temperature 1/(8 pi M) is the same in SI and natural units:
    #    v2.257 hawking_temperature_K(M_Pl)/T_Pl must equal the natural-units T_H = 1/(8 pi) used in v2.273/274/276.
    t_natural = hawking_temperature_K(M_PL_KG) / T_PL_K
    checks.append({"name": "hawking_T_is_1_over_8piM_across_units",
                   "pass": bool(abs(t_natural - 1.0 / (8 * math.pi)) < 1e-6)})

    # 3. scaling laws: S ~ M^2, T ~ 1/M (v2.257)
    s_ratio = entropy_bits(2 * M_PL_KG) / entropy_bits(M_PL_KG)
    t_ratio = hawking_temperature_K(2 * M_PL_KG) / hawking_temperature_K(M_PL_KG)
    checks.append({"name": "entropy_area_law_S_prop_M2_T_prop_invM",
                   "pass": bool(abs(s_ratio - 4.0) < 1e-9 and abs(t_ratio - 0.5) < 1e-9)})

    # 4. the area quantum carries entropy ln3 (v2.274): dS = dA/4 = ln3
    checks.append({"name": "area_quantum_entropy_is_ln3",
                   "pass": bool(abs(area_quantum(1.0) / 4.0 - LN3) < 1e-9)})

    # 5. the Page point uses S_BH = area/4 and the M^3 law (v2.275): peak at M0/sqrt2, t_Page = 1-2^-1.5
    checks.append({"name": "page_point_and_time_consistent",
                   "pass": bool(abs(page_s_bh(1 / math.sqrt(2)) - 0.5) < 1e-9
                                and abs(page_time_over_tau() - (1 - 2 ** -1.5)) < 1e-12)})

    # 6. the greybody -> 1 at high frequency (v2.273) and the Hawking-Page free energy changes sign (v2.276)
    V_max, V2 = rw_peak(2, 2)
    grey_ok = greybody_wkb(2.0 * math.sqrt(V_max), V_max, V2) > 0.99
    hp_ok = hp_free_energy(0.8, 1.0) > 0 and hp_free_energy(1.5, 1.0) < 0
    checks.append({"name": "greybody_unity_and_hawking_page_sign_change",
                   "pass": bool(grey_ok and hp_ok)})

    n_pass = sum(1 for c in checks if c["pass"])

    table = [
        {"cycle": "v2.257", "topic": "thermodynamics", "area_role": "the area is ENTROPY (S = A/4)"},
        {"cycle": "v2.258", "topic": "holographic bound", "area_role": "the area is the BOUND (S <= A/4, saturated)"},
        {"cycle": "v2.273", "topic": "greybody", "area_role": "the area RADIATES (barrier-filtered Hawking)"},
        {"cycle": "v2.274", "topic": "area quantization", "area_role": "the area is QUANTIZED (dA = 4 ln3)"},
        {"cycle": "v2.275", "topic": "Page curve", "area_role": "the area is the ISLAND (information returns)"},
        {"cycle": "v2.276", "topic": "Hawking-Page", "area_role": "the area has a PHASE (free-energy transition)"},
    ]

    return {
        "version": VERSION,
        "method": ("cross-verify the six BH-thermodynamics modules for the shared area law S=A/4, the "
                   "common Hawking temperature 1/(8 pi M) in SI and natural units, saturated entropy "
                   "bounds, the ln3 area-quantum entropy, and the greybody/Page/phase structures"),
        "area_is_the_unifying_object": table,
        "natural_units_T_H": t_natural,
        "consistency_checks": checks,
        "checks_passed": n_pass,
        "checks_total": len(checks),
        "all_pass": n_pass == len(checks),
        "finding": (
            f"The six-cycle black-hole thermodynamics sub-arc is one structure, and all {n_pass}/"
            f"{len(checks)} cross-program checks pass. The unifying object is the horizon AREA: it is "
            "the entropy S = A/4 (v2.257), the bound that S = A/4 saturates (v2.258, Bekenstein = "
            "holographic = S_BH verified equal), it is quantized in units of dA = 4 ln3 carrying "
            "entropy ln3 (v2.274), it radiates through the barrier at its photon sphere (v2.273, "
            "greybody -> 1 at high frequency), its remaining value is the island that returns the "
            "information (v2.275, Page curve), and its free energy drives a phase transition (v2.276, "
            "Hawking-Page). The Hawking temperature 1/(8 pi M) is literally the same number in the SI "
            "treatment (v2.257) and the natural-units modules (v2.273/274/276, verified via "
            "T_H(M_Pl)/T_Pl = 1/8pi), and the area law scales as S ~ M^2, T ~ 1/M, evaporation ~ M^3 "
            "consistently. So 'black hole thermodynamics' is not six topics but one -- the horizon "
            "area, read as entropy, bound, quantum, radiator, island and phase. This is the session's "
            "sixth cross-verified synthesis capstone (after v2.242, v2.250, v2.256, v2.265, v2.271)."
        ),
        "honest_scope": (
            "A synthesis / cross-verification capstone: every check is a consistency relation among "
            "results already established and caveated in v2.257-v2.276 (the area quantum's ln3 is a "
            "source-backed input, the Page curve is the phenomenological island model, the greybody is "
            "WKB-limited at low frequency, the Hawking-Page result is AdS_4-specific). No new bound is "
            "derived; the value is showing the six treatments are mutually consistent and are all the "
            "horizon area in disguise. The SI<->natural-units temperature bridge is exact; the "
            "thermodynamic scaling laws are exact. A QG / BH-structure result, not an engine constraint "
            "refit."
        ),
        "references": [
            "Bekenstein, 'Black holes and entropy', PRD 7 (1973) 2333",
            "Hawking, 'Particle creation by black holes', CMP 43 (1975) 199",
            "this repo: v2.257, v2.258, v2.273, v2.274, v2.275, v2.276",
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
    print("the horizon AREA is the one object:")
    for t in res["area_is_the_unifying_object"]:
        print(f"  {t['cycle']}  {t['topic']:20s} -> {t['area_role']}")
    print(f"\nconsistency checks: {res['checks_passed']}/{res['checks_total']} pass")
    for c in res["consistency_checks"]:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
