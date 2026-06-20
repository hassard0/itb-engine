"""Tests for the v2.169 post-parity-bridge frontier."""

from experiments.post_parity_bridge_frontier import (
    diagnose_post_parity_bridge_frontier,
    frontier_rows_after_parity_bridge_spec,
)


def test_post_parity_bridge_frontier_has_no_claim_or_promotion_ready_route():
    result = diagnose_post_parity_bridge_frontier()

    assert result["version"] == "v2.169"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "post_parity_bridge_frontier_no_claim_route"


def test_parity_route_uses_operator_bridge_contract_and_remains_blocked():
    rows = {row["route"]: row for row in frontier_rows_after_parity_bridge_spec()}
    parity = rows["gw_parity_operator_normalization_search"]

    assert parity["priority_rank"] == 5
    assert parity["status"] == "operator_bridge_contract_ready_real_bridge_missing"
    assert parity["current_in_repo_diagnostic_ready"] is True
    assert parity["current_in_repo_promotion_ready"] is False
    assert parity["claim_ready"] is False
    assert "ready_current_operator_bridge_missing" in parity["blockers"]
    assert "source_backed_operator_normalization" in parity["blockers"]
    assert "engine_axis_target" in parity["blockers"]


def test_priority_order_matches_post_g8_external_frontier_with_parity_updated():
    result = diagnose_post_parity_bridge_frontier()

    assert result["priority_order"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"


def test_source_side_parity_likelihood_ready_but_no_operator_bridge():
    result = diagnose_post_parity_bridge_frontier()

    assert result["source_side_parity_likelihood_ready_routes"] == [
        "ng_gwtc3_kappa_at_100hz",
        "callister_sgwb_kappaD_kappaz",
    ]
    assert result["ready_current_operator_bridges"] == []
    assert "gw_parity_operator_normalization_search" in (
        result["external_dependency_routes"]
    )


def test_diagnostic_ready_routes_include_parity_bridge_contract():
    result = diagnose_post_parity_bridge_frontier()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["blocker_counts"]["ready_current_operator_bridge_missing"] == 1
