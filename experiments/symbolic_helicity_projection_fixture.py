"""Symbolic helicity projection fixture for the Bresciani R4 coordinates."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_projection_guard_schema import evaluate_r4_projection_packet
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.symbolic_string_r4_to_bresciani_projection_plan import (
    bresciani_coordinate_solver,
)


VERSION = "v2.136"


def fixture_source_helicity_input() -> dict[str, Any]:
    """A positive-control shape for source-level c_plus/c_minus data.

    This is not a string-theory derivation. It is a guard-compatible fixture for
    the algebraic contract that a future source-backed helicity calculation must
    satisfy.
    """
    return {
        "framework": "string_tree_eft",
        "source_family": "symbolic_fixture_not_string_derivation",
        "source_url": "https://arxiv.org/abs/2504.12855",
        "source_type": "computed_framework_projection",
        "source_version": "v2.136-symbolic-fixture",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "c_plus": 0.3,
        "c_minus": {
            "real": 0.1,
            "imag": 0.05,
        },
        "normalization": {
            "status": "engine_lambda_r4_defined",
            "lambda_r4": 1.0,
            "note": "symbolic unit-normalization fixture",
        },
        "operator_projection_matrix": {
            "status": "source_backed",
            "rows": ["c_plus", "Re(c_minus)", "Im(c_minus)"],
            "columns": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "matrix": [
                [1.0, 1.0, 0.0],
                [1.0, -1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            "note": "Bresciani coordinate inversion matrix, not a string tensor projection",
        },
        "valid_energy_domain": {
            "status": "bounded_for_qg_eft",
            "s_over_lambda_r4_max": 0.25,
        },
        "uncertainty_or_covariance": {
            "status": "bounded_systematic_envelope",
            "axes": ["g_R4_c1", "g_R4_c2", "g_R4_c3"],
            "relative_envelope": 0.0,
            "note": "zero-width symbolic fixture, not a measured covariance",
        },
        "ownership_metadata": {
            "framework_owned_derivation": "symbolic fixture for string_tree_eft adapter contract",
            "synthetic_fixture": True,
        },
        "unitarity_bound": {
            "status": "source_backed",
            "uses_bresciani_spin2_bound": True,
        },
        "discriminator_math": "projection_only",
    }


def invert_bresciani_coordinates(helicity_input: dict[str, Any]) -> dict[str, float]:
    c_plus = float(helicity_input["c_plus"])
    c_minus = helicity_input["c_minus"]
    if not isinstance(c_minus, dict):
        raise TypeError("c_minus must provide real and imag components")
    c_minus_real = float(c_minus["real"])
    c_minus_imag = float(c_minus["imag"])
    return {
        "g_R4_c1": (c_plus + c_minus_real) / 2.0,
        "g_R4_c2": (c_plus - c_minus_real) / 2.0,
        "g_R4_c3": c_minus_imag,
    }


def derived_bresciani_coordinates(coefficients: dict[str, float]) -> dict[str, float]:
    c1 = coefficients["g_R4_c1"]
    c2 = coefficients["g_R4_c2"]
    c3 = coefficients["g_R4_c3"]
    return {
        "g_R4_plus": c1 + c2,
        "g_R4_minus_abs": math.hypot(c1 - c2, c3),
    }


def positivity_summary(coefficients: dict[str, float]) -> dict[str, Any]:
    c1 = coefficients["g_R4_c1"]
    c2 = coefficients["g_R4_c2"]
    c3 = coefficients["g_R4_c3"]
    residual = 4.0 * c1 * c2 - c3**2
    return {
        "c1_nonnegative": c1 >= 0.0,
        "c2_nonnegative": c2 >= 0.0,
        "c3_square_bound_residual": residual,
        "passed": c1 >= 0.0 and c2 >= 0.0 and residual >= -1e-12,
    }


def build_projection_packet(helicity_input: dict[str, Any]) -> dict[str, Any]:
    coefficients = invert_bresciani_coordinates(helicity_input)
    derived = derived_bresciani_coordinates(coefficients)
    return {
        "framework": helicity_input["framework"],
        "axis_family": "gravity_R4_Riemann4",
        "source_url": helicity_input["source_url"],
        "source_type": helicity_input["source_type"],
        "source_version": helicity_input["source_version"],
        "adapter_kind": "framework_native_r4_projection",
        "basis": helicity_input["basis"],
        "coefficients": coefficients,
        "derived": derived,
        "normalization": helicity_input["normalization"],
        "operator_projection_matrix": helicity_input["operator_projection_matrix"],
        "valid_energy_domain": helicity_input["valid_energy_domain"],
        "uncertainty_or_covariance": helicity_input["uncertainty_or_covariance"],
        "ownership_metadata": helicity_input["ownership_metadata"],
        "unitarity_bound": helicity_input["unitarity_bound"],
        "positivity_status": "checked",
        "discriminator_math": helicity_input["discriminator_math"],
    }


def diagnose_symbolic_helicity_projection_fixture() -> dict[str, Any]:
    helicity_input = fixture_source_helicity_input()
    coefficients = invert_bresciani_coordinates(helicity_input)
    derived = derived_bresciani_coordinates(coefficients)
    packet = build_projection_packet(helicity_input)
    guard = evaluate_r4_projection_packet(packet)
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.135_symbolic_string_r4_to_bresciani_projection_plan",
            "v2.133_gravity_r4_projection_guard_schema",
            "Bresciani_c_plus_c_minus_coordinate_contract",
        ],
        "fixture_is_source_backed_string_derivation": False,
        "source_gap": (
            "Replace the fixture c_plus/c_minus values with a source-backed "
            "string R4 helicity/tensor evaluation in a fixed four-dimensional "
            "frame."
        ),
        "coordinate_solver": bresciani_coordinate_solver(),
        "helicity_input": helicity_input,
        "inverted_coefficients": coefficients,
        "derived_coordinates": derived,
        "positivity_summary": positivity_summary(coefficients),
        "projection_packet": packet,
        "guard_result": guard,
        "ready_for_framework_projection_fixture": (
            guard["ready_for_framework_projection"]
        ),
        "ready_for_framework_claim": guard["ready_for_framework_claim"],
        "claimable_framework_exclusions_now": [],
        "route_status": "symbolic_helicity_fixture_passes_projection_guard_nonclaiming",
        "selected_next_build_action": (
            "replace_fixture_with_source_backed_string_r4_helicity_evaluation"
        ),
        "best_next_artifact": (
            "A source-backed helicity/tensor evaluation that supplies c_plus "
            "and c_minus for the chosen string R4 source family, using the "
            "same v2.136 inversion and v2.133 guard."
        ),
        "interpretation": (
            "The algebraic and guard plumbing works: c_plus/c_minus can be "
            "inverted into g_R4_c1/c2/c3 and accepted as a projection packet. "
            "The result remains non-claiming because the helicity input is a "
            "fixture and no measurement likelihood or excluding discriminator "
            "math is present."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.136/"
            "symbolic_helicity_projection_fixture.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_symbolic_helicity_projection_fixture()
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
