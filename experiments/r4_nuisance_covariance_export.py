"""Nuisance-grid covariance export for the calibrated R4 GWOSC projection."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_lalsuite_marginal_alpha_likelihood import nuisance_grid
from experiments.r4_lalsuite_calibrated_gwosc_projection import (
    evaluate_r4_lalsuite_calibrated_gwosc_projection,
)
from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES


VERSION = "v2.186"
DEFAULT_CALIBRATED_PROJECTION_PATH = Path(
    "experiments/results/v2.185/r4_lalsuite_calibrated_gwosc_projection.json"
)
AXES = tuple(RESPONSE_AXES)
REFERENCE_NUISANCE = {
    "total_mass_solar": 19.0,
    "eta": 0.22,
    "tc_shift_seconds": 0.0,
    "phic_rad": 0.0,
}
NUISANCE_SCALES = {
    "total_mass_solar": 1.0,
    "eta": 0.02,
    "tc_shift_seconds": 0.002,
    "phic_rad": math.pi / 4.0,
}
AXIS_SENSITIVITY = {
    "g_R4_c1": {
        "total_mass_solar": 2.5e-4,
        "eta": -1.2e-4,
        "tc_shift_seconds": 0.8e-4,
        "phic_rad": 0.5e-4,
    },
    "g_R4_c2": {
        "total_mass_solar": -2.0e-4,
        "eta": 1.5e-4,
        "tc_shift_seconds": -0.5e-4,
        "phic_rad": 0.7e-4,
    },
    "g_R4_c3": {
        "total_mass_solar": 5.0e-4,
        "eta": 2.5e-4,
        "tc_shift_seconds": 1.0e-4,
        "phic_rad": -1.5e-4,
    },
}
REMAINING_AFTER_NUISANCE_EXPORT = (
    "full_imr_r4_merger_ringdown_completion_missing",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
    "nuisance_grid_is_coarse_not_posterior_sampler",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def calibrated_projection_packet(
    result: dict[str, Any],
) -> dict[str, Any]:
    return result["projected_packet"]


def _scaled_nuisance_offsets(row: dict[str, float]) -> dict[str, float]:
    return {
        key: (float(row[key]) - REFERENCE_NUISANCE[key]) / NUISANCE_SCALES[key]
        for key in REFERENCE_NUISANCE
    }


def r4_nuisance_shift(row: dict[str, float]) -> dict[str, float]:
    offsets = _scaled_nuisance_offsets(row)
    return {
        axis: float(
            sum(
                AXIS_SENSITIVITY[axis][name] * offsets[name]
                for name in REFERENCE_NUISANCE
            )
        )
        for axis in AXES
    }


def nuisance_shifted_r4_points(
    packet: dict[str, Any],
    *,
    grid: list[dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    central = packet["likelihood"]["central_values"]
    rows = nuisance_grid() if grid is None else grid
    shifted = []
    for row in rows:
        shift = r4_nuisance_shift(row)
        shifted.append({
            "nuisance": row,
            "r4_shift": shift,
            "central_values": {
                axis: float(central[axis] + shift[axis])
                for axis in AXES
            },
        })
    return canonicalize_json_floats(shifted)


def _weighted_covariance(points: np.ndarray, weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = weights / float(np.sum(weights))
    mean = weights @ points
    centered = points - mean
    return centered.T @ (centered * weights[:, None])


def nuisance_covariance_export(
    packet: dict[str, Any],
    *,
    grid: list[dict[str, float]] | None = None,
) -> dict[str, Any]:
    rows = nuisance_shifted_r4_points(packet, grid=grid)
    point_matrix = np.asarray(
        [[row["central_values"][axis] for axis in AXES] for row in rows],
        dtype=float,
    )
    weights = np.full(len(rows), 1.0 / len(rows), dtype=float)
    nuisance_covariance = _weighted_covariance(point_matrix, weights)
    base_covariance = np.asarray(packet["likelihood"]["covariance"], dtype=float)
    exported_covariance = base_covariance + nuisance_covariance
    eigenvalues = np.linalg.eigvalsh(exported_covariance)
    mean = weights @ point_matrix
    return canonicalize_json_floats({
        "export_id": "r4_uniform_nuisance_covariance_export_v1",
        "covariance_kind": (
            "uniform_grid_nuisance_covariance_added_to_v2_185_seed"
        ),
        "axes": list(AXES),
        "nuisance_grid": {
            "parameters": list(REFERENCE_NUISANCE),
            "reference": REFERENCE_NUISANCE,
            "scales": NUISANCE_SCALES,
            "points": len(rows),
            "weighting": "uniform",
            "grid_is_posterior_sampler": False,
        },
        "axis_sensitivity": AXIS_SENSITIVITY,
        "base_central_values": {
            axis: float(packet["likelihood"]["central_values"][axis])
            for axis in AXES
        },
        "nuisance_marginal_mean": {
            axis: float(mean[index]) for index, axis in enumerate(AXES)
        },
        "base_covariance": base_covariance.tolist(),
        "nuisance_covariance": nuisance_covariance.tolist(),
        "exported_covariance": exported_covariance.tolist(),
        "exported_covariance_eigenvalues": eigenvalues.tolist(),
        "positive_definite": bool(np.all(eigenvalues > 0.0)),
        "shifted_points": rows,
    })


def evaluate_r4_nuisance_covariance_export(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = result or diagnose_r4_nuisance_covariance_export()
    packet = result["source_projection_packet"]
    projection_eval = evaluate_r4_lalsuite_calibrated_gwosc_projection(packet)
    export = result["nuisance_covariance_export"]
    blockers: set[str] = set()
    if projection_eval["lalsuite_calibrated_gwosc_projection_ready"] is not True:
        blockers.add("v2_185_calibrated_projection_not_ready")
    if export["nuisance_grid"]["points"] != 81:
        blockers.add("nuisance_grid_point_count_unexpected")
    if export["positive_definite"] is not True:
        blockers.add("exported_covariance_not_positive_definite")
    if sorted(export["axes"]) != sorted(AXES):
        blockers.add("export_axes_not_r4_projection_axes")

    claim_blockers = set(REMAINING_AFTER_NUISANCE_EXPORT)
    if packet.get("provenance", {}).get("synthetic_control") is True:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if blockers:
        claim_blockers.add("nuisance_covariance_export_not_ready")

    return canonicalize_json_floats({
        "export_ready": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "projection_evaluation": projection_eval,
        "export_blockers": sorted(blockers),
        "removed_v2_185_blocker": (
            "nuisance_marginalized_covariance_not_exported"
            if not blockers else None
        ),
        "remaining_real_reanalysis_blockers": sorted(
            REMAINING_AFTER_NUISANCE_EXPORT
        ),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "r4_nuisance_covariance_export_ready_nonclaiming"
            if not blockers
            else "r4_nuisance_covariance_export_blocked"
        ),
    })


def malformed_r4_nuisance_covariance_result(
    calibrated_projection_path: Path = DEFAULT_CALIBRATED_PROJECTION_PATH,
) -> dict[str, Any]:
    source_result = load_json(calibrated_projection_path)
    packet = calibrated_projection_packet(source_result)
    export = nuisance_covariance_export(packet)
    result = {
        "source_projection_packet": packet,
        "nuisance_covariance_export": export,
    }
    export = result["nuisance_covariance_export"]
    export["nuisance_grid"]["points"] = 1
    export["exported_covariance"][2][2] = -1.0
    export["positive_definite"] = False
    return result


def diagnose_r4_nuisance_covariance_export(
    calibrated_projection_path: Path = DEFAULT_CALIBRATED_PROJECTION_PATH,
) -> dict[str, Any]:
    source_result = load_json(calibrated_projection_path)
    packet = calibrated_projection_packet(source_result)
    export = nuisance_covariance_export(packet)
    result = {
        "version": VERSION,
        "basis": [
            "v2.185_r4_lalsuite_calibrated_gwosc_projection",
            "v2.115_gw_nuisance_grid_convention",
        ],
        "calibrated_projection_path": Path(calibrated_projection_path).as_posix(),
        "source_projection_packet": packet,
        "nuisance_covariance_export": export,
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "replace_coarse_nuisance_covariance_with_r4_waveform_likelihood"
        ),
        "best_next_artifact": (
            "Build a real R4 waveform likelihood over the same nuisance axes, "
            "then replace this uniform-grid covariance scaffold with a "
            "posterior or source-owned likelihood export."
        ),
        "interpretation": (
            "The calibrated R4 GWOSC projection now has an exported covariance "
            "contribution from the established event nuisance grid. It remains "
            "nonclaiming because the nuisance grid is deterministic and uniform, "
            "not a posterior sampler, and the full R4 IMR waveform is still missing."
        ),
    }
    evaluation = evaluate_r4_nuisance_covariance_export(result)
    malformed = evaluate_r4_nuisance_covariance_export(
        malformed_r4_nuisance_covariance_result(calibrated_projection_path)
    )
    result["evaluation"] = evaluation
    result["malformed_control_evaluation"] = malformed
    result["export_ready"] = evaluation["export_ready"]
    result["route_status"] = evaluation["route_status"]
    return canonicalize_json_floats(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--calibrated-projection",
        default=str(DEFAULT_CALIBRATED_PROJECTION_PATH),
    )
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.186/"
            "r4_nuisance_covariance_export.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_nuisance_covariance_export(
        Path(args.calibrated_projection)
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
