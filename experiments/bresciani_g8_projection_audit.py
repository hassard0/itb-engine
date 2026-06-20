"""Audit whether Bresciani v2 partial-wave gravity bounds project to engine g8."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.130"
SOURCE_URL = "https://arxiv.org/abs/2504.12855"
SOURCE_VERSION = "arXiv:2504.12855v2"
SPIN = 2


def engine_g8_contract() -> dict[str, Any]:
    return {
        "axis": "g_8",
        "source_reference": "README.md matter row and dispersion_tower.py",
        "sector": "matter_forward_limit",
        "meaning": "forward-limit scattering positivity moment",
        "amplitude_power": "s^4",
        "formal_definition": (
            "g_8 is the engine coefficient for the next-next-order matter "
            "forward-amplitude moment, constrained with g_4 and g_6 by "
            "g_6^2 <= g_4 * g_8."
        ),
        "accepted_source_bases": [
            "matter_2_to_2_forward_limit_s4_coefficient",
            "spin4_or_detector_high_moment_with_source_backed_engine_g8_projection",
        ],
        "required_for_jacobian": [
            "same_sector_or_source_backed_cross_sector_identity",
            "dimensionless_engine_normalization",
            "operator_identity_into_g_8",
            "lower_moment_mixing_control",
            "public_likelihood_or_covariance_if_claiming",
        ],
    }


def bresciani_v2_gravity_basis() -> dict[str, Any]:
    spin_ratio = (2 * SPIN + 3) / (2 * SPIN + 1)
    return {
        "source_url": SOURCE_URL,
        "source_version": SOURCE_VERSION,
        "source_role": "partial_wave_unitarity_formalism",
        "sector": "four_graviton_eight_derivative_gravity",
        "spin_S": SPIN,
        "operator_basis": [
            "c_1^(S) * (Q^(S))^2",
            "c_2^(S) * (Qtilde^(S))^2",
            "c_3^(S) * Q^(S) * Qtilde^(S)",
        ],
        "gravity_identification": {
            "Q^(2)": "Mpl^2 * Riemann_{mu nu rho sigma} Riemann^{mu nu rho sigma}",
            "Qtilde^(2)": (
                "Mpl^2 * Riemann_{mu nu rho sigma} "
                "Riemann_dual^{mu nu rho sigma}"
            ),
            "coefficient_dimension": "-8 for S=2",
            "operator_dimension": "12 for S=2",
        },
        "linear_combinations": {
            "c_plus": "c_1^(S) + c_2^(S)",
            "c_minus": "c_1^(S) - c_2^(S) + i*c_3^(S)",
        },
        "source_unitarity_bound": {
            "generic": (
                "s^(2S)/(2*pi) * (abs(c_plus) + "
                "((2S+3)/(2S+1))*abs(c_minus)) <= 1"
            ),
            "spin2_ratio": spin_ratio,
            "spin2": (
                "s^4/(2*pi) * (abs(c_plus) + "
                "1.4*abs(c_minus)) <= 1"
            ),
        },
        "source_positivity_bounds": [
            "c_1^(S) >= 0",
            "c_2^(S) >= 0",
            "(c_3^(S))^2 <= 4*c_1^(S)*c_2^(S)",
        ],
        "evidence_loci": [
            "arXiv HTML lines 108-121: gravity/light-by-light EFT application and eight-derivative gravity",
            "TeX lines 214-233: three-coefficient Lagrangian and Q^(2), Qtilde^(2)",
            "TeX lines 253, 374, 381: c_plus/c_minus and unitarity bound",
            "TeX lines 404-410: positivity inequalities",
        ],
    }


def projection_requirements() -> list[dict[str, Any]]:
    return [
        {
            "check": "primary_versioned_source",
            "passed": True,
            "blocker": None,
            "reason": "Bresciani v2 is a current primary arXiv source.",
        },
        {
            "check": "derivative_order_matches_s4",
            "passed": True,
            "blocker": None,
            "reason": "For S=2 the source bound scales as s^4.",
        },
        {
            "check": "sector_matches_engine_g8",
            "passed": False,
            "blocker": "sector_mismatch_four_graviton_vs_matter_forward",
            "reason": (
                "The source basis is four-graviton Riemann^4-type gravity; "
                "engine g_8 is a matter forward-limit positivity moment."
            ),
        },
        {
            "check": "operator_identity_to_engine_g8",
            "passed": False,
            "blocker": "source_backed_operator_identity_missing",
            "reason": (
                "The source provides c_i^(2) gravity coefficients, not a cited "
                "identity mapping those coefficients into engine g_8."
            ),
        },
        {
            "check": "dimensionless_engine_normalization",
            "passed": False,
            "blocker": "dimensionful_gravity_coefficients_not_engine_normalized",
            "reason": (
                "For S=2 the source coefficients have mass dimension -8 and "
                "enter dimensionless bounds through s^4*c_i combinations."
            ),
        },
        {
            "check": "lower_moment_mixing_control",
            "passed": False,
            "blocker": "lower_moment_mixing_control_missing",
            "reason": (
                "No source-backed control is supplied for mixing into the "
                "engine matter moments g_4 and g_6."
            ),
        },
        {
            "check": "public_numeric_measurement_or_likelihood",
            "passed": False,
            "blocker": "public_g8_likelihood_or_measurement_missing",
            "reason": "The source is a theory bound/formalism, not a measured G8 packet.",
        },
        {
            "check": "claim_systematics_and_framework_math",
            "passed": False,
            "blocker": "claim_systematics_and_framework_math_missing",
            "reason": (
                "No component-level measurement systematics or registered "
                "framework-exclusion calculation is supplied."
            ),
        },
    ]


def projection_attempts() -> list[dict[str, Any]]:
    requirements = projection_requirements()
    blockers = sorted(
        row["blocker"] for row in requirements if row["blocker"] is not None
    )
    return [
        {
            "label": "naive_same_s4_derivative_order_map",
            "candidate_map": "g_8 = k1*c_1^(2) + k2*c_2^(2) + k3*c_3^(2)",
            "passes_derivative_order_check": True,
            "can_define_engine_g8_jacobian": False,
            "jacobian_to_engine_g8": None,
            "blockers": blockers,
            "interpretation": (
                "Matching s^4 power is necessary but not sufficient. The "
                "source axis is a gravity Riemann^4 basis, not the engine "
                "matter-forward g_8 axis."
            ),
        },
        {
            "label": "use_bresciani_as_gravity_r4_axis_extension",
            "candidate_map": "new gravity_R4_even_odd basis from c_1^(2), c_2^(2), c_3^(2)",
            "passes_derivative_order_check": True,
            "can_define_engine_g8_jacobian": False,
            "jacobian_to_engine_g8": None,
            "blockers": [
                "not_an_engine_g8_projection",
                "requires_new_engine_axis_contract",
                "requires_framework_projection_for_R4_basis",
            ],
            "interpretation": (
                "The source may be useful as a future gravity-sector R4/Riemann^4 "
                "axis extension, but that is a different route from G8 sidecar "
                "promotion."
            ),
        },
    ]


def diagnose_bresciani_g8_projection_audit() -> dict[str, Any]:
    requirements = projection_requirements()
    blockers = sorted(
        row["blocker"] for row in requirements if row["blocker"] is not None
    )
    passed_checks = [row["check"] for row in requirements if row["passed"]]
    failed_checks = [row["check"] for row in requirements if not row["passed"]]
    return {
        "version": VERSION,
        "basis": [
            "v2.129_gw_alpha_g8_sidecar_source_scout",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_v2",
            "engine_g8_contract_from_README_and_dispersion_tower",
        ],
        "source_url": SOURCE_URL,
        "engine_g8_contract": engine_g8_contract(),
        "bresciani_v2_gravity_basis": bresciani_v2_gravity_basis(),
        "projection_requirements": requirements,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "can_define_engine_g8_jacobian": False,
        "jacobian_to_engine_g8": None,
        "claimable_discriminator_now": False,
        "blockers": blockers,
        "projection_attempts": projection_attempts(),
        "route_status": "bresciani_v2_projection_audit_no_engine_g8_jacobian",
        "selected_next_build_action": (
            "register_bresciani_v2_as_gravity_r4_axis_extension_candidate"
        ),
        "best_next_artifact": (
            "A separate gravity Riemann^4/R4 axis-extension gate can preserve "
            "the useful Bresciani v2 formalism without mislabeling it as an "
            "engine g_8 sidecar packet."
        ),
        "interpretation": (
            "Bresciani v2 supplies a source-backed four-graviton s^4 "
            "partial-wave bound, but not a source-backed projection into the "
            "engine's matter-forward g_8 coordinate. The G8 sidecar remains "
            "missing; the source should be routed as a possible new gravity "
            "R4 axis instead."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.130/bresciani_g8_projection_audit.json",
    )
    args = parser.parse_args()

    result = canonicalize_json_floats(diagnose_bresciani_g8_projection_audit())
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
