"""Tests for the v2.81 g_8 route decision."""

from experiments.g8_route_decision import (
    diagnose_g8_route_decision,
    route_decision_rows,
)


def test_g8_route_decision_retires_direct_public_data_promotion():
    result = diagnose_g8_route_decision()

    assert result["version"] == "v2.81"
    assert "cms_energy_correlator_direct_g8_promotion" in result["retired_routes"]
    assert "heavy_ion_eec_direct_g8_promotion" in result["retired_routes"]
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "direct_public_data_g8_promotion_retired_no_claim_ready_route"
    )


def test_source_backed_adapter_derivation_is_retained_required_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "source_backed_energy_correlator_to_g8_adapter_derivation"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert row["status"] == "retained_required_before_any_data_based_g8_claim"
    assert "source_backed_jacobian_to_engine_g8_missing" in row["blockers"]
    assert "public_g8_covariance_missing" in row["blockers"]


def test_new_spin4_detector_measurement_remains_cleanest_retained_route():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "new_spin4_or_detector_g8_measurement"
    )

    assert row["status"] == "retained_as_cleanest_measurement_route"
    assert row["retained"] is True
    assert "external_numeric_g8_measurement_missing" in row["blockers"]


def test_theory_bridge_archive_is_nonpromoting():
    row = next(
        row for row in route_decision_rows()
        if row["route"] == "g8_theory_bridge_archive"
    )

    assert row["retained"] is True
    assert row["claim_ready"] is False
    assert "theory_formalism_not_external_measurement" in row["blockers"]
