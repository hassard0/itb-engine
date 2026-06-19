"""g_8 adapter acceptance harness (v2.79).

v2.78 left the g_8 route blocked on the absence of a source-backed measurement
packet. This harness defines the exact packet gate a future partial-wave,
detector-moment, or high-moment adapter must pass before the non-tower
promotion guard may even consider a framework discriminator claim.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


REQUIRED_G8_ADAPTER_FIELDS = (
    "axis",
    "route",
    "source_url",
    "source_type",
    "measurement_kind",
    "central_value_or_bound",
    "statistical_uncertainty",
    "systematic_uncertainty",
    "observable_basis",
    "wilson_coefficient_normalization",
    "cutoff_or_energy_domain",
    "jacobian_or_projection_to_g_8",
    "mixing_with_g_4_g_6",
    "covariance_or_likelihood",
    "systematics_budget",
    "framework_applicability_domain",
    "discriminator_math",
)

SUPPORTED_OBSERVABLE_BASES = {
    "spin_4_partial_wave",
    "asymptotic_detector_moment",
    "source_projected_high_moment",
}

VALID_G8_NORMALIZATIONS = {
    "engine_low_energy_g8",
    "source_backed_engine_g8",
}

MIXING_CONTROL_STATUSES = {
    "pure_g8_projection",
    "bounded_with_covariance",
    "marginalized_with_public_covariance",
}

LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
}

REQUIRED_SYSTEMATICS_COMPONENTS = (
    "angular_acceptance",
    "calibration",
    "background_model",
    "eft_truncation",
    "renormalization_or_running",
)

CLOSED_SYSTEMATICS_STATUSES = {"bounded", "closed"}
PROJECTION_TOLERANCE = 1e-12


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


def _positive_float(value: Any) -> bool:
    numeric = _float_or_none(value)
    return numeric is not None and numeric > 0.0


def _projection_summary(packet: dict[str, Any]) -> dict[str, Any]:
    projection = packet.get("jacobian_or_projection_to_g_8")
    if not isinstance(projection, dict):
        return {
            "projection_present": False,
            "g8_component": None,
            "lower_moment_l1": None,
            "pure_g8_projection": False,
            "lower_moment_mixing_controlled": False,
        }

    g8_component = _float_or_none(projection.get("g_8"))
    lower_moment_l1 = sum(
        abs(_float_or_none(projection.get(axis)) or 0.0)
        for axis in ("g_4", "g_6")
    )
    mixing_status = _status_value(packet.get("mixing_with_g_4_g_6"))
    pure_g8_projection = (
        g8_component is not None
        and abs(g8_component) > PROJECTION_TOLERANCE
        and lower_moment_l1 <= PROJECTION_TOLERANCE
    )
    lower_moment_mixing_controlled = (
        pure_g8_projection or mixing_status in MIXING_CONTROL_STATUSES
    )
    return {
        "projection_present": True,
        "g8_component": g8_component,
        "lower_moment_l1": float(lower_moment_l1),
        "pure_g8_projection": pure_g8_projection,
        "lower_moment_mixing_controlled": lower_moment_mixing_controlled,
        "mixing_status": mixing_status,
    }


def _systematics_summary(packet: dict[str, Any]) -> dict[str, Any]:
    budget = packet.get("systematics_budget")
    if not isinstance(budget, dict):
        status = _status_value(budget)
        return {
            "systematics_status": status,
            "missing_components": list(REQUIRED_SYSTEMATICS_COMPONENTS),
            "components_closed": False,
            "budget_closed": False,
        }

    status = _status_value(budget)
    components = budget.get("components")
    if not isinstance(components, dict):
        components = {}
    missing = [
        component for component in REQUIRED_SYSTEMATICS_COMPONENTS
        if component not in components
    ]
    components_closed = (
        not missing
        and all(
            _status_value(components[component]) in CLOSED_SYSTEMATICS_STATUSES
            for component in REQUIRED_SYSTEMATICS_COMPONENTS
        )
    )
    return {
        "systematics_status": status,
        "missing_components": missing,
        "components_closed": components_closed,
        "budget_closed": status in CLOSED_SYSTEMATICS_STATUSES and components_closed,
    }


def _likelihood_summary(packet: dict[str, Any]) -> dict[str, Any]:
    likelihood = packet.get("covariance_or_likelihood")
    if not isinstance(likelihood, dict):
        status = _status_value(likelihood)
        return {
            "likelihood_status": status,
            "engine_usable": status in LIKELIHOOD_STATUSES,
            "contains_g8": False,
        }

    axes = likelihood.get("axes") or likelihood.get("dimensions") or []
    contains_g8 = "g_8" in axes
    status = _status_value(likelihood)
    return {
        "likelihood_status": status,
        "engine_usable": status in LIKELIHOOD_STATUSES and contains_g8,
        "contains_g8": contains_g8,
        "kind": likelihood.get("kind"),
    }


def _axis_mapping_kind(packet: dict[str, Any], *, mapping_ready: bool) -> str:
    explicit = packet.get("axis_mapping_kind")
    if explicit:
        return str(explicit)
    return "validated_framework_adapter" if mapping_ready else "adapter_incomplete"


def evaluate_g8_adapter_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether a packet satisfies the g_8 adapter acceptance gate."""

    missing = [
        field for field in REQUIRED_G8_ADAPTER_FIELDS
        if packet.get(field) in (None, "")
    ]
    blockers: set[str] = set()
    if missing:
        blockers.add("missing_required_fields")
    if packet.get("axis") != "g_8":
        blockers.add("axis_not_g8")

    source_url = str(packet.get("source_url") or "")
    if source_url and not source_url.startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.add("source_url_not_primary_allowed")

    if packet.get("observable_basis") not in SUPPORTED_OBSERVABLE_BASES:
        blockers.add("observable_basis_not_adapter_supported")
    if packet.get("wilson_coefficient_normalization") not in VALID_G8_NORMALIZATIONS:
        blockers.add("wilson_coefficient_normalization_not_engine_g8")
    if _status_value(packet.get("cutoff_or_energy_domain")) != "bounded_for_qg_eft":
        blockers.add("eft_validity_not_bounded")

    central_value = _float_or_none(packet.get("central_value_or_bound"))
    stat_uncertainty_valid = _positive_float(packet.get("statistical_uncertainty"))
    syst_uncertainty_valid = _positive_float(packet.get("systematic_uncertainty"))
    if central_value is None or not stat_uncertainty_valid or not syst_uncertainty_valid:
        blockers.add("missing_external_numeric_measurement")

    projection = _projection_summary(packet)
    if not projection["projection_present"]:
        blockers.add("missing_jacobian_or_projection_to_g8")
    elif projection["g8_component"] is None or abs(projection["g8_component"]) <= PROJECTION_TOLERANCE:
        blockers.add("projection_missing_g8_component")
    if not projection["lower_moment_mixing_controlled"]:
        blockers.add("g8_not_isolated_from_lower_matter_moments")
    mapping_ready = (
        packet.get("axis") == "g_8"
        and packet.get("observable_basis") in SUPPORTED_OBSERVABLE_BASES
        and packet.get("wilson_coefficient_normalization") in VALID_G8_NORMALIZATIONS
        and _status_value(packet.get("cutoff_or_energy_domain")) == "bounded_for_qg_eft"
        and projection["projection_present"]
        and projection["g8_component"] is not None
        and abs(projection["g8_component"]) > PROJECTION_TOLERANCE
        and projection["lower_moment_mixing_controlled"]
    )

    likelihood = _likelihood_summary(packet)
    if not likelihood["engine_usable"]:
        blockers.add("missing_public_likelihood_or_covariance")

    systematics = _systematics_summary(packet)
    if not systematics["budget_closed"]:
        blockers.add("systematics_not_closed")

    if packet.get("framework_applicability_domain") != "registered_framework_low_energy_eft":
        blockers.add("framework_domain_not_validated")
    discriminator_claimable_by_math = (
        packet.get("discriminator_math") == "excludes_registered_framework"
    )
    if not discriminator_claimable_by_math:
        blockers.add("discriminator_math_not_excluding")

    axis_mapping_kind = _axis_mapping_kind(packet, mapping_ready=mapping_ready)
    uncertainty = None
    if stat_uncertainty_valid and syst_uncertainty_valid:
        uncertainty = math.hypot(
            float(packet["statistical_uncertainty"]),
            float(packet["systematic_uncertainty"]),
        )
    evidence = ExternalMeasurementEvidence(
        axis=str(packet.get("axis") or ""),
        route=str(packet.get("route") or ""),
        source_url=source_url,
        source_type=str(packet.get("source_type") or ""),
        measurement_kind=str(packet.get("measurement_kind") or ""),
        numerical_value=central_value,
        uncertainty=uncertainty,
        axis_mapping_kind=axis_mapping_kind,
        systematics_status=systematics["systematics_status"],
        metadata={
            "observable_basis": packet.get("observable_basis"),
            "wilson_coefficient_normalization": packet.get(
                "wilson_coefficient_normalization"
            ),
            "cutoff_or_energy_domain": packet.get("cutoff_or_energy_domain"),
            "projection_summary": projection,
            "likelihood_summary": likelihood,
            "systematics_summary": systematics,
            "synthetic_fixture": bool(packet.get("synthetic_fixture")),
        },
    )
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=discriminator_claimable_by_math,
    )
    blockers.update(guard["blockers"])

    adapter_acceptance_ready = not blockers
    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_source")

    return {
        "label": packet.get("label", packet.get("route", "unnamed_g8_packet")),
        "axis": packet.get("axis"),
        "route": packet.get("route"),
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing,
        "projection_summary": projection,
        "likelihood_summary": likelihood,
        "systematics_summary": systematics,
        "evidence": evidence.to_dict(),
        "promotion_guard": guard,
        "adapter_acceptance_ready": adapter_acceptance_ready,
        "ready_for_g8_claim": adapter_acceptance_ready and not synthetic_fixture,
        "acceptance_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "frontier_status": (
            "g8_adapter_packet_acceptance_ready"
            if adapter_acceptance_ready
            else "g8_adapter_packet_blocked"
        ),
    }


def synthetic_ready_adapter_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_spin4_partial_wave_adapter",
        "axis": "g_8",
        "route": "spin_4_partial_wave_or_detector_high_moment",
        "source_url": "https://doi.org/10.0000/synthetic-g8-adapter-fixture",
        "source_type": "validated_measurement",
        "measurement_kind": "external_numeric_measurement",
        "central_value_or_bound": 0.552,
        "statistical_uncertainty": 0.018,
        "systematic_uncertainty": 0.011,
        "observable_basis": "spin_4_partial_wave",
        "wilson_coefficient_normalization": "engine_low_energy_g8",
        "cutoff_or_energy_domain": "bounded_for_qg_eft",
        "jacobian_or_projection_to_g_8": {"g_4": 0.0, "g_6": 0.0, "g_8": 1.0},
        "mixing_with_g_4_g_6": "pure_g8_projection",
        "covariance_or_likelihood": {
            "status": "public_engine_usable",
            "kind": "gaussian_likelihood",
            "axes": ["g_8"],
        },
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "angular_acceptance": "bounded",
                "calibration": "bounded",
                "background_model": "bounded",
                "eft_truncation": "bounded",
                "renormalization_or_running": "bounded",
            },
        },
        "framework_applicability_domain": "registered_framework_low_energy_eft",
        "discriminator_math": "excludes_registered_framework",
        "synthetic_fixture": True,
    }


def current_cms_energy_correlator_packet() -> dict[str, Any]:
    return {
        "label": "current_cms_energy_correlator_design_seed",
        "axis": "g_8",
        "route": "cms_energy_correlator_measurements",
        "source_url": "https://arxiv.org/abs/2402.13864",
        "source_type": "primary_literature",
        "measurement_kind": "external_numeric_measurement",
        "central_value_or_bound": None,
        "statistical_uncertainty": None,
        "systematic_uncertainty": None,
        "observable_basis": "qcd_jet_energy_correlator",
        "wilson_coefficient_normalization": "qcd_alpha_s_not_engine_g8",
        "cutoff_or_energy_domain": "qcd_jet_substructure_not_qg_eft",
        "jacobian_or_projection_to_g_8": {},
        "mixing_with_g_4_g_6": "uncontrolled",
        "covariance_or_likelihood": "public_tables_not_engine_likelihood",
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "angular_acceptance": "bounded",
                "calibration": "bounded",
                "background_model": "bounded",
                "eft_truncation": "not_applicable_to_qg_eft",
                "renormalization_or_running": "bounded",
            },
        },
        "framework_applicability_domain": "standard_model_qcd_not_registered_qg_framework",
        "discriminator_math": "no_qg_framework_exclusion",
        "synthetic_fixture": False,
    }


def current_partial_wave_bridge_packet() -> dict[str, Any]:
    return {
        "label": "current_partial_wave_unitarity_theory_bridge",
        "axis": "g_8",
        "route": "partial_wave_unitarity_theory_bridge",
        "source_url": "https://arxiv.org/abs/2504.12855",
        "source_type": "primary_literature",
        "measurement_kind": "theory_formalism",
        "central_value_or_bound": None,
        "statistical_uncertainty": None,
        "systematic_uncertainty": None,
        "observable_basis": "spin_4_partial_wave",
        "wilson_coefficient_normalization": "not_engine_normalized",
        "cutoff_or_energy_domain": "formalism_only",
        "jacobian_or_projection_to_g_8": {"g_8": 1.0},
        "mixing_with_g_4_g_6": "adapter_design_only",
        "covariance_or_likelihood": "none_theory_only",
        "systematics_budget": "open",
        "framework_applicability_domain": "not_registered_framework_adapter",
        "discriminator_math": "no_qg_framework_exclusion",
        "synthetic_fixture": False,
    }


def diagnose_g8_adapter_acceptance_harness() -> dict[str, Any]:
    synthetic_fixture = evaluate_g8_adapter_packet(synthetic_ready_adapter_packet())
    current_packets = [
        evaluate_g8_adapter_packet(current_cms_energy_correlator_packet()),
        evaluate_g8_adapter_packet(current_partial_wave_bridge_packet()),
    ]
    real_claim_ready = [
        row["label"] for row in current_packets if row["ready_for_g8_claim"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in current_packets:
        for blocker in row["acceptance_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.79",
        "basis": [
            "v2.54_g8_measurement_contract",
            "v2.55_g8_existing_measurement_packet_search",
            "v2.78_current_source_recheck",
            "v2.52_nontower_promotion_guard",
        ],
        "axis": "g_8",
        "route": "spin_4_partial_wave_or_detector_high_moment_adapter",
        "required_adapter_fields": list(REQUIRED_G8_ADAPTER_FIELDS),
        "synthetic_fixture": synthetic_fixture,
        "current_packet_assessments": current_packets,
        "real_claim_ready_routes": real_claim_ready,
        "claimable_discriminator_now": bool(real_claim_ready),
        "current_packet_blocker_counts": dict(sorted(blocker_counts.items())),
        "route_status": "g8_adapter_acceptance_harness_ready_no_real_packet",
        "best_next_artifact": (
            "A real published partial-wave, detector-moment, or source-projected "
            "high-moment packet that fills this schema with a public likelihood "
            "and engine-normalized g_8 projection."
        ),
        "interpretation": (
            "The harness can accept a correctly shaped future adapter packet, "
            "but the synthetic fixture is not a source claim. Current CMS "
            "energy-correlator and partial-wave theory-bridge material still "
            "fails the gate because it lacks an engine-normalized g_8 projection, "
            "public engine-usable likelihood, bounded QG EFT domain, and "
            "framework-exclusion math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.79/g8_adapter_acceptance_harness.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_adapter_acceptance_harness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
