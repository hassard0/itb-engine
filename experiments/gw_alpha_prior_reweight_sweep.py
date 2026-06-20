"""Nuisance-prior reweight sweep from the GW alpha likelihood cube."""

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
from experiments.gw_alpha_prior_treatment_stress_test import alpha_axis_step
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.123"
DEFAULT_CUBE_EXPORT_PATH = Path(
    "experiments/results/v2.122/gw_alpha_likelihood_cube_export.json"
)
ALPHA_PREFERENCE_LOG_LIKELIHOOD_TOLERANCE = 1.0e-2
FLOAT_TOLERANCE = 1.0e-12
JSON_FLOAT_DIGITS = 12


def logsumexp(values: list[float]) -> float:
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("logsumexp requires finite values")
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def normalized_log_weights(log_weights: list[float]) -> list[float]:
    log_norm = logsumexp(log_weights)
    return [value - log_norm for value in log_weights]


def shortest_angular_difference(rad: float, center: float) -> float:
    return (rad - center + math.pi) % (2.0 * math.pi) - math.pi


def normal_log_density(value: float, *, mean: float, sigma: float) -> float:
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    z = (value - mean) / sigma
    return -0.5 * z * z - math.log(sigma * math.sqrt(2.0 * math.pi))


def wrapped_normal_log_density(value: float, *, mean: float, sigma: float) -> float:
    return normal_log_density(
        shortest_angular_difference(value, mean),
        mean=0.0,
        sigma=sigma,
    )


def declared_prior_catalog() -> list[dict[str, Any]]:
    return [
        {
            "name": "uniform_grid_control",
            "scope": "physical_catalog",
            "description": "The v2.115 uniform nuisance-grid prior.",
            "factors": {},
        },
        {
            "name": "central_broad_event_prior",
            "scope": "physical_catalog",
            "description": (
                "Broad event-centered prior over total mass, symmetric mass "
                "ratio, coalescence time, and phase."
            ),
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "central_tight_event_prior",
            "scope": "physical_catalog",
            "description": (
                "Tighter one-cell-scale event prior to test whether the "
                "catalog is sensitive to concentrated, but still smooth, "
                "nuisance weighting."
            ),
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.45},
                "eta": {"mean": 0.22, "sigma": 0.012},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.00075},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 6.0},
            },
        },
        {
            "name": "low_mass_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward the lower total-mass sideband.",
            "factors": {
                "total_mass_solar": {"mean": 18.35, "sigma": 0.45},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "high_mass_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward the upper total-mass sideband.",
            "factors": {
                "total_mass_solar": {"mean": 19.65, "sigma": 0.45},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "low_eta_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward the lower eta sideband.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.205, "sigma": 0.012},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "high_eta_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward the upper eta sideband.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.235, "sigma": 0.012},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "early_tc_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward earlier coalescence time.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": -0.0015, "sigma": 0.00075},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "late_tc_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward later coalescence time.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0015, "sigma": 0.00075},
                "phic_rad": {"mean": 0.0, "sigma": math.pi / 3.0},
            },
        },
        {
            "name": "negative_phase_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward negative coalescence phase.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": -math.pi / 6.0, "sigma": math.pi / 6.0},
            },
        },
        {
            "name": "positive_phase_sideband_prior",
            "scope": "physical_catalog",
            "description": "Prior stress toward positive coalescence phase.",
            "factors": {
                "total_mass_solar": {"mean": 19.0, "sigma": 0.75},
                "eta": {"mean": 0.22, "sigma": 0.025},
                "tc_shift_seconds": {"mean": 0.0, "sigma": 0.0015},
                "phic_rad": {"mean": math.pi / 6.0, "sigma": math.pi / 6.0},
            },
        },
        {
            "name": "lower_corner_combined_stress_prior",
            "scope": "physical_catalog_boundary_stress",
            "description": (
                "Combined lower-corner stress over mass, eta, time, and phase."
            ),
            "factors": {
                "total_mass_solar": {"mean": 18.0, "sigma": 0.35},
                "eta": {"mean": 0.20, "sigma": 0.010},
                "tc_shift_seconds": {"mean": -0.002, "sigma": 0.0005},
                "phic_rad": {"mean": -math.pi / 4.0, "sigma": math.pi / 8.0},
            },
        },
        {
            "name": "upper_corner_combined_stress_prior",
            "scope": "physical_catalog_boundary_stress",
            "description": (
                "Combined upper-corner stress over mass, eta, time, and phase."
            ),
            "factors": {
                "total_mass_solar": {"mean": 20.0, "sigma": 0.35},
                "eta": {"mean": 0.24, "sigma": 0.010},
                "tc_shift_seconds": {"mean": 0.002, "sigma": 0.0005},
                "phic_rad": {"mean": math.pi / 4.0, "sigma": math.pi / 8.0},
            },
        },
    ]


def prior_log_weight(row: dict[str, float], prior: dict[str, Any]) -> float:
    total = 0.0
    factors = prior.get("factors", {})
    for field, spec in factors.items():
        if field == "phic_rad":
            total += wrapped_normal_log_density(
                float(row[field]),
                mean=float(spec["mean"]),
                sigma=float(spec["sigma"]),
            )
        else:
            total += normal_log_density(
                float(row[field]),
                mean=float(spec["mean"]),
                sigma=float(spec["sigma"]),
            )
    return total


def nuisance_log_weights(
    nuisance_grid: list[dict[str, float]],
    prior: dict[str, Any],
) -> list[float]:
    if not nuisance_grid:
        raise ValueError("nuisance grid must not be empty")
    if not prior.get("factors"):
        return [-math.log(len(nuisance_grid)) for _row in nuisance_grid]
    return normalized_log_weights(
        [prior_log_weight(row, prior) for row in nuisance_grid],
    )


def nuisance_weight_summary(log_weights: list[float]) -> dict[str, float]:
    weights = [math.exp(value) for value in log_weights]
    effective_sample_count = 1.0 / sum(weight * weight for weight in weights)
    return {
        "effective_sample_count": float(effective_sample_count),
        "max_weight": float(max(weights)),
        "min_weight": float(min(weights)),
        "weight_sum": float(sum(weights)),
    }


def detector_reweighted_log_likelihoods(
    detector_cube: dict[str, Any],
    prior: dict[str, Any],
) -> dict[str, Any]:
    matrix = detector_cube["log_likelihood_matrix"]
    if not matrix:
        raise ValueError("log likelihood matrix must not be empty")
    log_weights = nuisance_log_weights(detector_cube["nuisance_grid"], prior)
    alpha_count = len(detector_cube["alpha_grid"])
    rows = []
    for alpha_index in range(alpha_count):
        rows.append(
            logsumexp(
                [
                    nuisance_row[alpha_index] + log_weights[nuisance_index]
                    for nuisance_index, nuisance_row in enumerate(matrix)
                ],
            ),
        )
    return {
        "detector": detector_cube["detector"],
        "log_likelihoods": rows,
        "nuisance_weight_summary": nuisance_weight_summary(log_weights),
    }


def reweighted_network_surface(
    cube_export: dict[str, Any],
    prior: dict[str, Any],
) -> dict[str, Any]:
    detector_cubes = cube_export["detector_cubes"]
    if not detector_cubes:
        raise ValueError("detector_cubes must not be empty")
    alpha_rows = detector_cubes[0]["alpha_grid"]
    detector_curves = [
        detector_reweighted_log_likelihoods(detector_cube, prior)
        for detector_cube in detector_cubes
    ]
    grid = []
    for alpha_index, alpha_point in enumerate(alpha_rows):
        log_likelihood = sum(
            curve["log_likelihoods"][alpha_index] for curve in detector_curves
        )
        grid.append(
            {
                **alpha_point,
                "log_reweighted_likelihood": float(log_likelihood),
            },
        )
    best = max(grid, key=lambda row: row["log_reweighted_likelihood"])
    gr = grid_point_at_alpha(grid, 0.0, 0.0)
    return {
        "prior_name": prior["name"],
        "prior_scope": prior["scope"],
        "detectors": [curve["detector"] for curve in detector_curves],
        "detector_weight_summaries": [
            {
                "detector": curve["detector"],
                **curve["nuisance_weight_summary"],
            }
            for curve in detector_curves
        ],
        "best_grid_point": best,
        "gr_grid_point": gr,
        "delta_log_likelihood_best_vs_gr": float(
            best["log_reweighted_likelihood"] - gr["log_reweighted_likelihood"]
        ),
        "grid_points": len(grid),
        "grid": grid,
    }


def grid_point_at_alpha(
    grid: list[dict[str, Any]],
    alpha_bar_1: float,
    alpha_bar_2: float,
) -> dict[str, Any]:
    for row in grid:
        if (
            abs(float(row["alpha_bar_1"]) - alpha_bar_1) <= FLOAT_TOLERANCE
            and abs(float(row["alpha_bar_2"]) - alpha_bar_2) <= FLOAT_TOLERANCE
        ):
            return row
    raise ValueError(f"alpha grid point missing: {alpha_bar_1}, {alpha_bar_2}")


def summarize_surface(
    surface: dict[str, Any],
    *,
    baseline_best: dict[str, Any],
    axis_step: float,
) -> dict[str, Any]:
    best = surface["best_grid_point"]
    delta_1 = float(best["alpha_bar_1"]) - float(baseline_best["alpha_bar_1"])
    delta_2 = float(best["alpha_bar_2"]) - float(baseline_best["alpha_bar_2"])
    max_abs_axis_shift = max(abs(delta_1), abs(delta_2))
    euclidean_shift = math.dist(
        (float(best["alpha_bar_1"]), float(best["alpha_bar_2"])),
        (float(baseline_best["alpha_bar_1"]), float(baseline_best["alpha_bar_2"])),
    )
    return {
        "prior_name": surface["prior_name"],
        "prior_scope": surface["prior_scope"],
        "detector_weight_summaries": surface["detector_weight_summaries"],
        "best_grid_point": surface["best_grid_point"],
        "gr_grid_point": surface["gr_grid_point"],
        "delta_log_likelihood_best_vs_gr": (
            surface["delta_log_likelihood_best_vs_gr"]
        ),
        "shift_from_uniform_best": {
            "delta_alpha_bar_1": delta_1,
            "delta_alpha_bar_2": delta_2,
            "max_abs_axis_shift": max_abs_axis_shift,
            "euclidean_shift": euclidean_shift,
            "max_abs_axis_grid_steps": max_abs_axis_shift / axis_step,
            "euclidean_grid_steps": euclidean_shift / axis_step,
        },
        "within_one_cell_per_axis": (
            max_abs_axis_shift <= axis_step + FLOAT_TOLERANCE
        ),
        "insignificant_preference_vs_gr": (
            surface["delta_log_likelihood_best_vs_gr"]
            <= ALPHA_PREFERENCE_LOG_LIKELIHOOD_TOLERANCE
        ),
    }


def prior_reweight_sweep_from_cube(
    cube_result: dict[str, Any],
    *,
    priors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    prior_catalog = declared_prior_catalog() if priors is None else priors
    cube_export = cube_result["likelihood_cube"]
    alpha_rows = cube_export["detector_cubes"][0]["alpha_grid"]
    axis_step = alpha_axis_step(alpha_rows)
    surfaces = [
        reweighted_network_surface(cube_export, prior)
        for prior in prior_catalog
    ]
    baseline = next(
        surface for surface in surfaces if surface["prior_name"] == "uniform_grid_control"
    )
    summaries = [
        summarize_surface(
            surface,
            baseline_best=baseline["best_grid_point"],
            axis_step=axis_step,
        )
        for surface in surfaces
    ]
    max_axis_grid_steps = max(
        row["shift_from_uniform_best"]["max_abs_axis_grid_steps"]
        for row in summaries
    )
    max_euclidean_grid_steps = max(
        row["shift_from_uniform_best"]["euclidean_grid_steps"] for row in summaries
    )
    max_delta_log_likelihood_best_vs_gr = max(
        row["delta_log_likelihood_best_vs_gr"] for row in summaries
    )
    bounded = (
        all(row["within_one_cell_per_axis"] for row in summaries)
        and all(row["insignificant_preference_vs_gr"] for row in summaries)
    )
    return {
        "sweep_kind": "factorized_nuisance_prior_reweighting_from_exported_cube",
        "source_cube_version": cube_result["version"],
        "prior_catalog": prior_catalog,
        "alpha_axis_step": axis_step,
        "baseline_prior_name": baseline["prior_name"],
        "baseline_best_grid_point": baseline["best_grid_point"],
        "prior_summary_rows": summaries,
        "reweighted_network_surfaces": surfaces,
        "stability_thresholds": {
            "max_abs_axis_grid_steps": 1.0,
            "max_delta_log_likelihood_best_vs_gr": (
                ALPHA_PREFERENCE_LOG_LIKELIHOOD_TOLERANCE
            ),
        },
        "max_abs_axis_grid_steps": float(max_axis_grid_steps),
        "max_euclidean_grid_steps": float(max_euclidean_grid_steps),
        "max_delta_log_likelihood_best_vs_gr": float(
            max_delta_log_likelihood_best_vs_gr
        ),
        "catalog_prior_sensitivity_bounded": bounded,
    }


def packet_with_prior_reweight_sweep(
    cube_packet: dict[str, Any],
    sweep: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(cube_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence["prior_sensitivity"] = {
        "status": (
            "bounded"
            if sweep["catalog_prior_sensitivity_bounded"]
            else "open"
        ),
        "basis": "factorized_nuisance_prior_reweight_sweep_from_likelihood_cube",
        "source_cube_version": sweep["source_cube_version"],
        "prior_catalog_size": len(sweep["prior_catalog"]),
        "alpha_axis_step": sweep["alpha_axis_step"],
        "baseline_best_grid_point": sweep["baseline_best_grid_point"],
        "prior_summary_rows": sweep["prior_summary_rows"],
        "stability_thresholds": sweep["stability_thresholds"],
        "max_abs_axis_grid_steps": sweep["max_abs_axis_grid_steps"],
        "max_euclidean_grid_steps": sweep["max_euclidean_grid_steps"],
        "max_delta_log_likelihood_best_vs_gr": (
            sweep["max_delta_log_likelihood_best_vs_gr"]
        ),
        "catalog_prior_sensitivity_bounded": (
            sweep["catalog_prior_sensitivity_bounded"]
        ),
        "closure_scope": (
            "Bounded for the declared factorized nuisance-prior catalog on the "
            "v2.122 detector-separable likelihood cube. This does not close "
            "waveform, EFT, or joint-event posterior systematics."
        ),
    }
    packet["label"] = "v2_123_prior_reweight_sweep_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = {
        component: row["status"] for component, row in evidence.items()
    }
    packet["systematics_budget"]["status"] = (
        "bounded"
        if all(row["status"] == "bounded" for row in evidence.values())
        else "open"
    )
    packet["validation_reference"] = "v2.123_alpha_prior_reweight_sweep"
    return packet


def evaluate_alpha_prior_reweight_sweep(
    packet: dict[str, Any],
    sweep: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    return {
        "prior_sensitivity_bounded": sweep["catalog_prior_sensitivity_bounded"],
        "max_abs_axis_grid_steps": sweep["max_abs_axis_grid_steps"],
        "max_delta_log_likelihood_best_vs_gr": (
            sweep["max_delta_log_likelihood_best_vs_gr"]
        ),
        "bounded_components": budget_eval["bounded_components"],
        "open_components": budget_eval["open_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "waveform_and_eft_systematics_still_open",
                "detector_separable_cube_not_joint_event_posterior",
            }
        ),
    }


def canonicalize_json_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, JSON_FLOAT_DIGITS)
    if isinstance(value, list):
        return [canonicalize_json_floats(row) for row in value]
    if isinstance(value, dict):
        return {
            key: canonicalize_json_floats(row)
            for key, row in value.items()
        }
    return value


def diagnose_gw_alpha_prior_reweight_sweep(
    cube_export_path: Path = DEFAULT_CUBE_EXPORT_PATH,
) -> dict[str, Any]:
    cube_result = load_json(cube_export_path)
    sweep = prior_reweight_sweep_from_cube(cube_result)
    packet = packet_with_prior_reweight_sweep(cube_result["packet"], sweep)
    evaluation = evaluate_alpha_prior_reweight_sweep(packet, sweep)
    return {
        "version": VERSION,
        "basis": [
            "v2.122_alpha_likelihood_cube_export",
            "v2.121_alpha_prior_treatment_stress_test",
        ],
        "cube_export_path": cube_export_path.as_posix(),
        "prior_reweight_sweep": sweep,
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "prior_reweight_sweep_bounded_nonclaiming"
            if sweep["catalog_prior_sensitivity_bounded"]
            else "prior_reweight_sweep_open_nonclaiming"
        ),
        "selected_next_build_action": (
            "bound_waveform_and_eft_truncation_systematics"
        ),
        "best_next_artifact": (
            "Attach a source-backed IMR cubic-EFT waveform uncertainty envelope "
            "and alpha-domain EFT truncation bound to the v2.123 packet."
        ),
        "interpretation": (
            "The actual detector alpha/nuisance likelihood cube was reweighted "
            "under the declared nuisance-prior catalog. The best alpha cell "
            "never moves by more than one grid cell per axis and the largest "
            "best-vs-GR log-likelihood preference is below the configured "
            "tolerance, so prior sensitivity is bounded for this catalog. The "
            "route remains nonclaiming because waveform and EFT systematics, "
            "joint-event posterior treatment, likelihood-scale calibration, "
            "and the G8 component are still open."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cube-export", default=str(DEFAULT_CUBE_EXPORT_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.123/"
            "gw_alpha_prior_reweight_sweep.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_prior_reweight_sweep(
        cube_export_path=Path(args.cube_export),
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
