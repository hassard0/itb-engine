"""Tests for the v2.82 post-g8 route-decision frontier."""

from experiments.post_g8_route_decision_frontier import (
    diagnose_post_g8_route_decision_frontier,
    frontier_rows_after_g8_route_decision,
)


def test_post_g8_frontier_has_no_claim_ready_routes():
    result = diagnose_post_g8_route_decision_frontier()

    assert result["version"] == "v2.82"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_g8_frontier_no_claim_ready_route_native_tower_next"
    )


def test_native_tower_is_top_priority_after_direct_g8_retirement():
    result = diagnose_post_g8_route_decision_frontier()

    assert result["top_priority_route"] == "native_tower_evidence"
    assert result["priority_order"][0] == "native_tower_evidence"
    row = next(row for row in result["rows"] if row["route"] == "native_tower_evidence")
    assert row["priority_rank"] == 1
    assert "native_framework_tower_spectrum_missing" in row["blockers"]


def test_source_backed_g8_adapter_remains_second_not_retired():
    row = next(
        row for row in frontier_rows_after_g8_route_decision()
        if row["route"] == "source_backed_g8_adapter_derivation"
    )

    assert row["priority_rank"] == 2
    assert row["status"] == "retained_required_not_currently_claimable"
    assert "source_backed_jacobian_to_engine_g8_missing" in row["blockers"]


def test_direct_g8_public_data_routes_are_recorded_retired():
    result = diagnose_post_g8_route_decision_frontier()

    assert "cms_energy_correlator_direct_g8_promotion" in (
        result["g8_retired_direct_routes"]
    )
    assert "heavy_ion_eec_direct_g8_promotion" in result["g8_retired_direct_routes"]


def test_cmb_beta_remains_low_priority_retired_route():
    row = next(
        row for row in frontier_rows_after_g8_route_decision()
        if row["route"] == "cmb_beta_em_axion"
    )

    assert row["priority_rank"] == 6
    assert row["status"] == "retired_as_direct_gravity_discriminator"
    assert "not_engine_gravity_parity_axis" in row["blockers"]
