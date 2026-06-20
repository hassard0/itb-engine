"""Tests for the v2.148 policy-scoped string_tree_eft R4 packet."""

from copy import deepcopy

from experiments.gravity_r4_projection_guard_schema import evaluate_r4_projection_packet
from experiments.gravity_r4_source_provenance_guard import (
    evaluate_r4_source_provenance_packet,
)
from experiments.policy_scoped_string_tree_r4_projection_packet import (
    diagnose_policy_scoped_string_tree_r4_projection_packet,
    evaluate_policy_scoped_string_tree_r4_packet,
    policy_scoped_string_tree_r4_projection_packet,
)


def test_policy_scoped_packet_uses_v2147_shape_coefficients():
    packet = policy_scoped_string_tree_r4_projection_packet()

    assert packet["framework"] == "string_tree_eft"
    assert packet["coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert packet["derived"] == {
        "g_R4_plus": 1.0,
        "g_R4_minus_abs": 0.0,
    }
    assert packet["normalization"]["policy_id"] == "engine_r4_shape_unit_v1"
    assert (
        packet["normalization"]["absolute_string_alpha_prime_normalization_backed"]
        is False
    )
    assert packet["normalization"]["claim_use_allowed"] is False


def test_policy_scope_evaluation_is_internal_only():
    packet = policy_scoped_string_tree_r4_projection_packet()
    result = evaluate_policy_scoped_string_tree_r4_packet(packet)

    assert result["ready_for_policy_scoped_projection"] is True
    assert result["ready_for_absolute_normalized_projection"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["blockers"] == []
    assert result["remaining_absolute_normalization_gaps"] == [
        "absolute_type_II_string_alpha_prime_R4_coefficient",
        "engine_Lambda_R4_unit_conversion",
        "source_backed_K_Russo_to_Kallosh_shape_bridge",
    ]


def test_policy_scope_rejects_claim_or_absolute_toggles():
    packet = deepcopy(policy_scoped_string_tree_r4_projection_packet())
    packet["normalization"]["claim_use_allowed"] = True
    packet["normalization"]["k_convention_bridge_source_backed"] = True

    result = evaluate_policy_scoped_string_tree_r4_packet(packet)

    assert result["ready_for_policy_scoped_projection"] is False
    assert "claim_use_not_disabled" in result["blockers"]
    assert "k_convention_bridge_not_disabled" in result["blockers"]


def test_base_guard_accepts_projection_but_not_claim():
    packet = policy_scoped_string_tree_r4_projection_packet()
    result = evaluate_r4_projection_packet(packet)

    assert result["ready_for_framework_projection"] is True
    assert result["projection_blockers"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["claim_blockers"] == [
        "absolute_string_alpha_prime_normalization_missing",
        "claim_use_not_allowed",
        "discriminator_math_not_excluding",
        "engine_lambda_r4_unit_conversion_missing",
        "k_convention_bridge_missing",
        "measurement_likelihood_missing_or_incomplete",
        "policy_scoped_normalization_not_claimable",
    ]


def test_strict_source_guard_accepts_nonfixture_projection_but_not_claim():
    packet = policy_scoped_string_tree_r4_projection_packet()
    result = evaluate_r4_source_provenance_packet(packet)
    provenance = result["source_provenance_summary"]

    assert result["base_ready_for_framework_projection"] is True
    assert result["ready_for_source_backed_framework_projection"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["strict_projection_blockers"] == []
    assert result["strict_claim_blockers"] == [
        "absolute_string_alpha_prime_normalization_missing",
        "claim_use_not_allowed",
        "discriminator_math_not_excluding",
        "engine_lambda_r4_unit_conversion_missing",
        "k_convention_bridge_missing",
        "measurement_likelihood_missing_or_incomplete",
        "policy_scoped_normalization_not_claimable",
    ]
    assert provenance["truthy_synthetic_fixture_paths"] == []
    assert provenance["source_backed_derivation"] is True
    assert packet["source_url"] in provenance["primary_source_urls"]


def test_diagnosis_records_ready_policy_packet_and_no_exclusion():
    result = diagnose_policy_scoped_string_tree_r4_projection_packet()

    assert result["version"] == "v2.148"
    assert result["ready_for_policy_scoped_projection"] is True
    assert result["ready_for_absolute_normalized_projection"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "policy_scoped_string_tree_r4_projection_packet_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "register_policy_scoped_r4_adapter_without_claim_promotion"
    )
