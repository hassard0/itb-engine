"""Callister real Zenodo variable-evolution posterior probe (v2.67)."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_parity_callister_real_release_probe import (
    ZENODO_API_URL,
    ZENODO_ARCHIVE_FILENAME,
    ZENODO_ARCHIVE_MD5,
    ZENODO_RECORD_URL,
    _download_archive,
    _md5,
)
from itb.gw_parity import (
    CALLISTER_VARIABLE_EVOLUTION_HDF_FILENAME,
    GW_PARITY_PROJECTION_BLOCKERS,
    load_callister_variable_evolution_hdf,
)


def _extract_variable_evolution_hdf(zip_path: Path, extract_dir: Path) -> Path:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path) as archive:
        archive.extract(CALLISTER_VARIABLE_EVOLUTION_HDF_FILENAME, extract_dir)
    return extract_dir / CALLISTER_VARIABLE_EVOLUTION_HDF_FILENAME


def diagnose_gw_parity_callister_variable_evolution_probe(
    cache_dir: Path | None = None,
) -> dict[str, object]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_callister_zenodo_10384998"
    zip_path = _download_archive(cache_dir)
    archive_md5 = _md5(zip_path)
    hdf_path = _extract_variable_evolution_hdf(zip_path, cache_dir / "extract")
    parser_result = load_callister_variable_evolution_hdf(str(hdf_path))
    artifact_blockers = [
        "posterior_sample_to_density_adapter_not_implemented",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]
    return {
        "version": "v2.67",
        "basis": [
            "v2.66_gw_parity_callister_real_release_probe",
            "Callister_Zenodo_10.5281_zenodo.10384998_variable_evolution",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "archive_filename": ZENODO_ARCHIVE_FILENAME,
        "archive_md5_expected": ZENODO_ARCHIVE_MD5,
        "archive_md5_observed": archive_md5,
        "archive_md5_verified": archive_md5 == ZENODO_ARCHIVE_MD5,
        "variable_evolution_file": hdf_path.name,
        "variable_evolution_file_size_bytes": hdf_path.stat().st_size,
        "parser_ready": parser_result["parser_ready"],
        "parser_blockers": parser_result["parser_blockers"],
        "sample_count": parser_result.get("sample_count", 0),
        "parameter_summaries": parser_result.get("parameter_summaries", {}),
        "spectra_summary": parser_result.get("spectra_summary", {}),
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "parser_projection_blockers": parser_result["projection_blockers"],
        "route_status": "callister_variable_evolution_ingested_projection_blocked",
        "best_next_artifact": (
            "Build a source-native posterior-sample density adapter for "
            "kappa_Dc/kappa_z, then compare fixed-rate and variable-evolution "
            "posteriors without engine-axis promotion."
        ),
        "interpretation": (
            "The remaining public Callister HDF product now has guarded ingestion "
            "coverage. The file is sample-based, not fixed-grid; it can be "
            "summarized safely, but a posterior-sample density adapter is still "
            "needed before combining it with the fixed-rate grids."
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
        default=(
            "experiments/results/v2.67/"
            "gw_parity_callister_variable_evolution_probe.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_callister_variable_evolution_probe(args.cache_dir)
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
