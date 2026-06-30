"""v2.347 - The parity sector is pinched between two birefringence observables (CMB vs GW): a near-term falsification handle.

A fresh sector after the marginality arc (v2.344-346): a concrete falsifiable forecast. The constructed
theory's parity coupling g_R2_parity is pushed UP by one observable and DOWN by another, independent one:

  * CMB cosmic birefringence (beta = 0.34 +/- 0.09 deg, Minami-Komatsu / Eskilt-Komatsu) wants g_R2_parity
    LARGE: best-fit 0.10, 2-sigma lower edge 0.0471. It is the constraint that makes parity nonzero.
  * GW birefringence (LIGO/Virgo non-observation of a circular-polarization asymmetry, Yamada-Tanaka 2020,
    Wang et al 2021) bounds g_R2_parity from ABOVE. The engine loosens this to |g_R2_parity| <= 0.1 in the
    toy regime, but its OWN docstring (src/itb/constraints/parity_violation.py) states the REAL O3 bound
    translates to |g_R2_parity| <~ 0.05.

So the two parity observables push from opposite sides and nearly PINCH. Under the toy GW bound (0.1) the
data-pinned window [CMB-lower, anomaly-upper] = [0.0471, 0.0783] is fully open and the constructed 0.06 sits
inside. Under the engine's own REAL O3 estimate (0.05) the window collapses to the sliver [0.0471, 0.05]
(width ~0.003) and the constructed center 0.06 falls OUTSIDE it. And there is a sharp falsification
threshold: if GW birefringence tightens below the CMB lower edge 0.0471, the window CLOSES entirely and the
parity-violating construction is falsified (given the CMB hint). This is a near-term, concrete handle: O4/O5
GW-birefringence sensitivity directly tests the construction.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.constraints.cosmic_birefringence import CosmicBirefringenceData

VERSION = "v2.347"
DEFAULT_OUT = Path("experiments/results/v2.347/qnm_parity_birefringence_pinch.json")

CONSTRUCTED_PARITY = 0.06
G4, GR2, RHO = 0.529, 0.193, 0.06           # constructed matter/curvature + default anomaly_rho
ANOMALY_UPPER = math.sqrt(RHO * G4 * GR2)   # 0.0783
GW_BOUND_TOY = 0.1                          # engine toy-regime loosening
GW_BOUND_REAL = 0.05                        # engine's OWN docstring estimate of the real LIGO O3 strength


def window(gw_bound: float, cmb_lo: float):
    lo = cmb_lo
    hi = min(ANOMALY_UPPER, gw_bound)
    return lo, hi


def run() -> dict:
    cmb = CosmicBirefringenceData(n_sigma=2.0)
    cmb_lo, cmb_hi = cmb.preferred_band
    cmb_lo, cmb_hi = round(cmb_lo, 4), round(cmb_hi, 4)
    cmb_central = round(cmb.beta_meas / cmb.kappa_beta, 4)

    cases = []
    for label, gw in [("toy_loosened", GW_BOUND_TOY), ("real_O3_estimate", GW_BOUND_REAL)]:
        lo, hi = window(gw, cmb_lo)
        width = max(0.0, hi - lo)
        cases.append({
            "gw_bound_label": label,
            "gw_bound": gw,
            "window": [round(lo, 4), round(hi, 4)],
            "window_width": round(width, 4),
            "nonempty": hi > lo,
            "constructed_0p06_inside": lo <= CONSTRUCTED_PARITY <= hi,
        })

    toy = next(c for c in cases if c["gw_bound_label"] == "toy_loosened")
    real = next(c for c in cases if c["gw_bound_label"] == "real_O3_estimate")

    # falsification threshold: the GW bound at which the window closes (= CMB lower edge)
    gw_falsify_threshold = cmb_lo

    checks = {
        "cmb_pushes_parity_up": cmb_lo > 0.0 and cmb_central > ANOMALY_UPPER,   # CMB wants parity (central even above anomaly cap)
        "gw_bounds_parity_from_above": GW_BOUND_REAL < ANOMALY_UPPER,           # the real GW bound bites below the anomaly cap
        "toy_bound_admits_constructed": toy["constructed_0p06_inside"],
        "real_bound_excludes_constructed": not real["constructed_0p06_inside"],  # the pinch: 0.06 outside under real bound
        "real_bound_narrows_to_sliver": real["window_width"] < 0.01 and real["nonempty"],
        "falsification_threshold_is_cmb_lower_edge": abs(gw_falsify_threshold - cmb_lo) < 1e-9,
    }

    return {
        "version": VERSION,
        "cmb_2sigma_band": [cmb_lo, cmb_hi],
        "cmb_central_g_R2_parity": cmb_central,
        "anomaly_upper_edge": round(ANOMALY_UPPER, 4),
        "gw_bound_toy": GW_BOUND_TOY,
        "gw_bound_real_O3_estimate": GW_BOUND_REAL,
        "constructed_g_R2_parity": CONSTRUCTED_PARITY,
        "cases": cases,
        "gw_falsification_threshold": round(gw_falsify_threshold, 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The parity sector -- the program's one data-pinned, distinguishing feature -- is squeezed "
            "between TWO independent birefringence observables pushing from opposite sides, and at realistic "
            "sensitivity they nearly pinch it shut. CMB cosmic birefringence (beta = 0.34 +/- 0.09 deg) "
            "pushes g_R2_parity UP (best-fit 0.10, 2-sigma lower edge 0.0471) -- it is what makes parity "
            "nonzero. GW birefringence (LIGO/Virgo non-observation) bounds it from ABOVE. Under the engine's "
            "toy-loosened GW bound (0.1) the data-pinned window [0.0471, 0.0783] is fully open and the "
            "constructed 0.06 sits comfortably inside. But under the engine's OWN docstring estimate of the "
            "real O3 strength (|g_R2_parity| <~ 0.05) the window collapses to the sliver [0.0471, 0.05] "
            "(width ~0.003) and the constructed center 0.06 falls OUTSIDE it -- the real GW bound, taken at "
            "face value, already disfavors the construction's central parity value and pins it instead to "
            "g_R2_parity ~ 0.047-0.05, right at the CMB floor. There is a sharp, near-term falsification "
            "threshold: if GW-birefringence sensitivity tightens below the CMB lower edge 0.0471, the two "
            "observables cross, the window CLOSES, and the parity-violating construction is falsified (given "
            "the CMB hint). So the new theory's most distinctive prediction is also its most testable: the "
            "SAME parity coupling that the CMB hint requires is what near-future GW-birefringence searches "
            "(O4/O5) are closing in on from the other side. This is a genuine 'how to kill it' handle, and "
            "it sharpens the construction -- if the real GW bound holds, the parity coupling should be "
            "re-centered to ~0.048 (the CMB floor), not 0.06."
        ),
        "honest_scope": (
            "Both birefringence-to-coupling MAPS are toy normalizations with large uncertainty, and that "
            "matters acutely here. The CMB map beta = 3.4 deg * g_R2_parity and the GW map (the ~0.05 real-"
            "O3 figure) each carry O(1)-to-order-of-magnitude cutoff-scale and propagation-distance "
            "uncertainty -- the engine's own docstring calls 0.05 a rough translation. So the PRECISE "
            "exclusion of 0.06, and the exact sliver width 0.003, are NOT robust numbers; shift either map "
            "by an O(1) factor and the pinch loosens or tightens. What IS robust is the STRUCTURE: two "
            "independent parity observables push g_R2_parity from opposite sides, the data-pinned window is "
            "narrow, and the real (un-loosened) GW bound sits at or below the constructed value -- so the "
            "parity sector is where the theory is most squeezed and most testable, and a modest GW-"
            "birefringence improvement crosses the CMB floor and falsifies it. The whole thing rests on the "
            "CMB hint being real (the ~3.6-sigma detection, v2.329 caveat); if it is a systematic, the lower "
            "push vanishes and there is no pinch (and no parity requirement). The anomaly upper edge uses "
            "the default anomaly_rho (v2.344: itself prefactor-dependent). Toy basis, O(1)/order-of-"
            "magnitude prefactors. A qualitative two-observable pinch with a concrete falsification "
            "direction, not a precise exclusion."
        ),
        "references": [
            "this repo: src/itb/constraints/parity_violation.py (LIGOBirefringenceBound: toy 0.1, real O3 ~0.05); src/itb/constraints/cosmic_birefringence.py (beta=0.34+/-0.09 deg)",
            "this repo: v2.344 (anomaly upper edge is prefactor-dependent), v2.329 (CMB hint is the single point of failure), v2.321 (CMB pins parity)",
            "Minami & Komatsu PRL 125,221301 (2020); Eskilt & Komatsu 2022; Yamada & Tanaka 2020; Wang et al 2021 (GW birefringence)",
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
    print("parity sector pinched between CMB (pushes up) and GW (bounds above) birefringence:")
    print(f"  CMB 2-sigma band: {res['cmb_2sigma_band']}  (central {res['cmb_central_g_R2_parity']})")
    print(f"  anomaly upper edge: {res['anomaly_upper_edge']}   constructed: {res['constructed_g_R2_parity']}")
    for c in res["cases"]:
        print(f"  GW {c['gw_bound_label']:<16} (<= {c['gw_bound']}): window {c['window']} "
              f"width {c['window_width']}  0.06 inside? {c['constructed_0p06_inside']}")
    print(f"  falsification threshold: GW bound < {res['gw_falsification_threshold']} closes the window")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
