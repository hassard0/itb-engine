"""Tests for discriminator frontier after GW parity route retirement."""

from experiments.post_gw_retirement_frontier import (
    diagnose_post_gw_retirement_frontier,
    frontier_rows_after_gw_retirement,
)


def test_post_gw_frontier_has_no_claim_ready_routes():
    result = diagnose_post_gw_retirement_frontier()

    assert result["version"] == "v2.77"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "post_gw_frontier_no_claim_ready_route_g8_next"


def test_g8_high_moment_is_top_priority_after_gw_retirement():
    result = diagnose_post_gw_retirement_frontier()

    assert result["top_priority_route"] == "g8_high_moment_measurement"
    assert result["priority_order"][0] == "g8_high_moment_measurement"
    row = next(
        row for row in result["rows"]
        if row["route"] == "g8_high_moment_measurement"
    )
    assert row["priority_rank"] == 1
    assert "missing_engine_normalized_g8_likelihood" in row["blockers"]


def test_gw_parity_route_is_retained_but_nonpromoting():
    row = next(
        row for row in frontier_rows_after_gw_retirement()
        if row["route"] == "gw_parity_source_native_archive"
    )

    assert row["claim_ready"] is False
    assert row["status"] == "retained_nonpromoting_direct_engine_route_retired"
    assert "direct_ng_ppv_engine_promotion_retired" in row["blockers"]


def test_cmb_beta_stays_retired_as_direct_gravity_discriminator():
    row = next(
        row for row in frontier_rows_after_gw_retirement()
        if row["route"] == "cmb_beta_em_axion"
    )

    assert row["claim_ready"] is False
    assert row["status"] == "retired_as_direct_gravity_discriminator"
    assert "not_engine_gravity_parity_axis" in row["blockers"]
