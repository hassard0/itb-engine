"""Executable intake gate for external evidence packets (v2.93)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.external_evidence_packet_contract import (
    COMMON_CLAIM_GATES,
    diagnose_external_evidence_packet_contract,
    external_evidence_contract_rows,
)


def _contract_by_route() -> dict[str, dict[str, Any]]:
    return {
        row["route"]: row
        for row in external_evidence_contract_rows()
    }


def _missing(value: Any) -> bool:
    return value in (None, "", [], {})


def _claim_gate_results(packet: dict[str, Any]) -> dict[str, bool]:
    declared = packet.get("claim_gates")
    if not isinstance(declared, dict):
        declared = {}

    results: dict[str, bool] = {}
    for gate in COMMON_CLAIM_GATES:
        if gate == "synthetic_fixture_false":
            results[gate] = not bool(packet.get("synthetic_fixture"))
        else:
            results[gate] = bool(declared.get(gate))
    return results


def evaluate_external_evidence_packet(packet: dict[str, Any]) -> dict[str, Any]:
    route = str(packet.get("route") or "")
    contract = _contract_by_route().get(route)
    blockers: set[str] = set()

    if contract is None:
        return {
            "label": packet.get("label", "unnamed_external_packet"),
            "route": route,
            "contract_found": False,
            "missing_fields": [],
            "claim_gate_results": {},
            "active_rejection_tests": [],
            "unknown_rejection_tests": sorted(
                str(item) for item in packet.get("known_rejection_tests", [])
            ),
            "schema_ready": False,
            "claim_ready": False,
            "blockers": ["unknown_route_no_contract"],
            "status": "external_packet_rejected_no_contract",
        }

    required_fields = contract["minimum_required_fields"]
    missing_fields = [
        field for field in required_fields
        if _missing(packet.get(field))
    ]
    if missing_fields:
        blockers.add("missing_required_fields")

    known_rejection_tests = {
        str(item) for item in packet.get("known_rejection_tests", [])
    }
    allowed_rejection_tests = set(contract["route_specific_rejection_tests"])
    active_rejection_tests = sorted(known_rejection_tests & allowed_rejection_tests)
    unknown_rejection_tests = sorted(known_rejection_tests - allowed_rejection_tests)
    blockers.update(active_rejection_tests)
    if unknown_rejection_tests:
        blockers.add("unknown_rejection_tests_for_route")

    claim_gate_results = _claim_gate_results(packet)
    failed_claim_gates = [
        gate for gate, passed in claim_gate_results.items()
        if not passed
    ]
    for gate in failed_claim_gates:
        blockers.add(f"claim_gate_not_satisfied:{gate}")

    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    if synthetic_fixture:
        blockers.add("synthetic_fixture_not_real_source")

    schema_ready = (
        not missing_fields
        and not active_rejection_tests
        and not unknown_rejection_tests
    )
    claim_ready = schema_ready and not blockers
    return {
        "label": packet.get("label", route),
        "route": route,
        "contract_found": True,
        "external_object": contract["external_object"],
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing_fields,
        "claim_gate_results": claim_gate_results,
        "failed_claim_gates": failed_claim_gates,
        "active_rejection_tests": active_rejection_tests,
        "unknown_rejection_tests": unknown_rejection_tests,
        "schema_ready": schema_ready,
        "claim_ready": claim_ready,
        "blockers": sorted(blockers),
        "status": (
            "external_packet_claim_ready"
            if claim_ready
            else "external_packet_rejected_or_nonpromoting"
        ),
    }


def synthetic_complete_external_packet(route: str) -> dict[str, Any]:
    contract = _contract_by_route()[route]
    packet = {
        field: f"synthetic_{field}"
        for field in contract["minimum_required_fields"]
    }
    packet.update(
        {
            "label": f"synthetic_complete_{route}",
            "route": route,
            "synthetic_fixture": True,
            "claim_gates": {
                gate: True
                for gate in COMMON_CLAIM_GATES
                if gate != "synthetic_fixture_false"
            },
            "known_rejection_tests": [],
        }
    )
    return packet


def incomplete_g8_packet() -> dict[str, Any]:
    return {
        "label": "incomplete_g8_packet",
        "route": "future_public_g8_measurement_ingestion",
        "source_url": "https://doi.org/10.0000/incomplete",
        "synthetic_fixture": False,
        "claim_gates": {
            "primary_or_release_source_present": True,
        },
        "known_rejection_tests": [
            "missing_public_likelihood_or_covariance",
            "wilson_coefficient_normalization_not_engine_g8",
        ],
    }


def native_packet_missing_ownership() -> dict[str, Any]:
    packet = synthetic_complete_external_packet(
        "framework_specific_native_tower_search"
    )
    packet.update(
        {
            "label": "native_packet_missing_ownership",
            "synthetic_fixture": False,
            "ownership_metadata": "",
            "known_rejection_tests": ["ownership_metadata_missing"],
        }
    )
    return packet


def unknown_route_packet() -> dict[str, Any]:
    return {
        "label": "unknown_route_packet",
        "route": "unregistered_external_route",
        "synthetic_fixture": False,
        "known_rejection_tests": ["unmapped_route"],
    }


def diagnose_external_evidence_intake_gate() -> dict[str, Any]:
    contract = diagnose_external_evidence_packet_contract()
    sample_packets = [
        synthetic_complete_external_packet("future_public_g8_measurement_ingestion"),
        incomplete_g8_packet(),
        native_packet_missing_ownership(),
        unknown_route_packet(),
    ]
    evaluations = [
        evaluate_external_evidence_packet(packet)
        for packet in sample_packets
    ]
    claim_ready = [
        row["label"] for row in evaluations
        if row["claim_ready"]
    ]
    schema_ready = [
        row["label"] for row in evaluations
        if row["schema_ready"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in evaluations:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.93",
        "basis": [
            "v2.92_external_evidence_packet_contract",
            "v2.91_post_g8_direct_measurement_frontier",
        ],
        "gate_scope": "external_evidence_packet_intake",
        "contract_route_status": contract["route_status"],
        "contract_route_count": contract["route_count"],
        "sample_packet_count": len(evaluations),
        "schema_ready_sample_packets": schema_ready,
        "claim_ready_sample_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "evaluations": evaluations,
        "route_status": "external_evidence_intake_gate_ready_no_real_packet",
        "best_next_artifact": (
            "Use this gate on a real external packet; do not promote synthetic "
            "or contract-incomplete packets."
        ),
        "interpretation": (
            "The intake gate is executable. It can distinguish schema-complete "
            "fixtures from real claim evidence and rejects unknown, incomplete, "
            "or route-rejected packets before discriminator promotion."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.93/external_evidence_intake_gate.json",
    )
    args = parser.parse_args()

    result = diagnose_external_evidence_intake_gate()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
