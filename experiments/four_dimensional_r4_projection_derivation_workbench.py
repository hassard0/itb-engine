"""Workbench for deriving a four-dimensional string R4 projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.symbolic_helicity_projection_fixture import (
    derived_bresciani_coordinates,
    invert_bresciani_coordinates,
    positivity_summary,
)


VERSION = "v2.139"


def bresciani_helicity_matching_contract() -> dict[str, Any]:
    return {
        "target_source": "https://arxiv.org/abs/2504.12855",
        "target_equation_refs": ["eq:amplitude", "eq:Lag-quartic"],
        "spin": 2,
        "target_channels": {
            "same_helicity_to_same_helicity": {
                "source_symbol": "c_plus",
                "amplitude_coefficient": "8*c_plus",
                "monomial_family": (
                    "<12>^4 [34]^4, <14>^4 [23]^4, or <34>^4 [12]^4"
                ),
            },
            "helicity_flip_complex_channel": {
                "source_symbol": "c_minus",
                "amplitude_coefficient": "8*c_minus",
                "monomial_family": (
                    "<12>^4<34>^4 + <13>^4<24>^4 + <14>^4<23>^4"
                ),
            },
            "conjugate_helicity_flip_channel": {
                "source_symbol": "conjugate(c_minus)",
                "amplitude_coefficient": "8*conjugate(c_minus)",
                "monomial_family": (
                    "[12]^4[34]^4 + [13]^4[24]^4 + [14]^4[23]^4"
                ),
            },
        },
        "coordinate_inversion": {
            "g_R4_c1": "(c_plus + Re(c_minus)) / 2",
            "g_R4_c2": "(c_plus - Re(c_minus)) / 2",
            "g_R4_c3": "Im(c_minus)",
        },
    }


def string_contact_matching_ansatz() -> dict[str, Any]:
    return {
        "source_family": "type_IIB_or_type_II_tree_R4_contact",
        "source_urls": [
            "https://arxiv.org/abs/hep-th/9707241",
            "https://arxiv.org/abs/hep-th/0010167",
            "https://doi.org/10.1016/0550-3213(86)90429-3",
        ],
        "source_equation_refs": {
            "russo_1997": ["venez", "logve", "aaa", "efff"],
            "peeters_vanhove_westerberg_2001": [
                "e:R4",
                "e:basicinvariants",
                "e:t8_definition",
            ],
        },
        "contact_term_shape": "A_R4 = overall_R4_factor * K_R4",
        "matching_equations": {
            "c_plus": "overall_R4_factor * K_plus / 8",
            "Re(c_minus)": "overall_R4_factor * Re(K_minus) / 8",
            "Im(c_minus)": "overall_R4_factor * Im(K_minus) / 8",
        },
        "required_source_components": [
            "overall_R4_factor_in_engine_lambda_r4_units",
            "K_plus_projection_on_same_helicity_channel",
            "K_minus_projection_on_helicity_flip_channel",
            "four_dimensional_frame_and_field_redefinition_policy",
        ],
    }


def derive_bresciani_from_source_projection(
    *,
    overall_r4_factor: float,
    k_plus: float,
    k_minus_real: float,
    k_minus_imag: float,
) -> dict[str, Any]:
    c_plus = overall_r4_factor * k_plus / 8.0
    c_minus_real = overall_r4_factor * k_minus_real / 8.0
    c_minus_imag = overall_r4_factor * k_minus_imag / 8.0
    helicity_input = {
        "c_plus": c_plus,
        "c_minus": {
            "real": c_minus_real,
            "imag": c_minus_imag,
        },
    }
    coefficients = invert_bresciani_coordinates(helicity_input)
    return canonicalize_json_floats({
        "helicity_coordinates": helicity_input,
        "inverted_coefficients": coefficients,
        "derived_coordinates": derived_bresciani_coordinates(coefficients),
        "positivity_summary": positivity_summary(coefficients),
    })


def synthetic_unit_projection_example() -> dict[str, Any]:
    return {
        "source_backed": False,
        "purpose": "algebraic workbench sanity check only",
        "input_components": {
            "overall_r4_factor": 8.0,
            "k_plus": 0.3,
            "k_minus_real": 0.1,
            "k_minus_imag": 0.05,
        },
        "derived": derive_bresciani_from_source_projection(
            overall_r4_factor=8.0,
            k_plus=0.3,
            k_minus_real=0.1,
            k_minus_imag=0.05,
        ),
    }


def source_component_status() -> list[dict[str, Any]]:
    return [
        {
            "component": "overall_R4_factor_in_engine_lambda_r4_units",
            "status": "missing",
            "blocker": "engine_lambda_r4_normalization_missing",
            "reason": (
                "The source R4 coefficient must be normalized into the "
                "engine's dimensionless Lambda_R4 convention."
            ),
        },
        {
            "component": "K_plus_projection_on_same_helicity_channel",
            "status": "missing",
            "blocker": "source_K_plus_projection_missing",
            "reason": (
                "The source kinematic factor K_R4 has not been decomposed "
                "onto Bresciani's same-helicity monomial family."
            ),
        },
        {
            "component": "K_minus_projection_on_helicity_flip_channel",
            "status": "missing",
            "blocker": "source_K_minus_projection_missing",
            "reason": (
                "The source kinematic factor K_R4 has not been decomposed "
                "onto the complex helicity-flip monomial family."
            ),
        },
        {
            "component": "four_dimensional_frame_and_field_redefinition_policy",
            "status": "missing",
            "blocker": "four_dimensional_frame_policy_missing",
            "reason": (
                "Ten-dimensional t8t8R4 and epsilon structures need an "
                "explicit four-dimensional truncation and field-redefinition "
                "policy before coefficient matching."
            ),
        },
    ]


def diagnose_four_dimensional_r4_projection_derivation_workbench() -> dict[str, Any]:
    statuses = source_component_status()
    blockers = sorted(row["blocker"] for row in statuses)
    example = synthetic_unit_projection_example()
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.138_string_r4_helicity_source_equation_audit",
            "v2.137_gravity_r4_source_provenance_guard",
            "Bresciani_eq_amplitude_matching_contract",
        ],
        "bresciani_helicity_matching_contract": (
            bresciani_helicity_matching_contract()
        ),
        "string_contact_matching_ansatz": string_contact_matching_ansatz(),
        "source_component_status": statuses,
        "source_projection_components_ready": False,
        "workbench_algebra_ready": True,
        "synthetic_unit_projection_example": example,
        "synthetic_example_guard_safe": (
            example["source_backed"] is False
            and example["derived"]["positivity_summary"]["passed"] is True
        ),
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "four_dimensional_r4_projection_workbench_ready_no_source_components",
        "selected_next_build_action": (
            "solve_source_k_factor_helicity_decomposition"
        ),
        "best_next_artifact": (
            "A source-backed K_R4 helicity decomposition that fills "
            "overall_R4_factor, K_plus, and complex K_minus in the v2.139 "
            "matching equations, then passes the v2.137 strict provenance "
            "guard."
        ),
        "interpretation": (
            "The downstream algebra is now executable: once source-backed "
            "K_plus and K_minus components are derived in a fixed "
            "four-dimensional frame, the workbench can produce Bresciani "
            "coordinates and positivity diagnostics. The current example is "
            "synthetic and only proves the matching machinery."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.139/"
            "four_dimensional_r4_projection_derivation_workbench.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_four_dimensional_r4_projection_derivation_workbench()
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
