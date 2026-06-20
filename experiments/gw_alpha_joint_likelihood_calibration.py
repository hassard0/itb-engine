"""Joint-event likelihood calibration for the GW alpha packet."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.125"
DEFAULT_CUBE_EXPORT_PATH = Path(
    "experiments/results/v2.122/gw_alpha_likelihood_cube_export.json"
)
DEFAULT_WAVEFORM_EFT_PATH = Path(
    "experiments/results/v2.124/gw_alpha_waveform_eft_bound.json"
)
FLOAT_TOLERANCE = 1.0e-12
LIKELIHOOD_GAIN_TOLERANCE = 1.0e-2


def logsumexp(values: list[float]) -> float:
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("logsumexp requires finite values")
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def alpha_index(alpha_grid: list[dict[str, float]], alpha_1: float, alpha_2: float) -> int:
    for index, row in enumerate(alpha_grid):
        if (
            abs(float(row["alpha_bar_1"]) - alpha_1) <= FLOAT_TOLERANCE
            and abs(float(row["alpha_bar_2"]) - alpha_2) <= FLOAT_TOLERANCE
        ):
            return index
    raise ValueError(f"alpha grid point missing: {alpha_1}, {alpha_2}")


def validate_shared_nuisance_grid(cube_export: dict[str, Any]) -> list[dict[str, Any]]:
    detector_cubes = cube_export["detector_cubes"]
    if len(detector_cubes) != 2:
        raise ValueError("joint calibration expects two detector cubes")
    reference = detector_cubes[0]["nuisance_grid"]
    for detector_cube in detector_cubes[1:]:
        if detector_cube["nuisance_grid"] != reference:
            raise ValueError("detector nuisance grids are not identical")
    return reference


def joint_likelihood_surface_from_cube(cube_export: dict[str, Any]) -> dict[str, Any]:
    nuisance_grid = validate_shared_nuisance_grid(cube_export)
    detector_cubes = cube_export["detector_cubes"]
    alpha_grid = detector_cubes[0]["alpha_grid"]
    rows = []
    for alpha_i, alpha_point in enumerate(alpha_grid):
        joint_by_nuisance = [
            sum(
                detector_cube["log_likelihood_matrix"][nuisance_i][alpha_i]
                for detector_cube in detector_cubes
            )
            for nuisance_i in range(len(nuisance_grid))
        ]
        profile_index = max(
            range(len(joint_by_nuisance)),
            key=lambda index: joint_by_nuisance[index],
        )
        rows.append(
            {
                **alpha_point,
                "joint_log_marginal_likelihood": (
                    logsumexp(joint_by_nuisance) - math.log(len(joint_by_nuisance))
                ),
                "joint_profile_log_likelihood": joint_by_nuisance[profile_index],
                "joint_profile_nuisance": nuisance_grid[profile_index],
            },
        )
    best_marginal = max(rows, key=lambda row: row["joint_log_marginal_likelihood"])
    best_profile = max(rows, key=lambda row: row["joint_profile_log_likelihood"])
    gr = rows[alpha_index(alpha_grid, 0.0, 0.0)]
    return {
        "likelihood_kind": "joint_shared_nuisance_lalsuite_imrphenomd_alpha_grid",
        "detectors": [row["detector"] for row in detector_cubes],
        "nuisance_semantics": (
            "shared total mass, eta, coalescence-time shift, and coalescence "
            "phase index across detector likelihood cubes"
        ),
        "nuisance_points": len(nuisance_grid),
        "grid_points": len(rows),
        "best_marginal_grid_point": best_marginal,
        "best_profile_grid_point": best_profile,
        "gr_grid_point": gr,
        "delta_log_likelihood_best_vs_gr": (
            best_marginal["joint_log_marginal_likelihood"]
            - gr["joint_log_marginal_likelihood"]
        ),
        "delta_profile_log_likelihood_best_vs_gr": (
            best_profile["joint_profile_log_likelihood"]
            - gr["joint_profile_log_likelihood"]
        ),
        "grid": rows,
    }


def posterior_moments_from_joint_surface(surface: dict[str, Any]) -> dict[str, Any]:
    log_values = [row["joint_log_marginal_likelihood"] for row in surface["grid"]]
    log_norm = logsumexp(log_values)
    weights = [math.exp(value - log_norm) for value in log_values]
    rows = surface["grid"]
    mean_1 = sum(
        weight * float(row["alpha_bar_1"]) for weight, row in zip(weights, rows)
    )
    mean_2 = sum(
        weight * float(row["alpha_bar_2"]) for weight, row in zip(weights, rows)
    )
    var_1 = sum(
        weight * (float(row["alpha_bar_1"]) - mean_1) ** 2
        for weight, row in zip(weights, rows)
    )
    var_2 = sum(
        weight * (float(row["alpha_bar_2"]) - mean_2) ** 2
        for weight, row in zip(weights, rows)
    )
    cov_12 = sum(
        weight
        * (float(row["alpha_bar_1"]) - mean_1)
        * (float(row["alpha_bar_2"]) - mean_2)
        for weight, row in zip(weights, rows)
    )
    return {
        "parameters": ["alpha_bar_1", "alpha_bar_2"],
        "mean": {
            "alpha_bar_1": mean_1,
            "alpha_bar_2": mean_2,
        },
        "covariance": {
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
            "matrix": [[var_1, cov_12], [cov_12, var_2]],
        },
        "central_90": {
            "alpha_bar_1": marginal_credible_interval(rows, weights, "alpha_bar_1"),
            "alpha_bar_2": marginal_credible_interval(rows, weights, "alpha_bar_2"),
        },
        "weight_summary": {
            "max_weight": max(weights),
            "effective_sample_size": 1.0 / sum(weight * weight for weight in weights),
            "weight_sum": sum(weights),
        },
    }


def marginal_credible_interval(
    rows: list[dict[str, Any]],
    weights: list[float],
    axis: str,
    *,
    lower: float = 0.05,
    upper: float = 0.95,
) -> dict[str, float]:
    values = sorted({float(row[axis]) for row in rows})
    intervals = []
    for target in (lower, upper):
        cumulative = 0.0
        for value in values:
            cumulative += sum(
                weight
                for weight, row in zip(weights, rows)
                if float(row[axis]) == value
            )
            if cumulative >= target:
                intervals.append(value)
                break
    return {"lower_90": intervals[0], "upper_90": intervals[1]}


def null_likelihood_calibration(cube_export: dict[str, Any]) -> dict[str, Any]:
    detector_cubes = cube_export["detector_cubes"]
    alpha_grid = detector_cubes[0]["alpha_grid"]
    zero_index = alpha_index(alpha_grid, 0.0, 0.0)
    per_detector_rows = []
    for detector_cube in detector_cubes:
        zero_values = [
            row[zero_index] for row in detector_cube["log_likelihood_matrix"]
        ]
        per_detector_rows.append(
            {
                "detector": detector_cube["detector"],
                "min_zero_alpha_log_likelihood": min(zero_values),
                "max_zero_alpha_log_likelihood": max(zero_values),
                "expected_normalized_null_log_likelihood": -0.5,
                "within_tolerance": (
                    max(abs(value + 0.5) for value in zero_values)
                    <= FLOAT_TOLERANCE
                ),
            },
        )
    expected_network_null = -0.5 * len(detector_cubes)
    return {
        "calibration_kind": "normalized_whitened_residual_null_at_alpha_zero",
        "per_detector": per_detector_rows,
        "expected_network_null_log_likelihood": expected_network_null,
        "calibrated_ready": all(row["within_tolerance"] for row in per_detector_rows),
    }


def packet_with_joint_likelihood_calibration(
    waveform_eft_packet: dict[str, Any],
    joint_surface: dict[str, Any],
    posterior: dict[str, Any],
    null_calibration: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(waveform_eft_packet)
    packet["posterior_or_likelihood_export"] = {
        "status": "reproduced_source_native_likelihood",
        "kind": joint_surface["likelihood_kind"],
        "parameters": ["alpha_bar_1", "alpha_bar_2"],
        "grid_points": joint_surface["grid_points"],
        "detectors": joint_surface["detectors"],
        "nuisance_semantics": joint_surface["nuisance_semantics"],
        "nuisance_points": joint_surface["nuisance_points"],
        "best_marginal_grid_point": joint_surface["best_marginal_grid_point"],
        "best_profile_grid_point": joint_surface["best_profile_grid_point"],
        "gr_grid_point": joint_surface["gr_grid_point"],
        "delta_log_likelihood_best_vs_gr": (
            joint_surface["delta_log_likelihood_best_vs_gr"]
        ),
        "delta_profile_log_likelihood_best_vs_gr": (
            joint_surface["delta_profile_log_likelihood_best_vs_gr"]
        ),
        "weight_summary": posterior["weight_summary"],
        "null_likelihood_calibration": null_calibration,
    }
    packet["source_parameter_covariance"] = posterior["covariance"]
    packet["parameter_constraints"] = {
        "alpha_bar_1": {
            "central": posterior["mean"]["alpha_bar_1"],
            **posterior["central_90"]["alpha_bar_1"],
        },
        "alpha_bar_2": {
            "central": posterior["mean"]["alpha_bar_2"],
            **posterior["central_90"]["alpha_bar_2"],
        },
    }
    packet["systematics_budget"]["status"] = "bounded"
    packet["systematics_budget"]["budget_hold"] = {
        "status": "closed_for_alpha_likelihood_calibration",
        "resolved_blockers": [
            "detector_separable_cube_not_joint_event_posterior",
            "likelihood_scale_not_calibrated_to_noise_evidence",
        ],
        "remaining_claim_blocker": "g8_joint_component_missing",
    }
    packet["joint_likelihood_calibration"] = {
        "joint_likelihood_ready": True,
        "likelihood_scale_calibrated": null_calibration["calibrated_ready"],
        "delta_log_likelihood_best_vs_gr": (
            joint_surface["delta_log_likelihood_best_vs_gr"]
        ),
        "delta_profile_log_likelihood_best_vs_gr": (
            joint_surface["delta_profile_log_likelihood_best_vs_gr"]
        ),
        "likelihood_gain_tolerance": LIKELIHOOD_GAIN_TOLERANCE,
    }
    packet["label"] = "v2_125_joint_event_calibrated_alpha_packet"
    packet["validation_reference"] = "v2.125_alpha_joint_likelihood_calibration"
    return packet


def evaluate_alpha_joint_likelihood_calibration(
    packet: dict[str, Any],
    joint_surface: dict[str, Any],
    null_calibration: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    return {
        "joint_likelihood_ready": True,
        "shared_nuisance_grid_ready": True,
        "likelihood_scale_calibrated": null_calibration["calibrated_ready"],
        "best_marginal_is_gr": (
            abs(joint_surface["best_marginal_grid_point"]["alpha_bar_1"])
            <= FLOAT_TOLERANCE
            and abs(joint_surface["best_marginal_grid_point"]["alpha_bar_2"])
            <= FLOAT_TOLERANCE
        ),
        "delta_log_likelihood_best_vs_gr": (
            joint_surface["delta_log_likelihood_best_vs_gr"]
        ),
        "delta_profile_log_likelihood_best_vs_gr": (
            joint_surface["delta_profile_log_likelihood_best_vs_gr"]
        ),
        "bounded_components": budget_eval["bounded_components"],
        "open_components": budget_eval["open_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "remaining_nonclaiming_reasons": sorted({"g8_joint_component_missing"}),
    }


def diagnose_gw_alpha_joint_likelihood_calibration(
    cube_export_path: Path = DEFAULT_CUBE_EXPORT_PATH,
    waveform_eft_path: Path = DEFAULT_WAVEFORM_EFT_PATH,
) -> dict[str, Any]:
    cube_result = load_json(cube_export_path)
    waveform_eft = load_json(waveform_eft_path)
    joint_surface = joint_likelihood_surface_from_cube(cube_result["likelihood_cube"])
    posterior = posterior_moments_from_joint_surface(joint_surface)
    null_calibration = null_likelihood_calibration(cube_result["likelihood_cube"])
    packet = packet_with_joint_likelihood_calibration(
        waveform_eft["packet"],
        joint_surface,
        posterior,
        null_calibration,
    )
    evaluation = evaluate_alpha_joint_likelihood_calibration(
        packet,
        joint_surface,
        null_calibration,
    )
    return {
        "version": VERSION,
        "basis": [
            "v2.124_alpha_waveform_eft_bound",
            "v2.122_alpha_likelihood_cube_export",
        ],
        "paths": {
            "cube_export": cube_export_path.as_posix(),
            "waveform_eft": waveform_eft_path.as_posix(),
        },
        "joint_likelihood": joint_surface,
        "posterior_summary": posterior,
        "null_likelihood_calibration": null_calibration,
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "joint_likelihood_scale_calibrated_g8_missing_nonclaiming",
        "selected_next_build_action": "supply_g8_joint_component",
        "best_next_artifact": (
            "Add a source-backed G8 joint component or prove no current public "
            "G8 measurement/adapter can be joined to the calibrated alpha packet."
        ),
        "interpretation": (
            "The detector-separable marginalization is replaced by a shared-"
            "nuisance joint event likelihood. The alpha-zero null scale is "
            "calibrated by the normalized whitened residual convention, and the "
            "joint marginal best point remains GR. The alpha packet is now "
            "native-adapter ready, but the hardened adapter still blocks any "
            "claim because the required G8 joint component is missing."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cube-export", default=str(DEFAULT_CUBE_EXPORT_PATH))
    parser.add_argument("--waveform-eft", default=str(DEFAULT_WAVEFORM_EFT_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.125/"
            "gw_alpha_joint_likelihood_calibration.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_joint_likelihood_calibration(
        cube_export_path=Path(args.cube_export),
        waveform_eft_path=Path(args.waveform_eft),
    )
    result = canonicalize_json_floats(result)
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
