"""Project the R4 response contract onto real GWOSC HDF5 strain files."""

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
from experiments.gw_strain_alpha_residual_projection import (
    condition_strain_segment,
    read_strain_values,
)
from experiments.public_gw_r4_reanalysis_fixture import (
    evaluate_public_gw_r4_reanalysis_fixture,
    synthetic_public_gw_r4_reanalysis_packet,
)
from experiments.r4_lalsuite_waveform_response_contract import (
    RESPONSE_AXES,
    evaluate_lalsuite_r4_response_candidate,
    synthetic_lalsuite_r4_response_candidate,
)
from experiments.r4_response_public_strain_projection import (
    BASE_VARIANCE,
    PROJECTION_SCALE,
    _template_arrays,
    r4_response_template_summary,
)


VERSION = "v2.179"
REAL_HDF5_REANALYSIS_BLOCKERS = (
    "r4_response_kernels_are_ansatz_not_source_backed",
    "lalsuite_r4_runtime_projection_not_run",
    "nuisance_marginalized_covariance_not_exported",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


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


def project_gwosc_record_r4_response(
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
    templates = _template_arrays(int(conditioning["sample_count"]))
    conditioned = conditioning["conditioned"]
    projections = {
        axis: float(np.dot(conditioned, templates[axis]))
        for axis in RESPONSE_AXES
    }
    projection_ready = (
        load["loader_ready"]
        and all(math.isfinite(value) for value in projections.values())
        and abs(conditioning["conditioned_rms"] - 1.0) <= 1.0e-12
    )
    return canonicalize_json_floats({
        "detector": record["detector"],
        "cache_path": cache_path_for_record(record, cache_dir).as_posix(),
        "metadata": metadata,
        "loader_ready": load["loader_ready"],
        "synthetic_strain_fixture": False,
        "real_public_hdf5_projection": True,
        "conditioning": {
            key: value for key, value in conditioning.items()
            if key != "conditioned"
        },
        "projection": projections,
        "projection_ready": projection_ready,
    })


def load_and_project_gwosc_r4_response(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    selected = _default_32s_records() if records is None else records
    return [
        project_gwosc_record_r4_response(record, cache_dir)
        for record in selected
    ]


def network_r4_hdf5_projection(detector_rows: list[dict[str, Any]]) -> dict[str, Any]:
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
        "detectors": [row["detector"] for row in detector_rows],
        "axes": list(RESPONSE_AXES),
        "projection_means": means,
        "projection_spreads": spreads,
        "central_values": central_values,
        "covariance": covariance,
        "covariance_status": "real_hdf5_projection_seed_positive_definite",
        "synthetic_strain_fixture": False,
        "real_public_hdf5_projection": True,
    })


def r4_gwosc_hdf5_projection_packet(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = load_and_project_gwosc_r4_response(cache_dir, records)
    network = network_r4_hdf5_projection(rows)
    packet = deepcopy(synthetic_public_gw_r4_reanalysis_packet())
    packet["packet_id"] = "gw170608_r4_gwosc_hdf5_projection_seed_v1"
    packet["likelihood"]["central_values"] = network["central_values"]
    packet["likelihood"]["covariance"] = network["covariance"]
    packet["likelihood"]["generation"] = (
        "real_gwosc_hdf5_r4_response_projection_seed"
    )
    packet["provenance"]["synthetic_control"] = True
    packet["provenance"]["real_public_hdf5_projection"] = True
    packet["provenance"]["public_r4_reanalysis_output"] = False
    packet["provenance"]["r4_gwosc_hdf5_projection_harness"] = {
        "cache_dir": Path(cache_dir).as_posix(),
        "template_summary": r4_response_template_summary(),
        "detector_rows": rows,
        "network_projection": network,
        "real_public_hdf5_projection": True,
        "r4_waveform_kernels_source_backed": False,
    }
    return canonicalize_json_floats(packet)


def evaluate_r4_response_gwosc_hdf5_projection(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or r4_gwosc_hdf5_projection_packet()
    response_eval = evaluate_lalsuite_r4_response_candidate(
        synthetic_lalsuite_r4_response_candidate()
    )
    fixture_eval = evaluate_public_gw_r4_reanalysis_fixture(packet)
    harness = packet.get("provenance", {}).get("r4_gwosc_hdf5_projection_harness", {})
    detector_rows = harness.get("detector_rows", [])
    network = harness.get("network_projection", {})

    blockers: set[str] = set()
    if response_eval["software_response_contract_ready"] is not True:
        blockers.add("r4_response_contract_not_ready")
    if fixture_eval["fixture_packet_engine_ready"] is not True:
        blockers.add("hdf5_projection_packet_not_engine_ready")
    if sorted(row.get("detector") for row in detector_rows) != ["H1", "L1"]:
        blockers.add("projection_detectors_not_h1_l1")
    if not detector_rows or not all(row.get("loader_ready") for row in detector_rows):
        blockers.add("one_or_more_hdf5_loaders_not_ready")
    if not detector_rows or not all(row.get("projection_ready") for row in detector_rows):
        blockers.add("one_or_more_hdf5_projections_not_ready")
    if network.get("real_public_hdf5_projection") is not True:
        blockers.add("network_projection_not_marked_real_hdf5")

    claim_blockers = set(REAL_HDF5_REANALYSIS_BLOCKERS)
    if packet.get("provenance", {}).get("synthetic_control") is True:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if blockers:
        claim_blockers.add("hdf5_projection_harness_not_engine_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "response_contract_evaluation": response_eval,
        "fixture_packet_evaluation": fixture_eval,
        "hdf5_projection_harness_engine_ready": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "projection_blockers": sorted(blockers),
        "real_hdf5_reanalysis_blockers": sorted(REAL_HDF5_REANALYSIS_BLOCKERS),
        "claim_blockers": sorted(claim_blockers),
        "shape_score": fixture_eval["shape_score"],
        "route_status": (
            "r4_response_gwosc_hdf5_projection_ready_nonclaiming"
            if not blockers
            else "r4_response_gwosc_hdf5_projection_blocked"
        ),
    })


def malformed_r4_gwosc_hdf5_projection_packet(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = r4_gwosc_hdf5_projection_packet(cache_dir, records)
    harness = packet["provenance"]["r4_gwosc_hdf5_projection_harness"]
    harness["detector_rows"] = harness["detector_rows"][:1]
    harness["network_projection"]["real_public_hdf5_projection"] = False
    packet["likelihood"]["covariance"][2][2] = 0.0
    return packet


def diagnose_r4_response_gwosc_hdf5_projection(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = r4_gwosc_hdf5_projection_packet(cache_dir, records)
    evaluation = evaluate_r4_response_gwosc_hdf5_projection(packet)
    malformed = evaluate_r4_response_gwosc_hdf5_projection(
        malformed_r4_gwosc_hdf5_projection_packet(cache_dir, records)
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.178_r4_response_public_strain_projection",
            "v2.177_r4_lalsuite_waveform_response_contract",
            "v2.107_gw_public_strain_loader",
            "GWOSC_GW170608_v3_H1_L1_32s_HDF5",
        ],
        "cache_dir": Path(cache_dir).as_posix(),
        "projected_hdf5_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "hdf5_projection_harness_engine_ready": (
            evaluation["hdf5_projection_harness_engine_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "r4_response_gwosc_hdf5_projection_ready_nonclaiming",
        "selected_next_build_action": (
            "replace_ansatz_r4_kernels_with_source_backed_pn_imr_derivation"
        ),
        "best_next_artifact": (
            "A source-backed R4 PN/IMR waveform derivation for g_R4_c1, "
            "g_R4_c2, and g_R4_c3 that can replace the ansatz response kernels "
            "while preserving the real GWOSC HDF5 projection path."
        ),
        "interpretation": (
            "The R4 response contract now projects through real public GWOSC "
            "H1/L1 HDF5 strain bytes and emits an ingestible covariance seed. "
            "This removes the synthetic-strain-row blocker but remains "
            "nonclaiming because the R4 waveform kernels are still an ansatz "
            "and no nuisance-marginalized public covariance has been exported."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.179/"
            "r4_response_gwosc_hdf5_projection.json"
        ),
    )
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    args = parser.parse_args()

    result = diagnose_r4_response_gwosc_hdf5_projection(Path(args.cache_dir))
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
