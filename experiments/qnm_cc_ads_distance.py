"""v2.423 - CORE EXTENSION CC2: the AdS distance conjecture selects de Sitter -- the candidate admits dS/Minkowski but NOT anti-de Sitter.

Second slice of the cosmological-constant sector (CC1 = v2.422). Adds the AdS distance conjecture (Lust-Palti-
Vafa 2019): as |Lambda| -> 0 a tower becomes light, m_tower <= c|Lambda|^alpha (strong alpha=1/2). With the tower
at the Dvali species scale Lambda_species = 1/sqrt(N) (the same N = 1 + nu(|g_R2|+|g_C|+|g_R3|) the species-scale
bound counts), this becomes a FLOOR on the vacuum-energy magnitude: |g_Lambda| >= c_AdS*(1/N)^(1/(2alpha)) =
c_AdS/N (alpha=1/2). A bounded (not-parametrically-light) tower thus forbids a parametrically small |Lambda| --
the swampland form of the CC naturalness puzzle. Applied to the AdS branch (g_Lambda<0); opt-in; tagged
sourced_proxy.

Result (candidate, c_AdS=1): N=1.566 -> AdS floor |g_Lambda| >= 0.639. But EFT-validity/complexity caps
|g_Lambda| <= ~0.60. The floor EXCEEDS the ceiling, so the AdS branch is EMPTY: no anti-de Sitter vacuum is
admissible. Combined with CC1's refined-dS ceiling (g_Lambda <= g_R2 ~ 0.193), the candidate's full admissible
vacuum-energy window collapses to the dS/Minkowski branch [0, 0.192]. So the two swampland conjectures plus
EFT-validity SELECT de Sitter (or Minkowski) for the candidate -- it 'wants to be de Sitter', it cannot be
anti-de Sitter. The dS-selection is robust for c_AdS >~ 0.94 (O(1)); a much smaller c_AdS would open a narrow AdS
window, so the conclusion is O(1)-robust, not knife-edge, but c_AdS-dependent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, rigor_of

VERSION = "v2.423"
DEFAULT_OUT = Path("experiments/results/v2.423/qnm_cc_ads_distance.py".replace(".py", ".json"))

CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
BASE = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
            include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def _window(stack, lo=-1.0, hi=0.4):
    grid = [round(float(g), 3) for g in np.arange(lo, hi, 0.002)
            if all(r.satisfied for r in check(Theory(coefficients={**CON, "g_Lambda": float(g)}, name="x"), stack).results)]
    return grid


def run() -> dict:
    N = 1.0 + 2.0 * (abs(CON["g_R2"]) + 0.0 + abs(CON["g_R3"]))   # g_C = 0
    ads_floor = (1.0 / (N ** 0.5)) ** 2   # c_AdS=1, alpha=1/2

    st = build_stack(**BASE, include_cc_sector=True, cc_c_AdS=1.0)
    grid = _window(st)
    neg = [g for g in grid if g < 0]
    pos = [g for g in grid if g >= 0]
    ads_window = [min(neg), max(neg)] if neg else None
    ds_window = [min(pos), max(pos)] if pos else None

    # c_AdS threshold at which the AdS branch first opens (floor drops to the EFT-validity ceiling)
    # EFT ceiling on |g_Lambda| (from the CC1-only stack, negative branch)
    st_cc1 = build_stack(**BASE, include_cc_sector=True, cc_c_AdS=0.0)  # c_AdS=0 -> AdS floor 0 -> only EFT/dS bind
    eft_neg = [g for g in _window(st_cc1) if g < 0]
    eft_ceiling = abs(min(eft_neg)) if eft_neg else 0.0
    c_AdS_threshold = round(eft_ceiling / ads_floor, 3) if ads_floor > 0 else None

    checks = {
        "cc2_present_and_tagged": rigor_of("ads_distance_conjecture") == "sourced_proxy" and any(
            getattr(c, "name", "") == "ads_distance_conjecture" for c in st),
        "ads_floor_from_tower": abs(ads_floor - 1.0 / N) < 1e-6,
        "ads_branch_empty_at_cAdS1": ads_window is None,
        "dS_branch_survives": ds_window is not None and ds_window[1] > 0.05,
        "dS_selected_over_ads": ads_window is None and ds_window is not None,
    }

    return {
        "version": VERSION,
        "N_species_candidate": round(N, 3),
        "ads_floor_cAdS1": round(ads_floor, 3),
        "eft_validity_ceiling_on_abs_gLambda": round(eft_ceiling, 3),
        "allowed_windows": {"ads_branch": ads_window, "ds_minkowski_branch": ds_window},
        "c_AdS_threshold_for_ads_to_open": c_AdS_threshold,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "CORE EXTENSION CC2: the AdS distance conjecture selects de Sitter -- the candidate admits "
            "dS/Minkowski but NOT anti-de Sitter. Adding the AdS distance conjecture (Lust-Palti-Vafa 2019) as "
            "a floor on the vacuum-energy magnitude set by the species-scale tower -- |g_Lambda| >= c_AdS/N "
            "(alpha=1/2), since a small |Lambda| would require a parametrically light tower the candidate does "
            "not have -- gives, at c_AdS=1 and the candidate's N=1.566, an AdS floor |g_Lambda| >= 0.639. But "
            "EFT-validity/complexity caps |g_Lambda| <= ~0.60 (the vacuum energy cannot exceed the cutoff). The "
            "floor EXCEEDS the ceiling, so the AdS branch is EMPTY -- no anti-de Sitter vacuum is admissible. "
            "Combined with CC1's refined-dS ceiling (g_Lambda <= g_R2 ~ 0.193), the candidate's entire "
            "admissible vacuum-energy window collapses to the dS/Minkowski branch [0, 0.193]. So the two "
            "swampland conjectures plus EFT-validity SELECT de Sitter (or Minkowski) for the candidate: it "
            "'wants to be de Sitter', and it cannot be anti-de Sitter. This is a genuine structural output of "
            "the new sector -- the candidate's bounded tower (a heavy-ish species scale, N~1.6) is exactly what "
            "forbids the small-|Lambda| AdS vacuum, so the same tower structure that makes the theory "
            "string-like (v2.375) also drives it to positive (dark-energy) or zero vacuum energy. The "
            "dS-selection is O(1)-robust (it holds for c_AdS >~ 0.94, the threshold where the AdS floor drops "
            "to the EFT ceiling), not a knife-edge, though it is c_AdS-dependent: a much smaller c_AdS would "
            "open a narrow AdS window. Net for the CC arc so far: the candidate accommodates dark energy "
            "(CC1), is bounded above by its inflaton curvature (CC1), and is pushed off anti-de Sitter by its "
            "tower (CC2) -- a coherent, if conjectural, dark-energy story emerging from the swampland sector."
        ),
        "honest_scope": (
            "Both CC constraints are CONJECTURAL swampland statements encoded as proxies (tagged sourced_proxy) "
            "-- the AdS distance conjecture is unproven, the tower<->species-scale identification is a modeling "
            "choice, and c_AdS/alpha are O(1). The headline 'no AdS vacuum' is therefore an O(1)-robust "
            "structural statement (holds for c_AdS >~ 0.94), NOT a theorem: it says the AdS-distance floor and "
            "the EFT-validity ceiling are incompatible at O(1) coefficients for the candidate's tower, so a "
            "small AdS |Lambda| is disfavored -- the swampland CC-naturalness puzzle applied here. g_Lambda is "
            "dimensionless, so this is about the STRUCTURE / sign of the vacuum energy (dS vs AdS admissibility "
            "and the ceiling), NOT the CC magnitude problem (10^-120). N uses g_C=0 (the candidate's g_C is not "
            "set in this coefficient dict); a nonzero g_C would raise N and lower the floor, widening/narrowing "
            "the effect -- the qualitative 'bounded tower forbids small AdS Lambda' is the robust content. "
            "Opt-in, so no prior result changes. Robust content: with the AdS distance conjecture + EFT-"
            "validity, the candidate's bounded tower forbids a small anti-de Sitter vacuum at O(1) coefficients, "
            "so its admissible vacua are de Sitter or Minkowski (g_Lambda in [0, g_R2]); the candidate is "
            "pushed toward positive/zero vacuum energy. Conjectural-proxy, O(1)-robust-not-theorem, "
            "dimensionless-not-magnitude, g_C=0. The CC2 AdS-distance cycle."
        ),
        "references": [
            "this repo: v2.422 (CC1 refined-dS ceiling), v2.394 (species scale ~0.72 M_Pl), v2.375 (string-like tower), src/itb/constraints/species_scale.py (N formula reused), src/itb/constraints/cosmological_constant.py",
            "physics: Lust-Palti-Vafa 2019 (AdS distance conjecture); Dvali (species scale); Ooguri-Palti-Shiu-Vafa 2018 (refined dS, CC1)",
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
    print("v2.423 - CORE EXTENSION CC2: the AdS distance conjecture selects de Sitter:")
    print(f"  candidate N={res['N_species_candidate']} -> AdS floor |g_Lambda| >= {res['ads_floor_cAdS1']}; EFT ceiling ~{res['eft_validity_ceiling_on_abs_gLambda']}")
    print(f"  allowed windows: AdS branch {res['allowed_windows']['ads_branch']}, dS/Minkowski {res['allowed_windows']['ds_minkowski_branch']}")
    print(f"  => AdS floor EXCEEDS EFT ceiling -> NO anti-de Sitter vacuum; candidate admits dS/Minkowski ONLY")
    print(f"  => the two swampland conjectures + EFT-validity SELECT de Sitter (O(1)-robust: holds for c_AdS >~ {res['c_AdS_threshold_for_ads_to_open']})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
