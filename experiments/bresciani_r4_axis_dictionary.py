"""Machine-readable Bresciani R4 axis dictionary for packet builders."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_k_monomial_projector import bresciani_monomial_families
from experiments.explicit_tower_basis import _json_default
from experiments.four_dimensional_r4_projection_derivation_workbench import (
    derive_bresciani_from_source_projection,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_shape_likelihood_packet_manifest import TARGET_AXES
from experiments.r4_shape_normalization_policy import (
    engine_r4_shape_normalization_policy,
    evaluate_r4_shape_normalization_policy,
)


VERSION = "v2.175"
DICTIONARY_ID = "bresciani_r4_axis_dictionary_v1"
BRESCIANI_SOURCE_URL = "https://arxiv.org/abs/2504.12855"
PROJECTION_AXES = ("g_R4_c1", "g_R4_c2", "g_R4_c3")
DERIVED_AXES = ("g_R4_plus", "g_R4_minus_abs")
DOWNSTREAM_LIKELIHOOD_BLOCKERS = (
    "modified_gravity_r4_waveform_adapter_missing",
    "public_covariance_over_engine_r4_axes_missing",
    "framework_exclusion_math_missing",
    "external_adversarial_review_missing",
)


def project_bresciani_components_to_engine_axes(
    *,
    overall_r4_factor: float,
    k_plus: float,
    k_minus_real: float,
    k_minus_imag: float,
) -> dict[str, Any]:
    """Project source K components into engine R4 axes."""
    projection = derive_bresciani_from_source_projection(
        overall_r4_factor=overall_r4_factor,
        k_plus=k_plus,
        k_minus_real=k_minus_real,
        k_minus_imag=k_minus_imag,
    )
    return canonicalize_json_floats({
        "input_components": {
            "overall_R4_factor": overall_r4_factor,
            "K_plus": k_plus,
            "K_minus_real": k_minus_real,
            "K_minus_imag": k_minus_imag,
        },
        "helicity_coordinates": projection["helicity_coordinates"],
        "coefficients": projection["inverted_coefficients"],
        "derived": projection["derived_coordinates"],
        "positivity_summary": projection["positivity_summary"],
    })


def bresciani_r4_axis_mapping_sidecar() -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    return canonicalize_json_floats({
        "dictionary_id": DICTIONARY_ID,
        "dictionary_version": VERSION,
        "status": "maps_to_bresciani_r4_axes",
        "mapped_axes": list(TARGET_AXES),
        "projection_axes": list(PROJECTION_AXES),
        "derived_axes": list(DERIVED_AXES),
        "source_coordinates": [
            "overall_R4_factor",
            "K_plus",
            "Re(K_minus)",
            "Im(K_minus)",
        ],
        "axis_normalization_declared": True,
        "normalization_scope": "shape_likelihood_only",
        "uses_numeric_lambda_r4_scale": False,
        "engine_unit_policy_id": policy["policy_id"],
        "engine_unit_policy_version": policy["version"],
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "axis_dictionary_only_not_claim_evidence": True,
        },
    })


def bresciani_r4_axis_dictionary() -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    policy_evaluation = evaluate_r4_shape_normalization_policy(policy)
    unit = policy["engine_unit_definition"]
    shape_source = policy["normalized_shape_source"]
    engine_unit_projection = project_bresciani_components_to_engine_axes(
        overall_r4_factor=float(unit["overall_R4_factor"]),
        k_plus=float(shape_source["K_plus"]),
        k_minus_real=float(shape_source["K_minus_real"]),
        k_minus_imag=float(shape_source["K_minus_imag"]),
    )
    mixed_helicity_control = project_bresciani_components_to_engine_axes(
        overall_r4_factor=8.0,
        k_plus=0.3,
        k_minus_real=0.1,
        k_minus_imag=0.05,
    )

    return canonicalize_json_floats({
        "dictionary_id": DICTIONARY_ID,
        "version": VERSION,
        "source": {
            "primary_source_url": BRESCIANI_SOURCE_URL,
            "source_equation_refs": [
                "eq:amplitude",
                "eq:Lag-quartic",
                "c_plus_c_minus_definitions",
            ],
            "basis": "Bresciani_c_i_spin2_Riemann4",
            "spin": 2,
        },
        "target_axes": list(TARGET_AXES),
        "monomial_family_dictionary": bresciani_monomial_families(),
        "source_to_engine_relations": {
            "source_coordinates": [
                "overall_R4_factor",
                "K_plus",
                "Re(K_minus)",
                "Im(K_minus)",
            ],
            "helicity_coordinates": {
                "c_plus": "overall_R4_factor*K_plus/8",
                "Re(c_minus)": "overall_R4_factor*Re(K_minus)/8",
                "Im(c_minus)": "overall_R4_factor*Im(K_minus)/8",
            },
            "engine_axis_equations": {
                "g_R4_c1": (
                    "overall_R4_factor*(K_plus + Re(K_minus))/16"
                ),
                "g_R4_c2": (
                    "overall_R4_factor*(K_plus - Re(K_minus))/16"
                ),
                "g_R4_c3": "overall_R4_factor*Im(K_minus)/8",
                "g_R4_plus": "overall_R4_factor*K_plus/8",
                "g_R4_minus_abs": (
                    "overall_R4_factor*sqrt(Re(K_minus)^2 + "
                    "Im(K_minus)^2)/8"
                ),
            },
            "engine_unit_simplification": {
                "condition": "overall_R4_factor=8",
                "g_R4_c1": "(K_plus + Re(K_minus))/2",
                "g_R4_c2": "(K_plus - Re(K_minus))/2",
                "g_R4_c3": "Im(K_minus)",
                "g_R4_plus": "K_plus",
                "g_R4_minus_abs": (
                    "sqrt(Re(K_minus)^2 + Im(K_minus)^2)"
                ),
            },
        },
        "operator_projection_matrix": {
            "status": "maps_to_bresciani_r4_axes",
            "rows": list(PROJECTION_AXES),
            "columns": ["K_plus", "Re(K_minus)", "Im(K_minus)"],
            "matrix_for_overall_R4_factor_8": [
                [0.5, 0.5, 0.0],
                [0.5, -0.5, 0.0],
                [0.0, 0.0, 1.0],
            ],
            "derived_axis_rule": {
                "g_R4_plus": "g_R4_c1 + g_R4_c2",
                "g_R4_minus_abs": "sqrt((g_R4_c1-g_R4_c2)^2 + g_R4_c3^2)",
            },
        },
        "normalization_contract": {
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"],
            "axis_normalization_declared": True,
            "normalization_scope": "shape_likelihood_only",
            "uses_numeric_lambda_r4_scale": False,
            "absolute_string_alpha_prime_normalization_backed": False,
            "engine_lambda_r4_unit_conversion_source_backed": False,
            "claim_use_allowed": False,
            "engine_unit_definition": unit,
            "policy_evaluation": policy_evaluation,
        },
        "domain_contract": {
            "status": "bounded_for_qg_eft",
            "shared_domain_with_query_row": True,
            "domain_scope": "dimensionless R4 shape axes",
            "physical_scale_claim_allowed": False,
        },
        "packet_builder_exports": {
            "axis_mapping": bresciani_r4_axis_mapping_sidecar(),
            "expected_manifest_target_axes": list(TARGET_AXES),
            "required_likelihood_axes_for_first_public_packet": (
                list(PROJECTION_AXES)
            ),
        },
        "calibration_examples": {
            "engine_unit_shape": engine_unit_projection,
            "mixed_helicity_control": mixed_helicity_control,
        },
        "provenance": {
            "source_backed_axis_formalism": True,
            "source_backed_engine_unit_shape": (
                shape_source["source_backed_shape"]
            ),
            "public_likelihood_or_covariance": False,
            "reproducible_data_or_code": True,
            "synthetic_measurement_fixture": False,
        },
        "likelihood": {
            "status": "not_attached",
            "public_covariance_over_target_axes": False,
            "public_likelihood_samples_over_target_axes": False,
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "axis_dictionary_only_not_claim_evidence": True,
        },
    })


def _project_formula_from_dictionary(
    axis_dictionary: dict[str, Any],
    *,
    overall_r4_factor: float,
    k_plus: float,
    k_minus_real: float,
    k_minus_imag: float,
) -> dict[str, Any]:
    relations = axis_dictionary.get("source_to_engine_relations", {})
    equations = relations.get("engine_axis_equations", {})
    required = set(TARGET_AXES)
    if not isinstance(equations, dict) or not required.issubset(equations):
        return {"ready": False, "blocker": "engine_axis_equations_incomplete"}

    scale = overall_r4_factor / 8.0
    c1 = scale * (k_plus + k_minus_real) / 2.0
    c2 = scale * (k_plus - k_minus_real) / 2.0
    c3 = scale * k_minus_imag
    return canonicalize_json_floats({
        "ready": True,
        "coefficients": {
            "g_R4_c1": c1,
            "g_R4_c2": c2,
            "g_R4_c3": c3,
        },
        "derived": {
            "g_R4_plus": c1 + c2,
            "g_R4_minus_abs": math.hypot(c1 - c2, c3),
        },
    })


def evaluate_bresciani_r4_axis_dictionary(
    axis_dictionary: dict[str, Any],
) -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    blockers: set[str] = set()
    target_axes = set(axis_dictionary.get("target_axes", []))
    if not set(TARGET_AXES).issubset(target_axes):
        blockers.add("target_axes_incomplete")

    source = axis_dictionary.get("source")
    if not isinstance(source, dict) or source.get("primary_source_url") != BRESCIANI_SOURCE_URL:
        blockers.add("bresciani_source_missing")

    families = axis_dictionary.get("monomial_family_dictionary")
    if families != bresciani_monomial_families():
        blockers.add("bresciani_monomial_families_changed")

    matrix = axis_dictionary.get("operator_projection_matrix")
    if not isinstance(matrix, dict) or matrix.get("status") != "maps_to_bresciani_r4_axes":
        blockers.add("operator_projection_matrix_not_bresciani")
    elif not set(PROJECTION_AXES).issubset(set(matrix.get("rows", []))):
        blockers.add("operator_projection_rows_incomplete")

    normalization = axis_dictionary.get("normalization_contract")
    if not isinstance(normalization, dict):
        blockers.add("normalization_contract_missing")
    else:
        if normalization.get("policy_id") != policy["policy_id"]:
            blockers.add("normalization_policy_id_mismatch")
        if normalization.get("axis_normalization_declared") is not True:
            blockers.add("axis_normalization_not_declared")
        if normalization.get("uses_numeric_lambda_r4_scale") is not False:
            blockers.add("numeric_lambda_r4_scale_not_disabled")
        if normalization.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")

    domain = axis_dictionary.get("domain_contract")
    if not isinstance(domain, dict) or domain.get("shared_domain_with_query_row") is not True:
        blockers.add("domain_not_shared_with_query_row")

    sidecar = axis_dictionary.get("packet_builder_exports", {}).get("axis_mapping")
    if not isinstance(sidecar, dict) or sidecar.get("status") != "maps_to_bresciani_r4_axes":
        blockers.add("axis_mapping_sidecar_missing")
    elif not set(TARGET_AXES).issubset(set(sidecar.get("mapped_axes", []))):
        blockers.add("axis_mapping_axes_incomplete")

    controls = axis_dictionary.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_not_disabled")
        if controls.get("axis_dictionary_only_not_claim_evidence") is not True:
            blockers.add("dictionary_not_marked_nonclaiming")

    engine_unit_formula = _project_formula_from_dictionary(
        axis_dictionary,
        overall_r4_factor=8.0,
        k_plus=1.0,
        k_minus_real=0.0,
        k_minus_imag=0.0,
    )
    if engine_unit_formula.get("ready") is not True:
        blockers.add(engine_unit_formula["blocker"])
    else:
        unit = policy["engine_unit_definition"]
        coefficients = engine_unit_formula["coefficients"]
        if coefficients["g_R4_c1"] != unit["g_R4_c1"]:
            blockers.add("engine_unit_g_R4_c1_mismatch")
        if coefficients["g_R4_c2"] != unit["g_R4_c2"]:
            blockers.add("engine_unit_g_R4_c2_mismatch")
        if coefficients["g_R4_c3"] != unit["g_R4_c3"]:
            blockers.add("engine_unit_g_R4_c3_mismatch")

    likelihood = axis_dictionary.get("likelihood")
    if not isinstance(likelihood, dict) or likelihood.get("status") != "not_attached":
        blockers.add("likelihood_status_not_dictionary_only")

    return canonicalize_json_floats({
        "dictionary_id": axis_dictionary.get("dictionary_id"),
        "ready_for_r4_shape_packet_axis_mapping": not blockers,
        "ready_for_likelihood_packet": False,
        "ready_for_framework_claim": False,
        "blockers": sorted(blockers),
        "downstream_likelihood_blockers": list(DOWNSTREAM_LIKELIHOOD_BLOCKERS),
        "engine_unit_formula_check": engine_unit_formula,
    })


def diagnose_bresciani_r4_axis_dictionary() -> dict[str, Any]:
    axis_dictionary = bresciani_r4_axis_dictionary()
    evaluation = evaluate_bresciani_r4_axis_dictionary(axis_dictionary)
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.174_r4_live_source_acquisition_queue",
            "v2.160_r4_shape_likelihood_packet_manifest",
            "v2.158_bresciani_r4_shape_unitarity_diagnostic",
            "v2.148_policy_scoped_string_tree_r4_projection_packet",
            "v2.143_bresciani_k_monomial_projector",
            "v2.139_four_dimensional_r4_projection_derivation_workbench",
        ],
        "axis_dictionary": axis_dictionary,
        "evaluation": evaluation,
        "ready_for_r4_shape_packet_axis_mapping": (
            evaluation["ready_for_r4_shape_packet_axis_mapping"]
        ),
        "ready_for_likelihood_packet": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "current_claim_blockers": list(DOWNSTREAM_LIKELIHOOD_BLOCKERS),
        "route_status": "bresciani_r4_axis_dictionary_ready_nonclaiming",
        "selected_next_build_action": (
            "build_public_gw_reanalysis_fixture_for_r4_waveform_model"
        ),
        "best_next_artifact": (
            "A public GW reanalysis fixture that emits central values and a "
            "covariance over g_R4_c1, g_R4_c2, and g_R4_c3 using this "
            "dictionary as the axis contract."
        ),
        "interpretation": (
            "The R4 source axis map is now machine-readable and compatible "
            "with the v2.160 packet manifest. It is ready for adapter and "
            "public-reanalysis construction, but it is not a likelihood packet "
            "and cannot support a framework claim by itself."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.175/"
            "bresciani_r4_axis_dictionary.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_bresciani_r4_axis_dictionary()
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
