"""G8 joint-component audit for the calibrated GW alpha packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_joint_packet_acceptance_gate import REQUIRED_JOINT_PACKET_FIELDS
from experiments.g8_joint_source_discovery_queue import (
    current_joint_source_candidates,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_alpha_systematics_budget_gate import load_json


VERSION = "v2.126"
DEFAULT_ALPHA_PACKET_PATH = Path(
    "experiments/results/v2.125/gw_alpha_joint_likelihood_calibration.json"
)
G8_REQUIRED_CAPABILITIES = (
    "external_numeric_measurement",
    "engine_g8_normalization",
    "joint_likelihood_or_covariance",
    "closed_systematics_budget",
    "framework_pair_exclusion_math",
)


def alpha_packet_join_status(alpha_result: dict[str, Any]) -> dict[str, Any]:
    adapter = alpha_result["evaluation"]["adapter_evaluation"]
    return {
        "alpha_packet_native_adapter_ready": adapter["native_adapter_ready"],
        "alpha_packet_claim_ready": adapter["claim_ready"],
        "adapter_blockers": adapter["adapter_blockers"],
        "claim_blockers": adapter["claim_blockers"],
        "ready_for_g8_join": (
            adapter["native_adapter_ready"]
            and adapter["adapter_blockers"] == []
            and adapter["claim_blockers"] == ["g8_joint_component_missing"]
        ),
    }


def g8_candidate_join_rows() -> list[dict[str, Any]]:
    rows = []
    for candidate in current_joint_source_candidates():
        missing = set(candidate["missing_gate_capabilities"])
        supplies = set(candidate["supplies"])
        has_g8_axis = "g_8" in set(candidate["potential_axes"])
        required_missing = [
            capability
            for capability in G8_REQUIRED_CAPABILITIES
            if capability in missing
            or (
                capability == "external_numeric_measurement"
                and "external_numeric_measurement" not in supplies
            )
            or (
                capability == "closed_systematics_budget"
                and "closed_systematics_budget" not in supplies
            )
        ]
        if not has_g8_axis:
            required_missing.append("candidate_not_on_g8_axis")
        join_ready = has_g8_axis and not required_missing
        rows.append(
            {
                "label": candidate["label"],
                "source_url": candidate["source_url"],
                "source_type": candidate["source_type"],
                "candidate_role": candidate["candidate_role"],
                "potential_axes": candidate["potential_axes"],
                "supplies": candidate["supplies"],
                "missing_gate_capabilities": candidate["missing_gate_capabilities"],
                "required_missing_for_alpha_join": sorted(set(required_missing)),
                "g8_axis_candidate": has_g8_axis,
                "join_ready_now": join_ready,
                "blocks_v2_98_gate": not join_ready,
            },
        )
    rows.sort(
        key=lambda row: (
            len(row["required_missing_for_alpha_join"]),
            row["label"],
        ),
    )
    return rows


def g8_joint_component_audit(alpha_result: dict[str, Any]) -> dict[str, Any]:
    alpha_status = alpha_packet_join_status(alpha_result)
    candidate_rows = g8_candidate_join_rows()
    join_ready = [row for row in candidate_rows if row["join_ready_now"]]
    g8_axis_candidates = [row for row in candidate_rows if row["g8_axis_candidate"]]
    blocker_counts: dict[str, int] = {}
    for row in candidate_rows:
        for blocker in row["required_missing_for_alpha_join"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    return {
        "audit_kind": "calibrated_alpha_packet_to_g8_joint_component_recheck",
        "alpha_status": alpha_status,
        "required_joint_packet_fields": list(REQUIRED_JOINT_PACKET_FIELDS),
        "required_g8_capabilities": list(G8_REQUIRED_CAPABILITIES),
        "candidate_count": len(candidate_rows),
        "g8_axis_candidate_count": len(g8_axis_candidates),
        "join_ready_candidate_count": len(join_ready),
        "join_ready_candidates": [row["label"] for row in join_ready],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "candidate_rows": candidate_rows,
        "g8_joint_component_supplied": bool(join_ready),
    }


def diagnose_gw_alpha_g8_joint_component_audit(
    alpha_packet_path: Path = DEFAULT_ALPHA_PACKET_PATH,
) -> dict[str, Any]:
    alpha_result = load_json(alpha_packet_path)
    audit = g8_joint_component_audit(alpha_result)
    return {
        "version": VERSION,
        "basis": [
            "v2.125_alpha_joint_likelihood_calibration",
            "v2.99_g8_joint_source_discovery_queue",
            "v2.98_g8_joint_packet_acceptance_gate",
        ],
        "paths": {
            "alpha_packet": alpha_packet_path.as_posix(),
        },
        "g8_joint_component_audit": audit,
        "claimable_discriminator_now": False,
        "route_status": "alpha_ready_g8_joint_component_missing_nonclaiming",
        "selected_next_build_action": (
            "external_spin4_or_detector_g8_measurement_packet_spec"
        ),
        "best_next_artifact": (
            "A concrete external measurement packet specification for a "
            "spin-4/detector G8 observable that satisfies the v2.98 gate and "
            "can be joined to the calibrated alpha packet."
        ),
        "interpretation": (
            "The alpha packet is ready for a G8 join, but the current source "
            "inventory has no engine-normalized G8 measurement with public "
            "likelihood/covariance, closed systematics, and framework-exclusion "
            "math. The next executable step is not another alpha refinement; it "
            "is a G8 measurement packet specification or an actual external G8 "
            "packet."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha-packet", default=str(DEFAULT_ALPHA_PACKET_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.126/"
            "gw_alpha_g8_joint_component_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_g8_joint_component_audit(
        alpha_packet_path=Path(args.alpha_packet),
    )
    result = canonicalize_json_floats(result)
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
