"""Tests for the v2.84 native tower route decision."""

from experiments.native_tower_route_decision import (
    diagnose_native_tower_route_decision,
    route_decision_rows,
)


def test_native_tower_route_decision_retires_direct_source_promotion():
    result = diagnose_native_tower_route_decision()

    assert result["version"] == "v2.84"
    assert "quintic_single_compactification_direct_string_tree_promotion" in (
        result["retired_routes"]
    )
    assert "string_positive_control_direct_exclusion" in result["retired_routes"]
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "direct_native_tower_source_promotion_retired_no_claim_ready_route"
    )


def test_quintic_direct_promotion_is_retired_for_scope():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "quintic_single_compactification_direct_string_tree_promotion"
    )

    assert row["retained"] is False
    assert row["status"] == "retired_for_generic_framework_claims"
    assert "finite_range_not_asymptotic" in row["blockers"]
    assert "single_compactification_not_generic_framework" in row["blockers"]


def test_registered_native_adapter_authoring_is_retained_required_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "registered_native_tower_adapter_authoring"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert row["status"] == "retained_required_before_any_native_tower_claim"
    assert "source_owned_tower_spectrum_missing" in row["blockers"]
    assert "framework_owned_endpoint_missing" in row["blockers"]


def test_horava_witten_to_horava_lifshitz_promotion_is_retired():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "horava_witten_to_horava_lifshitz_promotion"
    )

    assert row["retained"] is False
    assert row["status"] == "retired_wrong_registered_framework_target"
    assert "horava_witten_string_setup_not_horava_lifshitz_framework" in (
        row["blockers"]
    )
