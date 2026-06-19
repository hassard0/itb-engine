"""GW parity engine-axis audit for the Ng PPV candidate (v2.75)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default


def _axis_row(
    *,
    axis: str,
    implemented_by: list[str],
    internal_sign_status: str,
    dimensional_status: str,
    frequency_status: str,
    source_backed_ng_ppv_map: bool,
    can_accept_ng_beta10_packet: bool,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "axis": axis,
        "implemented_by": implemented_by,
        "internal_sign_status": internal_sign_status,
        "dimensional_status": dimensional_status,
        "frequency_status": frequency_status,
        "source_backed_ng_ppv_map": source_backed_ng_ppv_map,
        "can_accept_ng_beta10_packet": can_accept_ng_beta10_packet,
        "blockers": sorted(set(blockers)),
    }


def engine_axis_rows() -> list[dict[str, Any]]:
    return [
        _axis_row(
            axis="g_R2_parity",
            implemented_by=[
                "src/itb/constraints/parity_violation.py:ParityViolatingPositivity",
                "src/itb/constraints/parity_violation.py:LeftHandedGravitonPositivity",
                "src/itb/constraints/parity_violation.py:RightHandedGravitonPositivity",
                "src/itb/constraints/parity_violation.py:LIGOBirefringenceBound",
                "src/itb/gravitational_observables.py:GravitationalBirefringence",
            ],
            internal_sign_status=(
                "left/right combinations exist internally as g_R2 +/- g_R2_parity"
            ),
            dimensional_status=(
                "dimensionless toy Wilson coordinate; no source-backed conversion "
                "from kappa_Gpc_inv or PPV beta_1_0"
            ),
            frequency_status=(
                "observable uses omega/omega0 toy scaling, not Ng f_hz/100Hz "
                "distance propagation"
            ),
            source_backed_ng_ppv_map=False,
            can_accept_ng_beta10_packet=False,
            blockers=[
                "internal_helicity_sign_not_source_backed_ng_ppv_sign",
                "no_kappa_Gpc_inv_to_g_R2_parity_normalization",
                "frequency_basis_mismatch_omega0_vs_100Hz",
                "legacy_ligo_bound_is_toy_not_reproduced_ng_likelihood",
                "no_framework_exclusion_math_in_engine_basis",
            ],
        ),
        _axis_row(
            axis="g_R3_parity",
            implemented_by=[
                "src/itb/constraints/cubic_parity.py:ParityViolatingCubicBound",
                "src/itb/gravitational_observables.py:GravitationalBirefringence",
            ],
            internal_sign_status=(
                "frequency-dependent toy term in GravitationalBirefringence"
            ),
            dimensional_status=(
                "dimensionless cubic parity coordinate; Ng/Jenks beta_1_0 is "
                "not a cubic-curvature Wilson coefficient"
            ),
            frequency_status=(
                "linear omega/omega0 toy scaling, not source-declared Ng beta_1_0"
            ),
            source_backed_ng_ppv_map=False,
            can_accept_ng_beta10_packet=False,
            blockers=[
                "wrong_operator_order_for_ng_beta10_candidate",
                "no_kappa_Gpc_inv_to_g_R3_parity_normalization",
                "frequency_basis_mismatch_omega0_vs_100Hz",
                "no_framework_exclusion_math_in_engine_basis",
            ],
        ),
        _axis_row(
            axis="engine_gravitational_birefringence_observable",
            implemented_by=[
                "src/itb/gravitational_observables.py:GravitationalBirefringence",
            ],
            internal_sign_status=(
                "predicts g_R2_parity + (omega/omega0) * g_R3_parity"
            ),
            dimensional_status="toy observable normalization",
            frequency_status="omega0 defaults to 1.0 without physical units",
            source_backed_ng_ppv_map=False,
            can_accept_ng_beta10_packet=False,
            blockers=[
                "observable_is_toy_normalization",
                "no_distance_factor_D_C_Gpc",
                "no_source_backed_kappa_to_axis_jacobian",
            ],
        ),
        _axis_row(
            axis="legacy_ligo_birefringence_bound",
            implemented_by=[
                "src/itb/constraints/parity_violation.py:LIGOBirefringenceBound",
            ],
            internal_sign_status="absolute bound erases sign",
            dimensional_status="hard-coded |g_R2_parity| <= 0.1 toy translation",
            frequency_status="no public likelihood or source grid",
            source_backed_ng_ppv_map=False,
            can_accept_ng_beta10_packet=False,
            blockers=[
                "legacy_bound_not_source_native_likelihood",
                "absolute_value_bound_erases_ng_sign",
                "not_the_reproduced_ng_restricted_likelihood",
            ],
        ),
    ]


def diagnose_gw_parity_engine_axis_audit() -> dict[str, Any]:
    rows = engine_axis_rows()
    promotable = [row for row in rows if row["can_accept_ng_beta10_packet"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.75",
        "basis": [
            "v2.74_gw_parity_ng_ppv_beta_candidate",
            "v2.61_gw_parity_adapter_readiness",
            "engine_parity_constraint_modules",
            "engine_gravitational_birefringence_observable",
        ],
        "audit_scope": "current_engine_axes_only",
        "axis_count": len(rows),
        "promotable_axis_count": len(promotable),
        "promotable_axes": [row["axis"] for row in promotable],
        "ng_ppv_candidate_packet_can_be_promoted_now": bool(promotable),
        "direct_ng_ppv_to_engine_route_status": "blocked_no_current_engine_axis_target",
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "required_adapter_contract": [
            "source-backed operator identity from beta_1_0 to engine axis",
            "dimensionless normalization from kappa_Gpc_inv to Wilson coordinate",
            "canonical helicity sign that reconciles Ng and engine conventions",
            "frequency-distance transfer from D_C_Gpc*f/100Hz to engine omega basis",
            "framework-exclusion math in the mapped engine basis",
        ],
        "closed_this_iteration": [
            "engine_axis_target_audited",
            "legacy_ligo_bound_separated_from_reproduced_ng_likelihood",
        ],
        "claimable_discriminator_now": False,
        "route_status": "current_engine_axes_cannot_accept_ng_ppv_beta10",
        "best_next_artifact": (
            "Either source a real operator-normalization map from PPV beta_1_0 "
            "to g_R2_parity/g_R3_parity, or retire direct Ng-to-engine promotion "
            "and keep the packet as source-native likelihood material."
        ),
        "interpretation": (
            "The current engine has parity coordinates and an internal left/right "
            "sign convention, but they are toy Wilson axes. They do not own a "
            "source-backed dimensional or frequency normalization for the reproduced "
            "Ng kappa likelihood. The Ng PPV beta_1_0 candidate therefore cannot "
            "be promoted to a framework discriminator in the current engine."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.75/gw_parity_engine_axis_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_engine_axis_audit()
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
