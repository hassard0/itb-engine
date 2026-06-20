"""Acceptance gate for future joint g8 plus secondary-axis packets (v2.98)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_secondary_axis_targets import diagnose_g8_secondary_axis_targets


VERSION = "v2.98"
ROUTE = "g8_joint_secondary_axis_measurement_design"
REQUIRED_JOINT_PACKET_FIELDS = (
    "label",
    "route",
    "source_url",
    "source_type",
    "axes",
    "framework_pair",
    "central_values",
    "statistical_uncertainties",
    "systematic_uncertainties",
    "axis_normalizations",
    "axis_projections",
    "covariance_or_likelihood",
    "systematics_budget",
    "shared_eft_domain",
    "secondary_axis",
    "discriminator_math",
    "synthetic_fixture",
)
PRIMARY_SOURCE_PREFIXES = ("https://arxiv.org/", "https://doi.org/")
VALID_LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
}
VALID_SYSTEMATICS_STATUSES = {"bounded", "closed"}
REQUIRED_SYSTEMATICS_COMPONENTS = (
    "g8_adapter",
    "secondary_axis_adapter",
    "cross_covariance",
    "eft_truncation",
    "calibration",
    "background_model",
)
VALID_G8_NORMALIZATIONS = {
    "engine_low_energy_g8",
    "source_backed_engine_g8",
}
VALID_SECONDARY_AXIS_NORMALIZATIONS = {
    "source_backed_engine_secondary_axis",
    "engine_low_energy_g_R2",
    "source_backed_engine_g_C",
}


def _missing(value: Any) -> bool:
    return value in (None, "", [], {})


def _status_value(value: Any) -> str:
    if isinstance(value, dict):
        status = value.get("status")
        return str(status) if status is not None else ""
    return str(value) if value is not None else ""


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _axis_target(secondary_axis: str) -> dict[str, Any] | None:
    targets = diagnose_g8_secondary_axis_targets()
    for target in targets["recommended_joint_targets"]:
        axis_row = target["best_secondary_axis_by_tolerance"]
        if axis_row["axis"] == secondary_axis:
            return target
        frontier_axis = target["weyl_g8_frontier_secondary_axis"]
        if frontier_axis["axis"] == secondary_axis:
            return target
    return None


def _secondary_axis_threshold(
    target: dict[str, Any],
    secondary_axis: str,
) -> float | None:
    for key in ("best_secondary_axis_by_tolerance", "weyl_g8_frontier_secondary_axis"):
        axis_row = target[key]
        if axis_row["axis"] == secondary_axis:
            return axis_row["required_total_sigma_for_2sigma_distinguishability"]
    return None


def _axis_uncertainty(packet: dict[str, Any], axis: str) -> float | None:
    stat = _float_or_none((packet.get("statistical_uncertainties") or {}).get(axis))
    syst = _float_or_none((packet.get("systematic_uncertainties") or {}).get(axis))
    if stat is None or syst is None or stat < 0.0 or syst < 0.0:
        return None
    return math.hypot(stat, syst)


def _likelihood_summary(packet: dict[str, Any], axes: set[str]) -> dict[str, Any]:
    likelihood = packet.get("covariance_or_likelihood")
    if not isinstance(likelihood, dict):
        return {
            "status": _status_value(likelihood),
            "contains_required_axes": False,
            "engine_usable": False,
        }
    declared_axes = set(likelihood.get("axes") or likelihood.get("dimensions") or [])
    status = _status_value(likelihood)
    contains_required_axes = axes <= declared_axes
    return {
        "status": status,
        "contains_required_axes": contains_required_axes,
        "engine_usable": status in VALID_LIKELIHOOD_STATUSES
        and contains_required_axes,
        "kind": likelihood.get("kind"),
    }


def _systematics_summary(packet: dict[str, Any]) -> dict[str, Any]:
    budget = packet.get("systematics_budget")
    if not isinstance(budget, dict):
        return {
            "status": _status_value(budget),
            "missing_components": list(REQUIRED_SYSTEMATICS_COMPONENTS),
            "components_closed": False,
            "budget_closed": False,
        }
    status = _status_value(budget)
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
        and all(
            _status_value(components[component]) in VALID_SYSTEMATICS_STATUSES
            for component in REQUIRED_SYSTEMATICS_COMPONENTS
        )
    )
    return {
        "status": status,
        "missing_components": missing,
        "components_closed": components_closed,
        "budget_closed": status in VALID_SYSTEMATICS_STATUSES and components_closed,
    }


def evaluate_g8_joint_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_JOINT_PACKET_FIELDS if _missing(packet.get(field))
    ]
    blockers: set[str] = set()
    if missing_fields:
        blockers.add("missing_required_fields")
    if packet.get("route") != ROUTE:
        blockers.add("route_not_g8_joint_secondary_axis_design")

    source_url = str(packet.get("source_url") or "")
    if source_url and not source_url.startswith(PRIMARY_SOURCE_PREFIXES):
        blockers.add("source_url_not_primary_allowed")

    axes = set(packet.get("axes") or [])
    if "g_8" not in axes:
        blockers.add("axes_missing_g8")
    secondary_axis = str(packet.get("secondary_axis") or "")
    if not secondary_axis:
        blockers.add("secondary_axis_missing")
    elif secondary_axis not in axes:
        blockers.add("axes_missing_secondary_axis")

    target = _axis_target(secondary_axis) if secondary_axis else None
    if target is None:
        blockers.add("secondary_axis_not_registered_target")
        g8_threshold = None
        secondary_threshold = None
        expected_pair: set[str] = set()
    else:
        g8_threshold = target["g8_required_total_sigma"]
        secondary_threshold = _secondary_axis_threshold(target, secondary_axis)
        expected_pair = set(target["frameworks"])

    framework_pair = set(packet.get("framework_pair") or [])
    if expected_pair and framework_pair != expected_pair:
        blockers.add("framework_pair_not_targeted")

    central_values = packet.get("central_values")
    if not isinstance(central_values, dict):
        central_values = {}
    required_axes = {"g_8"}
    if secondary_axis:
        required_axes.add(secondary_axis)
    missing_numeric_axes = [
        axis for axis in sorted(required_axes) if _float_or_none(central_values.get(axis)) is None
    ]
    if missing_numeric_axes:
        blockers.add("missing_joint_numeric_measurement")

    g8_uncertainty = _axis_uncertainty(packet, "g_8")
    secondary_uncertainty = (
        _axis_uncertainty(packet, secondary_axis) if secondary_axis else None
    )
    if g8_threshold is None or g8_uncertainty is None:
        blockers.add("g8_uncertainty_missing_or_unusable")
    elif g8_uncertainty >= g8_threshold:
        blockers.add("g8_uncertainty_not_below_target")

    if secondary_threshold is None or secondary_uncertainty is None:
        blockers.add("secondary_axis_uncertainty_missing_or_unusable")
    elif secondary_uncertainty >= secondary_threshold:
        blockers.add("secondary_axis_uncertainty_not_below_target")

    normalizations = packet.get("axis_normalizations")
    if not isinstance(normalizations, dict):
        normalizations = {}
    if normalizations.get("g_8") not in VALID_G8_NORMALIZATIONS:
        blockers.add("g8_normalization_not_engine")
    if normalizations.get(secondary_axis) not in VALID_SECONDARY_AXIS_NORMALIZATIONS:
        blockers.add("secondary_axis_normalization_not_engine")

    projections = packet.get("axis_projections")
    if not isinstance(projections, dict):
        projections = {}
    if not bool(projections.get("g_8")):
        blockers.add("g8_projection_missing")
    if secondary_axis and not bool(projections.get(secondary_axis)):
        blockers.add("secondary_axis_projection_missing")
    if not bool(projections.get("cross_axis_mixing_controlled")):
        blockers.add("cross_axis_mixing_not_controlled")

    likelihood = _likelihood_summary(packet, required_axes)
    if not likelihood["engine_usable"]:
        blockers.add("missing_joint_likelihood_or_covariance")

    systematics = _systematics_summary(packet)
    if not systematics["budget_closed"]:
        blockers.add("systematics_not_closed")

    if packet.get("shared_eft_domain") != "bounded_for_qg_eft":
        blockers.add("shared_eft_domain_not_bounded")
    if packet.get("discriminator_math") != "excludes_nearest_eligible_pair_at_2sigma":
        blockers.add("discriminator_math_not_pair_excluding")

    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_source")

    acceptance_ready = not blockers
    return {
        "label": packet.get("label", "unnamed_g8_joint_packet"),
        "route": packet.get("route"),
        "synthetic_fixture": synthetic_fixture,
        "secondary_axis": secondary_axis,
        "framework_pair": sorted(framework_pair),
        "expected_framework_pair": sorted(expected_pair),
        "missing_fields": missing_fields,
        "missing_numeric_axes": missing_numeric_axes,
        "required_axes": sorted(required_axes),
        "g8_total_uncertainty": g8_uncertainty,
        "g8_required_total_sigma": g8_threshold,
        "secondary_axis_total_uncertainty": secondary_uncertainty,
        "secondary_axis_required_total_sigma": secondary_threshold,
        "likelihood_summary": likelihood,
        "systematics_summary": systematics,
        "acceptance_ready": acceptance_ready,
        "claim_ready": acceptance_ready and not synthetic_fixture,
        "acceptance_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "g8_joint_packet_claim_ready"
            if acceptance_ready and not synthetic_fixture
            else "g8_joint_packet_rejected_or_nonpromoting"
        ),
    }


def synthetic_ready_joint_g8_g_c_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_joint_g8_g_c_packet",
        "route": ROUTE,
        "source_url": "https://doi.org/10.0000/synthetic-joint-g8-gc",
        "source_type": "validated_measurement",
        "axes": ["g_8", "g_C"],
        "framework_pair": ["string_tree_eft", "discovered_data_driven"],
        "central_values": {"g_8": 0.402, "g_C": 0.30},
        "statistical_uncertainties": {"g_8": 0.001, "g_C": 0.03},
        "systematic_uncertainties": {"g_8": 0.0005, "g_C": 0.01},
        "axis_normalizations": {
            "g_8": "engine_low_energy_g8",
            "g_C": "source_backed_engine_g_C",
        },
        "axis_projections": {
            "g_8": True,
            "g_C": True,
            "cross_axis_mixing_controlled": True,
        },
        "covariance_or_likelihood": {
            "status": "public_engine_usable",
            "kind": "joint_gaussian_likelihood",
            "axes": ["g_8", "g_C"],
        },
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "g8_adapter": "bounded",
                "secondary_axis_adapter": "bounded",
                "cross_covariance": "bounded",
                "eft_truncation": "bounded",
                "calibration": "bounded",
                "background_model": "bounded",
            },
        },
        "shared_eft_domain": "bounded_for_qg_eft",
        "secondary_axis": "g_C",
        "discriminator_math": "excludes_nearest_eligible_pair_at_2sigma",
        "synthetic_fixture": True,
    }


def synthetic_ready_joint_g8_g_r2_packet() -> dict[str, Any]:
    packet = synthetic_ready_joint_g8_g_c_packet()
    packet.update(
        {
            "label": "synthetic_ready_joint_g8_g_r2_packet",
            "source_url": "https://doi.org/10.0000/synthetic-joint-g8-gr2",
            "axes": ["g_8", "g_R2"],
            "central_values": {"g_8": 0.402, "g_R2": 0.26},
            "statistical_uncertainties": {"g_8": 0.001, "g_R2": 0.035},
            "systematic_uncertainties": {"g_8": 0.0005, "g_R2": 0.015},
            "axis_normalizations": {
                "g_8": "engine_low_energy_g8",
                "g_R2": "engine_low_energy_g_R2",
            },
            "axis_projections": {
                "g_8": True,
                "g_R2": True,
                "cross_axis_mixing_controlled": True,
            },
            "covariance_or_likelihood": {
                "status": "public_engine_usable",
                "kind": "joint_gaussian_likelihood",
                "axes": ["g_8", "g_R2"],
            },
            "secondary_axis": "g_R2",
        }
    )
    return packet


def incomplete_joint_packet() -> dict[str, Any]:
    return {
        "label": "incomplete_joint_packet",
        "route": ROUTE,
        "source_url": "https://doi.org/10.0000/incomplete-joint",
        "source_type": "validated_measurement",
        "axes": ["g_8"],
        "secondary_axis": "g_C",
        "synthetic_fixture": False,
    }


def imprecise_joint_packet() -> dict[str, Any]:
    packet = synthetic_ready_joint_g8_g_c_packet()
    packet.update(
        {
            "label": "imprecise_joint_packet",
            "synthetic_fixture": False,
            "statistical_uncertainties": {"g_8": 0.003, "g_C": 0.07},
            "systematic_uncertainties": {"g_8": 0.001, "g_C": 0.02},
        }
    )
    return packet


def diagnose_g8_joint_packet_acceptance_gate() -> dict[str, Any]:
    sample_packets = [
        synthetic_ready_joint_g8_g_c_packet(),
        synthetic_ready_joint_g8_g_r2_packet(),
        incomplete_joint_packet(),
        imprecise_joint_packet(),
    ]
    evaluations = [evaluate_g8_joint_packet(packet) for packet in sample_packets]
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
            "v2.97_g8_secondary_axis_targets",
            "v2.96_g8_measurement_sensitivity_targets",
            "v2.93_external_evidence_intake_gate",
        ],
        "route": ROUTE,
        "required_joint_packet_fields": list(REQUIRED_JOINT_PACKET_FIELDS),
        "sample_packet_count": len(evaluations),
        "acceptance_ready_sample_packets": acceptance_ready,
        "claim_ready_sample_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "evaluations": evaluations,
        "route_status": "g8_joint_packet_gate_ready_no_real_packet",
        "best_next_artifact": (
            "Run this gate on a real joint g_8 plus secondary-axis packet. "
            "Synthetic fixtures and precision-incomplete packets remain "
            "non-promoting."
        ),
        "interpretation": (
            "The joint route now has an executable acceptance gate. It can accept "
            "correctly shaped future g_8+g_C or g_8+g_R2 packets, but no current "
            "sample is a real claim-ready source."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.98/g8_joint_packet_acceptance_gate.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_joint_packet_acceptance_gate()
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
