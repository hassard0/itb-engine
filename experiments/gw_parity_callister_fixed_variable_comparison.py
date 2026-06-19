"""Callister fixed-rate versus variable-evolution posterior diagnostic (v2.69)."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import h5py

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_parity_callister_real_release_probe import (
    ZENODO_API_URL,
    ZENODO_ARCHIVE_FILENAME,
    ZENODO_ARCHIVE_MD5,
    ZENODO_RECORD_URL,
    _download_archive,
    _extract_fixed_rate_hdfs,
    _md5,
)
from experiments.gw_parity_callister_variable_evolution_probe import (
    _extract_variable_evolution_hdf,
)
from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    compare_one_dimensional_posteriors,
    histogram_posterior_from_samples,
    load_callister_fixed_rate_hdf,
)


def _compact_comparison(comparison: dict[str, object]) -> dict[str, object]:
    return {
        "ready": comparison["ready"],
        "comparison_points": comparison["comparison_points"],
        "overlap_min": comparison["overlap_min"],
        "overlap_max": comparison["overlap_max"],
        "reference_peak_coordinate": comparison["reference_peak_coordinate"],
        "candidate_peak_coordinate": comparison["candidate_peak_coordinate"],
        "peak_offset_candidate_minus_reference": comparison[
            "peak_offset_candidate_minus_reference"
        ],
        "total_variation_distance": comparison["total_variation_distance"],
        "hellinger_distance": comparison["hellinger_distance"],
        "blockers": comparison["blockers"],
    }


def diagnose_gw_parity_callister_fixed_variable_comparison(
    cache_dir: Path | None = None,
) -> dict[str, object]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_callister_zenodo_10384998"
    zip_path = _download_archive(cache_dir)
    archive_md5 = _md5(zip_path)
    extract_dir = cache_dir / "extract"
    fixed_paths = _extract_fixed_rate_hdfs(zip_path, extract_dir)
    variable_path = _extract_variable_evolution_hdf(zip_path, extract_dir)
    fixed_path = next(
        path for path in fixed_paths
        if path.name == "fixed_rate_delayedSFR.hdf"
    )
    fixed = load_callister_fixed_rate_hdf(str(fixed_path))
    with h5py.File(variable_path, "r") as hdf:
        result = hdf["result"]
        variable_kappa_dc = result["kappa_Dc"][()]
        variable_kappa_z = result["kappa_z"][()]

    variable_kappa_dc_density = histogram_posterior_from_samples(
        variable_kappa_dc,
        bins=120,
        value_range=(-0.4, 0.4),
    )
    variable_kappa_z_density = histogram_posterior_from_samples(
        variable_kappa_z,
        bins=120,
        value_range=(-0.5, 0.5),
    )
    kappa_d_comparison = compare_one_dimensional_posteriors(
        fixed["one_dimensional"]["kappa_D"]["coordinates"],
        fixed["one_dimensional"]["kappa_D"]["density"],
        variable_kappa_dc_density["coordinates"],
        variable_kappa_dc_density["density"],
    )
    kappa_z_comparison = compare_one_dimensional_posteriors(
        fixed["one_dimensional"]["kappa_z"]["coordinates"],
        fixed["one_dimensional"]["kappa_z"]["density"],
        variable_kappa_z_density["coordinates"],
        variable_kappa_z_density["density"],
    )
    comparison_ready = (
        fixed["parser_ready"]
        and variable_kappa_dc_density["ready"]
        and variable_kappa_z_density["ready"]
        and kappa_d_comparison["ready"]
        and kappa_z_comparison["ready"]
    )
    artifact_blockers = [
        "comparison_statistic_source_native_only",
        "population_assumption_change_not_framework_exclusion_math",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]
    return {
        "version": "v2.69",
        "basis": [
            "v2.68_gw_parity_callister_sample_density_adapter",
            "Callister_Zenodo_10.5281_zenodo.10384998",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "archive_filename": ZENODO_ARCHIVE_FILENAME,
        "archive_md5_expected": ZENODO_ARCHIVE_MD5,
        "archive_md5_observed": archive_md5,
        "archive_md5_verified": archive_md5 == ZENODO_ARCHIVE_MD5,
        "fixed_reference_file": fixed_path.name,
        "variable_reference_file": variable_path.name,
        "comparison_ready": comparison_ready,
        "kappa_D_fixed_vs_variable_kappa_Dc": _compact_comparison(
            kappa_d_comparison
        ),
        "kappa_z_fixed_vs_variable": _compact_comparison(kappa_z_comparison),
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "route_status": (
            "callister_fixed_variable_comparison_ready_projection_blocked"
        ),
        "best_next_artifact": (
            "Use the source-native comparison to define a release-internal "
            "robustness criterion, then separately harmonize PPV beta conventions."
        ),
        "interpretation": (
            "Fixed-rate and variable-evolution Callister posteriors can now be "
            "compared in native kappa coordinates. The distances quantify "
            "population-model sensitivity only; they are not a quantum-gravity "
            "framework exclusion or engine-axis projection."
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
            "experiments/results/v2.69/"
            "gw_parity_callister_fixed_variable_comparison.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_callister_fixed_variable_comparison(args.cache_dir)
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
