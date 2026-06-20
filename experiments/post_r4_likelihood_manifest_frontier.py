"""Discriminator frontier after the R4 likelihood manifest (v2.161)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_shape_unitarity_diagnostic import (
    diagnose_bresciani_r4_shape_unitarity_diagnostic,
)
from experiments.explicit_tower_basis import _json_default
from experiments.post_g8_direct_measurement_frontier import (
    diagnose_post_g8_direct_measurement_frontier,
)
from experiments.r4_public_shape_likelihood_search import (
    diagnose_r4_public_shape_likelihood_search,
)
from experiments.r4_shape_likelihood_packet_manifest import (
    diagnose_r4_shape_likelihood_packet_manifest,
)


VERSION = "v2.161"


def _frontier_row(
    *,
    route: str,
    family: str,
    status: str,
    execution_class: str,
    priority_rank: int,
    current_in_repo_diagnostic_ready: bool,
    current_in_repo_promotion_ready: bool,
    claim_ready: bool,
    reason: str,
    next_artifact: str,
    blockers: list[str],
    basis: list[str],
) -> dict[str, Any]:
    return {
        "route": route,
        "family": family,
        "status": status,
        "execution_class": execution_class,
        "priority_rank": priority_rank,
        "current_in_repo_diagnostic_ready": current_in_repo_diagnostic_ready,
        "current_in_repo_promotion_ready": current_in_repo_promotion_ready,
        "claim_ready": claim_ready,
        "reason": reason,
        "next_artifact": next_artifact,
        "blockers": sorted(set(blockers)),
        "basis": basis,
    }


def frontier_rows_after_r4_likelihood_manifest() -> list[dict[str, Any]]:
    r4_diagnostic = diagnose_bresciani_r4_shape_unitarity_diagnostic()
    r4_search = diagnose_r4_public_shape_likelihood_search()
    g8_frontier = diagnose_post_g8_direct_measurement_frontier()
    g8_row = next(
        row for row in g8_frontier["rows"]
        if row["route"] == "future_public_g8_measurement_ingestion"
    )
    native_row = next(
        row for row in g8_frontier["rows"]
        if row["route"] == "framework_specific_native_tower_search"
    )
    weyl_row = next(
        row for row in g8_frontier["rows"]
        if row["route"] == "weyl_g8_joint_frontier"
    )
    parity_row = next(
        row for row in g8_frontier["rows"]
        if row["route"] == "gw_parity_operator_normalization_search"
    )

    return [
        _frontier_row(
            route="future_public_r4_shape_likelihood_ingestion",
            family="gravity_R4_shape",
            status="diagnostic_and_manifest_ready_public_likelihood_missing",
            execution_class="external_packet_required_before_claim_adapter",
            priority_rank=1,
            current_in_repo_diagnostic_ready=(
                r4_diagnostic["ready_for_internal_shape_unitarity_diagnostic"]
            ),
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The R4 path is now more mature than before v2.153: it has a "
                "source-backed shape projection, symbolic Lambda ledger, "
                "compactification-agnostic Bresciani diagnostic, public-source "
                "search, and future likelihood manifest. It still lacks the "
                "external likelihood/covariance packet required for a claim."
            ),
            next_artifact=(
                "Ingest a future public R4 shape likelihood packet only if it "
                "passes the v2.160 manifest; otherwise keep the R4 diagnostic "
                "non-claiming."
            ),
            blockers=[
                "public_r4_shape_likelihood_or_covariance_missing",
                "maps_to_bresciani_r4_axes_missing",
                "axis_normalization_declared_missing",
                "excluding_discriminator_math_missing",
            ]
            + sorted(r4_search["failure_counts"]),
            basis=[
                "v2.158_bresciani_r4_shape_unitarity_diagnostic",
                "v2.159_r4_public_shape_likelihood_search",
                "v2.160_r4_shape_likelihood_packet_manifest",
            ],
        ),
        _frontier_row(
            route=g8_row["route"],
            family=g8_row["family"],
            status=g8_row["status"],
            execution_class=g8_row["execution_class"],
            priority_rank=2,
            current_in_repo_diagnostic_ready=False,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=g8_row["reason"],
            next_artifact=g8_row["next_artifact"],
            blockers=g8_row["blockers"],
            basis=g8_row["basis"],
        ),
        _frontier_row(
            route=native_row["route"],
            family=native_row["family"],
            status=native_row["status"],
            execution_class=native_row["execution_class"],
            priority_rank=3,
            current_in_repo_diagnostic_ready=False,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=native_row["reason"],
            next_artifact=native_row["next_artifact"],
            blockers=native_row["blockers"],
            basis=native_row["basis"],
        ),
        _frontier_row(
            route=weyl_row["route"],
            family=weyl_row["family"],
            status=weyl_row["status"],
            execution_class=weyl_row["execution_class"],
            priority_rank=4,
            current_in_repo_diagnostic_ready=False,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=weyl_row["reason"],
            next_artifact=weyl_row["next_artifact"],
            blockers=weyl_row["blockers"],
            basis=weyl_row["basis"],
        ),
        _frontier_row(
            route=parity_row["route"],
            family=parity_row["family"],
            status=parity_row["status"],
            execution_class=parity_row["execution_class"],
            priority_rank=5,
            current_in_repo_diagnostic_ready=False,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=parity_row["reason"],
            next_artifact=parity_row["next_artifact"],
            blockers=parity_row["blockers"],
            basis=parity_row["basis"],
        ),
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
                "The symbolic R4 scale ledger is implemented, but v2.156 showed "
                "that current primary sources do not define a compactification-"
                "independent numeric Lambda_R4 scale."
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


def diagnose_post_r4_likelihood_manifest_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_r4_likelihood_manifest(),
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
    execution_class_counts: dict[str, int] = {}
    for row in rows:
        execution_class = row["execution_class"]
        execution_class_counts[execution_class] = (
            execution_class_counts.get(execution_class, 0) + 1
        )
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    r4_manifest = diagnose_r4_shape_likelihood_packet_manifest()
    return {
        "version": VERSION,
        "basis": [
            "v2.160_r4_shape_likelihood_packet_manifest",
            "v2.159_r4_public_shape_likelihood_search",
            "v2.158_bresciani_r4_shape_unitarity_diagnostic",
            "v2.91_post_g8_direct_measurement_frontier",
        ],
        "frontier_scope": "post_r4_likelihood_manifest",
        "route_count": len(rows),
        "r4_ready_likelihood_packets_now": r4_manifest[
            "ready_likelihood_packets_now"
        ],
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
        "execution_class_counts": dict(sorted(execution_class_counts.items())),
        "rows": rows,
        "route_status": "post_r4_frontier_diagnostic_ready_no_claim_ready_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "The R4 branch is now diagnostic-ready and future-evidence-ready, "
            "but it is not claim-ready. The frontier still has no current "
            "in-repo promotion-ready route; the highest priority is future "
            "public R4 shape likelihood ingestion, followed by the existing "
            "g_8 external packet route."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.161/"
            "post_r4_likelihood_manifest_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_r4_likelihood_manifest_frontier()
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
