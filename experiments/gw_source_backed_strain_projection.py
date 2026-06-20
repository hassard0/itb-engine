"""Source-backed frequency-domain strain projection for v2.110."""

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
    VF_GRID_MAX,
    VF_GRID_MIN,
    amplitude_response_kernels,
    phase_response_kernels,
    validate_eta,
)
from experiments.gw_strain_alpha_residual_projection import (
    condition_strain_segment,
    read_strain_values,
)


VERSION = "v2.110"
M_SOLAR_SECONDS = 4.925490947e-6
REFERENCE_TOTAL_MASS_SOLAR = 19.0
FREQUENCY_MIN_HZ = 20.0


def validate_total_mass_solar(total_mass_solar: float) -> float:
    mass = float(total_mass_solar)
    if not math.isfinite(mass) or mass <= 0.0:
        raise ValueError("total_mass_solar must be positive and finite")
    return mass


def vf_from_frequency_hz(
    frequencies_hz: np.ndarray,
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
) -> np.ndarray:
    mass_seconds = validate_total_mass_solar(total_mass_solar) * M_SOLAR_SECONDS
    frequencies = np.asarray(frequencies_hz, dtype=float)
    if not np.all(np.isfinite(frequencies)) or np.any(frequencies < 0.0):
        raise ValueError("frequencies_hz must be finite and non-negative")
    return (np.pi * mass_seconds * frequencies) ** (1.0 / 3.0)


def source_inspiral_frequency_window(
    sample_count: int,
    *,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    min_frequency_hz: float = FREQUENCY_MIN_HZ,
    min_vf: float = VF_GRID_MIN,
    max_vf: float = VF_GRID_MAX,
) -> dict[str, Any]:
    if sample_count < 4:
        raise ValueError("sample_count must be at least 4")
    frequencies = np.fft.rfftfreq(sample_count, d=1.0 / float(sample_rate_hz))
    v_f = vf_from_frequency_hz(
        frequencies,
        total_mass_solar=total_mass_solar,
    )
    mask = (
        (frequencies >= float(min_frequency_hz))
        & (v_f >= float(min_vf))
        & (v_f <= float(max_vf))
    )
    selected_frequencies = frequencies[mask]
    selected_vf = v_f[mask]
    if selected_frequencies.size < 8:
        raise ValueError("selected source-backed frequency window is too small")
    return {
        "frequencies_hz": selected_frequencies,
        "v_f": selected_vf,
        "bin_count": int(selected_frequencies.size),
        "frequency_min_hz": float(selected_frequencies[0]),
        "frequency_max_hz": float(selected_frequencies[-1]),
        "v_f_min": float(selected_vf[0]),
        "v_f_max": float(selected_vf[-1]),
        "frequency_resolution_hz": float(
            selected_frequencies[1] - selected_frequencies[0]
        ),
        "total_mass_solar": float(total_mass_solar),
        "eta_reference": ETA_REFERENCE,
    }


def normalized_vector(values: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or vector.size < 3:
        raise ValueError("values must be a one-dimensional vector")
    centered = vector - float(np.mean(vector))
    norm = float(np.linalg.norm(centered))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("values cannot be normalized")
    return centered / norm


def conditioned_frequency_feature(
    conditioned: np.ndarray,
    *,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
) -> dict[str, Any]:
    strain = np.asarray(conditioned, dtype=float)
    if strain.ndim != 1 or strain.size < 4:
        raise ValueError("conditioned strain must be a one-dimensional vector")
    window = source_inspiral_frequency_window(
        strain.size,
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    spectrum = np.fft.rfft(strain)
    frequencies = np.fft.rfftfreq(strain.size, d=1.0 / float(sample_rate_hz))
    selected = np.isin(frequencies, window["frequencies_hz"])
    log_magnitude = np.log1p(np.abs(spectrum[selected]))
    feature = normalized_vector(log_magnitude)
    return {
        "frequency_window": {
            key: value
            for key, value in window.items()
            if key not in {"frequencies_hz", "v_f"}
        },
        "frequencies_hz": window["frequencies_hz"],
        "v_f": window["v_f"],
        "normalized_feature": feature,
        "feature_kind": "centered_unit_log_magnitude_spectrum",
        "feature_norm": float(np.linalg.norm(feature)),
        "raw_log_magnitude_mean": float(np.mean(log_magnitude)),
        "raw_log_magnitude_std": float(np.std(log_magnitude)),
    }


def source_frequency_templates(
    v_f: np.ndarray,
    *,
    eta: float = ETA_REFERENCE,
) -> dict[str, np.ndarray]:
    eta_value = validate_eta(eta)
    grid = np.asarray(v_f, dtype=float)
    phase = phase_response_kernels(grid, eta_value)
    amplitude = amplitude_response_kernels(grid, eta_value)
    return {
        "phase_alpha_bar_1": normalized_vector(phase["alpha_bar_1"]),
        "phase_alpha_bar_2": normalized_vector(phase["alpha_bar_2"]),
        "amplitude_alpha_bar_1": normalized_vector(amplitude["alpha_bar_1"]),
        "amplitude_alpha_bar_2": normalized_vector(amplitude["alpha_bar_2"]),
    }


def project_conditioned_source_response(
    conditioned: np.ndarray,
    *,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, Any]:
    feature = conditioned_frequency_feature(
        conditioned,
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    templates = source_frequency_templates(feature["v_f"], eta=eta)
    projections = {
        name: float(np.dot(feature["normalized_feature"], template))
        for name, template in templates.items()
    }
    template_norms = {
        name: float(np.linalg.norm(template)) for name, template in templates.items()
    }
    return {
        "source_reference": SOURCE_REFERENCE,
        "feature_kind": feature["feature_kind"],
        "frequency_window": feature["frequency_window"],
        "projection_kind": (
            "source_weighted_spectral_shape_projection_not_matched_filter"
        ),
        "projections": projections,
        "template_norms": template_norms,
        "feature_norm": feature["feature_norm"],
        "raw_log_magnitude_mean": feature["raw_log_magnitude_mean"],
        "raw_log_magnitude_std": feature["raw_log_magnitude_std"],
        "projection_ready": (
            all(math.isfinite(value) for value in projections.values())
            and all(abs(norm - 1.0) < 1.0e-12 for norm in template_norms.values())
            and abs(feature["feature_norm"] - 1.0) < 1.0e-12
        ),
    }


def load_and_project_detector_record(
    record: dict[str, Any],
    cache_dir: Path,
    *,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
    eta: float = ETA_REFERENCE,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    conditioning = condition_strain_segment(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    projection = project_conditioned_source_response(
        conditioning["conditioned"],
        sample_rate_hz=int(record["sample_rate_hz"]),
        total_mass_solar=total_mass_solar,
        eta=eta,
    )
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "conditioning": {
            key: value for key, value in conditioning.items() if key != "conditioned"
        },
        "source_backed_projection": projection,
        "projection_ready": projection["projection_ready"],
    }


def network_source_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    projection_names = sorted(
        detector_rows[0]["source_backed_projection"]["projections"]
    )
    summary: dict[str, Any] = {
        "detectors": [row["detector"] for row in detector_rows],
        "projection_names": projection_names,
    }
    for name in projection_names:
        values = [
            row["source_backed_projection"]["projections"][name]
            for row in detector_rows
        ]
        summary[f"{name}_mean"] = float(np.mean(values))
        summary[f"{name}_detector_spread"] = float(max(values) - min(values))
    return summary


def evaluate_source_backed_strain_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers: set[str] = set()
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row["projection_ready"] for row in detector_rows):
        blockers.add("one_or_more_source_backed_projections_not_ready")
    for row in detector_rows:
        projection = row.get("source_backed_projection", {})
        if projection.get("source_reference") != SOURCE_REFERENCE:
            blockers.add("source_reference_missing_or_unexpected")
        window = projection.get("frequency_window", {})
        if int(window.get("bin_count", 0)) < 8:
            blockers.add("source_frequency_window_too_small")
        if projection.get("projection_kind") != (
            "source_weighted_spectral_shape_projection_not_matched_filter"
        ):
            blockers.add("projection_kind_unexpected")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "projection_is_spectral_shape_not_calibrated_likelihood",
            "complex_gr_waveform_phase_reference_missing",
            "psd_whitening_and_calibration_likelihood_missing",
            "event_mass_eta_posterior_sampling_missing",
            "full_imr_merger_ringdown_response_missing",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )
    return {
        "strain_projection_ready": not blockers,
        "claim_ready": False,
        "projection_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "removed_v2_109_blocker": (
            "frequency_domain_to_strain_projection_missing"
            if not blockers
            else None
        ),
    }


def diagnose_gw_source_backed_strain_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_and_project_detector_record(record, cache_dir) for record in records
    ]
    evaluation = evaluate_source_backed_strain_projection(detector_rows)
    return {
        "version": VERSION,
        "basis": [
            "v2.109_source_backed_cubic_inspiral_response",
            "v2.108_public_strain_conditioning",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "source_reference": SOURCE_REFERENCE,
        "cache_dir": str(cache_dir),
        "reference_total_mass_solar": REFERENCE_TOTAL_MASS_SOLAR,
        "reference_eta": ETA_REFERENCE,
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_projections": detector_rows,
        "network_projection": network_source_projection(detector_rows),
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "source_backed_frequency_domain_strain_projection_ready_nonclaiming"
            if evaluation["strain_projection_ready"]
            else "source_backed_frequency_domain_strain_projection_not_ready"
        ),
        "selected_next_build_action": (
            "replace_spectral_shape_projection_with_psd_whitened_complex_template"
        ),
        "best_next_artifact": (
            "Use the source-backed alpha kernels inside a PSD-whitened complex "
            "frequency-domain residual with a GR waveform phase reference, then "
            "sample over event mass and eta instead of using a fixed reference."
        ),
        "interpretation": (
            "The v2.109 source-backed alpha response now touches the verified "
            "public H1/L1 strain in frequency space. The projection is still a "
            "spectral-shape diagnostic, not a likelihood or matched-filter "
            "alpha estimate, because it lacks PSD/calibration treatment, a GR "
            "phase reference, posterior sampling over mass and eta, and a full "
            "IMR treatment."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.110/"
            "gw_source_backed_strain_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_source_backed_strain_projection(Path(args.cache_dir))
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
