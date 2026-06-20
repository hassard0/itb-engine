"""Policy-scoped string_tree_eft R4 projection packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.four_dimensional_r4_projection_derivation_workbench import (
    derive_bresciani_from_source_projection,
)
from experiments.gravity_r4_projection_guard_schema import (
    evaluate_r4_projection_packet,
)
from experiments.gravity_r4_source_provenance_guard import (
    evaluate_r4_source_provenance_packet,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_shape_normalization_policy import (
    engine_r4_shape_normalization_policy,
    evaluate_r4_shape_normalization_policy,
)


VERSION = "v2.148"

SOURCE_URLS = [
    "https://arxiv.org/abs/0811.3417",
    "https://arxiv.org/abs/2504.12855",
    "https://arxiv.org/abs/hep-th/9707241",
]
REMAINING_ABSOLUTE_NORMALIZATION_GAPS = [
    "absolute_type_II_string_alpha_prime_R4_coefficient",
    "engine_Lambda_R4_unit_conversion",
    "source_backed_K_Russo_to_Kallosh_shape_bridge",
]


def _policy_projection_components() -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    unit = policy["engine_unit_definition"]
    shape = policy["normalized_shape_source"]
    projection = derive_bresciani_from_source_projection(
        overall_r4_factor=float(unit["overall_R4_factor"]),
        k_plus=float(shape["K_plus"]),
        k_minus_real=float(shape["K_minus_real"]),
        k_minus_imag=float(shape["K_minus_imag"]),
    )
    return {
        "policy": policy,
        "projection": projection,
        "coefficients": projection["inverted_coefficients"],
        "derived": projection["derived_coordinates"],
    }


def policy_scoped_string_tree_r4_projection_packet() -> dict[str, Any]:
    components = _policy_projection_components()
    policy = components["policy"]
    unit = policy["engine_unit_definition"]
    coefficients = components["coefficients"]
    derived = components["derived"]
    source_url = policy["normalized_shape_source"]["source_urls"][0]
    return canonicalize_json_floats({
        "framework": "string_tree_eft",
        "axis_family": "gravity_R4_Riemann4",
        "source_url": source_url,
        "source_type": "computed_framework_projection",
        "source_version": "engine_r4_shape_unit_v1_policy_scoped",
        "adapter_kind": "framework_native_r4_projection",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "coefficients": coefficients,
        "derived": derived,
        "normalization": {
            "status": "engine_lambda_r4_defined",
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"],
            "allowed_policy_use": "internal_bresciani_basis_projection",
            "overall_R4_factor": unit["overall_R4_factor"],
            "absolute_string_alpha_prime_normalization_backed": False,
            "engine_lambda_r4_unit_conversion_source_backed": False,
            "k_convention_bridge_source_backed": False,
            "claim_use_allowed": False,
        },
        "operator_projection_matrix": {
            "status": "source_backed",
            "source_basis": "Kallosh/Bresciani R4 helicity shape",
            "target_basis": "Bresciani c_i spin-2 Riemann4",
            "rows": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "columns": ["K_plus", "Re(K_minus)", "Im(K_minus)"],
            "matrix": [
                [0.5, 0.5, 0.0],
                [0.5, -0.5, 0.0],
                [0.0, 0.0, 1.0],
            ],
            "matching_equation": (
                "With overall_R4_factor=8, Bresciani c_plus=K_plus and "
                "c_minus=K_minus, then c1=(c_plus+Re(c_minus))/2, "
                "c2=(c_plus-Re(c_minus))/2, c3=Im(c_minus)."
            ),
        },
        "valid_energy_domain": {
            "status": "bounded_for_qg_eft",
            "domain_scope": "dimensionless R4 shape algebra only",
            "physical_scale_claim_allowed": False,
        },
        "uncertainty_or_covariance": {
            "status": "bounded_systematic_envelope",
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "relative_envelope": 0.0,
            "scope": (
                "source-backed shape reanalysis under the v2.147 unit policy; "
                "absolute coefficient uncertainty is represented by claim "
                "blockers, not by a measurement covariance."
            ),
        },
        "ownership_metadata": {
            "framework_owned_derivation": (
                "policy-scoped string_tree_eft R4 adapter shape derived from "
                "the maximally supersymmetric R4 source family"
            ),
            "source_owned_by_framework": True,
            "policy_scoped_not_absolute_framework_coefficient": True,
        },
        "source_provenance": {
            "source_backed_derivation": True,
            "derivation_kind": "validated_public_reanalysis",
            "primary_source_urls": SOURCE_URLS,
            "synthetic_fixture": False,
            "derivation_scope": (
                "Internal R4 helicity-shape projection only. This packet does "
                "not provide the absolute type-II string alpha-prime "
                "normalization or an engine Lambda_R4 conversion."
            ),
            "source_equation_refs": {
                "kallosh_lee_rube_2008": [
                    "Omega4",
                    "P3-loop_UV",
                    "M_UV_3-loop",
                ],
                "bresciani_levati_paradisi_2025": [
                    "eq:amplitude",
                    "c_plus_c_minus_definitions",
                ],
                "russo_1997": [
                    "A4",
                    "A4^0",
                    "2*zeta(3)_contact_scalar",
                ],
            },
        },
        "unitarity_bound": {
            "status": "source_backed",
            "uses_bresciani_spin2_bound": True,
            "source_url": "https://arxiv.org/abs/2504.12855",
        },
        "positivity_status": "checked",
        "discriminator_math": "projection_only",
    })


def evaluate_policy_scoped_string_tree_r4_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    policy = engine_r4_shape_normalization_policy()
    policy_evaluation = evaluate_r4_shape_normalization_policy(policy)
    normalization = packet.get("normalization")
    blockers: set[str] = set()
    warnings: set[str] = set(REMAINING_ABSOLUTE_NORMALIZATION_GAPS)

    if not isinstance(normalization, dict):
        blockers.add("normalization_missing")
    else:
        if normalization.get("policy_id") != policy["policy_id"]:
            blockers.add("normalization_policy_id_mismatch")
        if normalization.get("allowed_policy_use") not in policy["allowed_uses"]:
            blockers.add("normalization_policy_use_not_allowed")
        if normalization.get("absolute_string_alpha_prime_normalization_backed") is not False:
            blockers.add("absolute_string_normalization_not_disabled")
        if normalization.get("engine_lambda_r4_unit_conversion_source_backed") is not False:
            blockers.add("engine_lambda_r4_unit_conversion_not_disabled")
        if normalization.get("k_convention_bridge_source_backed") is not False:
            blockers.add("k_convention_bridge_not_disabled")
        if normalization.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")

    if policy_evaluation["ready_for_internal_shape_normalization"] is not True:
        blockers.add("engine_shape_policy_not_ready")
    if policy_evaluation["ready_for_absolute_string_normalization"] is not False:
        blockers.add("absolute_string_normalization_unexpectedly_ready")
    if policy_evaluation["ready_for_framework_claim"] is not False:
        blockers.add("framework_claim_unexpectedly_ready")

    return canonicalize_json_floats({
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "ready_for_policy_scoped_projection": not blockers,
        "ready_for_absolute_normalized_projection": False,
        "ready_for_framework_claim": False,
        "blockers": sorted(blockers),
        "remaining_absolute_normalization_gaps": sorted(warnings),
        "allowed_policy_use": (
            normalization.get("allowed_policy_use")
            if isinstance(normalization, dict)
            else None
        ),
    })


def diagnose_policy_scoped_string_tree_r4_projection_packet() -> dict[str, Any]:
    packet = policy_scoped_string_tree_r4_projection_packet()
    policy_scope = evaluate_policy_scoped_string_tree_r4_packet(packet)
    base_guard = evaluate_r4_projection_packet(packet)
    strict_guard = evaluate_r4_source_provenance_packet(packet)
    ready_policy_projection = (
        policy_scope["ready_for_policy_scoped_projection"]
        and base_guard["ready_for_framework_projection"]
        and strict_guard["ready_for_source_backed_framework_projection"]
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.147_r4_shape_normalization_policy",
            "v2.144_supersymmetric_r4_shape_projection",
            "v2.137_gravity_r4_source_provenance_guard",
            "v2.133_gravity_r4_projection_guard_schema",
        ],
        "projection_packet": packet,
        "policy_scope_evaluation": policy_scope,
        "base_guard_result": base_guard,
        "strict_source_guard_result": strict_guard,
        "ready_for_policy_scoped_projection": ready_policy_projection,
        "ready_for_absolute_normalized_projection": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "current_claim_blockers": strict_guard["strict_claim_blockers"],
        "remaining_absolute_normalization_gaps": (
            REMAINING_ABSOLUTE_NORMALIZATION_GAPS
        ),
        "route_status": (
            "policy_scoped_string_tree_r4_projection_packet_ready_nonclaiming"
        ),
        "selected_next_build_action": (
            "register_policy_scoped_r4_adapter_without_claim_promotion"
        ),
        "best_next_artifact": (
            "A registry-side adapter hook that exposes this string_tree_eft "
            "R4 shape packet for internal projection algebra while retaining "
            "the v2.133/v2.137 claim blockers."
        ),
        "interpretation": (
            "The engine can now build a source-provenance-clean string_tree_eft "
            "R4 projection packet under the v2.147 shape policy. It is useful "
            "for internal Bresciani-basis projection and positivity algebra, "
            "but it is still not an absolute string-scale prediction or a "
            "framework exclusion because the measurement likelihood and "
            "absolute normalization bridge remain absent."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.148/"
            "policy_scoped_string_tree_r4_projection_packet.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_policy_scoped_string_tree_r4_projection_packet()
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
