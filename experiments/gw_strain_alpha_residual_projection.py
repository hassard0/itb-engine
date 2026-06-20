"""Strain conditioning and alpha-proxy residual projection for v2.108."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import h5py
import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_public_strain_connector import GPS, SAMPLE_RATE_HZ
from experiments.gw_public_strain_loader import (
    DEFAULT_CACHE_DIR,
    cache_path_for_record,
    ensure_cached_strain_file,
    gw170608_v3_strain_records,
    load_required_32s_strain,
)


VERSION = "v2.108"
SEGMENT_HALF_WINDOW_SECONDS = 2.0
SEGMENT_SECONDS = 2.0 * SEGMENT_HALF_WINDOW_SECONDS
TEMPLATE_ENVELOPE_SECONDS = 0.35
TEMPLATE_F0_HZ = 80.0
TEMPLATE_CHIRP_HZ_PER_SECOND = 120.0


def read_strain_values(path: Path) -> np.ndarray:
    with h5py.File(path, "r") as hdf:
        return np.asarray(hdf["/strain/Strain"], dtype=float)


def event_centered_slice(
    *,
    gps_start: int,
    sample_count: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    event_gps: float = GPS,
    half_window_seconds: float = SEGMENT_HALF_WINDOW_SECONDS,
) -> slice:
    event_index = int(round((event_gps - float(gps_start)) * sample_rate_hz))
    half_width = int(round(half_window_seconds * sample_rate_hz))
    start = event_index - half_width
    stop = event_index + half_width
    if start < 0 or stop > sample_count:
        raise ValueError(
            f"event-centered slice [{start}, {stop}) outside sample_count={sample_count}"
        )
    return slice(start, stop)


def condition_strain_segment(
    strain: np.ndarray,
    *,
    gps_start: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    selection = event_centered_slice(
        gps_start=gps_start,
        sample_count=int(strain.size),
        sample_rate_hz=sample_rate_hz,
    )
    raw = np.asarray(strain[selection], dtype=float)
    demeaned = raw - float(np.mean(raw))
    taper = np.hanning(raw.size)
    tapered = demeaned * taper
    rms = float(np.sqrt(np.mean(tapered * tapered)))
    if not math.isfinite(rms) or rms <= 0.0:
        raise ValueError("conditioned strain RMS is not positive finite")
    conditioned = tapered / rms
    return {
        "conditioned": conditioned,
        "start_index": int(selection.start or 0),
        "stop_index": int(selection.stop or 0),
        "sample_count": int(conditioned.size),
        "raw_mean": float(np.mean(raw)),
        "raw_rms": float(np.sqrt(np.mean(raw * raw))),
        "conditioned_mean": float(np.mean(conditioned)),
        "conditioned_rms": float(np.sqrt(np.mean(conditioned * conditioned))),
    }


def alpha_proxy_templates(
    sample_count: int,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
) -> dict[str, np.ndarray]:
    times = (np.arange(sample_count, dtype=float) / sample_rate_hz) - (
        sample_count / (2.0 * sample_rate_hz)
    )
    envelope = np.exp(-0.5 * (times / TEMPLATE_ENVELOPE_SECONDS) ** 2)
    phase = 2.0 * np.pi * (
        TEMPLATE_F0_HZ * times
        + 0.5 * TEMPLATE_CHIRP_HZ_PER_SECOND * times * times
    )
    template_1 = envelope * np.cos(phase)
    template_2_seed = envelope * np.sin(phase) * (
        1.0 + times / TEMPLATE_ENVELOPE_SECONDS
    )
    template_1 = template_1 / np.linalg.norm(template_1)
    template_2 = template_2_seed - np.dot(template_2_seed, template_1) * template_1
    template_2 = template_2 / np.linalg.norm(template_2)
    return {"alpha_bar_1": template_1, "alpha_bar_2": template_2}


def template_summary(templates: dict[str, np.ndarray]) -> dict[str, Any]:
    alpha_1 = templates["alpha_bar_1"]
    alpha_2 = templates["alpha_bar_2"]
    return {
        "template_kind": "deterministic_proxy_not_source_backed_eft_waveform",
        "alpha_bar_1_norm": float(np.linalg.norm(alpha_1)),
        "alpha_bar_2_norm": float(np.linalg.norm(alpha_2)),
        "alpha_template_dot": float(np.dot(alpha_1, alpha_2)),
        "envelope_seconds": TEMPLATE_ENVELOPE_SECONDS,
        "f0_hz": TEMPLATE_F0_HZ,
        "chirp_hz_per_second": TEMPLATE_CHIRP_HZ_PER_SECOND,
    }


def project_conditioned_strain(
    conditioned: np.ndarray,
    templates: dict[str, np.ndarray],
) -> dict[str, float]:
    return {
        "alpha_bar_1_proxy_projection": float(
            np.dot(conditioned, templates["alpha_bar_1"])
        ),
        "alpha_bar_2_proxy_projection": float(
            np.dot(conditioned, templates["alpha_bar_2"])
        ),
        "conditioned_energy": float(np.mean(conditioned * conditioned)),
    }


def load_and_project_detector_record(
    record: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    path = ensure_cached_strain_file(record, cache_dir)
    strain = read_strain_values(path)
    conditioning = condition_strain_segment(
        strain,
        gps_start=int(record["gps_start"]),
        sample_rate_hz=int(record["sample_rate_hz"]),
    )
    templates = alpha_proxy_templates(conditioning["sample_count"])
    projection = project_conditioned_strain(conditioning["conditioned"], templates)
    return {
        "detector": record["detector"],
        "path": str(cache_path_for_record(record, cache_dir)),
        "conditioning": {
            key: value for key, value in conditioning.items() if key != "conditioned"
        },
        "projection": projection,
        "projection_ready": (
            math.isfinite(projection["alpha_bar_1_proxy_projection"])
            and math.isfinite(projection["alpha_bar_2_proxy_projection"])
            and abs(projection["conditioned_energy"] - 1.0) < 1.0e-9
        ),
    }


def network_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
    alpha_1 = [
        row["projection"]["alpha_bar_1_proxy_projection"] for row in detector_rows
    ]
    alpha_2 = [
        row["projection"]["alpha_bar_2_proxy_projection"] for row in detector_rows
    ]
    return {
        "detectors": [row["detector"] for row in detector_rows],
        "alpha_bar_1_proxy_mean": float(np.mean(alpha_1)),
        "alpha_bar_2_proxy_mean": float(np.mean(alpha_2)),
        "alpha_bar_1_detector_spread": float(max(alpha_1) - min(alpha_1)),
        "alpha_bar_2_detector_spread": float(max(alpha_2) - min(alpha_2)),
    }


def evaluate_projection_harness(
    detector_rows: list[dict[str, Any]],
    templates: dict[str, np.ndarray],
) -> dict[str, Any]:
    blockers: set[str] = set()
    detectors = sorted(row["detector"] for row in detector_rows)
    if detectors != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row["projection_ready"] for row in detector_rows):
        blockers.add("one_or_more_detector_projections_not_ready")
    summary = template_summary(templates)
    if abs(summary["alpha_bar_1_norm"] - 1.0) > 1.0e-12:
        blockers.add("alpha_bar_1_template_not_normalized")
    if abs(summary["alpha_bar_2_norm"] - 1.0) > 1.0e-12:
        blockers.add("alpha_bar_2_template_not_normalized")
    if abs(summary["alpha_template_dot"]) > 1.0e-12:
        blockers.add("alpha_templates_not_orthogonal")
    claim_blockers = set(blockers)
    claim_blockers.add("alpha_templates_proxy_not_source_backed")
    claim_blockers.add("psd_whitening_and_calibration_not_applied")
    claim_blockers.add("g8_joint_component_missing")
    return {
        "projection_harness_ready": not blockers,
        "claim_ready": False,
        "projection_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "template_summary": summary,
    }


def diagnose_gw_strain_alpha_residual_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    load_summary = load_required_32s_strain(cache_dir)
    records = [
        record for record in gw170608_v3_strain_records() if int(record["duration"]) == 32
    ]
    detector_rows = [
        load_and_project_detector_record(record, cache_dir) for record in records
    ]
    templates = alpha_proxy_templates(detector_rows[0]["conditioning"]["sample_count"])
    evaluation = evaluate_projection_harness(detector_rows, templates)
    return {
        "version": VERSION,
        "basis": [
            "v2.107_public_hdf5_strain_loader",
            "v2.105_alpha_likelihood_stub",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "cache_dir": str(cache_dir),
        "conditioning_window_seconds": SEGMENT_SECONDS,
        "loader_evaluation": {
            "load_count": len(load_summary),
            "all_loader_ready": all(row["loader_ready"] for row in load_summary),
        },
        "detector_projections": detector_rows,
        "network_projection": network_projection(detector_rows),
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "public_strain_alpha_proxy_projection_ready_nonclaiming"
            if evaluation["projection_harness_ready"]
            else "public_strain_alpha_proxy_projection_not_ready"
        ),
        "selected_next_build_action": (
            "replace_proxy_templates_with_source_backed_cubic_eft_waveform"
        ),
        "best_next_artifact": (
            "A source-backed cubic-EFT waveform response for alpha_bar_1 and "
            "alpha_bar_2 that can replace the proxy templates while preserving "
            "the verified strain-conditioning and projection harness."
        ),
        "interpretation": (
            "The public strain now feeds a deterministic conditioning and "
            "projection pipeline. The output is still a proxy residual, not a "
            "Liu-Yunes alpha-bar likelihood, because the templates are not a "
            "source-backed cubic-EFT waveform and no PSD/calibration treatment "
            "has been applied."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.108/"
            "gw_strain_alpha_residual_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_gw_strain_alpha_residual_projection(Path(args.cache_dir))
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
