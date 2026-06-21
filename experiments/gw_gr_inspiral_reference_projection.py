"""Leading-order GR inspiral reference projection for v2.112."""

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
from experiments.gw_psd_whitened_complex_projection import (
    event_tapered_segment,
    welch_psd_estimate,
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
    source_inspiral_frequency_window,
    validate_total_mass_solar,
)
from experiments.gw_strain_alpha_residual_projection import read_strain_values


VERSION = "v2.112"


def chirp_mass_solar(
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> float:
    mass = validate_total_mass_solar(total_mass_solar)
    eta_value = validate_eta(eta)
    return float(mass * eta_value ** (3.0 / 5.0))


def leading_order_gr_inspiral_reference(
    frequencies_hz: np.ndarray,
    v_f: np.ndarray,
    *,
    eta: float = ETA_REFERENCE,
) -> np.ndarray:
    eta_value = validate_eta(eta)
    frequencies = np.asarray(frequencies_hz, dtype=float)
    grid = np.asarray(v_f, dtype=float)
    if frequencies.shape != grid.shape:
        raise ValueError("frequencies_hz and v_f must have matching shapes")
    if np.any(frequencies <= 0.0) or np.any(grid <= 0.0):
        raise ValueError("frequencies_hz and v_f must be positive")
    amplitude = frequencies ** (-7.0 / 6.0)
    phase = 3.0 / (128.0 * eta_value) * grid ** (-5.0)
    return amplitude * np.exp(1j * phase)


def _normalized_complex(values: np.ndarray, label: str) -> np.ndarray:
    vector = np.asarray(values, dtype=complex)
    if vector.ndim != 1 or vector.size < 3:
        raise ValueError(f"{label} must be a one-dimensional complex vector")
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError(f"{label} cannot be normalized")
    return vector / norm


def psd_whitened_reference_context(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    event_gps: float | None = None,
) -> dict[str, Any]:
    event = event_tapered_segment(
        strain,
        gps_start=gps_start,
        sample_rate_hz=sample_rate_hz,
        event_gps=event_gps,
    )
    psd = welch_psd_estimate(
        strain,
        sample_rate_hz=sample_rate_hz,
        exclude_slice=event["selection"],
    )
    window = source_inspiral_frequency_window(
        event["sample_count"],
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    event_frequencies = np.fft.rfftfreq(
        event["sample_count"],
        d=1.0 / float(sample_rate_hz),
    )
    selected = np.isin(event_frequencies, window["frequencies_hz"])
    psd_interp = np.interp(
        window["frequencies_hz"],
        psd["frequencies_hz"],
        psd["psd"],
    )
    event_fft = np.fft.rfft(event["tapered"])[selected]
    whitened_data = event_fft / np.sqrt(psd_interp)
    normalized_data = _normalized_complex(whitened_data, "whitened_data")
    return {
        "frequencies_hz": window["frequencies_hz"],
        "v_f": window["v_f"],
        "psd_interp": psd_interp,
        "normalized_whitened_data": normalized_data,
        "frequency_window": {
            key: value
            for key, value in window.items()
            if key not in {"frequencies_hz", "v_f"}
        },
        "event_summary": {
            key: value for key, value in event.items() if key not in {"tapered", "selection"}
        },
        "psd_summary": {
            key: value
            for key, value in psd.items()
            if key not in {"frequencies_hz", "psd", "used_starts"}
        },
        "normalized_data_norm": float(np.linalg.norm(normalized_data)),
    }


def gr_inspiral_source_response_templates(
    frequencies_hz: np.ndarray,
    v_f: np.ndarray,
    psd: np.ndarray,
    *,
    eta: float = ETA_REFERENCE,
) -> dict[str, np.ndarray]:
    eta_value = validate_eta(eta)
    grid = np.asarray(v_f, dtype=float)
    psd_values = np.asarray(psd, dtype=float)
    if psd_values.shape != grid.shape or np.any(psd_values <= 0.0):
        raise ValueError("psd must match v_f and be positive")
    gr_reference = leading_order_gr_inspiral_reference(
        frequencies_hz,
        grid,
        eta=eta_value,
    )
    phase = phase_response_kernels(grid, eta_value)
    amplitude = amplitude_response_kernels(grid, eta_value)
    raw_templates = {
        "alpha_bar_1": gr_reference
        * (amplitude["alpha_bar_1"] + 1j * phase["alpha_bar_1"])
        / np.sqrt(psd_values),
        "alpha_bar_2": gr_reference
        * (amplitude["alpha_bar_2"] + 1j * phase["alpha_bar_2"])
        / np.sqrt(psd_values),
    }
    return {
        parameter: _normalized_complex(template, parameter)
        for parameter, template in raw_templates.items()
    }


def project_gr_inspiral_reference_response(
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
    templates = gr_inspiral_source_response_templates(
        context["frequencies_hz"],
        context["v_f"],
        context["psd_interp"],
        eta=eta,
    )
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
        "projection_kind": (
            "psd_whitened_leading_order_gr_inspiral_response"
        ),
        "reference_waveform": {
            "kind": "leading_order_stationary_phase_gr_inspiral",
            "total_mass_solar": float(total_mass_solar),
            "eta": float(eta),
            "chirp_mass_solar": chirp_mass_solar(
                total_mass_solar=total_mass_solar,
                eta=eta,
            ),
            "tc_phic_fixed_to_zero": True,
        },
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
    projection = project_gr_inspiral_reference_response(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "gr_inspiral_projection": projection,
        "projection_ready": projection["projection_ready"],
    }


def network_gr_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    parameters = sorted(detector_rows[0]["gr_inspiral_projection"]["projections"])
    summary: dict[str, Any] = {
        "detectors": [row["detector"] for row in detector_rows],
        "parameters": parameters,
    }
    for parameter in parameters:
        abs_values = [
            row["gr_inspiral_projection"]["projections"][parameter]["abs"]
            for row in detector_rows
        ]
        real_values = [
            row["gr_inspiral_projection"]["projections"][parameter]["real"]
            for row in detector_rows
        ]
        imag_values = [
            row["gr_inspiral_projection"]["projections"][parameter]["imag"]
            for row in detector_rows
        ]
        summary[f"{parameter}_abs_mean"] = float(np.mean(abs_values))
        summary[f"{parameter}_abs_detector_spread"] = float(
            max(abs_values) - min(abs_values)
        )
        summary[f"{parameter}_real_mean"] = float(np.mean(real_values))
        summary[f"{parameter}_imag_mean"] = float(np.mean(imag_values))
    return summary


def evaluate_gr_inspiral_reference_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers: set[str] = set()
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row["projection_ready"] for row in detector_rows):
        blockers.add("one_or_more_gr_reference_projections_not_ready")
    for row in detector_rows:
        projection = row.get("gr_inspiral_projection", {})
        if projection.get("source_reference") != SOURCE_REFERENCE:
            blockers.add("source_reference_missing_or_unexpected")
        if projection.get("projection_kind") != (
            "psd_whitened_leading_order_gr_inspiral_response"
        ):
            blockers.add("projection_kind_unexpected")
        reference = projection.get("reference_waveform", {})
        if reference.get("kind") != "leading_order_stationary_phase_gr_inspiral":
            blockers.add("gr_reference_waveform_missing")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "leading_order_gr_reference_not_full_imr",
            "tc_phic_not_sampled",
            "detector_calibration_uncertainty_missing",
            "event_mass_eta_posterior_sampling_missing",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )
    return {
        "gr_inspiral_reference_projection_ready": not blockers,
        "claim_ready": False,
        "projection_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "removed_v2_111_blocker": (
            "unit_gr_reference_not_physical_waveform" if not blockers else None
        ),
    }


def diagnose_gw_gr_inspiral_reference_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_and_project_detector_record(record, cache_dir) for record in records
    ]
    evaluation = evaluate_gr_inspiral_reference_projection(detector_rows)
    return {
        "version": VERSION,
        "basis": [
            "v2.111_psd_whitened_complex_source_projection",
            "v2.109_source_backed_cubic_inspiral_response",
            "leading_order_GR_stationary_phase_inspiral_reference",
        ],
        "source_reference": SOURCE_REFERENCE,
        "cache_dir": str(cache_dir),
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_projections": detector_rows,
        "network_projection": network_gr_projection(detector_rows),
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "leading_order_gr_inspiral_reference_projection_ready_nonclaiming"
            if evaluation["gr_inspiral_reference_projection_ready"]
            else "leading_order_gr_inspiral_reference_projection_not_ready"
        ),
        "selected_next_build_action": (
            "replace_leading_order_reference_with_lalsuite_imr_waveform"
        ),
        "best_next_artifact": (
            "Use an IMR waveform implementation or source release waveform code "
            "for the GR baseline, then sample tc, phic, mass, eta, and alpha_bar "
            "to export a source-native likelihood packet."
        ),
        "interpretation": (
            "The v2.111 unit complex reference is replaced with a physical "
            "leading-order GR stationary-phase inspiral reference. This is still "
            "not a claim-ready likelihood because it is not a calibrated full "
            "IMR waveform and does not sample event parameters or systematics."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.112/"
            "gw_gr_inspiral_reference_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_gr_inspiral_reference_projection(Path(args.cache_dir))
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
