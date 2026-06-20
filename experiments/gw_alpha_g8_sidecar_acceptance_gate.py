"""Acceptance gate for external G8 sidecar packets joined to GW alpha."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_g8_external_measurement_spec import (
    DEFAULT_G8_AUDIT_PATH,
    g8_sidecar_required_fields,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.128"
PRIMARY_SOURCE_PREFIXES = ("https://arxiv.org/", "https://doi.org/")
VALID_SOURCE_TYPES = {
    "primary_literature_or_public_dataset",
    "primary_measurement",
    "public_data_product",
}
VALID_LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
}
VALID_SYSTEMATICS_STATUSES = {"bounded", "closed"}
VALID_CROSS_COVARIANCE_STATUSES = {
    "public_joint_covariance_with_alpha",
    "source_backed_independence_proof_with_error_bound",
}
REQUIRED_SYSTEMATICS_COMPONENTS = (
    "g8_adapter",
    "cross_covariance",
    "eft_truncation",
    "calibration_or_acceptance",
    "background_model",
    "running_or_renormalization",
)
MIN_FRAMEWORK_EXCLUSION_SIGMA = 2.0


def _missing(value: Any) -> bool:
    return value in (None, "", [], {})


def _status(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("status") or "")
    return str(value or "")


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        number = float(value)
        return number if math.isfinite(number) else None
    return None


def _missing_fields(packet: dict[str, Any]) -> list[str]:
    return [field for field in g8_sidecar_required_fields() if _missing(packet.get(field))]


def _likelihood_summary(packet: dict[str, Any]) -> dict[str, Any]:
    likelihood = packet.get("covariance_or_likelihood")
    if not isinstance(likelihood, dict):
        return {
            "status": _status(likelihood),
            "contains_g8": False,
            "public_engine_usable": False,
        }
    axes = set(likelihood.get("axes") or likelihood.get("dimensions") or [])
    status = _status(likelihood)
    return {
        "status": status,
        "contains_g8": "g_8" in axes,
        "public_engine_usable": status in VALID_LIKELIHOOD_STATUSES and "g_8" in axes,
        "kind": likelihood.get("kind"),
    }


def _cross_covariance_summary(packet: dict[str, Any]) -> dict[str, Any]:
    row = packet.get("cross_covariance_with_alpha")
    if not isinstance(row, dict):
        return {
            "status": _status(row),
            "acceptable": False,
            "has_numeric_bound": False,
        }
    status = _status(row)
    error_bound = _float_or_none(row.get("error_bound"))
    correlation_bound = _float_or_none(row.get("max_abs_correlation_with_alpha"))
    has_numeric_bound = error_bound is not None or correlation_bound is not None
    return {
        "status": status,
        "acceptable": status in VALID_CROSS_COVARIANCE_STATUSES and has_numeric_bound,
        "has_numeric_bound": has_numeric_bound,
        "error_bound": error_bound,
        "max_abs_correlation_with_alpha": correlation_bound,
    }


def _systematics_summary(packet: dict[str, Any]) -> dict[str, Any]:
    budget = packet.get("systematics_budget")
    if not isinstance(budget, dict):
        return {
            "status": _status(budget),
            "missing_components": list(REQUIRED_SYSTEMATICS_COMPONENTS),
            "components_closed": False,
            "budget_closed": False,
        }
    components = budget.get("components")
    if not isinstance(components, dict):
        components = {}
    missing = [
        component
        for component in REQUIRED_SYSTEMATICS_COMPONENTS
        if component not in components
    ]
    components_closed = (
        not missing
        and all(_status(components[component]) in VALID_SYSTEMATICS_STATUSES for component in REQUIRED_SYSTEMATICS_COMPONENTS)
    )
    status = _status(budget)
    return {
        "status": status,
        "missing_components": missing,
        "components_closed": components_closed,
        "budget_closed": status in VALID_SYSTEMATICS_STATUSES and components_closed,
    }


def _framework_projection_summary(packet: dict[str, Any]) -> dict[str, Any]:
    projection = packet.get("framework_projection")
    if not isinstance(projection, dict):
        return {
            "status": _status(projection),
            "excludes_framework": False,
            "confidence_sigma": None,
        }
    confidence = _float_or_none(projection.get("confidence_sigma"))
    excludes = bool(projection.get("excluded_framework_branch"))
    return {
        "status": _status(projection),
        "excludes_framework": excludes,
        "confidence_sigma": confidence,
        "framework_projection_ready": (
            _status(projection) == "source_backed_framework_projection"
            and excludes
            and confidence is not None
            and confidence >= MIN_FRAMEWORK_EXCLUSION_SIGMA
        ),
    }


def _discriminator_summary(packet: dict[str, Any]) -> dict[str, Any]:
    math_row = packet.get("discriminator_math")
    if not isinstance(math_row, dict):
        return {
            "status": _status(math_row),
            "confidence_sigma": None,
            "excluding": False,
        }
    confidence = _float_or_none(math_row.get("confidence_sigma"))
    return {
        "status": _status(math_row),
        "confidence_sigma": confidence,
        "excluding": (
            _status(math_row) == "excludes_registered_framework_branch"
            and confidence is not None
            and confidence >= MIN_FRAMEWORK_EXCLUSION_SIGMA
        ),
    }


def evaluate_g8_sidecar_packet(packet: dict[str, Any]) -> dict[str, Any]:
    blockers: set[str] = set()
    missing = _missing_fields(packet)
    if missing:
        blockers.add("missing_required_fields")

    source_url = str(packet.get("source_url") or "")
    if not source_url.startswith(PRIMARY_SOURCE_PREFIXES):
        blockers.add("source_url_not_primary_allowed")
    if packet.get("source_type") not in VALID_SOURCE_TYPES:
        blockers.add("source_type_not_allowed")

    if packet.get("observable_basis") != "spin4_partial_wave_or_detector_high_moment":
        blockers.add("observable_basis_not_g8_high_moment")
    if packet.get("g8_axis_normalization") != "source_backed_engine_g8":
        blockers.add("engine_g8_normalization_missing")
    if _float_or_none(packet.get("g8_central_value_or_bound")) is None:
        blockers.add("external_numeric_measurement_missing")
    for uncertainty_field in ("statistical_uncertainty", "systematic_uncertainty"):
        uncertainty = _float_or_none(packet.get(uncertainty_field))
        if uncertainty is None or uncertainty < 0.0:
            blockers.add(f"{uncertainty_field}_missing_or_invalid")

    likelihood = _likelihood_summary(packet)
    if not likelihood["public_engine_usable"]:
        blockers.add("public_g8_likelihood_or_covariance_missing")

    projection = packet.get("projection_to_engine_g8")
    if not isinstance(projection, dict) or _status(projection) != "source_backed_engine_g8_projection":
        blockers.add("projection_to_engine_g8_missing")
    elif not bool(projection.get("jacobian_to_engine_g8")):
        blockers.add("jacobian_to_engine_g8_missing")

    cross_covariance = _cross_covariance_summary(packet)
    if not cross_covariance["acceptable"]:
        blockers.add("cross_covariance_with_alpha_missing")

    systematics = _systematics_summary(packet)
    if not systematics["budget_closed"]:
        blockers.add("g8_systematics_not_closed")

    if packet.get("shared_eft_domain") != "bounded_for_qg_eft_and_alpha_packet":
        blockers.add("shared_eft_domain_not_bounded")

    framework_projection = _framework_projection_summary(packet)
    if not framework_projection.get("framework_projection_ready"):
        blockers.add("framework_projection_missing_or_nonexcluding")

    discriminator = _discriminator_summary(packet)
    if not discriminator["excluding"]:
        blockers.add("framework_pair_exclusion_math_missing")

    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_source")
    acceptance_ready = not blockers
    return {
        "label": packet.get("label", "unnamed_g8_sidecar_packet"),
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing,
        "likelihood_summary": likelihood,
        "cross_covariance_summary": cross_covariance,
        "systematics_summary": systematics,
        "framework_projection_summary": framework_projection,
        "discriminator_summary": discriminator,
        "acceptance_ready": acceptance_ready,
        "claim_ready": not claim_blockers,
        "acceptance_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "g8_sidecar_packet_claim_ready"
            if not claim_blockers
            else "g8_sidecar_packet_rejected_or_nonpromoting"
        ),
    }


def synthetic_ready_g8_sidecar_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_g8_sidecar_packet",
        "source_url": "https://doi.org/10.0000/synthetic-g8-sidecar",
        "source_type": "primary_measurement",
        "observable_basis": "spin4_partial_wave_or_detector_high_moment",
        "g8_axis_normalization": "source_backed_engine_g8",
        "g8_central_value_or_bound": 0.402,
        "statistical_uncertainty": 0.001,
        "systematic_uncertainty": 0.0005,
        "covariance_or_likelihood": {
            "status": "public_engine_usable",
            "kind": "g8_sidecar_gaussian_likelihood",
            "axes": ["g_8"],
        },
        "projection_to_engine_g8": {
            "status": "source_backed_engine_g8_projection",
            "operator_identity": "synthetic_spin4_detector_to_engine_g8",
            "normalization_convention": "engine_low_energy_g8",
            "jacobian_to_engine_g8": 1.0,
            "mixing_control_for_lower_moments": "bounded_by_spin4_projection",
        },
        "cross_covariance_with_alpha": {
            "status": "source_backed_independence_proof_with_error_bound",
            "error_bound": 0.01,
            "max_abs_correlation_with_alpha": 0.0,
        },
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "g8_adapter": "bounded",
                "cross_covariance": "bounded",
                "eft_truncation": "bounded",
                "calibration_or_acceptance": "bounded",
                "background_model": "bounded",
                "running_or_renormalization": "bounded",
            },
        },
        "shared_eft_domain": "bounded_for_qg_eft_and_alpha_packet",
        "framework_projection": {
            "status": "source_backed_framework_projection",
            "excluded_framework_branch": "synthetic_registered_branch",
            "confidence_sigma": 2.5,
        },
        "discriminator_math": {
            "status": "excludes_registered_framework_branch",
            "confidence_sigma": 2.5,
        },
        "synthetic_fixture": True,
    }


def incomplete_g8_sidecar_packet() -> dict[str, Any]:
    return {
        "label": "incomplete_g8_sidecar_packet",
        "source_url": "https://arxiv.org/abs/2504.12855",
        "source_type": "primary_literature_or_public_dataset",
        "observable_basis": "spin4_partial_wave_or_detector_high_moment",
        "synthetic_fixture": False,
    }


def diagnose_gw_alpha_g8_sidecar_acceptance_gate(
    spec_path: Path = DEFAULT_G8_AUDIT_PATH,
) -> dict[str, Any]:
    sample_packets = [
        synthetic_ready_g8_sidecar_packet(),
        incomplete_g8_sidecar_packet(),
    ]
    evaluations = [evaluate_g8_sidecar_packet(packet) for packet in sample_packets]
    acceptance_ready = [
        row["label"] for row in evaluations if row["acceptance_ready"]
    ]
    claim_ready = [row["label"] for row in evaluations if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in evaluations:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    return {
        "version": VERSION,
        "basis": [
            "v2.127_alpha_g8_external_measurement_spec",
            "v2.126_alpha_g8_joint_component_audit",
        ],
        "spec_path": spec_path.as_posix(),
        "required_sidecar_fields": g8_sidecar_required_fields(),
        "sample_packet_count": len(sample_packets),
        "acceptance_ready_sample_packets": acceptance_ready,
        "claim_ready_sample_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "evaluations": evaluations,
        "route_status": "g8_sidecar_acceptance_gate_ready_no_real_packet",
        "selected_next_build_action": "run_gate_on_real_external_g8_sidecar_packet",
        "best_next_artifact": (
            "A real non-synthetic external G8 sidecar packet that passes this "
            "gate and can be joined to the calibrated alpha packet."
        ),
        "interpretation": (
            "The sidecar contract is now executable. A correctly shaped packet "
            "can satisfy acceptance in a synthetic fixture, but the fixture stays "
            "nonclaiming and the incomplete current-source packet is rejected."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default=str(DEFAULT_G8_AUDIT_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.128/"
            "gw_alpha_g8_sidecar_acceptance_gate.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_g8_sidecar_acceptance_gate(
        spec_path=Path(args.spec),
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
