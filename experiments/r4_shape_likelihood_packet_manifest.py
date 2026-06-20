"""Manifest schema for future public R4 shape likelihood packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_public_shape_likelihood_search import (
    r4_shape_likelihood_acceptance_contract,
)


VERSION = "v2.160"

REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "source_url",
    "source_type",
    "target_axes",
    "likelihood",
    "axis_mapping",
    "normalization",
    "domain",
    "systematics",
    "provenance",
    "discriminator_math",
    "claim_controls",
)
VALID_LIKELIHOOD_STATUSES = {
    "public_covariance_matrix",
    "public_likelihood_samples",
    "public_log_likelihood_grid",
}
TARGET_AXES = (
    "g_R4_c1",
    "g_R4_c2",
    "g_R4_c3",
    "g_R4_plus",
    "g_R4_minus_abs",
)


def r4_shape_likelihood_packet_schema() -> dict[str, Any]:
    return {
        "version": VERSION,
        "required_packet_fields": list(REQUIRED_PACKET_FIELDS),
        "target_axes": list(TARGET_AXES),
        "valid_likelihood_statuses": sorted(VALID_LIKELIHOOD_STATUSES),
        "acceptance_contract": r4_shape_likelihood_acceptance_contract(),
        "claim_rule": (
            "All schema fields and acceptance criteria must pass before the "
            "packet can be considered claim evidence. This schema by itself "
            "does not make any framework claim."
        ),
    }


def empty_r4_shape_likelihood_packet() -> dict[str, Any]:
    return {
        "packet_id": "empty_r4_shape_likelihood_packet",
        "source_url": "",
        "source_type": "",
        "target_axes": [],
        "likelihood": {},
        "axis_mapping": {},
        "normalization": {},
        "domain": {},
        "systematics": {},
        "provenance": {},
        "discriminator_math": "projection_only",
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
        },
    }


def synthetic_complete_r4_shape_likelihood_packet() -> dict[str, Any]:
    return {
        "packet_id": "synthetic_complete_r4_shape_likelihood_packet",
        "source_url": "https://example.invalid/synthetic-r4-likelihood",
        "source_type": "unit_test_control",
        "target_axes": list(TARGET_AXES),
        "likelihood": {
            "status": "public_covariance_matrix",
            "central_values": {
                "g_R4_c1": 0.5,
                "g_R4_c2": 0.5,
                "g_R4_c3": 0.0,
            },
            "covariance": [
                [0.01, 0.0, 0.0],
                [0.0, 0.01, 0.0],
                [0.0, 0.0, 0.01],
            ],
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
        },
        "axis_mapping": {
            "status": "maps_to_bresciani_r4_axes",
            "mapped_axes": list(TARGET_AXES),
        },
        "normalization": {
            "axis_normalization_declared": True,
            "uses_numeric_lambda_r4_scale": False,
            "normalization_scope": "shape_likelihood_only",
        },
        "domain": {
            "status": "bounded_for_qg_eft",
            "shared_domain_with_query_row": True,
        },
        "systematics": {
            "status": "declared",
            "items": ["synthetic_control_only"],
        },
        "provenance": {
            "reproducible_data_or_code": True,
            "public_likelihood_or_covariance": True,
            "synthetic_control": True,
        },
        "discriminator_math": "excludes_registered_framework",
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "synthetic_control_not_claim_evidence": True,
        },
    }


def evaluate_r4_shape_likelihood_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_PACKET_FIELDS
        if field not in packet or packet[field] in (None, "", {}, [], ())
    ]
    blockers: set[str] = set(missing_fields)
    target_axes = set(packet.get("target_axes", []))
    if not set(TARGET_AXES).issubset(target_axes):
        blockers.add("target_axes_incomplete")

    likelihood = packet.get("likelihood")
    if not isinstance(likelihood, dict):
        blockers.add("likelihood_missing")
        likelihood_status = ""
    else:
        likelihood_status = str(likelihood.get("status") or "")
        if likelihood_status not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("likelihood_status_not_public_engine_usable")
        if not set(likelihood.get("axes", [])).issubset(set(TARGET_AXES)):
            blockers.add("likelihood_axes_not_subset_of_target_axes")
        if not likelihood.get("central_values"):
            blockers.add("likelihood_central_values_missing")

    mapping = packet.get("axis_mapping")
    if not isinstance(mapping, dict) or mapping.get("status") != "maps_to_bresciani_r4_axes":
        blockers.add("axis_mapping_not_bresciani_r4")
    elif not set(TARGET_AXES).issubset(set(mapping.get("mapped_axes", []))):
        blockers.add("axis_mapping_axes_incomplete")

    normalization = packet.get("normalization")
    if (
        not isinstance(normalization, dict)
        or normalization.get("axis_normalization_declared") is not True
    ):
        blockers.add("axis_normalization_not_declared")

    domain = packet.get("domain")
    if not isinstance(domain, dict) or domain.get("shared_domain_with_query_row") is not True:
        blockers.add("domain_not_shared_with_query_row")

    systematics = packet.get("systematics")
    if not isinstance(systematics, dict) or systematics.get("status") != "declared":
        blockers.add("systematics_not_declared")

    provenance = packet.get("provenance")
    if not isinstance(provenance, dict):
        blockers.add("provenance_missing")
    else:
        if provenance.get("public_likelihood_or_covariance") is not True:
            blockers.add("public_likelihood_or_covariance_missing")
        if provenance.get("reproducible_data_or_code") is not True:
            blockers.add("reproducible_data_or_code_missing")

    if packet.get("discriminator_math") != "excludes_registered_framework":
        blockers.add("excluding_discriminator_math_missing")

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_must_remain_disabled_until_external_review")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_must_remain_disabled_until_external_review")
        if controls.get("synthetic_control_not_claim_evidence") is True:
            blockers.add("synthetic_control_not_claim_evidence")

    ready_packet = not blockers or blockers == {"synthetic_control_not_claim_evidence"}
    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "likelihood_status": likelihood_status,
        "ready_for_engine_likelihood_packet": ready_packet,
        "ready_for_framework_claim": False,
        "blockers": sorted(blockers),
        "missing_required_fields": sorted(missing_fields),
    })


def diagnose_r4_shape_likelihood_packet_manifest() -> dict[str, Any]:
    empty = empty_r4_shape_likelihood_packet()
    synthetic = synthetic_complete_r4_shape_likelihood_packet()
    evaluations = {
        "empty_r4_shape_likelihood_packet": (
            evaluate_r4_shape_likelihood_packet(empty)
        ),
        "synthetic_complete_r4_shape_likelihood_packet": (
            evaluate_r4_shape_likelihood_packet(synthetic)
        ),
    }

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.159_r4_public_shape_likelihood_search",
            "r4_likelihood_packet_contract",
        ],
        "schema": r4_shape_likelihood_packet_schema(),
        "example_packets": {
            "empty": empty,
            "synthetic_complete_control": synthetic,
        },
        "evaluations": evaluations,
        "ready_likelihood_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "r4_shape_likelihood_packet_manifest_ready_nonclaiming",
        "selected_next_build_action": (
            "monitor_or_ingest_future_r4_likelihood_sources"
        ),
        "best_next_artifact": (
            "A future evidence ingester can use this manifest to validate "
            "GW/GREFT likelihood packets before they touch framework-claim "
            "logic."
        ),
        "interpretation": (
            "The engine now has a reusable packet schema for future public R4 "
            "shape likelihood evidence. The schema is not itself evidence and "
            "does not enable a framework claim."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.160/"
            "r4_shape_likelihood_packet_manifest.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_shape_likelihood_packet_manifest()
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
