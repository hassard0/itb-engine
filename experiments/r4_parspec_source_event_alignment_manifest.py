"""GWOSC event-set alignment manifest for the ParSpec qEFT bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_qeft_source_asset_audit import DEFAULT_OUT as DEFAULT_V2191_PATH
from experiments.r4_parspec_ringdown_source_bridge import (
    CURRENT_V2187_EVENT,
    SOURCE_EVENTS,
    load_json,
)


VERSION = "v2.192"
DEFAULT_OUT = Path(
    "experiments/results/v2.192/r4_parspec_source_event_alignment_manifest.json"
)
SAMPLE_RATE_HZ = 4096
QUERY_SAMPLE_RATE_KHZ = 4
SOURCE_EVENT_PAPER_TO_GWOSC = {
    "GW150914": "GW150914",
    "GW200129": "GW200129_065458",
}
MINIMAL_ENGINE_DETECTORS = ("H1", "L1")
REQUIRED_DURATIONS = (32, 4096)


def parspec_source_event_records() -> list[dict[str, Any]]:
    return [
        {
            "paper_event": "GW150914",
            "gwosc_event_name": "GW150914",
            "event_version": "GW150914-v3",
            "version": 3,
            "catalog": "GWTC-1-confident",
            "run": "O1",
            "gps": 1126259462.4,
            "grace_id": "G184098",
            "doi": "https://doi.org/10.7935/82H3-HH23",
            "detectors": ["H1", "L1"],
            "event_version_url": "https://gwosc.org/api/v2/event-versions/GW150914-v3",
            "strain_files_url": (
                "https://gwosc.org/api/v2/event-versions/GW150914-v3/strain-files"
            ),
            "source_catalog_url": "https://gwosc.org/eventapi/html/GWTC/",
        },
        {
            "paper_event": "GW200129",
            "gwosc_event_name": "GW200129_065458",
            "event_version": "GW200129_065458-v1",
            "version": 1,
            "catalog": "GWTC-3-confident",
            "run": "O3b",
            "gps": 1264316116.4,
            "grace_id": "S200129m",
            "doi": "https://doi.org/10.7935/b024-1886",
            "detectors": ["H1", "L1", "V1"],
            "event_version_url": (
                "https://gwosc.org/api/v2/event-versions/GW200129_065458-v1"
            ),
            "strain_files_url": (
                "https://gwosc.org/api/v2/event-versions/"
                "GW200129_065458-v1/strain-files"
            ),
            "source_catalog_url": "https://gwosc.org/eventapi/html/GWTC/",
        },
    ]


def _strain_record(
    event: dict[str, Any],
    *,
    detector: str,
    duration: int,
    gps_start: int,
) -> dict[str, Any]:
    prefix = detector[0]
    event_name = str(event["gwosc_event_name"])
    version = str(event["version"])
    catalog = str(event["catalog"])
    return {
        "paper_event": event["paper_event"],
        "gwosc_event_name": event_name,
        "event_version": event["event_version"],
        "detector": detector,
        "duration": duration,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "file_format": "HDF",
        "gps_start": gps_start,
        "download_url": (
            f"https://gwosc.org/eventapi/json/{catalog}/{event_name}/"
            f"v{version}/{prefix}-{detector}_GWOSC_4KHZ_R1-"
            f"{gps_start}-{duration}.hdf5"
        ),
        "query_url": (
            f"{event['strain_files_url']}?detector={detector}"
            f"&sample-rate={QUERY_SAMPLE_RATE_KHZ}&duration={duration}"
            "&file-format=hdf5"
        ),
    }


def parspec_source_event_strain_records() -> list[dict[str, Any]]:
    events = {event["paper_event"]: event for event in parspec_source_event_records()}
    rows = []
    for detector in ("H1", "L1"):
        rows.append(
            _strain_record(
                events["GW150914"],
                detector=detector,
                duration=32,
                gps_start=1126259447,
            )
        )
        rows.append(
            _strain_record(
                events["GW150914"],
                detector=detector,
                duration=4096,
                gps_start=1126257415,
            )
        )
    for detector in ("H1", "L1", "V1"):
        rows.append(
            _strain_record(
                events["GW200129"],
                detector=detector,
                duration=32,
                gps_start=1264316101,
            )
        )
    for detector in ("H1", "L1", "V1"):
        rows.append(
            _strain_record(
                events["GW200129"],
                detector=detector,
                duration=4096,
                gps_start=1264314069,
            )
        )
    return rows


def enrich_source_event_strain_record(
    record: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    duration = int(record["duration"])
    gps_start = float(record["gps_start"])
    event_offset_seconds = float(event["gps"]) - gps_start
    return {
        **record,
        "expected_sample_count": duration * int(record["sample_rate_hz"]),
        "event_offset_seconds": event_offset_seconds,
        "event_inside_segment": 0.0 <= event_offset_seconds <= duration,
        "download_url_is_hdf5": str(record["download_url"]).endswith(".hdf5"),
        "query_url_uses_hdf5_filter": "file-format=hdf5" in str(record["query_url"]),
    }


def summarize_source_event_manifest(
    events: list[dict[str, Any]],
    strain_records: list[dict[str, Any]],
) -> dict[str, Any]:
    event_by_label = {event["paper_event"]: event for event in events}
    enriched = [
        enrich_source_event_strain_record(record, event_by_label[record["paper_event"]])
        for record in strain_records
    ]
    source_labels = [event["paper_event"] for event in events]
    missing_source_events = [
        event for event in SOURCE_EVENTS if event not in source_labels
    ]
    keys = {
        (record["paper_event"], record["detector"], int(record["duration"]))
        for record in enriched
    }
    missing_minimal_h1_l1 = [
        {
            "paper_event": event,
            "detector": detector,
            "duration": duration,
        }
        for event in SOURCE_EVENTS
        for detector in MINIMAL_ENGINE_DETECTORS
        for duration in REQUIRED_DURATIONS
        if (event, detector, duration) not in keys
    ]
    malformed = [
        record
        for record in enriched
        if record["file_format"] != "HDF"
        or int(record["sample_rate_hz"]) != SAMPLE_RATE_HZ
        or not record["download_url_is_hdf5"]
        or not record["query_url_uses_hdf5_filter"]
        or not record["event_inside_segment"]
    ]
    detector_topology = {
        event["paper_event"]: event["detectors"]
        for event in events
    }
    gw200129_requires_v1_policy = "V1" in detector_topology.get("GW200129", [])
    return canonicalize_json_floats({
        "events": events,
        "strain_records": enriched,
        "source_event_labels": source_labels,
        "gwosc_event_names": {
            event["paper_event"]: event["gwosc_event_name"]
            for event in events
        },
        "missing_source_events": missing_source_events,
        "minimal_h1_l1_records_missing": missing_minimal_h1_l1,
        "malformed_records": [
            {
                "paper_event": record["paper_event"],
                "detector": record["detector"],
                "duration": record["duration"],
            }
            for record in malformed
        ],
        "detector_topology_by_event": detector_topology,
        "gw200129_requires_v1_policy": gw200129_requires_v1_policy,
        "source_event_public_strain_urls_ready": (
            not missing_source_events
            and not missing_minimal_h1_l1
            and not malformed
        ),
    })


def evaluate_parspec_event_set_alignment_manifest(
    manifest: dict[str, Any],
    *,
    current_engine_events: tuple[str, ...] = (CURRENT_V2187_EVENT,),
) -> dict[str, Any]:
    blockers: set[str] = set()
    summary = manifest["source_event_manifest_summary"]
    if not summary["source_event_public_strain_urls_ready"]:
        blockers.add("parspec_source_event_public_strain_urls_not_ready")
    if tuple(summary["source_event_labels"]) != SOURCE_EVENTS:
        blockers.add("parspec_source_event_labels_not_exact")
    if tuple(current_engine_events) != SOURCE_EVENTS:
        blockers.add("current_engine_event_set_not_parspec_source_events")
    if summary["gw200129_requires_v1_policy"]:
        blockers.add("gw200129_v1_detector_topology_policy_missing")

    v2191 = manifest["v2191_remaining_state"]
    if "public_parspec_qeft_likelihood_or_posterior_samples_missing" in v2191[
        "remaining_contract_blockers_after_asset_audit"
    ]:
        blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
    for blocker in (
        "operator_basis_map_missing",
        "engine_axis_orientation_missing",
        "axis_normalization_missing",
    ):
        if blocker in v2191["remaining_contract_blockers_after_asset_audit"]:
            blockers.add(blocker)

    event_set_manifest_ready = not (
        {"parspec_source_event_public_strain_urls_not_ready"} & blockers
    )
    event_set_alignment_ready = event_set_manifest_ready and not (
        {
            "current_engine_event_set_not_parspec_source_events",
            "gw200129_v1_detector_topology_policy_missing",
        }
        & blockers
    )
    return canonicalize_json_floats({
        "event_set_manifest_ready": event_set_manifest_ready,
        "event_set_alignment_ready": event_set_alignment_ready,
        "source_event_public_strain_urls_ready": summary[
            "source_event_public_strain_urls_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "alignment_blockers": sorted(blockers),
        "split_v2191_event_blocker": {
            "previous": "event_set_mismatch_gw170608_vs_gw150914_gw200129",
            "now_resolved_subpiece": (
                "gwosc_source_event_versions_and_hdf5_urls_identified"
            ),
            "remaining_subpieces": [
                "rerun_engine_likelihood_on_gw150914_and_gw200129",
                "gw200129_v1_detector_topology_policy",
                "public_parspec_qeft_likelihood_or_posterior_samples",
            ],
        },
        "route_status": (
            "parspec_source_event_gwosc_manifest_ready_alignment_not_run"
            if event_set_manifest_ready
            else "parspec_source_event_gwosc_manifest_blocked"
        ),
    })


def diagnose_r4_parspec_source_event_alignment_manifest(
    *,
    v2191_path: str | Path = DEFAULT_V2191_PATH,
) -> dict[str, Any]:
    events = parspec_source_event_records()
    strains = parspec_source_event_strain_records()
    summary = summarize_source_event_manifest(events, strains)
    v2191 = load_json(v2191_path)
    manifest = canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.187_r4_lalsuite_waveform_likelihood_posterior",
            "v2.188_r4_parspec_ringdown_source_bridge",
            "v2.191_r4_parspec_qeft_source_asset_audit",
            "GWOSC_api_event_versions_GW150914_v3",
            "GWOSC_api_event_versions_GW200129_065458_v1",
        ],
        "required_paper_source_events": list(SOURCE_EVENTS),
        "current_engine_events": [CURRENT_V2187_EVENT],
        "source_event_manifest_summary": summary,
        "v2191_remaining_state": {
            "route_status": v2191["route_status"],
            "remaining_contract_blockers_after_asset_audit": v2191[
                "remaining_contract_blockers_after_asset_audit"
            ],
        },
        "alignment_contract": {
            "required_minimal_engine_run": (
                "Run the R4 LALSuite/GWOSC likelihood path on GW150914 and "
                "GW200129_065458, using at least H1/L1 4 kHz 32 s HDF5 strain."
            ),
            "detector_topology_policy_needed": (
                "GW200129_065458-v1 has H1/L1/V1 strain. A claim-grade rerun "
                "must either include V1 or justify an H1/L1-only projection "
                "against the ParSpec source analysis."
            ),
            "nonclaiming_until": [
                "same_event_likelihood_rerun_complete",
                "public_parspec_qeft_likelihood_or_covariance_attached",
                "engine_axis_map_ready",
                "systematics_export_ready",
                "external_adversarial_review_complete",
            ],
        },
    })
    evaluation = evaluate_parspec_event_set_alignment_manifest(manifest)
    return canonicalize_json_floats({
        **manifest,
        "evaluation": evaluation,
        "event_set_manifest_ready": evaluation["event_set_manifest_ready"],
        "event_set_alignment_ready": evaluation["event_set_alignment_ready"],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "rerun_r4_lalsuite_likelihood_on_gw150914_gw200129_with_v1_policy"
        ),
        "interpretation": (
            "The ParSpec source events are now mapped to exact GWOSC event "
            "versions and public 4 kHz HDF5 strain URLs. This resolves the "
            "event-discovery subpiece, but not the event-set mismatch itself: "
            "the engine still has to rerun the R4 likelihood on GW150914 and "
            "GW200129_065458, decide the V1 policy for GW200129, and attach a "
            "public qEFT likelihood or covariance before any claim is allowed."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2191", default=str(DEFAULT_V2191_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_source_event_alignment_manifest(
        v2191_path=Path(args.v2191)
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
