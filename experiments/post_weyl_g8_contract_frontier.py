"""Frontier refresh after the Weyl/G8 dual-likelihood contract (v2.173)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.post_r4_likelihood_manifest_frontier import _frontier_row
from experiments.post_r4_scale_contract_frontier import (
    frontier_rows_after_r4_scale_contract,
)
from experiments.weyl_g8_dual_likelihood_contract import (
    diagnose_weyl_g8_dual_likelihood_contract,
)


VERSION = "v2.173"


def frontier_rows_after_weyl_g8_contract() -> list[dict[str, Any]]:
    previous_rows = {
        row["route"]: row for row in frontier_rows_after_r4_scale_contract()
    }
    weyl = diagnose_weyl_g8_dual_likelihood_contract()
    missing_packet = weyl["current_missing_packet_slot_evaluation"]
    base = missing_packet["base_joint_packet_evaluation"]
    extension = missing_packet["weyl_extension_evaluation"]

    return [
        previous_rows["future_public_r4_shape_likelihood_ingestion"],
        previous_rows["external_spin4_or_detector_g8_measurement_packet_spec"],
        previous_rows["registered_native_tower_adapter_authoring"],
        _frontier_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            status="dual_likelihood_contract_ready_real_packet_missing",
            execution_class="external_dual_likelihood_required_to_use_ready_contract",
            priority_rank=4,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.172 wraps the v2.98 joint g8+gC gate in a Weyl/G8-specific "
                "dual-likelihood contract with source packets, covariance, "
                "projection, exclusion statistic, scan policy, reanalysis, "
                "and claim controls. No real current packet fills it."
            ),
            next_artifact=weyl["best_next_artifact"],
            blockers=[
                "ready_current_weyl_g8_packet_missing",
                *missing_packet["packet_blockers"],
                *base["acceptance_blockers"],
                *extension["extension_blockers"],
            ],
            basis=[
                "v2.172_weyl_g8_dual_likelihood_contract",
                "v2.99_g8_joint_source_discovery_queue",
                "v2.98_g8_joint_packet_acceptance_gate",
                "v2.50_weyl_g8_discriminator_frontier",
            ],
        ),
        previous_rows["gw_parity_operator_normalization_search"],
        previous_rows["r4_symbolic_scale_resolution"],
    ]


def diagnose_post_weyl_g8_contract_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_weyl_g8_contract(),
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

    weyl = diagnose_weyl_g8_dual_likelihood_contract()
    synthetic = weyl["synthetic_control_evaluation"]
    return {
        "version": VERSION,
        "basis": [
            "v2.172_weyl_g8_dual_likelihood_contract",
            "v2.171_post_r4_scale_contract_frontier",
            "v2.170_r4_symbolic_scale_resolution_contract",
        ],
        "frontier_scope": "post_weyl_g8_dual_likelihood_contract",
        "route_count": len(rows),
        "weyl_g8_contract_route_status": weyl["route_status"],
        "weyl_g8_synthetic_control_status": synthetic["route_status"],
        "ready_current_weyl_g8_packets": weyl["ready_current_weyl_g8_packets"],
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
        "route_status": "post_weyl_g8_contract_frontier_no_claim_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "All six active frontier routes now have executable diagnostic "
            "infrastructure or packet contracts. The engine still has no "
            "promotion-ready or claim-ready route because every route depends "
            "on missing real external evidence, source-owned adapters, or "
            "source-backed scale policies."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.173/"
            "post_weyl_g8_contract_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_weyl_g8_contract_frontier()
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
