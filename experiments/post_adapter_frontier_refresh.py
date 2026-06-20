"""Frontier refresh after R4 ingestion and native tower requirements (v2.165)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.native_tower_adapter_requirement_sheet import (
    diagnose_native_tower_adapter_requirement_sheet,
)
from experiments.post_g8_direct_measurement_frontier import (
    diagnose_post_g8_direct_measurement_frontier,
)
from experiments.post_r4_likelihood_manifest_frontier import _frontier_row
from experiments.r4_shape_likelihood_ingestion_adapter import (
    diagnose_r4_shape_likelihood_ingestion_adapter,
)


VERSION = "v2.165"


def _carried_g8_row(route: str, priority_rank: int) -> dict[str, Any]:
    g8_frontier = diagnose_post_g8_direct_measurement_frontier()
    row = next(row for row in g8_frontier["rows"] if row["route"] == route)
    return _frontier_row(
        route=row["route"],
        family=row["family"],
        status=row["status"],
        execution_class=row["execution_class"],
        priority_rank=priority_rank,
        current_in_repo_diagnostic_ready=False,
        current_in_repo_promotion_ready=False,
        claim_ready=False,
        reason=row["reason"],
        next_artifact=row["next_artifact"],
        blockers=row["blockers"],
        basis=row["basis"],
    )


def frontier_rows_after_adapter_refresh() -> list[dict[str, Any]]:
    r4 = diagnose_r4_shape_likelihood_ingestion_adapter()
    native = diagnose_native_tower_adapter_requirement_sheet()
    r4_missing_public = r4["current_public_packet_assessments"][0]
    native_top_missing = [
        name for name, _count in sorted(
            native["missing_requirement_counts"].items(),
            key=lambda item: (-item[1], item[0]),
        )[:8]
    ]

    return [
        _frontier_row(
            route="future_public_r4_shape_likelihood_ingestion",
            family="gravity_R4_shape",
            status="ingestion_adapter_ready_public_packet_missing",
            execution_class="external_packet_required_to_use_ready_adapter",
            priority_rank=1,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.162 implemented a manifest-gated R4 likelihood ingester "
                "and covariance-weighted Bresciani shape score. It has no "
                "ready public packet, so it remains diagnostic infrastructure."
            ),
            next_artifact=r4["best_next_artifact"],
            blockers=[
                "ready_public_r4_likelihood_packet_missing",
                *r4_missing_public["ingestion_blockers"],
            ],
            basis=[
                "v2.162_r4_shape_likelihood_ingestion_adapter",
                "v2.161_post_r4_likelihood_manifest_frontier",
            ],
        ),
        _carried_g8_row("future_public_g8_measurement_ingestion", 2),
        _frontier_row(
            route="registered_native_tower_adapter_authoring",
            family="swampland_tower",
            status="requirements_defined_no_source_ready_framework",
            execution_class="future_source_required_before_adapter_authoring",
            priority_rank=3,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.164 converted the native-tower blocker into a per-framework "
                "authoring contract. No registered framework currently fills "
                "the source-backed spectrum, evidence, ownership, normalization, "
                "threshold, and review fields."
            ),
            next_artifact=native["best_next_artifact"],
            blockers=[
                "adapter_authoring_ready_framework_missing",
                "native_framework_endpoint",
                "native_framework_displacement",
                "source_owned_tower_evidence",
                "registered_framework_exclusion_math",
                *native_top_missing,
            ],
            basis=[
                "v2.163_native_tower_live_source_triage",
                "v2.164_native_tower_adapter_requirement_sheet",
            ],
        ),
        _carried_g8_row("weyl_g8_joint_frontier", 4),
        _carried_g8_row("gw_parity_operator_normalization_search", 5),
        _frontier_row(
            route="r4_symbolic_scale_resolution",
            family="gravity_R4_normalization",
            status="symbolic_policy_ready_numeric_scale_blocked",
            execution_class="future_source_or_compactification_policy_required",
            priority_rank=6,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The symbolic R4 scale ledger is implemented, but the source-"
                "backed four-dimensional numeric Lambda_R4 policy is still "
                "missing."
            ),
            next_artifact=(
                "Reopen only if a source-backed four-dimensional frame and "
                "alpha-prime/kappa-to-Lambda_R4 policy appears."
            ),
            blockers=[
                "numeric_alpha_prime_to_lambda_r4_value_missing",
                "four_dimensional_frame_and_field_redefinition_policy_missing",
                "compactification_or_planck_normalization_policy_missing",
            ],
            basis=[
                "v2.154_r4_lambda_unit_policy",
                "v2.156_r4_frame_scale_policy_audit",
            ],
        ),
    ]


def diagnose_post_adapter_frontier_refresh() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_adapter_refresh(),
        key=lambda row: row["priority_rank"],
    )
    claim_ready = [row for row in rows if row["claim_ready"]]
    promotion_ready = [
        row for row in rows if row["current_in_repo_promotion_ready"]
    ]
    diagnostic_ready = [
        row for row in rows if row["current_in_repo_diagnostic_ready"]
    ]
    external_dependency = [
        row for row in rows
        if row["execution_class"].startswith("external")
        or row["execution_class"].startswith("future")
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": VERSION,
        "basis": [
            "v2.162_r4_shape_likelihood_ingestion_adapter",
            "v2.164_native_tower_adapter_requirement_sheet",
            "v2.91_post_g8_direct_measurement_frontier",
        ],
        "frontier_scope": "post_r4_ingester_and_native_requirement_sheet",
        "route_count": len(rows),
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "current_in_repo_promotion_ready_routes": [
            row["route"] for row in promotion_ready
        ],
        "current_in_repo_diagnostic_ready_routes": [
            row["route"] for row in diagnostic_ready
        ],
        "external_dependency_routes": [row["route"] for row in external_dependency],
        "claimable_discriminator_now": bool(claim_ready),
        "priority_order": [row["route"] for row in rows],
        "top_priority_route": rows[0]["route"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "post_adapter_frontier_infrastructure_ready_no_claim_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "The engine has improved infrastructure on the R4 and native-tower "
            "routes, but the frontier remains evidence/source blocked. No "
            "current route is promotion-ready or claim-ready."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.165/"
            "post_adapter_frontier_refresh.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_adapter_frontier_refresh()
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
