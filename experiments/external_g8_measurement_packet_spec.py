"""External G8 measurement packet specification for alpha joins (v2.166)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_adapter_acceptance_harness import (
    REQUIRED_G8_ADAPTER_FIELDS,
    evaluate_g8_adapter_packet,
    synthetic_ready_adapter_packet,
)
from experiments.g8_joint_packet_acceptance_gate import REQUIRED_JOINT_PACKET_FIELDS
from experiments.g8_joint_source_discovery_queue import current_joint_source_candidates
from experiments.gw_alpha_g8_joint_component_audit import (
    G8_REQUIRED_CAPABILITIES,
    diagnose_gw_alpha_g8_joint_component_audit,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.166"

REQUIRED_ALPHA_JOIN_EXTENSION_FIELDS = (
    "join_target",
    "join_axes",
    "alpha_packet_reference",
    "joint_covariance_export",
    "cross_covariance_with_alpha",
    "shared_likelihood_domain",
    "source_reanalysis_package",
    "claim_controls",
)

REQUIRED_SOURCE_REANALYSIS_FIELDS = (
    "public_data_or_samples",
    "analysis_code_or_likelihood_sampler",
    "waveform_or_observable_model",
    "nuisance_parameter_policy",
    "reproducibility_instructions",
)

REQUIRED_CLAIM_CONTROLS = (
    "claim_use_allowed",
    "framework_claim_allowed",
    "external_adversarial_review_complete",
)


def external_g8_measurement_packet_contract() -> dict[str, Any]:
    return {
        "version": VERSION,
        "route": "external_spin4_or_detector_g8_measurement_packet_spec",
        "base_g8_adapter_fields": list(REQUIRED_G8_ADAPTER_FIELDS),
        "alpha_join_extension_fields": list(REQUIRED_ALPHA_JOIN_EXTENSION_FIELDS),
        "source_reanalysis_required_fields": list(REQUIRED_SOURCE_REANALYSIS_FIELDS),
        "claim_control_fields": list(REQUIRED_CLAIM_CONTROLS),
        "target_joint_gate_fields": list(REQUIRED_JOINT_PACKET_FIELDS),
        "required_capabilities_for_alpha_join": list(G8_REQUIRED_CAPABILITIES),
        "source_url_policy": "https://arxiv.org/ or https://doi.org/",
        "claim_rule": (
            "A packet may become engine-join-ready only after the base g_8 "
            "adapter gate and alpha-join extension pass. Framework claims "
            "remain disabled unless external adversarial review is complete."
        ),
    }


def synthetic_alpha_join_g8_packet() -> dict[str, Any]:
    packet = synthetic_ready_adapter_packet()
    packet["label"] = "synthetic_alpha_join_ready_g8_packet"
    packet["join_target"] = "v2.125_calibrated_gw_alpha_packet"
    packet["join_axes"] = ["g_8", "alpha_bar_1", "alpha_bar_2"]
    packet["alpha_packet_reference"] = (
        "experiments/results/v2.125/gw_alpha_joint_likelihood_calibration.json"
    )
    packet["joint_covariance_export"] = {
        "status": "public_covariance_matrix",
        "axes": ["g_8", "alpha_bar_1", "alpha_bar_2"],
        "kind": "joint_gaussian_likelihood",
    }
    packet["cross_covariance_with_alpha"] = {
        "status": "bounded",
        "g8_alpha_cross_terms_declared": True,
    }
    packet["shared_likelihood_domain"] = "bounded_for_qg_eft"
    packet["source_reanalysis_package"] = {
        "public_data_or_samples": True,
        "analysis_code_or_likelihood_sampler": True,
        "waveform_or_observable_model": "synthetic_spin4_detector_model",
        "nuisance_parameter_policy": "shared_or_marginalized_with_alpha_packet",
        "reproducibility_instructions": True,
    }
    packet["claim_controls"] = {
        "claim_use_allowed": False,
        "framework_claim_allowed": False,
        "external_adversarial_review_complete": False,
        "synthetic_control_not_claim_evidence": True,
    }
    return packet


def current_missing_external_g8_packet_slot() -> dict[str, Any]:
    return {
        "label": "current_missing_external_g8_measurement_packet_slot",
        "axis": "g_8",
        "route": "spin_4_partial_wave_or_detector_high_moment",
        "source_url": "",
        "source_type": "",
        "measurement_kind": "",
        "synthetic_fixture": False,
    }


def _field_missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def _evaluate_join_extension(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_ALPHA_JOIN_EXTENSION_FIELDS
        if _field_missing(packet.get(field))
    ]
    blockers: set[str] = set(missing_fields)

    join_axes = set(packet.get("join_axes") or [])
    if "g_8" not in join_axes:
        blockers.add("join_axes_missing_g8")
    if not {"alpha_bar_1", "alpha_bar_2"} <= join_axes:
        blockers.add("join_axes_missing_alpha_parameters")
    if packet.get("join_target") != "v2.125_calibrated_gw_alpha_packet":
        blockers.add("join_target_not_calibrated_alpha_packet")

    covariance = packet.get("joint_covariance_export")
    if not isinstance(covariance, dict):
        blockers.add("joint_covariance_export_missing")
    else:
        if covariance.get("status") not in {
            "public_covariance_matrix",
            "public_likelihood_samples",
            "public_engine_usable",
        }:
            blockers.add("joint_covariance_export_not_public_engine_usable")
        if not join_axes <= set(covariance.get("axes") or []):
            blockers.add("joint_covariance_axes_incomplete")

    cross_covariance = packet.get("cross_covariance_with_alpha")
    if not isinstance(cross_covariance, dict):
        blockers.add("cross_covariance_with_alpha_missing")
    else:
        if cross_covariance.get("status") not in {"bounded", "closed"}:
            blockers.add("cross_covariance_with_alpha_not_bounded")
        if cross_covariance.get("g8_alpha_cross_terms_declared") is not True:
            blockers.add("g8_alpha_cross_terms_not_declared")

    if packet.get("shared_likelihood_domain") != "bounded_for_qg_eft":
        blockers.add("shared_likelihood_domain_not_bounded")

    reanalysis = packet.get("source_reanalysis_package")
    if not isinstance(reanalysis, dict):
        blockers.add("source_reanalysis_package_missing")
        missing_reanalysis = list(REQUIRED_SOURCE_REANALYSIS_FIELDS)
    else:
        missing_reanalysis = [
            field for field in REQUIRED_SOURCE_REANALYSIS_FIELDS
            if _field_missing(reanalysis.get(field))
        ]
        blockers.update(f"source_reanalysis.{field}" for field in missing_reanalysis)

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
    else:
        missing_controls = [
            field for field in REQUIRED_CLAIM_CONTROLS
            if field not in controls
        ]
        blockers.update(f"claim_controls.{field}" for field in missing_controls)
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_must_remain_disabled_before_review")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_must_remain_disabled_before_review")
        if controls.get("external_adversarial_review_complete") is not False:
            blockers.add("external_review_must_be_false_in_preclaim_spec")

    return {
        "ready_for_alpha_join_extension": not blockers,
        "missing_join_extension_fields": sorted(missing_fields),
        "missing_source_reanalysis_fields": sorted(missing_reanalysis),
        "blockers": sorted(blockers),
    }


def evaluate_external_g8_measurement_packet(packet: dict[str, Any]) -> dict[str, Any]:
    base = evaluate_g8_adapter_packet(packet)
    join = _evaluate_join_extension(packet)
    synthetic_control = bool(
        packet.get("synthetic_fixture")
        or packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )

    blockers: set[str] = set()
    if base["adapter_acceptance_ready"] is not True:
        blockers.add("base_g8_adapter_gate_failed")
    if join["ready_for_alpha_join_extension"] is not True:
        blockers.add("alpha_join_extension_gate_failed")

    engine_join_ready = not blockers
    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic_control:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not engine_join_ready:
        claim_blockers.add("external_g8_join_packet_not_ready")

    return canonicalize_json_floats({
        "label": packet.get("label"),
        "base_g8_adapter_evaluation": base,
        "alpha_join_extension_evaluation": join,
        "synthetic_control": synthetic_control,
        "ready_for_engine_g8_join_packet": engine_join_ready,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions": [],
        "packet_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "external_g8_measurement_packet_engine_join_ready_nonclaiming"
            if engine_join_ready
            else "external_g8_measurement_packet_blocked"
        ),
    })


def current_source_gap_rows() -> list[dict[str, Any]]:
    rows = []
    for candidate in current_joint_source_candidates():
        missing = candidate["missing_gate_capabilities"]
        rows.append({
            "label": candidate["label"],
            "source_url": candidate["source_url"],
            "potential_axes": candidate["potential_axes"],
            "g8_axis_candidate": "g_8" in candidate["potential_axes"],
            "missing_gate_capabilities": missing,
            "fills_external_g8_packet_contract_now": False,
            "contract_gap_count": len(missing),
        })
    return sorted(rows, key=lambda row: (row["contract_gap_count"], row["label"]))


def diagnose_external_g8_measurement_packet_spec() -> dict[str, Any]:
    alpha_audit = diagnose_gw_alpha_g8_joint_component_audit()
    synthetic = evaluate_external_g8_measurement_packet(
        synthetic_alpha_join_g8_packet()
    )
    missing_slot = evaluate_external_g8_measurement_packet(
        current_missing_external_g8_packet_slot()
    )
    source_gaps = current_source_gap_rows()
    ready_current_sources = [
        row["label"] for row in source_gaps
        if row["fills_external_g8_packet_contract_now"]
    ]

    return {
        "version": VERSION,
        "basis": [
            "v2.54_g8_high_moment_measurement_specification",
            "v2.79_g8_adapter_acceptance_harness",
            "v2.98_g8_joint_packet_acceptance_gate",
            "v2.126_gw_alpha_g8_joint_component_audit",
        ],
        "route": "external_spin4_or_detector_g8_measurement_packet_spec",
        "contract": external_g8_measurement_packet_contract(),
        "alpha_packet_ready_for_g8_join": alpha_audit[
            "g8_joint_component_audit"
        ]["alpha_status"]["ready_for_g8_join"],
        "synthetic_control_evaluation": synthetic,
        "current_missing_packet_slot_evaluation": missing_slot,
        "current_source_gap_rows": source_gaps,
        "ready_current_external_g8_packets": ready_current_sources,
        "claimable_framework_exclusions_now": [],
        "claimable_discriminator_now": False,
        "route_status": "external_g8_packet_spec_ready_no_real_packet",
        "selected_next_build_action": (
            "search_or_request_real_external_g8_packet_that_fills_v2_166_contract"
        ),
        "best_next_artifact": (
            "A public spin-4 partial-wave, detector-moment, or source-projected "
            "high-moment g_8 packet with covariance to the calibrated alpha "
            "likelihood and closed systematics."
        ),
        "interpretation": (
            "The alpha side can already accept a G8 join. v2.166 defines the "
            "missing external G8 packet contract and proves the evaluator accepts "
            "a complete synthetic control, while current source candidates still "
            "leave the real packet slot empty."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.166/"
            "external_g8_measurement_packet_spec.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_external_g8_measurement_packet_spec()
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
