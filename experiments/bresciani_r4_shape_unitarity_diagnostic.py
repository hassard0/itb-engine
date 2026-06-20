"""Non-claiming Bresciani R4 shape-unitarity diagnostic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_symbolic_lambda_query_attachment import (
    query_r4_symbolic_lambda_surface,
)


VERSION = "v2.158"
DERIVED_TOLERANCE = 1e-9


def bresciani_shape_diagnostic_requirements() -> list[str]:
    return [
        "registered_r4_query_row",
        "numeric_shape_coefficients_available",
        "derived_shape_coordinates_available",
        "symbolic_lambda_sidecar_attached",
        "claim_blocker_ledger_preserved",
    ]


def compute_bresciani_shape_diagnostics(row: dict[str, Any]) -> dict[str, Any]:
    coefficients = row.get("coefficients", {})
    derived = row.get("derived", {})
    c1 = float(coefficients["g_R4_c1"])
    c2 = float(coefficients["g_R4_c2"])
    c3 = float(coefficients["g_R4_c3"])
    g_plus = float(derived["g_R4_plus"])
    g_minus_abs = float(derived["g_R4_minus_abs"])
    positivity_residual = float(4.0 * c1 * c2 - c3**2)
    minus_over_plus = (
        None if abs(g_plus) <= DERIVED_TOLERANCE
        else float(g_minus_abs / g_plus)
    )
    source_family = (
        "supersymmetric_same_helicity_R4_shape"
        if abs(g_minus_abs) <= DERIVED_TOLERANCE
        else "mixed_helicity_R4_shape"
    )

    return canonicalize_json_floats({
        "coefficients": {
            "g_R4_c1": c1,
            "g_R4_c2": c2,
            "g_R4_c3": c3,
        },
        "derived": {
            "g_R4_plus": g_plus,
            "g_R4_minus_abs": g_minus_abs,
        },
        "positivity": {
            "residual_4_c1_c2_minus_c3_squared": positivity_residual,
            "c1_nonnegative": c1 >= -DERIVED_TOLERANCE,
            "c2_nonnegative": c2 >= -DERIVED_TOLERANCE,
            "residual_nonnegative": positivity_residual >= -DERIVED_TOLERANCE,
            "passed": (
                c1 >= -DERIVED_TOLERANCE
                and c2 >= -DERIVED_TOLERANCE
                and positivity_residual >= -DERIVED_TOLERANCE
            ),
        },
        "shape_ratio_summary": {
            "g_R4_minus_abs_over_g_R4_plus": minus_over_plus,
            "g_R4_plus_positive": g_plus > DERIVED_TOLERANCE,
            "same_helicity_dominant": (
                minus_over_plus is not None
                and minus_over_plus <= DERIVED_TOLERANCE
            ),
            "source_family": source_family,
        },
        "unitarity_shape_family": {
            "source_url": "https://arxiv.org/abs/2504.12855",
            "status": "shape_diagnostic_only",
            "uses_absolute_lambda_scale": False,
            "measurement_likelihood_attached": False,
        },
    })


def evaluate_bresciani_r4_shape_unitarity_diagnostic(
    row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = row or query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )
    requirements = bresciani_shape_diagnostic_requirements()
    blockers: set[str] = set()
    if row.get("ready_for_internal_symbolic_query") is not True:
        blockers.add("registered_r4_query_row_not_ready")
    if not isinstance(row.get("coefficients"), dict) or not row["coefficients"]:
        blockers.add("numeric_shape_coefficients_missing")
    if not isinstance(row.get("derived"), dict) or not row["derived"]:
        blockers.add("derived_shape_coordinates_missing")
    if row.get("symbolic_lambda_r4_sidecar") is None:
        blockers.add("symbolic_lambda_sidecar_missing")
    if not row.get("claim_blockers"):
        blockers.add("claim_blocker_ledger_missing")

    diagnostics = None
    if not blockers:
        diagnostics = compute_bresciani_shape_diagnostics(row)
        if diagnostics["positivity"]["passed"] is not True:
            blockers.add("bresciani_shape_positivity_failed")

    return canonicalize_json_floats({
        "query_key": row.get("query_key"),
        "requirements": requirements,
        "diagnostics": diagnostics,
        "ready_for_internal_shape_unitarity_diagnostic": not blockers,
        "ready_for_measurement_likelihood_claim": False,
        "ready_for_numeric_wilson_export": False,
        "ready_for_framework_claim": False,
        "diagnostic_blockers": sorted(blockers),
        "claim_blockers": sorted(set(row.get("claim_blockers", []))),
        "interpretation": (
            "The registered string_tree_eft R4 row passes the Bresciani "
            "shape-level positivity diagnostic in the supersymmetric "
            "same-helicity family. This is a theory diagnostic, not a "
            "measurement likelihood or framework exclusion."
        ),
    })


def diagnose_bresciani_r4_shape_unitarity_diagnostic() -> dict[str, Any]:
    row = query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )
    evaluation = evaluate_bresciani_r4_shape_unitarity_diagnostic(row)

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.157_r4_compactification_agnostic_observable_routes",
            "v2.155_r4_symbolic_lambda_query_attachment",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855",
        ],
        "query_row": row,
        "evaluation": evaluation,
        "ready_for_internal_shape_unitarity_diagnostic": (
            evaluation["ready_for_internal_shape_unitarity_diagnostic"]
        ),
        "ready_for_measurement_likelihood_claim": False,
        "ready_for_numeric_wilson_export": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "route_status": "bresciani_r4_shape_unitarity_diagnostic_ready_nonclaiming",
        "selected_next_build_action": "search_public_r4_shape_likelihood_packet",
        "best_next_artifact": (
            "A public likelihood/covariance packet over R4-sensitive axes, "
            "or a proof that available GW/GREFT observables cannot yet be "
            "mapped to the Bresciani R4 query surface."
        ),
        "interpretation": (
            "The engine now has an executable compactification-agnostic R4 "
            "shape diagnostic. It adds useful theory information but still "
            "does not claim a framework exclusion because no public likelihood "
            "or numeric Lambda_R4 scale is attached."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.158/"
            "bresciani_r4_shape_unitarity_diagnostic.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_bresciani_r4_shape_unitarity_diagnostic()
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
