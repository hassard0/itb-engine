"""Public GW170608 strain connector readiness for v2.106."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


VERSION = "v2.106"
EVENT = "GW170608"
EVENT_VERSION = "GW170608-v3"
CATALOG = "GWTC-1-confident"
GPS = 1180922494.5
SAMPLE_RATE_HZ = 4096
DETECTORS = ("H1", "L1")
REQUIRED_DURATIONS = (32, 4096)


def gw170608_v3_event_record() -> dict[str, Any]:
    return {
        "name": EVENT,
        "event_version": EVENT_VERSION,
        "version": 3,
        "catalog": CATALOG,
        "run": "O2",
        "gps": GPS,
        "detectors": list(DETECTORS),
        "event_version_url": "https://gwosc.org/api/v2/event-versions/GW170608-v3",
        "strain_files_url": (
            "https://gwosc.org/api/v2/event-versions/GW170608-v3/strain-files"
        ),
        "source_url": "https://gwosc.org/GWTC-1/",
    }


def gw170608_v3_strain_records() -> list[dict[str, Any]]:
    return [
        {
            "detector": "H1",
            "duration": 32,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "gps_start": 1180922479,
            "file_format": "HDF",
            "download_url": (
                "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170608/"
                "v3/H-H1_GWOSC_4KHZ_R1-1180922479-32.hdf5"
            ),
        },
        {
            "detector": "L1",
            "duration": 32,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "gps_start": 1180922479,
            "file_format": "HDF",
            "download_url": (
                "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170608/"
                "v3/L-L1_GWOSC_4KHZ_R1-1180922479-32.hdf5"
            ),
        },
        {
            "detector": "H1",
            "duration": 4096,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "gps_start": 1180920447,
            "file_format": "HDF",
            "download_url": (
                "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170608/"
                "v3/H-H1_GWOSC_4KHZ_R1-1180920447-4096.hdf5"
            ),
        },
        {
            "detector": "L1",
            "duration": 4096,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "gps_start": 1180920447,
            "file_format": "HDF",
            "download_url": (
                "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170608/"
                "v3/L-L1_GWOSC_4KHZ_R1-1180920447-4096.hdf5"
            ),
        },
    ]


def _record_key(record: dict[str, Any]) -> tuple[str, int]:
    return str(record["detector"]), int(record["duration"])


def enrich_strain_record(record: dict[str, Any]) -> dict[str, Any]:
    duration = int(record["duration"])
    gps_start = float(record["gps_start"])
    event_offset_seconds = GPS - gps_start
    return {
        **record,
        "expected_sample_count": duration * int(record["sample_rate_hz"]),
        "event_offset_seconds": event_offset_seconds,
        "event_inside_segment": 0.0 <= event_offset_seconds <= duration,
        "query_url": (
            "https://gwosc.org/api/v2/event-versions/GW170608-v3/"
            f"strain-files?detector={record['detector']}"
            f"&sample-rate=4&duration={duration}&file-format=hdf5"
        ),
    }


def summarize_strain_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = [enrich_strain_record(record) for record in records]
    keys = {_record_key(record) for record in enriched}
    missing = [
        {"detector": detector, "duration": duration}
        for detector in DETECTORS
        for duration in REQUIRED_DURATIONS
        if (detector, duration) not in keys
    ]
    malformed = [
        record
        for record in enriched
        if record["file_format"] != "HDF"
        or record["sample_rate_hz"] != SAMPLE_RATE_HZ
        or not record["download_url"].endswith(".hdf5")
        or not record["event_inside_segment"]
    ]
    return {
        "records": enriched,
        "record_count": len(enriched),
        "required_record_count": len(DETECTORS) * len(REQUIRED_DURATIONS),
        "missing_required_records": missing,
        "malformed_records": [
            {"detector": row["detector"], "duration": row["duration"]}
            for row in malformed
        ],
        "public_strain_urls_ready": not missing and not malformed,
    }


def synthetic_ready_public_strain_connector() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_public_strain_connector",
        "event_record": gw170608_v3_event_record(),
        "strain_records": gw170608_v3_strain_records(),
        "hdf5_loader": {
            "status": "ready",
            "required_datasets": ["/strain/Strain", "/meta/GPSstart"],
        },
        "strain_bytes": {
            "status": "ready",
            "cache_policy": "local_verified_hashes",
        },
        "alpha_waveform_residual": {
            "status": "ready",
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
        },
        "source_native_packet_target": "v2.105_alpha_likelihood_stub_packet",
        "synthetic_fixture": True,
    }


def current_public_strain_connector() -> dict[str, Any]:
    return {
        "label": "current_public_strain_connector",
        "event_record": gw170608_v3_event_record(),
        "strain_records": gw170608_v3_strain_records(),
        "hdf5_loader": {
            "status": "contract_defined_not_run",
            "required_datasets": ["/strain/Strain", "/meta/GPSstart"],
            "next_work_item": "implement_hdf5_strain_loader_smoke_test",
        },
        "strain_bytes": {
            "status": "not_downloaded",
            "reason": "connector currently validates URLs but does not cache HDF5 bytes",
        },
        "alpha_waveform_residual": {
            "status": "missing",
            "next_work_item": "replace_quadratic_stub_with_strain_residual",
        },
        "source_native_packet_target": "v2.105_alpha_likelihood_stub_packet",
        "synthetic_fixture": False,
    }


def evaluate_public_strain_connector(connector: dict[str, Any]) -> dict[str, Any]:
    blockers: set[str] = set()
    event_record = connector.get("event_record")
    if not isinstance(event_record, dict) or event_record.get("event_version") != EVENT_VERSION:
        blockers.add("event_version_not_gw170608_v3")
    elif set(event_record.get("detectors") or []) != set(DETECTORS):
        blockers.add("event_detectors_not_h1_l1")

    summary = summarize_strain_records(list(connector.get("strain_records") or []))
    if not summary["public_strain_urls_ready"]:
        blockers.add("public_strain_urls_not_ready")

    hdf5_loader = connector.get("hdf5_loader")
    if not isinstance(hdf5_loader, dict) or hdf5_loader.get("status") != "ready":
        blockers.add("hdf5_loader_not_run")

    strain_bytes = connector.get("strain_bytes")
    if not isinstance(strain_bytes, dict) or strain_bytes.get("status") != "ready":
        blockers.add("strain_bytes_not_ingested")

    residual = connector.get("alpha_waveform_residual")
    if not isinstance(residual, dict) or residual.get("status") != "ready":
        blockers.add("alpha_waveform_residual_not_connected")

    if connector.get("source_native_packet_target") != "v2.105_alpha_likelihood_stub_packet":
        blockers.add("source_native_packet_target_not_v2_105")

    synthetic_fixture = bool(connector.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_public_strain_run")
    claim_blockers.add("g8_joint_component_missing")

    connector_ready = not blockers
    return {
        "label": connector.get("label", "unnamed_public_strain_connector"),
        "event_version": (
            event_record.get("event_version") if isinstance(event_record, dict) else None
        ),
        "synthetic_fixture": synthetic_fixture,
        "strain_summary": summary,
        "connector_ready": connector_ready,
        "claim_ready": connector_ready and not synthetic_fixture,
        "connector_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "public_strain_connector_claim_ready"
            if connector_ready and not synthetic_fixture
            else "public_strain_connector_rejected_or_nonpromoting"
        ),
    }


def diagnose_gw_public_strain_connector() -> dict[str, Any]:
    connectors = [
        synthetic_ready_public_strain_connector(),
        current_public_strain_connector(),
    ]
    evaluations = [evaluate_public_strain_connector(connector) for connector in connectors]
    ready = [row["label"] for row in evaluations if row["connector_ready"]]
    claim_ready = [row["label"] for row in evaluations if row["claim_ready"]]
    current = evaluations[1]

    return {
        "version": VERSION,
        "basis": [
            "v2.105_alpha_likelihood_stub",
            "GWOSC_api_event_versions_GW170608_v3",
            "GWOSC_api_strain_files_H1_L1_4kHz_HDF5",
        ],
        "event_record": gw170608_v3_event_record(),
        "strain_records": [
            enrich_strain_record(record) for record in gw170608_v3_strain_records()
        ],
        "sample_connector_count": len(evaluations),
        "connector_ready_samples": ready,
        "claim_ready_samples": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "evaluations": evaluations,
        "current_public_connector_blockers": current["connector_blockers"],
        "route_status": "public_strain_urls_connected_hdf5_loader_missing",
        "selected_next_build_action": "implement_hdf5_strain_loader_smoke_test",
        "best_next_artifact": (
            "A small HDF5 loader that downloads or reads the 32-second H1/L1 "
            "GW170608 files, verifies /strain/Strain sample counts and GPS "
            "metadata, and exposes arrays to the alpha likelihood harness."
        ),
        "interpretation": (
            "The public strain endpoint is now connected at the URL and segment "
            "level. The remaining implementation work is to ingest the HDF5 "
            "bytes and replace the synthetic alpha residual with one computed "
            "from public strain."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.106/gw_public_strain_connector.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_public_strain_connector()
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
