"""Source audit for a string R4 to Bresciani-basis translation (v2.134)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_projection_guard_schema import evaluate_r4_projection_packet
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.134"


def string_r4_source_candidates() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "bresciani_levati_paradisi_2026",
            "title": "Amplitudes and partial wave unitarity bounds",
            "url": "https://arxiv.org/abs/2504.12855",
            "source_role": "target_bresciani_spin2_basis",
            "establishes_string_r4_family": False,
            "establishes_bresciani_target_basis": True,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": True,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "Defines the target c_i^(2) Riemann^4 basis and source bounds, "
                "but does not translate string R4 tensors into that basis."
            ),
        },
        {
            "source_id": "gross_witten_1986",
            "title": "Superstring modifications of Einstein's equations",
            "url": "https://doi.org/10.1016/0550-3213(86)90429-3",
            "source_role": "type_ii_tree_level_r4_source",
            "establishes_string_r4_family": True,
            "establishes_bresciani_target_basis": False,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": False,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "A primary source for tree-level string corrections through "
                "quartic order in Riemann, but not an engine-normalized "
                "Bresciani c_i projection."
            ),
        },
        {
            "source_id": "gross_sloan_1987",
            "title": "The Quartic Effective Action for the Heterotic String",
            "url": "https://doi.org/10.1016/0550-3213(87)90465-2",
            "source_role": "heterotic_quartic_action_source",
            "establishes_string_r4_family": True,
            "establishes_bresciani_target_basis": False,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": False,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "A primary heterotic quartic-action source. It supports the "
                "string R4 route but does not provide c_i^(2) values or an "
                "operator projection matrix to the Bresciani basis."
            ),
        },
        {
            "source_id": "peeters_vanhove_westerberg_2001",
            "title": (
                "Supersymmetric higher-derivative actions in ten and eleven "
                "dimensions"
            ),
            "url": "https://arxiv.org/abs/hep-th/0010167",
            "source_role": "supersymmetric_r4_structure_source",
            "establishes_string_r4_family": True,
            "establishes_bresciani_target_basis": False,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": False,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "Documents t8t8R4 and related higher-derivative structures, "
                "including normalization and frame issues, but still not the "
                "required Bresciani three-axis adapter."
            ),
        },
        {
            "source_id": "russo_1997",
            "title": (
                "An ansatz for a non-perturbative four-graviton amplitude in "
                "type IIB superstring theory"
            ),
            "url": "https://arxiv.org/abs/hep-th/9707241",
            "source_role": "four_graviton_amplitude_expansion_source",
            "establishes_string_r4_family": True,
            "establishes_bresciani_target_basis": False,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": False,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "Gives a four-graviton amplitude expansion with an R4 term, "
                "but not a source-backed map into g_R4_c1/c2/c3."
            ),
        },
        {
            "source_id": "basu_2016_heterotic_one_loop",
            "title": "A simplifying feature of the heterotic one loop four graviton amplitude",
            "url": "https://inspirehep.net/literature/1473144",
            "source_role": "higher_loop_tensor_structure_context",
            "establishes_string_r4_family": True,
            "establishes_bresciani_target_basis": False,
            "gives_four_graviton_r4_action_or_amplitude": True,
            "gives_bresciani_c_i_spin2_values": False,
            "gives_string_to_bresciani_projection_matrix": False,
            "normalization_to_engine_lambda_r4": False,
            "four_dimensional_engine_frame_fixed": False,
            "uncertainty_or_covariance_ready": False,
            "interpretation": (
                "Useful tensor-structure context for string four-graviton "
                "amplitudes, but not a complete tree-level string_tree_eft "
                "projection into the Bresciani basis."
            ),
        },
    ]


def required_translation_steps() -> list[dict[str, Any]]:
    return [
        {
            "step": "choose_string_r4_source_family",
            "status": "partially_sourced",
            "blocker": None,
            "reason": "Primary sources establish string R4 action/amplitude families.",
        },
        {
            "step": "fix_four_dimensional_engine_frame",
            "status": "blocked",
            "blocker": "four_dimensional_compactification_frame_missing",
            "reason": (
                "The engine axes are four-dimensional; the scanned sources are "
                "primarily ten- or eleven-dimensional action/amplitude sources."
            ),
        },
        {
            "step": "derive_operator_projection_matrix",
            "status": "blocked",
            "blocker": "string_to_bresciani_operator_projection_matrix_missing",
            "reason": (
                "No scanned source directly maps t8t8R4/epsilon structures to "
                "the Bresciani c_1^(2), c_2^(2), c_3^(2) coordinates."
            ),
        },
        {
            "step": "fix_engine_normalization",
            "status": "blocked",
            "blocker": "engine_lambda_r4_normalization_missing",
            "reason": (
                "A guard-ready packet needs Lambda_R4 or an equivalent "
                "source-backed dimensionless normalization."
            ),
        },
        {
            "step": "propagate_uncertainty",
            "status": "blocked",
            "blocker": "r4_uncertainty_or_covariance_missing",
            "reason": (
                "No covariance, uncertainty envelope, or likelihood over "
                "g_R4_c1/c2/c3 is present."
            ),
        },
        {
            "step": "supply_claim_likelihood",
            "status": "blocked",
            "blocker": "measurement_likelihood_missing",
            "reason": (
                "A framework projection alone is not a measurement-backed "
                "framework exclusion."
            ),
        },
    ]


def _string_tree_guard_probe() -> dict[str, Any]:
    return evaluate_r4_projection_packet({
        "framework": "string_tree_eft",
        "axis_family": "gravity_R4_Riemann4",
        "source_url": "https://doi.org/10.1016/0550-3213(86)90429-3",
        "source_type": "primary_literature",
        "source_version": "Gross-Witten-1986",
        "adapter_kind": "framework_native_r4_projection",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "coefficients": {},
        "derived": {},
        "normalization": {},
        "operator_projection_matrix": {},
        "valid_energy_domain": {},
        "uncertainty_or_covariance": {},
        "ownership_metadata": {
            "framework_owned_derivation": (
                "string_tree_eft candidate source family, projection missing"
            ),
        },
        "unitarity_bound": {},
        "positivity_status": "not_checked",
        "discriminator_math": "projection_only",
    })


def diagnose_string_r4_basis_translation_source_audit() -> dict[str, Any]:
    sources = string_r4_source_candidates()
    direct_projection_sources = [
        row["source_id"] for row in sources
        if (
            row["gives_bresciani_c_i_spin2_values"]
            and row["gives_string_to_bresciani_projection_matrix"]
            and row["normalization_to_engine_lambda_r4"]
            and row["four_dimensional_engine_frame_fixed"]
            and row["uncertainty_or_covariance_ready"]
        )
    ]
    useful_string_sources = [
        row["source_id"] for row in sources
        if row["establishes_string_r4_family"]
    ]
    requirements = required_translation_steps()
    blockers = sorted({
        row["blocker"] for row in requirements
        if row["blocker"] is not None
    })
    guard_probe = _string_tree_guard_probe()
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.133_gravity_r4_projection_guard_schema",
            "string_tree_eft_highest_priority_translation_candidate",
            "current_primary_and_public_string_R4_sources",
        ],
        "source_count": len(sources),
        "useful_string_r4_sources": useful_string_sources,
        "direct_guard_ready_projection_sources": direct_projection_sources,
        "can_build_guard_passing_string_r4_adapter_now": bool(
            direct_projection_sources
        ),
        "sources": sources,
        "required_translation_steps": requirements,
        "translation_blockers": blockers,
        "string_tree_guard_probe": guard_probe,
        "claimable_framework_exclusions_now": [],
        "route_status": "string_r4_sources_found_no_bresciani_projection_adapter",
        "selected_next_build_action": (
            "build_symbolic_string_r4_to_bresciani_projection_plan"
        ),
        "best_next_artifact": (
            "A symbolic helicity/operator projection plan for the string R4 "
            "candidate, explicitly deciding whether t8t8R4 and epsilon "
            "structures can be reduced to c_1^(2), c_2^(2), c_3^(2) after a "
            "four-dimensional frame choice."
        ),
        "interpretation": (
            "The source search confirms that string theory is the right R4 "
            "family to pursue, but it does not yet provide a guard-ready "
            "adapter. The missing object is a source-backed projection matrix "
            "from string R4 tensor structures into the Bresciani spin-2 "
            "three-coordinate basis, with normalization and uncertainty."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.134/"
            "string_r4_basis_translation_source_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_string_r4_basis_translation_source_audit()
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
