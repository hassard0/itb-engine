"""Discriminator frontier after direct g_8 public-data promotion retirement (v2.82)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_route_decision import diagnose_g8_route_decision


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


def frontier_rows_after_g8_route_decision() -> list[dict[str, Any]]:
    return [
        _frontier_row(
            route="native_tower_evidence",
            family="swampland_tower",
            status="adapter_contract_ready_native_spectra_missing",
            claim_ready=False,
            priority_rank=1,
            reason=(
                "After v2.81, direct public-data g_8 promotion is retired. "
                "Native tower evidence is now the most actionable no-new-"
                "experiment route because its acceptance harness already exists "
                "and the missing artifact is framework-owned spectral evidence."
            ),
            next_artifact=(
                "Run a targeted source audit for native tower spectra in named "
                "frameworks, then pass any candidate through the adapter harness."
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
            route="source_backed_g8_adapter_derivation",
            family="matter_forward_amplitude",
            status="retained_required_not_currently_claimable",
            claim_ready=False,
            priority_rank=2,
            reason=(
                "The g_8 data route remains open only through a citable adapter "
                "derivation from energy-correlator or detector observables into "
                "the engine Wilson basis."
            ),
            next_artifact=(
                "Search for or derive a source-backed g_8 Jacobian with public "
                "covariance, component-level systematics, and QG EFT domain."
            ),
            blockers=[
                "source_backed_jacobian_to_engine_g8_missing",
                "public_g8_covariance_missing",
                "component_level_systematics_budget_missing",
                "low_energy_qg_eft_domain_missing",
            ],
            basis=[
                "v2.79_g8_adapter_acceptance_harness",
                "v2.80_g8_public_data_product_acquisition_audit",
                "v2.81_g8_route_decision",
            ],
        ),
        _frontier_row(
            route="new_spin4_or_detector_g8_measurement",
            family="matter_forward_amplitude",
            status="clean_route_requires_new_external_measurement",
            claim_ready=False,
            priority_rank=3,
            reason=(
                "The cleanest g_8 route is a direct spin-4/detector measurement, "
                "but it appears to require a new external measurement packet."
            ),
            next_artifact=(
                "Specify the measurement design enough to hand to an external "
                "program, or identify a new publication already in this basis."
            ),
            blockers=[
                "external_numeric_g8_measurement_missing",
                "public_g8_likelihood_or_covariance_missing",
                "registered_framework_exclusion_math_missing",
            ],
            basis=[
                "v2.54_g8_high_moment_measurement_specification",
                "v2.79_g8_adapter_acceptance_harness",
                "v2.81_g8_route_decision",
            ],
        ),
        _frontier_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            status="theory_frontier_confirmed_measurement_blocked",
            claim_ready=False,
            priority_rank=4,
            reason=(
                "The Weyl/g8 frontier is geometrically robust, but it needs at "
                "least two engine-normalized external likelihoods."
            ),
            next_artifact=(
                "Defer until either g_C or g_8 has a real external packet; then "
                "build the joint likelihood."
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
            claim_ready=False,
            priority_rank=5,
            reason=(
                "The GW parity source-native likelihood is valuable, but v2.76 "
                "retired direct promotion until an operator-normalization bridge "
                "exists."
            ),
            next_artifact=(
                "Search for an operator-level PPV-to-engine parity normalization "
                "source; do not run more posterior parsers first."
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
            claim_ready=False,
            priority_rank=6,
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


def diagnose_post_g8_route_decision_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_g8_route_decision(),
        key=lambda row: row["priority_rank"],
    )
    claim_ready = [row for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    g8_decision = diagnose_g8_route_decision()
    return {
        "version": "v2.82",
        "basis": [
            "v2.81_g8_route_decision",
            "v2.77_post_gw_retirement_frontier",
            "v2.46_to_v2.48_tower_frontier",
            "v2.50_v2.51_weyl_g8_frontier",
        ],
        "frontier_scope": "post_g8_direct_public_data_promotion_retirement",
        "route_count": len(rows),
        "g8_retired_direct_routes": g8_decision["retired_routes"],
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "priority_order": [row["route"] for row in rows],
        "top_priority_route": rows[0]["route"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "post_g8_frontier_no_claim_ready_route_native_tower_next",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "Retiring direct g_8 public-data promotion leaves no solved "
            "discriminator. The next highest-value route is native tower "
            "evidence because it does not require a new experiment and already "
            "has adapter and guard infrastructure. The g_8 adapter route remains "
            "second, but only as a source-backed derivation path."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.82/"
            "post_g8_route_decision_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_g8_route_decision_frontier()
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
