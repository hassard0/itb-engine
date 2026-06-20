"""Route decision for attacking remaining R4 claim blockers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_projection_query_surface import diagnose_r4_projection_query_surface


VERSION = "v2.151"
SOURCE_CHECK_DATE = "2026-06-20"


def r4_claim_source_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "gross_witten_1986_tree_graviton_scattering",
            "url": "https://doi.org/10.1016/0550-3213(86)90429-3",
            "role": "primary_type_II_tree_R4_normalization_candidate",
            "route": "absolute_normalization",
            "status": "candidate_primary_source_not_machine_ingested",
            "provides": [
                "tree_level_gravitational_scattering_amplitudes",
                "quartic_order_Riemann_effective_action_context",
            ],
            "missing_for_engine_claim": [
                "machine_readable_K_factor_formula",
                "K_Russo_to_Kallosh_shape_bridge",
                "alpha_prime_to_engine_Lambda_R4_conversion",
            ],
        },
        {
            "source_id": "russo_1997_type_iib_four_graviton",
            "url": "https://arxiv.org/abs/hep-th/9707241",
            "role": "tree_contact_scalar_source",
            "route": "absolute_normalization",
            "status": "partial_source_component_ready",
            "provides": [
                "A4_equals_kappa_squared_K_A4_zero",
                "A4_zero_contains_2_zeta_3_contact_scalar",
            ],
            "missing_for_engine_claim": [
                "dimensionless_K_convention_bridge",
                "engine_Lambda_R4_unit_conversion",
            ],
        },
        {
            "source_id": "kallosh_lee_rube_2008_n8_r4_shape",
            "url": "https://arxiv.org/abs/0811.3417",
            "role": "source_backed_helicity_shape",
            "route": "absolute_normalization",
            "status": "shape_ready_normalization_open",
            "provides": [
                "K_plus_equals_1",
                "K_minus_equals_0",
                "Bresciani_shape_projection_input",
            ],
            "missing_for_engine_claim": [
                "absolute_type_II_string_alpha_prime_coefficient",
                "engine_Lambda_R4_unit_conversion",
            ],
        },
        {
            "source_id": "bresciani_levati_paradisi_2025_spin2_basis",
            "url": "https://arxiv.org/abs/2504.12855",
            "role": "target_R4_basis_and_positivity_bound",
            "route": "projection_and_positivity",
            "status": "basis_ready_not_measurement_likelihood",
            "provides": [
                "Bresciani_c_i_spin2_basis",
                "c_plus_c_minus_contract",
                "spin2_positivity_bound",
            ],
            "missing_for_engine_claim": [
                "public_measurement_likelihood",
                "framework_excluding_discriminator_math",
            ],
        },
        {
            "source_id": "baccianti_eberhardt_mizera_2025_4graviton_one_loop",
            "url": "https://arxiv.org/abs/2507.22105",
            "role": "recent_four_graviton_amplitude_context",
            "route": "absolute_normalization_context",
            "status": "context_not_tree_R4_bridge",
            "provides": [
                "finite_alpha_prime_one_loop_four_graviton_amplitudes",
                "modern_source_trail_for_string_amplitude_normalization",
            ],
            "missing_for_engine_claim": [
                "tree_level_R4_engine_normalization",
                "Bresciani_c_i_measurement_likelihood",
            ],
        },
        {
            "source_id": "public_gravity_r4_likelihood_search_2026_06_20",
            "url": "https://arxiv.org/",
            "role": "public_measurement_likelihood_route_check",
            "route": "measurement_likelihood",
            "status": "no_ready_public_R4_axis_likelihood_found",
            "provides": [],
            "missing_for_engine_claim": [
                "public_covariance_or_likelihood_over_g_R4_c1_c2_c3",
                "source_backed_projection_from_observable_to_Bresciani_R4_axes",
            ],
        },
    ]


def evaluate_r4_claim_attack_routes() -> dict[str, Any]:
    query_surface = diagnose_r4_projection_query_surface()
    rows = r4_claim_source_rows()
    route_rows = {
        "absolute_normalization": [
            row for row in rows if row["route"] in {
                "absolute_normalization",
                "absolute_normalization_context",
            }
        ],
        "measurement_likelihood": [
            row for row in rows if row["route"] == "measurement_likelihood"
        ],
    }
    route_scores = {
        "absolute_normalization": {
            "ready_components": [
                row["source_id"] for row in route_rows["absolute_normalization"]
                if row["status"] in {
                    "partial_source_component_ready",
                    "shape_ready_normalization_open",
                }
            ],
            "claim_ready_now": False,
            "score": 2,
            "primary_blockers": [
                "machine_readable_K_factor_formula",
                "K_Russo_to_Kallosh_shape_bridge",
                "alpha_prime_to_engine_Lambda_R4_conversion",
            ],
        },
        "measurement_likelihood": {
            "ready_components": [],
            "claim_ready_now": False,
            "score": 0,
            "primary_blockers": [
                "public_covariance_or_likelihood_over_g_R4_c1_c2_c3",
                "observable_to_Bresciani_R4_projection",
            ],
        },
    }
    selected_route = "absolute_normalization"
    return canonicalize_json_floats({
        "source_check_date": SOURCE_CHECK_DATE,
        "query_surface_ready": bool(
            query_surface["ready_internal_query_keys"]
        ),
        "query_surface_claim_ready": bool(
            query_surface["claim_ready_query_keys"]
        ),
        "source_rows": rows,
        "route_scores": route_scores,
        "selected_attack_route": selected_route,
        "selected_route_reason": (
            "The adapter/query plumbing is ready and the absolute route already "
            "has source-backed shape plus Russo contact-scalar components. The "
            "measurement route currently lacks a public likelihood over the "
            "Bresciani R4 axes."
        ),
        "selected_next_source_target": (
            "gross_witten_1986_tree_graviton_scattering"
        ),
        "selected_next_build_action": (
            "ingest_or_rederive_gross_witten_k_formula_and_lambda_bridge"
        ),
    })


def diagnose_r4_claim_blocker_attack_plan() -> dict[str, Any]:
    route = evaluate_r4_claim_attack_routes()
    blockers = sorted({
        blocker
        for score in route["route_scores"].values()
        for blocker in score["primary_blockers"]
    })
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.150_r4_projection_query_surface",
            "v2.146_k_convention_bridge_audit",
            "source_check_2026_06_20",
        ],
        "route_evaluation": route,
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "ready_to_claim_now": False,
        "route_status": "r4_claim_blockers_ranked_absolute_normalization_next",
        "selected_next_build_action": route["selected_next_build_action"],
        "best_next_artifact": (
            "A machine-checkable Gross-Witten/Russo/Kallosh K-convention bridge "
            "and alpha-prime to engine Lambda_R4 policy. If that fails, the "
            "secondary route is a public R4-axis measurement likelihood search."
        ),
        "interpretation": (
            "The R4 adapter path is no longer blocked by plumbing. The only "
            "defensible next attack is the remaining claim evidence: absolute "
            "normalization first, because it has partial primary-source support; "
            "measurement likelihood second, because no public likelihood over "
            "the Bresciani R4 axes was identified in this source check."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.151/r4_claim_blocker_attack_plan.json",
    )
    args = parser.parse_args()

    result = diagnose_r4_claim_blocker_attack_plan()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
