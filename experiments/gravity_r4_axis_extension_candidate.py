"""Register Bresciani v2 as a non-claiming gravity R4 axis candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_g8_projection_audit import (
    SOURCE_URL,
    SOURCE_VERSION,
    bresciani_v2_gravity_basis,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.131"


def candidate_axis_contract() -> dict[str, Any]:
    return {
        "candidate_family": "gravity_R4_Riemann4",
        "source_url": SOURCE_URL,
        "source_version": SOURCE_VERSION,
        "source_basis": "Bresciani c_i^(2) four-graviton eight-derivative basis",
        "proposed_engine_axes": [
            {
                "axis": "g_R4_c1",
                "source_coefficient": "c_1^(2)",
                "operator": "(Mpl^2 * Riemann^2)^2",
                "parity_role": "even",
            },
            {
                "axis": "g_R4_c2",
                "source_coefficient": "c_2^(2)",
                "operator": "(Mpl^2 * Riemann * Riemann_dual)^2",
                "parity_role": "even_from_dual_square",
            },
            {
                "axis": "g_R4_c3",
                "source_coefficient": "c_3^(2)",
                "operator": "(Mpl^2 * Riemann^2) * (Mpl^2 * Riemann * Riemann_dual)",
                "parity_role": "mixed_odd",
            },
        ],
        "derived_source_coordinates": [
            {
                "axis": "g_R4_plus",
                "source_expression": "c_1^(2) + c_2^(2)",
                "role": "unitarity_eigenvalue_center",
            },
            {
                "axis": "g_R4_minus_abs",
                "source_expression": "abs(c_1^(2) - c_2^(2) + i*c_3^(2))",
                "role": "unitarity_eigenvalue_radius",
            },
        ],
        "normalization_options": [
            {
                "name": "source_running_energy_normalization",
                "formula": "hat_c_i(s) = s^4 * c_i^(2)",
                "status": "source_bound_dimensionless_but_energy_dependent",
            },
            {
                "name": "engine_cutoff_normalization",
                "formula": "g_R4_ci = Lambda_R4^8 * c_i^(2)",
                "status": "requires_source_backed_cutoff_or_matching_scale",
            },
        ],
    }


def axis_extension_gates() -> list[dict[str, Any]]:
    return [
        {
            "check": "source_backed_operator_basis",
            "status": "passed",
            "blocker": None,
            "reason": "Bresciani v2 gives a three-coefficient S=2 Riemann^4 basis.",
        },
        {
            "check": "source_backed_unitarity_bound",
            "status": "passed",
            "blocker": None,
            "reason": "For S=2 the source gives an s^4 partial-wave unitarity bound.",
        },
        {
            "check": "source_backed_positivity_bounds",
            "status": "passed",
            "blocker": None,
            "reason": "The source gives c1,c2 >= 0 and c3^2 <= 4*c1*c2.",
        },
        {
            "check": "dimensionless_engine_normalization",
            "status": "blocked",
            "blocker": "r4_dimensionless_engine_normalization_missing",
            "reason": (
                "The source coefficients are dimensionful; an engine axis needs "
                "a source-backed cutoff or matching scale."
            ),
        },
        {
            "check": "framework_encoder_projection",
            "status": "blocked",
            "blocker": "registered_framework_r4_projection_missing",
            "reason": (
                "No registered framework currently exposes c_1^(2), c_2^(2), "
                "or c_3^(2) in this basis."
            ),
        },
        {
            "check": "observable_or_measurement_likelihood",
            "status": "blocked",
            "blocker": "r4_measurement_likelihood_missing",
            "reason": "The source supplies theory bounds, not measured R4 likelihoods.",
        },
        {
            "check": "engine_constraint_integration",
            "status": "blocked",
            "blocker": "r4_engine_constraint_integration_missing",
            "reason": (
                "The current engine basis has g_R2, g_C, and g_R3 gravity "
                "coordinates, but no R4/Riemann^4 coordinate contract."
            ),
        },
        {
            "check": "promotion_guard",
            "status": "blocked",
            "blocker": "r4_claim_guard_missing",
            "reason": (
                "Any future R4 axis must stay non-claiming until framework "
                "projections and measurements pass a promotion guard."
            ),
        },
    ]


def candidate_equations() -> dict[str, Any]:
    basis = bresciani_v2_gravity_basis()
    return {
        "source_unitarity_bound": basis["source_unitarity_bound"],
        "source_positivity_bounds": basis["source_positivity_bounds"],
        "engine_candidate_bound_templates": [
            {
                "name": "r4_source_unitarity_template",
                "formula": (
                    "abs(g_R4_plus) + 1.4*g_R4_minus_abs <= "
                    "2*pi / (s^4 * N_R4)"
                ),
                "status": "template_only_until_normalization_N_R4_is_defined",
            },
            {
                "name": "r4_source_positivity_template",
                "formula": "g_R4_c1 >= 0; g_R4_c2 >= 0; g_R4_c3^2 <= 4*g_R4_c1*g_R4_c2",
                "status": "source_backed_after_axis_normalization_is_defined",
            },
        ],
    }


def diagnose_gravity_r4_axis_extension_candidate() -> dict[str, Any]:
    gates = axis_extension_gates()
    blockers = sorted(
        row["blocker"] for row in gates if row["blocker"] is not None
    )
    passed = [row["check"] for row in gates if row["status"] == "passed"]
    blocked = [row["check"] for row in gates if row["status"] == "blocked"]
    return {
        "version": VERSION,
        "basis": [
            "v2.130_bresciani_g8_projection_audit",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_v2",
        ],
        "candidate_registered": True,
        "axis_contract_ready": False,
        "claimable_discriminator_now": False,
        "candidate_axis_contract": candidate_axis_contract(),
        "candidate_equations": candidate_equations(),
        "axis_extension_gates": gates,
        "passed_checks": passed,
        "blocked_checks": blocked,
        "promotion_blockers": blockers,
        "route_status": "gravity_r4_axis_candidate_registered_nonclaiming",
        "selected_next_build_action": "derive_framework_r4_projection_requirements",
        "best_next_artifact": (
            "A framework-projection requirement audit for the R4/Riemann^4 "
            "candidate axes, deciding what each registered framework would need "
            "to supply before this axis can enter discriminator math."
        ),
        "interpretation": (
            "The Bresciani v2 source is preserved as a concrete gravity-sector "
            "axis-extension candidate. It is not claim-ready and does not solve "
            "the G8 sidecar gap, but it gives a source-backed R4 operator basis "
            "and equations for a future engine extension."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.131/"
            "gravity_r4_axis_extension_candidate.json"
        ),
    )
    args = parser.parse_args()

    result = canonicalize_json_floats(
        diagnose_gravity_r4_axis_extension_candidate()
    )
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
