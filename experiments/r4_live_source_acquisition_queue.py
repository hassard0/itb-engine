"""Live-source acquisition queue for the R4 shape likelihood route."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_public_shape_likelihood_search import (
    LIKELIHOOD_ACCEPTANCE_FIELDS,
)
from experiments.r4_shape_likelihood_packet_manifest import (
    REQUIRED_PACKET_FIELDS,
    TARGET_AXES,
)
from experiments.r4_shape_likelihood_ingestion_adapter import (
    diagnose_r4_shape_likelihood_ingestion_adapter,
)


VERSION = "v2.174"
SCAN_DATE = "2026-06-20"


def current_r4_live_source_candidates() -> list[dict[str, Any]]:
    return [
        {
            "label": "bresciani_partial_wave_unitarity_bounds_2025",
            "source_url": "https://arxiv.org/abs/2504.12855",
            "source_type": "primary_theory_formalism",
            "candidate_role": "r4_shape_axis_formalism",
            "potential_axes": list(TARGET_AXES),
            "supplies": [
                "spin2_partial_wave_formalism",
                "amplitude_operator_basis_seed",
                "bresciani_r4_axis_context",
            ],
            "missing_packet_capabilities": [
                "public_likelihood_or_covariance",
                "central_values_over_engine_r4_axes",
                "covariance_over_g_R4_c1_c2_c3",
                "experimental_or_reanalysis_data",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "derive_machine_axis_dictionary_from_bresciani_basis",
                "pair_with_public_reanalysis_or_likelihood_source",
                "export_v2_160_shape_likelihood_packet",
            ],
            "citation": (
                "Bresciani, Levati, and Paradisi, Amplitudes and partial wave "
                "unitarity bounds"
            ),
        },
        {
            "label": "gwosc_public_catalog_and_event_data",
            "source_url": "https://gwosc.org/eventapi/html/GWTC/",
            "source_type": "public_data_product",
            "candidate_role": "public_reanalysis_input",
            "potential_axes": [],
            "supplies": [
                "public_event_catalog",
                "public_strain_data_entry_points",
                "reanalysis_input",
            ],
            "missing_packet_capabilities": [
                "modified_gravity_r4_waveform_adapter",
                "maps_to_bresciani_r4_axes",
                "public_r4_shape_likelihood",
                "closed_systematics_budget",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "build_public_gw_reanalysis_fixture_for_r4_waveform_model",
                "attach_r4_shape_axis_projection",
                "export_covariance_over_engine_r4_axes",
            ],
            "citation": "Gravitational Wave Open Science Center public event data",
        },
        {
            "label": "liu_yunes_higher_curvature_gw_constraints_2025",
            "source_url": "https://arxiv.org/abs/2407.08929",
            "source_type": "primary_measurement_analysis",
            "candidate_role": "higher_curvature_gw_constraint_seed",
            "potential_axes": ["higher_curvature_eft_alpha"],
            "supplies": [
                "bayesian_higher_curvature_gw_analysis",
                "strong_field_constraint_context",
                "event_reanalysis_design_target",
            ],
            "missing_packet_capabilities": [
                "r4_shape_axis_decomposition",
                "maps_to_bresciani_r4_axes",
                "public_covariance_over_engine_r4_axes",
                "target_axes_complete",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "map_higher_curvature_alpha_to_engine_r4_shape_axes",
                "check_public_samples_or_reproduce_likelihood",
                "test_v2_160_manifest_export",
            ],
            "citation": (
                "Liu and Yunes, Robust and improved constraints on "
                "higher-curvature gravitational effective-field-theory"
            ),
        },
        {
            "label": "matching_tidal_deformability_wilson_coefficients_2026",
            "source_url": "https://arxiv.org/abs/2604.04259",
            "source_type": "primary_theory_mapping",
            "candidate_role": "wilson_matching_method_seed",
            "potential_axes": ["tidal_wilson_coefficients", "cubic_curvature"],
            "supplies": [
                "wilson_coefficient_matching_method",
                "tidal_love_number_mapping_controls",
                "higher_curvature_matching_caveats",
            ],
            "missing_packet_capabilities": [
                "quartic_r4_shape_axes",
                "public_likelihood_or_covariance",
                "maps_to_bresciani_r4_axes",
                "central_values_over_engine_r4_axes",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "audit_whether_matching_method_extends_to_quartic_r4",
                "derive_required_extra_terms_for_r4_shape_packet",
                "pair_with_public_gw_likelihood_only_after_axis_map_exists",
            ],
            "citation": (
                "Matching tidal deformability coefficients to black-hole "
                "Wilson coefficients in higher-curvature EFT"
            ),
        },
        {
            "label": "causality_constraints_gravitational_efts_2021",
            "source_url": "https://arxiv.org/abs/2112.05054",
            "source_type": "primary_theory_constraint",
            "candidate_role": "dimension8_causality_bound_seed",
            "potential_axes": ["dimension8_gravity_operators"],
            "supplies": [
                "causality_constraints_on_gravity_eft",
                "black_hole_background_consistency_context",
            ],
            "missing_packet_capabilities": [
                "external_numeric_measurement",
                "public_likelihood_or_covariance",
                "maps_to_bresciani_r4_axes",
                "r4_shape_covariance",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "compare_dimension8_operator_basis_to_engine_r4_axes",
                "mark_as_theory_constraint_not_likelihood_packet",
                "use_only_as_claim_guard_context",
            ],
            "citation": "Causality Constraints on Gravitational Effective Field Theories",
        },
        {
            "label": "curvature_dependence_gw_tests_dictionary_2024",
            "source_url": "https://arxiv.org/abs/2407.07043",
            "source_type": "primary_theory_dictionary",
            "candidate_role": "gw_observation_to_eft_dictionary",
            "potential_axes": ["higher_curvature_gw_deviation_scaling"],
            "supplies": [
                "curvature_scaling_argument",
                "gw_test_dictionary_context",
            ],
            "missing_packet_capabilities": [
                "numeric_r4_shape_likelihood",
                "maps_to_bresciani_r4_axes",
                "public_covariance_over_engine_r4_axes",
                "closed_systematics_budget",
                "framework_exclusion_math",
            ],
            "adapter_work_items": [
                "translate_dictionary_terms_to_r4_shape_requirements",
                "pair_with_event_reanalysis_after_waveform_adapter_exists",
                "test_against_v2_160_manifest",
            ],
            "citation": "Curvature dependence of gravitational-wave tests of GR",
        },
    ]


def _readiness_score(candidate: dict[str, Any]) -> int:
    supplies = len(candidate["supplies"])
    missing = len(candidate["missing_packet_capabilities"])
    axis_bonus = 2 if set(TARGET_AXES) & set(candidate["potential_axes"]) else 0
    data_bonus = 2 if candidate["source_type"] == "public_data_product" else 0
    return max(0, 10 + supplies + axis_bonus + data_bonus - missing)


def _candidate_row(candidate: dict[str, Any]) -> dict[str, Any]:
    missing = candidate["missing_packet_capabilities"]
    criteria = {
        field: False for field in LIKELIHOOD_ACCEPTANCE_FIELDS
    }
    if candidate["source_type"] == "public_data_product":
        criteria["reproducible_data_or_code"] = True
        criteria["systematics_or_domain_declared"] = True
    if "maps_to_bresciani_r4_axes" not in missing:
        criteria["maps_to_bresciani_r4_axes"] = True

    return canonicalize_json_floats({
        **candidate,
        "readiness_score": _readiness_score(candidate),
        "acceptance_criteria_status": criteria,
        "required_manifest_fields": list(REQUIRED_PACKET_FIELDS),
        "claim_ready_now": False,
        "manifest_ready_now": False,
        "ingestion_ready_now": False,
        "missing_packet_capability_count": len(missing),
        "adapter_work_item_count": len(candidate["adapter_work_items"]),
        "next_build_action": candidate["adapter_work_items"][0],
    })


def _composite_build_routes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_label = {row["label"]: row for row in rows}
    return [
        {
            "route": "bresciani_axis_dictionary_plus_public_gw_reanalysis",
            "status": "buildable_but_not_packet_ready",
            "inputs": [
                "bresciani_partial_wave_unitarity_bounds_2025",
                "gwosc_public_catalog_and_event_data",
                "liu_yunes_higher_curvature_gw_constraints_2025",
            ],
            "target_gate": "v2.162_r4_shape_likelihood_ingestion_adapter",
            "can_attack": list(TARGET_AXES),
            "still_missing": [
                "modified_gravity_r4_waveform_adapter",
                "public_covariance_over_engine_r4_axes",
                "framework_exclusion_math",
                "external_adversarial_review",
            ],
            "next_build_action": (
                "derive_machine_axis_dictionary_from_bresciani_basis"
            ),
            "aggregate_readiness_score": sum(
                by_label[label]["readiness_score"]
                for label in [
                    "bresciani_partial_wave_unitarity_bounds_2025",
                    "gwosc_public_catalog_and_event_data",
                    "liu_yunes_higher_curvature_gw_constraints_2025",
                ]
            ),
        },
        {
            "route": "wilson_matching_method_to_r4_shape_requirements",
            "status": "theory_mapping_audit_needed",
            "inputs": [
                "matching_tidal_deformability_wilson_coefficients_2026",
                "causality_constraints_gravitational_efts_2021",
            ],
            "target_gate": "v2.160_r4_shape_likelihood_packet_manifest",
            "can_attack": ["axis_mapping", "normalization", "domain"],
            "still_missing": [
                "quartic_r4_shape_extension",
                "public_likelihood_or_covariance",
                "central_values_over_engine_r4_axes",
            ],
            "next_build_action": "audit_whether_matching_method_extends_to_quartic_r4",
            "aggregate_readiness_score": sum(
                by_label[label]["readiness_score"]
                for label in [
                    "matching_tidal_deformability_wilson_coefficients_2026",
                    "causality_constraints_gravitational_efts_2021",
                ]
            ),
        },
        {
            "route": "gw_dictionary_to_r4_waveform_adapter_requirements",
            "status": "design_route_not_packet_ready",
            "inputs": ["curvature_dependence_gw_tests_dictionary_2024"],
            "target_gate": "v2.160_r4_shape_likelihood_packet_manifest",
            "can_attack": ["waveform_model", "domain", "systematics"],
            "still_missing": [
                "numeric_r4_shape_likelihood",
                "maps_to_bresciani_r4_axes",
                "public_covariance_over_engine_r4_axes",
            ],
            "next_build_action": "translate_dictionary_terms_to_r4_shape_requirements",
            "aggregate_readiness_score": by_label[
                "curvature_dependence_gw_tests_dictionary_2024"
            ]["readiness_score"],
        },
    ]


def diagnose_r4_live_source_acquisition_queue() -> dict[str, Any]:
    adapter = diagnose_r4_shape_likelihood_ingestion_adapter()
    candidates = [
        _candidate_row(candidate)
        for candidate in current_r4_live_source_candidates()
    ]
    candidates.sort(key=lambda row: (-row["readiness_score"], row["label"]))
    build_routes = _composite_build_routes(candidates)
    build_routes.sort(
        key=lambda row: (-row["aggregate_readiness_score"], row["route"])
    )

    manifest_ready = [
        row["label"] for row in candidates if row["manifest_ready_now"]
    ]
    ingestion_ready = [
        row["label"] for row in candidates if row["ingestion_ready_now"]
    ]
    claim_ready = [row["label"] for row in candidates if row["claim_ready_now"]]
    failure_counts: dict[str, int] = {}
    for row in candidates:
        for missing in row["missing_packet_capabilities"]:
            failure_counts[missing] = failure_counts.get(missing, 0) + 1

    return canonicalize_json_floats({
        "version": VERSION,
        "scan_date": SCAN_DATE,
        "basis": [
            "v2.173_post_weyl_g8_contract_frontier",
            "v2.162_r4_shape_likelihood_ingestion_adapter",
            "v2.160_r4_shape_likelihood_packet_manifest",
            "live_primary_or_public_source_sweep_2026_06_20",
        ],
        "route": "future_public_r4_shape_likelihood_ingestion",
        "target_axes": list(TARGET_AXES),
        "adapter_route_status": adapter["route_status"],
        "ready_public_r4_likelihood_packets_now": (
            adapter["ready_public_r4_likelihood_packets_now"]
        ),
        "required_packet_fields": list(REQUIRED_PACKET_FIELDS),
        "acceptance_fields": list(LIKELIHOOD_ACCEPTANCE_FIELDS),
        "candidate_count": len(candidates),
        "manifest_ready_candidates": manifest_ready,
        "ingestion_ready_candidates": ingestion_ready,
        "claim_ready_candidates": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "source_urls_checked": [
            row["source_url"] for row in candidates
        ],
        "candidates_ranked": candidates,
        "composite_build_routes_ranked": build_routes,
        "selected_next_build_route": build_routes[0],
        "selected_next_build_action": build_routes[0]["next_build_action"],
        "failure_counts": dict(sorted(failure_counts.items())),
        "route_status": "r4_live_source_queue_ready_no_packet",
        "best_next_artifact": (
            "A Bresciani-axis dictionary plus public GW reanalysis fixture "
            "that can attempt a v2.160 R4 shape likelihood packet export. "
            "Until that export exists, the route stays diagnostic-only."
        ),
        "interpretation": (
            "The live source sweep found useful formalism, data, and adjacent "
            "higher-curvature analyses, but no current source supplies a "
            "public likelihood or covariance over the engine R4 shape axes. "
            "The next action is an adapter build, not a claim."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.174/"
            "r4_live_source_acquisition_queue.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_live_source_acquisition_queue()
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
