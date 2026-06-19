"""Callister fixed-rate posterior parser contract (v2.65).

v2.64 implemented source-native GW parity formulas but still blocked on
release-specific posterior ingestion. This iteration implements the Callister
fixed-rate HDF schema parser with synthetic release-shaped data, while keeping
real release files and all engine projection out of scope.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from itb.gw_parity import (
    CALLISTER_FIXED_RATE_HDF_FILENAMES,
    CALLISTER_FIXED_RATE_HDF_KEYS,
    GW_PARITY_PROJECTION_BLOCKERS,
    parse_callister_fixed_rate_hdf_datasets,
)


def _release_shaped_fixture() -> dict[str, Any]:
    kappa_d_1d = np.linspace(-0.2, 0.2, 21)
    probability_kappa_d = np.exp(-0.5 * (kappa_d_1d / 0.06) ** 2)
    kappa_z_1d = np.linspace(-0.4, 0.4, 23)
    probability_kappa_z = np.exp(-0.5 * (kappa_z_1d / 0.11) ** 2)

    kappa_d_2d = np.linspace(-0.5, 0.5, 17)
    kappa_z_2d = np.linspace(-1.0, 1.0, 19)
    probabilities = np.exp(
        -0.5
        * (
            (kappa_d_2d[:, None] / 0.18) ** 2
            + (kappa_z_2d[None, :] / 0.31) ** 2
        )
    )
    return {
        "kappa_dcs_1D": kappa_d_1d,
        "probability_kappa_dc_1D": probability_kappa_d,
        "kappa_zs_1D": kappa_z_1d,
        "probability_kappa_z_1D": probability_kappa_z,
        "kappa_dcs_2D": kappa_d_2d,
        "kappa_zs_2D": kappa_z_2d,
        "probabilities": probabilities,
    }


def diagnose_gw_parity_callister_posterior_parser() -> dict[str, Any]:
    parser_result = parse_callister_fixed_rate_hdf_datasets(
        {"result": _release_shaped_fixture()},
        source_file="synthetic_release_shaped_fixed_rate_delayedSFR.hdf",
    )
    artifact_blockers = [
        "real_zenodo_hdf_file_not_bundled",
        "h5py_optional_dependency_not_installed_in_current_venv",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]
    return {
        "version": "v2.65",
        "basis": [
            "v2.64_gw_parity_ppv_formula_implementation",
            "Callister_2312.12532_public_fixed_rate_hdf_schema",
            "Callister_Zenodo_10.5281_zenodo.10384997",
        ],
        "implemented_layer": "release_specific_callister_fixed_rate_parser",
        "expected_release_filenames": list(CALLISTER_FIXED_RATE_HDF_FILENAMES),
        "expected_hdf_keys": list(CALLISTER_FIXED_RATE_HDF_KEYS),
        "expected_hdf_group": "/result",
        "parser_smoke_ready": parser_result["parser_ready"],
        "parser_smoke_blockers": parser_result["parser_blockers"],
        "one_dimensional_normalized": {
            "kappa_D": parser_result["one_dimensional"]["kappa_D"][
                "normalized_norm"
            ],
            "kappa_z": parser_result["one_dimensional"]["kappa_z"][
                "normalized_norm"
            ],
        },
        "joint_normalized_norm": parser_result["joint"]["normalized_norm"],
        "joint_shape": parser_result["joint"]["shape"],
        "hdf_loader_ready_if_h5py_installed": True,
        "real_release_file_bundled": False,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "parser_result": parser_result,
        "route_status": "callister_release_schema_parser_ready_real_file_blocked",
        "best_next_artifact": (
            "Download or point to a Zenodo fixed-rate HDF file, install h5py in "
            "the runtime, and run the same parser against the real release bytes "
            "without changing the engine projection guard."
        ),
        "interpretation": (
            "The Callister posterior ingestion blocker is narrowed from unknown "
            "schema to a tested fixed-rate parser contract. The parser normalizes "
            "release-shaped kappa_D, kappa_z, and joint grids under the public "
            "/result HDF group, but no real Zenodo HDF file is bundled and no PPV "
            "beta or engine-axis promotion follows."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.65/gw_parity_callister_posterior_parser.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_callister_posterior_parser()
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
