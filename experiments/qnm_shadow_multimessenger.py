"""v2.230 - The photon sphere as the common origin of ringdown and the black-hole shadow.

Extends the v2.229 eikonal correspondence into a multi-messenger consistency statement. The SAME
unstable photon sphere that sets the eikonal ringdown also sets the black-hole SHADOW: the
critical impact parameter b_c (the shadow's apparent radius, what the EHT images) satisfies

    b_c = r_ph / sqrt(f(r_ph)) = 3 sqrt3 M   (Schwarzschild),     Omega_c = 1 / b_c,

so the eikonal ringdown real frequency is omega_R -> (l + 1/2) / b_c. A gravitational-wave
ringdown (LIGO/Virgo) and an electromagnetic shadow (EHT) therefore probe the SAME geometric
quantity Omega_c = 1/b_c -- a genuine cross-channel test of the photon-sphere (Kerr) hypothesis: a
non-Kerr or quantum-corrected metric shifts b_c and moves BOTH observables coherently.

Two verifications with the in-house WKB solver (most accurate at large l, v2.218):
  1. ringdown<->shadow:  omega_R * b_c / (l + 1/2)  ->  1   (the GW frequency in units of the
     shadow light-crossing rate).
  2. overtone ladder:    the imaginary parts are EQUALLY spaced in n with spacing -> -lambda =
     -Omega_c = -1/b_c (the Lyapunov peel-off rate), so the shadow scale sets the damping ladder.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_wkb_solver import schwarzschild_qnm

VERSION = "v2.230"
DEFAULT_OUT = Path("experiments/results/v2.230/qnm_shadow_multimessenger.json")
L_VALUES = [2, 4, 6, 8, 12]


def photon_sphere_shadow() -> dict:
    """First-principles Schwarzschild (M=1) photon sphere, shadow radius, and Lyapunov rate."""
    r = 3.0
    f = 1.0 - 2.0 / r
    fpp = -4.0 / r**3
    omega_c = math.sqrt(f) / r
    b_c = r / math.sqrt(f)                                  # critical impact parameter = shadow radius
    lam = math.sqrt(f * (2 * f - r**2 * fpp) / (2 * r**2))
    return {"r_ph": r, "b_c_shadow_radius": b_c, "Omega_c": omega_c, "lambda": lam,
            "b_c_closed_form_3sqrt3": 3 * math.sqrt(3), "Omega_c_times_b_c": omega_c * b_c}


def ringdown_shadow_consistency(ps: dict) -> list[dict]:
    rows = []
    for l in L_VALUES:
        w = schwarzschild_qnm(n=0, L=l, s=2)
        rows.append({"l": l, "omega_R": w.real,
                     "omega_R_b_c_over_l_half": w.real * ps["b_c_shadow_radius"] / (l + 0.5)})
    return rows


def overtone_ladder(ps: dict, L: int = 10) -> dict:
    wi = [schwarzschild_qnm(n=n, L=L, s=2).imag for n in (0, 1, 2)]
    spacings = [wi[1] - wi[0], wi[2] - wi[1]]
    return {"L": L, "omega_I": wi, "spacings": spacings,
            "target_minus_lambda": -ps["lambda"],
            "max_rel_err": max(abs(s - (-ps["lambda"])) / ps["lambda"] for s in spacings)}


def run() -> dict:
    ps = photon_sphere_shadow()
    rd = ringdown_shadow_consistency(ps)
    ladder = overtone_ladder(ps)
    ratios = [r["omega_R_b_c_over_l_half"] for r in rd]
    converging = all(abs(ratios[i + 1] - 1) < abs(ratios[i] - 1) for i in range(len(ratios) - 1))
    return {
        "version": VERSION,
        "method": ("first-principles photon-sphere / shadow quantities vs the in-house WKB QNM "
                   "solver; ringdown<->shadow consistency and the overtone damping ladder; "
                   "Schwarzschild M=1"),
        "photon_sphere_shadow": ps,
        "first_principles_consistency": {
            "b_c_equals_3sqrt3": abs(ps["b_c_shadow_radius"] - ps["b_c_closed_form_3sqrt3"]) < 1e-12,
            "Omega_c_times_b_c_equals_1": abs(ps["Omega_c_times_b_c"] - 1.0) < 1e-12,
        },
        "ringdown_shadow_consistency": rd,
        "consistency_converges_to_1": bool(converging),
        "best_ringdown_shadow_ratio": max(ratios),
        "overtone_ladder": ladder,
        "finding": (
            f"The photon sphere is the common origin of ringdown and the shadow. The shadow radius "
            f"b_c = 3 sqrt3 = {ps['b_c_shadow_radius']:.4f} M and the orbital frequency satisfy "
            f"Omega_c * b_c = 1 exactly (first principles). The WKB ringdown then obeys the "
            f"multi-messenger consistency omega_R * b_c / (l+1/2) -> 1 (reaching "
            f"{max(ratios):.3f} at l=12), and the overtone imaginary parts form an equally-spaced "
            f"ladder with spacing -> -lambda = -1/b_c (to {100*ladder['max_rel_err']:.1f}% at "
            "l=10). So a LIGO/Virgo ringdown and an EHT shadow probe the SAME geometric quantity "
            "(1/b_c): a non-Kerr or quantum-corrected metric that shifts the photon sphere moves "
            "BOTH observables coherently -- a genuine gravitational-wave / electromagnetic "
            "cross-channel test of the Kerr hypothesis."
        ),
        "honest_scope": (
            "Eikonal (large-l) and Schwarzschild-only: the consistency ratio approaches 1 with "
            "O(1/l) corrections (22% at l=2 -> 0.8% at l=12), and the overtone ladder uses 3rd-"
            "order WKB (good for these low n at l=10). The cross-channel TEST is the physical "
            "claim; turning it into a quantitative joint bound needs a specific non-Kerr metric and "
            "real EHT + ringdown data (not done here). Kerr would split Omega_c != lambda and make "
            "the shadow non-circular. This is a geodesic/geometric-optics result; it frames a QG "
            "test (photon-sphere deviations from exotic/quantum-corrected compact objects) but does "
            "not itself constrain a coupling. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Cardoso, Miranda, Berti, Witek, Zanchin, PRD 79 (2009) 064016 -- eikonal QNM / photon sphere",
            "Event Horizon Telescope Collab., ApJL 875 (2019) L1; 930 (2022) L12 -- BH shadow",
            "this repo: v2.229 (eikonal correspondence), v2.210 (WKB solver)",
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
    ps = res["photon_sphere_shadow"]
    print(f"b_c = {ps['b_c_shadow_radius']:.5f} (3 sqrt3)  Omega_c*b_c = {ps['Omega_c_times_b_c']:.5f}")
    for r in res["ringdown_shadow_consistency"]:
        print(f"  l={r['l']:2d}  omega_R*b_c/(l+1/2) = {r['omega_R_b_c_over_l_half']:.5f}")
    lad = res["overtone_ladder"]
    print(f"overtone ladder spacings {[round(s,5) for s in lad['spacings']]} -> "
          f"-lambda={lad['target_minus_lambda']:.5f} (err {100*lad['max_rel_err']:.1f}%)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
