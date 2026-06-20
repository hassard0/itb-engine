"""Tests for the v2.165 post-adapter frontier refresh."""

from experiments.post_adapter_frontier_refresh import (
    diagnose_post_adapter_frontier_refresh,
    frontier_rows_after_adapter_refresh,
)


def test_post_adapter_frontier_has_no_claim_or_promotion_ready_route():
    result = diagnose_post_adapter_frontier_refresh()

    assert result["version"] == "v2.165"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_adapter_frontier_infrastructure_ready_no_claim_route"
    )


def test_r4_ingestion_remains_top_priority_but_public_packet_blocked():
    result = diagnose_post_adapter_frontier_refresh()
    row = result["rows"][0]

    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"
    assert row["status"] == "ingestion_adapter_ready_public_packet_missing"
    assert row["current_in_repo_diagnostic_ready"] is True
    assert row["current_in_repo_promotion_ready"] is False
    assert row["claim_ready"] is False
    assert "ready_public_r4_likelihood_packet_missing" in row["blockers"]
    assert "manifest_packet_gate_failed" in row["blockers"]


def test_native_requirement_sheet_is_third_priority_infrastructure_route():
    rows = {row["route"]: row for row in frontier_rows_after_adapter_refresh()}
    native = rows["registered_native_tower_adapter_authoring"]

    assert native["priority_rank"] == 3
    assert native["current_in_repo_diagnostic_ready"] is True
    assert native["current_in_repo_promotion_ready"] is False
    assert native["claim_ready"] is False
    assert "adapter_authoring_ready_framework_missing" in native["blockers"]
    assert "registered_framework_exclusion_math" in native["blockers"]


def test_priority_order_carries_forward_g8_weyl_parity_and_r4_scale():
    result = diagnose_post_adapter_frontier_refresh()

    assert result["priority_order"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "future_public_g8_measurement_ingestion",
        "registered_native_tower_adapter_authoring",
        "weyl_g8_joint_frontier",
        "gw_parity_operator_normalization_search",
        "r4_symbolic_scale_resolution",
    ]
    assert "future_public_g8_measurement_ingestion" in (
        result["external_dependency_routes"]
    )
    assert "weyl_g8_joint_frontier" in result["external_dependency_routes"]


def test_diagnostic_ready_routes_are_infrastructure_not_claims():
    result = diagnose_post_adapter_frontier_refresh()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "registered_native_tower_adapter_authoring",
        "r4_symbolic_scale_resolution",
    ]
    assert result["blocker_counts"]["future_public_g8_packet_missing"] == 1
    assert result["blocker_counts"]["ready_public_r4_likelihood_packet_missing"] == 1
