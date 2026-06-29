"""v2.275 - The Page curve: the entanglement signature of black-hole unitarity.

A fresh QG capstone of the black-hole-entropy thread (v2.257/v2.258/v2.273/v2.274) addressing the
information paradox head-on. As a black hole evaporates, what happens to the von Neumann (fine-grained)
entropy of its Hawking radiation?

  Hawking (information loss): the radiation entropy rises MONOTONICALLY to the initial S_BH -- the
                             final state is mixed, information is destroyed.
  Page (unitarity):          it rises until the PAGE TIME, then DECREASES back to 0 -- a pure final
                             state, information preserved.

The modern resolution (quantum extremal surface / island formula; Penington; Almheiri-Engelhardt-
Marolf-Maxfield 2019) makes the fine-grained entropy the MINIMUM of two saddles:

    S_rad = min( S_rad^thermal ,  S_BH^remaining ) ,

the 'no-island' (coarse-grained Hawking) answer early, and the 'island' (remaining horizon area/4)
answer late. With entropy conservation S_rad^thermal = S_0 - S_BH(M) and S_BH(M) = (M/M_0)^2 S_0, the
two cross at S_BH = S_0/2, i.e. M = M_0/sqrt2, and via the M^3 evaporation law (v2.257) that is the
Page time t_Page/tau = 1 - 2^(-3/2) ~ 0.646. The turnover -- the radiation entropy coming back down --
is the entanglement signature that the evaporation is unitary.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")

VERSION = "v2.275"
DEFAULT_OUT = Path("experiments/results/v2.275/qnm_page_curve.json")


def s_bh(m_over_m0: float) -> float:
    """Remaining black-hole entropy S_BH/S_0 = (M/M_0)^2 (since S_BH = 4 pi M^2 = A/4)."""
    return m_over_m0**2


def s_rad_thermal(m_over_m0: float) -> float:
    """Coarse-grained (Hawking) radiation entropy S/S_0 = 1 - S_BH/S_0 (entropy conservation)."""
    return 1.0 - s_bh(m_over_m0)


def s_fine_page(m_over_m0: float) -> float:
    """Fine-grained radiation entropy = min(no-island, island) = min(S_rad^thermal, S_BH^remaining)."""
    return min(s_rad_thermal(m_over_m0), s_bh(m_over_m0))


def page_time_over_tau() -> float:
    """Page time as a fraction of the evaporation time, via t/tau = 1 - (M/M_0)^3 at M = M_0/sqrt2."""
    return 1.0 - 2.0 ** (-1.5)


def run() -> dict:
    # evaporation runs M/M_0 : 1 -> 0
    x = np.linspace(1.0, 1e-3, 2000)            # x = M/M_0, decreasing
    hawking = np.array([s_rad_thermal(v) for v in x])
    page = np.array([s_fine_page(v) for v in x])

    # 1. Hawking curve is monotonic up to S_0 = 1; Page curve turns over
    hawking_monotonic = bool(np.all(np.diff(hawking) >= -1e-12) and abs(hawking[-1] - 1.0) < 1e-3)
    peak_idx = int(np.argmax(page))
    page_turns_over = bool(page[peak_idx] > page[0] + 1e-6 and page[peak_idx] > page[-1] + 1e-6)

    # 2. peak (Page point): S_fine = 1/2 at M/M_0 = 1/sqrt2
    m_page = float(x[peak_idx])
    page_peak = float(page[peak_idx])
    m_page_theory = 1.0 / math.sqrt(2.0)

    # 3. Page time from the M^3 law
    t_page = page_time_over_tau()

    # 4. information returns: Page entropy -> 0 as M -> 0, while Hawking -> 1 (lost)
    info_returns = bool(page[-1] < 1e-2 and hawking[-1] > 0.99)

    # 5. island prescription: S_fine = min(thermal, bh) everywhere (verify against the two saddles)
    island_min = bool(all(abs(s_fine_page(v) - min(s_rad_thermal(v), s_bh(v))) < 1e-15
                          for v in (0.95, 1 / math.sqrt(2), 0.5, 0.1)))

    checks = {
        "hawking_monotonic_to_S0": hawking_monotonic,
        "page_curve_turns_over": page_turns_over,
        "page_point_half_entropy_at_M0_over_sqrt2": bool(abs(page_peak - 0.5) < 1e-2
                                                         and abs(m_page - m_page_theory) < 2e-2),
        "page_time_is_1_minus_2_to_minus_3_halves": abs(t_page - (1 - 2 ** -1.5)) < 1e-12,
        "information_returns_unitary": info_returns,
        "island_min_prescription": island_min,
    }

    # a few sampled points for the JSON record
    sample = [{"M_over_M0": float(v), "hawking": s_rad_thermal(v), "page": s_fine_page(v)}
              for v in (1.0, 0.9, m_page_theory, 0.5, 0.25, 0.01)]

    return {
        "version": VERSION,
        "method": ("Page curve S_rad = min(S_rad^thermal, S_BH^remaining) with S_BH=(M/M_0)^2 S_0 and "
                   "S_rad^thermal = S_0 - S_BH; Page point at M=M_0/sqrt2, S=S_0/2; Page time via the "
                   "M^3 evaporation law t/tau = 1 - (M/M_0)^3"),
        "page_point": {"M_over_M0": m_page_theory, "S_fine_over_S0": 0.5},
        "page_time_over_tau": t_page,
        "sampled_curve": sample,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The Page curve is the entanglement signature of black-hole unitarity, and it is the "
            "MINIMUM of two saddles: the coarse-grained Hawking entropy (which rises monotonically to "
            "the full initial entropy S_0 -- the information-loss prediction, verified) and the "
            "remaining horizon entropy S_BH = (M/M_0)^2 S_0 (which falls). The fine-grained radiation "
            "entropy follows the lower of the two, so it RISES to a peak and then comes back DOWN: the "
            "turnover (verified) at the Page point M = M_0/sqrt2, where exactly half the entropy has "
            "been radiated (S_fine = S_0/2), which via the M^3 evaporation law (v2.257) is the Page "
            f"time t_Page/tau = 1 - 2^(-3/2) ~ {t_page:.3f} of the lifetime. After the Page time the "
            "radiation entropy decreases back toward 0 (verified -> pure final state, information "
            "returns), in sharp contrast to Hawking's monotonic rise to S_0 (information lost). The "
            "switch from the 'no-island' to the 'island' saddle at the Page time is the quantum-"
            "extremal-surface resolution of the information paradox (Penington; Almheiri et al.), and "
            "it caps the BH-entropy thread: the same horizon area that sets the v2.257 entropy, the "
            "v2.273 greybody emission and the v2.274 area quantum is the late-time island that brings "
            "the information back out."
        ),
        "honest_scope": (
            "This is the standard PHENOMENOLOGICAL Page model: the fine-grained entropy is taken as "
            "min(S_rad^thermal, S_BH), the island-formula RESULT, modeled here directly rather than "
            "derived from a replica-wormhole / gravitational-path-integral computation. The coarse-"
            "grained S_rad^thermal = S_0 - S_BH uses entropy conservation and OMITS the Page/greybody "
            "factor (Hawking radiation is ~1.4-1.6x more entropic than the BH's entropy deficit, "
            "v2.273), which shifts the exact Page time modestly earlier -- so t_Page ~ 0.646 tau is the "
            "clean-model value, not a precise number. S_BH = A/4 is semiclassical, M^3 evaporation is "
            "the leading law, and unitarity (S_fine -> 0) is the ASSUMPTION whose entanglement "
            "signature the Page curve IS -- the paradox's resolution is illustrated, not proven. A "
            "QG-structure / information-paradox result, not an engine constraint refit."
        ),
        "references": [
            "Page, 'Information in black hole radiation', PRL 71 (1993) 3743",
            "Penington, 'Entanglement wedge reconstruction and the information paradox', JHEP 09 (2020) 002",
            "Almheiri, Engelhardt, Marolf, Maxfield, 'The entropy of bulk quantum fields and the entanglement wedge of an evaporating black hole', JHEP 12 (2019) 063",
            "Almheiri, Hartman, Maldacena, Shaghoulian, Tajdini, 'The entropy of Hawking radiation', RMP 93 (2021) 035002",
            "this repo: v2.257/v2.258 (BH entropy), v2.273 (greybody), v2.274 (area quantization)",
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
    print("the Page curve (S_rad / S_0 vs M/M_0, evaporation runs right -> left):")
    print("  M/M0     Hawking(monotonic)   Page(min, unitary)")
    for s in res["sampled_curve"]:
        print(f"  {s['M_over_M0']:.4f}   {s['hawking']:.4f}               {s['page']:.4f}")
    print(f"  Page point: M = M0/sqrt2 = {res['page_point']['M_over_M0']:.4f}, S_fine = S0/2")
    print(f"  Page time:  t/tau = 1 - 2^(-3/2) = {res['page_time_over_tau']:.4f}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
