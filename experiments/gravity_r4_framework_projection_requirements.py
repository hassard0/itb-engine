"""Derive framework projection requirements for the gravity R4 axis candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_axis_extension_candidate import (
    VERSION as R4_CANDIDATE_VERSION,
    candidate_axis_contract,
    candidate_equations,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from itb.predict import FRAMEWORKS
from itb.scope import engine_validity


VERSION = "v2.132"

REQUIRED_R4_COEFFICIENTS = ("g_R4_c1", "g_R4_c2", "g_R4_c3")
DERIVED_R4_COORDINATES = ("g_R4_plus", "g_R4_minus_abs")
R4_METADATA_KEYS = (
    "r4_source_url",
    "r4_source_version",
    "r4_basis",
    "r4_operator_projection_matrix",
    "r4_normalization_scale",
    "r4_valid_energy_domain",
    "r4_uncertainty_or_covariance",
)


def r4_framework_projection_schema() -> list[dict[str, Any]]:
    return [
        {
            "field": f"coefficients.{axis}",
            "kind": "required_numeric_axis",
            "reason": "Framework-owned coefficient in the Bresciani R4 basis.",
        }
        for axis in REQUIRED_R4_COEFFICIENTS
    ] + [
        {
            "field": f"derived.{axis}",
            "kind": "derived_coordinate",
            "reason": "Needed for source unitarity and positivity templates.",
        }
        for axis in DERIVED_R4_COORDINATES
    ] + [
        {
            "field": f"metadata.{key}",
            "kind": "required_source_metadata",
            "reason": "Required before the axis can be normalized and audited.",
        }
        for key in R4_METADATA_KEYS
    ]


def _framework_requirement_profile(name: str) -> dict[str, Any]:
    if name == "string_tree_eft":
        return {
            "projection_class": "highest_priority_translation_candidate",
            "priority": 1,
            "source_path_status": "known_R4_family_but_no_engine_projection",
            "additional_blockers": [
                "string_r4_basis_translation_to_bresciani_missing",
                "string_scale_to_lambda_r4_normalization_missing",
                "compactification_frame_choice_missing",
            ],
            "next_required_data": (
                "A source-backed translation from the string tree-level R4 "
                "operator basis into c_1^(2), c_2^(2), c_3^(2), with the "
                "string scale and frame normalization fixed."
            ),
        }
    if name == "asymptotic_safety":
        return {
            "projection_class": "frg_truncation_candidate",
            "priority": 2,
            "source_path_status": "plausible_if_R4_fixed_point_couplings_exist",
            "additional_blockers": [
                "frg_r4_fixed_point_couplings_missing",
                "frg_basis_rotation_to_bresciani_missing",
                "rg_scale_to_lambda_r4_normalization_missing",
            ],
            "next_required_data": (
                "An FRG truncation that reports independent Riemann^4 "
                "couplings and a source-backed projection into the Bresciani "
                "three-coefficient basis."
            ),
        }
    if name in {"lqg_induced", "group_field_theory"}:
        return {
            "projection_class": "spin_foam_continuum_matching_candidate",
            "priority": 3,
            "source_path_status": "requires_semiclassical_eft_matching",
            "additional_blockers": [
                "spin_foam_r4_continuum_limit_missing",
                "spin_foam_basis_rotation_to_bresciani_missing",
                "semiclassical_scale_to_lambda_r4_missing",
            ],
            "next_required_data": (
                "A continuum semiclassical effective action with independent "
                "Riemann^4 terms, plus a basis rotation into c_i^(2)."
            ),
        }
    if name in {"cdt", "causal_set"}:
        return {
            "projection_class": "discrete_continuum_eft_candidate",
            "priority": 4,
            "source_path_status": "requires_continuum_effective_action_matching",
            "additional_blockers": [
                "discrete_continuum_r4_matching_missing",
                "discrete_scale_to_lambda_r4_missing",
            ],
            "next_required_data": (
                "A continuum effective action fit that isolates Riemann^4 "
                "operators and reports uncertainties in the Bresciani basis."
            ),
        }
    if name == "pure_gr":
        return {
            "projection_class": "null_baseline_policy_candidate",
            "priority": 5,
            "source_path_status": "zero_r4_baseline_requires_policy",
            "additional_blockers": [
                "pure_gr_zero_r4_baseline_policy_missing",
                "quantum_loop_r4_policy_missing",
            ],
            "next_required_data": (
                "A repository-level policy deciding whether pure GR encodes "
                "zero higher-curvature R4 coefficients or stays undefined."
            ),
        }
    if name == "horava_lifshitz":
        return {
            "projection_class": "lorentz_breaking_lifshitz_candidate",
            "priority": 6,
            "source_path_status": "out_of_current_lorentzian_r4_gate",
            "additional_blockers": [
                "lorentz_invariant_r4_gate_not_applicable",
                "lifshitz_basis_to_bresciani_missing",
            ],
            "next_required_data": (
                "A Lorentzian low-energy EFT limit with Riemann^4 couplings, "
                "or a separate non-Lorentzian R4 gate."
            ),
        }
    if name == "emergent_gravity":
        return {
            "projection_class": "outside_uv_wilson_axis_scope",
            "priority": 7,
            "source_path_status": "not_a_fundamental_uv_eft_projection",
            "additional_blockers": [
                "not_fundamental_uv_eft_axis",
                "nonlocal_emergent_r4_projection_missing",
            ],
            "next_required_data": (
                "A scope expansion showing how an emergent/nonlocal model owns "
                "UV Riemann^4 Wilson coefficients."
            ),
        }
    if name.startswith("discovered_"):
        return {
            "projection_class": "engine_generated_not_framework_owned",
            "priority": 8,
            "source_path_status": "not_source_owned_framework_evidence",
            "additional_blockers": [
                "engine_generated_framework_not_literature_owned",
                "r4_source_ownership_missing",
            ],
            "next_required_data": (
                "An external framework-owned derivation; generated Wilson "
                "points cannot define a source-backed R4 projection."
            ),
        }
    return {
        "projection_class": "generic_framework_projection_candidate",
        "priority": 9,
        "source_path_status": "no_registered_r4_path",
        "additional_blockers": ["framework_specific_r4_derivation_missing"],
        "next_required_data": (
            "A source-backed derivation of c_1^(2), c_2^(2), c_3^(2), "
            "normalization, and uncertainty."
        ),
    }


def _scope_blockers(framework: Any) -> list[str]:
    blockers: list[str] = []
    if not getattr(framework, "fundamental", True):
        blockers.append("framework_not_fundamental_uv_gravity")
    if not getattr(framework, "local", True):
        blockers.append("framework_not_local_for_current_r4_gate")
    if not getattr(framework, "lorentz_invariant", True):
        blockers.append("framework_not_lorentz_invariant_for_current_r4_gate")
    return blockers


def _r4_presence(framework: Any, theory: Any) -> dict[str, Any]:
    coefficient_keys = sorted(theory.coefficients)
    metadata_keys = sorted(theory.metadata)
    return {
        "encoded_coefficient_keys": coefficient_keys,
        "metadata_keys": metadata_keys,
        "required_r4_coefficients_present": [
            axis for axis in REQUIRED_R4_COEFFICIENTS
            if axis in theory.coefficients
        ],
        "derived_r4_coordinates_present": [
            axis for axis in DERIVED_R4_COORDINATES
            if axis in theory.metadata or axis in theory.coefficients
        ],
        "r4_metadata_keys_present": [
            key for key in R4_METADATA_KEYS
            if key in theory.metadata
        ],
        "has_native_r4_projection_method": callable(
            getattr(framework, "r4_projection", None)
        ),
    }


def _row(name: str, framework: Any) -> dict[str, Any]:
    theory = framework.encode()
    scope = engine_validity(framework)
    presence = _r4_presence(framework, theory)
    profile = _framework_requirement_profile(name)
    missing_coefficients = [
        axis for axis in REQUIRED_R4_COEFFICIENTS
        if axis not in presence["required_r4_coefficients_present"]
    ]
    missing_metadata = [
        key for key in R4_METADATA_KEYS
        if key not in presence["r4_metadata_keys_present"]
    ]
    blockers = set(profile["additional_blockers"])
    blockers.update(_scope_blockers(framework))
    if missing_coefficients:
        blockers.add("r4_coefficients_missing_from_encoder")
    if missing_metadata:
        blockers.add("r4_source_metadata_missing_from_encoder")
    if not presence["has_native_r4_projection_method"]:
        blockers.add("native_r4_projection_method_missing")

    projection_ready = (
        not missing_coefficients
        and not missing_metadata
        and presence["has_native_r4_projection_method"]
        and scope.in_scope
    )
    return {
        "framework": name,
        "citation": framework.citation,
        "engine_scope": {
            "in_scope": scope.in_scope,
            "violations": scope.violations,
            "note": scope.note,
        },
        "projection_class": profile["projection_class"],
        "priority": profile["priority"],
        "source_path_status": profile["source_path_status"],
        "r4_presence": presence,
        "missing_required_r4_coefficients": missing_coefficients,
        "missing_required_r4_metadata": missing_metadata,
        "r4_projection_ready": projection_ready,
        "can_enter_discriminator_math": False,
        "promotion_blockers": sorted(blockers),
        "next_required_data": profile["next_required_data"],
    }


def diagnose_gravity_r4_framework_projection_requirements() -> dict[str, Any]:
    rows = {
        name: _row(name, framework)
        for name, framework in FRAMEWORKS.items()
    }
    blocker_counts = {
        blocker: sum(
            1 for row in rows.values()
            if blocker in row["promotion_blockers"]
        )
        for blocker in sorted({
            blocker
            for row in rows.values()
            for blocker in row["promotion_blockers"]
        })
    }
    status_counts = {
        status: sum(
            1 for row in rows.values()
            if row["source_path_status"] == status
        )
        for status in sorted({
            row["source_path_status"] for row in rows.values()
        })
    }
    ready = [
        name for name, row in rows.items()
        if row["r4_projection_ready"]
    ]
    priorities = sorted(
        rows,
        key=lambda name: (rows[name]["priority"], name),
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            R4_CANDIDATE_VERSION,
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_v2",
            "registered_FRAMEWORKS_from_itb.predict",
        ],
        "candidate_axis_contract": candidate_axis_contract(),
        "candidate_equations": candidate_equations(),
        "r4_framework_projection_schema": r4_framework_projection_schema(),
        "registered_framework_count": len(rows),
        "r4_projection_ready_frameworks": ready,
        "frameworks_missing_r4_projection": sorted(
            name for name, row in rows.items()
            if not row["r4_projection_ready"]
        ),
        "highest_priority_translation_candidates": [
            name for name in priorities
            if rows[name]["priority"] <= 2
        ],
        "projection_status_counts": status_counts,
        "promotion_blocker_counts": blocker_counts,
        "claimable_framework_exclusions_now": [],
        "frameworks": rows,
        "route_status": "r4_framework_projection_requirements_defined_nonclaiming",
        "selected_next_build_action": "implement_r4_projection_guard_schema",
        "best_next_artifact": (
            "A small R4 projection guard/schema that can reject partial "
            "framework adapters until all required coefficients, metadata, "
            "normalization, and source ownership fields are present."
        ),
        "interpretation": (
            "No registered framework currently exposes the Bresciani R4 "
            "coordinates or their source metadata. String tree-level EFT is "
            "the most promising translation target, but it still needs a "
            "basis rotation, scale normalization, and uncertainty model before "
            "the R4 axis can enter discriminator math."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.132/"
            "gravity_r4_framework_projection_requirements.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gravity_r4_framework_projection_requirements()
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
