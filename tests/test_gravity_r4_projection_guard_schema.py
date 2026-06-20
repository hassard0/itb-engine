"""Tests for the v2.133 gravity R4 projection guard/schema."""

import math

from experiments.gravity_r4_projection_guard_schema import (
    REQUIRED_R4_PROJECTION_FIELDS,
    diagnose_gravity_r4_projection_guard_schema,
    evaluate_r4_projection_packet,
)


def _complete_packet(discriminator_math="projection_only"):
    c1 = 0.2
    c2 = 0.1
    c3 = 0.05
    return {
        "framework": "string_tree_eft",
        "axis_family": "gravity_R4_Riemann4",
        "source_url": "https://arxiv.org/abs/2504.12855",
        "source_type": "computed_framework_projection",
        "source_version": "unit-test-source-version",
        "adapter_kind": "framework_native_r4_projection",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "coefficients": {
            "g_R4_c1": c1,
            "g_R4_c2": c2,
            "g_R4_c3": c3,
        },
        "derived": {
            "g_R4_plus": c1 + c2,
            "g_R4_minus_abs": math.hypot(c1 - c2, c3),
        },
        "normalization": {
            "status": "engine_lambda_r4_defined",
            "lambda_r4": 1.0,
        },
        "operator_projection_matrix": {
            "status": "source_backed",
            "basis": "Bresciani c_i spin-2 Riemann4",
        },
        "valid_energy_domain": {
            "status": "bounded_for_qg_eft",
            "s_max_over_lambda_r4": 0.2,
        },
        "uncertainty_or_covariance": {
            "status": "public_covariance_matrix",
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
        },
        "ownership_metadata": {
            "framework_owned_derivation": "unit-test owned derivation",
        },
        "unitarity_bound": {
            "status": "source_backed",
            "uses_bresciani_spin2_bound": True,
        },
        "positivity_status": "checked",
        "measurement_likelihood": {
            "status": "public_covariance_matrix",
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
        },
        "discriminator_math": discriminator_math,
    }


def test_required_packet_fields_include_source_projection_and_claim_inputs():
    assert "framework" in REQUIRED_R4_PROJECTION_FIELDS
    assert "coefficients" in REQUIRED_R4_PROJECTION_FIELDS
    assert "operator_projection_matrix" in REQUIRED_R4_PROJECTION_FIELDS
    assert "uncertainty_or_covariance" in REQUIRED_R4_PROJECTION_FIELDS
    assert "discriminator_math" in REQUIRED_R4_PROJECTION_FIELDS


def test_complete_projection_packet_passes_projection_but_not_claim_by_default():
    result = evaluate_r4_projection_packet(_complete_packet())

    assert result["ready_for_framework_projection"] is True
    assert result["projection_blockers"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["claim_blockers"] == ["discriminator_math_not_excluding"]


def test_complete_excluding_packet_can_pass_full_claim_guard():
    result = evaluate_r4_projection_packet(
        _complete_packet(discriminator_math="excludes_registered_framework")
    )

    assert result["ready_for_framework_projection"] is True
    assert result["ready_for_framework_claim"] is True
    assert result["claim_blockers"] == []


def test_guard_rejects_missing_current_framework_packet_fields():
    result = diagnose_gravity_r4_projection_guard_schema()

    assert result["version"] == "v2.133"
    assert result["registered_framework_count"] == 13
    assert result["ready_framework_projection_packets"] == []
    assert result["claim_ready_framework_packets"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["projection_blocker_counts"]["missing_required_fields"] == 13
    assert result["projection_blocker_counts"][
        "r4_coefficients_missing_or_nonnumeric"
    ] == 13


def test_guard_rejects_positivity_violation():
    packet = _complete_packet()
    packet["coefficients"]["g_R4_c3"] = 3.0
    packet["derived"]["g_R4_minus_abs"] = math.hypot(
        packet["coefficients"]["g_R4_c1"] - packet["coefficients"]["g_R4_c2"],
        packet["coefficients"]["g_R4_c3"],
    )
    result = evaluate_r4_projection_packet(packet)

    assert result["ready_for_framework_projection"] is False
    assert "r4_source_positivity_failed" in result["projection_blockers"]


def test_guard_rejects_inconsistent_derived_coordinates():
    packet = _complete_packet()
    packet["derived"]["g_R4_plus"] = 999.0
    result = evaluate_r4_projection_packet(packet)

    assert result["ready_for_framework_projection"] is False
    assert "r4_derived_coordinates_inconsistent" in (
        result["projection_blockers"]
    )


def test_guard_next_action_targets_string_r4_translation_search():
    result = diagnose_gravity_r4_projection_guard_schema()

    assert result["route_status"] == (
        "r4_projection_guard_schema_ready_no_current_adapter"
    )
    assert result["selected_next_build_action"] == (
        "search_string_r4_basis_translation_source"
    )
