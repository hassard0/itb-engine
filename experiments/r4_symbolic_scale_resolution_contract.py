"""R4 symbolic-scale resolution contract for numeric Lambda_R4 policies."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_frame_scale_policy_audit import (
    candidate_frame_scale_policies,
    diagnose_r4_frame_scale_policy_audit,
    frame_scale_source_inputs,
)
from experiments.r4_lambda_unit_policy import (
    NUMERIC_CLAIM_BLOCKERS,
    diagnose_r4_lambda_unit_policy,
)


VERSION = "v2.170"
ENGINE_R4_SCALE_AXIS = "Lambda_R4"
TARGET_R4_AXES = (
    "g_R4_c1",
    "g_R4_c2",
    "g_R4_c3",
    "g_R4_plus",
    "g_R4_minus_abs",
)
REQUIRED_SCALE_POLICY_FIELDS = (
    "label",
    "source_url",
    "source_type",
    "source_backed_absolute_normalization",
    "four_dimensional_frame_policy",
    "string_to_einstein_frame_map",
    "alpha_prime_to_engine_lambda_r4",
    "kappa_normalization",
    "compactification_volume_or_moduli_policy",
    "field_redefinition_policy",
    "dimensionful_contact_normalization",
    "engine_lambda_r4_numeric_value",
    "uncertainty_or_covariance",
    "measurement_likelihood_reference",
    "claim_controls",
)
REQUIRED_CLAIM_CONTROLS = (
    "claim_use_allowed",
    "framework_claim_allowed",
    "external_adversarial_review_complete",
)
VALID_SOURCE_TYPES = {
    "validated_measurement",
    "source_backed_compactification_policy",
    "source_backed_effective_action_policy",
    "unit_test_control",
}
VALID_FRAME_POLICIES = {
    "four_dimensional_einstein_frame",
    "four_dimensional_string_frame",
}
VALID_LIKELIHOOD_STATUSES = {
    "public_covariance_matrix",
    "public_likelihood_samples",
    "public_log_likelihood_grid",
    "public_engine_usable",
}


def r4_symbolic_scale_resolution_contract() -> dict[str, Any]:
    return {
        "version": VERSION,
        "route": "r4_symbolic_scale_resolution",
        "external_object": "source_backed_numeric_lambda_r4_scale_policy",
        "engine_scale_axis": ENGINE_R4_SCALE_AXIS,
        "target_r4_axes": list(TARGET_R4_AXES),
        "required_scale_policy_fields": list(REQUIRED_SCALE_POLICY_FIELDS),
        "claim_control_fields": list(REQUIRED_CLAIM_CONTROLS),
        "source_url_policy": "https://arxiv.org/ or https://doi.org/",
        "claim_rule": (
            "A policy can become numeric-engine-ready only after every frame, "
            "field-basis, alpha-prime, kappa, compactification, covariance, "
            "and likelihood field is source backed. Framework claims remain "
            "disabled until external adversarial review completes."
        ),
    }


def synthetic_ready_r4_scale_policy_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_numeric_lambda_r4_scale_policy",
        "source_url": "https://doi.org/10.0000/synthetic-r4-scale-policy",
        "source_type": "unit_test_control",
        "source_backed_absolute_normalization": {
            "status": "source_backed",
            "operator": "Riemann4",
            "normalization_source": (
                "synthetic complete control for Lambda_R4 policy evaluator"
            ),
        },
        "four_dimensional_frame_policy": {
            "status": "declared",
            "frame": "four_dimensional_einstein_frame",
            "dimension": 4,
        },
        "string_to_einstein_frame_map": {
            "status": "source_backed",
            "map_declared": True,
            "field_rescaling_closed": True,
        },
        "alpha_prime_to_engine_lambda_r4": {
            "status": "numeric_source_backed",
            "numeric_alpha_prime_value": 0.015625,
            "maps_to_engine_axis": ENGINE_R4_SCALE_AXIS,
            "lambda_power": 8,
        },
        "kappa_normalization": {
            "status": "declared",
            "numeric_kappa_value": 1.0,
            "dimensionless_engine_convention": True,
        },
        "compactification_volume_or_moduli_policy": {
            "status": "declared",
            "volume_moduli_fixed": True,
            "policy_scope": "four_dimensional_effective_action",
        },
        "field_redefinition_policy": {
            "status": "maps_to_bresciani_r4_axes",
            "mapped_axes": list(TARGET_R4_AXES),
            "field_redefinition_ambiguity_closed": True,
        },
        "dimensionful_contact_normalization": {
            "status": "declared",
            "expression": "Lambda_R4^8*alpha_prime^3/kappa^2",
            "contains_alpha_prime_and_kappa": True,
        },
        "engine_lambda_r4_numeric_value": {
            "status": "public_engine_usable",
            "axis": ENGINE_R4_SCALE_AXIS,
            "numeric_value": 1.0,
            "unit": "engine_R4_axis_units",
            "source_backed": True,
        },
        "uncertainty_or_covariance": {
            "status": "public_covariance_matrix",
            "axes": [ENGINE_R4_SCALE_AXIS],
            "covariance": [[0.01]],
        },
        "measurement_likelihood_reference": {
            "status": "public_engine_usable",
            "target_axes": list(TARGET_R4_AXES),
            "likelihood_kind": "synthetic_scale_policy_control",
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
            "synthetic_control_not_claim_evidence": True,
        },
    }


def current_symbolic_only_r4_scale_slot() -> dict[str, Any]:
    return {
        "label": "current_symbolic_only_lambda_r4_scale_slot",
        "source_url": "",
        "source_type": "",
        "source_backed_absolute_normalization": {},
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
        },
    }


def _missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def _finite_positive(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if not isinstance(value, int | float):
        return False
    numeric = float(value)
    return math.isfinite(numeric) and numeric > 0.0


def _covariance_matrix_positive(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 1:
        return False
    row = value[0]
    if not isinstance(row, list) or len(row) != 1:
        return False
    return _finite_positive(row[0])


def evaluate_r4_scale_policy_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_SCALE_POLICY_FIELDS
        if _missing(packet.get(field))
    ]
    blockers: set[str] = set(missing_fields)

    source_url = str(packet.get("source_url") or "")
    if source_url and not source_url.startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.add("source_url_not_primary_allowed")
    if packet.get("source_type") and packet.get("source_type") not in VALID_SOURCE_TYPES:
        blockers.add("source_type_not_allowed")

    absolute = packet.get("source_backed_absolute_normalization")
    if not isinstance(absolute, dict):
        blockers.add("source_backed_absolute_normalization_missing")
    elif absolute.get("status") != "source_backed":
        blockers.add("source_backed_absolute_normalization_missing")
    elif absolute.get("operator") != "Riemann4":
        blockers.add("absolute_normalization_operator_not_riemann4")

    frame = packet.get("four_dimensional_frame_policy")
    if not isinstance(frame, dict):
        blockers.add("four_dimensional_frame_policy_missing")
    else:
        if frame.get("status") != "declared":
            blockers.add("four_dimensional_frame_policy_not_declared")
        if frame.get("frame") not in VALID_FRAME_POLICIES:
            blockers.add("four_dimensional_frame_choice_invalid")
        if frame.get("dimension") != 4:
            blockers.add("four_dimensional_policy_dimension_not_4")

    frame_map = packet.get("string_to_einstein_frame_map")
    if not isinstance(frame_map, dict):
        blockers.add("string_to_einstein_frame_map_missing")
    else:
        if frame_map.get("status") != "source_backed":
            blockers.add("string_to_einstein_frame_map_not_source_backed")
        if frame_map.get("map_declared") is not True:
            blockers.add("string_to_einstein_frame_map_not_declared")
        if frame_map.get("field_rescaling_closed") is not True:
            blockers.add("field_rescaling_not_closed")

    alpha = packet.get("alpha_prime_to_engine_lambda_r4")
    if not isinstance(alpha, dict):
        blockers.add("alpha_prime_to_engine_lambda_r4_missing")
    else:
        if alpha.get("status") != "numeric_source_backed":
            blockers.add("numeric_alpha_prime_to_lambda_r4_not_source_backed")
        if not _finite_positive(alpha.get("numeric_alpha_prime_value")):
            blockers.add("numeric_alpha_prime_value_missing")
        if alpha.get("maps_to_engine_axis") != ENGINE_R4_SCALE_AXIS:
            blockers.add("alpha_prime_map_engine_axis_mismatch")
        if alpha.get("lambda_power") != 8:
            blockers.add("lambda_r4_power_not_8")

    kappa = packet.get("kappa_normalization")
    if not isinstance(kappa, dict):
        blockers.add("kappa_normalization_missing")
    else:
        if kappa.get("status") != "declared":
            blockers.add("kappa_normalization_not_declared")
        if not _finite_positive(kappa.get("numeric_kappa_value")):
            blockers.add("numeric_kappa_value_missing")
        if kappa.get("dimensionless_engine_convention") is not True:
            blockers.add("kappa_dimensionless_engine_convention_missing")

    compactification = packet.get("compactification_volume_or_moduli_policy")
    if not isinstance(compactification, dict):
        blockers.add("compactification_volume_or_moduli_policy_missing")
    else:
        if compactification.get("status") != "declared":
            blockers.add("compactification_policy_not_declared")
        if compactification.get("volume_moduli_fixed") is not True:
            blockers.add("compactification_moduli_policy_missing")
        if compactification.get("policy_scope") != "four_dimensional_effective_action":
            blockers.add("compactification_policy_scope_invalid")

    field_policy = packet.get("field_redefinition_policy")
    if not isinstance(field_policy, dict):
        blockers.add("field_redefinition_policy_missing")
    else:
        mapped_axes = set(field_policy.get("mapped_axes") or [])
        if field_policy.get("status") != "maps_to_bresciani_r4_axes":
            blockers.add("field_redefinition_policy_not_bresciani_r4")
        if not set(TARGET_R4_AXES).issubset(mapped_axes):
            blockers.add("field_redefinition_mapped_axes_incomplete")
        if field_policy.get("field_redefinition_ambiguity_closed") is not True:
            blockers.add("field_redefinition_ambiguity_not_closed")

    contact = packet.get("dimensionful_contact_normalization")
    if not isinstance(contact, dict):
        blockers.add("dimensionful_contact_normalization_missing")
    else:
        expression = str(contact.get("expression") or "")
        if contact.get("status") != "declared":
            blockers.add("dimensionful_contact_normalization_not_declared")
        if "Lambda_R4^8" not in expression:
            blockers.add("dimensionful_contact_missing_lambda_r4_power")
        if (
            "alpha_prime" not in expression
            or "kappa" not in expression
            or contact.get("contains_alpha_prime_and_kappa") is not True
        ):
            blockers.add("dimensionful_contact_lost_alpha_prime_or_kappa")

    numeric = packet.get("engine_lambda_r4_numeric_value")
    if not isinstance(numeric, dict):
        blockers.add("engine_lambda_r4_numeric_value_missing")
    else:
        if numeric.get("status") != "public_engine_usable":
            blockers.add("engine_lambda_r4_value_not_public_engine_usable")
        if numeric.get("axis") != ENGINE_R4_SCALE_AXIS:
            blockers.add("engine_lambda_r4_axis_mismatch")
        if not _finite_positive(numeric.get("numeric_value")):
            blockers.add("engine_lambda_r4_numeric_value_missing")
        if numeric.get("unit") != "engine_R4_axis_units":
            blockers.add("engine_lambda_r4_unit_missing")
        if numeric.get("source_backed") is not True:
            blockers.add("engine_lambda_r4_source_backing_missing")

    covariance = packet.get("uncertainty_or_covariance")
    if not isinstance(covariance, dict):
        blockers.add("uncertainty_or_covariance_missing")
    else:
        if covariance.get("status") not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("uncertainty_or_covariance_not_public")
        if ENGINE_R4_SCALE_AXIS not in set(covariance.get("axes") or []):
            blockers.add("uncertainty_or_covariance_axis_missing")
        if (
            covariance.get("status") == "public_covariance_matrix"
            and not _covariance_matrix_positive(covariance.get("covariance"))
        ):
            blockers.add("uncertainty_or_covariance_matrix_invalid")

    likelihood = packet.get("measurement_likelihood_reference")
    if not isinstance(likelihood, dict):
        blockers.add("measurement_likelihood_reference_missing")
    else:
        if likelihood.get("status") not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("measurement_likelihood_reference_not_public")
        if not set(TARGET_R4_AXES).issubset(set(likelihood.get("target_axes") or [])):
            blockers.add("measurement_likelihood_target_axes_incomplete")

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
        missing_controls = list(REQUIRED_CLAIM_CONTROLS)
    else:
        missing_controls = [
            field for field in REQUIRED_CLAIM_CONTROLS if field not in controls
        ]
        blockers.update(f"claim_controls.{field}" for field in missing_controls)
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_must_remain_disabled_before_review")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_must_remain_disabled_before_review")
        if controls.get("external_adversarial_review_complete") is not False:
            blockers.add("external_review_must_be_false_in_preclaim_spec")

    synthetic = bool(
        packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )
    policy_ready = not blockers
    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not policy_ready:
        claim_blockers.add("numeric_lambda_r4_scale_policy_not_ready")

    return canonicalize_json_floats({
        "label": packet.get("label"),
        "ready_for_numeric_lambda_r4_scale_policy": policy_ready,
        "ready_for_framework_claim": False,
        "synthetic_control": synthetic,
        "missing_required_fields": sorted(missing_fields),
        "missing_claim_controls": sorted(missing_controls),
        "scale_policy_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "r4_numeric_scale_policy_ready_nonclaiming"
            if policy_ready
            else "r4_numeric_scale_policy_blocked"
        ),
    })


def current_r4_scale_source_gap_rows() -> list[dict[str, Any]]:
    rows = []
    for source in frame_scale_source_inputs():
        missing = sorted(source["does_not_provide"])
        rows.append({
            "label": source["source_id"],
            "source_url": source["url"],
            "source_role": source["source_role"],
            "machine_usable_symbolic_or_shape_input": source["machine_usable"],
            "fills_numeric_scale_contract_now": False,
            "missing_contract_capabilities": missing,
            "gap_count": len(missing),
        })

    for candidate in candidate_frame_scale_policies():
        missing = sorted({
            *candidate["missing_requirements"],
            *NUMERIC_CLAIM_BLOCKERS,
        })
        rows.append({
            "label": candidate["candidate"],
            "source_url": "",
            "source_role": "current_candidate_frame_scale_policy",
            "machine_usable_symbolic_or_shape_input": (
                candidate["ready_for_internal_symbolic_query"]
            ),
            "fills_numeric_scale_contract_now": False,
            "missing_contract_capabilities": missing,
            "gap_count": len(missing),
        })

    return sorted(rows, key=lambda row: (row["gap_count"], row["label"]))


def diagnose_r4_symbolic_scale_resolution_contract() -> dict[str, Any]:
    lambda_policy = diagnose_r4_lambda_unit_policy()
    frame_audit = diagnose_r4_frame_scale_policy_audit()
    synthetic = evaluate_r4_scale_policy_packet(
        synthetic_ready_r4_scale_policy_packet()
    )
    missing_slot = evaluate_r4_scale_policy_packet(
        current_symbolic_only_r4_scale_slot()
    )
    source_gaps = current_r4_scale_source_gap_rows()
    ready_current = [
        row["label"] for row in source_gaps
        if row["fills_numeric_scale_contract_now"]
    ]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.154_r4_lambda_unit_policy",
            "v2.156_r4_frame_scale_policy_audit",
            "v2.162_r4_shape_likelihood_ingestion_adapter",
        ],
        "route": "r4_symbolic_scale_resolution",
        "contract": r4_symbolic_scale_resolution_contract(),
        "symbolic_lambda_policy_ready": (
            lambda_policy["ready_for_symbolic_engine_lambda_policy"]
        ),
        "symbolic_query_ready": lambda_policy["ready_for_internal_symbolic_query"],
        "numeric_lambda_r4_ready_before_contract": (
            frame_audit["ready_numeric_lambda_r4_scale_policy"]
        ),
        "frame_scale_numeric_ready_candidates_before_contract": (
            frame_audit["numeric_lambda_r4_ready_candidates"]
        ),
        "synthetic_control_evaluation": synthetic,
        "current_symbolic_only_slot_evaluation": missing_slot,
        "current_source_gap_rows": source_gaps,
        "ready_current_numeric_scale_policies": ready_current,
        "numeric_claim_blockers": sorted(NUMERIC_CLAIM_BLOCKERS),
        "claimable_framework_exclusions_now": [],
        "claimable_discriminator_now": False,
        "route_status": "r4_scale_resolution_contract_ready_no_numeric_policy",
        "selected_next_build_action": (
            "search_or_request_source_backed_four_dimensional_r4_scale_policy"
        ),
        "best_next_artifact": (
            "A public source-backed numeric Lambda_R4 policy packet with a "
            "four-dimensional frame choice, string/Einstein-frame map, "
            "alpha-prime/kappa normalization, compactification or moduli "
            "policy, field-redefinition closure, covariance, and likelihood "
            "reference over the engine R4 axes."
        ),
        "interpretation": (
            "The symbolic R4 scale ledger remains useful and nonclaiming. "
            "v2.170 makes the missing numeric-scale object executable: a "
            "complete packet passes the engine gate, while every current "
            "source/candidate row still leaves the real numeric policy slot "
            "empty."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.170/"
            "r4_symbolic_scale_resolution_contract.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_symbolic_scale_resolution_contract()
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
