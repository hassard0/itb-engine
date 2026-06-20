"""Tests for the v2.131 gravity R4 axis-extension candidate registry."""

from experiments.gravity_r4_axis_extension_candidate import (
    candidate_axis_contract,
    candidate_equations,
    diagnose_gravity_r4_axis_extension_candidate,
)


def test_candidate_registers_three_source_coefficients_and_derived_axes():
    contract = candidate_axis_contract()
    axes = {row["axis"] for row in contract["proposed_engine_axes"]}
    derived = {row["axis"] for row in contract["derived_source_coordinates"]}

    assert contract["candidate_family"] == "gravity_R4_Riemann4"
    assert axes == {"g_R4_c1", "g_R4_c2", "g_R4_c3"}
    assert derived == {"g_R4_plus", "g_R4_minus_abs"}


def test_candidate_equations_preserve_bresciani_source_bounds():
    equations = candidate_equations()

    assert equations["source_unitarity_bound"]["spin2_ratio"] == 1.4
    assert "c_1^(S) >= 0" in equations["source_positivity_bounds"]
    assert any(
        row["name"] == "r4_source_positivity_template"
        for row in equations["engine_candidate_bound_templates"]
    )


def test_r4_candidate_is_registered_but_not_axis_contract_ready():
    result = diagnose_gravity_r4_axis_extension_candidate()

    assert result["version"] == "v2.131"
    assert result["candidate_registered"] is True
    assert result["axis_contract_ready"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "gravity_r4_axis_candidate_registered_nonclaiming"
    )


def test_r4_candidate_has_promotion_blockers():
    result = diagnose_gravity_r4_axis_extension_candidate()

    assert "r4_dimensionless_engine_normalization_missing" in (
        result["promotion_blockers"]
    )
    assert "registered_framework_r4_projection_missing" in (
        result["promotion_blockers"]
    )
    assert "r4_measurement_likelihood_missing" in result["promotion_blockers"]
    assert "r4_engine_constraint_integration_missing" in (
        result["promotion_blockers"]
    )


def test_next_action_targets_framework_projection_requirements():
    result = diagnose_gravity_r4_axis_extension_candidate()

    assert result["selected_next_build_action"] == (
        "derive_framework_r4_projection_requirements"
    )
    assert result["passed_checks"] == [
        "source_backed_operator_basis",
        "source_backed_unitarity_bound",
        "source_backed_positivity_bounds",
    ]
