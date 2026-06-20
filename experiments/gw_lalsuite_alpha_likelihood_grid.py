"""Fixed-parameter LALSuite alpha-bar likelihood grid for v2.114."""

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
    psd_whitened_reference_context,
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
from experiments.gw_source_backed_cubic_waveform_response import (
    ETA_REFERENCE,
    SOURCE_REFERENCE,
)
from experiments.gw_source_backed_strain_projection import (
    REFERENCE_TOTAL_MASS_SOLAR,
)
from experiments.gw_strain_alpha_residual_projection import read_strain_values


VERSION = "v2.114"
GRID_HALF_WIDTH = 2.0
GRID_POINTS_PER_AXIS = 21


def alpha_grid(
    *,
    half_width: float = GRID_HALF_WIDTH,
    points_per_axis: int = GRID_POINTS_PER_AXIS,
) -> list[dict[str, float]]:
    if points_per_axis < 3:
        raise ValueError("points_per_axis must be at least 3")
    if not math.isfinite(float(half_width)) or half_width <= 0.0:
        raise ValueError("half_width must be positive and finite")
    axis = np.linspace(-float(half_width), float(half_width), points_per_axis)
    return [
        {"alpha_bar_1": float(alpha_1), "alpha_bar_2": float(alpha_2)}
        for alpha_1 in axis
        for alpha_2 in axis
    ]


def real_alpha_least_squares(
    data: np.ndarray,
    templates: dict[str, np.ndarray],
) -> dict[str, float]:
    alpha_1 = np.asarray(templates["alpha_bar_1"], dtype=complex)
    alpha_2 = np.asarray(templates["alpha_bar_2"], dtype=complex)
    target = np.asarray(data, dtype=complex)
    design_complex = np.column_stack([alpha_1, alpha_2])
    design = np.vstack([design_complex.real, design_complex.imag])
    observed = np.concatenate([target.real, target.imag])
    solution, *_ = np.linalg.lstsq(design, observed, rcond=None)
    return {
        "alpha_bar_1_hat": float(solution[0]),
        "alpha_bar_2_hat": float(solution[1]),
    }


def fixed_parameter_log_likelihood(
    data: np.ndarray,
    templates: dict[str, np.ndarray],
    *,
    alpha_bar_1: float,
    alpha_bar_2: float,
) -> float:
    model = (
        float(alpha_bar_1) * np.asarray(templates["alpha_bar_1"], dtype=complex)
        + float(alpha_bar_2) * np.asarray(templates["alpha_bar_2"], dtype=complex)
    )
    residual = np.asarray(data, dtype=complex) - model
    return -0.5 * float(np.vdot(residual, residual).real)


def detector_alpha_likelihood_grid(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, Any]:
    context = psd_whitened_reference_context(
        strain,
        gps_start=gps_start,
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    template_packet = imrphenomd_source_response_templates(
        context["frequencies_hz"],
        context["v_f"],
        context["psd_interp"],
        total_mass_solar=total_mass_solar,
        eta=eta,
    )
    templates = template_packet["templates"]
    data = context["normalized_whitened_data"]
    rows = []
    for point in alpha_grid():
        rows.append(
            {
                **point,
                "log_likelihood": fixed_parameter_log_likelihood(
                    data,
                    templates,
                    alpha_bar_1=point["alpha_bar_1"],
                    alpha_bar_2=point["alpha_bar_2"],
                ),
            }
        )
    best = max(rows, key=lambda row: row["log_likelihood"])
    center = fixed_parameter_log_likelihood(
        data,
        templates,
        alpha_bar_1=0.0,
        alpha_bar_2=0.0,
    )
    return {
        "source_reference": SOURCE_REFERENCE,
        "likelihood_kind": (
            "fixed_event_parameter_lalsuite_imrphenomd_alpha_grid"
        ),
        "grid_points": len(rows),
        "grid_half_width": GRID_HALF_WIDTH,
        "best_grid_point": best,
        "zero_alpha_log_likelihood": center,
        "least_squares_alpha_hat": real_alpha_least_squares(data, templates),
        "waveform_summary": template_packet["waveform_summary"],
        "frequency_window": context["frequency_window"],
        "event_summary": context["event_summary"],
        "psd_summary": context["psd_summary"],
        "grid": rows,
        "likelihood_ready": (
            len(rows) == GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
            and all(math.isfinite(row["log_likelihood"]) for row in rows)
            and math.isfinite(best["log_likelihood"])
        ),
    }


def load_detector_alpha_likelihood_grid(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    likelihood = detector_alpha_likelihood_grid(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "alpha_likelihood": likelihood,
        "likelihood_ready": likelihood["likelihood_ready"],
    }


def network_alpha_likelihood(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    grid = alpha_grid()
    network_rows = []
    for point in grid:
        total = 0.0
        for row in detector_rows:
            detector_grid = row["alpha_likelihood"]["grid"]
            match = next(
                grid_row
                for grid_row in detector_grid
                if grid_row["alpha_bar_1"] == point["alpha_bar_1"]
                and grid_row["alpha_bar_2"] == point["alpha_bar_2"]
            )
            total += match["log_likelihood"]
        network_rows.append({**point, "log_likelihood": float(total)})
    best = max(network_rows, key=lambda row: row["log_likelihood"])
    return {
        "detectors": [row["detector"] for row in detector_rows],
        "grid_points": len(network_rows),
        "best_grid_point": best,
        "grid": network_rows,
    }


def evaluate_lalsuite_alpha_likelihood_grid(
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
        blockers.add("one_or_more_detector_likelihoods_not_ready")
    if network is None or int(network.get("grid_points", 0)) != (
        GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
    ):
        blockers.add("network_likelihood_grid_missing")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "event_mass_eta_tc_phic_fixed_not_marginalized",
            "detector_calibration_uncertainty_missing",
            "likelihood_scale_not_calibrated_to_noise_evidence",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )
    return {
        "fixed_alpha_likelihood_grid_ready": not blockers,
        "claim_ready": False,
        "likelihood_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "lalsuite_status": status,
        "removed_v2_113_blocker": (
            "alpha_likelihood_grid_not_sampled" if not blockers else None
        ),
    }


def diagnose_gw_lalsuite_alpha_likelihood_grid(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        return {
            "version": VERSION,
            "basis": ["v2.113_lalsuite_imrphenomd_projection"],
            "source_reference": SOURCE_REFERENCE,
            "cache_dir": str(cache_dir),
            "evaluation": {
                "fixed_alpha_likelihood_grid_ready": False,
                "claim_ready": False,
                "likelihood_blockers": [
                    "lalsuite_not_installed"
                    if not status["available"]
                    else "lalsuite_imrphenomd_unavailable"
                ],
                "claim_blockers": [
                    "fixed_alpha_likelihood_grid_not_ready",
                    "g8_joint_component_missing",
                ],
                "lalsuite_status": status,
                "removed_v2_113_blocker": None,
            },
            "claimable_discriminator_now": False,
            "route_status": "lalsuite_alpha_likelihood_grid_not_ready",
            "selected_next_build_action": "install_lalsuite_optional_gw_dependency",
        }

    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_detector_alpha_likelihood_grid(record, cache_dir) for record in records
    ]
    network = network_alpha_likelihood(detector_rows)
    evaluation = evaluate_lalsuite_alpha_likelihood_grid(detector_rows, network)
    return {
        "version": VERSION,
        "basis": [
            "v2.113_lalsuite_imrphenomd_projection",
            "v2.102_source_native_alpha_adapter",
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
            "fixed_parameter_lalsuite_alpha_likelihood_ready_nonclaiming"
            if evaluation["fixed_alpha_likelihood_grid_ready"]
            else "lalsuite_alpha_likelihood_grid_not_ready"
        ),
        "selected_next_build_action": (
            "marginalize_lalsuite_alpha_likelihood_over_event_parameters"
        ),
        "best_next_artifact": (
            "Turn the fixed alpha grid into a marginal likelihood over mass, "
            "eta, tc, phic, and calibration nuisance parameters, then export a "
            "v2.102 source-native packet."
        ),
        "interpretation": (
            "The IMRPhenomD projection is promoted into a fixed-event-parameter "
            "two-dimensional alpha_bar likelihood grid. It remains nonclaiming "
            "because the likelihood scale is diagnostic and event/systematic "
            "parameters are not marginalized."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.114/"
            "gw_lalsuite_alpha_likelihood_grid.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_lalsuite_alpha_likelihood_grid(Path(args.cache_dir))
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
