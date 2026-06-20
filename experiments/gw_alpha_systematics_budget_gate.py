"""Partial systematics-budget closure for the v2.117 alpha packet."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_engine_projection_packet import (
    DEFAULT_PACKET_EXPORT_PATH,
    load_v2_116_packet,
    packet_with_explicit_alpha_engine_projection,
)
from experiments.gw_cubic_source_native_adapter import (
    REQUIRED_SYSTEMATICS_COMPONENTS,
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_lalsuite_marginal_alpha_likelihood import (
    GRID_POINTS_PER_AXIS,
)
from experiments.gw_marginal_alpha_packet_export import DEFAULT_MARGINAL_RESULT_PATH


VERSION = "v2.118"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sampler_convergence_evidence(
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    network = marginal_result["network_likelihood"]
    detector_likelihoods = marginal_result["detector_likelihoods"]
    nuisance_counts = [
        row["marginal_alpha_likelihood"]["nuisance_grid"]["nuisance_points"]
        for row in detector_likelihoods
    ]
    grid_points = int(network["grid_points"])
    expected_grid_points = GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
    deterministic_ready = (
        grid_points == expected_grid_points
        and nuisance_counts == [81, 81]
        and all(row["likelihood_ready"] for row in detector_likelihoods)
        and network["best_marginal_grid_point"]["alpha_bar_1"] == 0.0
        and network["best_marginal_grid_point"]["alpha_bar_2"] == 0.0
    )
    return {
        "status": "bounded" if deterministic_ready else "open",
        "basis": "deterministic_grid_enumeration_no_stochastic_sampler",
        "alpha_grid_points": grid_points,
        "expected_alpha_grid_points": expected_grid_points,
        "nuisance_points_per_detector": nuisance_counts,
        "detectors": network["detectors"],
        "best_marginal_grid_point": network["best_marginal_grid_point"],
        "best_profile_grid_point": network["best_profile_grid_point"],
        "deterministic_ready": deterministic_ready,
    }


def public_data_reproducibility_evidence() -> dict[str, Any]:
    return {
        "status": "bounded",
        "basis": "v2.107_hash_metadata_and_vulcan_reproduction",
        "required_detectors": ["H1", "L1"],
        "public_strain_artifact": (
            "experiments/results/v2.107/gw_public_strain_loader.json"
        ),
        "cache_rehydration_supported": True,
    }


def open_systematics_evidence() -> dict[str, dict[str, Any]]:
    return {
        "waveform_systematics": {
            "status": "open",
            "reason": (
                "Linearized cubic response uses source-backed inspiral terms and "
                "LALSuite IMRPhenomD GR baseline, but no calibrated cubic-EFT "
                "full-IMR waveform systematics envelope exists."
            ),
            "next_required_evidence": "source-backed IMR cubic-EFT waveform uncertainty",
        },
        "detector_calibration": {
            "status": "open",
            "reason": "No detector calibration uncertainty envelope is propagated.",
            "next_required_evidence": "H1/L1 calibration amplitude-phase uncertainty model",
        },
        "prior_sensitivity": {
            "status": "open",
            "reason": (
                "The marginal optimum and profile optimum disagree, so current "
                "coarse nuisance weighting is not a posterior prior study."
            ),
            "next_required_evidence": "prior sweep or posterior sampler stability",
        },
        "eft_truncation": {
            "status": "open",
            "reason": (
                "The source-backed response includes finite-order cubic EFT "
                "terms without a numerical higher-order truncation bound."
            ),
            "next_required_evidence": "alpha-domain EFT truncation remainder estimate",
        },
    }


def component_evidence(
    marginal_result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    evidence = open_systematics_evidence()
    evidence["sampler_convergence"] = sampler_convergence_evidence(marginal_result)
    evidence["public_data_reproducibility"] = public_data_reproducibility_evidence()
    return {
        component: evidence[component] for component in REQUIRED_SYSTEMATICS_COMPONENTS
    }


def packet_with_partial_systematics_budget(
    packet: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    evidence = component_evidence(marginal_result)
    projected = deepcopy(packet)
    projected["label"] = "v2_118_partial_systematics_alpha_packet"
    projected["systematics_budget"] = {
        "status": (
            "bounded"
            if all(row["status"] == "bounded" for row in evidence.values())
            else "open"
        ),
        "components": {
            component: row["status"] for component, row in evidence.items()
        },
        "evidence": evidence,
    }
    projected["validation_reference"] = "v2.118_alpha_systematics_budget_gate"
    return projected


def evaluate_alpha_systematics_budget(
    packet: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget = packet["systematics_budget"]
    components = budget["components"]
    bounded = [
        component
        for component in REQUIRED_SYSTEMATICS_COMPONENTS
        if components.get(component) == "bounded"
    ]
    open_components = [
        component
        for component in REQUIRED_SYSTEMATICS_COMPONENTS
        if components.get(component) != "bounded"
    ]
    return {
        "partial_systematics_budget_ready": bool(bounded),
        "bounded_components": bounded,
        "open_components": open_components,
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "removed_v2_117_subblockers": [
            component
            for component in ("sampler_convergence", "public_data_reproducibility")
            if component in bounded
        ],
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "gw_cubic_alpha_axis_not_framework_discriminator_by_itself",
            }
        ),
    }


def diagnose_gw_alpha_systematics_budget_gate(
    packet_export_path: Path = DEFAULT_PACKET_EXPORT_PATH,
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
) -> dict[str, Any]:
    base_packet = packet_with_explicit_alpha_engine_projection(
        load_v2_116_packet(packet_export_path)
    )
    marginal_result = load_json(marginal_result_path)
    packet = packet_with_partial_systematics_budget(base_packet, marginal_result)
    evaluation = evaluate_alpha_systematics_budget(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.117_alpha_engine_projection_packet",
            "v2.115_lalsuite_marginal_alpha_likelihood",
            "v2.102_source_native_alpha_adapter",
        ],
        "packet_export_path": str(packet_export_path),
        "marginal_result_path": str(marginal_result_path),
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "alpha_systematics_budget_partially_bounded_nonclaiming",
        "selected_next_build_action": (
            "bound_waveform_calibration_prior_and_eft_systematics"
        ),
        "best_next_artifact": (
            "Attach quantitative waveform, detector-calibration, prior, and "
            "EFT-truncation envelopes to the v2.118 packet, then rerun the "
            "v2.102 adapter gate."
        ),
        "interpretation": (
            "The packet now carries executable evidence for bounded deterministic "
            "grid convergence and public-data reproducibility. It remains "
            "nonclaiming because waveform, detector calibration, prior "
            "sensitivity, and EFT truncation systematics are still open."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-export", default=str(DEFAULT_PACKET_EXPORT_PATH))
    parser.add_argument("--marginal-result", default=str(DEFAULT_MARGINAL_RESULT_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.118/gw_alpha_systematics_budget_gate.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_systematics_budget_gate(
        packet_export_path=Path(args.packet_export),
        marginal_result_path=Path(args.marginal_result),
    )
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
