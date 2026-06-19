"""Cross-route external evidence packet contract (v2.92)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_adapter_acceptance_harness import (
    REQUIRED_G8_ADAPTER_FIELDS,
    REQUIRED_SYSTEMATICS_COMPONENTS,
)
from experiments.post_g8_direct_measurement_frontier import (
    diagnose_post_g8_direct_measurement_frontier,
)


COMMON_PROVENANCE_FIELDS = (
    "source_url",
    "source_type",
    "source_version_or_release",
    "public_data_or_code_url",
    "license_or_access_terms",
    "citation",
)

COMMON_CLAIM_GATES = (
    "primary_or_release_source_present",
    "public_likelihood_or_covariance_present",
    "component_systematics_budget_closed",
    "engine_axis_mapping_source_backed",
    "registered_framework_domain_bounded",
    "framework_exclusion_math_present",
    "synthetic_fixture_false",
)


def _contract_row(
    *,
    route: str,
    family: str,
    external_object: str,
    minimum_required_fields: list[str],
    route_specific_rejection_tests: list[str],
    acceptance_gate: str,
    basis: list[str],
) -> dict[str, Any]:
    fields = sorted(set(COMMON_PROVENANCE_FIELDS).union(minimum_required_fields))
    rejection_tests = sorted(
        set(route_specific_rejection_tests).union(
            {
                "synthetic_fixture_not_real_source",
                "missing_public_likelihood_or_covariance",
                "missing_component_systematics_budget",
                "missing_framework_exclusion_math",
            }
        )
    )
    return {
        "route": route,
        "family": family,
        "external_object": external_object,
        "minimum_required_fields": fields,
        "field_count": len(fields),
        "common_claim_gates": list(COMMON_CLAIM_GATES),
        "route_specific_rejection_tests": rejection_tests,
        "acceptance_gate": acceptance_gate,
        "claim_ready_without_external_packet": False,
        "basis": basis,
    }


def external_evidence_contract_rows() -> list[dict[str, Any]]:
    return [
        _contract_row(
            route="future_public_g8_measurement_ingestion",
            family="matter_forward_amplitude",
            external_object="engine_normalized_g8_measurement_packet",
            minimum_required_fields=[
                *REQUIRED_G8_ADAPTER_FIELDS,
                "systematics_components",
                "analysis_code_or_likelihood_sampler",
                "low_energy_eft_validity_statement",
            ],
            route_specific_rejection_tests=[
                "axis_not_g8",
                "observable_basis_not_adapter_supported",
                "wilson_coefficient_normalization_not_engine_g8",
                "g8_not_isolated_from_lower_matter_moments",
                "systematics_components_not_closed",
            ],
            acceptance_gate="experiments.g8_adapter_acceptance_harness",
            basis=[
                "v2.79_g8_adapter_acceptance_harness",
                "v2.90_g8_direct_measurement_route_decision",
                "v2.91_post_g8_direct_measurement_frontier",
            ],
        ),
        _contract_row(
            route="external_spin4_detector_measurement_request",
            family="matter_forward_amplitude",
            external_object="spin4_detector_measurement_release",
            minimum_required_fields=[
                "spin_or_detector_basis",
                "measured_observable_definition",
                "central_value_or_bound",
                "statistical_uncertainty",
                "systematic_uncertainty",
                "covariance_or_likelihood",
                "eft_cutoff_or_energy_domain",
                "projection_to_engine_g8",
                "background_model",
                "calibration_model",
            ],
            route_specific_rejection_tests=[
                "measurement_not_in_spin4_or_detector_basis",
                "projection_to_engine_g8_missing",
                "external_experimental_release_missing",
                "eft_domain_unbounded",
            ],
            acceptance_gate="future_g8_external_measurement_adapter",
            basis=[
                "v2.54_g8_high_moment_measurement_specification",
                "v2.89_g8_direct_measurement_feasibility_audit",
                "v2.90_g8_direct_measurement_route_decision",
            ],
        ),
        _contract_row(
            route="future_source_backed_g8_operator_identity_search",
            family="matter_forward_amplitude",
            external_object="source_backed_g8_operator_identity",
            minimum_required_fields=[
                "operator_identity_statement",
                "source_jacobian_to_engine_g8",
                "uncertainty_propagation",
                "covariance_or_likelihood",
                "lower_moment_mixing_control",
                "normalization_convention",
                "low_energy_eft_domain",
            ],
            route_specific_rejection_tests=[
                "operator_identity_missing",
                "jacobian_to_engine_g8_missing",
                "lower_moment_mixing_uncontrolled",
                "normalization_not_source_declared",
            ],
            acceptance_gate="future_source_backed_g8_operator_adapter",
            basis=[
                "v2.86_g8_adapter_derivation_source_audit",
                "v2.87_g8_adapter_derivation_route_decision",
            ],
        ),
        _contract_row(
            route="framework_specific_native_tower_search",
            family="swampland_tower",
            external_object="registered_framework_native_tower_packet",
            minimum_required_fields=[
                "framework_id",
                "native_tower_spectrum",
                "asymptotic_regime",
                "field_distance_metric",
                "tower_mass_law",
                "normalization_to_engine_tower",
                "ownership_metadata",
                "uncertainty_model",
                "exclusion_interval",
                "tower_evidence_adapter_version",
            ],
            route_specific_rejection_tests=[
                "framework_id_not_registered",
                "native_tower_spectrum_missing",
                "asymptotic_regime_missing",
                "adapter_normalization_missing",
                "ownership_metadata_missing",
            ],
            acceptance_gate="experiments.native_adapter_acceptance_harness",
            basis=[
                "v2.47_native_adapter_acceptance_harness",
                "v2.83_native_tower_current_source_audit",
                "v2.84_native_tower_route_decision",
            ],
        ),
        _contract_row(
            route="gw_parity_operator_normalization_search",
            family="gravitational_wave_parity",
            external_object="ppv_to_engine_parity_operator_bridge",
            minimum_required_fields=[
                "source_native_likelihood",
                "source_backed_operator_normalization",
                "ppv_parameter_definition",
                "engine_axis_target",
                "sign_convention",
                "unit_conversion",
                "frequency_reference",
                "covariance_or_samples",
                "helicity_basis_harmonization",
                "framework_exclusion_projection",
            ],
            route_specific_rejection_tests=[
                "source_backed_operator_normalization_missing",
                "source_native_packet_not_engine_axis",
                "dimensionless_ppv_normalization_missing",
                "engine_axis_target_missing",
                "helicity_harmonization_missing",
            ],
            acceptance_gate="future_gw_parity_engine_projection_adapter",
            basis=[
                "v2.71_to_v2.76_gw_parity_ng_source_native_chain",
                "v2.76_gw_parity_route_decision",
            ],
        ),
        _contract_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            external_object="joint_engine_gC_g8_likelihood",
            minimum_required_fields=[
                "engine_gC_packet",
                "engine_g8_packet",
                "joint_covariance_or_likelihood",
                "shared_eft_domain",
                "cross_axis_correlation_model",
                "framework_projection_matrix",
                "joint_exclusion_statistic",
                "look_elsewhere_or_scan_policy",
            ],
            route_specific_rejection_tests=[
                "g_C_external_measurement_missing",
                "g8_external_measurement_missing",
                "joint_likelihood_missing",
                "shared_eft_domain_missing",
                "cross_axis_correlation_unbounded",
            ],
            acceptance_gate="future_weyl_g8_joint_likelihood_adapter",
            basis=[
                "v2.50_weyl_g8_discriminator_frontier",
                "v2.51_weyl_g8_observable_sourceability",
                "v2.91_post_g8_direct_measurement_frontier",
            ],
        ),
    ]


def diagnose_external_evidence_packet_contract() -> dict[str, Any]:
    rows = external_evidence_contract_rows()
    frontier = diagnose_post_g8_direct_measurement_frontier()
    required_field_counts = {
        row["route"]: row["field_count"]
        for row in rows
    }
    rejection_test_counts = {
        row["route"]: len(row["route_specific_rejection_tests"])
        for row in rows
    }
    claim_without_external = [
        row["route"]
        for row in rows
        if row["claim_ready_without_external_packet"]
    ]
    all_required_fields = sorted(
        {
            field
            for row in rows
            for field in row["minimum_required_fields"]
        }
    )

    return {
        "version": "v2.92",
        "basis": [
            "v2.91_post_g8_direct_measurement_frontier",
            "v2.79_g8_adapter_acceptance_harness",
            "v2.47_native_adapter_acceptance_harness",
            "v2.76_gw_parity_route_decision",
        ],
        "contract_scope": "cross_route_external_evidence_intake",
        "frontier_route_status": frontier["route_status"],
        "frontier_promotion_ready_routes": (
            frontier["current_in_repo_promotion_ready_routes"]
        ),
        "frontier_claim_ready_routes": frontier["claim_ready_routes"],
        "route_count": len(rows),
        "common_provenance_fields": list(COMMON_PROVENANCE_FIELDS),
        "common_claim_gates": list(COMMON_CLAIM_GATES),
        "systematics_components_required_for_g8": list(
            REQUIRED_SYSTEMATICS_COMPONENTS
        ),
        "required_field_counts": dict(sorted(required_field_counts.items())),
        "rejection_test_counts": dict(sorted(rejection_test_counts.items())),
        "all_required_fields": all_required_fields,
        "claim_ready_without_external_packet_routes": claim_without_external,
        "claimable_discriminator_now": bool(claim_without_external),
        "rows": rows,
        "route_status": "external_evidence_contract_ready_no_packet",
        "best_next_artifact": (
            "Obtain one real external packet satisfying a row in this contract, "
            "starting with engine-normalized g_8 measurement ingestion."
        ),
        "interpretation": (
            "The frontier is not claim-ready, but the missing external objects "
            "are now explicit. Future work should add data only by satisfying "
            "one of these packet contracts; synthetic or source-incomplete rows "
            "remain non-promoting."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.92/external_evidence_packet_contract.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_external_evidence_packet_contract()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
