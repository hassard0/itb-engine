"""GW parity route decision after Ng PPV engine-axis audit (v2.76)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


def _decision_row(
    *,
    route: str,
    status: str,
    retained: bool,
    claim_ready: bool,
    reason: str,
    next_action: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "route": route,
        "status": status,
        "retained": retained,
        "claim_ready": claim_ready,
        "reason": reason,
        "next_action": next_action,
        "blockers": sorted(set(blockers)),
    }


def route_decision_rows() -> list[dict[str, Any]]:
    shared_engine_blockers = [
        "no_current_engine_axis_target",
        "source_backed_operator_normalization_missing",
        "framework_exclusion_math_missing",
    ]
    return [
        _decision_row(
            route="ng_ppv_beta10_direct_engine_promotion",
            status="retired_for_current_engine",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.75 found zero current engine axes that can accept the "
                "source-native Ng/Jenks beta_1_0 candidate packet."
            ),
            next_action=(
                "Do not use this route for framework verdicts unless a new "
                "source-backed operator-normalization map is added."
            ),
            blockers=[
                *shared_engine_blockers,
                "dimensionless_ppv_beta10_normalization_missing",
                "engine_canonical_helicity_sign_missing",
            ],
        ),
        _decision_row(
            route="ng_source_native_likelihood_archive",
            status="retained_as_nonpromoting_measurement_packet",
            retained=True,
            claim_ready=False,
            reason=(
                "v2.71-v2.74 verified public data, reproduced the restricted "
                "kappa likelihood, and wrapped it as a guarded PPV candidate."
            ),
            next_action=(
                "Keep the packet available for comparison, plotting, and future "
                "adapter tests; never treat it as an engine-axis likelihood."
            ),
            blockers=[
                "source_native_packet_not_engine_axis",
                "engine_projection_out_of_scope",
            ],
        ),
        _decision_row(
            route="callister_alpha_beta_split_route",
            status="open_source_native_route_engine_blocked",
            retained=True,
            claim_ready=False,
            reason=(
                "Callister supplies source-backed alpha/beta and SGWB energy "
                "material, but it is a two-axis stochastic-background route."
            ),
            next_action=(
                "Only revisit after a separate alpha_1/beta_1 engine adapter "
                "contract exists; do not merge it into the Ng beta_1_0 route."
            ),
            blockers=[
                "two_axis_alpha1_beta1_not_single_beta10",
                "sgwb_energy_convention_not_waveform_beta",
                *shared_engine_blockers,
            ],
        ),
        _decision_row(
            route="external_operator_normalization_search",
            status="required_before_any_gw_parity_claim",
            retained=True,
            claim_ready=False,
            reason=(
                "The live missing artifact is not another posterior parser; it "
                "is an operator-level normalization from a source parameter to "
                "the engine Wilson basis."
            ),
            next_action=(
                "Search for or derive a source-backed map from PPV beta_1_0 or "
                "a named parity-violating theory to the engine parity axes."
            ),
            blockers=[
                "operator_identity_not_source_backed_in_engine_basis",
                "dimensionful_to_dimensionless_normalization_missing",
                "noncircular_framework_predictions_missing",
            ],
        ),
    ]


def diagnose_gw_parity_route_decision() -> dict[str, Any]:
    rows = route_decision_rows()
    retired = [row["route"] for row in rows if row["status"].startswith("retired")]
    retained = [row["route"] for row in rows if row["retained"]]
    claim_ready = [row["route"] for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.76",
        "basis": [
            "v2.75_gw_parity_engine_axis_audit",
            "v2.74_gw_parity_ng_ppv_beta_candidate",
            "v2.70_gw_parity_ppv_convention_audit",
            "targeted_primary_source_search_jenks_ng_callister",
        ],
        "decision_scope": "gw_parity_source_native_to_engine_routes",
        "route_count": len(rows),
        "retired_routes": retired,
        "retained_nonpromoting_routes": retained,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "direct_ng_ppv_engine_promotion_retired_no_claim_ready_route",
        "best_next_artifact": (
            "Pivot out of direct Ng promotion and search for an independent "
            "operator-normalization source, or move to a different discriminator "
            "frontier with a cleaner engine-axis measurement contract."
        ),
        "interpretation": (
            "The GW parity work produced high-quality source-native likelihood "
            "material, but no current engine-normalized framework discriminator. "
            "The direct Ng PPV beta_1_0 promotion route is therefore retired for "
            "the current engine rather than left as an ambiguous blocker."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.76/gw_parity_route_decision.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_route_decision()
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
