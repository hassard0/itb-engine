"""Tests for the v2.87 g_8 adapter derivation route decision."""

from experiments.g8_adapter_derivation_route_decision import (
    diagnose_g8_adapter_derivation_route_decision,
    route_decision_rows,
)


def test_g8_adapter_derivation_route_decision_retires_current_sources():
    result = diagnose_g8_adapter_derivation_route_decision()

    assert result["version"] == "v2.87"
    assert "current_detector_formalism_direct_g8_adapter" in result["retired_routes"]
    assert "current_wilson_formalism_direct_detector_adapter" in (
        result["retired_routes"]
    )
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "current_g8_adapter_derivation_retired_no_claim_ready_route"
    )


def test_detector_formalism_direct_adapter_is_retired_for_missing_identity():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "current_detector_formalism_direct_g8_adapter"
    )

    assert row["retained"] is False
    assert row["status"] == "retired_for_current_sources"
    assert "source_backed_operator_identity_to_engine_g8_missing" in row["blockers"]
    assert "public_g8_jacobian_or_projection_missing" in row["blockers"]


def test_future_operator_identity_search_is_retained_only_as_future_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "new_source_backed_g8_operator_identity_search"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert row["status"] == "retained_as_future_source_search"
    assert "future_source_operator_identity_missing" in row["blockers"]


def test_new_spin4_detector_measurement_remains_clean_retained_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "new_spin4_or_detector_g8_measurement"
    )

    assert row["retained"] is True
    assert row["status"] == "retained_as_cleanest_measurement_route"
    assert "external_numeric_g8_measurement_missing" in row["blockers"]
