"""Tests for the v2.147 R4 shape normalization policy."""

from copy import deepcopy

from experiments.r4_shape_normalization_policy import (
    ALLOWED_POLICY_USES,
    DISALLOWED_POLICY_USES,
    diagnose_r4_shape_normalization_policy,
    engine_r4_shape_normalization_policy,
    evaluate_r4_shape_normalization_policy,
)


def test_policy_defines_nonclaiming_engine_shape_unit():
    policy = engine_r4_shape_normalization_policy()

    assert policy["status"] == "engine_convention_nonclaiming"
    assert policy["normalized_shape_source"]["source_backed_shape"] is True
    assert policy["normalized_shape_source"]["K_plus"] == 1.0
    assert policy["normalized_shape_source"]["K_minus_real"] == 0.0
    assert policy["normalized_shape_source"]["K_minus_imag"] == 0.0
    assert policy["engine_unit_definition"]["overall_R4_factor"] == 8.0
    assert policy["engine_unit_definition"]["g_R4_c1"] == 0.5
    assert policy["engine_unit_definition"]["g_R4_c2"] == 0.5
    assert policy["engine_unit_definition"]["g_R4_c3"] == 0.0
    assert policy["framework_claim_allowed"] is False
    assert policy["measurement_claim_allowed"] is False


def test_policy_keeps_internal_uses_separate_from_claim_uses():
    policy = engine_r4_shape_normalization_policy()

    assert set(ALLOWED_POLICY_USES).issubset(policy["allowed_uses"])
    assert set(DISALLOWED_POLICY_USES).issubset(policy["disallowed_uses"])
    assert "internal_bresciani_basis_projection" in policy["allowed_uses"]
    assert "framework_exclusion_claim" in policy["disallowed_uses"]
    assert "measurement_likelihood_claim" in policy["disallowed_uses"]


def test_evaluation_allows_internal_shape_policy_only():
    policy = engine_r4_shape_normalization_policy()
    result = evaluate_r4_shape_normalization_policy(policy)

    assert result["ready_for_internal_shape_normalization"] is True
    assert result["ready_for_absolute_string_normalization"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["blockers"] == []
    assert result["warnings"] == []


def test_evaluation_blocks_if_claim_toggles_are_enabled():
    policy = deepcopy(engine_r4_shape_normalization_policy())
    policy["framework_claim_allowed"] = True
    policy["measurement_claim_allowed"] = True

    result = evaluate_r4_shape_normalization_policy(policy)

    assert result["ready_for_internal_shape_normalization"] is False
    assert "framework_claim_not_disabled" in result["blockers"]
    assert "measurement_claim_not_disabled" in result["blockers"]
    assert result["ready_for_framework_claim"] is False


def test_evaluation_warns_without_promoting_absolute_string_claims():
    policy = deepcopy(engine_r4_shape_normalization_policy())
    policy["absolute_normalization"][
        "type_II_string_alpha_prime_units_source_backed"
    ] = True
    policy["absolute_normalization"][
        "engine_lambda_r4_unit_conversion_source_backed"
    ] = True
    policy["absolute_normalization"]["k_convention_bridge_source_backed"] = True

    result = evaluate_r4_shape_normalization_policy(policy)

    assert result["ready_for_internal_shape_normalization"] is True
    assert result["ready_for_absolute_string_normalization"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["warnings"] == [
        "policy_would_enable_absolute_string_claim",
        "policy_would_enable_engine_lambda_conversion_claim",
        "policy_would_enable_k_bridge_claim",
    ]


def test_diagnosis_records_nonclaiming_policy_and_next_packet():
    result = diagnose_r4_shape_normalization_policy()

    assert result["version"] == "v2.147"
    assert result["ready_internal_shape_policy"] is True
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == "engine_r4_shape_unit_policy_ready_nonclaiming"
    assert result["selected_next_build_action"] == (
        "build_policy_scoped_string_tree_r4_projection_packet"
    )
    assert result["evaluation"]["ready_for_framework_claim"] is False
