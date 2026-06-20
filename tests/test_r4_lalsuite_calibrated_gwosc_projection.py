"""Tests for the v2.185 LALSuite-calibrated GWOSC R4 projection."""

from pathlib import Path

import h5py
import numpy as np
import pytest

from experiments.gw_public_strain_loader import cache_path_for_record
from experiments.r4_lalsuite_calibrated_gwosc_projection import (
    PACKET_ID,
    calibrated_channel_coefficients,
    diagnose_r4_lalsuite_calibrated_gwosc_projection,
    evaluate_r4_lalsuite_calibrated_gwosc_projection,
    lalsuite_calibrated_detector_r4_templates,
    load_and_project_lalsuite_calibrated_gwosc_r4,
    malformed_r4_lalsuite_calibrated_gwosc_projection_packet,
    network_lalsuite_calibrated_r4_projection,
    project_gwosc_record_lalsuite_calibrated_r4,
    r4_lalsuite_calibrated_gwosc_projection_packet,
)
from experiments.r4_lalsuite_detector_channel_response import (
    CALIBRATED_CHANNEL_RESPONSE,
)
from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES


def _write_fixture(path: Path, detector: str = "H1") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    times = np.arange(32 * 4096, dtype=float) / 4096
    phase = 0.0 if detector == "H1" else 0.41
    strain_values = np.sin(2.0 * np.pi * 42.0 * times + phase)
    strain_values += 0.2 * np.cos(2.0 * np.pi * 87.0 * times - phase)
    with h5py.File(path, "w") as hdf:
        strain = hdf.create_group("strain")
        strain.create_dataset("Strain", data=strain_values)
        meta = hdf.create_group("meta")
        meta.create_dataset("GPSstart", data=1180922479)
        meta.create_dataset("Duration", data=32)
        meta.create_dataset("Detector", data=np.bytes_(detector))


def _fixture_record(detector: str, cache_dir: Path) -> dict:
    filename = f"{detector}-lalsuite-calibrated-fixture.hdf5"
    return {
        "detector": detector,
        "duration": 32,
        "sample_rate_hz": 4096,
        "gps_start": 1180922479,
        "file_format": "HDF",
        "download_url": f"https://example.test/{filename}",
        "cache_dir": cache_dir,
    }


def _fixture_records(cache_dir: Path) -> list[dict]:
    records = []
    for detector in ("H1", "L1"):
        record = _fixture_record(detector, cache_dir)
        _write_fixture(cache_path_for_record(record, cache_dir), detector=detector)
        records.append(record)
    return records


def test_calibrated_channel_coefficients_match_v2_183_response():
    h1 = calibrated_channel_coefficients("H1")
    l1 = calibrated_channel_coefficients("L1")

    assert h1["K_plus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["H1"]["K_plus"]
    )
    assert h1["Re_K_minus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["H1"]["Re_K_minus"]
    )
    assert l1["K_plus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["L1"]["K_plus"]
    )
    assert l1["Im_K_minus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["L1"]["Im_K_minus"]
    )


def test_lalsuite_calibrated_templates_are_normalized_for_all_axes():
    grid = np.linspace(0.08, 0.32, 32)
    templates = lalsuite_calibrated_detector_r4_templates(grid, "H1")

    assert set(templates) == set(RESPONSE_AXES)
    for axis, template in templates.items():
        assert template.shape == grid.shape
        assert np.isfinite(template).all(), axis
        np.testing.assert_allclose(
            np.linalg.norm(template),
            1.0,
            rtol=0.0,
            atol=1.0e-12,
        )


def test_project_gwosc_record_marks_lalsuite_channel_calibrated(tmp_path):
    record = _fixture_record("H1", tmp_path)
    _write_fixture(cache_path_for_record(record, tmp_path), detector="H1")

    result = project_gwosc_record_lalsuite_calibrated_r4(record, tmp_path)
    projection = result["lalsuite_calibrated_r4_projection"]

    assert result["detector"] == "H1"
    assert result["loader_ready"] is True
    assert result["projection_ready"] is True
    assert projection["source_backed_kernel_derivation"] is True
    assert projection["detector_channel_response_calibrated"] is True
    assert projection["detector_channel_response_id"] == (
        "lalsuite_r4_detector_channel_response_v1"
    )
    assert set(projection["projections"]) == set(RESPONSE_AXES)


def test_h1_l1_lalsuite_calibrated_projection_builds_covariance_seed(tmp_path):
    records = _fixture_records(tmp_path)
    rows = load_and_project_lalsuite_calibrated_gwosc_r4(tmp_path, records)
    network = network_lalsuite_calibrated_r4_projection(rows)

    assert [row["detector"] for row in rows] == ["H1", "L1"]
    assert all(row["projection_ready"] for row in rows)
    assert network["source_backed_kernel_derivation"] is True
    assert network["real_public_hdf5_projection"] is True
    assert network["detector_channel_response_calibrated"] is True
    assert all(network["covariance"][idx][idx] > 0.0 for idx in range(3))


def test_lalsuite_calibrated_packet_ready_but_nonclaiming(tmp_path):
    records = _fixture_records(tmp_path)
    packet = r4_lalsuite_calibrated_gwosc_projection_packet(tmp_path, records)
    result = evaluate_r4_lalsuite_calibrated_gwosc_projection(packet)

    assert packet["packet_id"] == PACKET_ID
    assert result["lalsuite_calibrated_gwosc_projection_ready"] is True
    assert result["fixture_packet_evaluation"]["fixture_packet_engine_ready"] is True
    assert result["ready_for_framework_claim"] is False
    assert "detector_antenna_r4_channel_response_not_calibrated" in (
        result["removed_v2_181_blockers"]
    )
    assert "detector_antenna_r4_channel_response_not_calibrated" not in (
        result["claim_blockers"]
    )
    assert "nuisance_marginalized_covariance_not_exported" in (
        result["claim_blockers"]
    )


def test_malformed_lalsuite_calibrated_packet_rejects_detector_response(tmp_path):
    records = _fixture_records(tmp_path)
    packet = malformed_r4_lalsuite_calibrated_gwosc_projection_packet(
        tmp_path,
        records,
    )
    result = evaluate_r4_lalsuite_calibrated_gwosc_projection(packet)

    assert result["lalsuite_calibrated_gwosc_projection_ready"] is False
    assert "projection_detectors_not_h1_l1" in result["projection_blockers"]
    assert "network_projection_not_lalsuite_calibrated" in (
        result["projection_blockers"]
    )
    assert "lalsuite_detector_channel_response_not_ready" in (
        result["projection_blockers"]
    )


def test_diagnosis_selects_nuisance_covariance_next(tmp_path):
    records = _fixture_records(tmp_path)
    result = diagnose_r4_lalsuite_calibrated_gwosc_projection(tmp_path, records)

    assert result["version"] == "v2.185"
    assert result["lalsuite_calibrated_gwosc_projection_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_lalsuite_calibrated_gwosc_projection_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "export_nuisance_marginalized_r4_covariance"
    )
