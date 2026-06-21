"""H1/L1 R4 likelihood rerun on the ParSpec source events."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_public_strain_loader import DEFAULT_CACHE_DIR
from experiments.r4_lalsuite_waveform_likelihood_posterior import (
    AXES,
    GRID_OFFSETS,
    DEFAULT_NUISANCE_EXPORT_PATH,
    detector_r4_waveform_likelihood,
    evaluate_r4_lalsuite_waveform_likelihood_posterior,
    lalsuite_status,
    load_json,
    network_r4_waveform_likelihood,
    nuisance_export_central_values,
)
from experiments.r4_parspec_qeft_source_asset_audit import DEFAULT_OUT as DEFAULT_V2191_PATH
from experiments.r4_parspec_source_event_alignment_manifest import (
    DEFAULT_OUT as DEFAULT_V2192_PATH,
)
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS


VERSION = "v2.193"
DEFAULT_OUT = Path(
    "experiments/results/v2.193/r4_parspec_same_event_h1l1_likelihood.json"
)
H1L1_DETECTORS = ("H1", "L1")
CLAIM_GRADE_REMAINING_BLOCKERS = (
    "gw200129_v1_detector_channel_response_missing",
    "source_event_specific_nuisance_covariance_export_missing",
    "public_parspec_qeft_likelihood_or_posterior_samples_missing",
    "operator_basis_map_missing",
    "engine_axis_orientation_missing",
    "axis_normalization_missing",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def source_event_h1l1_32s_records(
    manifest: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    summary = manifest["source_event_manifest_summary"]
    records = summary["strain_records"]
    event_gps = {
        event["paper_event"]: float(event["gps"])
        for event in summary["events"]
    }
    grouped: dict[str, list[dict[str, Any]]] = {event: [] for event in SOURCE_EVENTS}
    for record in records:
        event = str(record["paper_event"])
        if (
            event in grouped
            and str(record["detector"]) in H1L1_DETECTORS
            and int(record["duration"]) == 32
        ):
            grouped[event].append({
                "paper_event": event,
                "gwosc_event_name": record["gwosc_event_name"],
                "event_version": record["event_version"],
                "detector": record["detector"],
                "duration": int(record["duration"]),
                "sample_rate_hz": int(record["sample_rate_hz"]),
                "file_format": record["file_format"],
                "gps_start": int(record["gps_start"]),
                "event_gps": event_gps[event],
                "download_url": record["download_url"],
            })
    return {
        event: sorted(rows, key=lambda row: row["detector"])
        for event, rows in grouped.items()
    }


def evaluate_source_event_h1l1_likelihoods(
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

    event_labels = [row.get("paper_event") for row in event_likelihoods]
    if tuple(event_labels) != SOURCE_EVENTS:
        blockers.add("source_event_likelihoods_not_exact_parspec_events")
    for event in SOURCE_EVENTS:
        rows = [
            row for row in event_likelihoods if row.get("paper_event") == event
        ]
        if len(rows) != 1:
            blockers.add(f"{event}_likelihood_missing")
            continue
        row = rows[0]
        detectors = sorted(row.get("detectors", []))
        if detectors != list(H1L1_DETECTORS):
            blockers.add(f"{event}_detectors_not_h1_l1")
        if row.get("h1l1_likelihood_ready") is not True:
            blockers.add(f"{event}_h1l1_likelihood_not_ready")
        network = row.get("network_likelihood", {})
        if int(network.get("grid_points", 0)) != len(GRID_OFFSETS) ** len(AXES):
            blockers.add(f"{event}_network_grid_missing")
        posterior = network.get("posterior", {})
        if posterior.get("posterior_normalized") is not True:
            blockers.add(f"{event}_posterior_not_normalized")
        if posterior.get("posterior_positive_semidefinite") is not True:
            blockers.add(f"{event}_posterior_covariance_not_psd")

    h1l1_same_event_likelihood_ready = not blockers
    claim_blockers = set(CLAIM_GRADE_REMAINING_BLOCKERS)
    if not h1l1_same_event_likelihood_ready:
        claim_blockers.add("same_event_h1l1_likelihood_not_ready")
    return canonicalize_json_floats({
        "h1l1_same_event_likelihood_ready": h1l1_same_event_likelihood_ready,
        "event_set_alignment_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "h1l1_likelihood_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "split_v2192_event_blocker": {
            "previous": "rerun_engine_likelihood_on_gw150914_and_gw200129",
            "now_resolved_subpiece": (
                "h1_l1_same_event_r4_likelihood_rerun"
                if h1l1_same_event_likelihood_ready
                else None
            ),
            "remaining_subpieces": [
                "gw200129_v1_detector_channel_response",
                "source_event_specific_nuisance_covariance_export",
                "public_parspec_qeft_likelihood_or_posterior_samples",
                "engine_axis_map_ready",
            ],
        },
        "route_status": (
            "parspec_source_events_h1l1_likelihood_ready_v1_policy_missing"
            if h1l1_same_event_likelihood_ready
            else "parspec_source_events_h1l1_likelihood_not_ready"
        ),
    })


def _event_likelihood_not_run(
    event: str,
    records: list[dict[str, Any]],
    reason: str,
) -> dict[str, Any]:
    return {
        "paper_event": event,
        "gwosc_event_name": records[0]["gwosc_event_name"] if records else None,
        "event_version": records[0]["event_version"] if records else None,
        "detectors": sorted({record["detector"] for record in records}),
        "detector_likelihoods": [],
        "network_likelihood": {},
        "h1l1_likelihood_ready": False,
        "not_run_reason": reason,
    }


def run_source_event_h1l1_likelihood(
    event: str,
    records: list[dict[str, Any]],
    *,
    cache_dir: Path,
    central_values: dict[str, float],
) -> dict[str, Any]:
    if sorted(record["detector"] for record in records) != list(H1L1_DETECTORS):
        return _event_likelihood_not_run(
            event,
            records,
            "h1_l1_32s_records_missing",
        )
    detector_rows = [
        detector_r4_waveform_likelihood(
            record,
            cache_dir,
            central_values=central_values,
            event_gps=float(record["event_gps"]),
        )
        for record in records
    ]
    network = network_r4_waveform_likelihood(detector_rows)
    evaluation = evaluate_r4_lalsuite_waveform_likelihood_posterior(
        detector_rows,
        network,
    )
    return canonicalize_json_floats({
        "paper_event": event,
        "gwosc_event_name": records[0]["gwosc_event_name"],
        "event_version": records[0]["event_version"],
        "detectors": [row["detector"] for row in detector_rows],
        "detector_likelihoods": detector_rows,
        "network_likelihood": network,
        "v2_187_evaluation": evaluation,
        "h1l1_likelihood_ready": evaluation[
            "r4_waveform_likelihood_posterior_ready"
        ],
    })


def diagnose_r4_parspec_same_event_h1l1_likelihood(
    *,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    v2192_path: Path = DEFAULT_V2192_PATH,
    v2191_path: Path = DEFAULT_V2191_PATH,
    nuisance_export_path: Path = DEFAULT_NUISANCE_EXPORT_PATH,
) -> dict[str, Any]:
    manifest = load_json(v2192_path)
    v2191 = load_json(v2191_path)
    nuisance = load_json(nuisance_export_path)
    central_values = nuisance_export_central_values(nuisance)
    records_by_event = source_event_h1l1_32s_records(manifest)
    status = lalsuite_status()
    if not status["available"] or not status["has_imrphenomd"]:
        event_likelihoods = [
            _event_likelihood_not_run(
                event,
                records_by_event[event],
                "lalsuite_imrphenomd_unavailable",
            )
            for event in SOURCE_EVENTS
        ]
    else:
        event_likelihoods = [
            run_source_event_h1l1_likelihood(
                event,
                records_by_event[event],
                cache_dir=cache_dir,
                central_values=central_values,
            )
            for event in SOURCE_EVENTS
        ]
    evaluation = evaluate_source_event_h1l1_likelihoods(
        event_likelihoods,
        status=status,
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.187_r4_lalsuite_waveform_likelihood_posterior",
            "v2.191_r4_parspec_qeft_source_asset_audit",
            "v2.192_r4_parspec_source_event_alignment_manifest",
            "GWOSC_GW150914_v3_H1_L1_32s_HDF5",
            "GWOSC_GW200129_065458_v1_H1_L1_32s_HDF5",
        ],
        "cache_dir": Path(cache_dir).as_posix(),
        "v2192_manifest_path": Path(v2192_path).as_posix(),
        "nuisance_export_path": Path(nuisance_export_path).as_posix(),
        "lalsuite_status": status,
        "central_values": central_values,
        "coefficient_grid": {
            "axes": list(AXES),
            "offsets": list(GRID_OFFSETS),
            "grid_points": len(GRID_OFFSETS) ** len(AXES),
        },
        "source_event_records": records_by_event,
        "event_likelihoods": event_likelihoods,
        "evaluation": evaluation,
        "h1l1_same_event_likelihood_ready": evaluation[
            "h1l1_same_event_likelihood_ready"
        ],
        "event_set_alignment_ready": False,
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
            "add_v1_detector_response_and_source_event_nuisance_covariance"
        ),
        "interpretation": (
            "The engine can now rerun the coarse R4 H1/L1 likelihood on the "
            "two ParSpec source events when LALSuite is available. This moves "
            "the event-set blocker past GW170608-only data, but it remains "
            "nonclaiming because GW200129 has V1 public strain without an "
            "engine V1 R4 channel response, the source-event nuisance covariance "
            "is still reused from the GW170608 frontier, and no public ParSpec "
            "qEFT likelihood or engine-axis map is attached."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--v2192", default=str(DEFAULT_V2192_PATH))
    parser.add_argument("--v2191", default=str(DEFAULT_V2191_PATH))
    parser.add_argument(
        "--nuisance-export",
        default=str(DEFAULT_NUISANCE_EXPORT_PATH),
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_same_event_h1l1_likelihood(
        cache_dir=Path(args.cache_dir),
        v2192_path=Path(args.v2192),
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
