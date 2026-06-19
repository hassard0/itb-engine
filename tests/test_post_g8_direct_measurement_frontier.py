"""Tests for the v2.91 post-direct-g8-measurement frontier."""

from experiments.post_g8_direct_measurement_frontier import (
    diagnose_post_g8_direct_measurement_frontier,
    frontier_rows_after_g8_direct_measurement_decision,
)


def test_post_direct_g8_frontier_has_no_claim_ready_routes():
    result = diagnose_post_g8_direct_measurement_frontier()

    assert result["version"] == "v2.91"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_direct_g8_measurement_frontier_external_only_no_claim_ready"
    )


def test_no_current_in_repo_promotion_ready_routes_remain():
    result = diagnose_post_g8_direct_measurement_frontier()

    assert result["current_in_repo_promotion_ready_routes"] == []
    assert len(result["external_dependency_routes"]) == 6
    assert result["execution_class_counts"][
        "external_packet_required_before_in_repo_adapter"
    ] == 1


def test_future_public_g8_ingestion_is_top_priority_but_waits_for_packet():
    result = diagnose_post_g8_direct_measurement_frontier()

    assert result["top_priority_route"] == "future_public_g8_measurement_ingestion"
    row = next(
        row for row in result["rows"]
        if row["route"] == "future_public_g8_measurement_ingestion"
    )
    assert row["priority_rank"] == 1
    assert row["claim_ready"] is False
    assert row["current_in_repo_promotion_ready"] is False
    assert row["execution_class"] == "external_packet_required_before_in_repo_adapter"
    assert "future_public_g8_packet_missing" in row["blockers"]


def test_v2_90_direct_g8_retirements_are_carried_forward():
    result = diagnose_post_g8_direct_measurement_frontier()

    assert "direct_spin4_detector_measurement_in_repo_execution" in (
        result["direct_g8_retired_routes"]
    )
    assert "synthetic_g8_measurement_fixture_as_claim" in (
        result["direct_g8_retired_routes"]
    )


def test_retired_cmb_beta_is_not_counted_as_external_dependency():
    result = diagnose_post_g8_direct_measurement_frontier()
    row = next(
        row for row in frontier_rows_after_g8_direct_measurement_decision()
        if row["route"] == "cmb_beta_em_axion"
    )

    assert row["execution_class"] == "retired_non_gravity_discriminator"
    assert "cmb_beta_em_axion" not in result["external_dependency_routes"]
