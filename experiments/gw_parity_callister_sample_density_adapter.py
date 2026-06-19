"""Callister source-native sample-density adapter diagnostic (v2.68)."""

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
    summarize_callister_release_file,
)
from experiments.gw_parity_callister_variable_evolution_probe import (
    _extract_variable_evolution_hdf,
)
from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    histogram_posterior_from_samples,
    joint_histogram_posterior_from_samples,
)


def _compact_histogram(histogram: dict[str, object]) -> dict[str, object]:
    compact = {
        "ready": histogram["ready"],
        "sample_count": histogram["sample_count"],
        "bins": histogram["bins"],
        "density_norm": histogram["density_norm"],
        "blockers": histogram["blockers"],
    }
    if histogram["ready"]:
        if "peak_coordinate" in histogram:
            compact["peak_coordinate"] = histogram["peak_coordinate"]
        else:
            compact["peak_x"] = histogram["peak_x"]
            compact["peak_y"] = histogram["peak_y"]
    return compact


def diagnose_gw_parity_callister_sample_density_adapter(
    cache_dir: Path | None = None,
) -> dict[str, object]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_callister_zenodo_10384998"
    zip_path = _download_archive(cache_dir)
    archive_md5 = _md5(zip_path)
    extract_dir = cache_dir / "extract"
    fixed_paths = _extract_fixed_rate_hdfs(zip_path, extract_dir)
    variable_path = _extract_variable_evolution_hdf(zip_path, extract_dir)
    fixed_delayed_path = next(
        path for path in fixed_paths
        if path.name == "fixed_rate_delayedSFR.hdf"
    )
    fixed_delayed_summary = summarize_callister_release_file(fixed_delayed_path)

    with h5py.File(variable_path, "r") as hdf:
        result = hdf["result"]
        kappa_dc = result["kappa_Dc"][()]
        kappa_z = result["kappa_z"][()]

    kappa_dc_hist = histogram_posterior_from_samples(
        kappa_dc,
        bins=80,
        value_range=(-0.4, 0.4),
    )
    kappa_z_hist = histogram_posterior_from_samples(
        kappa_z,
        bins=80,
        value_range=(-0.5, 0.5),
    )
    joint_hist = joint_histogram_posterior_from_samples(
        kappa_dc,
        kappa_z,
        bins=(80, 80),
        value_range=((-0.4, 0.4), (-0.5, 0.5)),
    )
    artifact_blockers = [
        "fixed_variable_posterior_model_comparison_not_interpreted",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]
    return {
        "version": "v2.68",
        "basis": [
            "v2.67_gw_parity_callister_variable_evolution_probe",
            "Callister_Zenodo_10.5281_zenodo.10384998",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "archive_filename": ZENODO_ARCHIVE_FILENAME,
        "archive_md5_expected": ZENODO_ARCHIVE_MD5,
        "archive_md5_observed": archive_md5,
        "archive_md5_verified": archive_md5 == ZENODO_ARCHIVE_MD5,
        "sample_density_adapter_ready": (
            kappa_dc_hist["ready"] and kappa_z_hist["ready"] and joint_hist["ready"]
        ),
        "variable_evolution_file": variable_path.name,
        "variable_kappa_Dc_density": _compact_histogram(kappa_dc_hist),
        "variable_kappa_z_density": _compact_histogram(kappa_z_hist),
        "variable_joint_density": _compact_histogram(joint_hist),
        "fixed_reference_file": fixed_delayed_path.name,
        "fixed_reference_peaks": {
            "kappa_D_1D": fixed_delayed_summary["kappa_D_1D"]["peak_coordinate"],
            "kappa_z_1D": fixed_delayed_summary["kappa_z_1D"]["peak_coordinate"],
            "joint_kappa_D": fixed_delayed_summary["joint"]["peak_kappa_D"],
            "joint_kappa_z": fixed_delayed_summary["joint"]["peak_kappa_z"],
        },
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "route_status": "callister_sample_density_adapter_ready_projection_blocked",
        "best_next_artifact": (
            "Define a sourced comparison statistic between fixed-rate grid "
            "posteriors and variable-evolution sample densities, still before "
            "PPV beta or engine-axis promotion."
        ),
        "interpretation": (
            "Variable-evolution kappa samples can now be converted into normalized "
            "source-native histogram densities. The comparison to a fixed-rate "
            "reference is diagnostic only and does not carry a physics claim."
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
            "experiments/results/v2.68/"
            "gw_parity_callister_sample_density_adapter.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_callister_sample_density_adapter(args.cache_dir)
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
