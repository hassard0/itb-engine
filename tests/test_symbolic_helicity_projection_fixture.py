"""Tests for the v2.136 symbolic helicity projection fixture."""

from experiments.symbolic_helicity_projection_fixture import (
    build_projection_packet,
    derived_bresciani_coordinates,
    diagnose_symbolic_helicity_projection_fixture,
    fixture_source_helicity_input,
    invert_bresciani_coordinates,
    positivity_summary,
)


def test_fixture_inverts_c_plus_c_minus_to_bresciani_axes():
    coefficients = invert_bresciani_coordinates(fixture_source_helicity_input())

    assert coefficients == {
        "g_R4_c1": 0.2,
        "g_R4_c2": 0.09999999999999999,
        "g_R4_c3": 0.05,
    }


def test_derived_coordinates_match_bresciani_contract():
    coefficients = invert_bresciani_coordinates(fixture_source_helicity_input())
    derived = derived_bresciani_coordinates(coefficients)

    assert derived["g_R4_plus"] == 0.3
    assert round(derived["g_R4_minus_abs"], 12) == round((0.1**2 + 0.05**2) ** 0.5, 12)


def test_fixture_positivity_passes():
    coefficients = invert_bresciani_coordinates(fixture_source_helicity_input())
    result = positivity_summary(coefficients)

    assert result["passed"] is True
    assert result["c3_square_bound_residual"] > 0.0


def test_projection_packet_is_guard_ready_but_not_claim_ready():
    result = diagnose_symbolic_helicity_projection_fixture()

    assert result["version"] == "v2.136"
    assert result["fixture_is_source_backed_string_derivation"] is False
    assert result["ready_for_framework_projection_fixture"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["guard_result"]["projection_blockers"] == []
    assert result["guard_result"]["claim_blockers"] == [
        "discriminator_math_not_excluding",
        "measurement_likelihood_missing_or_incomplete",
    ]


def test_projection_packet_contains_required_guard_fields():
    packet = build_projection_packet(fixture_source_helicity_input())

    for field in [
        "framework",
        "axis_family",
        "source_url",
        "coefficients",
        "derived",
        "operator_projection_matrix",
        "valid_energy_domain",
        "uncertainty_or_covariance",
        "ownership_metadata",
        "unitarity_bound",
    ]:
        assert field in packet


def test_next_action_replaces_fixture_with_source_backed_helicity_evaluation():
    result = diagnose_symbolic_helicity_projection_fixture()

    assert result["route_status"] == (
        "symbolic_helicity_fixture_passes_projection_guard_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "replace_fixture_with_source_backed_string_r4_helicity_evaluation"
    )
