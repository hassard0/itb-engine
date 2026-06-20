"""Attach symbolic Lambda_R4 policy sidecars to R4 query rows."""

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
    get_r4_adapter_registry_entry,
    r4_adapter_registry_entries,
)
from experiments.r4_lambda_unit_policy import (
    NUMERIC_CLAIM_BLOCKERS,
    evaluate_symbolic_lambda_r4_sidecar,
    symbolic_lambda_r4_sidecar_for_packet,
)
from experiments.r4_projection_query_surface import (
    BLOCKED_CLAIM_ACTIONS,
    query_r4_projection_surface,
)


VERSION = "v2.155"
SYMBOLIC_INTERNAL_ACTION = "inspect_symbolic_lambda_r4_alpha_prime_policy"
SYMBOLIC_BLOCKED_CLAIM_ACTION = "use_symbolic_alpha_prime_policy_for_framework_claim"


def _ordered_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def attach_symbolic_lambda_policy_to_query_row(
    row: dict[str, Any],
    packet: dict[str, Any],
) -> dict[str, Any]:
    sidecar = symbolic_lambda_r4_sidecar_for_packet(packet=packet)
    sidecar_evaluation = evaluate_symbolic_lambda_r4_sidecar(sidecar)
    claim_blockers = _ordered_unique(
        list(row.get("claim_blockers", []))
        + list(sidecar_evaluation["numeric_claim_blockers"])
        + ["symbolic_lambda_policy_nonclaiming"]
    )
    internal_actions = _ordered_unique(
        list(row.get("allowed_internal_actions", []))
        + [SYMBOLIC_INTERNAL_ACTION]
    )
    blocked_actions = _ordered_unique(
        list(row.get("blocked_claim_actions", []))
        + list(BLOCKED_CLAIM_ACTIONS)
        + [SYMBOLIC_BLOCKED_CLAIM_ACTION]
    )
    ready_symbolic = (
        row.get("ready_for_internal_query") is True
        and sidecar_evaluation["ready_for_internal_symbolic_query"] is True
    )

    enhanced = dict(row)
    enhanced.update({
        "symbolic_lambda_r4_policy_status": (
            "internal_symbolic_query_ready_nonclaiming"
            if ready_symbolic
            else "symbolic_lambda_policy_not_ready"
        ),
        "symbolic_lambda_r4_sidecar": sidecar,
        "symbolic_lambda_r4_sidecar_evaluation": sidecar_evaluation,
        "symbolic_normalization_claim_blockers": sorted(
            sidecar_evaluation["numeric_claim_blockers"]
        ),
        "allowed_internal_actions": internal_actions,
        "blocked_claim_actions": blocked_actions,
        "claim_blockers": claim_blockers,
        "ready_for_internal_symbolic_query": ready_symbolic,
        "ready_for_numeric_wilson_export": False,
        "ready_for_framework_claim": False,
        "claim_status": "claim_blocked",
    })
    return canonicalize_json_floats(enhanced)


def query_r4_symbolic_lambda_surface(
    framework: str,
    axis_family: str,
) -> dict[str, Any]:
    base_row = query_r4_projection_surface(framework, axis_family)
    entry = get_r4_adapter_registry_entry(
        framework=framework,
        axis_family=axis_family,
    )
    if entry is None:
        blocked_actions = _ordered_unique(
            list(base_row.get("blocked_claim_actions", []))
            + [SYMBOLIC_BLOCKED_CLAIM_ACTION]
        )
        enhanced = dict(base_row)
        enhanced.update({
            "symbolic_lambda_r4_policy_status": "adapter_not_registered",
            "symbolic_lambda_r4_sidecar": None,
            "ready_for_internal_symbolic_query": False,
            "ready_for_numeric_wilson_export": False,
            "ready_for_framework_claim": False,
            "blocked_claim_actions": blocked_actions,
        })
        return canonicalize_json_floats(enhanced)
    return attach_symbolic_lambda_policy_to_query_row(base_row, entry["packet"])


def r4_symbolic_lambda_query_surface_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in r4_adapter_registry_entries():
        rows.append(
            query_r4_symbolic_lambda_surface(
                entry["framework"],
                entry["axis_family"],
            )
        )
    return rows


def diagnose_r4_symbolic_lambda_query_attachment() -> dict[str, Any]:
    rows = r4_symbolic_lambda_query_surface_rows()
    ready_symbolic = [
        row["query_key"] for row in rows
        if row["ready_for_internal_symbolic_query"]
    ]
    numeric_ready = [
        row["query_key"] for row in rows
        if row["ready_for_numeric_wilson_export"]
    ]
    claim_ready = [
        row["query_key"] for row in rows
        if row["ready_for_framework_claim"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    lookup_examples = {
        "registered_string_tree_eft": query_r4_symbolic_lambda_surface(
            "string_tree_eft",
            "gravity_R4_Riemann4",
        ),
        "unregistered_pure_gr": query_r4_symbolic_lambda_surface(
            "pure_gr",
            "gravity_R4_Riemann4",
        ),
    }

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.154_r4_lambda_unit_policy",
            "v2.150_r4_projection_query_surface",
            "v2.149_r4_adapter_registry_hook",
        ],
        "query_row_count": len(rows),
        "ready_internal_symbolic_query_keys": ready_symbolic,
        "numeric_wilson_export_ready_keys": numeric_ready,
        "claim_ready_query_keys": claim_ready,
        "claimable_framework_exclusions_now": [],
        "rows": rows,
        "lookup_examples": lookup_examples,
        "claim_blocker_counts": dict(sorted(blocker_counts.items())),
        "required_numeric_claim_blockers": sorted(NUMERIC_CLAIM_BLOCKERS),
        "route_status": "r4_symbolic_lambda_query_surface_ready_nonclaiming",
        "selected_next_build_action": (
            "source_four_dimensional_frame_and_lambda_r4_scale_policy"
        ),
        "best_next_artifact": (
            "A source-backed four-dimensional frame, field-redefinition, "
            "and Lambda_R4 scale policy that can decide whether the symbolic "
            "alpha-prime/kappa ledger can ever become a numeric engine-axis "
            "coefficient."
        ),
        "interpretation": (
            "The R4 query surface now exposes the symbolic Lambda_R4 sidecar "
            "for internal inspection. It still blocks numeric Wilson export "
            "and framework claims because alpha-prime, kappa, frame, scale, "
            "and likelihood prerequisites remain unresolved."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.155/"
            "r4_symbolic_lambda_query_attachment.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_symbolic_lambda_query_attachment()
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
