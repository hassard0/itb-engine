"""Strict source-provenance overlay for R4 framework projection packets."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_projection_guard_schema import (
    evaluate_r4_projection_packet,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.symbolic_helicity_projection_fixture import (
    build_projection_packet,
    fixture_source_helicity_input,
)


VERSION = "v2.137"
PRIMARY_SOURCE_PREFIXES = ("https://arxiv.org/", "https://doi.org/")
VALID_DERIVATION_KINDS = {
    "published_framework_projection",
    "primary_source_derivation",
    "validated_public_reanalysis",
}
REQUIRED_SOURCE_PROVENANCE_FIELDS = (
    "source_backed_derivation",
    "derivation_kind",
    "primary_source_urls",
    "synthetic_fixture",
)


def _is_truthy_marker(value: Any) -> bool:
    return value not in (False, None, "", [], {}, ())


def _truthy_key_paths(value: Any, marker: str, path: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if marker in str(key).lower() and _is_truthy_marker(item):
                paths.append(child_path)
            paths.extend(_truthy_key_paths(item, marker, child_path))
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            paths.extend(_truthy_key_paths(item, marker, f"{path}[{index}]"))
    return paths


def _text_marker_paths(value: Any, marker: str, path: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        if marker in value.lower():
            paths.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if marker in str(key).lower():
                paths.append(child_path)
            paths.extend(_text_marker_paths(item, marker, child_path))
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            paths.extend(_text_marker_paths(item, marker, f"{path}[{index}]"))
    return paths


def _source_url_allowed(url: str) -> bool:
    return url.startswith(PRIMARY_SOURCE_PREFIXES)


def source_provenance_summary(packet: dict[str, Any]) -> dict[str, Any]:
    provenance = packet.get("source_provenance")
    missing_fields = list(REQUIRED_SOURCE_PROVENANCE_FIELDS)
    if isinstance(provenance, dict):
        missing_fields = [
            field for field in REQUIRED_SOURCE_PROVENANCE_FIELDS
            if field not in provenance
        ]

    primary_urls = []
    if isinstance(provenance, dict) and isinstance(
        provenance.get("primary_source_urls"),
        list,
    ):
        primary_urls = [
            str(url) for url in provenance["primary_source_urls"]
        ]

    packet_source_url = str(packet.get("source_url") or "")
    primary_urls_valid = bool(primary_urls) and all(
        _source_url_allowed(url) for url in primary_urls
    )
    source_url_is_listed = bool(packet_source_url) and packet_source_url in primary_urls
    source_backed_derivation = bool(
        isinstance(provenance, dict)
        and provenance.get("source_backed_derivation") is True
    )
    derivation_kind = (
        str(provenance.get("derivation_kind"))
        if isinstance(provenance, dict)
        and provenance.get("derivation_kind") is not None
        else ""
    )
    synthetic_fixture_declared_false = bool(
        isinstance(provenance, dict)
        and provenance.get("synthetic_fixture") is False
    )
    synthetic_fixture_paths = _truthy_key_paths(packet, "synthetic_fixture")
    fixture_text_paths = _text_marker_paths(packet, "fixture")

    source_provenance_complete = (
        isinstance(provenance, dict)
        and not missing_fields
        and source_backed_derivation
        and derivation_kind in VALID_DERIVATION_KINDS
        and synthetic_fixture_declared_false
        and primary_urls_valid
        and source_url_is_listed
        and not synthetic_fixture_paths
    )

    blockers: set[str] = set()
    if synthetic_fixture_paths:
        blockers.add("synthetic_fixture_not_real_source")
    if not source_provenance_complete:
        blockers.add("source_provenance_missing_or_incomplete")
    if primary_urls and not primary_urls_valid:
        blockers.add("source_provenance_url_not_primary_allowed")
    if packet_source_url and primary_urls and not source_url_is_listed:
        blockers.add("source_url_not_listed_in_source_provenance")

    return canonicalize_json_floats({
        "source_provenance_present": isinstance(provenance, dict),
        "missing_source_provenance_fields": missing_fields,
        "source_backed_derivation": source_backed_derivation,
        "derivation_kind": derivation_kind,
        "derivation_kind_valid": derivation_kind in VALID_DERIVATION_KINDS,
        "primary_source_urls": primary_urls,
        "primary_source_urls_valid": primary_urls_valid,
        "packet_source_url": packet_source_url,
        "source_url_is_listed": source_url_is_listed,
        "synthetic_fixture_declared_false": synthetic_fixture_declared_false,
        "truthy_synthetic_fixture_paths": synthetic_fixture_paths,
        "fixture_text_paths": fixture_text_paths,
        "source_provenance_complete": source_provenance_complete,
        "source_provenance_blockers": sorted(blockers),
    })


def evaluate_r4_source_provenance_packet(packet: dict[str, Any]) -> dict[str, Any]:
    base_guard = evaluate_r4_projection_packet(packet)
    provenance = source_provenance_summary(packet)
    strict_projection_blockers = set(base_guard["projection_blockers"])
    strict_projection_blockers.update(provenance["source_provenance_blockers"])
    strict_claim_blockers = set(base_guard["claim_blockers"])
    strict_claim_blockers.update(strict_projection_blockers)

    return canonicalize_json_floats({
        "framework": packet.get("framework"),
        "base_ready_for_framework_projection": (
            base_guard["ready_for_framework_projection"]
        ),
        "ready_for_source_backed_framework_projection": (
            not strict_projection_blockers
        ),
        "ready_for_framework_claim": not strict_claim_blockers,
        "base_guard": base_guard,
        "source_provenance_summary": provenance,
        "strict_projection_blockers": sorted(strict_projection_blockers),
        "strict_claim_blockers": sorted(strict_claim_blockers),
    })


def source_backed_control_packet() -> dict[str, Any]:
    c1 = 0.2
    c2 = 0.1
    c3 = 0.05
    source_url = "https://arxiv.org/abs/2504.12855"
    return {
        "framework": "string_tree_eft",
        "axis_family": "gravity_R4_Riemann4",
        "source_url": source_url,
        "source_type": "computed_framework_projection",
        "source_version": "Bresciani_Levati_Paradisi_arXiv_2504_12855_v2",
        "adapter_kind": "framework_native_r4_projection",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "coefficients": {
            "g_R4_c1": c1,
            "g_R4_c2": c2,
            "g_R4_c3": c3,
        },
        "derived": {
            "g_R4_plus": c1 + c2,
            "g_R4_minus_abs": math.hypot(c1 - c2, c3),
        },
        "normalization": {
            "status": "engine_lambda_r4_defined",
            "lambda_r4": 1.0,
            "definition": "unit R4 normalization for guard contract control",
        },
        "operator_projection_matrix": {
            "status": "source_backed",
            "rows": ["g_R4_plus", "g_R4_minus_abs"],
            "columns": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "basis": "Bresciani c_i spin-2 Riemann4",
        },
        "valid_energy_domain": {
            "status": "bounded_for_qg_eft",
            "s_over_lambda_r4_max": 0.25,
        },
        "uncertainty_or_covariance": {
            "status": "bounded_systematic_envelope",
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "relative_envelope": 0.0,
        },
        "ownership_metadata": {
            "framework_owned_derivation": "Bresciani spin-2 Riemann4 source family",
            "source_owned_by_framework": True,
        },
        "source_provenance": {
            "source_backed_derivation": True,
            "derivation_kind": "published_framework_projection",
            "primary_source_urls": [source_url],
            "synthetic_fixture": False,
            "derivation_scope": (
                "R4 coordinate projection and positivity control only; "
                "not a measurement likelihood."
            ),
        },
        "unitarity_bound": {
            "status": "source_backed",
            "uses_bresciani_spin2_bound": True,
        },
        "positivity_status": "checked",
        "discriminator_math": "projection_only",
    }


def v2136_symbolic_fixture_packet() -> dict[str, Any]:
    return copy.deepcopy(build_projection_packet(fixture_source_helicity_input()))


def diagnose_gravity_r4_source_provenance_guard() -> dict[str, Any]:
    packets = {
        "source_backed_control": source_backed_control_packet(),
        "v2.136_symbolic_fixture_replay": v2136_symbolic_fixture_packet(),
    }
    evaluations = {
        label: evaluate_r4_source_provenance_packet(packet)
        for label, packet in packets.items()
    }
    source_backed_ready = [
        label for label, row in evaluations.items()
        if row["ready_for_source_backed_framework_projection"]
    ]
    fixture_blocked = [
        label for label, row in evaluations.items()
        if "synthetic_fixture_not_real_source" in row["strict_projection_blockers"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in evaluations.values():
        for blocker in row["strict_projection_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.133_gravity_r4_projection_guard_schema",
            "v2.136_symbolic_helicity_projection_fixture",
            "strict_source_provenance_overlay",
        ],
        "required_source_provenance_fields": list(
            REQUIRED_SOURCE_PROVENANCE_FIELDS
        ),
        "valid_derivation_kinds": sorted(VALID_DERIVATION_KINDS),
        "evaluations": evaluations,
        "source_backed_ready_projection_packets": source_backed_ready,
        "fixture_blocked_packets": fixture_blocked,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "claimable_framework_exclusions_now": [],
        "route_status": "r4_source_provenance_guard_blocks_nested_fixture",
        "selected_next_build_action": (
            "replace_fixture_with_source_backed_string_r4_helicity_evaluation"
        ),
        "best_next_artifact": (
            "A string R4 helicity/tensor evaluation that supplies c_plus, "
            "c_minus, and source_provenance, then passes the strict R4 "
            "source-provenance guard without fixture markers."
        ),
        "interpretation": (
            "The algebraic R4 guard remains usable for packet shape, but "
            "future adapters must also pass an explicit source-provenance "
            "overlay. The v2.136 symbolic fixture is a useful contract "
            "control and is correctly blocked from source-backed projection "
            "readiness by nested synthetic-fixture metadata."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.137/"
            "gravity_r4_source_provenance_guard.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gravity_r4_source_provenance_guard()
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
