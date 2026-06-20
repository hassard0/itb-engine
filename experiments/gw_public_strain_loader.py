"""HDF5 smoke loader for public GW170608 strain files (v2.107)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path
from typing import Any

import h5py
import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_public_strain_connector import (
    GPS,
    SAMPLE_RATE_HZ,
    enrich_strain_record,
    gw170608_v3_strain_records,
)


VERSION = "v2.107"
DEFAULT_CACHE_DIR = Path("data/runs/gwosc_cache")
REQUIRED_DATASETS = (
    "/strain/Strain",
    "/meta/GPSstart",
    "/meta/Duration",
    "/meta/Detector",
)


def _decode_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if hasattr(value, "item"):
        item = value.item()
        if isinstance(item, bytes):
            return item.decode("utf-8")
        return item
    return value


def cache_path_for_record(record: dict[str, Any], cache_dir: Path) -> Path:
    filename = str(record["download_url"]).rsplit("/", 1)[-1]
    return cache_dir / filename


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_cached_strain_file(record: dict[str, Any], cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path_for_record(record, cache_dir)
    if not path.exists():
        urllib.request.urlretrieve(record["download_url"], path)  # noqa: S310
    return path


def read_gwosc_hdf5_metadata(path: Path) -> dict[str, Any]:
    with h5py.File(path, "r") as hdf:
        datasets_present = [
            dataset for dataset in REQUIRED_DATASETS if dataset.strip("/") in hdf
        ]
        missing = [
            dataset for dataset in REQUIRED_DATASETS if dataset.strip("/") not in hdf
        ]
        strain = hdf["/strain/Strain"]
        strain_values = np.asarray(strain, dtype=float)
        gps_start = int(_decode_scalar(hdf["/meta/GPSstart"][()]))
        duration = int(_decode_scalar(hdf["/meta/Duration"][()]))
        detector = str(_decode_scalar(hdf["/meta/Detector"][()]))
    return {
        "path": str(path),
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "datasets_present": datasets_present,
        "datasets_missing": missing,
        "detector": detector,
        "gps_start": gps_start,
        "duration": duration,
        "sample_count": int(strain_values.size),
        "sample_rate_hz": int(strain_values.size // duration) if duration else None,
        "strain_finite": bool(np.isfinite(strain_values).all()),
        "strain_mean": float(np.mean(strain_values)),
        "strain_rms": float(np.sqrt(np.mean(strain_values * strain_values))),
        "strain_min": float(np.min(strain_values)),
        "strain_max": float(np.max(strain_values)),
    }


def load_strain_record(record: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    enriched = enrich_strain_record(record)
    path = ensure_cached_strain_file(record, cache_dir)
    metadata = read_gwosc_hdf5_metadata(path)
    expected_samples = int(enriched["expected_sample_count"])
    event_offset = GPS - float(metadata["gps_start"])
    return {
        "record": enriched,
        "metadata": metadata,
        "sample_count_matches": metadata["sample_count"] == expected_samples,
        "duration_matches": metadata["duration"] == int(record["duration"]),
        "detector_matches": metadata["detector"] == str(record["detector"]),
        "gps_start_matches": metadata["gps_start"] == int(record["gps_start"]),
        "sample_rate_matches": metadata["sample_rate_hz"] == SAMPLE_RATE_HZ,
        "event_offset_seconds_from_metadata": event_offset,
        "event_inside_segment_from_metadata": 0.0 <= event_offset <= metadata["duration"],
        "loader_ready": (
            not metadata["datasets_missing"]
            and metadata["sample_count"] == expected_samples
            and metadata["duration"] == int(record["duration"])
            and metadata["detector"] == str(record["detector"])
            and metadata["gps_start"] == int(record["gps_start"])
            and metadata["sample_rate_hz"] == SAMPLE_RATE_HZ
            and metadata["strain_finite"]
            and math.isfinite(metadata["strain_rms"])
            and metadata["strain_rms"] > 0.0
        ),
    }


def load_required_32s_strain(cache_dir: Path) -> list[dict[str, Any]]:
    records = [
        record
        for record in gw170608_v3_strain_records()
        if int(record["duration"]) == 32
    ]
    return [load_strain_record(record, cache_dir) for record in records]


def evaluate_loaded_strain(loads: list[dict[str, Any]]) -> dict[str, Any]:
    ready_loads = [row for row in loads if row["loader_ready"]]
    detectors = sorted({row["metadata"]["detector"] for row in loads})
    blockers: set[str] = set()
    if detectors != ["H1", "L1"]:
        blockers.add("loaded_detectors_not_h1_l1")
    if len(loads) != 2:
        blockers.add("required_32s_load_count_not_two")
    if len(ready_loads) != len(loads):
        blockers.add("one_or_more_hdf5_loads_failed_validation")
    for row in loads:
        if not row["event_inside_segment_from_metadata"]:
            blockers.add("event_not_inside_loaded_segment")
        if not row["sample_count_matches"]:
            blockers.add("sample_count_mismatch")
    claim_blockers = set(blockers)
    claim_blockers.add("alpha_waveform_residual_not_connected")
    claim_blockers.add("g8_joint_component_missing")
    return {
        "load_count": len(loads),
        "ready_load_count": len(ready_loads),
        "detectors_loaded": detectors,
        "hdf5_loader_ready": not blockers,
        "claim_ready": False,
        "loader_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
    }


def diagnose_gw_public_strain_loader(cache_dir: Path = DEFAULT_CACHE_DIR) -> dict[str, Any]:
    loads = load_required_32s_strain(cache_dir)
    evaluation = evaluate_loaded_strain(loads)
    return {
        "version": VERSION,
        "basis": [
            "v2.106_gw_public_strain_connector",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "cache_dir": str(cache_dir),
        "required_datasets": list(REQUIRED_DATASETS),
        "loads": loads,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "public_hdf5_strain_loader_ready_alpha_residual_missing"
            if evaluation["hdf5_loader_ready"]
            else "public_hdf5_strain_loader_not_ready"
        ),
        "selected_next_build_action": (
            "implement_strain_conditioning_and_alpha_residual_projection"
        ),
        "best_next_artifact": (
            "A deterministic strain-conditioning and residual-projection layer "
            "that consumes the verified H1/L1 arrays and replaces the v2.105 "
            "quadratic alpha stub residual."
        ),
        "interpretation": (
            "The 32-second public GWOSC HDF5 files can now be downloaded, "
            "hashed, opened, and checked for strain sample counts and metadata. "
            "This is still not an alpha-bar likelihood until waveform residuals "
            "are computed from the loaded strain."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.107/gw_public_strain_loader.json",
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_public_strain_loader(Path(args.cache_dir))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
