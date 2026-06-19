"""Frontier after direct native tower source promotion retirement (v2.85)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.native_tower_route_decision import diagnose_native_tower_route_decision


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


def frontier_rows_after_native_tower_decision() -> list[dict[str, Any]]:
    return [
        _frontier_row(
            route="source_backed_g8_adapter_derivation",
            family="matter_forward_amplitude",
            status="retained_required_not_currently_claimable",
            claim_ready=False,
            priority_rank=1,
            reason=(
                "After v2.84, direct native tower source promotion is retired. "
                "The next best non-new-measurement route is the retained g_8 "
                "adapter derivation path."
            ),
            next_artifact=(
                "Attempt a source-backed derivation audit for mapping detector or "
                "energy-correlator observables into engine g_8, including a "
                "hard no-go if no operator identity exists."
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
            route="framework_specific_native_tower_search",
            family="swampland_tower",
            status="retained_search_route_no_current_adapter",
            claim_ready=False,
            priority_rank=2,
            reason=(
                "v2.84 retained a narrower framework-specific search, but v2.83 "
                "already found no current registered native adapter in the "
                "audited source classes."
            ),
            next_artifact=(
                "Only revisit when a named registered framework source provides "
                "asymptotic tower spectra and ownership metadata."
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
            route="new_spin4_or_detector_g8_measurement",
            family="matter_forward_amplitude",
            status="clean_route_requires_new_external_measurement",
            claim_ready=False,
            priority_rank=3,
            reason=(
                "A direct spin-4/detector measurement remains clean, but it "
                "appears to require a new external measurement packet."
            ),
            next_artifact=(
                "Specify a measurement packet for an external program, or wait "
                "for a publication already in this basis."
            ),
            blockers=[
                "external_numeric_g8_measurement_missing",
                "public_g8_likelihood_or_covariance_missing",
                "registered_framework_exclusion_math_missing",
            ],
            basis=[
                "v2.54_g8_high_moment_measurement_specification",
                "v2.79_g8_adapter_acceptance_harness",
            ],
        ),
        _frontier_row(
            route="weyl_g8_joint_frontier",
            family="non_tower_geometry_matter",
            status="theory_frontier_confirmed_measurement_blocked",
            claim_ready=False,
            priority_rank=4,
            reason=(
                "The joint frontier needs external likelihoods for both g_C and "
                "g_8; neither exists in engine normalization."
            ),
            next_artifact=(
                "Defer until either g_C or g_8 has a real external packet."
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
                "Direct GW parity promotion is retired until an operator-level "
                "normalization bridge is sourced."
            ),
            next_artifact=(
                "Search for PPV-to-engine parity normalization; do not run more "
                "posterior parsers first."
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
            reason="CMB beta is not a direct gravitational parity engine route.",
            next_artifact=(
                "Only revisit for an EM/axion catalogue or source-backed "
                "multimessenger common-field model."
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


def diagnose_post_native_tower_route_decision_frontier() -> dict[str, Any]:
    rows = sorted(
        frontier_rows_after_native_tower_decision(),
        key=lambda row: row["priority_rank"],
    )
    claim_ready = [row for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    native_decision = diagnose_native_tower_route_decision()
    return {
        "version": "v2.85",
        "basis": [
            "v2.84_native_tower_route_decision",
            "v2.82_post_g8_route_decision_frontier",
            "v2.81_g8_route_decision",
        ],
        "frontier_scope": "post_native_tower_direct_source_promotion_retirement",
        "route_count": len(rows),
        "native_retired_direct_routes": native_decision["retired_routes"],
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "priority_order": [row["route"] for row in rows],
        "top_priority_route": rows[0]["route"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "post_native_frontier_no_claim_ready_route_g8_adapter_next",
        "best_next_artifact": rows[0]["next_artifact"],
        "interpretation": (
            "Direct native tower source promotion is retired, so the next live "
            "route is the source-backed g_8 adapter derivation. This does not "
            "make g_8 claim-ready; it means the next artifact should decide "
            "whether a source-backed operator identity exists or the route must "
            "also be retired."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.85/"
            "post_native_tower_route_decision_frontier.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_post_native_tower_route_decision_frontier()
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
