"""Tests for the v2.107 public strain HDF5 smoke loader."""

from pathlib import Path

import h5py
import numpy as np

from experiments.gw_public_strain_connector import gw170608_v3_strain_records
from experiments.gw_public_strain_loader import (
    REQUIRED_DATASETS,
    cache_path_for_record,
    evaluate_loaded_strain,
    load_strain_record,
    read_gwosc_hdf5_metadata,
)


def _write_fixture(path: Path, detector: str = "H1") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as hdf:
        strain = hdf.create_group("strain")
        strain.create_dataset("Strain", data=np.linspace(-1.0, 1.0, 32 * 4096))
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


def test_required_dataset_contract_matches_gwosc_hdf5_layout():
    assert REQUIRED_DATASETS == (
        "/strain/Strain",
        "/meta/GPSstart",
        "/meta/Duration",
        "/meta/Detector",
    )


def test_read_gwosc_hdf5_metadata_from_fixture(tmp_path):
    path = tmp_path / "H1-fixture.hdf5"
    _write_fixture(path, detector="H1")

    metadata = read_gwosc_hdf5_metadata(path)

    assert metadata["datasets_missing"] == []
    assert metadata["detector"] == "H1"
    assert metadata["gps_start"] == 1180922479
    assert metadata["duration"] == 32
    assert metadata["sample_count"] == 32 * 4096
    assert metadata["sample_rate_hz"] == 4096
    assert metadata["strain_finite"] is True
    assert metadata["strain_rms"] > 0.0


def test_load_strain_record_uses_cache_without_network(tmp_path):
    record = _fixture_record("H1", tmp_path)
    cached = cache_path_for_record(record, tmp_path)
    _write_fixture(cached, detector="H1")

    result = load_strain_record(record, tmp_path)

    assert result["loader_ready"] is True
    assert result["sample_count_matches"] is True
    assert result["duration_matches"] is True
    assert result["detector_matches"] is True
    assert result["gps_start_matches"] is True
    assert result["event_inside_segment_from_metadata"] is True


def test_evaluate_loaded_strain_accepts_h1_l1_ready_loads(tmp_path):
    loads = []
    for detector in ("H1", "L1"):
        record = _fixture_record(detector, tmp_path)
        cached = cache_path_for_record(record, tmp_path)
        _write_fixture(cached, detector=detector)
        loads.append(load_strain_record(record, tmp_path))

    result = evaluate_loaded_strain(loads)

    assert result["hdf5_loader_ready"] is True
    assert result["ready_load_count"] == 2
    assert result["detectors_loaded"] == ["H1", "L1"]
    assert result["loader_blockers"] == []
    assert "alpha_waveform_residual_not_connected" in result["claim_blockers"]


def test_evaluate_loaded_strain_rejects_missing_l1(tmp_path):
    record = _fixture_record("H1", tmp_path)
    cached = cache_path_for_record(record, tmp_path)
    _write_fixture(cached, detector="H1")
    load = load_strain_record(record, tmp_path)

    result = evaluate_loaded_strain([load])

    assert result["hdf5_loader_ready"] is False
    assert "loaded_detectors_not_h1_l1" in result["loader_blockers"]
    assert "required_32s_load_count_not_two" in result["loader_blockers"]


def test_real_records_cache_paths_are_hdf5_names(tmp_path):
    records = [
        row for row in gw170608_v3_strain_records() if row["duration"] == 32
    ]

    names = [cache_path_for_record(record, tmp_path).name for record in records]

    assert names == [
        "H-H1_GWOSC_4KHZ_R1-1180922479-32.hdf5",
        "L-L1_GWOSC_4KHZ_R1-1180922479-32.hdf5",
    ]
