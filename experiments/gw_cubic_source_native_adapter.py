"""Source-native cubic GW alpha adapter for v2.102."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_secondary_axis_adapter_blueprint import (
    liu_yunes_gw170608_paper_summary_adapter_candidate,
)


VERSION = "v2.102"
SOURCE_MODEL = "cubic_parity_preserving_higher_curvature_eft"
SOURCE_PARAMETERS = ("alpha_bar_1", "alpha_bar_2")
VALID_SOURCE_NATIVE_LIKELIHOOD_STATUSES = {
    "public_source_native_samples",
    "public_source_native_covariance",
    "reproduced_source_native_likelihood",
}
VALID_SYSTEMATICS_STATUSES = {"bounded", "closed"}
REQUIRED_SYSTEMATICS_COMPONENTS = (
    "waveform_systematics",
    "detector_calibration",
    "prior_sensitivity",
    "eft_truncation",
    "sampler_convergence",
    "public_data_reproducibility",
)
REQUIRED_SOURCE_NATIVE_PACKET_FIELDS = (
    "label",
    "source_url",
    "source_model",
    "event",
    "source_parameters",
    "parameter_constraints",
    "posterior_or_likelihood_export",
    "source_parameter_covariance",
    "waveform_model_reference",
    "normalization_convention",
    "engine_axis_strategy",
    "framework_projection_strategy",
    "systematics_budget",
    "shared_eft_domain",
    "validation_reference",
    "synthetic_fixture",
)


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
    if not isinstance(constraints, dict):
        return {
            "parameters_present": [],
            "parameters_missing": list(SOURCE_PARAMETERS),
            "all_source_parameters_numeric": False,
        }

    present = []
    missing = []
    numeric = True
    for parameter in SOURCE_PARAMETERS:
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
        "all_source_parameters_numeric": bool(
            not missing and numeric and present
        ),
    }


def _likelihood_summary(packet: dict[str, Any]) -> dict[str, Any]:
    likelihood = packet.get("posterior_or_likelihood_export")
    if not isinstance(likelihood, dict):
        return {
            "status": _status_value(likelihood),
            "contains_source_parameters": False,
            "source_native_usable": False,
            "kind": None,
        }
    axes = set(likelihood.get("parameters") or likelihood.get("axes") or [])
    status = _status_value(likelihood)
    contains_source_parameters = set(SOURCE_PARAMETERS) <= axes
    return {
        "status": status,
        "contains_source_parameters": contains_source_parameters,
        "source_native_usable": (
            status in VALID_SOURCE_NATIVE_LIKELIHOOD_STATUSES
            and contains_source_parameters
        ),
        "kind": likelihood.get("kind"),
    }


def _covariance_summary(packet: dict[str, Any]) -> dict[str, Any]:
    covariance = packet.get("source_parameter_covariance")
    if not isinstance(covariance, dict):
        return {
            "present": False,
            "parameters_covered": [],
            "parameters_missing": list(SOURCE_PARAMETERS),
            "numeric": False,
        }
    parameters = list(covariance.get("parameters") or [])
    matrix = covariance.get("matrix")
    numeric = (
        isinstance(matrix, list)
        and len(matrix) == len(SOURCE_PARAMETERS)
        and all(isinstance(row, list) for row in matrix)
        and all(len(row) == len(SOURCE_PARAMETERS) for row in matrix)
        and all(
            _float_or_none(value) is not None
            for row in matrix
            for value in row
        )
    )
    missing = [
        parameter
        for parameter in SOURCE_PARAMETERS
        if parameter not in parameters
    ]
    return {
        "present": True,
        "parameters_covered": [
            parameter for parameter in SOURCE_PARAMETERS if parameter in parameters
        ],
        "parameters_missing": missing,
        "numeric": bool(numeric and not missing),
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
            _status_value(components[component]) in VALID_SYSTEMATICS_STATUSES
            for component in REQUIRED_SYSTEMATICS_COMPONENTS
        )
    )
    status = _status_value(budget)
    return {
        "status": status,
        "missing_components": missing,
        "components_closed": components_closed,
        "budget_closed": status in VALID_SYSTEMATICS_STATUSES
        and components_closed,
    }


def _engine_projection_summary(packet: dict[str, Any]) -> dict[str, Any]:
    strategy = packet.get("engine_axis_strategy")
    projection = packet.get("framework_projection_strategy")
    if not isinstance(strategy, dict):
        return {
            "status": _status_value(strategy),
            "source_native_only": False,
            "engine_projection_ready": False,
            "target_axis": None,
        }
    status = _status_value(strategy)
    target_axis = strategy.get("target_axis")
    has_jacobian = bool(strategy.get("source_to_engine_jacobian"))
    source_native_only = status == "source_native_alpha_space_only"
    projection_ready = (
        status == "explicit_engine_projection"
        and target_axis in {"g_R3", "gw_cubic_alpha"}
        and has_jacobian
        and projection == "framework_alpha_response_defined"
    )
    return {
        "status": status,
        "source_native_only": source_native_only,
        "engine_projection_ready": projection_ready,
        "target_axis": target_axis,
    }


def evaluate_gw_cubic_source_native_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_SOURCE_NATIVE_PACKET_FIELDS
        if _missing(packet.get(field))
    ]
    blockers: set[str] = set()
    if missing_fields:
        blockers.add("missing_required_fields")

    if packet.get("source_model") != SOURCE_MODEL:
        blockers.add("source_model_not_cubic_parity_preserving_eft")
    if packet.get("event") != "GW170608":
        blockers.add("event_not_gw170608")

    declared_parameters = set(packet.get("source_parameters") or [])
    if set(SOURCE_PARAMETERS) - declared_parameters:
        blockers.add("source_parameters_missing_alpha_bar_basis")

    constraints = _constraints_summary(packet)
    if not constraints["all_source_parameters_numeric"]:
        blockers.add("source_parameter_constraints_incomplete")

    likelihood = _likelihood_summary(packet)
    if not likelihood["source_native_usable"]:
        blockers.add("source_native_likelihood_export_missing")

    covariance = _covariance_summary(packet)
    if not covariance["numeric"]:
        blockers.add("source_parameter_covariance_missing")

    systematics = _systematics_summary(packet)
    if not systematics["budget_closed"]:
        blockers.add("systematics_not_closed")

    if packet.get("shared_eft_domain") != "bounded_for_source_native_cubic_gw":
        blockers.add("shared_eft_domain_not_bounded")

    source_url = str(packet.get("source_url") or "")
    if not source_url.startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.add("source_url_not_primary_allowed")

    projection = _engine_projection_summary(packet)
    engine_projection_ready = projection["engine_projection_ready"]
    synthetic_fixture = bool(packet.get("synthetic_fixture"))
    native_adapter_ready = not blockers

    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_source")
    if not engine_projection_ready:
        claim_blockers.add("engine_projection_not_ready")
    claim_blockers.add("g8_joint_component_missing")
    claim_ready = not claim_blockers

    return {
        "label": packet.get("label", "unnamed_gw_cubic_source_native_packet"),
        "source_url": packet.get("source_url"),
        "event": packet.get("event"),
        "source_model": packet.get("source_model"),
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing_fields,
        "constraints_summary": constraints,
        "likelihood_summary": likelihood,
        "covariance_summary": covariance,
        "systematics_summary": systematics,
        "engine_projection_summary": projection,
        "native_adapter_ready": native_adapter_ready,
        "claim_ready": claim_ready,
        "adapter_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "gw_cubic_source_native_packet_claim_ready"
            if claim_ready
            else "gw_cubic_source_native_packet_rejected_or_nonpromoting"
        ),
    }


def synthetic_ready_gw_cubic_source_native_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_gw_cubic_source_native_packet",
        "source_url": "https://doi.org/10.0000/synthetic-cubic-gw-alpha",
        "source_model": SOURCE_MODEL,
        "event": "GW170608",
        "source_parameters": ["alpha_bar_1", "alpha_bar_2"],
        "parameter_constraints": {
            "alpha_bar_1": {"central": 0.87, "lower_90": -0.16, "upper_90": 2.82},
            "alpha_bar_2": {"central": -0.35, "lower_90": -3.27, "upper_90": 3.77},
        },
        "posterior_or_likelihood_export": {
            "status": "public_source_native_covariance",
            "kind": "source_native_gaussian_likelihood",
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
        },
        "source_parameter_covariance": {
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
            "matrix": [[0.21, 0.03], [0.03, 1.25]],
        },
        "waveform_model_reference": "source_native_imr_cubic_eft_waveform",
        "normalization_convention": "paper_native_dimensionless_alpha_bar",
        "engine_axis_strategy": {"status": "source_native_alpha_space_only"},
        "framework_projection_strategy": "not_attempted_source_native_only",
        "systematics_budget": {
            "status": "bounded",
            "components": {
                "waveform_systematics": "bounded",
                "detector_calibration": "bounded",
                "prior_sensitivity": "bounded",
                "eft_truncation": "bounded",
                "sampler_convergence": "bounded",
                "public_data_reproducibility": "bounded",
            },
        },
        "shared_eft_domain": "bounded_for_source_native_cubic_gw",
        "validation_reference": "v2.101_gw_alpha_engine_jacobian_audit",
        "synthetic_fixture": True,
    }


def liu_yunes_paper_summary_source_native_candidate() -> dict[str, Any]:
    candidate = liu_yunes_gw170608_paper_summary_adapter_candidate()
    return {
        "label": "liu_yunes_paper_summary_source_native_candidate",
        "source_url": candidate["source_url"],
        "source_model": SOURCE_MODEL,
        "event": "GW170608",
        "source_parameters": ["alpha_bar_1", "alpha_bar_2"],
        "parameter_constraints": candidate["parameter_constraints"],
        "posterior_or_likelihood_export": {
            "status": "paper_summary_constraints_only",
            "kind": "abstract_level_interval_summary",
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
        },
        "source_parameter_covariance": None,
        "waveform_model_reference": "paper_native_imr_cubic_eft_waveform",
        "normalization_convention": "paper_native_dimensionless_alpha_bar",
        "engine_axis_strategy": {"status": "source_native_alpha_space_only"},
        "framework_projection_strategy": "not_attempted_source_native_only",
        "systematics_budget": "published_analysis_not_adapter_budget",
        "shared_eft_domain": "gw170608_native_domain_not_bounded_for_adapter",
        "validation_reference": "https://arxiv.org/abs/2407.08929",
        "synthetic_fixture": False,
    }


def public_o2_bbh_gr_posterior_candidate() -> dict[str, Any]:
    return {
        "label": "public_o2_bbh_gr_posterior_candidate",
        "source_url": "https://doi.org/10.3847/1538-4357/aab1fc",
        "source_model": "general_relativity_binary_black_hole_pe",
        "event": "GW170608",
        "source_parameters": ["mass_1", "mass_2", "spin_1z", "spin_2z"],
        "parameter_constraints": {},
        "posterior_or_likelihood_export": {
            "status": "public_source_native_samples",
            "kind": "public_gr_posterior_samples",
            "parameters": ["mass_1", "mass_2", "spin_1z", "spin_2z"],
            "public_record": "https://github.com/gwastro/o2-bbh-pe",
        },
        "source_parameter_covariance": None,
        "waveform_model_reference": "pycbc_inference_gr_o2_release",
        "normalization_convention": "not_alpha_bar",
        "engine_axis_strategy": {"status": "not_modified_gravity_alpha_space"},
        "framework_projection_strategy": "not_applicable",
        "systematics_budget": "public_gr_reanalysis_not_alpha_adapter_budget",
        "shared_eft_domain": "gr_posterior_not_cubic_eft_domain",
        "validation_reference": "https://github.com/gwastro/o2-bbh-pe",
        "synthetic_fixture": False,
    }


def diagnose_gw_cubic_source_native_adapter() -> dict[str, Any]:
    packets = [
        synthetic_ready_gw_cubic_source_native_packet(),
        liu_yunes_paper_summary_source_native_candidate(),
        public_o2_bbh_gr_posterior_candidate(),
    ]
    evaluations = [
        evaluate_gw_cubic_source_native_packet(packet) for packet in packets
    ]
    native_ready = [
        row["label"] for row in evaluations if row["native_adapter_ready"]
    ]
    claim_ready = [row["label"] for row in evaluations if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in evaluations:
        for blocker in row["claim_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": VERSION,
        "basis": [
            "v2.101_gw_alpha_engine_jacobian_audit",
            "arXiv_2407.08929_cubic_gw_alpha_constraints",
            "gwastro_o2_bbh_pe_public_gr_posterior_record",
        ],
        "adapter_scope": "source_native_cubic_gw_alpha_bar_packet",
        "required_source_native_packet_fields": list(
            REQUIRED_SOURCE_NATIVE_PACKET_FIELDS
        ),
        "source_parameters": list(SOURCE_PARAMETERS),
        "sample_packet_count": len(evaluations),
        "native_adapter_ready_sample_packets": native_ready,
        "claim_ready_sample_packets": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "evaluations": evaluations,
        "route_status": (
            "source_native_cubic_gw_adapter_ready_no_real_likelihood_export"
        ),
        "selected_next_build_action": (
            "reproduce_gw170608_alpha_bar_likelihood_from_public_data"
        ),
        "best_next_artifact": (
            "A reproducible GW170608 alpha_bar likelihood or covariance export "
            "built from public strain/posterior inputs and the source-native "
            "cubic waveform model."
        ),
        "interpretation": (
            "The route now has a source-native alpha-space gate. The paper "
            "summary has real intervals but lacks public source-native samples "
            "or covariance, while public O2 BBH samples are GR parameters rather "
            "than alpha_bar evidence. The next build step is reproduction of the "
            "alpha_bar likelihood, not an existing-axis projection."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.102/"
            "gw_cubic_source_native_adapter.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_cubic_source_native_adapter()
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
