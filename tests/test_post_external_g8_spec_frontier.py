"""Tests for the v2.167 post-external-G8-spec frontier."""

from experiments.post_external_g8_spec_frontier import (
    diagnose_post_external_g8_spec_frontier,
    frontier_rows_after_external_g8_spec,
)


def test_post_external_g8_frontier_has_no_claim_or_promotion_ready_routes():
    result = diagnose_post_external_g8_spec_frontier()

    assert result["version"] == "v2.167"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "post_external_g8_spec_frontier_no_claim_route"


def test_g8_route_uses_external_packet_contract_and_remains_blocked():
    rows = {row["route"]: row for row in frontier_rows_after_external_g8_spec()}
    g8 = rows["external_spin4_or_detector_g8_measurement_packet_spec"]

    assert g8["priority_rank"] == 2
    assert g8["status"] == "packet_contract_ready_real_external_g8_packet_missing"
    assert g8["current_in_repo_diagnostic_ready"] is True
    assert g8["current_in_repo_promotion_ready"] is False
    assert g8["claim_ready"] is False
    assert "ready_current_external_g8_packet_missing" in g8["blockers"]
    assert "base_g8_adapter_gate_failed" in g8["blockers"]
    assert "alpha_join_extension_gate_failed" in g8["blockers"]


def test_priority_order_retains_r4_first_and_native_third():
    result = diagnose_post_external_g8_spec_frontier()

    assert result["priority_order"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"


def test_alpha_ready_but_no_current_external_g8_packets():
    result = diagnose_post_external_g8_spec_frontier()

    assert result["alpha_packet_ready_for_g8_join"] is True
    assert result["ready_current_external_g8_packets"] == []
    assert "external_spin4_or_detector_g8_measurement_packet_spec" in (
        result["external_dependency_routes"]
    )


def test_diagnostic_ready_routes_include_new_g8_contract():
    result = diagnose_post_external_g8_spec_frontier()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "external_spin4_or_detector_g8_measurement_packet_spec",
        "registered_native_tower_adapter_authoring",
        "r4_symbolic_scale_resolution",
    ]
    assert result["blocker_counts"]["ready_current_external_g8_packet_missing"] == 1
