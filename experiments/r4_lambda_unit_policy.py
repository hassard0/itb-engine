"""Symbolic, non-claiming Lambda_R4 unit policy for string R4 normalization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.policy_scoped_string_tree_r4_projection_packet import (
    policy_scoped_string_tree_r4_projection_packet,
)
from experiments.r4_shape_normalization_policy import (
    engine_r4_shape_normalization_policy,
    evaluate_r4_shape_normalization_policy,
)
from experiments.virasoro_shapiro_k_bridge_rederivation import (
    evaluate_rederived_k_bridge,
    open_source_formula_inputs,
    rederive_raw_k_bridge,
)


VERSION = "v2.154"

ALLOWED_POLICY_USES = (
    "symbolic_absolute_factor_inspection",
    "normalization_blocker_accounting",
    "internal_scale_sensitivity_sweep",
    "adapter_metadata_sidecar",
)
DISALLOWED_POLICY_USES = (
    "numeric_wilson_coefficient_export",
    "framework_exclusion_claim",
    "measurement_likelihood_claim",
    "collapse_symbolic_alpha_prime_or_kappa_to_one",
)
NUMERIC_CLAIM_BLOCKERS = (
    "amplitude_normalization_conventions_not_unified",
    "bridge_depends_on_alpha_prime_units",
    "bridge_depends_on_kappa_convention",
    "discriminator_math_not_excluding",
    "engine_lambda_r4_numeric_unit_not_defined",
    "four_dimensional_frame_and_field_redefinition_policy_missing",
    "numeric_alpha_prime_to_lambda_r4_value_missing",
    "measurement_likelihood_missing_or_incomplete",
    "source_backed_absolute_normalization_missing",
    "string_vs_einstein_frame_not_fixed",
)


def engine_r4_lambda_alpha_prime_policy() -> dict[str, Any]:
    """Define the symbolic Lambda_R4 policy without numeric claim promotion."""

    shape_policy = engine_r4_shape_normalization_policy()
    bridge = rederive_raw_k_bridge()
    bridge_evaluation = evaluate_rederived_k_bridge()
    contact = bridge["russo_pole_term"]["contact_scalar"]
    return canonicalize_json_floats({
        "policy_id": "engine_r4_lambda_symbolic_alpha_prime_policy_v1",
        "version": VERSION,
        "status": "engine_convention_symbolic_nonclaiming",
        "depends_on_shape_policy": {
            "policy_id": shape_policy["policy_id"],
            "status": shape_policy["status"],
            "engine_unit_definition": shape_policy["engine_unit_definition"],
        },
        "source_formula_inputs": open_source_formula_inputs(),
        "source_bridge": {
            "source_backed_open_rederivation": (
                bridge_evaluation["criteria"]["source_backed_open_rederivation"]
            ),
            "contact_scalar_expression": "2*zeta(3)",
            "contact_scalar_value": contact,
            "pole_match_equation": bridge["pole_match_equation"],
            "k_russo_over_shape": (
                bridge["derived_bridge"]["K_Russo_over_shape"]
            ),
            "symbolic_r4_contact_after_pole_match": (
                bridge["derived_r4_contact_after_pole_match"]["expression"]
            ),
            "symbolic_factor_without_shape": (
                "2*zeta(3)*alpha_prime^3/(64*kappa^2)"
            ),
            "alpha_prime_set_to_one_control": (
                bridge["derived_bridge"]["alpha_prime_set_to_one_control"]
            ),
        },
        "engine_axis_contract": {
            "source_formula": "g_R4_ci = Lambda_R4^8 * c_i^(2)",
            "lambda_power": 8,
            "numeric_lambda_r4_value": None,
            "lambda_r4_value_source_backed": False,
            "normalizes_dimensionful_contact": True,
        },
        "symbolic_scale": {
            "id": "xi_R4_string_tree_symbolic",
            "expression": "Lambda_R4^8*alpha_prime^3/kappa^2",
            "numeric_value": None,
            "source_backed_numeric_value": False,
        },
        "symbolic_projection": {
            "K_plus": "1",
            "K_minus": "0",
            "overall_R4_factor_symbolic": (
                "2*zeta(3)*Lambda_R4^8*alpha_prime^3/(64*kappa^2)"
            ),
            "coefficients_symbolic": {
                "g_R4_c1": (
                    "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
                ),
                "g_R4_c2": (
                    "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
                ),
                "g_R4_c3": "0",
            },
            "derived_symbolic": {
                "g_R4_plus": (
                    "zeta(3)*Lambda_R4^8*alpha_prime^3/(256*kappa^2)"
                ),
                "g_R4_minus_abs": "0",
            },
            "matching_equation": (
                "c_plus=overall_R4_factor*K_plus/8 and "
                "g_R4_c1=g_R4_c2=c_plus/2 for K_minus=0"
            ),
        },
        "engine_axis_policy": {
            "axis_family": "gravity_R4_Riemann4",
            "engine_axis": "Lambda_R4",
            "unit_status": "symbolic_only",
            "numeric_lambda_r4_value": None,
            "numeric_alpha_prime_value": None,
            "numeric_kappa_value": None,
            "frame_choice": None,
            "symbolic_scale_token": "Lambda_R4^8*alpha_prime^3/kappa^2",
            "numeric_coefficient_export_allowed": False,
            "symbolic_sidecar_export_allowed": True,
        },
        "allowed_uses": list(ALLOWED_POLICY_USES),
        "disallowed_uses": list(DISALLOWED_POLICY_USES),
        "framework_claim_allowed": False,
        "measurement_claim_allowed": False,
        "wilson_coefficient_magnitude_claim_allowed": False,
    })


def evaluate_r4_lambda_alpha_prime_policy(
    policy: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    warnings: set[str] = set()

    if policy.get("status") != "engine_convention_symbolic_nonclaiming":
        blockers.add("policy_status_not_symbolic_nonclaiming")
    if policy.get("policy_id") != "engine_r4_lambda_symbolic_alpha_prime_policy_v1":
        blockers.add("policy_id_mismatch")

    shape = policy.get("depends_on_shape_policy")
    if not isinstance(shape, dict):
        blockers.add("shape_policy_missing")
    else:
        shape_policy = engine_r4_shape_normalization_policy()
        shape_eval = evaluate_r4_shape_normalization_policy(shape_policy)
        if shape.get("policy_id") != shape_policy["policy_id"]:
            blockers.add("shape_policy_id_mismatch")
        if shape_eval["ready_for_internal_shape_normalization"] is not True:
            blockers.add("shape_policy_not_ready")

    source_bridge = policy.get("source_bridge")
    if not isinstance(source_bridge, dict):
        blockers.add("source_bridge_missing")
    else:
        if source_bridge.get("source_backed_open_rederivation") is not True:
            blockers.add("source_backed_open_rederivation_missing")
        if source_bridge.get("symbolic_factor_without_shape") != (
            "2*zeta(3)*alpha_prime^3/(64*kappa^2)"
        ):
            blockers.add("symbolic_factor_missing_or_changed")
        if "alpha_prime" not in str(source_bridge) or "kappa" not in str(source_bridge):
            blockers.add("alpha_prime_kappa_dependence_not_preserved")

    contract = policy.get("engine_axis_contract")
    if not isinstance(contract, dict):
        blockers.add("engine_axis_contract_missing")
    else:
        if contract.get("source_formula") != "g_R4_ci = Lambda_R4^8 * c_i^(2)":
            blockers.add("engine_axis_contract_formula_missing_or_changed")
        if contract.get("lambda_power") != 8:
            blockers.add("engine_axis_lambda_power_not_8")
        if contract.get("numeric_lambda_r4_value") is not None:
            blockers.add("numeric_lambda_r4_value_must_remain_unset")
        if contract.get("lambda_r4_value_source_backed") is not False:
            blockers.add("lambda_r4_value_source_backing_not_disabled")

    scale = policy.get("symbolic_scale")
    if not isinstance(scale, dict):
        blockers.add("symbolic_scale_missing")
    else:
        if scale.get("expression") != "Lambda_R4^8*alpha_prime^3/kappa^2":
            blockers.add("symbolic_scale_expression_missing_or_changed")
        if scale.get("numeric_value") is not None:
            blockers.add("symbolic_scale_numeric_value_must_remain_unset")
        if scale.get("source_backed_numeric_value") is not False:
            blockers.add("symbolic_scale_source_backing_not_disabled")

    projection = policy.get("symbolic_projection")
    if not isinstance(projection, dict):
        blockers.add("symbolic_projection_missing")
    else:
        coefficients = projection.get("coefficients_symbolic")
        if not isinstance(coefficients, dict):
            blockers.add("symbolic_projection_coefficients_missing")
        else:
            expected = (
                "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
            )
            if coefficients.get("g_R4_c1") != expected:
                blockers.add("symbolic_projection_g_r4_c1_changed")
            if coefficients.get("g_R4_c2") != expected:
                blockers.add("symbolic_projection_g_r4_c2_changed")
            if coefficients.get("g_R4_c3") != "0":
                blockers.add("symbolic_projection_g_r4_c3_changed")
            if "Lambda_R4^8" not in str(coefficients):
                blockers.add("symbolic_projection_lost_lambda_power")

    axis = policy.get("engine_axis_policy")
    if not isinstance(axis, dict):
        blockers.add("engine_axis_policy_missing")
    else:
        if axis.get("unit_status") != "symbolic_only":
            blockers.add("engine_axis_policy_not_symbolic_only")
        if axis.get("numeric_coefficient_export_allowed") is not False:
            blockers.add("numeric_coefficient_export_not_disabled")
        if axis.get("symbolic_sidecar_export_allowed") is not True:
            blockers.add("symbolic_sidecar_export_not_enabled")
        numeric_fields = (
            "numeric_lambda_r4_value",
            "numeric_alpha_prime_value",
            "numeric_kappa_value",
            "frame_choice",
        )
        for field in numeric_fields:
            if axis.get(field) is not None:
                blockers.add(f"{field}_must_remain_unset")

    allowed = set(policy.get("allowed_uses", []))
    disallowed = set(policy.get("disallowed_uses", []))
    if not set(ALLOWED_POLICY_USES).issubset(allowed):
        blockers.add("allowed_policy_uses_incomplete")
    if not set(DISALLOWED_POLICY_USES).issubset(disallowed):
        blockers.add("disallowed_policy_uses_incomplete")
    if policy.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if policy.get("measurement_claim_allowed") is not False:
        blockers.add("measurement_claim_not_disabled")
    if policy.get("wilson_coefficient_magnitude_claim_allowed") is not False:
        blockers.add("wilson_magnitude_claim_not_disabled")

    if not blockers:
        warnings.update(NUMERIC_CLAIM_BLOCKERS)

    return canonicalize_json_floats({
        "policy_id": policy.get("policy_id"),
        "ready_for_symbolic_engine_lambda_policy": not blockers,
        "ready_for_numeric_engine_lambda_r4": False,
        "ready_for_framework_claim": False,
        "symbolic_policy_blockers": sorted(blockers),
        "numeric_claim_blockers": sorted(NUMERIC_CLAIM_BLOCKERS),
        "warnings": sorted(warnings),
        "allowed_uses": sorted(allowed),
        "disallowed_uses": sorted(disallowed),
    })


def symbolic_lambda_r4_sidecar_for_packet(
    packet: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or policy_scoped_string_tree_r4_projection_packet()
    policy = policy or engine_r4_lambda_alpha_prime_policy()
    factor = policy["source_bridge"]["symbolic_factor_without_shape"]
    projection = policy["symbolic_projection"]
    coefficients = packet.get("coefficients", {})

    return canonicalize_json_floats({
        "sidecar_id": "string_tree_eft_r4_symbolic_lambda_policy_sidecar_v1",
        "policy_id": policy["policy_id"],
        "framework": packet.get("framework"),
        "axis_family": packet.get("axis_family"),
        "source_version": packet.get("source_version"),
        "numeric_shape_coefficients": coefficients,
        "symbolic_raw_contact_factor": factor,
        "symbolic_scale": policy["symbolic_scale"],
        "engine_axis_contract": policy["engine_axis_contract"],
        "symbolic_absolute_factor": projection["overall_R4_factor_symbolic"],
        "symbolic_coefficients": projection["coefficients_symbolic"],
        "symbolic_derived": projection["derived_symbolic"],
        "matching_equation": projection["matching_equation"],
        "numeric_values_exported": False,
        "claim_use_allowed": False,
        "measurement_likelihood_attached": False,
        "discriminator_math": "symbolic_policy_sidecar_only",
        "remaining_numeric_claim_blockers": list(NUMERIC_CLAIM_BLOCKERS),
    })


def evaluate_symbolic_lambda_r4_sidecar(sidecar: dict[str, Any]) -> dict[str, Any]:
    blockers: set[str] = set()
    if sidecar.get("policy_id") != "engine_r4_lambda_symbolic_alpha_prime_policy_v1":
        blockers.add("policy_id_mismatch")
    if sidecar.get("framework") != "string_tree_eft":
        blockers.add("framework_mismatch")
    if sidecar.get("axis_family") != "gravity_R4_Riemann4":
        blockers.add("axis_family_mismatch")
    if sidecar.get("numeric_values_exported") is not False:
        blockers.add("numeric_values_exported")
    if sidecar.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if sidecar.get("measurement_likelihood_attached") is not False:
        blockers.add("measurement_likelihood_unexpectedly_attached")
    raw_factor = sidecar.get("symbolic_raw_contact_factor")
    if raw_factor != "2*zeta(3)*alpha_prime^3/(64*kappa^2)":
        blockers.add("symbolic_raw_contact_factor_missing_or_changed")
    factor = sidecar.get("symbolic_absolute_factor")
    if factor != "2*zeta(3)*Lambda_R4^8*alpha_prime^3/(64*kappa^2)":
        blockers.add("symbolic_absolute_factor_missing_or_changed")
    symbolic = sidecar.get("symbolic_coefficients")
    if not isinstance(symbolic, dict) or not symbolic:
        blockers.add("symbolic_coefficients_missing")
    elif not all(
        "alpha_prime" in value and "kappa" in value and "Lambda_R4^8" in value
        for value in symbolic.values()
        if value != "0"
    ):
        blockers.add("symbolic_coefficients_lost_alpha_prime_or_kappa")
    elif symbolic.get("g_R4_c1") != (
        "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
    ):
        blockers.add("symbolic_coefficients_bresciani_factor_changed")

    return canonicalize_json_floats({
        "sidecar_id": sidecar.get("sidecar_id"),
        "ready_for_internal_symbolic_query": not blockers,
        "ready_for_numeric_wilson_export": False,
        "ready_for_framework_claim": False,
        "blockers": sorted(blockers),
        "numeric_claim_blockers": sorted(NUMERIC_CLAIM_BLOCKERS),
    })


def diagnose_r4_lambda_unit_policy() -> dict[str, Any]:
    policy = engine_r4_lambda_alpha_prime_policy()
    policy_evaluation = evaluate_r4_lambda_alpha_prime_policy(policy)
    sidecar = symbolic_lambda_r4_sidecar_for_packet(policy=policy)
    sidecar_evaluation = evaluate_symbolic_lambda_r4_sidecar(sidecar)

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.153_virasoro_shapiro_k_bridge_rederivation",
            "v2.148_policy_scoped_string_tree_r4_projection_packet",
            "v2.147_r4_shape_normalization_policy",
        ],
        "policy": policy,
        "policy_evaluation": policy_evaluation,
        "symbolic_sidecar": sidecar,
        "sidecar_evaluation": sidecar_evaluation,
        "ready_for_symbolic_engine_lambda_policy": (
            policy_evaluation["ready_for_symbolic_engine_lambda_policy"]
        ),
        "ready_for_internal_symbolic_query": (
            sidecar_evaluation["ready_for_internal_symbolic_query"]
        ),
        "ready_for_numeric_engine_lambda_r4": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "current_claim_blockers": sorted(NUMERIC_CLAIM_BLOCKERS),
        "route_status": "symbolic_lambda_r4_alpha_prime_policy_ready_nonclaiming",
        "selected_next_build_action": (
            "attach_symbolic_lambda_policy_to_r4_query_surface"
        ),
        "best_next_artifact": (
            "Expose the symbolic Lambda_R4 sidecar through the R4 query "
            "surface so internal tools can inspect the alpha-prime/kappa "
            "normalization ledger while numeric Wilson exports and framework "
            "claims remain blocked."
        ),
        "interpretation": (
            "The engine now has an explicit symbolic policy for the "
            "alpha_prime^3/kappa^2 factor found by v2.153. This advances the "
            "normalization work without collapsing alpha_prime or kappa to "
            "unit values or claiming an absolute string-scale Wilson "
            "coefficient."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.154/r4_lambda_unit_policy.json",
    )
    args = parser.parse_args()

    result = diagnose_r4_lambda_unit_policy()
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
