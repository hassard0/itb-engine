"""Public-GW secondary-axis adapter blueprint for v2.100."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


VERSION = "v2.100"
VALID_ENGINE_SECONDARY_AXES = {"g_C", "g_R2"}
REQUIRED_ADAPTER_FIELDS = (
    "label",
    "source_url",
    "source_model",
    "event",
    "source_parameters",
    "parameter_constraints",
    "operator_dictionary",
    "engine_axis_target",
    "source_to_engine_jacobian",
    "likelihood_export",
    "systematics_budget",
    "shared_eft_domain",
    "validation_reference",
    "synthetic_fixture",
)
REQUIRED_SYSTEMATICS_COMPONENTS = (
    "waveform_systematics",
    "detector_calibration",
    "prior_sensitivity",
    "eft_truncation",
    "numerical_relativity_calibration",
)
VALID_STATUSES = {"bounded", "closed"}
VALID_LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
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


def _constraints_summary(packet: dict[str, Any]) -> dict[str, Any]:
    constraints = packet.get("parameter_constraints")
    parameters = list(packet.get("source_parameters") or [])
    if not isinstance(constraints, dict):
        return {
            "parameters_present": [],
            "parameters_missing": parameters,
            "all_parameters_have_numeric_constraints": False,
        }

    present = []
    missing = []
    numeric = True
    for parameter in parameters:
        row = constraints.get(parameter)
        if not isinstance(row, dict):
            missing.append(parameter)
            numeric = False
            continue
        present.append(parameter)
        for key in ("central", "lower_90", "upper_90"):
            if _float_or_none(row.get(key)) is None:
                numeric = False
    return {
        "parameters_present": present,
        "parameters_missing": missing,
        "all_parameters_have_numeric_constraints": bool(
            not missing and numeric and parameters
        ),
    }


def _jacobian_summary(packet: dict[str, Any]) -> dict[str, Any]:
    jacobian = packet.get("source_to_engine_jacobian")
    target_axis = str(packet.get("engine_axis_target") or "")
    parameters = list(packet.get("source_parameters") or [])
    if not isinstance(jacobian, dict):
        return {
            "present": False,
            "target_axis_matches": False,
            "parameters_covered": [],
            "parameters_missing": parameters,
            "numeric": False,
        }
    covered = []
    missing = []
    numeric = True
    for parameter in parameters:
        value = _float_or_none(jacobian.get(parameter))
        if value is None:
            missing.append(parameter)
            numeric = False
        else:
            covered.append(parameter)
    return {
        "present": True,
        "target_axis_matches": jacobian.get("target_axis") == target_axis,
        "parameters_covered": covered,
        "parameters_missing": missing,
        "numeric": numeric,
        "normalization_source_url": jacobian.get("normalization_source_url"),
    }


def _likelihood_summary(packet: dict[str, Any]) -> dict[str, Any]:
    likelihood = packet.get("likelihood_export")
    target_axis = str(packet.get("engine_axis_target") or "")
    if not isinstance(likelihood, dict):
        return {
            "status": _status_value(likelihood),
            "contains_target_axis": False,
            "engine_usable": False,
        }
    axes = set(likelihood.get("axes") or [])
    status = _status_value(likelihood)
    return {
        "status": status,
        "contains_target_axis": target_axis in axes,
        "engine_usable": status in VALID_LIKELIHOOD_STATUSES and target_axis in axes,
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
            _status_value(components[component]) in VALID_STATUSES
            for component in REQUIRED_SYSTEMATICS_COMPONENTS
        )
    )
    status = _status_value(budget)
    return {
        "status": status,
        "missing_components": missing,
        "components_closed": components_closed,
        "budget_closed": status in VALID_STATUSES and components_closed,
    }


def evaluate_gw_secondary_axis_adapter(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_ADAPTER_FIELDS if _missing(packet.get(field))
    ]
    blockers: set[str] = set()
    if missing_fields:
        blockers.add("missing_required_fields")

    target_axis = str(packet.get("engine_axis_target") or "")
    if target_axis not in VALID_ENGINE_SECONDARY_AXES:
        blockers.add("engine_axis_target_not_supported")

    constraints = _constraints_summary(packet)
    if not constraints["all_parameters_have_numeric_constraints"]:
        blockers.add("source_parameter_constraints_incomplete")

    jacobian = _jacobian_summary(packet)
    if not jacobian["present"]:
        blockers.add("source_to_engine_jacobian_missing")
    elif not jacobian["target_axis_matches"]:
        blockers.add("source_to_engine_jacobian_axis_mismatch")
    elif not jacobian["numeric"] or jacobian["parameters_missing"]:
        blockers.add("source_to_engine_jacobian_incomplete")

    likelihood = _likelihood_summary(packet)
    if not likelihood["engine_usable"]:
        blockers.add("engine_axis_likelihood_export_missing")

    systematics = _systematics_summary(packet)
    if not systematics["budget_closed"]:
        blockers.add("systematics_not_closed")

    if packet.get("shared_eft_domain") != "bounded_for_qg_eft":
        blockers.add("shared_eft_domain_not_bounded")
    if not str(packet.get("source_url") or "").startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.add("source_url_not_primary_allowed")

    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_source")

    adapter_ready = not blockers
    return {
        "label": packet.get("label", "unnamed_gw_secondary_axis_adapter"),
        "source_url": packet.get("source_url"),
        "event": packet.get("event"),
        "engine_axis_target": target_axis,
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing_fields,
        "constraints_summary": constraints,
        "jacobian_summary": jacobian,
        "likelihood_summary": likelihood,
        "systematics_summary": systematics,
        "adapter_ready": adapter_ready,
        "claim_ready": adapter_ready and not synthetic_fixture,
        "adapter_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "gw_secondary_axis_adapter_claim_ready"
            if adapter_ready and not synthetic_fixture
            else "gw_secondary_axis_adapter_rejected_or_nonpromoting"
        ),
    }


def synthetic_ready_gw_secondary_axis_adapter() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_gw_secondary_axis_adapter",
        "source_url": "https://doi.org/10.0000/synthetic-gw-secondary-axis",
        "source_model": "cubic_parity_preserving_higher_curvature_eft",
        "event": "GW170608",
        "source_parameters": ["alpha_bar_1", "alpha_bar_2"],
        "parameter_constraints": {
            "alpha_bar_1": {"central": 0.87, "lower_90": -0.16, "upper_90": 2.82},
            "alpha_bar_2": {"central": -0.35, "lower_90": -3.27, "upper_90": 3.77},
        },
        "operator_dictionary": "source_backed_curvature_operator_dictionary",
        "engine_axis_target": "g_C",
        "source_to_engine_jacobian": {
            "target_axis": "g_C",
            "alpha_bar_1": 0.12,
            "alpha_bar_2": -0.03,
            "normalization_source_url": "https://doi.org/10.0000/synthetic-gc-normalization",
        },
        "likelihood_export": {
            "status": "public_engine_usable",
            "kind": "gaussianized_source_constraints",
            "axes": ["g_C"],
        },
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "waveform_systematics": "bounded",
                "detector_calibration": "bounded",
                "prior_sensitivity": "bounded",
                "eft_truncation": "bounded",
                "numerical_relativity_calibration": "bounded",
            },
        },
        "shared_eft_domain": "bounded_for_qg_eft",
        "validation_reference": "v2.99_gw_reanalysis_to_joint_secondary_packet",
        "synthetic_fixture": True,
    }


def liu_yunes_gw170608_paper_summary_adapter_candidate() -> dict[str, Any]:
    return {
        "label": "liu_yunes_gw170608_paper_summary_adapter_candidate",
        "source_url": "https://arxiv.org/abs/2407.08929",
        "source_model": "cubic_parity_preserving_higher_curvature_eft",
        "event": "GW170608",
        "source_parameters": ["alpha_bar_1", "alpha_bar_2"],
        "parameter_constraints": {
            "alpha_bar_1": {"central": 0.87, "lower_90": -0.16, "upper_90": 2.82},
            "alpha_bar_2": {"central": -0.35, "lower_90": -3.27, "upper_90": 3.77},
        },
        "operator_dictionary": "paper_native_cubic_higher_curvature_eft",
        "engine_axis_target": "g_C",
        "source_to_engine_jacobian": None,
        "likelihood_export": {
            "status": "paper_summary_constraints_only",
            "kind": "abstract_level_interval_summary",
            "axes": ["alpha_bar_1", "alpha_bar_2"],
        },
        "systematics_budget": "published_bayesian_analysis_not_engine_axis_budget",
        "shared_eft_domain": "gw170608_higher_curvature_eft_native_domain",
        "validation_reference": "https://arxiv.org/abs/2407.08929",
        "synthetic_fixture": False,
    }


def bernard_dictionary_only_adapter_candidate() -> dict[str, Any]:
    return {
        "label": "bernard_dictionary_only_adapter_candidate",
        "source_url": "https://arxiv.org/abs/2507.17143",
        "source_model": "generic_eft_motivated_beyond_gr_dictionary",
        "event": "not_event_specific",
        "source_parameters": [],
        "parameter_constraints": {},
        "operator_dictionary": "curvature_operator_scaling_dictionary",
        "engine_axis_target": "g_C",
        "source_to_engine_jacobian": None,
        "likelihood_export": None,
        "systematics_budget": None,
        "shared_eft_domain": "dictionary_only_no_event_domain",
        "validation_reference": "https://arxiv.org/abs/2507.17143",
        "synthetic_fixture": False,
    }


def diagnose_gw_secondary_axis_adapter_blueprint() -> dict[str, Any]:
    packets = [
        synthetic_ready_gw_secondary_axis_adapter(),
        liu_yunes_gw170608_paper_summary_adapter_candidate(),
        bernard_dictionary_only_adapter_candidate(),
    ]
    evaluations = [evaluate_gw_secondary_axis_adapter(packet) for packet in packets]
    adapter_ready = [row["label"] for row in evaluations if row["adapter_ready"]]
    claim_ready = [row["label"] for row in evaluations if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in evaluations:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": VERSION,
        "basis": [
            "v2.99_g8_joint_source_discovery_queue",
            "arXiv_2407.08929_gw170608_higher_curvature_constraints",
            "arXiv_2507.17143_eft_observation_dictionary",
        ],
        "adapter_scope": "public_gw_reanalysis_secondary_axis",
        "required_adapter_fields": list(REQUIRED_ADAPTER_FIELDS),
        "valid_engine_secondary_axes": sorted(VALID_ENGINE_SECONDARY_AXES),
        "sample_packet_count": len(evaluations),
        "adapter_ready_sample_packets": adapter_ready,
        "claim_ready_sample_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "evaluations": evaluations,
        "route_status": "gw_secondary_axis_adapter_blueprint_ready_no_real_jacobian",
        "selected_next_build_action": (
            "derive_source_to_engine_jacobian_for_alpha_bar_to_g_C_or_g_R2"
        ),
        "best_next_artifact": (
            "A source-backed Jacobian from alpha_bar_1/alpha_bar_2 to an engine "
            "secondary axis, plus an engine-usable likelihood export."
        ),
        "interpretation": (
            "The public-GW secondary-axis adapter is now executable. The Liu-Yunes "
            "GW170608 source supplies useful numeric alpha constraints, but it is "
            "not yet an engine-axis packet because the source-to-engine Jacobian "
            "and engine likelihood export are missing."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.100/"
            "gw_secondary_axis_adapter_blueprint.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_secondary_axis_adapter_blueprint()
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
