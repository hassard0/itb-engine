"""Tests for the v2.85 post-native-tower route-decision frontier."""

from experiments.post_native_tower_route_decision_frontier import (
    diagnose_post_native_tower_route_decision_frontier,
    frontier_rows_after_native_tower_decision,
)


def test_post_native_frontier_has_no_claim_ready_routes():
    result = diagnose_post_native_tower_route_decision_frontier()

    assert result["version"] == "v2.85"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_native_frontier_no_claim_ready_route_g8_adapter_next"
    )


def test_source_backed_g8_adapter_is_top_priority_after_native_retirement():
    result = diagnose_post_native_tower_route_decision_frontier()

    assert result["top_priority_route"] == "source_backed_g8_adapter_derivation"
    assert result["priority_order"][0] == "source_backed_g8_adapter_derivation"
    row = next(
        row for row in result["rows"]
        if row["route"] == "source_backed_g8_adapter_derivation"
    )
    assert row["priority_rank"] == 1
    assert "source_backed_jacobian_to_engine_g8_missing" in row["blockers"]


def test_framework_specific_native_search_is_retained_but_second():
    row = next(
        row for row in frontier_rows_after_native_tower_decision()
        if row["route"] == "framework_specific_native_tower_search"
    )

    assert row["priority_rank"] == 2
    assert row["status"] == "retained_search_route_no_current_adapter"
    assert "named_framework_native_source_missing" in row["blockers"]


def test_native_retired_routes_are_carried_forward():
    result = diagnose_post_native_tower_route_decision_frontier()

    assert "quintic_single_compactification_direct_string_tree_promotion" in (
        result["native_retired_direct_routes"]
    )
    assert "asymptotic_safety_swampland_comparison_direct_tower" in (
        result["native_retired_direct_routes"]
    )
