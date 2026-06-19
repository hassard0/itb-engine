"""Tests for current-source recheck of the g8 route."""

from experiments.g8_current_source_recheck import (
    current_source_rows,
    diagnose_g8_current_source_recheck,
)


def test_current_source_recheck_finds_no_claim_ready_g8_packet():
    result = diagnose_g8_current_source_recheck()

    assert result["version"] == "v2.78"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "current_sources_no_engine_g8_measurement_packet"


def test_partial_wave_unitarity_source_is_theory_bridge_only():
    row = next(
        row for row in current_source_rows()
        if row["label"] == "bresciani_levati_paradisi_partial_wave_unitarity"
    )

    assert row["source_kind"] == "theory_formalism"
    assert row["external_numeric_measurement"] is False
    assert row["claim_ready"] is False
    assert "theory_formalism_not_external_measurement" in row["blockers"]


def test_cms_energy_correlator_is_external_but_not_engine_g8():
    row = next(
        row for row in current_source_rows()
        if row["label"] == "cms_energy_correlator_measurements"
    )

    assert row["external_numeric_measurement"] is True
    assert row["engine_g8_mapping"] is False
    assert row["claim_ready"] is False
    assert "qcd_jet_observable_not_qg_eft_g8" in row["blockers"]


def test_current_recheck_preserves_adapter_next_step():
    result = diagnose_g8_current_source_recheck()

    assert "partial-wave/detector theory bridges" in result["best_next_artifact"]
    assert "no_engine_g8_normalization" in result["blocker_counts"]
