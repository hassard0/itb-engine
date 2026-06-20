"""Optional LALSuite IMRPhenomD projection for v2.113."""

from __future__ import annotations

import argparse
import importlib
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
    amplitude_response_kernels,
    phase_response_kernels,
    validate_eta,
)
from experiments.gw_source_backed_strain_projection import (
    REFERENCE_TOTAL_MASS_SOLAR,
    validate_total_mass_solar,
)
from experiments.gw_strain_alpha_residual_projection import read_strain_values


VERSION = "v2.113"
REFERENCE_DISTANCE_MPC = 400.0


def lalsuite_status() -> dict[str, Any]:
    lal_spec = importlib.util.find_spec("lal")
    lalsim_spec = importlib.util.find_spec("lalsimulation")
    if lal_spec is None or lalsim_spec is None:
        return {
            "available": False,
            "lal_version": None,
            "has_imrphenomd": False,
        }
    lal = importlib.import_module("lal")
    lalsim = importlib.import_module("lalsimulation")
    return {
        "available": True,
        "lal_version": getattr(lal, "__version__", "unknown"),
        "has_imrphenomd": hasattr(lalsim, "IMRPhenomD"),
    }


def component_masses_from_total_eta(
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, float]:
    total = validate_total_mass_solar(total_mass_solar)
    eta_value = validate_eta(eta)
    discriminant = 1.0 - 4.0 * eta_value
    if discriminant < 0.0:
        raise ValueError("eta is outside the two-body physical range")
    root = math.sqrt(discriminant)
    return {
        "mass_1_solar": 0.5 * total * (1.0 + root),
        "mass_2_solar": 0.5 * total * (1.0 - root),
        "total_mass_solar": total,
        "eta": eta_value,
    }


def _uniform_delta_f(frequencies_hz: np.ndarray) -> float:
    frequencies = np.asarray(frequencies_hz, dtype=float)
    if frequencies.ndim != 1 or frequencies.size < 3:
        raise ValueError("frequencies_hz must be a one-dimensional grid")
    steps = np.diff(frequencies)
    delta_f = float(steps[0])
    if not np.allclose(steps, delta_f, rtol=0.0, atol=1.0e-12):
        raise ValueError("frequencies_hz must be uniformly spaced")
    if delta_f <= 0.0:
        raise ValueError("frequency spacing must be positive")
    return delta_f


def generate_imrphenomd_reference(
    frequencies_hz: np.ndarray,
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
    distance_mpc: float = REFERENCE_DISTANCE_MPC,
) -> dict[str, Any]:
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        raise ImportError("LALSuite with IMRPhenomD is not available")
    lal = importlib.import_module("lal")
    lalsim = importlib.import_module("lalsimulation")
    frequencies = np.asarray(frequencies_hz, dtype=float)
    delta_f = _uniform_delta_f(frequencies)
    masses = component_masses_from_total_eta(
        total_mass_solar=total_mass_solar,
        eta=eta,
    )
    hp, _hc = lalsim.SimInspiralChooseFDWaveform(
        masses["mass_1_solar"] * lal.MSUN_SI,
        masses["mass_2_solar"] * lal.MSUN_SI,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        float(distance_mpc) * 1.0e6 * lal.PC_SI,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        delta_f,
        float(frequencies[0]),
        float(frequencies[-1] + delta_f),
        float(frequencies[0]),
        None,
        lalsim.IMRPhenomD,
    )
    series_frequencies = hp.f0 + hp.deltaF * np.arange(hp.data.length)
    indices = np.rint((frequencies - hp.f0) / hp.deltaF).astype(int)
    if np.any(indices < 0) or np.any(indices >= hp.data.length):
        raise ValueError("requested frequencies outside generated waveform")
    selected = hp.data.data[indices]
    if not np.allclose(series_frequencies[indices], frequencies, atol=1.0e-12):
        raise ValueError("generated waveform frequency grid mismatch")
    if not np.any(np.abs(selected) > 0.0):
        raise ValueError("generated IMRPhenomD reference is zero on selected band")
    return {
        "frequencies_hz": frequencies,
        "h_plus": selected,
        "waveform_summary": {
            "approximant": "IMRPhenomD",
            "lal_version": status["lal_version"],
            "delta_f_hz": float(delta_f),
            "frequency_min_hz": float(frequencies[0]),
            "frequency_max_hz": float(frequencies[-1]),
            "distance_mpc": float(distance_mpc),
            **masses,
            "nonzero_bins": int(np.count_nonzero(np.abs(selected) > 0.0)),
            "max_abs_h_plus": float(np.max(np.abs(selected))),
        },
    }


def imrphenomd_source_response_templates(
    frequencies_hz: np.ndarray,
    v_f: np.ndarray,
    psd: np.ndarray,
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
    distance_mpc: float = REFERENCE_DISTANCE_MPC,
) -> dict[str, Any]:
    waveform = generate_imrphenomd_reference(
        frequencies_hz,
        total_mass_solar=total_mass_solar,
        eta=eta,
        distance_mpc=distance_mpc,
    )
    grid = np.asarray(v_f, dtype=float)
    psd_values = np.asarray(psd, dtype=float)
    if psd_values.shape != grid.shape or np.any(psd_values <= 0.0):
        raise ValueError("psd must match v_f and be positive")
    phase = phase_response_kernels(grid, eta)
    amplitude = amplitude_response_kernels(grid, eta)
    h_plus = waveform["h_plus"]
    raw_templates = {
        "alpha_bar_1": h_plus
        * (amplitude["alpha_bar_1"] + 1j * phase["alpha_bar_1"])
        / np.sqrt(psd_values),
        "alpha_bar_2": h_plus
        * (amplitude["alpha_bar_2"] + 1j * phase["alpha_bar_2"])
        / np.sqrt(psd_values),
    }
    return {
        "templates": {
            parameter: _normalized_complex(template, parameter)
            for parameter, template in raw_templates.items()
        },
        "waveform_summary": waveform["waveform_summary"],
    }


def project_lalsuite_imr_response(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
    distance_mpc: float = REFERENCE_DISTANCE_MPC,
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
        distance_mpc=distance_mpc,
    )
    templates = template_packet["templates"]
    data = context["normalized_whitened_data"]
    projections = {}
    for parameter, template in templates.items():
        value = np.vdot(template, data)
        projections[parameter] = {
            "real": float(np.real(value)),
            "imag": float(np.imag(value)),
            "abs": float(abs(value)),
        }
    template_norms = {
        parameter: float(np.linalg.norm(template))
        for parameter, template in templates.items()
    }
    return {
        "source_reference": SOURCE_REFERENCE,
        "projection_kind": "lalsuite_imrphenomd_psd_whitened_source_response",
        "reference_waveform": template_packet["waveform_summary"],
        "frequency_window": context["frequency_window"],
        "event_summary": context["event_summary"],
        "psd_summary": context["psd_summary"],
        "projections": projections,
        "template_norms": template_norms,
        "normalized_data_norm": context["normalized_data_norm"],
        "projection_ready": (
            all(
                math.isfinite(component)
                for row in projections.values()
                for component in row.values()
            )
            and all(abs(norm - 1.0) < 1.0e-12 for norm in template_norms.values())
            and abs(context["normalized_data_norm"] - 1.0) < 1.0e-12
        ),
    }


def load_and_project_detector_record(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    projection = project_lalsuite_imr_response(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "lalsuite_imr_projection": projection,
        "projection_ready": projection["projection_ready"],
    }


def network_lalsuite_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    parameters = sorted(detector_rows[0]["lalsuite_imr_projection"]["projections"])
    summary: dict[str, Any] = {
        "detectors": [row["detector"] for row in detector_rows],
        "parameters": parameters,
    }
    for parameter in parameters:
        abs_values = [
            row["lalsuite_imr_projection"]["projections"][parameter]["abs"]
            for row in detector_rows
        ]
        real_values = [
            row["lalsuite_imr_projection"]["projections"][parameter]["real"]
            for row in detector_rows
        ]
        imag_values = [
            row["lalsuite_imr_projection"]["projections"][parameter]["imag"]
            for row in detector_rows
        ]
        summary[f"{parameter}_abs_mean"] = float(np.mean(abs_values))
        summary[f"{parameter}_abs_detector_spread"] = float(
            max(abs_values) - min(abs_values)
        )
        summary[f"{parameter}_real_mean"] = float(np.mean(real_values))
        summary[f"{parameter}_imag_mean"] = float(np.mean(imag_values))
    return summary


def evaluate_lalsuite_imr_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers: set[str] = set()
    status = lalsuite_status()
    if not status["available"]:
        blockers.add("lalsuite_not_installed")
    if not status["has_imrphenomd"]:
        blockers.add("lalsuite_imrphenomd_unavailable")
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row["projection_ready"] for row in detector_rows):
        blockers.add("one_or_more_lalsuite_imr_projections_not_ready")
    for row in detector_rows:
        projection = row.get("lalsuite_imr_projection", {})
        if projection.get("source_reference") != SOURCE_REFERENCE:
            blockers.add("source_reference_missing_or_unexpected")
        if projection.get("projection_kind") != (
            "lalsuite_imrphenomd_psd_whitened_source_response"
        ):
            blockers.add("projection_kind_unexpected")
        reference = projection.get("reference_waveform", {})
        if reference.get("approximant") != "IMRPhenomD":
            blockers.add("imrphenomd_reference_missing")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "event_mass_eta_tc_phic_not_sampled",
            "detector_calibration_uncertainty_missing",
            "alpha_likelihood_grid_not_sampled",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )
    return {
        "lalsuite_imr_projection_ready": not blockers,
        "claim_ready": False,
        "projection_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "lalsuite_status": status,
        "removed_v2_112_blocker": (
            "leading_order_gr_reference_not_full_imr" if not blockers else None
        ),
    }


def diagnose_gw_lalsuite_imr_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        return {
            "version": VERSION,
            "basis": ["v2.112_gr_inspiral_reference_projection"],
            "source_reference": SOURCE_REFERENCE,
            "cache_dir": str(cache_dir),
            "evaluation": {
                "lalsuite_imr_projection_ready": False,
                "claim_ready": False,
                "projection_blockers": [
                    "lalsuite_not_installed"
                    if not status["available"]
                    else "lalsuite_imrphenomd_unavailable"
                ],
                "claim_blockers": [
                    "lalsuite_imr_projection_not_ready",
                    "g8_joint_component_missing",
                ],
                "lalsuite_status": status,
                "removed_v2_112_blocker": None,
            },
            "claimable_discriminator_now": False,
            "route_status": "lalsuite_imrphenomd_projection_not_ready",
            "selected_next_build_action": "install_lalsuite_optional_gw_dependency",
        }

    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_and_project_detector_record(record, cache_dir) for record in records
    ]
    evaluation = evaluate_lalsuite_imr_projection(detector_rows)
    return {
        "version": VERSION,
        "basis": [
            "v2.112_gr_inspiral_reference_projection",
            "LALSuite_IMRPhenomD_frequency_domain_waveform",
            "v2.109_source_backed_cubic_inspiral_response",
        ],
        "source_reference": SOURCE_REFERENCE,
        "cache_dir": str(cache_dir),
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_projections": detector_rows,
        "network_projection": network_lalsuite_projection(detector_rows),
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "lalsuite_imrphenomd_source_projection_ready_nonclaiming"
            if evaluation["lalsuite_imr_projection_ready"]
            else "lalsuite_imrphenomd_projection_not_ready"
        ),
        "selected_next_build_action": (
            "sample_alpha_bar_likelihood_grid_with_imr_templates"
        ),
        "best_next_artifact": (
            "Promote the IMRPhenomD projection into a small alpha_bar grid "
            "likelihood over mass, eta, tc, and phic, then export a v2.102 "
            "source-native packet."
        ),
        "interpretation": (
            "The leading-order GR reference is replaced by a LALSuite "
            "IMRPhenomD baseline. This removes the full-IMR reference blocker "
            "for the projection layer, but the result is still not a likelihood "
            "because event parameters and alpha_bar are not sampled."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.113/gw_lalsuite_imr_projection.json",
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_lalsuite_imr_projection(Path(args.cache_dir))
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
