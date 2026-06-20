"""Tests for the v2.135 symbolic string R4 projection plan."""

from experiments.symbolic_string_r4_to_bresciani_projection_plan import (
    bresciani_coordinate_solver,
    diagnose_symbolic_string_r4_to_bresciani_projection_plan,
    symbolic_projection_acceptance_tests,
    symbolic_projection_stages,
)


def test_coordinate_solver_contains_bresciani_inversion_formulas():
    solver = bresciani_coordinate_solver()
    inversion = solver["inversion_if_c_plus_and_c_minus_known"]

    assert inversion["g_R4_c1"] == "(c_plus + Re(c_minus)) / 2"
    assert inversion["g_R4_c2"] == "(c_plus - Re(c_minus)) / 2"
    assert inversion["g_R4_c3"] == "Im(c_minus)"
    assert solver["derived_coordinates"]["g_R4_minus_abs"] == (
        "sqrt((g_R4_c1 - g_R4_c2)^2 + g_R4_c3^2)"
    )


def test_projection_plan_has_ordered_source_to_guard_stages():
    stages = symbolic_projection_stages()
    names = [row["stage"] for row in stages]

    assert names == [
        "fix_source_family",
        "fix_four_dimensional_frame",
        "construct_string_tensor_basis",
        "evaluate_independent_helicity_amplitudes",
        "invert_to_bresciani_coordinates",
        "normalize_to_engine_axis",
        "package_guard_packet",
    ]


def test_acceptance_tests_require_guard_validation_and_nonclaiming_behavior():
    tests = {row["test"] for row in symbolic_projection_acceptance_tests()}

    assert "guard_packet_validation" in tests
    assert "nonclaiming_without_measurement" in tests
    assert "source_ownership" in tests


def test_diagnosis_is_nonclaiming_and_tracks_source_audit():
    result = diagnose_symbolic_string_r4_to_bresciani_projection_plan()

    assert result["version"] == "v2.135"
    assert result["source_audit_route_status"] == (
        "string_r4_sources_found_no_bresciani_projection_adapter"
    )
    assert result["claimable_framework_exclusions_now"] == []
    assert result["can_build_guard_passing_string_r4_adapter_now"] is False


def test_plan_blockers_keep_frame_helicity_and_normalization_explicit():
    result = diagnose_symbolic_string_r4_to_bresciani_projection_plan()

    assert "frame_choice_or_field_redefinition_ambiguity" in (
        result["current_projection_blockers"]
    )
    assert "helicity_projection_underconstrained" in (
        result["current_projection_blockers"]
    )
    assert "engine_lambda_r4_normalization_missing" in (
        result["current_projection_blockers"]
    )


def test_next_action_implements_symbolic_helicity_fixture():
    result = diagnose_symbolic_string_r4_to_bresciani_projection_plan()

    assert result["route_status"] == (
        "symbolic_string_r4_projection_plan_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "implement_symbolic_helicity_projection_fixture"
    )
