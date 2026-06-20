"""Project source-backed R4 PN kernels through real GWOSC HDF5 strain."""

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
from experiments.gw_public_strain_loader import (
    DEFAULT_CACHE_DIR,
    cache_path_for_record,
    ensure_cached_strain_file,
    gw170608_v3_strain_records,
    load_strain_record,
    read_gwosc_hdf5_metadata,
)
from experiments.gw_source_backed_strain_projection import (
    REFERENCE_TOTAL_MASS_SOLAR,
    conditioned_frequency_feature,
    normalized_vector,
)
from experiments.gw_strain_alpha_residual_projection import (
    condition_strain_segment,
    read_strain_values,
)
from experiments.public_gw_r4_reanalysis_fixture import (
    evaluate_public_gw_r4_reanalysis_fixture,
    synthetic_public_gw_r4_reanalysis_packet,
)
from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES
from experiments.r4_response_public_strain_projection import (
    BASE_VARIANCE,
    PROJECTION_SCALE,
)
from experiments.r4_source_backed_pn_imr_derivation import (
    ENGINE_AXIS_CHANNEL_WEIGHTS,
    REMAINING_REAL_REANALYSIS_BLOCKERS,
    SOURCE_CHANNELS,
    evaluate_r4_source_backed_pn_imr_derivation,
    r4_pn_power_law_terms,
    source_backed_r4_pn_imr_response_derivation,
)


VERSION = "v2.181"
DETECTOR_CHANNEL_RESPONSE_PROXY = {
    "H1": {"K_plus": 1.0, "Re_K_minus": 0.22, "Im_K_minus": -0.18},
    "L1": {"K_plus": 0.94, "Re_K_minus": -0.31, "Im_K_minus": 0.26},
}
SOURCE_BACKED_GWOSC_BLOCKERS = (
    "detector_antenna_r4_channel_response_not_calibrated",
    "full_imr_r4_merger_ringdown_completion_missing",
    "lalsuite_r4_runtime_projection_not_run",
    "nuisance_marginalized_covariance_not_exported",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def _channel_preview_response(
    terms: dict[str, Any],
    channel: str,
) -> np.ndarray:
    phase = terms["phase_delta_psi"]
    amplitude = terms["relative_amplitude_delta_a_over_a_newt"]
    if channel == "K_plus":
        return (
            np.asarray(phase["tidal_5pn"], dtype=float)
            + np.asarray(phase["direct_bulk_7pn"], dtype=float)
            + np.asarray(amplitude["tidal_5pn"], dtype=float)
            + np.asarray(amplitude["direct_bulk_7pn"], dtype=float)
        )
    if channel == "Re_K_minus":
        return (
            np.asarray(phase["direct_bulk_7pn"], dtype=float)
            + np.asarray(amplitude["direct_bulk_7pn"], dtype=float)
        )
    if channel == "Im_K_minus":
        return (
            np.asarray(phase["direct_bulk_7pn"], dtype=float)
            - np.asarray(amplitude["direct_bulk_7pn"], dtype=float)
        )
    raise ValueError(f"unsupported source channel: {channel}")


def _default_32s_records() -> list[dict[str, Any]]:
    return [
        record for record in gw170608_v3_strain_records()
        if int(record["duration"]) == 32
    ]


def _posix(value: str | Path) -> str:
    return Path(value).as_posix()


def _normalized_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(metadata)
    if "path" in normalized:
        normalized["path"] = _posix(str(normalized["path"]))
    return normalized


def source_backed_detector_r4_templates(
    v_f: np.ndarray,
    detector: str,
) -> dict[str, np.ndarray]:
    if detector not in DETECTOR_CHANNEL_RESPONSE_PROXY:
        raise ValueError(f"unsupported detector: {detector}")
    terms = r4_pn_power_law_terms(np.asarray(v_f, dtype=float))
    proxy = DETECTOR_CHANNEL_RESPONSE_PROXY[detector]
    templates: dict[str, np.ndarray] = {}
    for axis in RESPONSE_AXES:
        weights = ENGINE_AXIS_CHANNEL_WEIGHTS[axis]
        response = np.zeros_like(np.asarray(v_f, dtype=float))
        for channel in SOURCE_CHANNELS:
            coefficient = float(weights[channel]) * float(proxy[channel])
            response += coefficient * _channel_preview_response(terms, channel)
        templates[axis] = normalized_vector(response)
    return templates


def project_conditioned_source_backed_r4_response(
    conditioned: np.ndarray,
    *,
    detector: str,
    sample_rate_hz: int,
    total_mass_solar: float = REFERENCE_TOTAL_MASS_SOLAR,
) -> dict[str, Any]:
    feature = conditioned_frequency_feature(
        conditioned,
        sample_rate_hz=sample_rate_hz,
        total_mass_solar=total_mass_solar,
    )
    templates = source_backed_detector_r4_templates(feature["v_f"], detector)
    projections = {
        axis: float(np.dot(feature["normalized_feature"], template))
        for axis, template in templates.items()
    }
    template_norms = {
        axis: float(np.linalg.norm(template)) for axis, template in templates.items()
    }
    return canonicalize_json_floats({
        "projection_kind": (
            "source_backed_r4_pn_channel_spectral_projection_not_matched_filter"
        ),
        "feature_kind": feature["feature_kind"],
        "frequency_window": feature["frequency_window"],
        "detector_channel_response_proxy": DETECTOR_CHANNEL_RESPONSE_PROXY[detector],
        "detector_channel_response_calibrated": False,
        "source_backed_kernel_derivation": True,
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
    })


def project_gwosc_record_source_backed_r4(
    record: dict[str, Any],
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    cache_dir = Path(cache_dir)
    path = ensure_cached_strain_file(record, cache_dir)
    load = load_strain_record(record, cache_dir)
    metadata = _normalized_metadata(read_gwosc_hdf5_metadata(path))
    strain = read_strain_values(path)
    conditioning = condition_strain_segment(
        strain,
        gps_start=int(metadata["gps_start"]),
        sample_rate_hz=int(metadata["sample_rate_hz"]),
    )
    projection = project_conditioned_source_backed_r4_response(
        conditioning["conditioned"],
        detector=str(record["detector"]),
        sample_rate_hz=int(metadata["sample_rate_hz"]),
    )
    return canonicalize_json_floats({
        "detector": record["detector"],
        "cache_path": cache_path_for_record(record, cache_dir).as_posix(),
        "metadata": metadata,
        "loader_ready": load["loader_ready"],
        "conditioning": {
            key: value for key, value in conditioning.items()
            if key != "conditioned"
        },
        "source_backed_r4_projection": projection,
        "projection_ready": (
            load["loader_ready"] is True and projection["projection_ready"] is True
        ),
    })


def load_and_project_source_backed_gwosc_r4(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    selected = _default_32s_records() if records is None else records
    return [
        project_gwosc_record_source_backed_r4(record, cache_dir)
        for record in selected
    ]


def network_source_backed_r4_projection(
    detector_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    projection_by_axis = {
        axis: [
            float(row["source_backed_r4_projection"]["projections"][axis])
            for row in detector_rows
        ]
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
        "detectors": [row["detector"] for row in detector_rows],
        "axes": list(RESPONSE_AXES),
        "projection_means": means,
        "projection_spreads": spreads,
        "central_values": central_values,
        "covariance": covariance,
        "covariance_status": "source_backed_r4_projection_seed_positive_definite",
        "real_public_hdf5_projection": True,
        "source_backed_kernel_derivation": True,
        "detector_channel_response_calibrated": False,
    })


def r4_source_backed_gwosc_projection_packet(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = load_and_project_source_backed_gwosc_r4(cache_dir, records)
    network = network_source_backed_r4_projection(rows)
    derivation = source_backed_r4_pn_imr_response_derivation()
    packet = deepcopy(synthetic_public_gw_r4_reanalysis_packet())
    packet["packet_id"] = "gw170608_r4_source_backed_gwosc_projection_seed_v1"
    packet["likelihood"]["central_values"] = network["central_values"]
    packet["likelihood"]["covariance"] = network["covariance"]
    packet["likelihood"]["generation"] = (
        "real_gwosc_hdf5_source_backed_r4_pn_projection_seed"
    )
    packet["provenance"]["synthetic_control"] = True
    packet["provenance"]["real_public_hdf5_projection"] = True
    packet["provenance"]["source_backed_r4_kernel_derivation"] = True
    packet["provenance"]["public_r4_reanalysis_output"] = False
    packet["provenance"]["r4_source_backed_gwosc_projection_harness"] = {
        "cache_dir": Path(cache_dir).as_posix(),
        "derivation_id": derivation["derivation_id"],
        "detector_rows": rows,
        "network_projection": network,
        "source_backed_kernel_derivation": derivation,
        "real_public_hdf5_projection": True,
        "detector_channel_response_calibrated": False,
    }
    return canonicalize_json_floats(packet)


def evaluate_r4_source_backed_gwosc_projection(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or r4_source_backed_gwosc_projection_packet()
    harness = packet.get("provenance", {}).get(
        "r4_source_backed_gwosc_projection_harness",
        {},
    )
    derivation = harness.get("source_backed_kernel_derivation", {})
    derivation_eval = evaluate_r4_source_backed_pn_imr_derivation(derivation)
    fixture_eval = evaluate_public_gw_r4_reanalysis_fixture(packet)
    detector_rows = harness.get("detector_rows", [])
    network = harness.get("network_projection", {})

    blockers: set[str] = set()
    if derivation_eval["response_derivation_ready"] is not True:
        blockers.add("source_backed_r4_derivation_not_ready")
    if fixture_eval["fixture_packet_engine_ready"] is not True:
        blockers.add("source_backed_projection_packet_not_engine_ready")
    if sorted(row.get("detector") for row in detector_rows) != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row.get("loader_ready") for row in detector_rows):
        blockers.add("one_or_more_hdf5_loaders_not_ready")
    if not detector_rows or not all(row.get("projection_ready") for row in detector_rows):
        blockers.add("one_or_more_source_backed_projections_not_ready")
    if network.get("source_backed_kernel_derivation") is not True:
        blockers.add("network_projection_not_source_backed")
    if network.get("real_public_hdf5_projection") is not True:
        blockers.add("network_projection_not_marked_real_hdf5")

    claim_blockers = set(SOURCE_BACKED_GWOSC_BLOCKERS)
    if packet.get("provenance", {}).get("synthetic_control") is True:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if blockers:
        claim_blockers.add("source_backed_gwosc_projection_harness_not_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "derivation_evaluation": derivation_eval,
        "fixture_packet_evaluation": fixture_eval,
        "source_backed_gwosc_projection_ready": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "projection_blockers": sorted(blockers),
        "remaining_real_reanalysis_blockers": sorted(
            set(REMAINING_REAL_REANALYSIS_BLOCKERS)
            | {"detector_antenna_r4_channel_response_not_calibrated"}
        ),
        "claim_blockers": sorted(claim_blockers),
        "shape_score": fixture_eval["shape_score"],
        "removed_v2_179_blockers": [
            "r4_response_kernels_are_ansatz_not_source_backed",
        ],
        "route_status": (
            "r4_source_backed_gwosc_projection_ready_nonclaiming"
            if not blockers
            else "r4_source_backed_gwosc_projection_blocked"
        ),
    })


def malformed_r4_source_backed_gwosc_projection_packet(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = r4_source_backed_gwosc_projection_packet(cache_dir, records)
    harness = packet["provenance"]["r4_source_backed_gwosc_projection_harness"]
    harness["detector_rows"] = harness["detector_rows"][:1]
    harness["network_projection"]["source_backed_kernel_derivation"] = False
    packet["likelihood"]["covariance"][2][2] = 0.0
    return packet


def diagnose_r4_source_backed_gwosc_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = r4_source_backed_gwosc_projection_packet(cache_dir, records)
    evaluation = evaluate_r4_source_backed_gwosc_projection(packet)
    malformed = evaluate_r4_source_backed_gwosc_projection(
        malformed_r4_source_backed_gwosc_projection_packet(cache_dir, records)
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.180_r4_source_backed_pn_imr_derivation",
            "v2.179_r4_response_gwosc_hdf5_projection",
            "v2.110_source_backed_frequency_domain_strain_projection",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "projected_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "source_backed_gwosc_projection_ready": (
            evaluation["source_backed_gwosc_projection_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "calibrate_r4_detector_channel_response_and_lalsuite_runtime"
        ),
        "best_next_artifact": (
            "Replace the deterministic detector-channel proxy with calibrated "
            "R4 antenna/channel response inside a LALSuite or successor runtime, "
            "then export nuisance-marginalized covariance."
        ),
        "interpretation": (
            "The GWOSC HDF5 route now uses source-backed R4 PN channel kernels "
            "instead of the v2.177 ansatz. It remains nonclaiming because the "
            "detector R4 channel response is still a deterministic proxy and "
            "no LALSuite runtime covariance or systematics closure exists."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.181/"
            "r4_source_backed_gwosc_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_r4_source_backed_gwosc_projection(Path(args.cache_dir))
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
