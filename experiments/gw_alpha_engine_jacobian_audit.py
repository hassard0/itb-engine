"""Alpha-bar to engine-axis Jacobian audit for v2.101."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_secondary_axis_adapter_blueprint import (
    liu_yunes_gw170608_paper_summary_adapter_candidate,
)


VERSION = "v2.101"
SOURCE_MODEL = "cubic_parity_preserving_higher_curvature_eft"
SOURCE_PARAMETERS = ("alpha_bar_1", "alpha_bar_2")
EXISTING_SECONDARY_AXES = ("g_C", "g_R2")
NATIVE_CUBIC_CANDIDATE_AXIS = "g_R3"

SOURCE_FACTS = (
    {
        "source_url": "https://arxiv.org/abs/2407.08929",
        "role": "measurement_analysis",
        "facts": [
            "GW170608 Bayesian analysis",
            "cubic parity-preserving higher-curvature EFT waveform model",
            "numeric alpha_bar_1 and alpha_bar_2 constraints",
        ],
    },
    {
        "source_url": "https://arxiv.org/abs/2507.17143",
        "role": "operator_dictionary",
        "facts": [
            "curvature-operator scaling dictionary",
            "not an event-level engine likelihood",
        ],
    },
)

ENGINE_AXIS_DEFINITIONS: dict[str, dict[str, Any]] = {
    "g_C": {
        "engine_role": "weyl_squared_central_charge_axis",
        "curvature_order": 2,
        "operator_family": "quadratic_weyl_or_c_anomaly",
        "status": "registered_secondary_axis",
        "compatible_source_models": ("quadratic_weyl_eft",),
    },
    "g_R2": {
        "engine_role": "r_squared_or_euler_proxy_axis",
        "curvature_order": 2,
        "operator_family": "quadratic_scalar_or_euler_curvature",
        "status": "registered_secondary_axis",
        "compatible_source_models": ("r_squared_scalar_eft",),
    },
    "g_R3": {
        "engine_role": "cubic_graviton_forward_amplitude_axis",
        "curvature_order": 3,
        "operator_family": "cubic_parity_even_curvature",
        "status": "registered_engine_coefficient_not_v2_98_secondary_axis",
        "compatible_source_models": (SOURCE_MODEL,),
    },
}

REQUIRED_PROMOTION_CRITERIA = (
    "curvature_order_match",
    "operator_family_match",
    "source_backed_normalization",
    "dimensionless_scaling_defined",
    "covariance_or_likelihood_export_available",
    "shared_eft_domain_bounded",
    "framework_projection_defined",
)


def _parameter_constraints() -> dict[str, Any]:
    candidate = liu_yunes_gw170608_paper_summary_adapter_candidate()
    return dict(candidate["parameter_constraints"])


def _source_parameter_summary() -> dict[str, Any]:
    constraints = _parameter_constraints()
    present = [
        parameter
        for parameter in SOURCE_PARAMETERS
        if isinstance(constraints.get(parameter), dict)
    ]
    intervals = {
        parameter: constraints[parameter]
        for parameter in present
    }
    return {
        "source_model": SOURCE_MODEL,
        "parameters": list(SOURCE_PARAMETERS),
        "parameters_with_numeric_constraints": present,
        "all_source_parameters_numeric": set(present) == set(SOURCE_PARAMETERS),
        "intervals": intervals,
    }


def evaluate_alpha_to_engine_axis_mapping(target_axis: str) -> dict[str, Any]:
    if target_axis not in ENGINE_AXIS_DEFINITIONS:
        raise KeyError(f"unknown target axis: {target_axis}")

    axis = ENGINE_AXIS_DEFINITIONS[target_axis]
    curvature_order_match = axis["curvature_order"] == 3
    operator_family_match = SOURCE_MODEL in axis["compatible_source_models"]

    passed = []
    failed = []
    if curvature_order_match:
        passed.append("curvature_order_match")
    else:
        failed.append("curvature_order_mismatch")
    if operator_family_match:
        passed.append("operator_family_match")
    else:
        failed.append("operator_family_mismatch")

    missing_promotion_requirements = [
        "source_backed_normalization",
        "dimensionless_scaling_defined",
        "covariance_or_likelihood_export_available",
        "shared_eft_domain_bounded",
        "framework_projection_defined",
    ]
    failed.extend(missing_promotion_requirements)

    if target_axis in EXISTING_SECONDARY_AXES:
        decision = "reject_direct_jacobian_to_existing_secondary_axis"
        next_action = "do_not_force_alpha_bar_into_quadratic_axis"
    else:
        decision = "axis_extension_candidate_nonpromoting"
        next_action = "register_source_native_cubic_gw_axis_adapter"
        failed.append("source_native_axis_not_registered_for_v2_98_gate")

    return {
        "source_parameters": list(SOURCE_PARAMETERS),
        "source_model": SOURCE_MODEL,
        "target_axis": target_axis,
        "target_axis_definition": axis,
        "passed_criteria": passed,
        "failed_criteria": failed,
        "promotion_ready": False,
        "direct_existing_secondary_axis": target_axis in EXISTING_SECONDARY_AXES,
        "decision": decision,
        "next_action": next_action,
        "risk_if_forced": (
            "would reinterpret cubic GW EFT constraints as a different engine "
            "operator family without a source-backed Jacobian"
        ),
    }


def diagnose_gw_alpha_engine_jacobian_audit() -> dict[str, Any]:
    mappings = [
        evaluate_alpha_to_engine_axis_mapping(axis)
        for axis in (*EXISTING_SECONDARY_AXES, NATIVE_CUBIC_CANDIDATE_AXIS)
    ]
    direct_existing = [
        row for row in mappings if row["direct_existing_secondary_axis"]
    ]
    extension_candidates = [
        row
        for row in mappings
        if row["decision"] == "axis_extension_candidate_nonpromoting"
    ]
    claim_ready = [row for row in mappings if row["promotion_ready"]]

    return {
        "version": VERSION,
        "basis": [
            "v2.100_gw_secondary_axis_adapter_blueprint",
            "arXiv_2407.08929_cubic_parity_preserving_gw170608_constraints",
            "arXiv_2507.17143_curvature_operator_dictionary",
            "engine_axes_g_C_g_R2_g_R3",
        ],
        "question": (
            "Can alpha_bar_1/alpha_bar_2 be source-backed into existing "
            "engine secondary axes g_C or g_R2?"
        ),
        "source_facts": list(SOURCE_FACTS),
        "source_parameter_summary": _source_parameter_summary(),
        "required_promotion_criteria": list(REQUIRED_PROMOTION_CRITERIA),
        "existing_secondary_axes_checked": list(EXISTING_SECONDARY_AXES),
        "native_cubic_candidate_axis": NATIVE_CUBIC_CANDIDATE_AXIS,
        "mapping_attempts": mappings,
        "direct_existing_secondary_axis_jacobian_ready": any(
            row["promotion_ready"] for row in direct_existing
        ),
        "source_native_cubic_axis_extension_available": bool(extension_candidates),
        "claimable_discriminator_now": bool(claim_ready),
        "claim_ready_mappings": claim_ready,
        "route_status": (
            "alpha_to_existing_secondary_axes_rejected_"
            "cubic_axis_extension_selected"
        ),
        "selected_next_build_action": (
            "register_source_native_cubic_gw_axis_adapter"
        ),
        "best_next_artifact": (
            "A non-promoting source-native cubic GW packet schema for "
            "alpha_bar_1/alpha_bar_2, with explicit normalization and "
            "likelihood export requirements before any g8 joint-gate use."
        ),
        "interpretation": (
            "The Liu-Yunes constraints are useful, but forcing them into g_C "
            "or g_R2 would mix cubic GW EFT parameters into quadratic engine "
            "axes. The build path is to preserve the source-native cubic basis "
            "first, then decide whether a defensible g_R3-family projection or "
            "new joint gate is possible."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.101/gw_alpha_engine_jacobian_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_engine_jacobian_audit()
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
