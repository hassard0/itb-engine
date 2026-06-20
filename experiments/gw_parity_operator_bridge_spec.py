"""GW parity PPV-to-engine operator bridge specification (v2.168)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_parity_adapter_readiness import (
    candidate_rows,
    diagnose_gw_parity_adapter_readiness,
)


VERSION = "v2.168"
ENGINE_PARITY_AXES = ("g_R2_parity", "g_R3_parity")
REQUIRED_BRIDGE_FIELDS = (
    "label",
    "source_url",
    "source_type",
    "source_native_likelihood",
    "source_backed_operator_normalization",
    "ppv_parameter_definition",
    "engine_axis_target",
    "sign_convention",
    "unit_conversion",
    "frequency_reference",
    "covariance_or_samples",
    "helicity_basis_harmonization",
    "framework_exclusion_projection",
    "claim_controls",
)
REQUIRED_CLAIM_CONTROLS = (
    "claim_use_allowed",
    "framework_claim_allowed",
    "external_adversarial_review_complete",
)


def gw_parity_operator_bridge_contract() -> dict[str, Any]:
    return {
        "version": VERSION,
        "route": "gw_parity_operator_normalization_search",
        "external_object": "ppv_to_engine_parity_operator_bridge",
        "required_bridge_fields": list(REQUIRED_BRIDGE_FIELDS),
        "engine_parity_axes": list(ENGINE_PARITY_AXES),
        "claim_control_fields": list(REQUIRED_CLAIM_CONTROLS),
        "source_url_policy": "https://arxiv.org/ or https://doi.org/",
        "claim_rule": (
            "The bridge can become engine-ready only with a source-backed "
            "operator normalization, dimensionless unit conversion, frequency "
            "reference, helicity convention, covariance/samples, and framework "
            "projection. Claims remain disabled until external adversarial "
            "review completes."
        ),
    }


def synthetic_ready_parity_bridge_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_ppv_to_engine_parity_bridge",
        "source_url": "https://doi.org/10.0000/synthetic-parity-bridge",
        "source_type": "validated_measurement",
        "source_native_likelihood": {
            "status": "public_engine_usable",
            "source_parameter": "kappa_Gpc^-1_at_100_Hz",
            "central_value": -0.019,
            "covariance_axes": ["kappa_Gpc^-1_at_100_Hz"],
        },
        "source_backed_operator_normalization": {
            "status": "source_backed",
            "operator_identity": (
                "synthetic kappa_100Hz to g_R2_parity/g_R3_parity map"
            ),
            "source_url": "https://doi.org/10.0000/synthetic-parity-bridge",
        },
        "ppv_parameter_definition": {
            "parameter": "beta_1_0",
            "basis": "parameterized_parity_violation",
            "dimensionless_definition_declared": True,
        },
        "engine_axis_target": {
            "axes": list(ENGINE_PARITY_AXES),
            "normalization": "engine_low_energy_parity_axes",
        },
        "sign_convention": {
            "status": "declared",
            "helicity_sign": "right_minus_left",
        },
        "unit_conversion": {
            "status": "dimensionless_engine_ready",
            "converts_kappa_gpc_to_engine_axis": True,
        },
        "frequency_reference": {
            "status": "declared",
            "reference_hz": 100.0,
        },
        "covariance_or_samples": {
            "status": "public_covariance_matrix",
            "axes": ["kappa_Gpc^-1_at_100_Hz"],
        },
        "helicity_basis_harmonization": {
            "status": "source_backed",
            "engine_helicity_basis": "canonical_engine_parity_basis",
        },
        "framework_exclusion_projection": {
            "status": "excludes_registered_framework",
            "projection_matrix_axes": list(ENGINE_PARITY_AXES),
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
            "synthetic_control_not_claim_evidence": True,
        },
    }


def current_missing_parity_bridge_slot() -> dict[str, Any]:
    return {
        "label": "current_missing_ppv_to_engine_parity_bridge_slot",
        "source_url": "",
        "source_type": "",
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
        },
    }


def _missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def evaluate_gw_parity_operator_bridge_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_BRIDGE_FIELDS if _missing(packet.get(field))
    ]
    blockers: set[str] = set(missing_fields)

    source_url = str(packet.get("source_url") or "")
    if source_url and not source_url.startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.add("source_url_not_primary_allowed")

    likelihood = packet.get("source_native_likelihood")
    if not isinstance(likelihood, dict):
        blockers.add("source_native_likelihood_missing")
    elif likelihood.get("status") not in {
        "public_engine_usable",
        "public_covariance_matrix",
        "public_likelihood_samples",
    }:
        blockers.add("source_native_likelihood_not_public_engine_usable")

    operator = packet.get("source_backed_operator_normalization")
    if not isinstance(operator, dict):
        blockers.add("source_backed_operator_normalization_missing")
    elif operator.get("status") != "source_backed":
        blockers.add("source_backed_operator_normalization_missing")

    definition = packet.get("ppv_parameter_definition")
    if not isinstance(definition, dict):
        blockers.add("ppv_parameter_definition_missing")
    elif definition.get("dimensionless_definition_declared") is not True:
        blockers.add("dimensionless_ppv_normalization_missing")

    target = packet.get("engine_axis_target")
    if not isinstance(target, dict):
        blockers.add("engine_axis_target_missing")
    else:
        axes = set(target.get("axes") or [])
        if not axes & set(ENGINE_PARITY_AXES):
            blockers.add("engine_axis_target_missing")
        if target.get("normalization") != "engine_low_energy_parity_axes":
            blockers.add("engine_parity_normalization_missing")

    sign = packet.get("sign_convention")
    if not isinstance(sign, dict) or sign.get("status") != "declared":
        blockers.add("sign_convention_missing")

    conversion = packet.get("unit_conversion")
    if (
        not isinstance(conversion, dict)
        or conversion.get("status") != "dimensionless_engine_ready"
    ):
        blockers.add("dimensionful_to_dimensionless_normalization_missing")

    frequency = packet.get("frequency_reference")
    if not isinstance(frequency, dict) or frequency.get("status") != "declared":
        blockers.add("frequency_reference_missing")

    covariance = packet.get("covariance_or_samples")
    if not isinstance(covariance, dict):
        blockers.add("covariance_or_samples_missing")
    elif covariance.get("status") not in {
        "public_covariance_matrix",
        "public_likelihood_samples",
    }:
        blockers.add("covariance_or_samples_not_public")

    helicity = packet.get("helicity_basis_harmonization")
    if not isinstance(helicity, dict) or helicity.get("status") != "source_backed":
        blockers.add("helicity_harmonization_missing")

    projection = packet.get("framework_exclusion_projection")
    if not isinstance(projection, dict):
        blockers.add("framework_exclusion_projection_missing")
    elif projection.get("status") != "excludes_registered_framework":
        blockers.add("framework_exclusion_math_missing")

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
    bridge_ready = not blockers
    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not bridge_ready:
        claim_blockers.add("parity_operator_bridge_not_ready")

    return canonicalize_json_floats({
        "label": packet.get("label"),
        "ready_for_engine_parity_bridge": bridge_ready,
        "ready_for_framework_claim": False,
        "synthetic_control": synthetic,
        "missing_required_fields": sorted(missing_fields),
        "missing_claim_controls": sorted(missing_controls),
        "bridge_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "gw_parity_operator_bridge_ready_nonclaiming"
            if bridge_ready
            else "gw_parity_operator_bridge_blocked"
        ),
    })


def current_parity_source_gap_rows() -> list[dict[str, Any]]:
    rows = []
    for candidate in candidate_rows():
        rows.append({
            "label": candidate["label"],
            "source": candidate["source"],
            "source_side_likelihood_ready": candidate["source_side_likelihood_ready"],
            "engine_adapter_ready": candidate["engine_adapter_ready"],
            "adapter_blockers": candidate["adapter_blockers"],
            "fills_operator_bridge_contract_now": False,
            "gap_count": len(candidate["adapter_blockers"]),
        })
    return sorted(rows, key=lambda row: (row["gap_count"], row["label"]))


def diagnose_gw_parity_operator_bridge_spec() -> dict[str, Any]:
    readiness = diagnose_gw_parity_adapter_readiness()
    synthetic = evaluate_gw_parity_operator_bridge_packet(
        synthetic_ready_parity_bridge_packet()
    )
    missing_slot = evaluate_gw_parity_operator_bridge_packet(
        current_missing_parity_bridge_slot()
    )
    source_gaps = current_parity_source_gap_rows()
    ready_current = [
        row["label"] for row in source_gaps if row["fills_operator_bridge_contract_now"]
    ]

    return {
        "version": VERSION,
        "basis": [
            "v2.61_gw_parity_adapter_readiness",
            "v2.76_gw_parity_route_decision",
            "v2.92_external_evidence_packet_contract",
        ],
        "route": "gw_parity_operator_normalization_search",
        "contract": gw_parity_operator_bridge_contract(),
        "source_side_likelihood_ready_routes": (
            readiness["source_side_likelihood_ready_routes"]
        ),
        "engine_adapter_ready_routes_before_bridge": (
            readiness["engine_adapter_ready_routes"]
        ),
        "synthetic_control_evaluation": synthetic,
        "current_missing_bridge_slot_evaluation": missing_slot,
        "current_source_gap_rows": source_gaps,
        "ready_current_operator_bridges": ready_current,
        "claimable_framework_exclusions_now": [],
        "claimable_discriminator_now": False,
        "route_status": "gw_parity_operator_bridge_spec_ready_no_real_bridge",
        "selected_next_build_action": (
            "search_or_derive_source_backed_ppv_to_engine_parity_bridge"
        ),
        "best_next_artifact": (
            "A source-backed PPV/native parity operator-normalization bridge "
            "that maps public GW parity likelihood material into engine "
            "g_R2_parity/g_R3_parity axes with declared units and helicity basis."
        ),
        "interpretation": (
            "Public source-side GW parity likelihood material exists, but no "
            "current row fills the operator-normalization bridge into engine "
            "axes. The new evaluator can accept a complete bridge packet while "
            "keeping claims disabled before adversarial review."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.168/"
            "gw_parity_operator_bridge_spec.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_operator_bridge_spec()
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
