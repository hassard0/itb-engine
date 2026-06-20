"""Tests for the v2.173 post-Weyl/G8-contract frontier."""

from experiments.post_weyl_g8_contract_frontier import (
    diagnose_post_weyl_g8_contract_frontier,
    frontier_rows_after_weyl_g8_contract,
)


def test_post_weyl_g8_contract_frontier_has_no_claim_or_promotion_route():
    result = diagnose_post_weyl_g8_contract_frontier()

    assert result["version"] == "v2.173"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "post_weyl_g8_contract_frontier_no_claim_route"


def test_weyl_g8_route_uses_dual_likelihood_contract_and_remains_blocked():
    rows = {row["route"]: row for row in frontier_rows_after_weyl_g8_contract()}
    weyl = rows["weyl_g8_joint_frontier"]

    assert weyl["priority_rank"] == 4
    assert weyl["status"] == "dual_likelihood_contract_ready_real_packet_missing"
    assert weyl["current_in_repo_diagnostic_ready"] is True
    assert weyl["current_in_repo_promotion_ready"] is False
    assert weyl["claim_ready"] is False
    assert "ready_current_weyl_g8_packet_missing" in weyl["blockers"]
    assert "base_g8_gc_joint_gate_failed" in weyl["blockers"]
    assert "weyl_g8_extension_gate_failed" in weyl["blockers"]
    assert "engine_g_c_packet_missing" in weyl["blockers"]
    assert "joint_covariance_or_likelihood_missing" in weyl["blockers"]
    assert "v2.172_weyl_g8_dual_likelihood_contract" in weyl["basis"]


def test_priority_order_is_preserved_with_weyl_row_updated():
    result = diagnose_post_weyl_g8_contract_frontier()

    assert result["priority_order"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"


def test_weyl_g8_contract_accepts_synthetic_but_no_current_real_packet():
    result = diagnose_post_weyl_g8_contract_frontier()

    assert result["weyl_g8_contract_route_status"] == (
        "weyl_g8_dual_likelihood_contract_ready_no_real_packet"
    )
    assert result["weyl_g8_synthetic_control_status"] == (
        "weyl_g8_dual_likelihood_ready_nonclaiming"
    )
    assert result["ready_current_weyl_g8_packets"] == []
    assert "weyl_g8_joint_frontier" in result["external_dependency_routes"]


def test_all_frontier_routes_have_diagnostic_infrastructure_after_contract():
    result = diagnose_post_weyl_g8_contract_frontier()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["blocker_counts"]["ready_current_weyl_g8_packet_missing"] == 1
