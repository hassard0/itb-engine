"""Tests for the v2.179 real GWOSC-HDF5 R4 projection harness."""

from pathlib import Path

import h5py
import numpy as np

from experiments.gw_public_strain_loader import cache_path_for_record
from experiments.r4_response_gwosc_hdf5_projection import (
    diagnose_r4_response_gwosc_hdf5_projection,
    evaluate_r4_response_gwosc_hdf5_projection,
    load_and_project_gwosc_r4_response,
    malformed_r4_gwosc_hdf5_projection_packet,
    network_r4_hdf5_projection,
    project_gwosc_record_r4_response,
    r4_gwosc_hdf5_projection_packet,
)


def _write_fixture(path: Path, detector: str = "H1") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    times = np.arange(32 * 4096, dtype=float) / 4096
    phase = 0.0 if detector == "H1" else 0.31
    strain_values = np.sin(2.0 * np.pi * 37.0 * times + phase)
    strain_values += 0.25 * np.cos(2.0 * np.pi * 91.0 * times - phase)
    with h5py.File(path, "w") as hdf:
        strain = hdf.create_group("strain")
        strain.create_dataset("Strain", data=strain_values)
        meta = hdf.create_group("meta")
        meta.create_dataset("GPSstart", data=1180922479)
        meta.create_dataset("Duration", data=32)
        meta.create_dataset("Detector", data=np.bytes_(detector))


def _fixture_record(detector: str, cache_dir: Path) -> dict:
    filename = f"{detector}-fixture.hdf5"
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


def test_project_gwosc_record_uses_cached_hdf5_without_network(tmp_path):
    record = _fixture_record("H1", tmp_path)
    _write_fixture(cache_path_for_record(record, tmp_path), detector="H1")

    result = project_gwosc_record_r4_response(record, tmp_path)

    assert result["detector"] == "H1"
    assert result["loader_ready"] is True
    assert result["projection_ready"] is True
    assert result["real_public_hdf5_projection"] is True
    assert result["synthetic_strain_fixture"] is False
    assert result["metadata"]["path"].endswith("H1-fixture.hdf5")


def test_h1_l1_hdf5_projection_builds_network_covariance(tmp_path):
    records = _fixture_records(tmp_path)
    rows = load_and_project_gwosc_r4_response(tmp_path, records)
    network = network_r4_hdf5_projection(rows)

    assert [row["detector"] for row in rows] == ["H1", "L1"]
    assert all(row["projection_ready"] for row in rows)
    assert network["real_public_hdf5_projection"] is True
    assert network["synthetic_strain_fixture"] is False
    assert all(network["covariance"][idx][idx] > 0.0 for idx in range(3))


def test_hdf5_projection_packet_ingests_and_scores(tmp_path):
    records = _fixture_records(tmp_path)
    packet = r4_gwosc_hdf5_projection_packet(tmp_path, records)
    result = evaluate_r4_response_gwosc_hdf5_projection(packet)

    assert result["hdf5_projection_harness_engine_ready"] is True
    assert result["fixture_packet_evaluation"]["fixture_packet_engine_ready"] is True
    assert result["shape_score"]["score_available"] is True
    assert result["ready_for_framework_claim"] is False
    assert "r4_response_kernels_are_ansatz_not_source_backed" in (
        result["claim_blockers"]
    )


def test_malformed_hdf5_projection_packet_rejects_missing_detector_and_covariance(
    tmp_path,
):
    records = _fixture_records(tmp_path)
    packet = malformed_r4_gwosc_hdf5_projection_packet(tmp_path, records)
    result = evaluate_r4_response_gwosc_hdf5_projection(packet)

    assert result["hdf5_projection_harness_engine_ready"] is False
    assert "projection_detectors_not_h1_l1" in result["projection_blockers"]
    assert "network_projection_not_marked_real_hdf5" in result["projection_blockers"]
    assert "hdf5_projection_packet_not_engine_ready" in result["projection_blockers"]


def test_diagnosis_selects_source_backed_r4_kernel_derivation_next(tmp_path):
    records = _fixture_records(tmp_path)
    result = diagnose_r4_response_gwosc_hdf5_projection(tmp_path, records)

    assert result["version"] == "v2.179"
    assert result["hdf5_projection_harness_engine_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_response_gwosc_hdf5_projection_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "replace_ansatz_r4_kernels_with_source_backed_pn_imr_derivation"
    )
