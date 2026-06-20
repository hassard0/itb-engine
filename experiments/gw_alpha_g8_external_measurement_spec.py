"""External G8 sidecar measurement specification for the calibrated alpha packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_g8_joint_component_audit import (
    DEFAULT_ALPHA_PACKET_PATH,
    G8_REQUIRED_CAPABILITIES,
    load_json,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.127"
DEFAULT_G8_AUDIT_PATH = Path(
    "experiments/results/v2.126/gw_alpha_g8_joint_component_audit.json"
)


def g8_sidecar_required_fields() -> list[str]:
    return [
        "label",
        "source_url",
        "source_type",
        "observable_basis",
        "g8_axis_normalization",
        "g8_central_value_or_bound",
        "statistical_uncertainty",
        "systematic_uncertainty",
        "covariance_or_likelihood",
        "projection_to_engine_g8",
        "cross_covariance_with_alpha",
        "systematics_budget",
        "shared_eft_domain",
        "framework_projection",
        "discriminator_math",
        "synthetic_fixture",
    ]


def g8_sidecar_packet_template() -> dict[str, Any]:
    return {
        "label": "external_g8_sidecar_packet_template",
        "source_url": None,
        "source_type": "primary_literature_or_public_dataset",
        "observable_basis": "spin4_partial_wave_or_detector_high_moment",
        "g8_axis_normalization": "source_backed_engine_g8",
        "g8_central_value_or_bound": None,
        "statistical_uncertainty": None,
        "systematic_uncertainty": None,
        "covariance_or_likelihood": {
            "status": "public_engine_usable",
            "kind": "g8_sidecar_likelihood_or_covariance",
            "axes": ["g_8"],
        },
        "projection_to_engine_g8": {
            "status": "required",
            "requires": [
                "operator_identity",
                "normalization_convention",
                "jacobian_to_engine_g8",
                "mixing_control_for_lower_moments",
            ],
        },
        "cross_covariance_with_alpha": {
            "status": "required",
            "allowed_forms": [
                "public_joint_covariance_with_alpha",
                "source_backed_independence_proof_with_error_bound",
            ],
        },
        "systematics_budget": {
            "status": "required_bounded_or_closed",
            "components": [
                "g8_adapter",
                "cross_covariance",
                "eft_truncation",
                "calibration_or_acceptance",
                "background_model",
                "running_or_renormalization",
            ],
        },
        "shared_eft_domain": "bounded_for_qg_eft_and_alpha_packet",
        "framework_projection": {
            "status": "required",
            "requires": [
                "registered_framework_values_or_intervals",
                "pair_or_branch_exclusion_math",
            ],
        },
        "discriminator_math": "must_exclude_registered_framework_branch_beyond_uncertainty",
        "synthetic_fixture": False,
    }


def g8_sidecar_acceptance_checks() -> list[dict[str, str]]:
    return [
        {
            "check": "primary_source",
            "pass_condition": "source_url starts with https://arxiv.org/ or https://doi.org/",
            "blocker": "source_url_not_primary_allowed",
        },
        {
            "check": "external_numeric_measurement",
            "pass_condition": "central value or bound plus statistical/systematic uncertainty is public",
            "blocker": "external_numeric_measurement_missing",
        },
        {
            "check": "engine_g8_normalization",
            "pass_condition": "source-backed projection to engine g_8 with normalization and Jacobian",
            "blocker": "engine_g8_normalization_missing",
        },
        {
            "check": "public_likelihood",
            "pass_condition": "public covariance, likelihood samples, or reproducible likelihood evaluator",
            "blocker": "public_g8_likelihood_or_covariance_missing",
        },
        {
            "check": "cross_covariance_with_alpha",
            "pass_condition": "joint covariance with alpha or bounded independence proof",
            "blocker": "cross_covariance_with_alpha_missing",
        },
        {
            "check": "closed_systematics",
            "pass_condition": "all G8 systematics components bounded or closed",
            "blocker": "g8_systematics_not_closed",
        },
        {
            "check": "framework_exclusion",
            "pass_condition": "registered framework branch excluded beyond uncertainty",
            "blocker": "framework_pair_exclusion_math_missing",
        },
    ]


def diagnose_gw_alpha_g8_external_measurement_spec(
    g8_audit_path: Path = DEFAULT_G8_AUDIT_PATH,
    alpha_packet_path: Path = DEFAULT_ALPHA_PACKET_PATH,
) -> dict[str, Any]:
    audit = load_json(g8_audit_path)
    alpha_packet = load_json(alpha_packet_path)
    alpha_ready = audit["g8_joint_component_audit"]["alpha_status"][
        "ready_for_g8_join"
    ]
    return {
        "version": VERSION,
        "basis": [
            "v2.126_alpha_g8_joint_component_audit",
            "v2.125_alpha_joint_likelihood_calibration",
            "v2.54_g8_high_moment_measurement_specification",
        ],
        "paths": {
            "g8_audit": g8_audit_path.as_posix(),
            "alpha_packet": alpha_packet_path.as_posix(),
        },
        "alpha_packet_ready_for_sidecar": alpha_ready,
        "alpha_packet_label": alpha_packet["packet"]["label"],
        "required_g8_capabilities": list(G8_REQUIRED_CAPABILITIES),
        "required_sidecar_fields": g8_sidecar_required_fields(),
        "sidecar_packet_template": g8_sidecar_packet_template(),
        "acceptance_checks": g8_sidecar_acceptance_checks(),
        "current_sidecar_available": False,
        "claimable_discriminator_now": False,
        "route_status": "external_g8_sidecar_packet_specified_not_satisfied",
        "selected_next_build_action": "obtain_or_publish_external_g8_sidecar_packet",
        "best_next_artifact": (
            "A real public G8 sidecar packet satisfying this template, with "
            "engine-normalized g_8 likelihood/covariance and cross-covariance "
            "or independence proof relative to the calibrated alpha packet."
        ),
        "interpretation": (
            "The missing G8 component is now an executable packet contract. The "
            "current repo can validate such a packet and join it to alpha, but "
            "the packet itself must come from a real external measurement or "
            "publication."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--g8-audit", default=str(DEFAULT_G8_AUDIT_PATH))
    parser.add_argument("--alpha-packet", default=str(DEFAULT_ALPHA_PACKET_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.127/"
            "gw_alpha_g8_external_measurement_spec.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_g8_external_measurement_spec(
        g8_audit_path=Path(args.g8_audit),
        alpha_packet_path=Path(args.alpha_packet),
    )
    result = canonicalize_json_floats(result)
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
