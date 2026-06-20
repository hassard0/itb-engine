"""Tests for the v2.106 public GW170608 strain connector."""

from experiments.gw_public_strain_connector import (
    GPS,
    current_public_strain_connector,
    diagnose_gw_public_strain_connector,
    enrich_strain_record,
    evaluate_public_strain_connector,
    gw170608_v3_event_record,
    gw170608_v3_strain_records,
    summarize_strain_records,
    synthetic_ready_public_strain_connector,
)


def test_event_record_selects_gwtc1_confident_v3_with_h1_l1():
    record = gw170608_v3_event_record()

    assert record["event_version"] == "GW170608-v3"
    assert record["catalog"] == "GWTC-1-confident"
    assert record["gps"] == GPS
    assert record["detectors"] == ["H1", "L1"]
    assert record["strain_files_url"].endswith("/GW170608-v3/strain-files")


def test_strain_records_cover_h1_l1_32s_and_4096s_hdf5():
    summary = summarize_strain_records(gw170608_v3_strain_records())

    assert summary["public_strain_urls_ready"] is True
    assert summary["record_count"] == 4
    assert summary["missing_required_records"] == []
    assert summary["malformed_records"] == []
    keys = {(row["detector"], row["duration"]) for row in summary["records"]}
    assert keys == {("H1", 32), ("L1", 32), ("H1", 4096), ("L1", 4096)}


def test_enriched_32_second_record_has_event_inside_segment_and_sample_count():
    record = next(
        row
        for row in gw170608_v3_strain_records()
        if row["detector"] == "H1" and row["duration"] == 32
    )
    enriched = enrich_strain_record(record)

    assert enriched["expected_sample_count"] == 32 * 4096
    assert enriched["event_offset_seconds"] == 15.5
    assert enriched["event_inside_segment"] is True
    assert "detector=H1" in enriched["query_url"]
    assert "duration=32" in enriched["query_url"]


def test_synthetic_connector_is_ready_but_nonclaiming():
    result = evaluate_public_strain_connector(synthetic_ready_public_strain_connector())

    assert result["connector_ready"] is True
    assert result["claim_ready"] is False
    assert result["connector_blockers"] == []
    assert "synthetic_fixture_not_real_public_strain_run" in result["claim_blockers"]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_current_connector_has_urls_ready_but_needs_ingestion_and_residual():
    result = evaluate_public_strain_connector(current_public_strain_connector())

    assert result["connector_ready"] is False
    assert result["strain_summary"]["public_strain_urls_ready"] is True
    assert "hdf5_loader_not_run" in result["connector_blockers"]
    assert "strain_bytes_not_ingested" in result["connector_blockers"]
    assert "alpha_waveform_residual_not_connected" in result["connector_blockers"]


def test_diagnosis_selects_hdf5_loader_smoke_test_next():
    result = diagnose_gw_public_strain_connector()

    assert result["version"] == "v2.106"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "public_strain_urls_connected_hdf5_loader_missing"
    assert result["selected_next_build_action"] == "implement_hdf5_strain_loader_smoke_test"
    assert result["connector_ready_samples"] == ["synthetic_ready_public_strain_connector"]
