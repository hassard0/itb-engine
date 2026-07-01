"""v2.388 - SWING: the SDC hierarchy bound and the string-like tower jointly fix the number of simultaneously-light couplings per sector.

A fresh swing connecting two prior swampland results that look in TENSION. v2.383: the Swampland Distance
Conjecture is encoded as a hierarchy bound, max|g|/min|g_nonzero| <= R_max = 20. v2.375/376: each sector's
couplings form an infinite, geometrically-decaying string-like tower with ratio r < 1 -- so the tower's deep
couplings g ~ r^n go to zero, and max/min -> infinity, which would VIOLATE the hierarchy bound if all levels
were simultaneous low-energy couplings.

The resolution is that they are NOT simultaneous: the deeper tower levels are HEAVIER states (the SDC's own
exponentially-light tower at large field distance -- the SDC predicts exactly the tower it appears to forbid).
So the hierarchy bound applies to the couplings within one 'window', and the number of simultaneously-light
levels a sector can carry is fixed by BOTH facts together:

    n_max = log(R_max) / log(1/r)     (levels before g drops below g_top / R_max).

With R_max = 20: the CURVATURE tower (r = g_R3/g_R2 = 0.466) gives n_max = 3.93 -- about four -- and the MATTER
tower (r = g_6/g_4 = 0.756) gives n_max = 10.7. The engine's basis (3 curvature couplings g_R2, g_R3, g_R4; 3
matter couplings g_4, g_6, g_8) fits comfortably inside both windows, and notably the CURVATURE basis nearly
SATURATES its ~4-slot window (3 of ~4) while matter uses only 3 of ~11 -- consistent with the curvature tower
being the harder / faster-decaying one (v2.376). So the SDC and the tower are two faces of one physics, and
together they predict how deep each sector's low-energy EFT can run.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.388"
DEFAULT_OUT = Path("experiments/results/v2.388/qnm_sdc_tower_light_couplings.json")

R_MAX = 20.0                       # SDC hierarchy bound (v2.383)
R_CURV = 0.09 / 0.193              # curvature tower ratio g_R3/g_R2 (v2.375)
R_MATTER = 0.4 / 0.529             # matter tower ratio g_6/g_4 (v2.376)
N_CURV_BASIS = 3                   # g_R2, g_R3, g_R4
N_MATTER_BASIS = 3                 # g_4, g_6, g_8


def run() -> dict:
    n_curv = math.log(R_MAX) / math.log(1.0 / R_CURV)
    n_matter = math.log(R_MAX) / math.log(1.0 / R_MATTER)

    checks = {
        "curvature_window_about_four": 3.0 < n_curv < 5.0,
        "matter_window_larger_than_curvature": n_matter > n_curv,
        "engine_curvature_basis_within_window": N_CURV_BASIS <= n_curv + 1e-9,
        "engine_matter_basis_within_window": N_MATTER_BASIS <= n_matter,
        "curvature_nearly_saturates_its_window": (N_CURV_BASIS / n_curv) > 0.7,
    }

    return {
        "version": VERSION,
        "R_max_sdc": R_MAX,
        "curvature_tower_ratio": round(R_CURV, 3),
        "matter_tower_ratio": round(R_MATTER, 3),
        "curvature_window_levels": round(n_curv, 2),
        "matter_window_levels": round(n_matter, 2),
        "curvature_basis_used": N_CURV_BASIS,
        "matter_basis_used": N_MATTER_BASIS,
        "curvature_window_saturation": round(N_CURV_BASIS / n_curv, 2),
        "matter_window_saturation": round(N_MATTER_BASIS / n_matter, 2),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The Swampland Distance Conjecture (v2.383) and the string-like tower (v2.375/376) are two faces "
            "of one physics, not in tension, and together they fix the number of simultaneously-light "
            "couplings per sector. The apparent tension: the SDC is a hierarchy bound max|g|/min|g| <= R_max "
            "= 20, but each sector's couplings form an infinite geometrically-decaying tower g ~ r^n whose "
            "deep levels -> 0, so max/min -> infinity would seem to violate it. The resolution: the deeper "
            "tower levels are HEAVIER states -- the SDC's own exponentially-light tower at large field "
            "distance -- so the SDC predicts exactly the tower it appears to forbid, and the hierarchy bound "
            "applies only to the couplings within one 'window'. The number of simultaneously-light levels a "
            "sector carries is then set by BOTH facts: n_max = log(R_max)/log(1/r). With R_max = 20 the "
            "curvature tower (r = 0.466) gives n_max = 3.93 (about four) and the matter tower (r = 0.756) "
            "gives 10.7. The engine's basis -- 3 curvature couplings (g_R2, g_R3, g_R4) and 3 matter (g_4, "
            "g_6, g_8) -- fits comfortably inside both windows, and the CURVATURE basis nearly SATURATES its "
            "~4-slot window (3 of ~4, saturation 0.76) while matter uses only 3 of ~11 (saturation 0.28). "
            "That is exactly what v2.376 predicts: the curvature tower is the harder, faster-decaying one, so "
            "it runs out of hierarchy room sooner -- the low-energy curvature EFT is nearly as deep as the "
            "SDC allows, while the matter EFT has room for many more operators before the hierarchy bound "
            "bites. So the two swampland facts jointly explain WHY the gravitational EFT truncates to a few "
            "curvature operators (the SDC window is only ~4 deep for the curvature tower's decay rate) -- the "
            "engine's finite curvature basis is not an arbitrary truncation but the depth the SDC + tower "
            "permit. It also predicts the matter sector could support a much deeper tower of light operators "
            "(~11) than the engine currently carries -- room the dark matter sector (v2.381) hides."
        ),
        "honest_scope": (
            "n_max = log(R_max)/log(1/r) is a HEURISTIC bridge between the two swampland facts, not a derived "
            "theorem: it counts geometric-floor tower levels (v2.375, single-scale saturated log-convexity) "
            "before the coupling drops below g_top/R_max, so a faster-decaying (multi-state) actual tower "
            "would give FEWER levels -- n_max is an upper estimate. R_max = 20 is the engine's TOY SDC proxy "
            "value (v2.383 scope); n_max scales as log(R_max), so a different SDC encoding shifts the window "
            "sizes (though weakly, logarithmically). The tower ratios r_curv = 0.466 and r_matter = 0.756 are "
            "the constructed toy-basis values, but the ORDERING (curvature window < matter window, curvature "
            "nearer saturation) is robust -- it follows from the basis-robust v2.376 fact that the curvature "
            "tower decays faster. The 'engine basis fits the window' is a CONSISTENCY check (the finite basis "
            "does not exceed the SDC+tower depth), not a prediction the engine independently tests, and the "
            "matching of the curvature basis (3) to its window (~4) is suggestive, not exact. This is a "
            "structural connection between two prior toy-encoded results, so it inherits both their scopes and "
            "adds no new datum. Robust content: the SDC and the tower are mutually consistent (deeper levels "
            "= heavier states), and the curvature sector's faster decay makes its hierarchy window shallower "
            "than matter's, so the curvature EFT truncates sooner -- a joint-consistency explanation for the "
            "few-curvature-operator basis. Toy R_max and ratios, robust ordering, heuristic count. A "
            "swampland-consistency swing."
        ),
        "references": [
            "this repo: v2.383 (SDC as hierarchy bound R_max=20), v2.375 (infinite log-convex curvature tower), v2.376 (matter vs curvature tower ratios), v2.381 (dark matter sector)",
            "physics: Ooguri-Vafa 2007 (SDC -> light tower at infinite distance); the SDC's tower IS the moment tower",
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
    print("SWING: SDC hierarchy bound + string-like tower jointly fix the number of light couplings per sector:")
    print(f"  R_max = {res['R_max_sdc']} (SDC, v2.383)")
    print(f"  curvature tower r = {res['curvature_tower_ratio']} -> window {res['curvature_window_levels']} levels (basis uses {res['curvature_basis_used']}, saturation {res['curvature_window_saturation']})")
    print(f"  matter    tower r = {res['matter_tower_ratio']} -> window {res['matter_window_levels']} levels (basis uses {res['matter_basis_used']}, saturation {res['matter_window_saturation']})")
    print(f"  => curvature EFT nearly saturates its ~4-slot SDC window (harder tower, v2.376); matter has room for ~11")
    print(f"  => the two swampland facts are consistent (deep tower levels = heavier states) and jointly explain the few-curvature-operator basis")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
