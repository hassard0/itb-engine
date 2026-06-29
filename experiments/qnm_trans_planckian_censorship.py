"""v2.263 - The Trans-Planckian Censorship Conjecture: why it predicts unobservable primordial GWs.

A fresh QG-consistency / swampland probe extending the inflation-tensor (v2.253) and Swampland
Distance Conjecture (v2.255) arc. The Trans-Planckian Censorship Conjecture (TCC; Bedroya-Vafa 2019)
demands that no length scale that was ever sub-Planckian is stretched outside the Hubble horizon by
an accelerating phase -- otherwise trans-Planckian quantum modes would be promoted to classical
observables, which a consistent theory of quantum gravity forbids. For an inflationary phase lasting
N e-folds with (near-constant) Hubble rate H_f at its end, the condition is

    a_f / a_i  <  M_Pl / H_f    =>    e^N  <  M_Pl / H_f    =>    H_f  <  M_Pl e^{-N}.

Combined with the measured scalar amplitude this caps the tensor-to-scalar ratio. Using the same
slow-roll relations as v2.253 (H = M_Pl pi sqrt(A_s r / 2), reduced M_Pl = 2.435e18 GeV,
A_s = 2.1e-9), the TCC bound on H translates to

    r_max(N) = 2 H_max^2 / (pi^2 A_s M_Pl^2) = 2 e^{-2N} / (pi^2 A_s),
    V^{1/4}_max(N) = (3/2 pi^2 A_s r_max)^{1/4} M_Pl.

The headline: even for the most generous e-fold count N ~ 44 (the CMB-pivot value Bedroya-Vafa use),
r_max ~ 6e-31 and V^{1/4}_max ~ 1e9 GeV -- some 27+ orders of magnitude below any conceivable B-mode
detector (CMB-S4 / LiteBIRD reach r ~ 1e-3). So the TCC predicts primordial tensors are FOREVER
unobservable, and a single r > ~1e-3 B-mode detection would FALSIFY the conjecture. This is a sharp,
falsifiable QG-consistency statement, exponentially stronger than the v2.255 SDC's mild small-r
preference.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_inflation_tensor_qg import (
    A_S,
    M_PL_GEV,
    H_inflation_gev,
    V_quarter_gev,
)

VERSION = "v2.263"
DEFAULT_OUT = Path("experiments/results/v2.263/qnm_trans_planckian_censorship.json")

# detection floors for the tensor-to-scalar ratio r
DETECTION_FLOORS = [
    {"r": 3.6e-2, "label": "current bound (BICEP/Keck 2021)"},
    {"r": 1e-3, "label": "CMB-S4 / LiteBIRD reach"},
    {"r": 1e-5, "label": "cosmic-variance / ultimate CMB"},
    {"r": 1e-6, "label": "speculative far-future floor"},
]


def tcc_r_max(n_efolds: float) -> float:
    """TCC cap on the tensor-to-scalar ratio from e^N < M_Pl/H: r_max = 2 e^{-2N}/(pi^2 A_s)."""
    return 2.0 * math.exp(-2.0 * n_efolds) / (math.pi**2 * A_S)


def tcc_H_max_gev(n_efolds: float) -> float:
    """TCC cap on the inflationary Hubble rate: H_max = M_Pl e^{-N} (reduced M_Pl)."""
    return M_PL_GEV * math.exp(-n_efolds)


def run() -> dict:
    n_grid = [44.0, 50.0, 60.0, 70.0]
    rows = []
    for n in n_grid:
        r_max = tcc_r_max(n)
        h_max = tcc_H_max_gev(n)
        v4_max = V_quarter_gev(r_max)
        # round-trip self-consistency: H from r (v2.253 relation) must equal the direct TCC H_max
        h_from_r = H_inflation_gev(r_max)
        rows.append({
            "N_efolds": n,
            "H_max_gev": h_max,
            "r_max": r_max,
            "V_quarter_max_gev": v4_max,
            "orders_below_CMB_S4": math.log10(1e-3 / r_max),
            "roundtrip_H_consistent": abs(h_from_r - h_max) / h_max < 1e-9,
        })

    # literature anchor: N ~ 44 reproduces Bedroya-Vafa V^{1/4} ~ 6e8 GeV, r ~ 1e-30 (order of mag)
    bv = rows[0]
    bv_anchor = {
        "N_efolds": 44.0,
        "V_quarter_max_gev": bv["V_quarter_max_gev"],
        "r_max": bv["r_max"],
        "reproduces_bedroya_vafa_order": (1e8 < bv["V_quarter_max_gev"] < 1e10
                                          and 1e-32 < bv["r_max"] < 1e-29),
    }

    # falsifiability: the smallest detector floor still sits enormously above the TCC ceiling
    floor_gaps = [{**f, "orders_above_tcc_N44": math.log10(f["r"] / bv["r_max"])}
                  for f in DETECTION_FLOORS]

    return {
        "version": VERSION,
        "method": ("Trans-Planckian Censorship Conjecture e^N < M_Pl/H_f translated to a tensor bound "
                   "via the v2.253 slow-roll relations: r_max(N)=2 e^{-2N}/(pi^2 A_s), "
                   "V^{1/4}_max=(3/2 pi^2 A_s r_max)^{1/4} M_Pl; reduced M_Pl=2.435e18 GeV, A_s=2.1e-9"),
        "scalar_amplitude": A_S,
        "reduced_M_Pl_gev": M_PL_GEV,
        "tcc_bounds": rows,
        "bedroya_vafa_anchor": bv_anchor,
        "detection_floor_gaps": floor_gaps,
        "finding": (
            "The TCC caps the inflationary Hubble rate at H < M_Pl e^{-N}, which (via the measured "
            "A_s) caps the tensor-to-scalar ratio at r_max(N) = 2 e^{-2N}/(pi^2 A_s). Even for the "
            "most generous e-fold count N ~ 44 (the CMB-pivot value), r_max ~ 6e-31 and "
            "V^{1/4}_max ~ 1e9 GeV -- reproducing the Bedroya-Vafa headline (V^{1/4} <~ 6e8 GeV, "
            "r <~ 1e-30) to order of magnitude. That is ~27 orders of magnitude below the CMB-S4 / "
            "LiteBIRD reach (r ~ 1e-3) and ~24 below even a speculative r ~ 1e-6 floor. So the TCC "
            "predicts primordial gravitational waves are FOREVER unobservable, and conversely a "
            "single B-mode detection at r > ~1e-3 would FALSIFY the conjecture -- a sharp, decidable "
            "QG-consistency test. This is exponentially stronger than the v2.255 Swampland Distance "
            "Conjecture, which only mildly prefers small r (sub-Planckian field excursion); the two "
            "swampland criteria agree in DIRECTION (both push r down) but the TCC is the aggressive "
            "one. The round-trip H(r) <-> H_max(N) is self-consistent to 1e-9 for every N."
        ),
        "honest_scope": (
            "The TCC is a conjecture, not a theorem; the bound assumes a single near-constant-H "
            "accelerating phase of N e-folds and uses the leading slow-roll tensor relation (exact at "
            "that order, as in v2.253). The result is exponentially sensitive to N (r_max ~ e^{-2N}): "
            "N=44 -> 6e-31, N=60 -> 7e-45 -- so the specific ceiling is order-of-magnitude, but the "
            "QUALITATIVE conclusion (r unobservably small for any plausible N >~ 40) is robust across "
            "the whole range. A_s is measured and M_Pl fixed (reduced convention). Multi-field or "
            "non-standard-thermal-history inflation can relax the e-fold bookkeeping; this is the "
            "vanilla single-field statement. A QG-consistency / falsifiability result, not an engine "
            "constraint refit."
        ),
        "references": [
            "Bedroya, Vafa, 'Trans-Planckian Censorship and the Swampland', JHEP 09 (2020) 123, arXiv:1909.11063",
            "Bedroya, Brandenberger, Loverde, Vafa, 'Trans-Planckian Censorship and Inflationary Cosmology', PRD 101 (2020) 103502",
            "this repo: v2.253 (inflation tensor spectrum), v2.255 (Swampland Distance Conjecture)",
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
    print("  N      H_max(GeV)     r_max         V^1/4_max(GeV)   orders below CMB-S4")
    for r in res["tcc_bounds"]:
        print(f"  {r['N_efolds']:.0f}   {r['H_max_gev']:.2e}    {r['r_max']:.2e}   "
              f"{r['V_quarter_max_gev']:.2e}        {r['orders_below_CMB_S4']:.1f}")
    a = res["bedroya_vafa_anchor"]
    print(f"Bedroya-Vafa anchor (N=44): V^1/4~{a['V_quarter_max_gev']:.1e} GeV, r~{a['r_max']:.1e}, "
          f"reproduces literature order = {a['reproduces_bedroya_vafa_order']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
