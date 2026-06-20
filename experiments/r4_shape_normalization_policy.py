"""Engine policy for non-claiming R4 shape normalization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.supersymmetric_r4_shape_projection import (
    kallosh_bresciani_shape_packet,
)


VERSION = "v2.147"

ALLOWED_POLICY_USES = (
    "internal_bresciani_basis_projection",
    "positivity_and_unitarity_algebra",
    "adapter_fixture_replacement",
    "relative_shape_comparison",
)
DISALLOWED_POLICY_USES = (
    "absolute_type_II_string_scale_claim",
    "framework_exclusion_claim",
    "measurement_likelihood_claim",
    "wilson_coefficient_magnitude_claim",
)


def engine_r4_shape_normalization_policy() -> dict[str, Any]:
    shape = kallosh_bresciani_shape_packet()
    return {
        "policy_id": "engine_r4_shape_unit_v1",
        "version": VERSION,
        "status": "engine_convention_nonclaiming",
        "normalized_shape_source": {
            "shape_packet": shape["label"],
            "source_urls": shape["source_urls"],
            "source_equation_refs": shape["source_equation_refs"],
            "source_backed_shape": shape["source_backed_derivation"],
            "K_plus": 1.0,
            "K_minus_real": 0.0,
            "K_minus_imag": 0.0,
        },
        "engine_unit_definition": {
            "overall_R4_factor": 8.0,
            "c_plus": 1.0,
            "c_minus_real": 0.0,
            "c_minus_imag": 0.0,
            "g_R4_c1": 0.5,
            "g_R4_c2": 0.5,
            "g_R4_c3": 0.0,
            "definition": (
                "One engine R4 shape unit equals the v2.144 "
                "Kallosh/Bresciani maximally supersymmetric R4 helicity shape."
            ),
        },
        "absolute_normalization": {
            "type_II_string_alpha_prime_units_source_backed": False,
            "engine_lambda_r4_unit_conversion_source_backed": False,
            "k_convention_bridge_source_backed": False,
        },
        "allowed_uses": list(ALLOWED_POLICY_USES),
        "disallowed_uses": list(DISALLOWED_POLICY_USES),
        "framework_claim_allowed": False,
        "measurement_claim_allowed": False,
    }


def evaluate_r4_shape_normalization_policy(policy: dict[str, Any]) -> dict[str, Any]:
    blockers: set[str] = set()
    warnings: set[str] = set()
    source = policy.get("normalized_shape_source")
    if not isinstance(source, dict) or source.get("source_backed_shape") is not True:
        blockers.add("source_backed_shape_missing")
    unit = policy.get("engine_unit_definition")
    if not isinstance(unit, dict) or unit.get("overall_R4_factor") != 8.0:
        blockers.add("engine_unit_definition_missing_or_changed")
    absolute = policy.get("absolute_normalization")
    if not isinstance(absolute, dict):
        blockers.add("absolute_normalization_policy_missing")
    else:
        if absolute.get("type_II_string_alpha_prime_units_source_backed") is True:
            warnings.add("policy_would_enable_absolute_string_claim")
        if absolute.get("engine_lambda_r4_unit_conversion_source_backed") is True:
            warnings.add("policy_would_enable_engine_lambda_conversion_claim")
        if absolute.get("k_convention_bridge_source_backed") is True:
            warnings.add("policy_would_enable_k_bridge_claim")

    allowed = set(policy.get("allowed_uses", []))
    disallowed = set(policy.get("disallowed_uses", []))
    if not set(ALLOWED_POLICY_USES).issubset(allowed):
        blockers.add("allowed_uses_incomplete")
    if not set(DISALLOWED_POLICY_USES).issubset(disallowed):
        blockers.add("disallowed_uses_incomplete")
    if policy.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if policy.get("measurement_claim_allowed") is not False:
        blockers.add("measurement_claim_not_disabled")

    return canonicalize_json_floats({
        "policy_id": policy.get("policy_id"),
        "ready_for_internal_shape_normalization": not blockers,
        "ready_for_absolute_string_normalization": False,
        "ready_for_framework_claim": False,
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
        "allowed_uses": sorted(allowed),
        "disallowed_uses": sorted(disallowed),
    })


def diagnose_r4_shape_normalization_policy() -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    evaluation = evaluate_r4_shape_normalization_policy(policy)
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.146_k_convention_bridge_audit",
            "v2.144_supersymmetric_r4_shape_projection",
            "v2.133_gravity_r4_projection_guard_schema",
        ],
        "policy": policy,
        "evaluation": evaluation,
        "ready_internal_shape_policy": (
            evaluation["ready_for_internal_shape_normalization"]
        ),
        "claimable_framework_exclusions_now": [],
        "route_status": "engine_r4_shape_unit_policy_ready_nonclaiming",
        "selected_next_build_action": (
            "build_policy_scoped_string_tree_r4_projection_packet"
        ),
        "best_next_artifact": (
            "A string_tree_eft R4 projection packet that can pass internal "
            "shape normalization gates under this policy while still failing "
            "absolute-normalization and framework-claim gates."
        ),
        "interpretation": (
            "The engine now has an explicit non-claiming R4 shape unit. This "
            "unblocks internal Bresciani-basis algebra and adapter tests "
            "without pretending that the Gross-Witten/Russo absolute string "
            "normalization has been solved."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.147/r4_shape_normalization_policy.json",
    )
    args = parser.parse_args()

    result = diagnose_r4_shape_normalization_policy()
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
