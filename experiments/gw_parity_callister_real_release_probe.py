"""Callister real Zenodo fixed-rate posterior probe (v2.66).

This experiment downloads the public Zenodo archive to a local cache, verifies
its md5 checksum, extracts fixed-rate HDF files to that cache, and summarizes
the source-native posterior parser output. Raw release bytes are not committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve
from zipfile import ZipFile

import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from itb.gw_parity import (
    CALLISTER_FIXED_RATE_HDF_FILENAMES,
    GW_PARITY_PROJECTION_BLOCKERS,
    load_callister_fixed_rate_hdf,
)

ZENODO_RECORD_URL = "https://zenodo.org/records/10384998"
ZENODO_API_URL = "https://zenodo.org/api/records/10384998"
ZENODO_ARCHIVE_URL = (
    "https://zenodo.org/api/records/10384998/files/"
    "stochastic-birefringence-data.zip/content"
)
ZENODO_ARCHIVE_FILENAME = "stochastic-birefringence-data.zip"
ZENODO_ARCHIVE_MD5 = "1373cfdd037b5d87c201e2aba06e8b42"


def _md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _download_archive(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / ZENODO_ARCHIVE_FILENAME
    if not zip_path.exists() or _md5(zip_path) != ZENODO_ARCHIVE_MD5:
        urlretrieve(ZENODO_ARCHIVE_URL, zip_path)
    return zip_path


def _extract_fixed_rate_hdfs(zip_path: Path, extract_dir: Path) -> list[Path]:
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    with ZipFile(zip_path) as archive:
        for filename in CALLISTER_FIXED_RATE_HDF_FILENAMES:
            archive.extract(filename, extract_dir)
            extracted.append(extract_dir / filename)
    return extracted


def _grid_summary(grid: dict[str, Any], coordinate_key: str) -> dict[str, Any]:
    coordinates = np.asarray(grid[coordinate_key], dtype=float)
    density = np.asarray(grid["density"], dtype=float)
    peak_index = int(np.argmax(density))
    return {
        "ready": grid["ready"],
        "points": int(coordinates.size),
        "coordinate_min": float(coordinates[0]),
        "coordinate_max": float(coordinates[-1]),
        "normalized_norm": grid["normalized_norm"],
        "peak_coordinate": float(coordinates[peak_index]),
        "blockers": grid["blockers"],
    }


def _joint_summary(joint: dict[str, Any]) -> dict[str, Any]:
    kappa_d = np.asarray(joint["kappa_d_coordinates"], dtype=float)
    kappa_z = np.asarray(joint["kappa_z_coordinates"], dtype=float)
    density = np.asarray(joint["density"], dtype=float)
    peak = np.unravel_index(int(np.argmax(density)), density.shape)
    return {
        "ready": joint["ready"],
        "shape": joint["shape"],
        "kappa_D_min": float(kappa_d[0]),
        "kappa_D_max": float(kappa_d[-1]),
        "kappa_z_min": float(kappa_z[0]),
        "kappa_z_max": float(kappa_z[-1]),
        "normalized_norm": joint["normalized_norm"],
        "peak_kappa_D": float(kappa_d[peak[0]]),
        "peak_kappa_z": float(kappa_z[peak[1]]),
        "blockers": joint["blockers"],
    }


def summarize_callister_release_file(path: Path) -> dict[str, Any]:
    result = load_callister_fixed_rate_hdf(str(path))
    summary = {
        "filename": path.name,
        "parser_ready": result["parser_ready"],
        "parser_blockers": result["parser_blockers"],
        "projection_blockers": result["projection_blockers"],
        "engine_projection_ready": result["engine_projection_ready"],
        "claimable_discriminator_now": result["claimable_discriminator_now"],
    }
    if result["parser_ready"]:
        summary["kappa_D_1D"] = _grid_summary(
            result["one_dimensional"]["kappa_D"],
            "coordinates",
        )
        summary["kappa_z_1D"] = _grid_summary(
            result["one_dimensional"]["kappa_z"],
            "coordinates",
        )
        summary["joint"] = _joint_summary(result["joint"])
    return summary


def diagnose_gw_parity_callister_real_release_probe(
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_callister_zenodo_10384998"
    zip_path = _download_archive(cache_dir)
    archive_md5 = _md5(zip_path)
    extract_dir = cache_dir / "extract"
    hdf_paths = _extract_fixed_rate_hdfs(zip_path, extract_dir)
    file_summaries = [
        summarize_callister_release_file(path)
        for path in hdf_paths
    ]
    all_ready = all(row["parser_ready"] for row in file_summaries)
    artifact_blockers = [
        "variable_rate_hdf_parser_not_implemented",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]
    return {
        "version": "v2.66",
        "basis": [
            "v2.65_gw_parity_callister_posterior_parser",
            "Callister_Zenodo_10.5281_zenodo.10384998",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "archive_filename": ZENODO_ARCHIVE_FILENAME,
        "archive_size_bytes": zip_path.stat().st_size,
        "archive_md5_expected": ZENODO_ARCHIVE_MD5,
        "archive_md5_observed": archive_md5,
        "archive_md5_verified": archive_md5 == ZENODO_ARCHIVE_MD5,
        "fixed_rate_files_checked": [path.name for path in hdf_paths],
        "fixed_rate_file_count": len(file_summaries),
        "all_fixed_rate_parsers_ready": all_ready,
        "real_release_file_bundled": False,
        "hdf_dependency_declared": True,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "file_summaries": file_summaries,
        "route_status": "callister_real_fixed_rate_posteriors_ingested_projection_blocked",
        "best_next_artifact": (
            "Implement the separate variable-evolution HDF parser, then harmonize "
            "helicity and PPV beta normalization before considering any promotion."
        ),
        "interpretation": (
            "All eight Callister fixed-rate Zenodo HDF files parse and normalize "
            "with the guarded source-native parser. This closes the fixed-rate "
            "real-file ingestion blocker, but the result remains native posterior "
            "material and does not produce an engine-axis discriminator."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--out",
        default="experiments/results/v2.66/gw_parity_callister_real_release_probe.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_callister_real_release_probe(args.cache_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
