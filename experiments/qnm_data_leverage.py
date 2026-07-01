"""v2.408 - SWING: the candidate's data-pinning hangs on ONE measurement -- cosmic birefringence is the only load-bearing datum.

v2.373 measured the AGGREGATE data leverage (all four ingested measurements together add ~1.7x carving). This
swing asks the per-constraint question: of the four data constraints (cosmic birefringence, Eot-Wash sub-mm
gravity, GW speed, GW dispersion), which actually pin the candidate -- is its data support broad, or
concentrated in one experiment? Method: drop each data constraint and measure how much the local feasible
region grows.

Result: only ONE datum carves. Dropping cosmic birefringence opens the local feasible region 7.4x; dropping any
of the other three -- sub-mm, GW speed, GW dispersion -- opens it 1.0x (no change). Sub-mm is satisfied
throughout the local region (the theory screens, v2.354, so the bound never bites there, even though it
mandates screening as a qualitative feature); GW speed and dispersion are frequency-suppressed and non-binding
(v2.358). So of the four ingested measurements, ONLY cosmic birefringence actively pins the candidate -- it is
the single load-bearing datum.

This sharpens the falsifiability picture to a precise, honest statement: the candidate's DATA support is
concentrated in one ~3.6-sigma hint (cosmic birefringence, v2.329). If that hint evaporates, the data-pinning
largely vanishes: the region grows ~7x and the theory-only Z2 handedness mirror returns (two islands, v2.406).
So while the candidate's STRUCTURE is robust on four independent axes (v2.405-407), its DATA-pinning is
birefringence-CONTINGENT -- exactly as every honest-scope caveat has said, now quantified per-constraint. The
one measurement to watch is cosmic birefringence (LiteBIRD / CMB-S4), and it is also the one that broke the
mirror degeneracy to select a single candidate.
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
from experiments.stack import build_stack

VERSION = "v2.408"
DEFAULT_OUT = Path("experiments/results/v2.408/qnm_data_leverage.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CON = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
FULL_KW = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
               include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def run(n_pts: int = 6000, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    pts = np.clip(CON + rng.uniform(-0.15, 0.15, (n_pts, 6)), 0.0, None)

    def frac(stack):
        return float(np.mean([all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, p)), name="x"), stack).results) for p in pts]))

    f_full = frac(build_stack(**FULL_KW))
    drops = {
        "cosmic_birefringence": dict(include_birefringence=False),
        "submm_screening": dict(include_data=False),
        "gw_speed": dict(include_gw_speed=False),
        "gw_dispersion": dict(include_gw_dispersion=False),
    }
    leverage = {}
    for name, kw in drops.items():
        base = dict(FULL_KW); base.update(kw)
        f = frac(build_stack(**base))
        leverage[name] = {"fraction_without": round(f, 4), "opens_x": round(f / f_full, 1) if f_full > 0 else None}

    biref_x = leverage["cosmic_birefringence"]["opens_x"]
    others_max = max(leverage[k]["opens_x"] for k in ("submm_screening", "gw_speed", "gw_dispersion"))

    checks = {
        "birefringence_is_load_bearing": biref_x > 3.0,
        "other_data_constraints_non_binding": others_max < 1.5,
        "single_load_bearing_datum": biref_x > 3.0 and others_max < 1.5,
        "full_region_small": f_full < 0.05,
        "birefringence_dominates_by_far": biref_x > 4 * others_max,
    }

    return {
        "version": VERSION,
        "full_local_feasible_fraction": round(f_full, 4),
        "per_datum_leverage": leverage,
        "birefringence_opens_x": biref_x,
        "other_data_max_opens_x": others_max,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's data-pinning hangs on ONE measurement -- cosmic birefringence is the only "
            "load-bearing datum. Of the four ingested measurements, dropping cosmic birefringence opens the "
            "local feasible region 7.4x, while dropping the sub-mm bound, the GW speed bound, or the GW "
            "dispersion bound opens it 1.0x (no change). Sub-mm is satisfied throughout the local region -- "
            "the theory screens (v2.354), so the bound mandates screening as a qualitative FEATURE but never "
            "bites inside the feasible region -- and GW speed/dispersion are frequency-suppressed and "
            "non-binding (v2.358). So only cosmic birefringence actively CARVES the candidate. This sharpens "
            "the falsifiability picture to a precise, honest statement: the candidate's DATA support is "
            "concentrated in one ~3.6-sigma hint (v2.329) -- if that hint evaporates, the data-pinning largely "
            "vanishes (the region grows ~7x and the theory-only Z2 handedness mirror returns, two islands, "
            "v2.406). The complete honest picture is therefore two-sided: the candidate's STRUCTURE is robust "
            "on four independent axes (family, basis, adversarial, prefactor -- v2.405-407), but its "
            "DATA-pinning is birefringence-CONTINGENT, resting on a single unconfirmed measurement. These are "
            "not in tension -- the swampland-complete carving (theory constraints) does most of the work "
            "(v2.373: data adds only ~1.7x aggregate), and the one datum that does bind is birefringence, "
            "which both pins the parity magnitude AND breaks the mirror to select a unique candidate. So 'the "
            "one experiment to watch' is unambiguous: cosmic birefringence (LiteBIRD / CMB-S4). It is the "
            "candidate's single empirical lifeline -- and CMB-S4's independent test of the matter sector "
            "(v2.395, the large-g_4 requirement) is the SECOND, orthogonal near-future probe, so the two "
            "make-or-break measurements are birefringence (parity/data-pinning) and the CMB-S4 inflationary "
            "self-coupling (matter dominance)."
        ),
        "honest_scope": (
            "Leverage is measured as the growth of the LOCAL feasible fraction (constructed +/- 0.15) when a "
            "constraint is dropped, so the 7.4x is a local number; the global leverage would differ, but "
            "birefringence's DOMINANCE (the only data constraint that binds locally) is robust. 'Sub-mm opens "
            "1.0x' means it does not shrink the local feasible region -- NOT that it is irrelevant: it "
            "mandates that the theory screen (v2.354), a real qualitative constraint on the theory's nature, "
            "but that requirement is satisfied throughout the local box so dropping it does not enlarge the "
            "region; its region-SHRINKING leverage is ~0 while its role is real. GW speed/dispersion are "
            "genuinely non-binding (frequency-suppressed, v2.358). The 'drop birefringence -> Z2 returns' link "
            "is the v2.406 mechanism (birefringence sign-selects the handedness). This is a per-constraint "
            "leverage audit of the four data inputs; it adds no new physical datum, it QUANTIFIES the "
            "pervasive 'birefringence-contingent' caveat. The birefringence detection itself is a ~3.6-sigma "
            "HINT (v2.329), not a discovery, with detector-angle-calibration systematics. Robust content: of "
            "the four ingested measurements only cosmic birefringence carves the candidate region (7.4x local "
            "leverage vs 1.0x for the others), so the candidate is structurally robust but data-pinned by a "
            "single unconfirmed measurement -- LiteBIRD/CMB-S4 is the empirical lifeline. Local leverage, "
            "sub-mm role-vs-leverage distinguished, hint-contingent. A data-leverage swing."
        ),
        "references": [
            "this repo: v2.373 (aggregate data leverage ~1.7x), v2.406 (birefringence breaks the Z2 handedness mirror), v2.404 (channels dark/non-binding), v2.358 (GW speed/dispersion non-binding), v2.354 (sub-mm mandates screening), v2.329 (birefringence ~3.6-sigma hint caveat), v2.395 (CMB-S4 matter test)",
            "physics: cosmic birefringence beta=0.34+/-0.09 deg (Minami-Komatsu / Eskilt-Komatsu); Eot-Wash sub-mm; GW speed/dispersion (LIGO/GW170817)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=6000)
    args = p.parse_args()
    res = run(n_pts=args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING: cosmic birefringence is the candidate's ONLY load-bearing datum:")
    print(f"  full-stack local feasible fraction: {res['full_local_feasible_fraction']}")
    for k, v in res["per_datum_leverage"].items():
        print(f"  drop {k:<22} -> opens region {v['opens_x']}x")
    print(f"  => only cosmic birefringence carves ({res['birefringence_opens_x']}x); the other three data constraints ~1x")
    print(f"  => structure robust (4 axes, v2.405-407) but DATA-pinning contingent on one ~3.6-sigma hint (LiteBIRD/CMB-S4 = the lifeline)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
