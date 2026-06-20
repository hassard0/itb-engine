"""Source-discovery queue for the joint g8 packet blocker (v2.99)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_joint_packet_acceptance_gate import (
    REQUIRED_JOINT_PACKET_FIELDS,
)


VERSION = "v2.99"
SCAN_DATE = "2026-06-20"


def current_joint_source_candidates() -> list[dict[str, Any]]:
    return [
        {
            "label": "bresciani_partial_wave_unitarity_bounds_2025",
            "source_url": "https://arxiv.org/abs/2504.12855",
            "source_type": "primary_theory_formalism",
            "candidate_role": "g8_formalism_seed",
            "potential_axes": ["g_8"],
            "supplies": [
                "partial_wave_formalism",
                "amplitude_operator_basis_seed",
            ],
            "missing_gate_capabilities": [
                "external_numeric_measurement",
                "engine_g8_normalization",
                "joint_likelihood_or_covariance",
                "secondary_axis_measurement",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "derive_source_backed_projection_to_engine_g8",
                "attach_to_public_numeric_measurement_or_reanalysis",
                "close_lower_moment_mixing_model",
            ],
            "citation": "Bresciani, Levati, and Paradisi, Amplitudes and partial wave unitarity bounds",
        },
        {
            "label": "liu_yunes_gw170608_higher_curvature_eft_2024",
            "source_url": "https://arxiv.org/abs/2407.08929",
            "source_type": "primary_measurement_analysis",
            "candidate_role": "gw_higher_curvature_secondary_axis_seed",
            "potential_axes": ["g_C", "g_R2"],
            "supplies": [
                "full_bayesian_gw_analysis",
                "higher_curvature_eft_constraints",
                "public_event_identifier_gw170608",
            ],
            "missing_gate_capabilities": [
                "engine_axis_normalization_to_g_C_or_g_R2",
                "joint_g8_component",
                "public_engine_joint_covariance",
                "shared_g8_secondary_eft_domain",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "map_alpha_couplings_to_engine_secondary_axis",
                "check_public_samples_or_reproduce_likelihood",
                "combine_with_source_backed_g8_projection",
            ],
            "citation": "Liu and Yunes, Robust and improved constraints on higher-curvature gravitational effective-field-theory with the GW170608 event",
        },
        {
            "label": "gwosc_gw170608_open_data_release",
            "source_url": "https://gwosc.org/GWTC-1/",
            "source_type": "public_data_product",
            "candidate_role": "public_reanalysis_input",
            "potential_axes": ["g_C", "g_R2", "g_8"],
            "supplies": [
                "public_strain_data",
                "event_metadata",
                "reanalysis_input",
            ],
            "missing_gate_capabilities": [
                "modified_gravity_waveform_adapter",
                "engine_axis_normalization",
                "public_joint_likelihood",
                "closed_systematics_budget",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "build_public_reanalysis_pipeline",
                "inject_engine_axes_into_waveform_model",
                "export_joint_likelihood_packet_for_v2_98_gate",
            ],
            "citation": "Gravitational Wave Open Science Center, GWTC-1 data release and GW170608 public data",
        },
        {
            "label": "gwastro_o2_bbh_posterior_release",
            "source_url": "https://github.com/gwastro/o2-bbh-pe",
            "source_type": "public_posterior_samples",
            "candidate_role": "public_posterior_seed",
            "potential_axes": ["g_C", "g_R2"],
            "supplies": [
                "public_gr_parameter_posteriors",
                "reproducible_pycbc_inference_material",
            ],
            "missing_gate_capabilities": [
                "modified_gravity_engine_axis_samples",
                "g8_axis_component",
                "joint_engine_covariance",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "use_as_validation_fixture_for_public_reanalysis_pipeline",
                "reconstruct_or_rerun_likelihood_with_engine_axis_model",
            ],
            "citation": "De et al., Posterior samples of the parameters of binary black holes from Advanced LIGO and Virgo's second observing run",
        },
        {
            "label": "bernard_eft_gravitational_wave_dictionary_2025",
            "source_url": "https://arxiv.org/abs/2507.17143",
            "source_type": "primary_theory_dictionary",
            "candidate_role": "observation_to_eft_dictionary",
            "potential_axes": ["g_C", "g_R2"],
            "supplies": [
                "curvature_operator_scaling_dictionary",
                "inspiral_observation_interpretation_bridge",
            ],
            "missing_gate_capabilities": [
                "numeric_event_likelihood",
                "engine_axis_jacobian",
                "g8_axis_component",
                "closed_systematics_budget",
            ],
            "adapter_work_items": [
                "translate_dictionary_terms_to_engine_secondary_axes",
                "pair_with_public_gw_reanalysis",
                "derive_covariance_export_format",
            ],
            "citation": "Bernard, Giri, Lehner, and Sturani, Generic EFT-motivated beyond General Relativity gravitational wave tests and their curvature dependence",
        },
        {
            "label": "murata_short_range_inverse_square_review_2026",
            "source_url": "https://arxiv.org/abs/2605.18212",
            "source_type": "primary_measurement_review",
            "candidate_role": "gR2_secondary_axis_seed",
            "potential_axes": ["g_R2"],
            "supplies": [
                "short_range_gravity_constraint_collection",
                "yukawa_power_law_parametrization_bridge",
            ],
            "missing_gate_capabilities": [
                "engine_gR2_normalization",
                "g8_axis_component",
                "joint_likelihood_with_g8",
                "shared_eft_domain",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "derive_yukawa_to_engine_gR2_adapter",
                "extract_or_digitize_public_constraint_envelope",
                "combine_only_after_real_g8_packet_exists",
            ],
            "citation": "Murata, Fujiie, and Suzuki, Short-Range Tests of the Gravitational Inverse-Square Law",
        },
        {
            "label": "sutton_quadratic_weyl_constraints_2025",
            "source_url": "https://arxiv.org/abs/2504.15005",
            "source_type": "primary_theory_constraint",
            "candidate_role": "gC_secondary_axis_seed",
            "potential_axes": ["g_C"],
            "supplies": [
                "quadratic_weyl_parameter_bounds",
                "analytical_stability_constraints",
            ],
            "missing_gate_capabilities": [
                "public_measurement_likelihood",
                "engine_gC_normalization",
                "g8_axis_component",
                "joint_covariance",
                "framework_pair_exclusion_math",
            ],
            "adapter_work_items": [
                "map_quadratic_weyl_alpha_to_engine_gC",
                "decide_whether_analytic_bound_can_be_nonclaim_design_constraint",
                "pair_with_real_g8_packet_or_gw_reanalysis",
            ],
            "citation": "Sutton, de Felice, and Sakellariadou, Analytical constraints on gravitational models with a quadratic Weyl tensor",
        },
    ]


def _readiness_score(candidate: dict[str, Any]) -> int:
    supplied = len(candidate["supplies"])
    missing = len(candidate["missing_gate_capabilities"])
    return max(0, 10 + supplied - missing)


def _candidate_row(candidate: dict[str, Any]) -> dict[str, Any]:
    missing = candidate["missing_gate_capabilities"]
    work_items = candidate["adapter_work_items"]
    return {
        **candidate,
        "readiness_score": _readiness_score(candidate),
        "claim_ready_now": False,
        "schema_ready_now": False,
        "blocks_v2_98_gate": bool(missing),
        "missing_gate_capability_count": len(missing),
        "adapter_work_item_count": len(work_items),
        "next_build_action": work_items[0],
    }


def _composite_build_routes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_label = {row["label"]: row for row in rows}
    return [
        {
            "route": "gw_reanalysis_to_joint_secondary_packet",
            "status": "buildable_but_not_completed",
            "inputs": [
                "gwosc_gw170608_open_data_release",
                "liu_yunes_gw170608_higher_curvature_eft_2024",
                "bernard_eft_gravitational_wave_dictionary_2025",
            ],
            "target_gate": "v2.98_g8_joint_packet_acceptance_gate",
            "can_attack": ["g_C", "g_R2"],
            "still_missing": [
                "source_backed_g8_projection",
                "joint_engine_axis_likelihood_export",
                "framework_pair_exclusion_math",
            ],
            "next_build_action": "map_public_gw_reanalysis_parameters_to_engine_secondary_axis",
            "aggregate_readiness_score": sum(
                by_label[label]["readiness_score"]
                for label in [
                    "gwosc_gw170608_open_data_release",
                    "liu_yunes_gw170608_higher_curvature_eft_2024",
                    "bernard_eft_gravitational_wave_dictionary_2025",
                ]
            ),
        },
        {
            "route": "partial_wave_g8_operator_identity_build",
            "status": "buildable_formalism_route",
            "inputs": ["bresciani_partial_wave_unitarity_bounds_2025"],
            "target_gate": "v2.98_g8_joint_packet_acceptance_gate",
            "can_attack": ["g_8"],
            "still_missing": [
                "numeric_measurement",
                "engine_g8_jacobian",
                "public_covariance",
            ],
            "next_build_action": "derive_source_backed_projection_to_engine_g8",
            "aggregate_readiness_score": by_label[
                "bresciani_partial_wave_unitarity_bounds_2025"
            ]["readiness_score"],
        },
        {
            "route": "short_range_gR2_secondary_adapter",
            "status": "buildable_secondary_axis_route",
            "inputs": ["murata_short_range_inverse_square_review_2026"],
            "target_gate": "v2.98_g8_joint_packet_acceptance_gate",
            "can_attack": ["g_R2"],
            "still_missing": [
                "engine_gR2_normalization",
                "joint_likelihood_with_g8",
            ],
            "next_build_action": "derive_yukawa_to_engine_gR2_adapter",
            "aggregate_readiness_score": by_label[
                "murata_short_range_inverse_square_review_2026"
            ]["readiness_score"],
        },
        {
            "route": "quadratic_weyl_gC_secondary_adapter",
            "status": "buildable_secondary_axis_route",
            "inputs": ["sutton_quadratic_weyl_constraints_2025"],
            "target_gate": "v2.98_g8_joint_packet_acceptance_gate",
            "can_attack": ["g_C"],
            "still_missing": [
                "engine_gC_normalization",
                "public_measurement_likelihood",
                "joint_likelihood_with_g8",
            ],
            "next_build_action": "map_quadratic_weyl_alpha_to_engine_gC",
            "aggregate_readiness_score": by_label[
                "sutton_quadratic_weyl_constraints_2025"
            ]["readiness_score"],
        },
    ]


def diagnose_g8_joint_source_discovery_queue() -> dict[str, Any]:
    candidates = [_candidate_row(candidate) for candidate in current_joint_source_candidates()]
    candidates.sort(
        key=lambda row: (-row["readiness_score"], row["label"])
    )
    build_routes = _composite_build_routes(candidates)
    build_routes.sort(
        key=lambda row: (-row["aggregate_readiness_score"], row["route"])
    )
    source_urls = [row["source_url"] for row in candidates]
    claim_ready = [row["label"] for row in candidates if row["claim_ready_now"]]
    schema_ready = [row["label"] for row in candidates if row["schema_ready_now"]]

    return {
        "version": VERSION,
        "scan_date": SCAN_DATE,
        "basis": [
            "v2.98_g8_joint_packet_acceptance_gate",
            "current_public_source_discovery_2026_06_20",
            "web_search_primary_or_public_records",
        ],
        "gate_target": "v2.98_g8_joint_packet_acceptance_gate",
        "required_joint_packet_fields": list(REQUIRED_JOINT_PACKET_FIELDS),
        "candidate_count": len(candidates),
        "schema_ready_candidates": schema_ready,
        "claim_ready_candidates": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "source_urls_checked": source_urls,
        "candidates_ranked": candidates,
        "composite_build_routes_ranked": build_routes,
        "selected_next_build_route": build_routes[0],
        "selected_next_build_action": build_routes[0]["next_build_action"],
        "route_status": "joint_source_queue_ready_next_adapter_build_selected",
        "best_next_artifact": (
            "Build the selected adapter action, then re-evaluate whether a "
            "source-backed packet can satisfy the v2.98 gate."
        ),
        "interpretation": (
            "The blocker is now decomposed into buildable source-adapter tasks. "
            "No checked source is claim-ready, but the next adapter target is "
            "explicit rather than an open-ended stop condition."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.99/g8_joint_source_discovery_queue.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_joint_source_discovery_queue()
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
