"""Tests for the v2.88 post-g8-derivation frontier."""

from experiments.post_g8_derivation_route_decision_frontier import (
    diagnose_post_g8_derivation_route_decision_frontier,
    frontier_rows_after_g8_derivation_decision,
)


def test_post_g8_derivation_frontier_has_no_claim_ready_routes():
    result = diagnose_post_g8_derivation_route_decision_frontier()

    assert result["version"] == "v2.88"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_g8_derivation_frontier_no_claim_ready_new_measurement_next"
    )


def test_new_spin4_detector_measurement_is_top_priority():
    result = diagnose_post_g8_derivation_route_decision_frontier()

    assert result["top_priority_route"] == "new_spin4_or_detector_g8_measurement"
    assert result["priority_order"][0] == "new_spin4_or_detector_g8_measurement"
    row = next(
        row for row in result["rows"]
        if row["route"] == "new_spin4_or_detector_g8_measurement"
    )
    assert row["priority_rank"] == 1
    assert "external_numeric_g8_measurement_missing" in row["blockers"]


def test_future_operator_identity_search_is_second_not_claim_ready():
    row = next(
        row for row in frontier_rows_after_g8_derivation_decision()
        if row["route"] == "future_source_backed_g8_operator_identity_search"
    )

    assert row["priority_rank"] == 2
    assert row["claim_ready"] is False
    assert "future_source_operator_identity_missing" in row["blockers"]


def test_g8_derivation_retired_routes_are_carried_forward():
    result = diagnose_post_g8_derivation_route_decision_frontier()

    assert "current_detector_formalism_direct_g8_adapter" in (
        result["g8_derivation_retired_routes"]
    )
    assert "public_energy_correlator_data_without_operator_identity" in (
        result["g8_derivation_retired_routes"]
    )
