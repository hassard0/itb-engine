"""v2.258 - The holographic bound, the Bekenstein bound, and the cosmic entropy budget.

Continues the entropy thread (v2.257), reconnecting to the engine's bh_entropy_positivity /
generalized_second_law / holographic_entropy constraints. Two quantum-gravity entropy bounds and
their saturation by black holes:

    Bekenstein bound:   S <= 2 pi R E / (hbar c)        (any system of size R, energy E)
    Holographic bound:  S <= A / (4 l_p^2)              (any region; entropy <= boundary AREA)

A Schwarzschild black hole SATURATES BOTH: S_BH = 4 pi (M/M_Pl)^2 = 2 pi (2M)(M) [Bekenstein, R=2M,
E=M] = (4 pi (2M)^2)/4 [holographic, A=16 pi M^2]. So the black hole is the MAXIMUM-entropy object
for its size -- the statement that ties the area-law (v2.257) to a universal bound, and the seed of
the holographic principle: the degrees of freedom in any region live on its boundary.

Applied to the observable universe (the de Sitter / Hubble horizon), the holographic bound is the
famous ~1e122 -- and the actual cosmic entropy (~1e104, dominated by supermassive black holes) sits
~18 orders of magnitude BELOW it, so the universe has used a tiny fraction of its entropy capacity:
the low-entropy-past / arrow-of-time puzzle. The generalized second law (S_BH + S_outside never
decreases) is what makes these bounds consistent with thermodynamics.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.258"
DEFAULT_OUT = Path("experiments/results/v2.258/qnm_holographic_bound.json")
L_P_M = 1.616e-35
R_HUBBLE_M = 1.30e26
S_SMBH_UNIVERSE = 3.1e104     # Egan & Lineweaver 2010 (nats)
S_CMB_UNIVERSE = 1.5e88


def bh_bounds(M_planck: float) -> dict:
    """Entropy, Bekenstein bound (R=2M, E=M), holographic bound (A=16 pi M^2) -- all equal."""
    s_bh = 4 * math.pi * M_planck**2
    bekenstein = 2 * math.pi * (2 * M_planck) * M_planck
    holographic = (4 * math.pi * (2 * M_planck) ** 2) / 4
    return {"S_BH": s_bh, "bekenstein_bound": bekenstein, "holographic_bound": holographic,
            "all_equal": abs(s_bh - bekenstein) < 1e-9 and abs(s_bh - holographic) < 1e-9}


def universe_holographic_bound() -> float:
    """de Sitter / Hubble-horizon holographic bound S = pi (R_H/l_p)^2 (nats)."""
    return math.pi * (R_HUBBLE_M / L_P_M) ** 2


def run() -> dict:
    sat = bh_bounds(10.0)
    s_holo = universe_holographic_bound()
    return {
        "version": VERSION,
        "method": ("Bekenstein S<=2piRE and holographic S<=A/4 bounds; BH saturation (R=2M,E=M,"
                   "A=16piM^2); observable-universe holographic bound pi(R_H/l_p)^2; cosmic entropy "
                   "budget"),
        "bh_saturation": sat,
        "bh_saturates_both": sat["all_equal"],
        "universe_holographic_bound_nats": s_holo,
        "cosmic_entropy_budget": {
            "holographic_capacity": s_holo,
            "actual_smbh_dominated": S_SMBH_UNIVERSE,
            "cmb": S_CMB_UNIVERSE,
            "fraction_of_capacity_used": S_SMBH_UNIVERSE / s_holo,
        },
        "finding": (
            "The Bekenstein bound (S <= 2 pi R E) and the holographic bound (S <= A/4) are both "
            "SATURATED by a Schwarzschild black hole -- S_BH = 4 pi M^2 = 2 pi (2M)(M) = (16 pi "
            "M^2)/4 -- so the black hole is the MAXIMUM-entropy object for its size, and the "
            "entropy of any region is capped by its boundary AREA, not its volume: the holographic "
            "principle. For the observable universe the holographic capacity (the de Sitter / Hubble "
            f"horizon, pi(R_H/l_p)^2) is ~{s_holo:.1e} nats -- the famous ~1e122 -- while the actual "
            f"cosmic entropy (~{S_SMBH_UNIVERSE:.0e}, dominated by supermassive black holes, with the "
            f"CMB a further ~1e16 below at ~{S_CMB_UNIVERSE:.0e}) is ~"
            f"{S_SMBH_UNIVERSE/s_holo:.0e} of that capacity. So the universe has used a TINY fraction "
            "of its entropy budget -- the quantitative form of the low-entropy-past / arrow-of-time "
            "puzzle (why did the universe begin so far from maximum entropy?). The generalized second "
            "law (S_BH + S_outside never decreases) is what keeps these QG bounds consistent with "
            "thermodynamics, and these are exactly the entropy constraints the engine encodes."
        ),
        "honest_scope": (
            "The Bekenstein and holographic bounds are well-established (the holographic / covariant "
            "Bousso bound is the rigorous form; the naive S <= A/4 has known subtleties for "
            "non-quasi-static / strongly-gravitating regions, which the covariant bound fixes). The "
            "BH saturation is exact. The cosmic-entropy numbers are the standard Egan-Lineweaver "
            "(2010) estimates (SMBH ~3e104, CMB ~1.5e88) -- order-of-magnitude, dominated by the "
            "most uncertain SMBH census; a future entropy (e.g. from a cosmological-horizon or "
            "putative dark-sector contribution) could shift the budget. de Sitter / Hubble-horizon "
            "entropy used for the capacity. Self-contained reconstruction of standard QG entropy "
            "bounds, not a new result. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Bekenstein, PRD 23 (1981) 287 -- the entropy bound",
            "'t Hooft (1993); Susskind, J. Math. Phys. 36 (1995) 6377 -- holographic principle",
            "Bousso, Rev. Mod. Phys. 74 (2002) 825 -- the covariant entropy bound",
            "Egan & Lineweaver, ApJ 710 (2010) 1825 -- the cosmic entropy budget; this repo: v2.257",
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
    s = res["bh_saturation"]
    print(f"BH saturation: S_BH={s['S_BH']:.2f}  Bekenstein={s['bekenstein_bound']:.2f}  "
          f"holographic={s['holographic_bound']:.2f}  (all equal={s['all_equal']})")
    b = res["cosmic_entropy_budget"]
    print(f"\ncosmic entropy budget:")
    print(f"  holographic capacity   {b['holographic_capacity']:.2e} nats (~1e122)")
    print(f"  actual (SMBH)          {b['actual_smbh_dominated']:.2e}")
    print(f"  CMB                    {b['cmb']:.2e}")
    print(f"  fraction used          {b['fraction_of_capacity_used']:.1e}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
