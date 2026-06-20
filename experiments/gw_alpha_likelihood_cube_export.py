"""Per-nuisance likelihood cube export for the GW alpha packet."""

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
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_lalsuite_alpha_likelihood_grid import (
    alpha_grid,
    fixed_parameter_log_likelihood,
)
from experiments.gw_lalsuite_imr_projection import lalsuite_status
from experiments.gw_lalsuite_marginal_alpha_likelihood import (
    DEFAULT_CACHE_DIR,
    detector_nuisance_template_packets,
    logsumexp,
)
from experiments.gw_public_strain_loader import (
    cache_path_for_record,
    ensure_cached_strain_file,
    gw170608_v3_strain_records,
    load_required_32s_strain,
)
from experiments.gw_strain_alpha_residual_projection import read_strain_values


VERSION = "v2.122"
DEFAULT_PRIOR_STRESS_PATH = Path(
    "experiments/results/v2.121/gw_alpha_prior_treatment_stress_test.json"
)
DEFAULT_MARGINAL_RESULT_PATH = Path(
    "experiments/results/v2.115/gw_lalsuite_marginal_alpha_likelihood.json"
)
SURFACE_TOLERANCE = 1.0e-9


def likelihood_matrix_from_packets(
    packets: list[dict[str, Any]],
    *,
    grid: list[dict[str, float]] | None = None,
) -> list[list[float]]:
    alpha_rows = alpha_grid() if grid is None else grid
    if not packets:
        raise ValueError("packets must not be empty")
    if not alpha_rows:
        raise ValueError("alpha grid must not be empty")
    matrix = []
    for packet in packets:
        nuisance_row = []
        for point in alpha_rows:
            nuisance_row.append(
                fixed_parameter_log_likelihood(
                    packet["data"],
                    packet["templates"],
                    alpha_bar_1=point["alpha_bar_1"],
                    alpha_bar_2=point["alpha_bar_2"],
                )
            )
        matrix.append(nuisance_row)
    return matrix


def detector_likelihood_cube_from_packets(
    detector: str,
    packets: list[dict[str, Any]],
    *,
    path: str | None = None,
    grid: list[dict[str, float]] | None = None,
) -> dict[str, Any]:
    alpha_rows = alpha_grid() if grid is None else grid
    matrix = likelihood_matrix_from_packets(packets, grid=alpha_rows)
    nuisance_rows = [packet["nuisance"] for packet in packets]
    finite = all(math.isfinite(value) for row in matrix for value in row)
    return {
        "detector": detector,
        "path": path,
        "nuisance_grid": nuisance_rows,
        "alpha_grid": alpha_rows,
        "log_likelihood_matrix": matrix,
        "shape": {
            "nuisance_points": len(nuisance_rows),
            "alpha_grid_points": len(alpha_rows),
            "matrix_rows": len(matrix),
            "matrix_columns": len(matrix[0]) if matrix else 0,
        },
        "finite": finite,
    }


def load_detector_likelihood_cube(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    packets = detector_nuisance_template_packets(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return detector_likelihood_cube_from_packets(
        record["detector"],
        packets,
        path=str(cache_path_for_record(record, cache_dir)),
    )


def network_surfaces_from_cube(cube_export: dict[str, Any]) -> dict[str, Any]:
    detector_cubes = cube_export["detector_cubes"]
    if not detector_cubes:
        raise ValueError("detector_cubes must not be empty")
    alpha_rows = detector_cubes[0]["alpha_grid"]
    network_rows = []
    for alpha_index, point in enumerate(alpha_rows):
        log_marginal = 0.0
        profile = 0.0
        for detector_cube in detector_cubes:
            column = [
                row[alpha_index]
                for row in detector_cube["log_likelihood_matrix"]
            ]
            log_marginal += logsumexp(column) - math.log(len(column))
            profile += max(column)
        network_rows.append(
            {
                **point,
                "log_marginal_likelihood": float(log_marginal),
                "profile_log_likelihood": float(profile),
            }
        )
    return {
        "detectors": [row["detector"] for row in detector_cubes],
        "grid_points": len(network_rows),
        "best_marginal_grid_point": max(
            network_rows,
            key=lambda row: row["log_marginal_likelihood"],
        ),
        "best_profile_grid_point": max(
            network_rows,
            key=lambda row: row["profile_log_likelihood"],
        ),
        "grid": network_rows,
    }


def cube_surface_deltas(
    cube_export: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    reconstructed = network_surfaces_from_cube(cube_export)
    reference_lookup = {
        (row["alpha_bar_1"], row["alpha_bar_2"]): row
        for row in marginal_result["network_likelihood"]["grid"]
    }
    max_marginal_delta = 0.0
    max_profile_delta = 0.0
    for row in reconstructed["grid"]:
        key = (row["alpha_bar_1"], row["alpha_bar_2"])
        reference = reference_lookup[key]
        max_marginal_delta = max(
            max_marginal_delta,
            abs(row["log_marginal_likelihood"] - reference["log_marginal_likelihood"]),
        )
        max_profile_delta = max(
            max_profile_delta,
            abs(row["profile_log_likelihood"] - reference["profile_log_likelihood"]),
        )
    return {
        "reconstructed_network": {
            "detectors": reconstructed["detectors"],
            "grid_points": reconstructed["grid_points"],
            "best_marginal_grid_point": reconstructed["best_marginal_grid_point"],
            "best_profile_grid_point": reconstructed["best_profile_grid_point"],
        },
        "max_marginal_log_likelihood_delta": max_marginal_delta,
        "max_profile_log_likelihood_delta": max_profile_delta,
        "within_tolerance": (
            max_marginal_delta <= SURFACE_TOLERANCE
            and max_profile_delta <= SURFACE_TOLERANCE
        ),
        "tolerance": SURFACE_TOLERANCE,
    }


def evaluate_likelihood_cube_export(
    cube_export: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    detector_cubes = cube_export.get("detector_cubes", [])
    shape_ready = (
        sorted(row.get("detector") for row in detector_cubes) == ["H1", "L1"]
        and all(row.get("finite") for row in detector_cubes)
        and all(row["shape"]["nuisance_points"] == 81 for row in detector_cubes)
        and all(row["shape"]["alpha_grid_points"] == 441 for row in detector_cubes)
        and all(row["shape"]["matrix_rows"] == 81 for row in detector_cubes)
        and all(row["shape"]["matrix_columns"] == 441 for row in detector_cubes)
    )
    surface_deltas = cube_surface_deltas(cube_export, marginal_result)
    cube_ready = shape_ready and surface_deltas["within_tolerance"]
    return {
        "likelihood_cube_ready": cube_ready,
        "shape_ready": shape_ready,
        "surface_reconstruction": surface_deltas,
        "cube_cells": sum(
            row["shape"]["matrix_rows"] * row["shape"]["matrix_columns"]
            for row in detector_cubes
        ),
        "claim_ready": False,
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "prior_reweight_sweep_not_yet_run",
                "waveform_and_eft_systematics_still_open",
            }
        ),
    }


def packet_with_likelihood_cube_export(
    prior_stress_packet: dict[str, Any],
    cube_evaluation: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(prior_stress_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence["prior_sensitivity"] = {
        "status": "open",
        "basis": "per_nuisance_likelihood_cube_exported",
        "likelihood_cube_ready": cube_evaluation["likelihood_cube_ready"],
        "cube_cells": cube_evaluation["cube_cells"],
        "surface_reconstruction": cube_evaluation["surface_reconstruction"],
        "closure_target": (
            "Run physically justified nuisance-prior sweeps over the exported "
            "detector alpha/nuisance likelihood cube."
        ),
    }
    packet["label"] = "v2_122_likelihood_cube_exported_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = {
        component: row["status"] for component, row in evidence.items()
    }
    packet["systematics_budget"]["status"] = (
        "bounded"
        if all(row["status"] == "bounded" for row in evidence.values())
        else "open"
    )
    packet["validation_reference"] = "v2.122_alpha_likelihood_cube_export"
    return packet


def diagnose_gw_alpha_likelihood_cube_export(
    prior_stress_path: Path = DEFAULT_PRIOR_STRESS_PATH,
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    prior_stress = load_json(prior_stress_path)
    marginal_result = load_json(marginal_result_path)
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        return {
            "version": VERSION,
            "basis": ["v2.121_alpha_prior_treatment_stress_test"],
            "lalsuite_status": status,
            "evaluation": {
                "likelihood_cube_ready": False,
                "claim_ready": False,
                "remaining_nonclaiming_reasons": [
                    "lalsuite_optional_dependency_missing",
                    "prior_nuisance_cube_missing",
                ],
            },
            "claimable_discriminator_now": False,
            "route_status": "likelihood_cube_export_not_ready",
            "selected_next_build_action": "install_lalsuite_and_export_cube",
        }

    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_cubes = [
        load_detector_likelihood_cube(record, cache_dir)
        for record in records
    ]
    cube_export = {
        "version": VERSION,
        "cube_kind": "detector_alpha_by_nuisance_log_likelihood_matrix",
        "source_result": "v2.115_lalsuite_marginal_alpha_likelihood",
        "detector_cubes": detector_cubes,
    }
    cube_evaluation = evaluate_likelihood_cube_export(cube_export, marginal_result)
    packet = packet_with_likelihood_cube_export(
        prior_stress["packet"],
        cube_evaluation,
    )
    budget_evaluation = evaluate_alpha_systematics_budget(packet)
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.121_alpha_prior_treatment_stress_test",
            "v2.115_lalsuite_marginal_alpha_likelihood",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "cache_dir": str(cache_dir),
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "lalsuite_status": status,
        "likelihood_cube": cube_export,
        "packet": packet,
        "evaluation": {
            **cube_evaluation,
            "bounded_components": budget_evaluation["bounded_components"],
            "open_components": budget_evaluation["open_components"],
            "adapter_evaluation": adapter,
        },
        "claimable_discriminator_now": False,
        "route_status": (
            "per_nuisance_likelihood_cube_exported_nonclaiming"
            if cube_evaluation["likelihood_cube_ready"]
            else "likelihood_cube_export_not_ready"
        ),
        "selected_next_build_action": "prior_reweight_sweep_from_likelihood_cube",
        "best_next_artifact": (
            "Use the exported detector alpha/nuisance cube to sweep physically "
            "justified priors over total mass, eta, coalescence time, and phase."
        ),
        "interpretation": (
            "The missing prior cube blocker is removed: the detector-by-detector "
            "alpha/nuisance log-likelihood matrices reconstruct the v2.115 "
            "marginal and profile network surfaces within tolerance. Prior "
            "sensitivity remains open until actual nuisance-prior reweighting "
            "is run on this cube."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-stress", default=str(DEFAULT_PRIOR_STRESS_PATH))
    parser.add_argument("--marginal-result", default=str(DEFAULT_MARGINAL_RESULT_PATH))
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.122/"
            "gw_alpha_likelihood_cube_export.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_likelihood_cube_export(
        prior_stress_path=Path(args.prior_stress),
        marginal_result_path=Path(args.marginal_result),
        cache_dir=Path(args.cache_dir),
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
