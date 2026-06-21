"""PSD-whitened complex source-response projection for v2.111."""

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
)
from experiments.gw_strain_alpha_residual_projection import (
    event_centered_slice,
    read_strain_values,
)


VERSION = "v2.111"
PSD_SEGMENT_SECONDS = 4.0
PSD_OVERLAP_FRACTION = 0.5


def _overlaps(left: slice, right: slice) -> bool:
    left_start = int(left.start or 0)
    left_stop = int(left.stop or left_start)
    right_start = int(right.start or 0)
    right_stop = int(right.stop or right_start)
    return left_start < right_stop and right_start < left_stop


def event_tapered_segment(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    event_gps: float | None = None,
) -> dict[str, Any]:
    gps_kwargs = {} if event_gps is None else {"event_gps": event_gps}
    selection = event_centered_slice(
        gps_start=gps_start,
        sample_count=int(np.asarray(strain).size),
        sample_rate_hz=sample_rate_hz,
        **gps_kwargs,
    )
    raw = np.asarray(strain[selection], dtype=float)
    demeaned = raw - float(np.mean(raw))
    tapered = demeaned * np.hanning(raw.size)
    return {
        "tapered": tapered,
        "selection": selection,
        "start_index": int(selection.start or 0),
        "stop_index": int(selection.stop or 0),
        "sample_count": int(tapered.size),
        "raw_mean": float(np.mean(raw)),
        "raw_rms": float(np.sqrt(np.mean(raw * raw))),
        "tapered_rms": float(np.sqrt(np.mean(tapered * tapered))),
    }


def welch_psd_estimate(
    strain: np.ndarray,
    *,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    segment_seconds: float = PSD_SEGMENT_SECONDS,
    overlap_fraction: float = PSD_OVERLAP_FRACTION,
    exclude_slice: slice | None = None,
) -> dict[str, Any]:
    values = np.asarray(strain, dtype=float)
    segment_length = int(round(float(segment_seconds) * sample_rate_hz))
    if segment_length < 8:
        raise ValueError("PSD segment is too short")
    step = int(round(segment_length * (1.0 - float(overlap_fraction))))
    if step <= 0:
        raise ValueError("overlap_fraction leaves no positive Welch step")
    window = np.hanning(segment_length)
    normalization = float(sample_rate_hz) * float(np.sum(window * window))
    estimates = []
    used_starts = []
    for start in range(0, values.size - segment_length + 1, step):
        candidate = slice(start, start + segment_length)
        if exclude_slice is not None and _overlaps(candidate, exclude_slice):
            continue
        segment = values[candidate]
        segment = segment - float(np.mean(segment))
        spectrum = np.fft.rfft(segment * window)
        psd = (np.abs(spectrum) ** 2) / normalization
        if psd.size > 2:
            psd[1:-1] *= 2.0
        estimates.append(psd)
        used_starts.append(start)
    if len(estimates) < 3:
        raise ValueError("not enough off-source segments for PSD estimate")
    stacked = np.vstack(estimates)
    median_psd = np.median(stacked, axis=0)
    median_psd = np.maximum(median_psd, np.finfo(float).tiny)
    return {
        "frequencies_hz": np.fft.rfftfreq(segment_length, d=1.0 / sample_rate_hz),
        "psd": median_psd,
        "segment_count": len(estimates),
        "segment_length": segment_length,
        "segment_seconds": float(segment_seconds),
        "overlap_fraction": float(overlap_fraction),
        "used_starts": [int(start) for start in used_starts],
        "psd_min": float(np.min(median_psd)),
        "psd_max": float(np.max(median_psd)),
    }


def psd_whitened_event_spectrum(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
) -> dict[str, Any]:
    event = event_tapered_segment(
        strain,
        gps_start=gps_start,
        sample_rate_hz=sample_rate_hz,
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
    event_fft = np.fft.rfft(event["tapered"])
    psd_interp = np.interp(
        window["frequencies_hz"],
        psd["frequencies_hz"],
        psd["psd"],
    )
    whitened = event_fft[selected] / np.sqrt(psd_interp)
    norm = float(np.linalg.norm(whitened))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("whitened event spectrum cannot be normalized")
    normalized = whitened / norm
    return {
        "frequencies_hz": window["frequencies_hz"],
        "v_f": window["v_f"],
        "normalized_whitened_spectrum": normalized,
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
        "whitened_norm": norm,
        "normalized_whitened_norm": float(np.linalg.norm(normalized)),
    }


def normalized_complex_source_templates(
    v_f: np.ndarray,
    *,
    eta: float = ETA_REFERENCE,
) -> dict[str, np.ndarray]:
    eta_value = validate_eta(eta)
    grid = np.asarray(v_f, dtype=float)
    phase = phase_response_kernels(grid, eta_value)
    amplitude = amplitude_response_kernels(grid, eta_value)
    templates = {
        "alpha_bar_1": amplitude["alpha_bar_1"] + 1j * phase["alpha_bar_1"],
        "alpha_bar_2": amplitude["alpha_bar_2"] + 1j * phase["alpha_bar_2"],
    }
    normalized = {}
    for parameter, template in templates.items():
        centered = template - np.mean(template)
        norm = float(np.linalg.norm(centered))
        if not math.isfinite(norm) or norm <= 0.0:
            raise ValueError(f"{parameter} complex template cannot be normalized")
        normalized[parameter] = centered / norm
    return normalized


def project_psd_whitened_complex_response(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, Any]:
    whitened = psd_whitened_event_spectrum(
        strain,
        gps_start=gps_start,
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    templates = normalized_complex_source_templates(whitened["v_f"], eta=eta)
    data = whitened["normalized_whitened_spectrum"]
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
            "psd_whitened_complex_source_response_with_unit_gr_reference"
        ),
        "frequency_window": whitened["frequency_window"],
        "event_summary": whitened["event_summary"],
        "psd_summary": whitened["psd_summary"],
        "projections": projections,
        "template_norms": template_norms,
        "normalized_whitened_norm": whitened["normalized_whitened_norm"],
        "projection_ready": (
            all(
                math.isfinite(component)
                for row in projections.values()
                for component in row.values()
            )
            and all(abs(norm - 1.0) < 1.0e-12 for norm in template_norms.values())
            and abs(whitened["normalized_whitened_norm"] - 1.0) < 1.0e-12
        ),
    }


def load_and_project_detector_record(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    projection = project_psd_whitened_complex_response(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "psd_whitened_projection": projection,
        "projection_ready": projection["projection_ready"],
    }


def network_complex_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    parameters = sorted(detector_rows[0]["psd_whitened_projection"]["projections"])
    summary: dict[str, Any] = {
        "detectors": [row["detector"] for row in detector_rows],
        "parameters": parameters,
    }
    for parameter in parameters:
        abs_values = [
            row["psd_whitened_projection"]["projections"][parameter]["abs"]
            for row in detector_rows
        ]
        real_values = [
            row["psd_whitened_projection"]["projections"][parameter]["real"]
            for row in detector_rows
        ]
        imag_values = [
            row["psd_whitened_projection"]["projections"][parameter]["imag"]
            for row in detector_rows
        ]
        summary[f"{parameter}_abs_mean"] = float(np.mean(abs_values))
        summary[f"{parameter}_abs_detector_spread"] = float(
            max(abs_values) - min(abs_values)
        )
        summary[f"{parameter}_real_mean"] = float(np.mean(real_values))
        summary[f"{parameter}_imag_mean"] = float(np.mean(imag_values))
    return summary


def evaluate_psd_whitened_complex_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers: set[str] = set()
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row["projection_ready"] for row in detector_rows):
        blockers.add("one_or_more_psd_whitened_projections_not_ready")
    for row in detector_rows:
        projection = row.get("psd_whitened_projection", {})
        if projection.get("source_reference") != SOURCE_REFERENCE:
            blockers.add("source_reference_missing_or_unexpected")
        if projection.get("projection_kind") != (
            "psd_whitened_complex_source_response_with_unit_gr_reference"
        ):
            blockers.add("projection_kind_unexpected")
        psd_summary = projection.get("psd_summary", {})
        if int(psd_summary.get("segment_count", 0)) < 3:
            blockers.add("off_source_psd_segment_count_too_small")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "unit_gr_reference_not_physical_waveform",
            "detector_calibration_uncertainty_missing",
            "event_mass_eta_posterior_sampling_missing",
            "full_imr_merger_ringdown_response_missing",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )
    return {
        "psd_whitened_complex_projection_ready": not blockers,
        "claim_ready": False,
        "projection_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "removed_v2_110_blocker": (
            "psd_whitening_and_calibration_likelihood_missing"
            if not blockers
            else None
        ),
    }


def diagnose_gw_psd_whitened_complex_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_and_project_detector_record(record, cache_dir) for record in records
    ]
    evaluation = evaluate_psd_whitened_complex_projection(detector_rows)
    return {
        "version": VERSION,
        "basis": [
            "v2.110_source_backed_frequency_domain_strain_projection",
            "v2.109_source_backed_cubic_inspiral_response",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "source_reference": SOURCE_REFERENCE,
        "cache_dir": str(cache_dir),
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_projections": detector_rows,
        "network_projection": network_complex_projection(detector_rows),
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "psd_whitened_complex_source_projection_ready_nonclaiming"
            if evaluation["psd_whitened_complex_projection_ready"]
            else "psd_whitened_complex_source_projection_not_ready"
        ),
        "selected_next_build_action": (
            "replace_unit_reference_with_physical_gr_waveform_phase"
        ),
        "best_next_artifact": (
            "Swap the unit complex reference for a physical GR inspiral/IMR "
            "frequency-domain waveform and export a posterior-sampled alpha_bar "
            "likelihood packet."
        ),
        "interpretation": (
            "The source-backed alpha response is now projected against a "
            "PSD-whitened complex event spectrum estimated from public "
            "off-source strain. This is stricter than a spectral-shape "
            "diagnostic, but it still is not a likelihood because the complex "
            "reference is unit-normalized rather than a physical GR waveform, "
            "and event-parameter/posterior systematics are not sampled."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.111/"
            "gw_psd_whitened_complex_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_psd_whitened_complex_projection(Path(args.cache_dir))
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
