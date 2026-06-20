"""Frontier refresh after the GW parity bridge spec (v2.169)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_parity_operator_bridge_spec import (
    diagnose_gw_parity_operator_bridge_spec,
)
from experiments.post_external_g8_spec_frontier import (
    frontier_rows_after_external_g8_spec,
)
from experiments.post_r4_likelihood_manifest_frontier import _frontier_row


VERSION = "v2.169"


def frontier_rows_after_parity_bridge_spec() -> list[dict[str, Any]]:
    previous_rows = {
        row["route"]: row for row in frontier_rows_after_external_g8_spec()
    }
    parity = diagnose_gw_parity_operator_bridge_spec()
    missing_bridge = parity["current_missing_bridge_slot_evaluation"]

    return [
        previous_rows["future_public_r4_shape_likelihood_ingestion"],
        previous_rows["external_spin4_or_detector_g8_measurement_packet_spec"],
        previous_rows["registered_native_tower_adapter_authoring"],
        previous_rows["weyl_g8_joint_frontier"],
        _frontier_row(
            route="gw_parity_operator_normalization_search",
            family="gravitational_wave_parity",
            status="operator_bridge_contract_ready_real_bridge_missing",
            execution_class="external_bridge_required_to_use_ready_contract",
            priority_rank=5,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.168 defines an executable PPV/native-parameter to engine "
                "parity-axis bridge. Public source-native likelihood material "
                "exists, but no real current row fills the bridge contract."
            ),
            next_artifact=parity["best_next_artifact"],
            blockers=[
                "ready_current_operator_bridge_missing",
                *missing_bridge["bridge_blockers"],
            ],
            basis=[
                "v2.168_gw_parity_operator_bridge_spec",
                "v2.76_gw_parity_route_decision",
                "v2.61_gw_parity_adapter_readiness",
            ],
        ),
        previous_rows["r4_symbolic_scale_resolution"],
    ]


def diagnose_post_parity_bridge_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_parity_bridge_spec(),
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

    parity = diagnose_gw_parity_operator_bridge_spec()
    return {
        "version": VERSION,
        "basis": [
            "v2.168_gw_parity_operator_bridge_spec",
            "v2.167_post_external_g8_spec_frontier",
            "v2.166_external_g8_measurement_packet_spec",
        ],
        "frontier_scope": "post_gw_parity_operator_bridge_spec",
        "route_count": len(rows),
        "source_side_parity_likelihood_ready_routes": (
            parity["source_side_likelihood_ready_routes"]
        ),
        "ready_current_operator_bridges": parity["ready_current_operator_bridges"],
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
        "route_status": "post_parity_bridge_frontier_no_claim_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "R4, G8, native tower, and parity routes now have sharper packet or "
            "adapter contracts, but each remains blocked on missing real "
            "external evidence/source rows. No current route is promotion-ready "
            "or claim-ready."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.169/"
            "post_parity_bridge_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_parity_bridge_frontier()
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
