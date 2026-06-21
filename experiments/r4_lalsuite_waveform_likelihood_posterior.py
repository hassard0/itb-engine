"""Coarse R4 waveform-likelihood posterior over GWOSC/LALSuite templates."""

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
from experiments.gw_gr_inspiral_reference_projection import (
    _normalized_complex,
    psd_whitened_reference_context,
)
from experiments.gw_lalsuite_imr_projection import (
    generate_imrphenomd_reference,
    lalsuite_status,
)
from experiments.gw_lalsuite_marginal_alpha_likelihood import (
    logsumexp,
    nuisance_grid,
    rotate_templates_for_tc_phic,
)
from experiments.gw_public_strain_loader import (
    DEFAULT_CACHE_DIR,
    cache_path_for_record,
    ensure_cached_strain_file,
    gw170608_v3_strain_records,
    load_required_32s_strain,
)
from experiments.gw_source_backed_cubic_waveform_response import ETA_REFERENCE
from experiments.gw_source_backed_strain_projection import REFERENCE_TOTAL_MASS_SOLAR
from experiments.gw_strain_alpha_residual_projection import read_strain_values
from experiments.r4_lalsuite_calibrated_gwosc_projection import (
    calibrated_channel_coefficients,
)
from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES
from experiments.r4_nuisance_covariance_export import (
    DEFAULT_CALIBRATED_PROJECTION_PATH,
    load_json,
)
from experiments.r4_source_backed_gwosc_projection import _channel_preview_response
from experiments.r4_source_backed_pn_imr_derivation import (
    ENGINE_AXIS_CHANNEL_WEIGHTS,
    SOURCE_CHANNELS,
    r4_pn_power_law_terms,
)


VERSION = "v2.187"
DEFAULT_NUISANCE_EXPORT_PATH = Path(
    "experiments/results/v2.186/r4_nuisance_covariance_export.json"
)
DEFAULT_OUT = Path(
    "experiments/results/v2.187/"
    "r4_lalsuite_waveform_likelihood_posterior.json"
)
AXES = tuple(RESPONSE_AXES)
GRID_OFFSETS = (-0.04, -0.02, 0.0, 0.02, 0.04)
COARSE_GRID_KIND = "five_point_axis_offsets_around_v2_186_nuisance_mean"
WAVEFORM_LIKELIHOOD_BLOCKERS = (
    "full_r4_modified_imr_merger_ringdown_completion_missing",
    "r4_likelihood_uses_linearized_pn_templates_not_source_owned_waveform",
    "nuisance_grid_is_coarse_not_posterior_sampler",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def _default_32s_records() -> list[dict[str, Any]]:
    return [
        record
        for record in gw170608_v3_strain_records()
        if int(record["duration"]) == 32
    ]


def nuisance_export_central_values(result: dict[str, Any]) -> dict[str, float]:
    export = result["nuisance_covariance_export"]
    values = export["nuisance_marginal_mean"]
    return {axis: float(values[axis]) for axis in AXES}


def r4_coefficient_grid(
    central_values: dict[str, float],
    *,
    offsets: tuple[float, ...] = GRID_OFFSETS,
) -> list[dict[str, float]]:
    if len(offsets) < 3 or 0.0 not in offsets:
        raise ValueError("offsets must contain at least three values and zero")
    rows = []
    for delta_1 in offsets:
        for delta_2 in offsets:
            for delta_3 in offsets:
                deltas = {
                    "g_R4_c1": float(delta_1),
                    "g_R4_c2": float(delta_2),
                    "g_R4_c3": float(delta_3),
                }
                rows.append({
                    **{
                        axis: float(central_values[axis] + deltas[axis])
                        for axis in AXES
                    },
                    "delta_g_R4_c1": deltas["g_R4_c1"],
                    "delta_g_R4_c2": deltas["g_R4_c2"],
                    "delta_g_R4_c3": deltas["g_R4_c3"],
                })
    return canonicalize_json_floats(rows)


def r4_imrphenomd_detector_templates(
    frequencies_hz: np.ndarray,
    v_f: np.ndarray,
    psd: np.ndarray,
    *,
    detector: str,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, Any]:
    waveform = generate_imrphenomd_reference(
        frequencies_hz,
        total_mass_solar=total_mass_solar,
        eta=eta,
    )
    psd_values = np.asarray(psd, dtype=float)
    grid = np.asarray(v_f, dtype=float)
    if psd_values.shape != grid.shape or np.any(psd_values <= 0.0):
        raise ValueError("psd must match v_f and be positive")
    terms = r4_pn_power_law_terms(grid)
    channel_response = calibrated_channel_coefficients(detector)
    raw_templates: dict[str, np.ndarray] = {}
    for axis in AXES:
        response = np.zeros_like(grid)
        for channel in SOURCE_CHANNELS:
            coefficient = (
                float(ENGINE_AXIS_CHANNEL_WEIGHTS[axis][channel])
                * float(channel_response[channel])
            )
            response += coefficient * _channel_preview_response(terms, channel)
        raw_templates[axis] = waveform["h_plus"] * response / np.sqrt(psd_values)
    return {
        "templates": {
            axis: _normalized_complex(template, axis)
            for axis, template in raw_templates.items()
        },
        "waveform_summary": waveform["waveform_summary"],
        "detector_channel_response": channel_response,
        "template_kind": (
            "linearized_r4_pn_imrphenomd_detector_channel_templates"
        ),
    }


def r4_fixed_parameter_log_likelihood(
    data: np.ndarray,
    templates: dict[str, np.ndarray],
    coefficients: dict[str, float],
    *,
    central_values: dict[str, float],
) -> float:
    model = np.zeros_like(np.asarray(data, dtype=complex))
    for axis in AXES:
        delta = float(coefficients[axis] - central_values[axis])
        model += delta * np.asarray(templates[axis], dtype=complex)
    residual = np.asarray(data, dtype=complex) - model
    return -0.5 * float(np.vdot(residual, residual).real)


def detector_nuisance_template_packets(
    strain: np.ndarray,
    *,
    detector: str,
    gps_start: int,
    sample_rate_hz: int,
    event_gps: float | None = None,
) -> list[dict[str, Any]]:
    packets = []
    for nuisance in nuisance_grid():
        context = psd_whitened_reference_context(
            strain,
            gps_start=gps_start,
            sample_rate_hz=sample_rate_hz,
            total_mass_solar=nuisance["total_mass_solar"],
            event_gps=event_gps,
        )
        template_packet = r4_imrphenomd_detector_templates(
            context["frequencies_hz"],
            context["v_f"],
            context["psd_interp"],
            detector=detector,
            total_mass_solar=nuisance["total_mass_solar"],
            eta=nuisance["eta"],
        )
        rotated = rotate_templates_for_tc_phic(
            template_packet["templates"],
            context["frequencies_hz"],
            tc_shift_seconds=nuisance["tc_shift_seconds"],
            phic_rad=nuisance["phic_rad"],
        )
        packets.append({
            "nuisance": nuisance,
            "data": context["normalized_whitened_data"],
            "templates": rotated,
            "frequency_window": context["frequency_window"],
            "waveform_summary": template_packet["waveform_summary"],
            "template_kind": template_packet["template_kind"],
        })
    return packets


def marginalize_r4_grid_from_packets(
    packets: list[dict[str, Any]],
    central_values: dict[str, float],
    *,
    grid: list[dict[str, float]] | None = None,
) -> dict[str, Any]:
    rows = []
    coefficient_rows = (
        r4_coefficient_grid(central_values) if grid is None else grid
    )
    if not packets:
        raise ValueError("packets must not be empty")
    for point in coefficient_rows:
        likelihoods = []
        best_nuisance = None
        best_profile = -math.inf
        for packet in packets:
            value = r4_fixed_parameter_log_likelihood(
                packet["data"],
                packet["templates"],
                point,
                central_values=central_values,
            )
            likelihoods.append(value)
            if value > best_profile:
                best_profile = value
                best_nuisance = packet["nuisance"]
        rows.append({
            **point,
            "log_marginal_likelihood": float(
                logsumexp(likelihoods) - math.log(len(likelihoods))
            ),
            "profile_log_likelihood": float(best_profile),
            "profile_nuisance": best_nuisance,
        })
    return canonicalize_json_floats({
        "grid_points": len(rows),
        "nuisance_points": len(packets),
        "best_marginal_grid_point": max(
            rows,
            key=lambda row: row["log_marginal_likelihood"],
        ),
        "best_profile_grid_point": max(
            rows,
            key=lambda row: row["profile_log_likelihood"],
        ),
        "grid": rows,
    })


def detector_r4_waveform_likelihood(
    record: dict[str, Any],
    cache_dir: Path,
    *,
    central_values: dict[str, float],
    event_gps: float | None = None,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    packets = detector_nuisance_template_packets(
        strain,
        detector=str(record["detector"]),
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
        event_gps=event_gps,
    )
    marginal = marginalize_r4_grid_from_packets(packets, central_values)
    return canonicalize_json_floats({
        "detector": record["detector"],
        "path": cache_path_for_record(record, cache_dir).as_posix(),
        "likelihood_kind": (
            "coarse_nuisance_marginal_linearized_r4_imrphenomd_grid"
        ),
        "template_kind": (
            "linearized_r4_pn_imrphenomd_detector_channel_templates"
        ),
        "nuisance_grid": {
            "nuisance_points": len(packets),
            "grid_is_posterior_sampler": False,
        },
        "coefficient_grid": {
            "axes": list(AXES),
            "grid_kind": COARSE_GRID_KIND,
            "offsets": list(GRID_OFFSETS),
            "grid_points": marginal["grid_points"],
            "central_values": central_values,
        },
        "best_marginal_grid_point": marginal["best_marginal_grid_point"],
        "best_profile_grid_point": marginal["best_profile_grid_point"],
        "grid": marginal["grid"],
        "likelihood_ready": (
            len(packets) == 81
            and marginal["grid_points"] == len(GRID_OFFSETS) ** len(AXES)
            and all(
                math.isfinite(row["log_marginal_likelihood"])
                and math.isfinite(row["profile_log_likelihood"])
                for row in marginal["grid"]
            )
        ),
    })


def posterior_summary_from_grid(
    rows: list[dict[str, float]],
) -> dict[str, Any]:
    log_values = np.asarray(
        [row["log_marginal_likelihood"] for row in rows],
        dtype=float,
    )
    if log_values.size == 0 or not np.all(np.isfinite(log_values)):
        raise ValueError("posterior grid requires finite log likelihoods")
    weights = np.exp(log_values - float(np.max(log_values)))
    weights = weights / float(np.sum(weights))
    points = np.asarray([[row[axis] for axis in AXES] for row in rows], dtype=float)
    mean = weights @ points
    centered = points - mean
    covariance = centered.T @ (centered * weights[:, None])
    enriched_rows = [
        {**row, "posterior_weight": float(weights[index])}
        for index, row in enumerate(rows)
    ]
    best = enriched_rows[int(np.argmax(weights))]
    eigenvalues = np.linalg.eigvalsh(covariance)
    return canonicalize_json_floats({
        "posterior_normalized": True,
        "posterior_weight_sum": float(np.sum(weights)),
        "maximum_posterior_grid_point": best,
        "posterior_mean": {
            axis: float(mean[index]) for index, axis in enumerate(AXES)
        },
        "posterior_covariance": covariance.tolist(),
        "posterior_covariance_eigenvalues": eigenvalues.tolist(),
        "posterior_positive_semidefinite": bool(np.all(eigenvalues >= -1.0e-14)),
        "top_posterior_points": sorted(
            enriched_rows,
            key=lambda row: row["posterior_weight"],
            reverse=True,
        )[:10],
        "grid": enriched_rows,
    })


def network_r4_waveform_likelihood(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    lookups = []
    for row in detector_rows:
        lookup = {
            tuple(grid_row[axis] for axis in AXES): grid_row
            for grid_row in row["grid"]
        }
        lookups.append(lookup)
    coefficient_rows = [
        {axis: float(value) for axis, value in zip(AXES, key, strict=True)}
        for key in lookups[0]
    ]
    network_rows = []
    for point in coefficient_rows:
        key = tuple(point[axis] for axis in AXES)
        log_marginal = sum(
            lookup[key]["log_marginal_likelihood"] for lookup in lookups
        )
        profile = sum(lookup[key]["profile_log_likelihood"] for lookup in lookups)
        network_rows.append({
            **point,
            "delta_g_R4_c1": float(lookups[0][key]["delta_g_R4_c1"]),
            "delta_g_R4_c2": float(lookups[0][key]["delta_g_R4_c2"]),
            "delta_g_R4_c3": float(lookups[0][key]["delta_g_R4_c3"]),
            "log_marginal_likelihood": float(log_marginal),
            "profile_log_likelihood": float(profile),
        })
    posterior = posterior_summary_from_grid(network_rows)
    return canonicalize_json_floats({
        "detectors": [row["detector"] for row in detector_rows],
        "axes": list(AXES),
        "grid_points": len(network_rows),
        "nuisance_points_per_detector": [
            row["nuisance_grid"]["nuisance_points"] for row in detector_rows
        ],
        "likelihood_kind": (
            "network_coarse_nuisance_marginal_linearized_r4_imrphenomd_grid"
        ),
        "best_marginal_grid_point": max(
            network_rows,
            key=lambda row: row["log_marginal_likelihood"],
        ),
        "best_profile_grid_point": max(
            network_rows,
            key=lambda row: row["profile_log_likelihood"],
        ),
        "posterior": posterior,
    })


def evaluate_r4_lalsuite_waveform_likelihood_posterior(
    detector_rows: list[dict[str, Any]],
    network: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers: set[str] = set()
    status = lalsuite_status()
    if not status["available"]:
        blockers.add("lalsuite_not_installed")
    if not status["has_imrphenomd"]:
        blockers.add("lalsuite_imrphenomd_unavailable")
    detectors = sorted(row.get("detector") for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("likelihood_detectors_not_h1_l1")
    if not detector_rows or not all(row.get("likelihood_ready") for row in detector_rows):
        blockers.add("one_or_more_detector_r4_likelihoods_not_ready")
    if network is None or int(network.get("grid_points", 0)) != (
        len(GRID_OFFSETS) ** len(AXES)
    ):
        blockers.add("network_r4_likelihood_grid_missing")
    elif network.get("posterior", {}).get("posterior_normalized") is not True:
        blockers.add("network_r4_posterior_not_normalized")
    elif network.get("posterior", {}).get("posterior_positive_semidefinite") is not True:
        blockers.add("network_r4_posterior_covariance_not_psd")

    claim_blockers = set(WAVEFORM_LIKELIHOOD_BLOCKERS)
    if blockers:
        claim_blockers.add("r4_waveform_likelihood_posterior_not_ready")
    return canonicalize_json_floats({
        "r4_waveform_likelihood_posterior_ready": not blockers,
        "claim_ready": False,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "likelihood_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "lalsuite_status": status,
        "removed_v2_186_blocker": (
            "uniform_grid_covariance_scaffold_not_waveform_likelihood"
            if not blockers else None
        ),
        "remaining_real_reanalysis_blockers": sorted(WAVEFORM_LIKELIHOOD_BLOCKERS),
        "route_status": (
            "r4_lalsuite_waveform_likelihood_posterior_ready_nonclaiming"
            if not blockers
            else "r4_lalsuite_waveform_likelihood_posterior_not_ready"
        ),
    })


def diagnose_r4_lalsuite_waveform_likelihood_posterior(
    *,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    nuisance_export_path: Path = DEFAULT_NUISANCE_EXPORT_PATH,
) -> dict[str, Any]:
    nuisance_result = load_json(nuisance_export_path)
    central_values = nuisance_export_central_values(nuisance_result)
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        evaluation = evaluate_r4_lalsuite_waveform_likelihood_posterior([], None)
        return canonicalize_json_floats({
            "version": VERSION,
            "basis": ["v2.186_r4_nuisance_covariance_export"],
            "cache_dir": Path(cache_dir).as_posix(),
            "nuisance_export_path": Path(nuisance_export_path).as_posix(),
            "central_values": central_values,
            "evaluation": evaluation,
            "claimable_framework_exclusions_now": [],
            "ready_for_framework_claim": False,
            "route_status": evaluation["route_status"],
            "selected_next_build_action": (
                "run_r4_waveform_likelihood_on_vulcan_with_lalsuite"
            ),
        })

    load_summary = load_required_32s_strain(cache_dir)
    detector_rows = [
        detector_r4_waveform_likelihood(
            record,
            cache_dir,
            central_values=central_values,
        )
        for record in _default_32s_records()
    ]
    network = network_r4_waveform_likelihood(detector_rows)
    evaluation = evaluate_r4_lalsuite_waveform_likelihood_posterior(
        detector_rows,
        network,
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.186_r4_nuisance_covariance_export",
            "v2.185_r4_lalsuite_calibrated_gwosc_projection",
            "v2.183_r4_lalsuite_detector_channel_response",
            "v2.180_source_backed_r4_pn_imr_derivation",
            "v2.115_lalsuite_nuisance_grid_convention",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "cache_dir": Path(cache_dir).as_posix(),
        "nuisance_export_path": Path(nuisance_export_path).as_posix(),
        "calibrated_projection_path": DEFAULT_CALIBRATED_PROJECTION_PATH.as_posix(),
        "central_values": central_values,
        "coefficient_grid": {
            "axes": list(AXES),
            "grid_kind": COARSE_GRID_KIND,
            "offsets": list(GRID_OFFSETS),
            "grid_points": len(GRID_OFFSETS) ** len(AXES),
        },
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_likelihoods": detector_rows,
        "network_likelihood": network,
        "evaluation": evaluation,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "replace_linearized_r4_template_grid_with_source_owned_r4_imr_sampler"
        ),
        "best_next_artifact": (
            "Replace this coarse linearized R4 waveform-template posterior with "
            "a source-owned full R4 IMR likelihood or posterior sampler, including "
            "merger-ringdown, calibration priors, EFT systematics, and adversarial "
            "review."
        ),
        "interpretation": (
            "The v2.186 covariance scaffold has been replaced by a coarse "
            "network likelihood/posterior over the R4 axes using real GWOSC "
            "strain, LALSuite IMRPhenomD baselines, calibrated H1/L1 channel "
            "responses, and the established nuisance grid. It remains nonclaiming "
            "because the R4 part is a linearized source-backed PN template bridge, "
            "not a complete source-owned R4 IMR waveform likelihood."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument(
        "--nuisance-export",
        default=str(DEFAULT_NUISANCE_EXPORT_PATH),
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_lalsuite_waveform_likelihood_posterior(
        cache_dir=Path(args.cache_dir),
        nuisance_export_path=Path(args.nuisance_export),
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
