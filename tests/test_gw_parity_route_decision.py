"""Tests for GW parity route decision after engine-axis audit."""

from experiments.gw_parity_route_decision import (
    diagnose_gw_parity_route_decision,
    route_decision_rows,
)


def test_route_decision_retires_direct_ng_engine_promotion():
    result = diagnose_gw_parity_route_decision()

    assert result["version"] == "v2.76"
    assert "ng_ppv_beta10_direct_engine_promotion" in result["retired_routes"]
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert (
        result["route_status"]
        == "direct_ng_ppv_engine_promotion_retired_no_claim_ready_route"
    )


def test_source_native_ng_packet_is_retained_nonpromoting():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "ng_source_native_likelihood_archive"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert row["status"] == "retained_as_nonpromoting_measurement_packet"
    assert "source_native_packet_not_engine_axis" in row["blockers"]


def test_callister_route_stays_separate_from_ng_beta10():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "callister_alpha_beta_split_route"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert "two_axis_alpha1_beta1_not_single_beta10" in row["blockers"]


def test_operator_normalization_search_remains_required():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "external_operator_normalization_search"
    )

    assert row["status"] == "required_before_any_gw_parity_claim"
    assert "operator_identity_not_source_backed_in_engine_basis" in row["blockers"]
    assert "dimensionful_to_dimensionless_normalization_missing" in row["blockers"]
