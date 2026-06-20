"""Source-equation audit for replacing the symbolic R4 helicity fixture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_source_provenance_guard import (
    evaluate_r4_source_provenance_packet,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.138"


def source_equation_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "bresciani_levati_paradisi_2026",
            "url": "https://arxiv.org/abs/2504.12855",
            "source_version": "arXiv:2504.12855v2",
            "role": "target_bresciani_spin2_coordinate_contract",
            "equation_refs": [
                "eq:Lag-quartic",
                "eq:amplitude",
                "eq:positivitybounds",
            ],
            "provides_bresciani_operator_basis": True,
            "provides_c_plus_c_minus_contract": True,
            "provides_spin2_positivity_guard": True,
            "provides_string_r4_family": False,
            "provides_string_helicity_amplitude_expansion": False,
            "provides_four_dimensional_string_to_bresciani_projection": False,
            "provides_engine_lambda_r4_normalization": False,
            "adapter_use": (
                "Defines the target c_i^(2) basis, helicity matrix, "
                "c_plus/c_minus coordinates, and positivity inequalities."
            ),
        },
        {
            "source_id": "peeters_vanhove_westerberg_2001",
            "url": "https://arxiv.org/abs/hep-th/0010167",
            "source_version": "arXiv:hep-th/0010167v4",
            "role": "string_tensor_structure_source",
            "equation_refs": [
                "e:R4",
                "e:basicinvariants",
                "e:t8_definition",
                "t8t8R4_reduction_to_Fulling_invariants",
            ],
            "provides_bresciani_operator_basis": False,
            "provides_c_plus_c_minus_contract": False,
            "provides_spin2_positivity_guard": False,
            "provides_string_r4_family": True,
            "provides_string_helicity_amplitude_expansion": False,
            "provides_four_dimensional_string_to_bresciani_projection": False,
            "provides_engine_lambda_r4_normalization": False,
            "adapter_use": (
                "Documents ten-dimensional t8t8R4, epsilon10-epsilon10 R4, "
                "and invariant reductions, but not the four-dimensional "
                "Bresciani three-axis projection."
            ),
        },
        {
            "source_id": "russo_1997_type_iib_four_graviton",
            "url": "https://arxiv.org/abs/hep-th/9707241",
            "source_version": "arXiv:hep-th/9707241v3",
            "role": "type_iib_four_graviton_amplitude_expansion_source",
            "equation_refs": [
                "venez",
                "logve",
                "aaa",
                "efff",
            ],
            "provides_bresciani_operator_basis": False,
            "provides_c_plus_c_minus_contract": False,
            "provides_spin2_positivity_guard": False,
            "provides_string_r4_family": True,
            "provides_string_helicity_amplitude_expansion": True,
            "provides_four_dimensional_string_to_bresciani_projection": False,
            "provides_engine_lambda_r4_normalization": False,
            "adapter_use": (
                "Gives a type IIB four-graviton amplitude expansion with a "
                "zeta(3) R4 term and higher-derivative R4 tower, but not "
                "Bresciani c_i^(2) values."
            ),
        },
        {
            "source_id": "gross_witten_1986",
            "url": "https://doi.org/10.1016/0550-3213(86)90429-3",
            "source_version": "Nucl.Phys.B277_1986",
            "role": "type_ii_tree_level_r4_primary_source",
            "equation_refs": [
                "tree_level_gravitational_scattering_amplitudes",
                "quartic_order_in_Riemann_effective_action",
            ],
            "provides_bresciani_operator_basis": False,
            "provides_c_plus_c_minus_contract": False,
            "provides_spin2_positivity_guard": False,
            "provides_string_r4_family": True,
            "provides_string_helicity_amplitude_expansion": True,
            "provides_four_dimensional_string_to_bresciani_projection": False,
            "provides_engine_lambda_r4_normalization": False,
            "adapter_use": (
                "Primary type-II string R4 provenance, but not an engine "
                "normalization or a Bresciani coordinate projection."
            ),
        },
    ]


def required_source_backed_helicity_steps() -> list[dict[str, Any]]:
    return [
        {
            "step": "target_coordinate_contract",
            "status": "sourced",
            "source_ids": ["bresciani_levati_paradisi_2026"],
            "blocker": None,
        },
        {
            "step": "string_r4_family_and_amplitude",
            "status": "sourced",
            "source_ids": [
                "gross_witten_1986",
                "peeters_vanhove_westerberg_2001",
                "russo_1997_type_iib_four_graviton",
            ],
            "blocker": None,
        },
        {
            "step": "four_dimensional_string_frame_choice",
            "status": "missing",
            "source_ids": [],
            "blocker": "four_dimensional_string_frame_choice_missing",
        },
        {
            "step": "string_tensor_to_bresciani_projection",
            "status": "missing",
            "source_ids": [],
            "blocker": "string_tensor_to_bresciani_projection_missing",
        },
        {
            "step": "source_backed_c_plus_c_minus_values",
            "status": "missing",
            "source_ids": [],
            "blocker": "source_backed_c_plus_c_minus_values_missing",
        },
        {
            "step": "alpha_prime_to_engine_lambda_r4_normalization",
            "status": "missing",
            "source_ids": [],
            "blocker": "engine_lambda_r4_normalization_missing",
        },
        {
            "step": "strict_source_provenance_packet",
            "status": "missing",
            "source_ids": [],
            "blocker": "strict_source_provenance_packet_missing",
        },
    ]


def partial_string_r4_packet_probe() -> dict[str, Any]:
    source_url = "https://arxiv.org/abs/hep-th/9707241"
    return {
        "framework": "string_tree_eft",
        "axis_family": "gravity_R4_Riemann4",
        "source_url": source_url,
        "source_type": "primary_literature",
        "source_version": "Russo_1997_type_IIB_R4_family_only",
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
                "string_tree_eft R4 source family located; Bresciani "
                "projection not derived"
            ),
        },
        "source_provenance": {
            "source_backed_derivation": False,
            "derivation_kind": "source_family_only",
            "primary_source_urls": [source_url],
            "synthetic_fixture": False,
        },
        "unitarity_bound": {},
        "positivity_status": "not_checked",
        "discriminator_math": "projection_only",
    }


def diagnose_string_r4_helicity_source_equation_audit() -> dict[str, Any]:
    rows = source_equation_rows()
    steps = required_source_backed_helicity_steps()
    blockers = sorted({
        step["blocker"] for step in steps
        if step["blocker"] is not None
    })
    target_sources = [
        row["source_id"] for row in rows
        if row["provides_c_plus_c_minus_contract"]
    ]
    string_family_sources = [
        row["source_id"] for row in rows
        if row["provides_string_r4_family"]
    ]
    direct_projection_sources = [
        row["source_id"] for row in rows
        if row["provides_four_dimensional_string_to_bresciani_projection"]
    ]
    c_plus_c_minus_sources = [
        row["source_id"] for row in rows
        if (
            row["provides_c_plus_c_minus_contract"]
            and row["provides_string_r4_family"]
            and row["provides_four_dimensional_string_to_bresciani_projection"]
        )
    ]
    strict_guard_probe = evaluate_r4_source_provenance_packet(
        partial_string_r4_packet_probe()
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.137_gravity_r4_source_provenance_guard",
            "v2.136_symbolic_helicity_projection_fixture",
            "source_tex_equation_audit_for_string_R4",
        ],
        "source_equation_rows": rows,
        "required_source_backed_helicity_steps": steps,
        "target_coordinate_sources": target_sources,
        "string_r4_family_sources": string_family_sources,
        "direct_string_to_bresciani_projection_sources": direct_projection_sources,
        "source_backed_c_plus_c_minus_sources": c_plus_c_minus_sources,
        "can_replace_fixture_with_source_backed_evaluation_now": bool(
            c_plus_c_minus_sources
        ),
        "strict_guard_probe": strict_guard_probe,
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "string_r4_helicity_sources_audited_projection_missing",
        "selected_next_build_action": (
            "build_four_dimensional_r4_projection_derivation_workbench"
        ),
        "best_next_artifact": (
            "A symbolic tensor/helicity workbench that takes the source "
            "t8t8R4 or four-graviton amplitude structures, fixes a "
            "four-dimensional frame, and derives Bresciani c_plus/c_minus "
            "with explicit provenance."
        ),
        "interpretation": (
            "The source equation audit now separates the target coordinate "
            "contract from the string R4 source family. The checked sources "
            "are sufficient to justify pursuing string_tree_eft, but they do "
            "not yet contain the four-dimensional string-to-Bresciani "
            "projection or source-backed c_plus/c_minus values needed to "
            "replace the v2.136 fixture."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.138/"
            "string_r4_helicity_source_equation_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_string_r4_helicity_source_equation_audit()
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
