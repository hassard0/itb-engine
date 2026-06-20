"""Tests for the v2.171 post-R4-scale-contract frontier."""

from experiments.post_r4_scale_contract_frontier import (
    diagnose_post_r4_scale_contract_frontier,
    frontier_rows_after_r4_scale_contract,
)


def test_post_r4_scale_contract_frontier_has_no_claim_or_promotion_route():
    result = diagnose_post_r4_scale_contract_frontier()

    assert result["version"] == "v2.171"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "post_r4_scale_contract_frontier_no_claim_route"


def test_r4_scale_route_uses_contract_and_remains_real_policy_blocked():
    rows = {row["route"]: row for row in frontier_rows_after_r4_scale_contract()}
    r4_scale = rows["r4_symbolic_scale_resolution"]

    assert r4_scale["priority_rank"] == 6
    assert r4_scale["status"] == "numeric_scale_contract_ready_real_policy_missing"
    assert r4_scale["current_in_repo_diagnostic_ready"] is True
    assert r4_scale["current_in_repo_promotion_ready"] is False
    assert r4_scale["claim_ready"] is False
    assert "ready_current_numeric_scale_policy_missing" in r4_scale["blockers"]
    assert "alpha_prime_to_engine_lambda_r4_missing" in r4_scale["blockers"]
    assert "engine_lambda_r4_numeric_value_missing" in r4_scale["blockers"]
    assert "v2.170_r4_symbolic_scale_resolution_contract" in r4_scale["basis"]


def test_priority_order_stays_global_frontier_order_with_scale_updated():
    result = diagnose_post_r4_scale_contract_frontier()

    assert result["priority_order"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"


def test_r4_scale_contract_accepts_synthetic_but_no_current_real_policy():
    result = diagnose_post_r4_scale_contract_frontier()

    assert result["r4_scale_contract_route_status"] == (
        "r4_scale_resolution_contract_ready_no_numeric_policy"
    )
    assert result["r4_scale_synthetic_control_status"] == (
        "r4_numeric_scale_policy_ready_nonclaiming"
    )
    assert result["ready_current_numeric_scale_policies"] == []
    assert "r4_symbolic_scale_resolution" in result["external_dependency_routes"]


def test_diagnostic_ready_routes_include_r4_scale_contract():
    result = diagnose_post_r4_scale_contract_frontier()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["blocker_counts"]["ready_current_numeric_scale_policy_missing"] == 1
