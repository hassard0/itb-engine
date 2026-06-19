"""Frontier after direct g_8 measurement execution retirement (v2.91)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_direct_measurement_route_decision import (
    diagnose_g8_direct_measurement_route_decision,
)


def _frontier_row(
    *,
    route: str,
    family: str,
    status: str,
    execution_class: str,
    priority_rank: int,
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
        "current_in_repo_promotion_ready": current_in_repo_promotion_ready,
        "claim_ready": claim_ready,
        "reason": reason,
        "next_artifact": next_artifact,
        "blockers": sorted(set(blockers)),
        "basis": basis,
    }


def frontier_rows_after_g8_direct_measurement_decision() -> list[dict[str, Any]]:
    return [
        _frontier_row(
            route="future_public_g8_measurement_ingestion",
            family="matter_forward_amplitude",
            status="retained_waiting_for_real_external_packet",
            execution_class="external_packet_required_before_in_repo_adapter",
            priority_rank=1,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The v2.79 acceptance harness can consume a real source packet, "
                "but v2.90 confirms the repo cannot produce the missing "
                "spin-4/detector measurement internally."
            ),
            next_artifact=(
                "Keep an intake contract ready and ingest only after a public "
                "packet supplies values, covariance, systematics, and EFT domain."
            ),
            blockers=[
                "future_public_g8_packet_missing",
                "public_g8_likelihood_or_covariance_missing",
                "component_level_systematics_budget_missing",
                "external_eft_domain_missing",
            ],
            basis=[
                "v2.79_g8_adapter_acceptance_harness",
                "v2.89_g8_direct_measurement_feasibility_audit",
                "v2.90_g8_direct_measurement_route_decision",
            ],
        ),
        _frontier_row(
            route="external_spin4_detector_measurement_request",
            family="matter_forward_amplitude",
            status="retained_external_experimental_dependency",
            execution_class="external_measurement_program_required",
            priority_rank=2,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The cleanest g_8 discriminator would be a direct external "
                "measurement in the engine basis; this is outside the current "
                "repo run."
            ),
            next_artifact=(
                "Prepare a minimal external-request checklist rather than "
                "attempting another synthetic in-repo measurement."
            ),
            blockers=[
                "external_experimental_program_required",
                "external_public_release_required",
                "external_systematics_budget_missing",
            ],
            basis=[
                "v2.54_g8_high_moment_measurement_specification",
                "v2.89_g8_direct_measurement_feasibility_audit",
                "v2.90_g8_direct_measurement_route_decision",
            ],
        ),
        _frontier_row(
            route="future_source_backed_g8_operator_identity_search",
            family="matter_forward_amplitude",
            status="retained_future_source_search",
            execution_class="future_source_required",
            priority_rank=3,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "Current sources do not provide the operator identity, Jacobian, "
                "or covariance needed to promote detector or energy-correlator "
                "data into engine g_8."
            ),
            next_artifact=(
                "Reopen only when a new source supplies a source-backed operator "
                "identity and uncertainty propagation."
            ),
            blockers=[
                "future_source_operator_identity_missing",
                "future_source_public_covariance_missing",
                "source_backed_jacobian_to_engine_g8_missing",
            ],
            basis=[
                "v2.86_g8_adapter_derivation_source_audit",
                "v2.87_g8_adapter_derivation_route_decision",
            ],
        ),
        _frontier_row(
            route="framework_specific_native_tower_search",
            family="swampland_tower",
            status="retained_future_named_framework_search",
            execution_class="future_source_required",
            priority_rank=4,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "Native tower evidence remains potentially decisive, but current "
                "audited sources do not provide a registered-framework-owned "
                "adapter row."
            ),
            next_artifact=(
                "Monitor named registered-framework sources for asymptotic tower "
                "spectra with ownership metadata."
            ),
            blockers=[
                "named_framework_native_source_missing",
                "asymptotic_tower_spectrum_missing",
                "adapter_normalization_missing",
            ],
            basis=[
                "v2.83_native_tower_current_source_audit",
                "v2.84_native_tower_route_decision",
            ],
        ),
        _frontier_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            status="theory_frontier_confirmed_measurement_blocked",
            execution_class="external_dual_likelihood_required",
            priority_rank=5,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The geometry is stable, but the joint cut needs external g_C "
                "and g_8 likelihood packets in engine normalization."
            ),
            next_artifact=(
                "Defer joint likelihood work until at least one external "
                "engine-normalized packet exists."
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
            route="gw_parity_operator_normalization_search",
            family="gravitational_wave_parity",
            status="retained_operator_bridge_missing",
            execution_class="future_operator_bridge_required",
            priority_rank=6,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "The Ng public likelihood is reproduced, but direct promotion "
                "remains retired without a source-backed PPV-to-engine operator "
                "normalization."
            ),
            next_artifact=(
                "Search only when a source-backed bridge appears; do not treat "
                "additional posterior parsing as a promotion route."
            ),
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
            execution_class="retired_non_gravity_discriminator",
            priority_rank=7,
            current_in_repo_promotion_ready=False,
            claim_ready=False,
            reason=(
                "CMB beta is an electromagnetic/axion route, not the engine's "
                "direct gravitational parity axis."
            ),
            next_artifact="Only revisit as a separate EM/axion catalogue.",
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


def diagnose_post_g8_direct_measurement_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_g8_direct_measurement_decision(),
        key=lambda row: row["priority_rank"],
    )
    claim_ready = [row for row in rows if row["claim_ready"]]
    promotion_ready = [row for row in rows if row["current_in_repo_promotion_ready"]]
    external_dependency = [
        row
        for row in rows
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

    direct_decision = diagnose_g8_direct_measurement_route_decision()
    return {
        "version": "v2.91",
        "basis": [
            "v2.90_g8_direct_measurement_route_decision",
            "v2.88_post_g8_derivation_route_decision_frontier",
            "v2.85_post_native_tower_route_decision_frontier",
            "v2.77_post_gw_retirement_frontier",
        ],
        "frontier_scope": "post_direct_g8_measurement_execution_retirement",
        "route_count": len(rows),
        "direct_g8_retired_routes": direct_decision["retired_routes"],
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "current_in_repo_promotion_ready_routes": [
            row["route"] for row in promotion_ready
        ],
        "external_dependency_routes": [row["route"] for row in external_dependency],
        "claimable_discriminator_now": bool(claim_ready),
        "priority_order": [row["route"] for row in rows],
        "top_priority_route": rows[0]["route"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "execution_class_counts": dict(sorted(execution_class_counts.items())),
        "rows": rows,
        "route_status": (
            "post_direct_g8_measurement_frontier_external_only_no_claim_ready"
        ),
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "After v2.90, the frontier has no current in-repo promotion-ready "
            "route. The highest-leverage path is to keep the g_8 ingestion "
            "contract ready for a real external packet, while preserving future "
            "source searches without treating them as claim evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.91/"
            "post_g8_direct_measurement_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_g8_direct_measurement_frontier()
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
