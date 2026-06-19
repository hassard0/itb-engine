"""Tests for the v2.90 g_8 direct measurement route decision."""

from experiments.g8_direct_measurement_route_decision import (
    diagnose_g8_direct_measurement_route_decision,
    route_decision_rows,
)


def test_g8_direct_measurement_execution_is_retired_for_current_run():
    result = diagnose_g8_direct_measurement_route_decision()

    assert result["version"] == "v2.90"
    assert "direct_spin4_detector_measurement_in_repo_execution" in (
        result["retired_routes"]
    )
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "direct_g8_measurement_execution_retired_external_dependency"
    )


def test_synthetic_measurement_fixture_cannot_be_claim_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "synthetic_g8_measurement_fixture_as_claim"
    )

    assert row["retained"] is False
    assert row["status"] == "retired_as_invalid_claim_route"
    assert "synthetic_fixture_not_real_source" in row["blockers"]


def test_external_measurement_request_is_retained_dependency():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "external_spin4_detector_measurement_request"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert row["status"] == "retained_external_dependency"
    assert "external_experimental_program_required" in row["blockers"]


def test_future_public_g8_ingestion_waits_for_external_packet():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "future_public_g8_measurement_ingestion"
    )

    assert row["retained"] is True
    assert row["status"] == "retained_ingestion_route"
    assert "future_public_g8_packet_missing" in row["blockers"]
    assert "blocked_until_external_packet_exists" in row["blockers"]
