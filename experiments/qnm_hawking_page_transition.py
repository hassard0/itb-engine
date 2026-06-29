"""v2.276 - The Hawking-Page transition: black holes have a phase diagram (and it is holographic).

A fresh QG thermodynamics probe completing the black-hole-entropy sub-arc (v2.257/v2.273/v2.274/v2.275).
Unlike an asymptotically-flat black hole (which has negative specific heat and cannot be in stable
equilibrium), a Schwarzschild-AdS black hole has a genuine PHASE DIAGRAM. For the AdS_4 metric
f(r) = 1 - 2M/r + r^2/L^2 with horizon r_+ (f(r_+)=0, so 2M = r_+ + r_+^3/L^2):

    T(r_+)   = (1/4pi)(1/r_+ + 3 r_+/L^2)        (Hawking temperature)
    M(r_+)   = (r_+/2)(1 + r_+^2/L^2)            (mass)
    S(r_+)   = pi r_+^2                           (entropy = area/4)
    F(r_+)   = M - T S = (r_+/4)(1 - r_+^2/L^2)   (free energy, relative to thermal AdS)

Three facts make the phase diagram: (1) T(r_+) has a MINIMUM at r_+ = L/sqrt3, so below
T_min = sqrt3/(2 pi L) no black hole exists at all; (2) the specific heat dM/dT changes sign there --
the small branch (r_+ < L/sqrt3) is unstable, the large branch is stable; (3) the free energy F
changes sign at r_+ = L, the HAWKING-PAGE point T_HP = 1/(pi L): below it thermal AdS dominates
(F > 0, black hole metastable), above it the large black hole dominates (F < 0). Witten showed this is
the gravity dual of the CONFINEMENT-DECONFINEMENT transition of the boundary gauge theory.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.276"
DEFAULT_OUT = Path("experiments/results/v2.276/qnm_hawking_page_transition.json")


def temperature(r: float, L: float = 1.0) -> float:
    return (1.0 / (4.0 * math.pi)) * (1.0 / r + 3.0 * r / L**2)


def mass(r: float, L: float = 1.0) -> float:
    return 0.5 * r * (1.0 + r**2 / L**2)


def entropy(r: float) -> float:
    return math.pi * r**2


def free_energy(r: float, L: float = 1.0) -> float:
    return mass(r, L) - temperature(r, L) * entropy(r)


def specific_heat(r: float, L: float = 1.0, h: float = 1e-6) -> float:
    """C = dM/dT = (dM/dr)/(dT/dr) via central differences (diverges at the temperature minimum)."""
    dM = (mass(r + h, L) - mass(r - h, L)) / (2 * h)
    dT = (temperature(r + h, L) - temperature(r - h, L)) / (2 * h)
    if abs(dT) < 1e-12:
        return math.copysign(float("inf"), dM)
    return dM / dT


def run() -> dict:
    L = 1.0
    r_min = L / math.sqrt(3.0)          # temperature minimum / specific-heat sign change
    r_hp = L                            # Hawking-Page point (F = 0)
    T_min = math.sqrt(3.0) / (2 * math.pi * L)
    T_hp = 1.0 / (math.pi * L)

    # 1. temperature minimum at r = L/sqrt3
    dT_at_min = (temperature(r_min + 1e-6, L) - temperature(r_min - 1e-6, L)) / 2e-6
    temp_min_ok = (abs(dT_at_min) < 1e-4 and abs(temperature(r_min, L) - T_min) < 1e-9)

    # 2. free energy closed form F = (r/4)(1 - r^2/L^2)
    fe_closed = all(abs(free_energy(r, L) - (r / 4.0) * (1 - r**2 / L**2)) < 1e-9
                    for r in (0.4, 0.7, 1.0, 1.5, 2.0))

    # 3. F changes sign at r = L (Hawking-Page): F>0 below, F<0 above
    hp_sign = (abs(free_energy(r_hp, L)) < 1e-9 and free_energy(1.5, L) < 0 and free_energy(0.8, L) > 0)

    # 4. T_HP = 1/(pi L) and exceeds T_min
    t_hp_ok = (abs(temperature(r_hp, L) - T_hp) < 1e-9 and T_hp > T_min)

    # 5. specific heat sign change at r = L/sqrt3 (small unstable, large stable)
    C_small = specific_heat(0.4, L)
    C_large = specific_heat(1.5, L)
    heat_sign = (C_small < 0 and C_large > 0)

    def phase_of(r: float) -> str:
        if r < r_min:
            return "small branch (unstable, C<0)"
        if r < r_hp:
            return "large branch, thermal AdS dominates (F>0)"
        return "large branch, black hole dominates (F<0)"

    # sample away from r_min (where C diverges) to keep the table finite/JSON-clean
    branches = [{"r_plus": r, "T": temperature(r, L), "F": free_energy(r, L),
                 "C": specific_heat(r, L), "phase": phase_of(r)}
                for r in (0.4, 0.5, 0.8, 1.0, 1.5, 2.5)]

    checks = {
        "temperature_has_minimum_at_L_over_sqrt3": temp_min_ok,
        "free_energy_closed_form": fe_closed,
        "hawking_page_free_energy_sign_change_at_rL": hp_sign,
        "T_HP_is_one_over_piL_above_Tmin": t_hp_ok,
        "specific_heat_sign_change": heat_sign,
    }

    return {
        "version": VERSION,
        "method": ("Schwarzschild-AdS_4 thermodynamics: T=(1/4pi)(1/r_+ + 3r_+/L^2), M=(r_+/2)(1+r_+^2/L^2), "
                   "S=pi r_+^2, F=M-TS=(r_+/4)(1-r_+^2/L^2); minima/sign-changes give the phase diagram (L=1)"),
        "L": L,
        "r_temperature_min": r_min, "T_min": T_min,
        "r_hawking_page": r_hp, "T_hawking_page": T_hp,
        "branch_table": branches,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "ads_cft_dual": ("the Hawking-Page transition is the gravity dual of the confinement-"
                         "deconfinement transition of the boundary gauge theory (Witten 1998): thermal "
                         "AdS = confined phase, large black hole = deconfined phase"),
        "finding": (
            "A Schwarzschild-AdS black hole has a real phase diagram, unlike its asymptotically-flat "
            "cousin. The Hawking temperature T(r_+) = (1/4pi)(1/r_+ + 3 r_+/L^2) has a MINIMUM at "
            f"r_+ = L/sqrt3, T_min = sqrt3/(2 pi L) ~ {T_min:.4f} (L=1): below T_min no black hole "
            "exists. The specific heat dM/dT changes sign there (verified) -- the small branch is "
            "thermodynamically UNSTABLE (negative C, like a flat-space hole), the large branch STABLE "
            "(positive C, it can sit in a heat bath). The free energy relative to thermal AdS is "
            "exactly F = (r_+/4)(1 - r_+^2/L^2) (verified against M - T S), which changes sign at the "
            f"HAWKING-PAGE point r_+ = L, T_HP = 1/(pi L) ~ {T_hp:.4f}: below T_HP thermal AdS wins "
            "(F > 0, the black hole is metastable), above it the large black hole dominates (F < 0). "
            "So there is a first-order phase transition between empty thermal AdS and a big black "
            "hole. Witten's insight makes it holographic: this is the gravity dual of the "
            "confinement-deconfinement transition of the boundary gauge theory -- thermal AdS is the "
            "confined phase, the black hole the deconfined plasma. It completes the BH-thermodynamics "
            "sub-arc: the v2.257 entropy and v2.275 Page curve described a single evaporating hole; "
            "here the hole has a genuine equilibrium phase structure with a sharp, holographically "
            "meaningful transition."
        ),
        "honest_scope": (
            "Exact textbook Schwarzschild-AdS_4 thermodynamics (Hawking-Page 1983; Witten 1998): the "
            "temperature, mass, entropy and free-energy formulas and all the derived critical points "
            "(r_+ = L/sqrt3 minimum, r_+ = L transition) are analytic and verified to machine "
            "precision. L=1 units; AdS_4 (the AdS_5/CFT_4 case shifts the numeric coefficients but not "
            "the structure). The AdS/CFT confinement-deconfinement identification is Witten's result, "
            "cited not re-derived (it needs the boundary-gauge-theory partition function). A "
            "BH-thermodynamics / holography result, not an engine constraint refit; the engine encodes "
            "asymptotically-flat / cosmological constraints, so this AdS phase structure is a "
            "companion piece, not an engine coupling."
        ),
        "references": [
            "Hawking, Page, 'Thermodynamics of black holes in anti-de Sitter space', Commun. Math. Phys. 87 (1983) 577",
            "Witten, 'Anti-de Sitter space, thermal phase transition, and confinement in gauge theories', ATMP 2 (1998) 505",
            "this repo: v2.257 (BH thermodynamics), v2.275 (Page curve), v2.258 (holographic bound)",
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
    print("Hawking-Page transition (Schwarzschild-AdS_4, L=1):")
    print(f"  T_min = sqrt3/(2pi) = {res['T_min']:.4f} at r_+ = L/sqrt3 = {res['r_temperature_min']:.4f}")
    print(f"  T_HP  = 1/pi        = {res['T_hawking_page']:.4f} at r_+ = L = {res['r_hawking_page']:.4f}")
    print("  r_+      T        F          C         phase")
    for b in res["branch_table"]:
        print(f"  {b['r_plus']:.4f}   {b['T']:.4f}   {b['F']:+.4f}    {b['C']:+8.2f}   {b['phase']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
