"""Frontier refresh after the external G8 packet spec (v2.167)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.external_g8_measurement_packet_spec import (
    diagnose_external_g8_measurement_packet_spec,
)
from experiments.post_adapter_frontier_refresh import (
    frontier_rows_after_adapter_refresh,
)
from experiments.post_r4_likelihood_manifest_frontier import _frontier_row


VERSION = "v2.167"


def frontier_rows_after_external_g8_spec() -> list[dict[str, Any]]:
    previous_rows = {
        row["route"]: row for row in frontier_rows_after_adapter_refresh()
    }
    g8_spec = diagnose_external_g8_measurement_packet_spec()
    missing_slot = g8_spec["current_missing_packet_slot_evaluation"]

    return [
        previous_rows["future_public_r4_shape_likelihood_ingestion"],
        _frontier_row(
            route="external_spin4_or_detector_g8_measurement_packet_spec",
            family="matter_forward_amplitude",
            status="packet_contract_ready_real_external_g8_packet_missing",
            execution_class="external_packet_required_to_use_ready_contract",
            priority_rank=2,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.166 defines the exact external G8 packet needed to join the "
                "calibrated GW alpha likelihood. The alpha side is ready, the "
                "synthetic control passes, but no real current external G8 "
                "packet fills the contract."
            ),
            next_artifact=g8_spec["best_next_artifact"],
            blockers=[
                "ready_current_external_g8_packet_missing",
                *missing_slot["packet_blockers"],
            ],
            basis=[
                "v2.166_external_g8_measurement_packet_spec",
                "v2.126_gw_alpha_g8_joint_component_audit",
                "v2.98_g8_joint_packet_acceptance_gate",
            ],
        ),
        previous_rows["registered_native_tower_adapter_authoring"],
        previous_rows["weyl_g8_joint_frontier"],
        previous_rows["gw_parity_operator_normalization_search"],
        previous_rows["r4_symbolic_scale_resolution"],
    ]


def diagnose_post_external_g8_spec_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_external_g8_spec(),
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

    g8_spec = diagnose_external_g8_measurement_packet_spec()
    return {
        "version": VERSION,
        "basis": [
            "v2.166_external_g8_measurement_packet_spec",
            "v2.165_post_adapter_frontier_refresh",
            "v2.162_r4_shape_likelihood_ingestion_adapter",
            "v2.164_native_tower_adapter_requirement_sheet",
        ],
        "frontier_scope": "post_external_g8_packet_spec",
        "route_count": len(rows),
        "alpha_packet_ready_for_g8_join": (
            g8_spec["alpha_packet_ready_for_g8_join"]
        ),
        "ready_current_external_g8_packets": (
            g8_spec["ready_current_external_g8_packets"]
        ),
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
        "route_status": "post_external_g8_spec_frontier_no_claim_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "The G8 route has moved from a vague missing measurement to a "
            "claim-safe external packet contract. The frontier still has no "
            "current promotion-ready or claim-ready route because the real "
            "external R4 and G8 packets remain absent."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.167/"
            "post_external_g8_spec_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_external_g8_spec_frontier()
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
