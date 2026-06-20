"""Symbolic projection plan from string R4 structures to Bresciani coordinates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_projection_guard_schema import (
    REQUIRED_R4_PROJECTION_FIELDS,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.string_r4_basis_translation_source_audit import (
    diagnose_string_r4_basis_translation_source_audit,
)


VERSION = "v2.135"


def bresciani_coordinate_solver() -> dict[str, Any]:
    return {
        "target_source_coordinates": {
            "c_plus": "c_1^(2) + c_2^(2)",
            "c_minus": "c_1^(2) - c_2^(2) + i*c_3^(2)",
        },
        "engine_axes": {
            "g_R4_c1": "c_1^(2)",
            "g_R4_c2": "c_2^(2)",
            "g_R4_c3": "c_3^(2)",
        },
        "inversion_if_c_plus_and_c_minus_known": {
            "g_R4_c1": "(c_plus + Re(c_minus)) / 2",
            "g_R4_c2": "(c_plus - Re(c_minus)) / 2",
            "g_R4_c3": "Im(c_minus)",
        },
        "derived_coordinates": {
            "g_R4_plus": "g_R4_c1 + g_R4_c2",
            "g_R4_minus_abs": "sqrt((g_R4_c1 - g_R4_c2)^2 + g_R4_c3^2)",
        },
        "positivity_guard": [
            "g_R4_c1 >= 0",
            "g_R4_c2 >= 0",
            "g_R4_c3^2 <= 4*g_R4_c1*g_R4_c2",
        ],
    }


def symbolic_projection_stages() -> list[dict[str, Any]]:
    return [
        {
            "stage": "fix_source_family",
            "status": "ready",
            "required_input": "Choose one string R4 source family, starting with type II tree-level R4.",
            "output": "source_family_id",
            "failure_mode": None,
        },
        {
            "stage": "fix_four_dimensional_frame",
            "status": "needed",
            "required_input": (
                "Compactification or truncation statement, Einstein-frame "
                "normalization, and field-redefinition policy."
            ),
            "output": "four_dimensional_on_shell_Riemann4_basis",
            "failure_mode": "frame_choice_or_field_redefinition_ambiguity",
        },
        {
            "stage": "construct_string_tensor_basis",
            "status": "needed",
            "required_input": "t8t8R4, epsilon-epsilon R4, and any parity-odd tensor structures retained.",
            "output": "symbolic_tensor_basis",
            "failure_mode": "string_tensor_basis_incomplete",
        },
        {
            "stage": "evaluate_independent_helicity_amplitudes",
            "status": "needed",
            "required_input": (
                "Four-graviton on-shell helicity amplitudes sufficient to "
                "identify c_plus and complex c_minus."
            ),
            "output": "source_c_plus_and_c_minus",
            "failure_mode": "helicity_projection_underconstrained",
        },
        {
            "stage": "invert_to_bresciani_coordinates",
            "status": "ready_once_stage_4_done",
            "required_input": "c_plus and c_minus from the source helicity amplitudes.",
            "output": "g_R4_c1, g_R4_c2, g_R4_c3",
            "failure_mode": "c_plus_c_minus_not_source_backed",
        },
        {
            "stage": "normalize_to_engine_axis",
            "status": "needed",
            "required_input": "Lambda_R4 or source-backed energy/cutoff convention.",
            "output": "dimensionless g_R4 axes and valid energy domain",
            "failure_mode": "engine_lambda_r4_normalization_missing",
        },
        {
            "stage": "package_guard_packet",
            "status": "needed",
            "required_input": "Projection matrix, derived axes, positivity check, covariance, ownership metadata.",
            "output": "v2.133 guard-compatible R4 projection packet",
            "failure_mode": "guard_packet_missing_required_fields",
        },
    ]


def symbolic_projection_acceptance_tests() -> list[dict[str, Any]]:
    return [
        {
            "test": "three_axis_solution",
            "criterion": "g_R4_c1, g_R4_c2, and g_R4_c3 are all numeric symbolic expressions.",
        },
        {
            "test": "derived_coordinate_consistency",
            "criterion": "g_R4_plus and g_R4_minus_abs match the v2.133 guard formulas.",
        },
        {
            "test": "source_ownership",
            "criterion": "Every tensor and normalization choice has a primary source or declared derivation.",
        },
        {
            "test": "positivity_bound_check",
            "criterion": "c1 >= 0, c2 >= 0, and c3^2 <= 4*c1*c2 are evaluated.",
        },
        {
            "test": "guard_packet_validation",
            "criterion": "evaluate_r4_projection_packet returns ready_for_framework_projection=true.",
        },
        {
            "test": "nonclaiming_without_measurement",
            "criterion": (
                "The packet remains non-claiming unless a measurement likelihood "
                "and excluding discriminator math are supplied."
            ),
        },
    ]


def diagnose_symbolic_string_r4_to_bresciani_projection_plan() -> dict[str, Any]:
    source_audit = diagnose_string_r4_basis_translation_source_audit()
    stages = symbolic_projection_stages()
    blockers = sorted({
        row["failure_mode"] for row in stages
        if row["failure_mode"] is not None
    })
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.134_string_r4_basis_translation_source_audit",
            "v2.133_gravity_r4_projection_guard_schema",
            "Bresciani_c_plus_c_minus_coordinate_contract",
        ],
        "source_audit_route_status": source_audit["route_status"],
        "useful_string_r4_sources": source_audit["useful_string_r4_sources"],
        "can_build_guard_passing_string_r4_adapter_now": False,
        "coordinate_solver": bresciani_coordinate_solver(),
        "symbolic_projection_stages": stages,
        "acceptance_tests": symbolic_projection_acceptance_tests(),
        "required_guard_packet_fields": list(REQUIRED_R4_PROJECTION_FIELDS),
        "current_projection_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "symbolic_string_r4_projection_plan_ready_nonclaiming",
        "selected_next_build_action": (
            "implement_symbolic_helicity_projection_fixture"
        ),
        "best_next_artifact": (
            "A symbolic fixture that accepts source-level c_plus/c_minus inputs, "
            "inverts them into g_R4_c1/c2/c3, and sends the result through the "
            "v2.133 guard without claiming a framework exclusion."
        ),
        "interpretation": (
            "The route is now reduced to a concrete derivation problem. If a "
            "source-backed string R4 helicity projection supplies c_plus and "
            "c_minus in a fixed four-dimensional frame, the Bresciani axes are "
            "algebraically recoverable. The missing work is the source-backed "
            "helicity/tensor evaluation, not the downstream guard logic."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.135/"
            "symbolic_string_r4_to_bresciani_projection_plan.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_symbolic_string_r4_to_bresciani_projection_plan()
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
