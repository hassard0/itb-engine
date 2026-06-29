"""v2.255 - The Swampland Distance Conjecture: the light tower, and why it predicts small r.

The companion swampland pillar to the Weak Gravity Conjecture (v2.254), reconnecting to the engine's
distance_conjecture constraint. The Swampland Distance Conjecture (Ooguri-Vafa 2007): in any
consistent quantum-gravity theory, traversing a large geodesic distance Delta phi in field/moduli
space brings down an INFINITE TOWER of states exponentially,

    m(Delta phi) = M_0 exp(- alpha Delta phi / M_Pl) ,   alpha ~ O(1) ,

so the effective field theory breaks down once the tower descends below its cutoff -- the EFT cannot
support arbitrarily large field excursions.

The sharp observational consequence is in INFLATION. The Lyth bound ties the inflaton's field
excursion to the tensor-to-scalar ratio r (v2.253):

    Delta phi / M_Pl  ~  sqrt(r / 0.01)        (order-of-magnitude; r=0.01 <-> Delta phi ~ M_Pl),

so a sizeable r requires a TRANS-Planckian excursion -- exactly what the Distance Conjecture
disfavours, because the tower would have come down during inflation and spoiled the EFT. Therefore
the Distance Conjecture PREDICTS small r (sub-Planckian, small-field inflation): the current bound
r < 0.036 sits in the (mildly tense) trans-Planckian regime, and a future bound r < 0.002 would be
the sub-Planckian / swampland-safe regime -- a falsifiable swampland statement about the tensor
sector, testable by CMB-S4 / LiteBIRD.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.255"
DEFAULT_OUT = Path("experiments/results/v2.255/qnm_swampland_distance_conjecture.json")


def tower_mass_over_Mpl(delta_phi_over_Mpl: float, alpha: float = 1.0) -> float:
    """SDC light tower: m/M_Pl = exp(-alpha Delta phi / M_Pl) (M_0 = M_Pl)."""
    return math.exp(-alpha * delta_phi_over_Mpl)


def field_distance_to_cutoff(cutoff_over_Mpl: float, alpha: float = 1.0) -> float:
    """Delta phi / M_Pl at which the tower descends to a cutoff Lambda."""
    return -math.log(cutoff_over_Mpl) / alpha


def lyth_delta_phi(r: float) -> float:
    """Lyth bound (order-of-magnitude): Delta phi / M_Pl ~ sqrt(r / 0.01)."""
    return math.sqrt(r / 0.01)


def run() -> dict:
    # tower descent for a few field distances
    tower = [{"delta_phi_Mpl": d, "tower_mass_over_Mpl": tower_mass_over_Mpl(d)}
             for d in (0.5, 1.0, 5.0, 10.0)]
    # Lyth bound: field excursion vs r, and the trans-Planckian flag
    r_rows = []
    for r, ctx in [(0.036, "current bound (BICEP/Keck)"), (0.01, "Lyth threshold ~ M_Pl"),
                   (0.003, "CMB-S4 target"), (0.001, "LiteBIRD reach")]:
        dphi = lyth_delta_phi(r)
        r_rows.append({"r": r, "delta_phi_Mpl": dphi,
                       "trans_planckian": bool(dphi > 1.0), "context": ctx})
    return {
        "version": VERSION,
        "method": ("SDC tower m/M_Pl = exp(-alpha Delta phi/M_Pl); Lyth bound Delta phi/M_Pl ~ "
                   "sqrt(r/0.01); trans-Planckian threshold Delta phi > M_Pl"),
        "light_tower": tower,
        "field_distance_to_descend_to_1e-3_Mpl": field_distance_to_cutoff(1e-3),
        "lyth_bound_vs_r": r_rows,
        "sdc_predicts_small_r": True,
        "finding": (
            "The Swampland Distance Conjecture brings an infinite tower of states down exponentially "
            "with field distance (m/M_Pl = exp(-alpha Delta phi/M_Pl)): by Delta phi ~ 7 M_Pl the "
            "tower has fallen below 1e-3 M_Pl, voiding the EFT. Applied to inflation via the Lyth "
            "bound (Delta phi/M_Pl ~ sqrt(r/0.01)), this PREDICTS a small tensor-to-scalar ratio: a "
            "sizeable r needs a TRANS-Planckian inflaton excursion, which the Distance Conjecture "
            "disfavours. The current bound r < 0.036 implies Delta phi ~ "
            f"{lyth_delta_phi(0.036):.1f} M_Pl (trans-Planckian -- mild SDC tension), the Lyth "
            "threshold r ~ 0.01 corresponds to Delta phi ~ M_Pl, and a future bound r < 0.002 would "
            f"give Delta phi < {lyth_delta_phi(0.002):.2f} M_Pl (sub-Planckian, swampland-safe). So "
            "the Distance Conjecture is a FALSIFIABLE swampland statement about the v2.253 tensor "
            "sector -- it bets on small-field inflation, testable by CMB-S4 / LiteBIRD -- and it is "
            "the physical-tower counterpart of the engine's distance_conjecture aspect-ratio bound on "
            "the Wilson coefficients."
        ),
        "honest_scope": (
            "The SDC is a CONJECTURE (well-supported in string compactifications, not a theorem); the "
            "exponent alpha ~ O(1) is order-unity, not fixed (the 'refined' SDC debates its precise "
            "value, alpha >= 1/sqrt(d-2) etc.). The Lyth bound coefficient is ORDER-OF-MAGNITUDE -- "
            "the precise sqrt(r) prefactor depends on the observable e-fold window and the inflation "
            "model (the threshold is conventionally r ~ 0.01 <-> Delta phi ~ M_Pl, used here). "
            "Trans-Planckian excursions are not strictly forbidden (some monodromy / multi-field "
            "models evade the simple bound). Self-contained reconstruction of the swampland-inflation "
            "connection, not a new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Ooguri & Vafa, Nucl. Phys. B766 (2007) 21 -- Swampland Distance Conjecture",
            "Lyth, PRL 78 (1997) 1861 -- field excursion vs tensor-to-scalar ratio",
            "Obied, Ooguri, Spodyneiko, Vafa (2018); Agrawal et al. (2018) -- de Sitter / refined SDC",
            "this repo: v2.253 (inflation tensor r), v2.254 (Weak Gravity Conjecture), engine distance_conjecture",
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
    print("Delta phi / M_Pl    tower mass / M_Pl")
    for t in res["light_tower"]:
        print(f"  {t['delta_phi_Mpl']:5.1f}             {t['tower_mass_over_Mpl']:.2e}")
    print("\nLyth bound: r -> field excursion")
    for r in res["lyth_bound_vs_r"]:
        print(f"  r={r['r']:.3f}  Delta phi ~ {r['delta_phi_Mpl']:.2f} M_Pl  "
              f"{'TRANS-Planckian' if r['trans_planckian'] else 'sub-Planckian'}  ({r['context']})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
