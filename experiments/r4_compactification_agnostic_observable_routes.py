"""Rank compactification-agnostic R4 observable and measurement routes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.157"


def compactification_agnostic_route_sources() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "bresciani_levati_paradisi_2025_partial_wave_unitarity",
            "url": "https://arxiv.org/abs/2504.12855",
            "route_family": "shape_unity_and_positivity_bounds",
            "provides_machine_route": True,
            "provides_public_likelihood": False,
            "uses_absolute_lambda_scale": False,
            "usable_axes": [
                "Bresciani_c_i_spin2_Riemann4",
                "g_R4_plus",
                "g_R4_minus_abs",
            ],
            "claim_limit": (
                "theoretical consistency diagnostic only unless paired with "
                "a measurement likelihood"
            ),
        },
        {
            "source_id": "greft_qnm_observability_discussion",
            "url": "https://link.springer.com/article/10.1140/epjp/s13360-024-05520-5",
            "route_family": "black_hole_qnm_or_gw_observable",
            "provides_machine_route": False,
            "provides_public_likelihood": False,
            "uses_absolute_lambda_scale": True,
            "usable_axes": [
                "GREFT_cubic_and_quartic_curvature_coefficients",
            ],
            "claim_limit": (
                "observability discussion is useful, but not a public "
                "Bresciani-axis likelihood packet"
            ),
        },
        {
            "source_id": "uv_graviton_scattering_positivity_bounds",
            "url": "https://link.aps.org/doi/10.1103/PhysRevD.106.105002",
            "route_family": "dispersion_positivity_bounds",
            "provides_machine_route": False,
            "provides_public_likelihood": False,
            "uses_absolute_lambda_scale": False,
            "usable_axes": [
                "gravitational_EFT_Wilson_coefficient_ratios",
            ],
            "claim_limit": (
                "theoretical positivity bound family, not a measurement "
                "likelihood over the engine R4 packet"
            ),
        },
        {
            "source_id": "generic_eft_gravitational_wave_dictionary_2025",
            "url": "https://link.aps.org/doi/10.1103/bl9q-1q3r",
            "route_family": "gw_waveform_dictionary",
            "provides_machine_route": False,
            "provides_public_likelihood": False,
            "uses_absolute_lambda_scale": True,
            "usable_axes": [
                "waveform_deviation_scaling_dictionary",
            ],
            "claim_limit": (
                "dictionary points toward observables but does not provide "
                "an R4 likelihood over Bresciani axes"
            ),
        },
    ]


def compactification_agnostic_route_requirements() -> list[str]:
    return [
        "does_not_require_numeric_alpha_prime_to_lambda_r4_ratio",
        "does_not_require_compactification_specific_planck_scale",
        "has_machine_usable_axis_mapping",
        "has_source_backed_theory_bound_or_public_likelihood",
        "keeps_framework_claim_disabled_without_likelihood",
    ]


def rank_compactification_agnostic_routes() -> dict[str, Any]:
    requirements = compactification_agnostic_route_requirements()
    rows: dict[str, dict[str, Any]] = {}
    for source in compactification_agnostic_route_sources():
        passed: dict[str, bool] = {
            "does_not_require_numeric_alpha_prime_to_lambda_r4_ratio": (
                source["uses_absolute_lambda_scale"] is False
            ),
            "does_not_require_compactification_specific_planck_scale": (
                source["uses_absolute_lambda_scale"] is False
            ),
            "has_machine_usable_axis_mapping": (
                source["provides_machine_route"] is True
            ),
            "has_source_backed_theory_bound_or_public_likelihood": (
                source["provides_machine_route"] is True
                or source["provides_public_likelihood"] is True
            ),
            "keeps_framework_claim_disabled_without_likelihood": (
                source["provides_public_likelihood"] is not True
            ),
        }
        score = sum(1 for value in passed.values() if value)
        missing = [
            requirement for requirement in requirements
            if passed[requirement] is not True
        ]
        rows[source["source_id"]] = {
            "source_id": source["source_id"],
            "route_family": source["route_family"],
            "score": score,
            "max_score": len(requirements),
            "criteria": passed,
            "missing_requirements": missing,
            "provides_public_likelihood": source["provides_public_likelihood"],
            "ready_for_internal_diagnostic": score >= 4,
            "ready_for_framework_claim": False,
            "claim_limit": source["claim_limit"],
        }

    ranked = sorted(
        rows,
        key=lambda source_id: (
            rows[source_id]["score"],
            rows[source_id]["provides_public_likelihood"],
        ),
        reverse=True,
    )
    return canonicalize_json_floats({
        "requirements": requirements,
        "route_scores": rows,
        "ranked_route_ids": ranked,
        "best_internal_diagnostic_route": ranked[0],
        "public_likelihood_ready_routes": [
            source_id for source_id, row in rows.items()
            if row["provides_public_likelihood"] is True
        ],
    })


def compactification_agnostic_observable_spec() -> dict[str, Any]:
    ranking = rank_compactification_agnostic_routes()
    route_id = ranking["best_internal_diagnostic_route"]
    return canonicalize_json_floats({
        "route_id": route_id,
        "status": "internal_theory_diagnostic_ready_nonclaiming",
        "source_url": "https://arxiv.org/abs/2504.12855",
        "observable_family": "Bresciani_spin2_R4_shape_unitarity",
        "input_axes": [
            "g_R4_c1",
            "g_R4_c2",
            "g_R4_c3",
            "g_R4_plus",
            "g_R4_minus_abs",
        ],
        "does_not_use_numeric_lambda_r4_scale": True,
        "does_not_use_compactification_policy": True,
        "claim_use_allowed": False,
        "measurement_likelihood_attached": False,
        "diagnostic_outputs": [
            "positivity_residual",
            "unitarity_shape_family",
            "shape_ratio_summary",
            "claim_blocker_ledger",
        ],
    })


def diagnose_r4_compactification_agnostic_observable_routes() -> dict[str, Any]:
    ranking = rank_compactification_agnostic_routes()
    spec = compactification_agnostic_observable_spec()
    public_likelihood_ready = ranking["public_likelihood_ready_routes"]
    internal_ready = [
        source_id for source_id, row in ranking["route_scores"].items()
        if row["ready_for_internal_diagnostic"]
    ]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.156_r4_frame_scale_policy_audit",
            "compactification_agnostic_route_search",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855",
        ],
        "source_routes": compactification_agnostic_route_sources(),
        "route_ranking": ranking,
        "internal_diagnostic_ready_routes": internal_ready,
        "public_likelihood_ready_routes": public_likelihood_ready,
        "selected_observable_spec": spec,
        "ready_for_internal_observable_diagnostic": bool(internal_ready),
        "ready_for_measurement_likelihood_claim": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "compactification_agnostic_r4_routes_ranked_no_public_likelihood"
        ),
        "selected_next_build_action": (
            "implement_bresciani_r4_shape_unitarity_diagnostic"
        ),
        "best_next_artifact": (
            "A non-claiming Bresciani R4 shape diagnostic adapter that consumes "
            "the registered string_tree_eft R4 query row, reports positivity "
            "and shape-unitarity diagnostics, and keeps the measurement "
            "likelihood and numeric Lambda_R4 blockers visible."
        ),
        "interpretation": (
            "A compactification-agnostic theory-diagnostic route exists via "
            "Bresciani spin-2 R4 shape bounds, but no public measurement "
            "likelihood over the engine R4 axes was found in this pass."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.157/"
            "r4_compactification_agnostic_observable_routes.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_compactification_agnostic_observable_routes()
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
