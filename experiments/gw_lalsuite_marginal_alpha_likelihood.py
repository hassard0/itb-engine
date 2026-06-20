"""Nuisance-marginalized LALSuite alpha likelihood for v2.115."""

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
from experiments.gw_gr_inspiral_reference_projection import (
    _normalized_complex,
    psd_whitened_reference_context,
)
from experiments.gw_lalsuite_alpha_likelihood_grid import (
    GRID_POINTS_PER_AXIS,
    alpha_grid,
    fixed_parameter_log_likelihood,
)
from experiments.gw_lalsuite_imr_projection import (
    imrphenomd_source_response_templates,
    lalsuite_status,
)
from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_public_strain_loader import (
    DEFAULT_CACHE_DIR,
    cache_path_for_record,
    ensure_cached_strain_file,
    gw170608_v3_strain_records,
    load_required_32s_strain,
)
from experiments.gw_source_backed_cubic_waveform_response import SOURCE_REFERENCE
from experiments.gw_strain_alpha_residual_projection import read_strain_values


VERSION = "v2.115"
TOTAL_MASS_GRID_SOLAR = (18.0, 19.0, 20.0)
ETA_GRID = (0.20, 0.22, 0.24)
TC_SHIFT_SECONDS_GRID = (-0.002, 0.0, 0.002)
PHIC_RAD_GRID = (-math.pi / 4.0, 0.0, math.pi / 4.0)


def nuisance_grid(
    *,
    total_masses_solar: tuple[float, ...] = TOTAL_MASS_GRID_SOLAR,
    etas: tuple[float, ...] = ETA_GRID,
    tc_shifts_seconds: tuple[float, ...] = TC_SHIFT_SECONDS_GRID,
    phic_radians: tuple[float, ...] = PHIC_RAD_GRID,
) -> list[dict[str, float]]:
    rows = []
    for total_mass_solar in total_masses_solar:
        for eta in etas:
            for tc_shift_seconds in tc_shifts_seconds:
                for phic_rad in phic_radians:
                    rows.append(
                        {
                            "total_mass_solar": float(total_mass_solar),
                            "eta": float(eta),
                            "tc_shift_seconds": float(tc_shift_seconds),
                            "phic_rad": float(phic_rad),
                        }
                    )
    if not rows:
        raise ValueError("nuisance grid is empty")
    return rows


def logsumexp(values: list[float] | np.ndarray) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("logsumexp requires finite values")
    maximum = float(np.max(array))
    return maximum + math.log(float(np.sum(np.exp(array - maximum))))


def rotate_templates_for_tc_phic(
    templates: dict[str, np.ndarray],
    frequencies_hz: np.ndarray,
    *,
    tc_shift_seconds: float,
    phic_rad: float,
) -> dict[str, np.ndarray]:
    frequencies = np.asarray(frequencies_hz, dtype=float)
    rotation = np.exp(
        1j * (float(phic_rad) - 2.0 * np.pi * frequencies * float(tc_shift_seconds))
    )
    return {
        parameter: _normalized_complex(np.asarray(template) * rotation, parameter)
        for parameter, template in templates.items()
    }


def marginalize_alpha_grid_from_packets(
    packets: list[dict[str, Any]],
    *,
    grid: list[dict[str, float]] | None = None,
) -> dict[str, Any]:
    alpha_rows = alpha_grid() if grid is None else grid
    if not packets:
        raise ValueError("packets must not be empty")
    rows = []
    for point in alpha_rows:
        likelihoods = []
        best_nuisance = None
        best_profile = -math.inf
        for packet in packets:
            log_likelihood = fixed_parameter_log_likelihood(
                packet["data"],
                packet["templates"],
                alpha_bar_1=point["alpha_bar_1"],
                alpha_bar_2=point["alpha_bar_2"],
            )
            likelihoods.append(log_likelihood)
            if log_likelihood > best_profile:
                best_profile = log_likelihood
                best_nuisance = packet["nuisance"]
        log_marginal = logsumexp(likelihoods) - math.log(len(likelihoods))
        rows.append(
            {
                **point,
                "log_marginal_likelihood": float(log_marginal),
                "profile_log_likelihood": float(best_profile),
                "profile_nuisance": best_nuisance,
            }
        )
    best = max(rows, key=lambda row: row["log_marginal_likelihood"])
    profile_best = max(rows, key=lambda row: row["profile_log_likelihood"])
    return {
        "grid_points": len(rows),
        "nuisance_points": len(packets),
        "best_marginal_grid_point": best,
        "best_profile_grid_point": profile_best,
        "grid": rows,
    }


def detector_nuisance_template_packets(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
) -> list[dict[str, Any]]:
    packets = []
    for nuisance in nuisance_grid():
        context = psd_whitened_reference_context(
            strain,
            gps_start=gps_start,
            sample_rate_hz=sample_rate_hz,
            total_mass_solar=nuisance["total_mass_solar"],
        )
        template_packet = imrphenomd_source_response_templates(
            context["frequencies_hz"],
            context["v_f"],
            context["psd_interp"],
            total_mass_solar=nuisance["total_mass_solar"],
            eta=nuisance["eta"],
        )
        templates = rotate_templates_for_tc_phic(
            template_packet["templates"],
            context["frequencies_hz"],
            tc_shift_seconds=nuisance["tc_shift_seconds"],
            phic_rad=nuisance["phic_rad"],
        )
        packets.append(
            {
                "nuisance": nuisance,
                "data": context["normalized_whitened_data"],
                "templates": templates,
                "waveform_summary": template_packet["waveform_summary"],
                "frequency_window": context["frequency_window"],
            }
        )
    return packets


def detector_marginal_alpha_likelihood(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    packets = detector_nuisance_template_packets(
        strain,
        gps_start=gps_start,
        sample_rate_hz=sample_rate_hz,
    )
    marginal = marginalize_alpha_grid_from_packets(packets)
    return {
        "source_reference": SOURCE_REFERENCE,
        "likelihood_kind": (
            "nuisance_marginal_lalsuite_imrphenomd_alpha_grid"
        ),
        "nuisance_grid": {
            "total_masses_solar": list(TOTAL_MASS_GRID_SOLAR),
            "etas": list(ETA_GRID),
            "tc_shifts_seconds": list(TC_SHIFT_SECONDS_GRID),
            "phic_radians": list(PHIC_RAD_GRID),
            "nuisance_points": len(packets),
        },
        "alpha_grid": {
            "points_per_axis": GRID_POINTS_PER_AXIS,
            "grid_points": marginal["grid_points"],
        },
        "waveform_reference": {
            "approximant": "IMRPhenomD",
            "nuisance_waveform_count": len(packets),
        },
        "best_marginal_grid_point": marginal["best_marginal_grid_point"],
        "best_profile_grid_point": marginal["best_profile_grid_point"],
        "grid": marginal["grid"],
        "likelihood_ready": (
            len(packets) == 81
            and marginal["grid_points"] == GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
            and all(
                math.isfinite(row["log_marginal_likelihood"])
                and math.isfinite(row["profile_log_likelihood"])
                for row in marginal["grid"]
            )
        ),
    }


def load_detector_marginal_alpha_likelihood(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    likelihood = detector_marginal_alpha_likelihood(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "marginal_alpha_likelihood": likelihood,
        "likelihood_ready": likelihood["likelihood_ready"],
    }


def network_marginal_alpha_likelihood(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    rows_by_detector = []
    for row in detector_rows:
        lookup = {
            (grid_row["alpha_bar_1"], grid_row["alpha_bar_2"]): grid_row
            for grid_row in row["marginal_alpha_likelihood"]["grid"]
        }
        rows_by_detector.append(lookup)

    network_rows = []
    for point in alpha_grid():
        key = (point["alpha_bar_1"], point["alpha_bar_2"])
        log_marginal = sum(
            lookup[key]["log_marginal_likelihood"] for lookup in rows_by_detector
        )
        profile = sum(
            lookup[key]["profile_log_likelihood"] for lookup in rows_by_detector
        )
        network_rows.append(
            {
                **point,
                "log_marginal_likelihood": float(log_marginal),
                "profile_log_likelihood": float(profile),
            }
        )
    return {
        "detectors": [row["detector"] for row in detector_rows],
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


def evaluate_lalsuite_marginal_alpha_likelihood(
    detector_rows: list[dict[str, Any]],
    network: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers: set[str] = set()
    status = lalsuite_status()
    if not status["available"]:
        blockers.add("lalsuite_not_installed")
    if not status["has_imrphenomd"]:
        blockers.add("lalsuite_imrphenomd_unavailable")
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("likelihood_detectors_not_h1_l1")
    if not detector_rows or not all(row["likelihood_ready"] for row in detector_rows):
        blockers.add("one_or_more_detector_marginals_not_ready")
    if network is None or int(network.get("grid_points", 0)) != (
        GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
    ):
        blockers.add("network_marginal_likelihood_grid_missing")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "detector_calibration_uncertainty_missing",
            "likelihood_scale_not_calibrated_to_noise_evidence",
            "nuisance_grid_is_coarse_not_posterior_sampler",
            "systematics_budget_missing",
            "source_native_packet_not_exported",
            "g8_joint_component_missing",
        }
    )
    return {
        "marginal_alpha_likelihood_ready": not blockers,
        "claim_ready": False,
        "likelihood_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "lalsuite_status": status,
        "removed_v2_114_blocker": (
            "event_mass_eta_tc_phic_fixed_not_marginalized"
            if not blockers
            else None
        ),
    }


def diagnose_gw_lalsuite_marginal_alpha_likelihood(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        return {
            "version": VERSION,
            "basis": ["v2.114_lalsuite_alpha_likelihood_grid"],
            "source_reference": SOURCE_REFERENCE,
            "cache_dir": str(cache_dir),
            "evaluation": {
                "marginal_alpha_likelihood_ready": False,
                "claim_ready": False,
                "likelihood_blockers": [
                    "lalsuite_not_installed"
                    if not status["available"]
                    else "lalsuite_imrphenomd_unavailable"
                ],
                "claim_blockers": [
                    "marginal_alpha_likelihood_not_ready",
                    "g8_joint_component_missing",
                ],
                "lalsuite_status": status,
                "removed_v2_114_blocker": None,
            },
            "claimable_discriminator_now": False,
            "route_status": "lalsuite_marginal_alpha_likelihood_not_ready",
            "selected_next_build_action": "install_lalsuite_optional_gw_dependency",
        }

    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_detector_marginal_alpha_likelihood(record, cache_dir)
        for record in records
    ]
    network = network_marginal_alpha_likelihood(detector_rows)
    evaluation = evaluate_lalsuite_marginal_alpha_likelihood(detector_rows, network)
    return {
        "version": VERSION,
        "basis": [
            "v2.114_fixed_parameter_lalsuite_alpha_grid",
            "v2.113_lalsuite_imrphenomd_projection",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "source_reference": SOURCE_REFERENCE,
        "cache_dir": str(cache_dir),
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_likelihoods": detector_rows,
        "network_likelihood": network,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "nuisance_marginal_lalsuite_alpha_likelihood_ready_nonclaiming"
            if evaluation["marginal_alpha_likelihood_ready"]
            else "lalsuite_marginal_alpha_likelihood_not_ready"
        ),
        "selected_next_build_action": "export_marginal_alpha_likelihood_packet",
        "best_next_artifact": (
            "Compress the nuisance-marginal grid into a v2.102 source-native "
            "alpha_bar packet with covariance, reproducibility metadata, and an "
            "explicit systematics budget."
        ),
        "interpretation": (
            "The fixed-event-parameter alpha grid is upgraded to a coarse "
            "nuisance-marginal likelihood over total mass, eta, coalescence "
            "time, and phase. It remains nonclaiming because the nuisance grid "
            "is not a posterior sampler, calibration/systematics are absent, "
            "and no v2.102 packet has been exported."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.115/"
            "gw_lalsuite_marginal_alpha_likelihood.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_lalsuite_marginal_alpha_likelihood(Path(args.cache_dir))
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
