"""v2.365 - The ringdown channel's quantitative readiness: floor + cap + source coefficients present; the qNM->R4 map is the single blocker.

A synthesis that CONNECTS this session's structural ringdown results (v2.349 floor, v2.351 causality cap) to
the repo's pre-existing ParSpec/qEFT ringdown source bridge (v2.188-191) -- two bodies of work that were never
joined -- and precisely locates why the ringdown channel is not yet QUANTITATIVE. This directly scopes the
open deep-research question (is the qNM->R4 sensitivity rank-3 or rank-1?).

The ringdown channel's four pieces:
  (1) FLOOR present      -- the moment tower mandates g_R4 >= g_R3^2/g_R2 (v2.349), re-verified live here;
  (2) CAP present        -- causality bounds the floor by kappa^2 g_4 (v2.351), re-verified live here;
  (3) SOURCE COEFFS present -- the repo has source-backed qEFT ParSpec QNM deformation coefficients from
      arXiv:2205.05132 (v2.191): p_qEFT = 6, delta_omega/delta_tau coefficients, 90% bounds ~51 km -- a
      RANK-1 map (a single length scale ell_qEFT / ParSpec gamma -> the QNM deformations);
  (4) ENGINE->PARSPEC MAP missing -- the operator-basis map + axis orientation from the engine's THREE R4 axes
      (g_R4_c1, g_R4_c2, g_R4_c3, Bresciani basis) onto the ParSpec ell_qEFT axis is NOT ready (v2.190/v2.191
      contract; ready_for_framework_claim = False).

Piece (4) IS the deep-research question: the public ParSpec source supplies a rank-1 ray (one ell_qEFT axis),
the engine has three R4 axes, and whether those three map FULL-RANK (rank-3) to the QNM observables or
COLLAPSE to the rank-1 ParSpec ray is exactly the operator_basis_map + engine_axis_orientation blocker. So a
quantitative ringdown delta_omega prediction is blocked at ONE identified subpiece, and no framework
exclusion is claimable from ringdown until it is supplied (consistent with the v2.191 claim boundary).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import CANONICAL

VERSION = "v2.365"
DEFAULT_OUT = Path("experiments/results/v2.365/qnm_ringdown_channel_readiness.json")
V191 = Path("experiments/results/v2.191/r4_parspec_qeft_source_asset_audit.json")
V190 = Path("experiments/results/v2.190/r4_parspec_engine_axis_map_contract.json")

CONSTRUCTED = {"g_4": 0.529, "g_R2": 0.193, "g_R3": 0.09}


def run() -> dict:
    # (1)+(2) re-verify this session's structural ringdown results live
    floor = CONSTRUCTED["g_R3"] ** 2 / CONSTRUCTED["g_R2"]        # v2.349
    cap = CANONICAL["cemz_kappa"] ** 2 * CONSTRUCTED["g_4"]       # v2.351
    floor_present = floor > 0.0
    cap_present = floor <= cap

    # (3) source coefficients present -- read from the tested v2.191 artifact
    v191 = json.loads(V191.read_text(encoding="utf-8")) if V191.exists() else {}
    src = v191.get("source_equation_facts", {})
    gamma = src.get("parspec_gamma_relation", {})
    p_qeft = gamma.get("qeft_power")
    source_coeffs_present = (p_qeft == 6 and src.get("source_axis") == "ell_qEFT_km")

    # (4) engine->ParSpec map missing -- read the remaining blockers + claim readiness
    remaining = set(v191.get("remaining_contract_blockers_after_asset_audit", []))
    map_blockers = sorted(b for b in remaining if any(
        k in b for k in ("operator_basis_map", "engine_axis_orientation", "engine_axis_map", "axis_normalization")))
    v190 = json.loads(V190.read_text(encoding="utf-8")) if V190.exists() else {}
    target_axes = v190.get("contract", {}).get("target_engine_axes") or ["g_R4_c1", "g_R4_c2", "g_R4_c3"]
    ready_for_framework_claim = bool(v191.get("ready_for_framework_claim", False))
    map_missing = ("operator_basis_map_missing" in remaining) and not ready_for_framework_claim

    # the deep-research question IS this blocker: 3 engine R4 axes -> the rank-1 ParSpec ell_qEFT ray
    n_engine_axes = len(target_axes)
    parspec_is_rank1 = (src.get("source_axis") == "ell_qEFT_km")   # a single source axis
    rank_question_is_the_blocker = (n_engine_axes == 3 and parspec_is_rank1 and map_missing)

    readiness = {
        "1_floor_present": bool(floor_present),
        "2_cap_present": bool(cap_present),
        "3_source_qeft_coefficients_present": bool(source_coeffs_present),
        "4_engine_to_parspec_map_present": (not map_missing),
    }
    n_ready = sum(readiness.values())

    checks = {
        "floor_verified_live": floor_present,
        "cap_verified_live": cap_present,
        "source_coefficients_present_v2191": source_coeffs_present,
        "engine_parspec_map_still_blocked": map_missing,
        "deep_research_question_is_the_map_blocker": rank_question_is_the_blocker,
    }

    return {
        "version": VERSION,
        "ringdown_floor_v2349": round(floor, 4),
        "ringdown_cap_v2351": round(cap, 4),
        "source_p_qeft": p_qeft,
        "source_ref": "arXiv:2205.05132 (PhysRevD.107.044030), preserved in v2.191",
        "engine_R4_axes": target_axes,
        "parspec_source_axis": src.get("source_axis"),
        "map_blockers": map_blockers,
        "ready_for_framework_claim": ready_for_framework_claim,
        "readiness_ledger": readiness,
        "n_ready_of_4": n_ready,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The ringdown channel is quantitatively blocked at ONE precisely-identified subpiece -- and it "
            f"is exactly the open deep-research question. Joining this session's structural results with the "
            f"repo's pre-existing ParSpec source bridge (v2.188-191, which this session's ringdown work never "
            f"referenced), the channel has {n_ready} of 4 pieces ready: (1) the moment-tower FLOOR "
            f"g_R4 >= g_R3^2/g_R2 = {floor:.3f} (v2.349, re-verified live); (2) the causality CAP "
            f"g_R4_floor <= kappa^2 g_4 = {cap:.3f} (v2.351, live); (3) source-backed qEFT ParSpec QNM "
            f"deformation coefficients from arXiv:2205.05132 (v2.191: p_qEFT = {p_qeft}, a single-length-"
            f"scale ell_qEFT / ParSpec-gamma deformation -> the QNM shifts, i.e. a RANK-1 ray); but (4) the "
            f"operator-basis map + axis orientation from the engine's THREE R4 axes {target_axes} onto the "
            f"ParSpec ell_qEFT axis is NOT ready (ready_for_framework_claim = False; blockers include "
            f"operator_basis_map_missing, engine_axis_orientation_missing, engine_axis_map_jacobian_missing). "
            f"Piece (4) IS the deep-research question 'is the qNM->R4 sensitivity rank-3 or rank-1?': the "
            f"public ParSpec source supplies a rank-1 ray (one ell_qEFT axis), the engine carries three R4 "
            f"operator directions, and whether the three map FULL-RANK to the QNM observables or COLLAPSE to "
            f"the single ParSpec ray is precisely the missing operator_basis_map + engine_axis_orientation. "
            f"So the honest state of the ringdown channel is: its STRUCTURE is complete and re-verified "
            f"(floor bracketed 0 <= g_R4_floor <= kappa^2 g_4, cross-checked cross-vendor), a source bridge "
            f"and source coefficients exist, but a numerical delta_omega prediction -- and any ringdown-based "
            f"framework exclusion -- is not claimable until the rank-3-vs-rank-1 axis map is supplied. This "
            f"gives the deep-research a precise acceptance target (the v2.190 operator_basis_map contract) "
            f"and connects it to the session's floor/cap, rather than leaving 'ringdown is schematic' vague."
        ),
        "honest_scope": (
            "Pieces (1) and (2) are re-verified live here (exact arithmetic on the constructed couplings); "
            "pieces (3) and (4) are READ from the pre-existing, tested v2.191/v2.190 artifacts, not "
            "re-derived -- this is a synthesis/status that connects them, so it inherits their claim "
            "boundaries verbatim: the source coefficients are genuinely source-backed (arXiv:2205.05132) but "
            "the engine->ParSpec map is explicitly NOT a claim (v2.190 is a non-claiming contract; v2.191 "
            "ready_for_framework_claim = False). 'RANK-1 ray' describes the PUBLIC ParSpec source's single "
            "ell_qEFT axis as preserved in the repo -- whether a full rank-3 qNM->R4 map is achievable from "
            "other sources is exactly the open question, not answered here. The floor/cap remain in the "
            "toy-basis + rank-1-schematic-magnitude regime (v2.336): they bound the g_R4 COUPLING, not a "
            "sourced frequency shift. No framework exclusion is claimable from ringdown (unchanged). Robust "
            "content: the ringdown channel's structure is complete and its single quantitative blocker is "
            "the identified qNM->R4 operator-basis map, which is the deep-research question. Toy basis, O(1) "
            "prefactors. A cross-arc synthesis locating the one blocker, non-claiming."
        ),
        "references": [
            "this repo: v2.349 (ringdown floor), v2.351 (causality cap), v2.336 (rank-1 schematic magnitude) -- the structural pieces re-verified",
            "this repo: v2.188 (source bridge), v2.190 (engine-axis map contract, non-claiming), v2.191 (source-asset audit: p_qEFT=6, QNM coefficients) -- the ParSpec pieces read",
            "source: arXiv:2205.05132 / PhysRevD.107.044030 (qEFT ParSpec ringdown bounds); Bresciani R4 axes g_R4_c1/c2/c3",
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
    print("ringdown channel quantitative readiness (floor+cap+source coeffs+map):")
    for k, v in res["readiness_ledger"].items():
        print(f"  {'READY ' if v else 'BLOCKED'} {k}")
    print(f"  floor {res['ringdown_floor_v2349']} <= cap {res['ringdown_cap_v2351']}   source p_qEFT={res['source_p_qeft']}")
    print(f"  engine R4 axes {res['engine_R4_axes']} -> ParSpec {res['parspec_source_axis']} (rank-1); map blockers: {len(res['map_blockers'])}")
    print(f"  => the deep-research rank-3-vs-rank-1 question IS the operator_basis_map blocker; framework-claim-ready: {res['ready_for_framework_claim']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
