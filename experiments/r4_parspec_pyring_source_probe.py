"""Probe public pyRing EFT QNM tables for the ParSpec/Bresciani route."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank


VERSION = "v2.201"
DEFAULT_OUT = Path("experiments/results/v2.201/r4_parspec_pyring_source_probe.json")

PYRING_REPO_URL = "https://git.ligo.org/lscsoft/pyring"
PYRING_BRANCH = "EFT_QNMs"
PYRING_BRANCH_HEAD_SHA = "01b7f797c6a260962a1662c4e3450ccfbf48653f"
PYRING_TREE_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/tree/EFT_QNMs/"
    "pyRing/data/NR_data"
)
PYRING_WAVEFORM_SOURCE_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/blob/EFT_QNMs/pyRing/waveform.pyx"
)
PYRING_INITIALISE_SOURCE_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/blob/EFT_QNMs/pyRing/initialise.py"
)
ROTATING_QNM_SOURCE_URL = "https://arxiv.org/abs/2307.07431"

PYRING_TABLE_BASE_RAW_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/raw/EFT_QNMs/"
    "pyRing/data/NR_data"
)
PYRING_QNM_PROBE_AXES = (
    "domega_220_n0_spin0",
    "domi_220_n0_spin0_pyring_sign",
    "domega_221_n1_spin0",
    "domi_221_n1_spin0_pyring_sign",
)
PYRING_QUARTIC_THEORIES = ("quartic_1", "quartic_2", "quartic_3")
PYRING_SOURCE_DIRECTIONS = (
    "quartic_1_minus",
    "quartic_1_plus",
    "quartic_2_minus",
    "quartic_2_plus",
    "quartic_3_minus",
    "quartic_3_plus",
)
REQUIRED_MODES = ((2, 2, 0), (2, 2, 1), (3, 3, 0))
REQUIRED_TABLE_COLUMNS = (
    "l",
    "m",
    "n",
    *tuple(f"om_r_{index}" for index in range(13)),
    *tuple(f"om_i_{index}" for index in range(13)),
)

# Snapshot from the public pyRing EFT_QNMs branch at PYRING_BRANCH_HEAD_SHA.
# The imaginary-frequency entries use pyRing's runtime sign convention:
# domi_EFT_coeff = -om_i_coeff.
PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT: dict[str, dict[str, Any]] = {
    "quartic_1_minus": {
        "filename": "EFT_coefficients_quartic_1_minus.txt",
        "sha256": (
            "595040fc50a87b31b766105c84856600c36fa1f6ec3ce2130efe46e5c18f96ab"
        ),
        "git_lfs_pointer_blob_sha1": "02fd720330226d5a08c45484e228eac027547972",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [-0.079381, 0.057608, -0.600495, -0.473316],
    },
    "quartic_1_plus": {
        "filename": "EFT_coefficients_quartic_1_plus.txt",
        "sha256": (
            "5f81fb7dd2839846b474a5fedc4aa02f5e927b1f8c9eabb91cebe5ebc3c33a86"
        ),
        "git_lfs_pointer_blob_sha1": "2983d46acb02bd9f9cdc2c215fe71a1c7f09ef13",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [-0.166139, 0.244369, -0.428423, 1.23114],
    },
    "quartic_2_minus": {
        "filename": "EFT_coefficients_quartic_2_minus.txt",
        "sha256": (
            "751f35d10bed3db75fbb321548f611483e785853e50b2d29d5add972abe2fbdd"
        ),
        "git_lfs_pointer_blob_sha1": "a03c0d55b7f068e8a002140cffe13f8c2739edcf",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [-0.199007, 0.35232, -0.777659, 1.258555],
    },
    "quartic_2_plus": {
        "filename": "EFT_coefficients_quartic_2_plus.txt",
        "sha256": (
            "a31664948aa56f77604c1d7f457cc874e95cfc9d832f6d107bf13688ac27f00c"
        ),
        "git_lfs_pointer_blob_sha1": "05e0c4a2203bebc7f7ea3f74b9deff3ce6faf5ec",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [0.0, 0.0, 0.0, 0.0],
    },
    "quartic_3_minus": {
        "filename": "EFT_coefficients_quartic_3_minus.txt",
        "sha256": (
            "b878ef82bbf5ec6584942fc75ef305aabeacaf627d2bf3fe1cc28d15d1e13575"
        ),
        "git_lfs_pointer_blob_sha1": "6ad6f01b10c682f39e90d2994194cebfb2a90625",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [-0.073712, 0.136392, -0.169775, 0.741556],
    },
    "quartic_3_plus": {
        "filename": "EFT_coefficients_quartic_3_plus.txt",
        "sha256": (
            "f94c81dc0dfc6b265b0b2638199499d0fb0a1d457c5b295b77f8088c28a716c9"
        ),
        "git_lfs_pointer_blob_sha1": "659adcb51d9b5ff53ee7a81e2f4e05ab0c92b112",
        "data_rows": 3,
        "columns": 29,
        "spin_zero_220_221_vector": [0.073712, -0.136392, 0.169775, -0.741556],
    },
}


def table_raw_url(filename: str) -> str:
    return f"{PYRING_TABLE_BASE_RAW_URL}/{filename}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_nr_data_path(source_root: Path) -> Path:
    nested = source_root / "pyRing" / "data" / "NR_data"
    return nested if nested.exists() else source_root


def _parse_table_file(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        columns = tuple(reader.fieldnames or ())

    if not rows:
        raise ValueError(f"{path} has no data rows")
    missing_columns = set(REQUIRED_TABLE_COLUMNS) - set(columns)
    if missing_columns:
        raise ValueError(f"{path} missing columns: {sorted(missing_columns)}")

    keyed = {
        (int(row["l"]), int(row["m"]), int(row["n"])): row
        for row in rows
    }
    missing_modes = [mode for mode in REQUIRED_MODES if mode not in keyed]
    if missing_modes:
        raise ValueError(f"{path} missing modes: {missing_modes}")

    row_220 = keyed[(2, 2, 0)]
    row_221 = keyed[(2, 2, 1)]
    vector = [
        float(row_220["om_r_0"]),
        -float(row_220["om_i_0"]),
        float(row_221["om_r_0"]),
        -float(row_221["om_i_0"]),
    ]
    return canonicalize_json_floats({
        "filename": path.name,
        "sha256": _sha256(path),
        "data_rows": len(rows),
        "columns": len(columns),
        "spin_zero_220_221_vector": vector,
    })


def load_pyring_quartic_snapshot_from_source_root(
    source_root: str | Path,
) -> dict[str, dict[str, Any]]:
    nr_data = _resolve_nr_data_path(Path(source_root))
    snapshot: dict[str, dict[str, Any]] = {}
    for direction in PYRING_SOURCE_DIRECTIONS:
        filename = f"EFT_coefficients_{direction}.txt"
        row = _parse_table_file(nr_data / filename)
        row["git_lfs_pointer_blob_sha1"] = PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT[
            direction
        ]["git_lfs_pointer_blob_sha1"]
        snapshot[direction] = row
    return canonicalize_json_floats(snapshot)


def pyring_quartic_table_manifest(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
    tables = []
    for direction in PYRING_SOURCE_DIRECTIONS:
        row = snapshot[direction]
        tables.append({
            "source_direction": direction,
            "filename": row["filename"],
            "raw_url": table_raw_url(row["filename"]),
            "sha256": row["sha256"],
            "git_lfs_pointer_blob_sha1": row["git_lfs_pointer_blob_sha1"],
            "data_rows": row["data_rows"],
            "columns": row["columns"],
            "required_modes_present": [list(mode) for mode in REQUIRED_MODES],
        })
    return canonicalize_json_floats({
        "repo_url": PYRING_REPO_URL,
        "branch": PYRING_BRANCH,
        "branch_head_sha": PYRING_BRANCH_HEAD_SHA,
        "tree_url": PYRING_TREE_URL,
        "waveform_source_url": PYRING_WAVEFORM_SOURCE_URL,
        "initialise_source_url": PYRING_INITIALISE_SOURCE_URL,
        "rotating_qnm_source_url": ROTATING_QNM_SOURCE_URL,
        "tables": tables,
        "runtime_interpretation": {
            "source": PYRING_WAVEFORM_SOURCE_URL,
            "frequency_coefficients": "df_EFT_coeffs[theory] = om_r_i",
            "imaginary_frequency_sign": "domi_EFT_coeffs[theory] = -om_i_i",
            "available_eft_theories": list(PYRING_QUARTIC_THEORIES),
            "branch_split": ["plus", "minus"],
            "branch_policy": (
                "plus/minus are QNM mode-splitting branches for a selected "
                "EFT theory, not independent Wilson/operator axes."
            ),
        },
    })


def pyring_spin_zero_qnm_direction_matrix(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
    matrix = [
        [
            float(snapshot[direction]["spin_zero_220_221_vector"][axis_index])
            for direction in PYRING_SOURCE_DIRECTIONS
        ]
        for axis_index in range(len(PYRING_QNM_PROBE_AXES))
    ]
    rank = matrix_rank(matrix)
    return canonicalize_json_floats({
        "matrix_id": "pyring_quartic_spin_zero_220_221_direction_matrix_v1",
        "rows": list(PYRING_QNM_PROBE_AXES),
        "columns": list(PYRING_SOURCE_DIRECTIONS),
        "columns_are_branch_splitting_directions": True,
        "columns_are_independent_operator_axes": False,
        "matrix": matrix,
        "rank": rank,
        "required_rank_for_probe_axes": len(PYRING_QNM_PROBE_AXES),
        "source_scope": (
            "Public pyRing quartic EFT coefficient tables at spin polynomial "
            "order zero for modes (2,2,0) and (2,2,1)."
        ),
    })


def evaluate_pyring_quartic_source_probe(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
    blockers: set[str] = set()

    if tuple(snapshot) != PYRING_SOURCE_DIRECTIONS:
        blockers.add("pyring_quartic_table_set_mismatch")
    for direction in PYRING_SOURCE_DIRECTIONS:
        row = snapshot.get(direction)
        expected = PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT[direction]
        if not isinstance(row, dict):
            blockers.add(f"{direction}_table_missing")
            continue
        if row.get("filename") != expected["filename"]:
            blockers.add(f"{direction}_filename_mismatch")
        if row.get("sha256") != expected["sha256"]:
            blockers.add(f"{direction}_sha256_mismatch")
        if (
            row.get("git_lfs_pointer_blob_sha1")
            != expected["git_lfs_pointer_blob_sha1"]
        ):
            blockers.add(f"{direction}_git_lfs_pointer_blob_sha1_mismatch")
        if row.get("data_rows") != 3:
            blockers.add(f"{direction}_row_count_mismatch")
        if row.get("columns") != len(REQUIRED_TABLE_COLUMNS):
            blockers.add(f"{direction}_column_count_mismatch")
        vector = row.get("spin_zero_220_221_vector")
        if not isinstance(vector, list) or len(vector) != len(PYRING_QNM_PROBE_AXES):
            blockers.add(f"{direction}_probe_vector_shape_mismatch")
            continue
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, int | float):
                blockers.add(f"{direction}_probe_vector_non_numeric")
                break
            if not math.isfinite(float(value)):
                blockers.add(f"{direction}_probe_vector_nonfinite")
                break

    direction_matrix = pyring_spin_zero_qnm_direction_matrix(snapshot)
    if direction_matrix["rank"] < len(PYRING_QNM_PROBE_AXES):
        blockers.add("pyring_quartic_spin_zero_direction_rank_deficient")

    source_intake_ready = not blockers
    independent_branch_columns_ready = (
        source_intake_ready
        and direction_matrix["rank"] == len(PYRING_QNM_PROBE_AXES)
    )
    remaining_claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_plus_minus_branches_not_independent_operator_axes",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "pyring_imaginary_frequency_to_parspec_tau_jacobian_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    return canonicalize_json_floats({
        "public_pyring_quartic_table_intake_ready": source_intake_ready,
        "independent_branch_qnm_columns_ready": independent_branch_columns_ready,
        "independent_qnm_source_directions_ready": False,
        "operator_theory_count": len(PYRING_QUARTIC_THEORIES),
        "branch_column_count": len(PYRING_SOURCE_DIRECTIONS),
        "qnm_to_bresciani_sensitivity_ready": False,
        "public_likelihood_ready": False,
        "ready_for_framework_claim": False,
        "source_intake_blockers": sorted(blockers),
        "remaining_claim_blockers": sorted(remaining_claim_blockers),
        "resolved_v2200_subpieces": (
            [
                "public_pyring_quartic_qnm_table_intake_ready",
                "spin_zero_quartic_branch_qnm_coefficients_ranked",
            ]
            if source_intake_ready
            else []
        ),
        "route_status": (
            "pyring_quartic_qnm_tables_ready_bresciani_map_missing"
            if source_intake_ready
            else "pyring_quartic_qnm_table_probe_not_ready"
        ),
    })


def malformed_pyring_quartic_snapshot() -> dict[str, dict[str, Any]]:
    snapshot = copy.deepcopy(PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT)
    snapshot["quartic_1_plus"]["spin_zero_220_221_vector"] = list(
        snapshot["quartic_1_minus"]["spin_zero_220_221_vector"]
    )
    snapshot["quartic_2_minus"]["spin_zero_220_221_vector"] = list(
        snapshot["quartic_1_minus"]["spin_zero_220_221_vector"]
    )
    snapshot["quartic_2_plus"]["spin_zero_220_221_vector"] = list(
        snapshot["quartic_1_minus"]["spin_zero_220_221_vector"]
    )
    snapshot["quartic_3_minus"]["spin_zero_220_221_vector"] = list(
        snapshot["quartic_1_minus"]["spin_zero_220_221_vector"]
    )
    snapshot["quartic_3_plus"]["spin_zero_220_221_vector"] = list(
        snapshot["quartic_1_minus"]["spin_zero_220_221_vector"]
    )
    return snapshot


def diagnose_r4_parspec_pyring_source_probe(
    *,
    source_root: str | Path | None = None,
) -> dict[str, Any]:
    snapshot = (
        load_pyring_quartic_snapshot_from_source_root(source_root)
        if source_root is not None
        else copy.deepcopy(PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT)
    )
    manifest = pyring_quartic_table_manifest(snapshot)
    direction_matrix = pyring_spin_zero_qnm_direction_matrix(snapshot)
    evaluation = evaluate_pyring_quartic_source_probe(snapshot)
    malformed_evaluation = evaluate_pyring_quartic_source_probe(
        malformed_pyring_quartic_snapshot()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.197_parspec_qnm_deformation_jacobian",
            "v2.200_parspec_qnm_to_bresciani_gate",
            "public_pyring_EFT_QNMs_branch",
        ],
        "source_manifest": manifest,
        "engine_target_axes": list(ENGINE_AXES),
        "parspec_qnm_axes": list(QNM_AXES),
        "pyring_probe_axes": list(PYRING_QNM_PROBE_AXES),
        "pyring_quartic_theories": list(PYRING_QUARTIC_THEORIES),
        "pyring_source_directions": list(PYRING_SOURCE_DIRECTIONS),
        "spin_zero_qnm_direction_matrix": direction_matrix,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed_evaluation,
        "public_pyring_quartic_table_intake_ready": evaluation[
            "public_pyring_quartic_table_intake_ready"
        ],
        "independent_branch_qnm_columns_ready": evaluation[
            "independent_branch_qnm_columns_ready"
        ],
        "independent_qnm_source_directions_ready": False,
        "qnm_to_bresciani_sensitivity_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_pyring_quartic_direction_to_bresciani_axis_orientation_or_"
            "obtain_public_parspec_likelihood"
        ),
        "route_status": evaluation["route_status"],
        "interpretation": (
            "pyRing's public EFT_QNMs branch supplies hash-pinned quartic QNM "
            "coefficient tables and the spin-zero (2,2,0)/(2,2,1) slice has "
            "full rank in the four local qNM probe axes when the plus/minus "
            "branch columns are kept separate. This is useful source material, "
            "but it is not a Bresciani engine-axis map: the physical source "
            "theories are three pyRing quartic labels, plus/minus are "
            "mode-splitting branches rather than independent operator axes, "
            "the imaginary-frequency coefficients still need a ParSpec "
            "tau-axis Jacobian, and no public qEFT likelihood or posterior is "
            "attached."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default=None)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_source_probe(
        source_root=args.source_root,
    )
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
