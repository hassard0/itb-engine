"""Tests for the v2.101 alpha-bar to engine-axis Jacobian audit."""

from experiments.gw_alpha_engine_jacobian_audit import (
    diagnose_gw_alpha_engine_jacobian_audit,
    evaluate_alpha_to_engine_axis_mapping,
)


def test_diagnosis_rejects_existing_secondary_axes_and_selects_cubic_adapter():
    result = diagnose_gw_alpha_engine_jacobian_audit()

    assert result["version"] == "v2.101"
    assert result["claimable_discriminator_now"] is False
    assert result["direct_existing_secondary_axis_jacobian_ready"] is False
    assert result["route_status"] == (
        "alpha_to_existing_secondary_axes_rejected_"
        "cubic_axis_extension_selected"
    )
    assert result["selected_next_build_action"] == (
        "register_source_native_cubic_gw_axis_adapter"
    )


def test_source_parameter_summary_preserves_numeric_alpha_constraints():
    result = diagnose_gw_alpha_engine_jacobian_audit()
    summary = result["source_parameter_summary"]

    assert summary["all_source_parameters_numeric"] is True
    assert summary["parameters_with_numeric_constraints"] == [
        "alpha_bar_1",
        "alpha_bar_2",
    ]
    assert summary["intervals"]["alpha_bar_1"]["central"] == 0.87
    assert summary["intervals"]["alpha_bar_2"]["central"] == -0.35


def test_g_c_direct_mapping_is_rejected_as_quadratic_axis_mismatch():
    result = evaluate_alpha_to_engine_axis_mapping("g_C")

    assert result["decision"] == "reject_direct_jacobian_to_existing_secondary_axis"
    assert result["promotion_ready"] is False
    assert result["direct_existing_secondary_axis"] is True
    assert "curvature_order_mismatch" in result["failed_criteria"]
    assert "operator_family_mismatch" in result["failed_criteria"]
    assert "source_backed_normalization" in result["failed_criteria"]


def test_g_r2_direct_mapping_is_rejected_as_quadratic_axis_mismatch():
    result = evaluate_alpha_to_engine_axis_mapping("g_R2")

    assert result["decision"] == "reject_direct_jacobian_to_existing_secondary_axis"
    assert result["target_axis_definition"]["curvature_order"] == 2
    assert "curvature_order_mismatch" in result["failed_criteria"]
    assert "operator_family_mismatch" in result["failed_criteria"]
    assert result["next_action"] == "do_not_force_alpha_bar_into_quadratic_axis"


def test_g_r3_is_only_a_nonpromoting_source_native_extension_candidate():
    result = evaluate_alpha_to_engine_axis_mapping("g_R3")

    assert result["decision"] == "axis_extension_candidate_nonpromoting"
    assert "curvature_order_match" in result["passed_criteria"]
    assert "operator_family_match" in result["passed_criteria"]
    assert "source_native_axis_not_registered_for_v2_98_gate" in result[
        "failed_criteria"
    ]
    assert result["promotion_ready"] is False


def test_required_promotion_criteria_prevent_claim_ready_shortcuts():
    result = diagnose_gw_alpha_engine_jacobian_audit()

    assert "source_backed_normalization" in result["required_promotion_criteria"]
    assert "covariance_or_likelihood_export_available" in result[
        "required_promotion_criteria"
    ]
    assert result["claim_ready_mappings"] == []
    for row in result["mapping_attempts"]:
        assert row["promotion_ready"] is False
