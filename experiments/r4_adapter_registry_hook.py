"""Non-promoting registry hook for policy-scoped R4 adapter packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_projection_guard_schema import (
    evaluate_r4_projection_packet,
)
from experiments.gravity_r4_source_provenance_guard import (
    evaluate_r4_source_provenance_packet,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.policy_scoped_string_tree_r4_projection_packet import (
    REMAINING_ABSOLUTE_NORMALIZATION_GAPS,
    evaluate_policy_scoped_string_tree_r4_packet,
    policy_scoped_string_tree_r4_projection_packet,
)


VERSION = "v2.149"
VALID_NONCLAIMING_REGISTRATION_SCOPES = {
    "internal_projection_algebra",
    "adapter_contract_testing",
    "positivity_frontier_wiring",
}


def r4_adapter_registry_entries() -> list[dict[str, Any]]:
    packet = policy_scoped_string_tree_r4_projection_packet()
    return [
        {
            "adapter_id": "string_tree_eft_r4_shape_policy_unit_v1",
            "framework": "string_tree_eft",
            "axis_family": "gravity_R4_Riemann4",
            "packet_factory": (
                "experiments.policy_scoped_string_tree_r4_projection_packet."
                "policy_scoped_string_tree_r4_projection_packet"
            ),
            "registration_scope": "internal_projection_algebra",
            "claim_path_enabled": False,
            "framework_registry_mutation": False,
            "measurement_likelihood_attached": False,
            "absolute_normalization_attached": False,
            "packet": packet,
        }
    ]


def evaluate_r4_adapter_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    packet = entry.get("packet")
    exposure_blockers: set[str] = set()
    if not isinstance(packet, dict):
        exposure_blockers.add("adapter_packet_missing")
        packet = {}

    if entry.get("registration_scope") not in VALID_NONCLAIMING_REGISTRATION_SCOPES:
        exposure_blockers.add("registration_scope_not_nonclaiming")
    if entry.get("claim_path_enabled") is not False:
        exposure_blockers.add("claim_path_not_disabled")
    if entry.get("framework_registry_mutation") is not False:
        exposure_blockers.add("framework_registry_mutation_not_allowed")
    if entry.get("measurement_likelihood_attached") is not False:
        exposure_blockers.add("measurement_likelihood_must_not_be_attached")
    if entry.get("absolute_normalization_attached") is not False:
        exposure_blockers.add("absolute_normalization_must_not_be_attached")

    policy_scope = evaluate_policy_scoped_string_tree_r4_packet(packet)
    base_guard = evaluate_r4_projection_packet(packet)
    strict_guard = evaluate_r4_source_provenance_packet(packet)
    if not policy_scope["ready_for_policy_scoped_projection"]:
        exposure_blockers.add("policy_scoped_packet_not_ready")
    if not base_guard["ready_for_framework_projection"]:
        exposure_blockers.add("base_projection_guard_not_ready")
    if not strict_guard["ready_for_source_backed_framework_projection"]:
        exposure_blockers.add("strict_source_guard_not_ready")

    claim_blockers = set(strict_guard["strict_claim_blockers"])
    claim_blockers.update(REMAINING_ABSOLUTE_NORMALIZATION_GAPS)
    claim_blockers.add("registry_claim_path_disabled")

    return canonicalize_json_floats({
        "adapter_id": entry.get("adapter_id"),
        "framework": entry.get("framework"),
        "axis_family": entry.get("axis_family"),
        "registration_scope": entry.get("registration_scope"),
        "adapter_exposed_for_internal_use": not exposure_blockers,
        "claim_promotion_allowed": False,
        "claimable_framework_exclusion_now": False,
        "framework_registry_mutation": entry.get("framework_registry_mutation"),
        "policy_scope_ready": policy_scope["ready_for_policy_scoped_projection"],
        "base_projection_ready": base_guard["ready_for_framework_projection"],
        "strict_source_projection_ready": (
            strict_guard["ready_for_source_backed_framework_projection"]
        ),
        "guard_ready_for_framework_claim": strict_guard["ready_for_framework_claim"],
        "exposure_blockers": sorted(exposure_blockers),
        "claim_blockers": sorted(claim_blockers),
    })


def get_r4_adapter_registry_entry(
    *,
    framework: str,
    axis_family: str,
) -> dict[str, Any] | None:
    for entry in r4_adapter_registry_entries():
        if entry["framework"] == framework and entry["axis_family"] == axis_family:
            return entry
    return None


def diagnose_r4_adapter_registry_hook() -> dict[str, Any]:
    entries = r4_adapter_registry_entries()
    evaluations = [
        evaluate_r4_adapter_registry_entry(entry) for entry in entries
    ]
    internal_ready = [
        row["adapter_id"] for row in evaluations
        if row["adapter_exposed_for_internal_use"]
    ]
    claim_ready = [
        row["adapter_id"] for row in evaluations
        if row["claimable_framework_exclusion_now"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in evaluations:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    lookup_control = get_r4_adapter_registry_entry(
        framework="string_tree_eft",
        axis_family="gravity_R4_Riemann4",
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.148_policy_scoped_string_tree_r4_projection_packet",
            "v2.147_r4_shape_normalization_policy",
            "non_promoting_adapter_registry_hook",
        ],
        "registry_entry_count": len(entries),
        "internal_projection_ready_adapters": internal_ready,
        "claim_promotion_ready_adapters": claim_ready,
        "claimable_framework_exclusions_now": [],
        "framework_registry_mutated": any(
            bool(entry.get("framework_registry_mutation")) for entry in entries
        ),
        "lookup_control_found": lookup_control is not None,
        "evaluations": evaluations,
        "claim_blocker_counts": dict(sorted(blocker_counts.items())),
        "route_status": "r4_adapter_registry_hook_ready_nonpromoting",
        "selected_next_build_action": (
            "wire_r4_registry_hook_into_projection_query_surface"
        ),
        "best_next_artifact": (
            "A query-surface or frontier-side reader that can consume the "
            "registered R4 projection packet for internal diagnostics while "
            "preserving the measurement-likelihood and absolute-normalization "
            "claim blockers."
        ),
        "interpretation": (
            "The policy-scoped string_tree_eft R4 packet is now exposed through "
            "a non-promoting adapter registry hook. This makes the projection "
            "queryable by future internal tooling without mutating the live "
            "framework registry or creating a framework exclusion."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.149/r4_adapter_registry_hook.json",
    )
    args = parser.parse_args()

    result = diagnose_r4_adapter_registry_hook()
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
