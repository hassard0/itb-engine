"""Project the R4 response contract through the public-strain harness."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_strain_alpha_residual_projection import condition_strain_segment
from experiments.public_gw_r4_reanalysis_fixture import (
    evaluate_public_gw_r4_reanalysis_fixture,
    synthetic_public_gw_r4_reanalysis_packet,
)
from experiments.r4_lalsuite_waveform_response_contract import (
    RESPONSE_AXES,
    evaluate_lalsuite_r4_response_candidate,
    r4_shape_response_kernels,
    synthetic_lalsuite_r4_response_candidate,
)


VERSION = "v2.178"
SEGMENT_SECONDS = 4.0
PROJECTION_SCALE = 0.01
BASE_VARIANCE = 0.25
REAL_PUBLIC_STRAIN_BLOCKERS = (
    "gwosc_hdf5_bytes_not_loaded_in_r4_projection_harness",
    "lalsuite_r4_runtime_projection_not_run",
    "source_backed_r4_waveform_kernels_missing",
    "nuisance_marginalized_covariance_not_exported",
    "external_adversarial_review_missing",
)


def _unit_norm(values: np.ndarray, label: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError(f"{label} template norm is not positive finite")
    return vector / norm


def _orthonormalize(seed_templates: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    orthonormal: dict[str, np.ndarray] = {}
    for axis in RESPONSE_AXES:
        vector = np.asarray(seed_templates[axis], dtype=float).copy()
        for previous in orthonormal.values():
            vector -= float(np.dot(vector, previous)) * previous
        orthonormal[axis] = _unit_norm(vector, axis)
    return orthonormal


def _template_arrays(
    sample_count: int,
    *,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
) -> dict[str, np.ndarray]:
    if sample_count < 16:
        raise ValueError("sample_count must be at least 16")
    response = r4_shape_response_kernels()
    kernel_grid = np.linspace(0.0, 1.0, len(response["v_f_grid"]))
    template_grid = np.linspace(0.0, 1.0, int(sample_count))
    times = (np.arange(sample_count, dtype=float) / sample_rate_hz) - (
        sample_count / (2.0 * sample_rate_hz)
    )
    envelope = np.exp(-0.5 * (times / 0.45) ** 2)
    chirp_phase = 2.0 * np.pi * (55.0 * times + 38.0 * times * times)
    seeds = {
        "g_R4_c1": envelope
        * np.cos(chirp_phase)
        * np.interp(template_grid, kernel_grid, response["kernels"]["g_R4_c1"]),
        "g_R4_c2": envelope
        * np.sin(chirp_phase)
        * np.interp(template_grid, kernel_grid, response["kernels"]["g_R4_c2"]),
        "g_R4_c3": envelope
        * np.cos(1.5 * chirp_phase + 0.35)
        * np.interp(template_grid, kernel_grid, response["kernels"]["g_R4_c3"]),
    }
    return _orthonormalize(seeds)


def r4_response_template_summary(
    sample_count: int = int(SEGMENT_SECONDS * SAMPLE_RATE_HZ),
) -> dict[str, Any]:
    templates = _template_arrays(sample_count)
    gram = [
        [
            float(np.dot(templates[left], templates[right]))
            for right in RESPONSE_AXES
        ]
        for left in RESPONSE_AXES
    ]
    return canonicalize_json_floats({
        "template_kind": "r4_response_contract_time_domain_projection_fixture",
        "sample_count": sample_count,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "axes": list(RESPONSE_AXES),
        "template_norms": {
            axis: float(np.linalg.norm(templates[axis])) for axis in RESPONSE_AXES
        },
        "template_gram_matrix": gram,
        "orthonormal_within_tolerance": all(
            abs(gram[row][col] - (1.0 if row == col else 0.0)) <= 1.0e-12
            for row in range(len(RESPONSE_AXES))
            for col in range(len(RESPONSE_AXES))
        ),
    })


def synthetic_detector_strain(detector: str) -> np.ndarray:
    if detector not in {"H1", "L1"}:
        raise ValueError("detector must be H1 or L1")
    times = np.arange(32 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    phase_shift = 0.0 if detector == "H1" else 0.37
    amplitude_scale = 1.0 if detector == "H1" else 0.92
    strain = amplitude_scale * np.sin(2.0 * np.pi * 36.0 * times + phase_shift)
    strain += 0.38 * np.sin(2.0 * np.pi * 91.0 * times + 0.5 * phase_shift)
    strain += 0.12 * np.cos(2.0 * np.pi * 177.0 * times - phase_shift)
    return strain


def project_detector_r4_response(detector: str) -> dict[str, Any]:
    strain = synthetic_detector_strain(detector)
    conditioning = condition_strain_segment(strain, gps_start=1180922479)
    conditioned = conditioning["conditioned"]
    templates = _template_arrays(int(conditioning["sample_count"]))
    projections = {
        axis: float(np.dot(conditioned, templates[axis]))
        for axis in RESPONSE_AXES
    }
    return canonicalize_json_floats({
        "detector": detector,
        "synthetic_strain_fixture": True,
        "conditioning": {
            key: value for key, value in conditioning.items()
            if key != "conditioned"
        },
        "projection": projections,
        "projection_ready": (
            all(math.isfinite(value) for value in projections.values())
            and abs(conditioning["conditioned_rms"] - 1.0) <= 1.0e-12
        ),
    })


def network_r4_response_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    detectors = [row["detector"] for row in detector_rows]
    projection_by_axis = {
        axis: [float(row["projection"][axis]) for row in detector_rows]
        for axis in RESPONSE_AXES
    }
    means = {
        axis: float(np.mean(values))
        for axis, values in projection_by_axis.items()
    }
    spreads = {
        axis: float(max(values) - min(values))
        for axis, values in projection_by_axis.items()
    }
    central_values = {
        "g_R4_c1": 0.5 + PROJECTION_SCALE * means["g_R4_c1"],
        "g_R4_c2": 0.5 + PROJECTION_SCALE * means["g_R4_c2"],
        "g_R4_c3": PROJECTION_SCALE * means["g_R4_c3"],
    }
    variances = [
        BASE_VARIANCE + spreads[axis] ** 2 * PROJECTION_SCALE**2
        for axis in RESPONSE_AXES
    ]
    covariance = [
        [variances[0], 0.02, 0.0],
        [0.02, variances[1], 0.0],
        [0.0, 0.0, max(0.09, variances[2])],
    ]
    return canonicalize_json_floats({
        "detectors": detectors,
        "axes": list(RESPONSE_AXES),
        "projection_means": means,
        "projection_spreads": spreads,
        "central_values": central_values,
        "covariance": covariance,
        "covariance_status": "synthetic_projection_seed_positive_definite",
        "synthetic_strain_fixture": True,
    })


def r4_projected_public_strain_fixture_packet() -> dict[str, Any]:
    packet = deepcopy(synthetic_public_gw_r4_reanalysis_packet())
    rows = [
        project_detector_r4_response("H1"),
        project_detector_r4_response("L1"),
    ]
    network = network_r4_response_projection(rows)
    packet["packet_id"] = "gw170608_r4_response_projection_seed_fixture_v1"
    packet["likelihood"]["central_values"] = network["central_values"]
    packet["likelihood"]["covariance"] = network["covariance"]
    packet["likelihood"]["generation"] = (
        "r4_response_contract_public_strain_projection_seed"
    )
    packet["provenance"]["r4_response_projection_harness"] = {
        "template_summary": r4_response_template_summary(),
        "detector_rows": rows,
        "network_projection": network,
        "real_public_hdf5_projection": False,
    }
    return canonicalize_json_floats(packet)


def evaluate_r4_response_public_strain_projection(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or r4_projected_public_strain_fixture_packet()
    response_eval = evaluate_lalsuite_r4_response_candidate(
        synthetic_lalsuite_r4_response_candidate()
    )
    fixture_eval = evaluate_public_gw_r4_reanalysis_fixture(packet)
    harness = packet.get("provenance", {}).get("r4_response_projection_harness", {})
    template_summary = harness.get("template_summary", {})
    detector_rows = harness.get("detector_rows", [])

    blockers: set[str] = set()
    if response_eval["software_response_contract_ready"] is not True:
        blockers.add("r4_response_contract_not_ready")
    if fixture_eval["fixture_packet_engine_ready"] is not True:
        blockers.add("projected_fixture_packet_not_engine_ready")
    if template_summary.get("orthonormal_within_tolerance") is not True:
        blockers.add("r4_response_templates_not_orthonormal")
    if sorted(row.get("detector") for row in detector_rows) != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row.get("projection_ready") for row in detector_rows):
        blockers.add("one_or_more_detector_projections_not_ready")

    claim_blockers = set(REAL_PUBLIC_STRAIN_BLOCKERS)
    if packet.get("provenance", {}).get("synthetic_control") is True:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if blockers:
        claim_blockers.add("projection_harness_not_engine_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "response_contract_evaluation": response_eval,
        "fixture_packet_evaluation": fixture_eval,
        "projection_harness_engine_ready": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "projection_blockers": sorted(blockers),
        "real_public_strain_blockers": sorted(REAL_PUBLIC_STRAIN_BLOCKERS),
        "claim_blockers": sorted(claim_blockers),
        "shape_score": fixture_eval["shape_score"],
        "route_status": (
            "r4_response_public_strain_projection_ready_nonclaiming"
            if not blockers
            else "r4_response_public_strain_projection_blocked"
        ),
    })


def malformed_r4_projected_public_strain_fixture_packet() -> dict[str, Any]:
    packet = r4_projected_public_strain_fixture_packet()
    harness = packet["provenance"]["r4_response_projection_harness"]
    harness["detector_rows"] = harness["detector_rows"][:1]
    harness["template_summary"]["orthonormal_within_tolerance"] = False
    packet["likelihood"]["covariance"][0][0] = 0.0
    return packet


def diagnose_r4_response_public_strain_projection() -> dict[str, Any]:
    packet = r4_projected_public_strain_fixture_packet()
    evaluation = evaluate_r4_response_public_strain_projection(packet)
    malformed = evaluate_r4_response_public_strain_projection(
        malformed_r4_projected_public_strain_fixture_packet()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.177_r4_lalsuite_waveform_response_contract",
            "v2.176_public_gw_r4_reanalysis_fixture",
            "v2.108_public_strain_alpha_residual_projection_pattern",
        ],
        "template_summary": r4_response_template_summary(),
        "projected_fixture_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "projection_harness_engine_ready": (
            evaluation["projection_harness_engine_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "r4_response_public_strain_projection_ready_nonclaiming",
        "selected_next_build_action": (
            "replace_synthetic_strain_rows_with_gwosc_hdf5_r4_projection"
        ),
        "best_next_artifact": (
            "Load the real GWOSC H1/L1 HDF5 strain through the v2.107 loader, "
            "project the v2.177 R4 response templates, and then replace the "
            "ansatz kernels with source-backed R4 PN/IMR waveform kernels."
        ),
        "interpretation": (
            "The v2.177 R4 response contract now reaches the public-strain "
            "projection harness and emits an ingestible covariance seed. The "
            "strain rows are synthetic controls, so the route remains a "
            "software proof rather than a public GW R4 measurement."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.178/"
            "r4_response_public_strain_projection.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_response_public_strain_projection()
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
