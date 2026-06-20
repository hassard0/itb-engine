"""Frontier refresh after the R4 scale-resolution contract (v2.171)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.post_parity_bridge_frontier import (
    frontier_rows_after_parity_bridge_spec,
)
from experiments.post_r4_likelihood_manifest_frontier import _frontier_row
from experiments.r4_symbolic_scale_resolution_contract import (
    diagnose_r4_symbolic_scale_resolution_contract,
)


VERSION = "v2.171"


def frontier_rows_after_r4_scale_contract() -> list[dict[str, Any]]:
    previous_rows = {
        row["route"]: row for row in frontier_rows_after_parity_bridge_spec()
    }
    scale = diagnose_r4_symbolic_scale_resolution_contract()
    missing_policy = scale["current_symbolic_only_slot_evaluation"]

    return [
        previous_rows["future_public_r4_shape_likelihood_ingestion"],
        previous_rows["external_spin4_or_detector_g8_measurement_packet_spec"],
        previous_rows["registered_native_tower_adapter_authoring"],
        previous_rows["weyl_g8_joint_frontier"],
        previous_rows["gw_parity_operator_normalization_search"],
        _frontier_row(
            route="r4_symbolic_scale_resolution",
            family="gravity_R4_normalization",
            status="numeric_scale_contract_ready_real_policy_missing",
            execution_class="external_scale_policy_required_to_use_ready_contract",
            priority_rank=6,
            current_in_repo_diagnostic_ready=True,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "v2.170 defines an executable numeric Lambda_R4 scale policy "
                "contract. The symbolic ledger remains ready, but no current "
                "source or candidate fills the real source-backed numeric "
                "policy slot."
            ),
            next_artifact=scale["best_next_artifact"],
            blockers=[
                "ready_current_numeric_scale_policy_missing",
                *missing_policy["scale_policy_blockers"],
            ],
            basis=[
                "v2.170_r4_symbolic_scale_resolution_contract",
                "v2.156_r4_frame_scale_policy_audit",
                "v2.154_r4_lambda_unit_policy",
            ],
        ),
    ]


def diagnose_post_r4_scale_contract_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_r4_scale_contract(),
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

    scale = diagnose_r4_symbolic_scale_resolution_contract()
    synthetic = scale["synthetic_control_evaluation"]
    return {
        "version": VERSION,
        "basis": [
            "v2.170_r4_symbolic_scale_resolution_contract",
            "v2.169_post_parity_bridge_frontier",
            "v2.168_gw_parity_operator_bridge_spec",
        ],
        "frontier_scope": "post_r4_scale_resolution_contract",
        "route_count": len(rows),
        "r4_scale_contract_route_status": scale["route_status"],
        "r4_scale_synthetic_control_status": synthetic["route_status"],
        "ready_current_numeric_scale_policies": (
            scale["ready_current_numeric_scale_policies"]
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
        "route_status": "post_r4_scale_contract_frontier_no_claim_route",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "The frontier now reflects executable contracts for R4 likelihood, "
            "external G8, native tower adapters, GW parity, and R4 numeric "
            "scale policy. None has the real external packet, source adapter, "
            "or source-backed scale policy needed for promotion or a framework "
            "claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.171/"
            "post_r4_scale_contract_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_r4_scale_contract_frontier()
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
