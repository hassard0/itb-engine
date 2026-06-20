"""Weyl/G8 dual-likelihood contract with explicit claim controls."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_joint_packet_acceptance_gate import (
    REQUIRED_JOINT_PACKET_FIELDS,
    evaluate_g8_joint_packet,
    synthetic_ready_joint_g8_g_c_packet,
)
from experiments.g8_joint_source_discovery_queue import (
    current_joint_source_candidates,
    diagnose_g8_joint_source_discovery_queue,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.172"
FRONTIER_ROUTE = "weyl_g8_joint_frontier"
BASE_JOINT_ROUTE = "g8_joint_secondary_axis_measurement_design"
TARGET_AXES = ("g_8", "g_C")
REQUIRED_WEYL_EXTENSION_FIELDS = (
    "frontier_route",
    "weyl_frontier_basis",
    "engine_g_c_packet",
    "engine_g8_packet",
    "joint_covariance_or_likelihood",
    "cross_axis_correlation_model",
    "framework_projection_matrix",
    "joint_exclusion_statistic",
    "look_elsewhere_or_scan_policy",
    "source_reanalysis_package",
    "claim_controls",
)
REQUIRED_SOURCE_REANALYSIS_FIELDS = (
    "public_data_or_samples",
    "analysis_code_or_likelihood_sampler",
    "observable_or_waveform_model",
    "nuisance_parameter_policy",
    "reproducibility_instructions",
)
REQUIRED_CLAIM_CONTROLS = (
    "claim_use_allowed",
    "framework_claim_allowed",
    "external_adversarial_review_complete",
)
VALID_ENGINE_PACKET_STATUSES = {
    "source_backed_engine_axis",
    "public_engine_usable",
}
VALID_LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
}
VALID_BOUNDED_STATUSES = {"bounded", "closed"}


def weyl_g8_dual_likelihood_contract() -> dict[str, Any]:
    return {
        "version": VERSION,
        "route": FRONTIER_ROUTE,
        "external_object": "joint_engine_gC_g8_likelihood",
        "target_axes": list(TARGET_AXES),
        "base_joint_packet_fields": list(REQUIRED_JOINT_PACKET_FIELDS),
        "weyl_extension_fields": list(REQUIRED_WEYL_EXTENSION_FIELDS),
        "source_reanalysis_required_fields": list(
            REQUIRED_SOURCE_REANALYSIS_FIELDS
        ),
        "claim_control_fields": list(REQUIRED_CLAIM_CONTROLS),
        "base_gate": "v2.98_g8_joint_packet_acceptance_gate",
        "source_url_policy": "https://arxiv.org/, https://doi.org/, or public data/code release",
        "claim_rule": (
            "A packet may become Weyl/G8-engine-ready only after the v2.98 "
            "joint packet gate and this frontier extension pass. Framework "
            "claims remain disabled until external adversarial review completes."
        ),
    }


def synthetic_ready_weyl_g8_dual_likelihood_packet() -> dict[str, Any]:
    packet = synthetic_ready_joint_g8_g_c_packet()
    packet["label"] = "synthetic_ready_weyl_g8_dual_likelihood_packet"
    packet["frontier_route"] = FRONTIER_ROUTE
    packet["weyl_frontier_basis"] = {
        "status": "confirmed",
        "basis": "v2.50_weyl_g8_discriminator_frontier",
        "axes": list(TARGET_AXES),
        "stable_weyl_g8_frontier": True,
    }
    packet["engine_g_c_packet"] = {
        "status": "source_backed_engine_axis",
        "axis": "g_C",
        "normalization": "source_backed_engine_g_C",
        "source_url": "https://doi.org/10.0000/synthetic-gc-packet",
    }
    packet["engine_g8_packet"] = {
        "status": "source_backed_engine_axis",
        "axis": "g_8",
        "normalization": "engine_low_energy_g8",
        "source_url": "https://doi.org/10.0000/synthetic-g8-packet",
    }
    packet["joint_covariance_or_likelihood"] = {
        "status": "public_engine_usable",
        "axes": list(TARGET_AXES),
        "kind": "joint_gaussian_likelihood",
        "covariance": [[1.25e-6, 0.0], [0.0, 0.001]],
    }
    packet["cross_axis_correlation_model"] = {
        "status": "bounded",
        "axes": list(TARGET_AXES),
        "cross_terms_declared": True,
    }
    packet["framework_projection_matrix"] = {
        "status": "excludes_registered_framework",
        "framework_pair": ["string_tree_eft", "discovered_data_driven"],
        "projection_axes": list(TARGET_AXES),
    }
    packet["joint_exclusion_statistic"] = {
        "status": "excludes_at_or_above_2sigma",
        "sigma_distance": 2.4,
        "statistic": "synthetic_delta_chi2",
    }
    packet["look_elsewhere_or_scan_policy"] = {
        "status": "declared",
        "multiple_testing_controlled": True,
    }
    packet["source_reanalysis_package"] = {
        "public_data_or_samples": True,
        "analysis_code_or_likelihood_sampler": True,
        "observable_or_waveform_model": "synthetic_weyl_g8_joint_model",
        "nuisance_parameter_policy": "shared_or_marginalized",
        "reproducibility_instructions": True,
    }
    packet["claim_controls"] = {
        "claim_use_allowed": False,
        "framework_claim_allowed": False,
        "external_adversarial_review_complete": False,
        "synthetic_control_not_claim_evidence": True,
    }
    return packet


def current_missing_weyl_g8_dual_likelihood_slot() -> dict[str, Any]:
    return {
        "label": "current_missing_weyl_g8_dual_likelihood_slot",
        "route": BASE_JOINT_ROUTE,
        "frontier_route": FRONTIER_ROUTE,
        "source_url": "",
        "source_type": "",
        "axes": list(TARGET_AXES),
        "secondary_axis": "g_C",
        "synthetic_fixture": False,
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
        },
    }


def _missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def _finite_at_least(value: Any, threshold: float) -> bool:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    numeric = float(value)
    return math.isfinite(numeric) and numeric >= threshold


def _evaluate_axis_packet(
    packet: dict[str, Any],
    *,
    axis: str,
    expected_normalizations: set[str],
) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") not in VALID_ENGINE_PACKET_STATUSES:
        blockers.append(f"{axis}_packet_not_source_backed_engine_axis")
    if packet.get("axis") != axis:
        blockers.append(f"{axis}_packet_axis_mismatch")
    if packet.get("normalization") not in expected_normalizations:
        blockers.append(f"{axis}_packet_normalization_not_engine")
    source_url = str(packet.get("source_url") or "")
    if source_url and not source_url.startswith(("https://arxiv.org/", "https://doi.org/")):
        blockers.append(f"{axis}_packet_source_url_not_primary_allowed")
    return blockers


def _evaluate_weyl_extension(packet: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_WEYL_EXTENSION_FIELDS
        if _missing(packet.get(field))
    ]
    blockers: set[str] = set(missing_fields)

    if packet.get("frontier_route") != FRONTIER_ROUTE:
        blockers.add("frontier_route_not_weyl_g8")
    axes = set(packet.get("axes") or [])
    if not set(TARGET_AXES).issubset(axes):
        blockers.add("packet_axes_missing_g8_or_g_c")
    if packet.get("secondary_axis") != "g_C":
        blockers.add("secondary_axis_not_g_c_for_weyl_frontier")

    basis = packet.get("weyl_frontier_basis")
    if not isinstance(basis, dict):
        blockers.add("weyl_frontier_basis_missing")
    else:
        if basis.get("status") != "confirmed":
            blockers.add("weyl_frontier_basis_not_confirmed")
        if basis.get("stable_weyl_g8_frontier") is not True:
            blockers.add("stable_weyl_g8_frontier_not_confirmed")
        if not set(TARGET_AXES).issubset(set(basis.get("axes") or [])):
            blockers.add("weyl_frontier_basis_axes_incomplete")

    g_c_packet = packet.get("engine_g_c_packet")
    if not isinstance(g_c_packet, dict):
        blockers.add("engine_g_c_packet_missing")
    else:
        blockers.update(
            _evaluate_axis_packet(
                g_c_packet,
                axis="g_C",
                expected_normalizations={"source_backed_engine_g_C"},
            )
        )

    g8_packet = packet.get("engine_g8_packet")
    if not isinstance(g8_packet, dict):
        blockers.add("engine_g8_packet_missing")
    else:
        blockers.update(
            _evaluate_axis_packet(
                g8_packet,
                axis="g_8",
                expected_normalizations={
                    "engine_low_energy_g8",
                    "source_backed_engine_g8",
                },
            )
        )

    likelihood = packet.get("joint_covariance_or_likelihood")
    if not isinstance(likelihood, dict):
        blockers.add("joint_covariance_or_likelihood_missing")
    else:
        if likelihood.get("status") not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("joint_covariance_or_likelihood_not_public")
        if not set(TARGET_AXES).issubset(set(likelihood.get("axes") or [])):
            blockers.add("joint_covariance_or_likelihood_axes_incomplete")

    correlation = packet.get("cross_axis_correlation_model")
    if not isinstance(correlation, dict):
        blockers.add("cross_axis_correlation_model_missing")
    else:
        if correlation.get("status") not in VALID_BOUNDED_STATUSES:
            blockers.add("cross_axis_correlation_not_bounded")
        if correlation.get("cross_terms_declared") is not True:
            blockers.add("cross_axis_terms_not_declared")

    projection = packet.get("framework_projection_matrix")
    if not isinstance(projection, dict):
        blockers.add("framework_projection_matrix_missing")
    else:
        if projection.get("status") != "excludes_registered_framework":
            blockers.add("framework_projection_matrix_not_excluding")
        if not set(TARGET_AXES).issubset(set(projection.get("projection_axes") or [])):
            blockers.add("framework_projection_axes_incomplete")

    statistic = packet.get("joint_exclusion_statistic")
    if not isinstance(statistic, dict):
        blockers.add("joint_exclusion_statistic_missing")
    else:
        if statistic.get("status") != "excludes_at_or_above_2sigma":
            blockers.add("joint_exclusion_statistic_not_excluding")
        if not _finite_at_least(statistic.get("sigma_distance"), 2.0):
            blockers.add("joint_exclusion_statistic_below_2sigma")

    scan = packet.get("look_elsewhere_or_scan_policy")
    if not isinstance(scan, dict):
        blockers.add("look_elsewhere_or_scan_policy_missing")
    else:
        if scan.get("status") != "declared":
            blockers.add("look_elsewhere_or_scan_policy_not_declared")
        if scan.get("multiple_testing_controlled") is not True:
            blockers.add("multiple_testing_not_controlled")

    reanalysis = packet.get("source_reanalysis_package")
    if not isinstance(reanalysis, dict):
        blockers.add("source_reanalysis_package_missing")
        missing_reanalysis = list(REQUIRED_SOURCE_REANALYSIS_FIELDS)
    else:
        missing_reanalysis = [
            field for field in REQUIRED_SOURCE_REANALYSIS_FIELDS
            if _missing(reanalysis.get(field))
        ]
        blockers.update(f"source_reanalysis.{field}" for field in missing_reanalysis)

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
        missing_controls = list(REQUIRED_CLAIM_CONTROLS)
    else:
        missing_controls = [
            field for field in REQUIRED_CLAIM_CONTROLS if field not in controls
        ]
        blockers.update(f"claim_controls.{field}" for field in missing_controls)
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_must_remain_disabled_before_review")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_must_remain_disabled_before_review")
        if controls.get("external_adversarial_review_complete") is not False:
            blockers.add("external_review_must_be_false_in_preclaim_spec")

    return {
        "ready_for_weyl_g8_extension": not blockers,
        "missing_weyl_extension_fields": sorted(missing_fields),
        "missing_source_reanalysis_fields": sorted(missing_reanalysis),
        "missing_claim_controls": sorted(missing_controls),
        "extension_blockers": sorted(blockers),
    }


def evaluate_weyl_g8_dual_likelihood_packet(packet: dict[str, Any]) -> dict[str, Any]:
    base = evaluate_g8_joint_packet(packet)
    extension = _evaluate_weyl_extension(packet)
    synthetic = bool(
        packet.get("synthetic_fixture")
        or packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )

    blockers: set[str] = set()
    if base["acceptance_ready"] is not True:
        blockers.add("base_g8_gc_joint_gate_failed")
    if extension["ready_for_weyl_g8_extension"] is not True:
        blockers.add("weyl_g8_extension_gate_failed")

    engine_ready = not blockers
    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not engine_ready:
        claim_blockers.add("weyl_g8_dual_likelihood_not_ready")

    return canonicalize_json_floats({
        "label": packet.get("label"),
        "base_joint_packet_evaluation": base,
        "weyl_extension_evaluation": extension,
        "synthetic_control": synthetic,
        "ready_for_weyl_g8_dual_likelihood": engine_ready,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions": [],
        "packet_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "weyl_g8_dual_likelihood_ready_nonclaiming"
            if engine_ready
            else "weyl_g8_dual_likelihood_blocked"
        ),
    })


def current_weyl_g8_source_gap_rows() -> list[dict[str, Any]]:
    rows = []
    for candidate in current_joint_source_candidates():
        axes = set(candidate["potential_axes"])
        if not axes & set(TARGET_AXES):
            continue
        missing = sorted(candidate["missing_gate_capabilities"])
        rows.append({
            "label": candidate["label"],
            "source_url": candidate["source_url"],
            "source_type": candidate["source_type"],
            "potential_axes": candidate["potential_axes"],
            "g8_axis_candidate": "g_8" in axes,
            "g_c_axis_candidate": "g_C" in axes,
            "fills_weyl_g8_contract_now": False,
            "missing_gate_capabilities": missing,
            "contract_gap_count": len(missing),
        })
    return sorted(rows, key=lambda row: (row["contract_gap_count"], row["label"]))


def diagnose_weyl_g8_dual_likelihood_contract() -> dict[str, Any]:
    source_queue = diagnose_g8_joint_source_discovery_queue()
    synthetic = evaluate_weyl_g8_dual_likelihood_packet(
        synthetic_ready_weyl_g8_dual_likelihood_packet()
    )
    missing_slot = evaluate_weyl_g8_dual_likelihood_packet(
        current_missing_weyl_g8_dual_likelihood_slot()
    )
    source_gaps = current_weyl_g8_source_gap_rows()
    ready_current = [
        row["label"] for row in source_gaps if row["fills_weyl_g8_contract_now"]
    ]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.50_weyl_g8_discriminator_frontier",
            "v2.51_weyl_g8_observable_sourceability",
            "v2.98_g8_joint_packet_acceptance_gate",
            "v2.99_g8_joint_source_discovery_queue",
        ],
        "route": FRONTIER_ROUTE,
        "contract": weyl_g8_dual_likelihood_contract(),
        "base_joint_gate_status": "v2.98_g8_joint_packet_gate_ready_no_real_packet",
        "selected_source_queue_build_route": source_queue[
            "selected_next_build_route"
        ]["route"],
        "synthetic_control_evaluation": synthetic,
        "current_missing_packet_slot_evaluation": missing_slot,
        "current_source_gap_rows": source_gaps,
        "ready_current_weyl_g8_packets": ready_current,
        "claimable_framework_exclusions_now": [],
        "claimable_discriminator_now": False,
        "route_status": "weyl_g8_dual_likelihood_contract_ready_no_real_packet",
        "selected_next_build_action": (
            "build_or_request_real_joint_engine_gC_g8_likelihood_packet"
        ),
        "best_next_artifact": (
            "A public joint engine-normalized g_C+g_8 likelihood packet with "
            "source-backed axis packets, covariance/correlation, projection "
            "matrix, exclusion statistic, scan policy, reproducible analysis, "
            "and adversarial review controls."
        ),
        "interpretation": (
            "The Weyl/G8 route now has a claim-safe executable packet contract. "
            "The v2.98 base gate and this extension accept a complete synthetic "
            "control, while current public source candidates still leave the "
            "real dual-likelihood slot empty."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.172/"
            "weyl_g8_dual_likelihood_contract.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_weyl_g8_dual_likelihood_contract()
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
