"""ParSpec source-event R4 likelihood with event-specific detector topology."""

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
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_public_strain_loader import DEFAULT_CACHE_DIR
from experiments.r4_lalsuite_waveform_likelihood_posterior import (
    AXES,
    GRID_OFFSETS,
    DEFAULT_NUISANCE_EXPORT_PATH,
    detector_r4_waveform_likelihood,
    lalsuite_status,
    load_json,
    network_r4_waveform_likelihood,
    nuisance_export_central_values,
)
from experiments.r4_parspec_qeft_source_asset_audit import DEFAULT_OUT as DEFAULT_V2191_PATH
from experiments.r4_parspec_same_event_h1l1_likelihood import (
    DEFAULT_OUT as DEFAULT_V2193_PATH,
)
from experiments.r4_parspec_source_event_alignment_manifest import (
    DEFAULT_OUT as DEFAULT_V2192_PATH,
)
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS


VERSION = "v2.194"
DEFAULT_OUT = Path(
    "experiments/results/v2.194/r4_parspec_event_topology_likelihood.json"
)
EVENT_TOPOLOGY_DETECTORS = {
    "GW150914": ("H1", "L1"),
    "GW200129": ("H1", "L1", "V1"),
}
DETECTOR_INDEX_NAMES = {
    "H1": "LALDetectorIndexLHODIFF",
    "L1": "LALDetectorIndexLLODIFF",
    "V1": "LALDetectorIndexVIRGODIFF",
}
RESPONSE_GRID = {
    "ra_count": 8,
    "dec_count": 7,
    "psi_count": 6,
    "sample_count": 336,
    "dec_min_rad": -0.75,
    "dec_max_rad": 0.75,
    "psi_period_rad": math.pi,
    "weighting": "cos(dec)",
}
CLAIM_GRADE_REMAINING_BLOCKERS = (
    "source_event_specific_nuisance_covariance_export_missing",
    "public_parspec_qeft_likelihood_or_posterior_samples_missing",
    "operator_basis_map_missing",
    "engine_axis_orientation_missing",
    "axis_normalization_missing",
    "nuisance_grid_is_coarse_not_posterior_sampler",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def source_event_topology_32s_records(
    manifest: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    summary = manifest["source_event_manifest_summary"]
    event_gps = {
        event["paper_event"]: float(event["gps"])
        for event in summary["events"]
    }
    grouped: dict[str, list[dict[str, Any]]] = {
        event: [] for event in SOURCE_EVENTS
    }
    for record in summary["strain_records"]:
        event = str(record["paper_event"])
        detector = str(record["detector"])
        if (
            event in grouped
            and detector in EVENT_TOPOLOGY_DETECTORS[event]
            and int(record["duration"]) == 32
        ):
            grouped[event].append({
                "paper_event": event,
                "gwosc_event_name": record["gwosc_event_name"],
                "event_version": record["event_version"],
                "detector": detector,
                "duration": int(record["duration"]),
                "sample_rate_hz": int(record["sample_rate_hz"]),
                "file_format": record["file_format"],
                "gps_start": int(record["gps_start"]),
                "event_gps": event_gps[event],
                "download_url": record["download_url"],
            })
    return {
        event: sorted(
            rows,
            key=lambda row: EVENT_TOPOLOGY_DETECTORS[event].index(row["detector"]),
        )
        for event, rows in grouped.items()
    }


def lalsuite_detector_channel_response_moments(
    detector: str,
    event_gps: float,
) -> dict[str, Any]:
    import lal  # noqa: PLC0415

    detector = str(detector)
    if detector not in DETECTOR_INDEX_NAMES:
        raise ValueError(f"unsupported detector: {detector}")
    detector_index_name = DETECTOR_INDEX_NAMES[detector]
    lal_detector = lal.CachedDetectors[getattr(lal, detector_index_name)]
    event_gmst = float(lal.GreenwichMeanSiderealTime(float(event_gps)))
    values = []
    for ra in np.linspace(0.0, 2.0 * math.pi, RESPONSE_GRID["ra_count"], endpoint=False):
        for dec in np.linspace(
            RESPONSE_GRID["dec_min_rad"],
            RESPONSE_GRID["dec_max_rad"],
            RESPONSE_GRID["dec_count"],
        ):
            weight = math.cos(float(dec))
            for psi in np.linspace(
                0.0,
                RESPONSE_GRID["psi_period_rad"],
                RESPONSE_GRID["psi_count"],
                endpoint=False,
            ):
                f_plus, f_cross = lal.ComputeDetAMResponse(
                    lal_detector.response,
                    float(ra),
                    float(dec),
                    float(psi),
                    event_gmst,
                )
                values.append((float(f_plus), float(f_cross), float(weight)))
    weights = np.asarray([row[2] for row in values], dtype=float)
    weights = weights / float(np.sum(weights))
    f_plus = np.asarray([row[0] for row in values], dtype=float)
    f_cross = np.asarray([row[1] for row in values], dtype=float)
    tensor_rms = math.sqrt(float(np.sum(weights * (f_plus**2 + f_cross**2))))
    helicity_re_rms = math.sqrt(
        float(np.sum(weights * ((f_plus**2 - f_cross**2) ** 2)))
    )
    helicity_im_rms = math.sqrt(
        float(np.sum(weights * ((2.0 * f_plus * f_cross) ** 2)))
    )
    return canonicalize_json_floats({
        "detector": detector,
        "lal_detector_index": detector_index_name,
        "event_gps": float(event_gps),
        "event_gmst": event_gmst,
        "grid": RESPONSE_GRID,
        "response_kind": (
            "event_time_sky_polarization_marginalized_lalsuite_tensor_rms_moments"
        ),
        "tensor_rms": tensor_rms,
        "helicity_re_rms": helicity_re_rms,
        "helicity_im_rms": helicity_im_rms,
        "K_plus": tensor_rms,
        "Re_K_minus": helicity_re_rms / tensor_rms,
        "Im_K_minus": helicity_im_rms / tensor_rms,
        "max_abs_fplus": float(np.max(np.abs(f_plus))),
        "max_abs_fcross": float(np.max(np.abs(f_cross))),
        "detector_channel_response_calibrated": True,
    })


def source_event_detector_responses(
    records_by_event: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    responses: dict[str, dict[str, dict[str, Any]]] = {}
    for event, records in records_by_event.items():
        responses[event] = {
            record["detector"]: lalsuite_detector_channel_response_moments(
                record["detector"],
                float(record["event_gps"]),
            )
            for record in records
        }
    return responses


def _event_likelihood_not_run(
    event: str,
    records: list[dict[str, Any]],
    reason: str,
) -> dict[str, Any]:
    return {
        "paper_event": event,
        "gwosc_event_name": records[0]["gwosc_event_name"] if records else None,
        "event_version": records[0]["event_version"] if records else None,
        "expected_detectors": list(EVENT_TOPOLOGY_DETECTORS[event]),
        "detectors": sorted({record["detector"] for record in records}),
        "detector_channel_responses": {},
        "detector_likelihoods": [],
        "network_likelihood": {},
        "event_detector_topology_likelihood_ready": False,
        "not_run_reason": reason,
    }


def run_source_event_topology_likelihood(
    event: str,
    records: list[dict[str, Any]],
    *,
    cache_dir: Path,
    central_values: dict[str, float],
    detector_responses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    expected = list(EVENT_TOPOLOGY_DETECTORS[event])
    if [record["detector"] for record in records] != expected:
        return _event_likelihood_not_run(
            event,
            records,
            "source_event_detector_topology_records_missing",
        )
    detector_rows = [
        detector_r4_waveform_likelihood(
            record,
            cache_dir,
            central_values=central_values,
            event_gps=float(record["event_gps"]),
            detector_channel_response=detector_responses[record["detector"]],
        )
        for record in records
    ]
    network = network_r4_waveform_likelihood(detector_rows)
    ready = (
        [row["detector"] for row in detector_rows] == expected
        and all(row["likelihood_ready"] for row in detector_rows)
        and int(network.get("grid_points", 0)) == len(GRID_OFFSETS) ** len(AXES)
        and network.get("posterior", {}).get("posterior_normalized") is True
        and network.get("posterior", {}).get("posterior_positive_semidefinite")
        is True
    )
    return canonicalize_json_floats({
        "paper_event": event,
        "gwosc_event_name": records[0]["gwosc_event_name"],
        "event_version": records[0]["event_version"],
        "expected_detectors": expected,
        "detectors": [row["detector"] for row in detector_rows],
        "detector_channel_responses": detector_responses,
        "detector_likelihoods": detector_rows,
        "network_likelihood": network,
        "event_detector_topology_likelihood_ready": ready,
    })


def evaluate_parspec_event_topology_likelihoods(
    event_likelihoods: list[dict[str, Any]],
    *,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers: set[str] = set()
    status = lalsuite_status() if status is None else status
    if not status.get("available"):
        blockers.add("lalsuite_not_installed")
    if not status.get("has_imrphenomd"):
        blockers.add("lalsuite_imrphenomd_unavailable")
    if tuple(row.get("paper_event") for row in event_likelihoods) != SOURCE_EVENTS:
        blockers.add("source_event_likelihoods_not_exact_parspec_events")
    for event in SOURCE_EVENTS:
        rows = [
            row for row in event_likelihoods if row.get("paper_event") == event
        ]
        if len(rows) != 1:
            blockers.add(f"{event}_likelihood_missing")
            continue
        row = rows[0]
        expected = list(EVENT_TOPOLOGY_DETECTORS[event])
        if row.get("detectors") != expected:
            blockers.add(f"{event}_detectors_not_expected_topology")
        if row.get("event_detector_topology_likelihood_ready") is not True:
            blockers.add(f"{event}_event_topology_likelihood_not_ready")
        responses = row.get("detector_channel_responses", {})
        for detector in expected:
            response = responses.get(detector, {})
            for field in ("K_plus", "Re_K_minus", "Im_K_minus"):
                value = float(response.get(field, math.nan))
                if not math.isfinite(value) or value <= 0.0:
                    blockers.add(f"{event}_{detector}_{field}_not_positive")
            if response.get("detector_channel_response_calibrated") is not True:
                blockers.add(f"{event}_{detector}_response_not_calibrated")
        network = row.get("network_likelihood", {})
        if int(network.get("grid_points", 0)) != len(GRID_OFFSETS) ** len(AXES):
            blockers.add(f"{event}_network_grid_missing")
        posterior = network.get("posterior", {})
        if posterior.get("posterior_normalized") is not True:
            blockers.add(f"{event}_posterior_not_normalized")
        if posterior.get("posterior_positive_semidefinite") is not True:
            blockers.add(f"{event}_posterior_covariance_not_psd")

    event_detector_topology_ready = not blockers
    claim_blockers = set(CLAIM_GRADE_REMAINING_BLOCKERS)
    if not event_detector_topology_ready:
        claim_blockers.add("source_event_detector_topology_likelihood_not_ready")
    return canonicalize_json_floats({
        "source_event_detector_topology_likelihood_ready": (
            event_detector_topology_ready
        ),
        "event_set_alignment_ready": event_detector_topology_ready,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "event_topology_likelihood_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "split_v2193_v1_blocker": {
            "previous": "gw200129_v1_detector_channel_response",
            "now_resolved_subpiece": (
                "gw200129_v1_detector_response_and_hlv_likelihood"
                if event_detector_topology_ready
                else None
            ),
            "remaining_subpieces": [
                "source_event_specific_nuisance_covariance_export",
                "public_parspec_qeft_likelihood_or_posterior_samples",
                "engine_axis_map_ready",
                "claim_grade_waveform_systematics_and_review",
            ],
        },
        "route_status": (
            "parspec_source_event_topology_likelihood_ready_covariance_missing"
            if event_detector_topology_ready
            else "parspec_source_event_topology_likelihood_not_ready"
        ),
    })


def diagnose_r4_parspec_event_topology_likelihood(
    *,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    v2192_path: Path = DEFAULT_V2192_PATH,
    v2193_path: Path = DEFAULT_V2193_PATH,
    v2191_path: Path = DEFAULT_V2191_PATH,
    nuisance_export_path: Path = DEFAULT_NUISANCE_EXPORT_PATH,
) -> dict[str, Any]:
    manifest = load_json(v2192_path)
    v2193 = load_json(v2193_path)
    v2191 = load_json(v2191_path)
    nuisance = load_json(nuisance_export_path)
    central_values = nuisance_export_central_values(nuisance)
    records_by_event = source_event_topology_32s_records(manifest)
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        event_likelihoods = [
            _event_likelihood_not_run(
                event,
                records_by_event[event],
                "lalsuite_antenna_or_imrphenomd_unavailable",
            )
            for event in SOURCE_EVENTS
        ]
    else:
        responses_by_event = source_event_detector_responses(records_by_event)
        event_likelihoods = [
            run_source_event_topology_likelihood(
                event,
                records_by_event[event],
                cache_dir=cache_dir,
                central_values=central_values,
                detector_responses=responses_by_event[event],
            )
            for event in SOURCE_EVENTS
        ]
    evaluation = evaluate_parspec_event_topology_likelihoods(
        event_likelihoods,
        status=status,
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.192_r4_parspec_source_event_alignment_manifest",
            "v2.193_r4_parspec_same_event_h1l1_likelihood",
            "lal.ComputeDetAMResponse",
            "GWOSC_GW150914_v3_H1_L1_32s_HDF5",
            "GWOSC_GW200129_065458_v1_H1_L1_V1_32s_HDF5",
        ],
        "cache_dir": Path(cache_dir).as_posix(),
        "v2192_manifest_path": Path(v2192_path).as_posix(),
        "v2193_h1l1_likelihood_path": Path(v2193_path).as_posix(),
        "nuisance_export_path": Path(nuisance_export_path).as_posix(),
        "lalsuite_status": status,
        "central_values": central_values,
        "coefficient_grid": {
            "axes": list(AXES),
            "offsets": list(GRID_OFFSETS),
            "grid_points": len(GRID_OFFSETS) ** len(AXES),
        },
        "response_grid": RESPONSE_GRID,
        "source_event_records": records_by_event,
        "event_likelihoods": event_likelihoods,
        "evaluation": evaluation,
        "source_event_detector_topology_likelihood_ready": evaluation[
            "source_event_detector_topology_likelihood_ready"
        ],
        "event_set_alignment_ready": evaluation["event_set_alignment_ready"],
        "v2193_previous_state": {
            "route_status": v2193["route_status"],
            "claim_blockers": v2193["evaluation"]["claim_blockers"],
        },
        "v2191_remaining_state": {
            "route_status": v2191["route_status"],
            "remaining_contract_blockers_after_asset_audit": v2191[
                "remaining_contract_blockers_after_asset_audit"
            ],
        },
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "export_source_event_specific_nuisance_covariance"
        ),
        "interpretation": (
            "The engine now has an event-specific detector-topology R4 "
            "likelihood bridge for the ParSpec source events: GW150914 uses "
            "H1/L1 and GW200129 uses H1/L1/V1 public strain with LALSuite "
            "event-time antenna responses. This removes the V1 detector-response "
            "subpiece from the event-alignment blocker, but remains nonclaiming "
            "because source-event-specific nuisance covariance, public ParSpec "
            "qEFT likelihood samples, an operator-basis axis map, waveform "
            "systematics, and external review are still missing."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--v2192", default=str(DEFAULT_V2192_PATH))
    parser.add_argument("--v2193", default=str(DEFAULT_V2193_PATH))
    parser.add_argument("--v2191", default=str(DEFAULT_V2191_PATH))
    parser.add_argument(
        "--nuisance-export",
        default=str(DEFAULT_NUISANCE_EXPORT_PATH),
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_event_topology_likelihood(
        cache_dir=Path(args.cache_dir),
        v2192_path=Path(args.v2192),
        v2193_path=Path(args.v2193),
        v2191_path=Path(args.v2191),
        nuisance_export_path=Path(args.nuisance_export),
    )
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
