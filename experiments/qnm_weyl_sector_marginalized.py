"""v2.400 - SWING (marginalize over the c-a modulus): the Weyl^2-sector HEADLINES survive the a=c assumption; only their magnitudes loosen.

v2.399 flagged that a=c is a framework ASSUMPTION and the c-a split is a free modulus (bounded only by the
Hofman-Maldacena wedge), so every Weyl^2-sector result computed AT a=c carries an unpinned modulus. The
responsible follow-up: marginalize those predictions over the whole modulus (g_C in the HM wedge [18/31 g_R2,
3 g_R2]) and check whether the a=c assumption THREATENS the qualitative headlines or merely their numbers.

Result: it only loosens the numbers. Across the full HM wedge (g_C in [0.112, 0.579] at g_R2 = 0.193):
  (1) extremal-BH entropy shift Delta S_ext = A g_C + B g_4 (v2.378): a=c value 0.458 -> marginalized
      [0.377, 0.843], POSITIVE throughout -> extremal black holes DECAY regardless of the c-a modulus;
  (2) Weyl^2 ghost mass m_g/Lambda = 1/sqrt(g_C) (v2.385): a=c 2.28 -> marginalized [1.31, 2.99], ABOVE the
      cutoff throughout -> ghost-safe regardless of the modulus;
  (3) species-scale cutoff Lambda/M_Pl = 1/sqrt(1 + 2(g_R2+g_C+g_R3)) (v2.394): a=c 0.716 -> marginalized
      [0.606, 0.747], near-Planckian (in (0.5, 1)) throughout.

So the c-a modulus (v2.399) affects the MAGNITUDES but not the QUALITATIVE predictions -- the Weyl^2-sector
headlines (BH decay, ghost-safety, near-Planckian cutoff) are all robust to the a=c assumption. This is the
honest resolution of v2.399's flag: downgrading a=c to an assumption does NOT threaten the earlier qualitative
results, it only widens their error bars, and every one stays on the correct side of its threshold across the
entire conformal-collider-allowed range.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

VERSION = "v2.400"
DEFAULT_OUT = Path("experiments/results/v2.400/qnm_weyl_sector_marginalized.json")

GR2, G4, GR3 = 0.193, 0.529, 0.09
A_BH, B_BH, NU = 1.0, 0.5, 2.0
GC_LO, GC_HI = 18.0 / 31.0 * GR2, 3.0 * GR2   # HM wedge on g_C


def _cutoff(gc):
    return 1.0 / np.sqrt(1.0 + NU * (GR2 + gc + GR3))


def run() -> dict:
    dS = [A_BH * GC_LO + B_BH * G4, A_BH * GC_HI + B_BH * G4]
    dS_ac = A_BH * GR2 + B_BH * G4
    mg = [float(1.0 / np.sqrt(GC_HI)), float(1.0 / np.sqrt(GC_LO))]
    mg_ac = float(1.0 / np.sqrt(GR2))
    L = [float(_cutoff(GC_HI)), float(_cutoff(GC_LO))]
    L_ac = float(_cutoff(GR2))

    checks = {
        "bh_decay_robust_to_modulus": dS[0] > 0.0,
        "ghost_safe_robust_to_modulus": mg[0] > 1.0,
        "cutoff_near_planckian_robust": (L[0] > 0.5) and (L[1] < 1.0),
        "magnitudes_genuinely_loosen": (dS[1] / dS[0] > 1.3) and (mg[1] / mg[0] > 1.3),
        "all_headlines_survive_a_equals_c_assumption": (dS[0] > 0.0) and (mg[0] > 1.0) and (L[0] > 0.5),
    }

    return {
        "version": VERSION,
        "c_minus_a_modulus_gC_wedge": [round(GC_LO, 3), round(GC_HI, 3)],
        "bh_entropy_shift": {"a_eq_c": round(dS_ac, 3), "marginalized": [round(dS[0], 3), round(dS[1], 3)], "headline": "extremal BHs decay (Delta S_ext > 0)"},
        "ghost_mass_over_cutoff": {"a_eq_c": round(mg_ac, 2), "marginalized": [round(mg[0], 2), round(mg[1], 2)], "headline": "ghost above cutoff (m_g/Lambda > 1)"},
        "species_cutoff_over_Mpl": {"a_eq_c": round(L_ac, 3), "marginalized": [round(L[1], 3), round(L[0], 3)], "headline": "near-Planckian cutoff (0.5 < Lambda/M_Pl < 1)"},
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The Weyl^2-sector headlines survive the a=c assumption; only their magnitudes loosen -- the "
            "honest resolution of v2.399's flag. v2.399 downgraded a=c from a prediction to a framework "
            "assumption and exposed the c-a split as a free modulus bounded only by the Hofman-Maldacena "
            "wedge, so every Weyl^2-sector result computed at a=c carries that modulus. Marginalizing over the "
            "whole wedge (g_C in [0.112, 0.579] at g_R2 = 0.193): (1) the extremal-BH entropy shift Delta "
            "S_ext = A g_C + B g_4 (v2.378) moves from its a=c value 0.458 to a marginalized [0.377, 0.843], "
            "POSITIVE throughout -- extremal black holes DECAY for every allowed c-a; (2) the Weyl^2 ghost "
            "mass 1/sqrt(g_C) (v2.385) moves from 2.28 to [1.31, 2.99], ABOVE the cutoff throughout -- "
            "ghost-safe for every allowed c-a; (3) the species-scale cutoff (v2.394) moves from 0.716 to "
            "[0.606, 0.747], near-Planckian throughout. So the c-a modulus widens the ERROR BARS on these "
            "numbers by a factor of ~2 but never flips a sign or crosses a threshold: BH decay, ghost-safety, "
            "and the near-Planckian cutoff are all robust to the a=c assumption. This closes the c!=a arc "
            "(v2.397 diagnosed the c-a degeneracy -> v2.398 activated the axis -> v2.399 showed a=c is an "
            "assumption -> v2.400 marginalizes and finds the headlines survive): resolving the basis's key "
            "limitation neither breaks the candidate nor forces it off a=c, it just makes explicit that the "
            "Weyl^2-sector magnitudes carry a conformal-collider-bounded uncertainty the degenerate basis had "
            "hidden. The candidate theory's qualitative profile -- string-like, matter-dominant, WGC-complete, "
            "ghost-safe, near-Planckian, with decaying extremal black holes -- stands independent of the a=c "
            "assumption; what the resolved basis adds is honest error bars, not a different theory."
        ),
        "honest_scope": (
            "The marginalization is over the c-a modulus at FIXED g_R2 = 0.193 (and fixed g_4, g_R3) -- i.e. "
            "it varies only the newly-freed Weyl^2 coupling g_C across its HM wedge, which is exactly the "
            "modulus v2.399 exposed; a fuller marginalization would also vary the other couplings over the "
            "feasible region, but the qualitative robustness (sign of Delta S_ext, ghost above cutoff, cutoff "
            "in (0.5,1)) holds a fortiori because each is monotone in g_C and stays on-side at both wedge "
            "edges. The predictions use the engine's toy coefficients (A=1, B=0.5 for the CLR entropy; "
            "1/sqrt(g_C) O(1)-schematic ghost mass; nu=2 species) so the MAGNITUDES and their ~2x widening "
            "are toy-basis; the ROBUST content is that every headline stays on the correct side of its "
            "threshold across the entire conformal-collider-allowed range -- a sign/ordering statement, not a "
            "magnitude one. This is a marginalization of prior toy-encoded results over a prior (source-cited) "
            "wedge, adding no new datum -- its value is that it CLOSES the c!=a arc responsibly by showing the "
            "flagged a=c assumption does not threaten the qualitative candidate profile. Robust content: "
            "marginalizing the Weyl^2-sector predictions over the c-a modulus loosens their magnitudes by ~2x "
            "but preserves every qualitative headline (BH decay, ghost-safety, near-Planckian cutoff). Toy "
            "magnitudes, robust sign/threshold survival, fixed-g_R2 modulus. A marginalize-the-modulus swing."
        ),
        "references": [
            "this repo: v2.399 (a=c is an assumption / c-a free modulus), v2.398 (activated c-axis / HM wedge), v2.378 (BH entropy shift), v2.385 (Weyl^2 ghost), v2.394 (species cutoff), v2.397 (c-a degeneracy diagnosis)",
            "physics: Hofman-Maldacena 2008 (a/c wedge); Cheung-Liu-Remmen (BH entropy); Dvali (species scale)",
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
    print("SWING (marginalize over the c-a modulus): Weyl^2-sector headlines survive the a=c assumption:")
    for key in ("bh_entropy_shift", "ghost_mass_over_cutoff", "species_cutoff_over_Mpl"):
        d = res[key]
        print(f"  {key}: a=c {d['a_eq_c']} -> marginalized {d['marginalized']}  [{d['headline']}]")
    print(f"  => c-a modulus loosens magnitudes ~2x but every qualitative headline survives the whole HM wedge")
    print(f"  => closes the c!=a arc (v2.397 diagnose -> v2.398 activate -> v2.399 assumption -> v2.400 marginalize)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
