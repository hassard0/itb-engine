"""Query surface for non-promoting R4 projection adapters."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_adapter_registry_hook import (
    evaluate_r4_adapter_registry_entry,
    get_r4_adapter_registry_entry,
    r4_adapter_registry_entries,
)


VERSION = "v2.150"
ALLOWED_INTERNAL_ACTIONS = [
    "inspect_bresciani_coefficients",
    "run_positivity_diagnostics",
    "compare_relative_r4_shapes",
]
BLOCKED_CLAIM_ACTIONS = [
    "make_framework_exclusion",
    "report_absolute_type_II_string_scale",
    "attach_measurement_likelihood_without_gate",
]


def _query_row(entry: dict[str, Any]) -> dict[str, Any]:
    packet = entry["packet"]
    evaluation = evaluate_r4_adapter_registry_entry(entry)
    query_key = f"{entry['framework']}:{entry['axis_family']}"
    projection_ready = evaluation["adapter_exposed_for_internal_use"]
    return canonicalize_json_floats({
        "query_key": query_key,
        "adapter_id": entry["adapter_id"],
        "framework": entry["framework"],
        "axis_family": entry["axis_family"],
        "projection_status": (
            "internal_projection_ready_nonclaiming"
            if projection_ready
            else "projection_not_ready"
        ),
        "claim_status": "claim_blocked",
        "coefficients": packet.get("coefficients", {}),
        "derived": packet.get("derived", {}),
        "normalization": packet.get("normalization", {}),
        "source_url": packet.get("source_url"),
        "source_version": packet.get("source_version"),
        "allowed_internal_actions": list(ALLOWED_INTERNAL_ACTIONS),
        "blocked_claim_actions": list(BLOCKED_CLAIM_ACTIONS),
        "claim_blockers": evaluation["claim_blockers"],
        "exposure_blockers": evaluation["exposure_blockers"],
        "ready_for_internal_query": projection_ready,
        "ready_for_framework_claim": False,
    })


def r4_projection_query_surface_rows() -> list[dict[str, Any]]:
    return [_query_row(entry) for entry in r4_adapter_registry_entries()]


def query_r4_projection_surface(framework: str, axis_family: str) -> dict[str, Any]:
    entry = get_r4_adapter_registry_entry(
        framework=framework,
        axis_family=axis_family,
    )
    if entry is None:
        return {
            "query_key": f"{framework}:{axis_family}",
            "projection_status": "adapter_not_registered",
            "claim_status": "claim_blocked",
            "ready_for_internal_query": False,
            "ready_for_framework_claim": False,
            "not_found_blocker": "r4_adapter_not_registered",
            "allowed_internal_actions": [],
            "blocked_claim_actions": list(BLOCKED_CLAIM_ACTIONS),
        }
    return _query_row(entry)


def diagnose_r4_projection_query_surface() -> dict[str, Any]:
    rows = r4_projection_query_surface_rows()
    ready_queries = [
        row["query_key"] for row in rows if row["ready_for_internal_query"]
    ]
    claim_ready = [
        row["query_key"] for row in rows if row["ready_for_framework_claim"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    lookup_examples = {
        "registered_string_tree_eft": query_r4_projection_surface(
            "string_tree_eft",
            "gravity_R4_Riemann4",
        ),
        "unregistered_pure_gr": query_r4_projection_surface(
            "pure_gr",
            "gravity_R4_Riemann4",
        ),
    }

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.149_r4_adapter_registry_hook",
            "v2.148_policy_scoped_string_tree_r4_projection_packet",
            "projection_query_surface",
        ],
        "query_row_count": len(rows),
        "ready_internal_query_keys": ready_queries,
        "claim_ready_query_keys": claim_ready,
        "claimable_framework_exclusions_now": [],
        "rows": rows,
        "lookup_examples": lookup_examples,
        "claim_blocker_counts": dict(sorted(blocker_counts.items())),
        "route_status": "r4_projection_query_surface_ready_nonclaiming",
        "selected_next_build_action": (
            "attack_r4_claim_blockers_absolute_normalization_or_likelihood"
        ),
        "best_next_artifact": (
            "A source-backed absolute R4 normalization bridge or public "
            "R4-axis measurement likelihood. The query surface is ready; "
            "the remaining work is claim evidence, not adapter plumbing."
        ),
        "interpretation": (
            "The R4 projection can now be queried as internal diagnostics: "
            "coefficients, derived Bresciani coordinates, source URL, "
            "normalization policy, and claim blockers are all exposed in a "
            "machine-readable row. It remains non-claiming by construction."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.150/r4_projection_query_surface.json",
    )
    args = parser.parse_args()

    result = diagnose_r4_projection_query_surface()
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
