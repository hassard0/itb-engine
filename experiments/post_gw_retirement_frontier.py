"""Discriminator frontier after direct GW parity promotion retirement (v2.77)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_parity_route_decision import diagnose_gw_parity_route_decision


def _frontier_row(
    *,
    route: str,
    family: str,
    status: str,
    claim_ready: bool,
    priority_rank: int,
    reason: str,
    next_artifact: str,
    blockers: list[str],
    basis: list[str],
) -> dict[str, Any]:
    return {
        "route": route,
        "family": family,
        "status": status,
        "claim_ready": claim_ready,
        "priority_rank": priority_rank,
        "reason": reason,
        "next_artifact": next_artifact,
        "blockers": sorted(set(blockers)),
        "basis": basis,
    }


def frontier_rows_after_gw_retirement() -> list[dict[str, Any]]:
    gw_decision = diagnose_gw_parity_route_decision()
    return [
        _frontier_row(
            route="g8_high_moment_measurement",
            family="matter_forward_amplitude",
            status="measurement_contract_defined_external_packet_missing",
            claim_ready=False,
            priority_rank=1,
            reason=(
                "The g8 route has a cleaner engine-axis contract than GW parity: "
                "the missing object is an external high-moment measurement packet."
            ),
            next_artifact=(
                "Search for a public, engine-normalized high-moment or energy-"
                "correlator likelihood that can constrain g_8."
            ),
            blockers=[
                "missing_engine_normalized_g8_likelihood",
                "missing_covariance_or_likelihood",
                "no_framework_excluding_measurement_packet",
            ],
            basis=[
                "v2.54_g8_high_moment_measurement_specification",
                "v2.55_g8_existing_measurement_packet_search",
            ],
        ),
        _frontier_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            status="theory_frontier_confirmed_measurement_blocked",
            claim_ready=False,
            priority_rank=2,
            reason=(
                "The Weyl/g8 frontier is geometrically robust, but still lacks "
                "external numerical cuts in engine normalization."
            ),
            next_artifact=(
                "Find or define external measurement packets for g_C and g_8, "
                "then test whether their joint likelihood excludes frameworks."
            ),
            blockers=[
                "g_C_external_measurement_missing",
                "g8_external_measurement_missing",
                "joint_likelihood_missing",
            ],
            basis=[
                "v2.50_weyl_g8_discriminator_frontier",
                "v2.51_weyl_g8_observable_sourceability",
            ],
        ),
        _frontier_row(
            route="native_tower_evidence",
            family="swampland_tower",
            status="adapter_contract_ready_native_spectra_missing",
            claim_ready=False,
            priority_rank=3,
            reason=(
                "Tower gates are implemented and guarded, but no live framework "
                "owns source-native tower spectra in the required schema."
            ),
            next_artifact=(
                "Extract or source native tower spectra for a named framework, "
                "then pass them through the acceptance harness."
            ),
            blockers=[
                "native_framework_tower_spectrum_missing",
                "asymptotic_regime_ownership_missing",
                "positive_controls_guarded_not_claim_ready",
            ],
            basis=[
                "v2.46_native_tower_ownership_frontier",
                "v2.47_native_adapter_acceptance_harness",
                "v2.48_candidate_native_adapter_promotion_audit",
            ],
        ),
        _frontier_row(
            route="gw_parity_source_native_archive",
            family="gravitational_wave_parity",
            status="retained_nonpromoting_direct_engine_route_retired",
            claim_ready=False,
            priority_rank=4,
            reason=gw_decision["interpretation"],
            next_artifact=gw_decision["best_next_artifact"],
            blockers=[
                "direct_ng_ppv_engine_promotion_retired",
                "source_backed_operator_normalization_missing",
                "engine_axis_target_missing",
            ],
            basis=[
                "v2.71_to_v2.76_gw_parity_ng_source_native_chain",
            ],
        ),
        _frontier_row(
            route="cmb_beta_em_axion",
            family="electromagnetic_axion",
            status="retired_as_direct_gravity_discriminator",
            claim_ready=False,
            priority_rank=5,
            reason=(
                "CMB beta remains an EM/axion hint, not a direct gravitational "
                "parity engine route."
            ),
            next_artifact=(
                "Only revisit for a separate EM/axion framework catalogue or a "
                "source-backed multimessenger common-field model."
            ),
            blockers=[
                "not_engine_gravity_parity_axis",
                "em_gravity_bridge_missing",
                "systematics_not_closed_for_framework_claim",
            ],
            basis=[
                "v2.58_birefringence_adapter_literature_sourceability",
                "v2.59_parity_route_split_frontier",
            ],
        ),
    ]


def diagnose_post_gw_retirement_frontier() -> dict[str, Any]:
    rows = sorted(frontier_rows_after_gw_retirement(), key=lambda row: row["priority_rank"])
    claim_ready = [row for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.77",
        "basis": [
            "v2.76_gw_parity_route_decision",
            "v2.53_unified_discriminator_route_frontier",
            "v2.54_g8_high_moment_measurement_specification",
            "v2.55_g8_existing_measurement_packet_search",
            "v2.50_v2.51_weyl_g8_frontier",
            "v2.46_to_v2.48_tower_frontier",
        ],
        "frontier_scope": "post_gw_direct_promotion_retirement",
        "route_count": len(rows),
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "priority_order": [row["route"] for row in rows],
        "top_priority_route": rows[0]["route"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "post_gw_frontier_no_claim_ready_route_g8_next",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "Retiring direct GW parity promotion leaves no solved discriminator. "
            "The next highest-value path is g8 high-moment measurement search "
            "because it asks for an external packet in an already-defined engine "
            "axis rather than a new parity operator-normalization bridge."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.77/post_gw_retirement_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_post_gw_retirement_frontier()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
