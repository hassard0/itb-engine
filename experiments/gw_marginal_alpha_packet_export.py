"""Export the v2.115 marginal alpha likelihood as a source-native packet."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_cubic_source_native_adapter import (
    REQUIRED_SOURCE_NATIVE_PACKET_FIELDS,
    SOURCE_MODEL,
    SOURCE_PARAMETERS,
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_source_backed_cubic_waveform_response import SOURCE_REFERENCE


VERSION = "v2.116"
DEFAULT_MARGINAL_RESULT_PATH = Path(
    "experiments/results/v2.115/gw_lalsuite_marginal_alpha_likelihood.json"
)


def load_marginal_result(path: Path = DEFAULT_MARGINAL_RESULT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_likelihood_weights(rows: list[dict[str, float]]) -> np.ndarray:
    log_likelihoods = np.asarray(
        [row["log_marginal_likelihood"] for row in rows],
        dtype=float,
    )
    if log_likelihoods.size == 0 or not np.all(np.isfinite(log_likelihoods)):
        raise ValueError("network likelihood rows must contain finite log values")
    shifted = log_likelihoods - float(np.max(log_likelihoods))
    weights = np.exp(shifted)
    total = float(np.sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("likelihood weights cannot be normalized")
    return weights / total


def weighted_quantile(
    values: np.ndarray,
    weights: np.ndarray,
    quantile: float,
) -> float:
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be in [0, 1]")
    order = np.argsort(values)
    sorted_values = np.asarray(values, dtype=float)[order]
    sorted_weights = np.asarray(weights, dtype=float)[order]
    cumulative = np.cumsum(sorted_weights)
    cumulative /= float(cumulative[-1])
    return float(np.interp(float(quantile), cumulative, sorted_values))


def marginal_alpha_statistics(network_likelihood: dict[str, Any]) -> dict[str, Any]:
    rows = network_likelihood["grid"]
    weights = normalized_likelihood_weights(rows)
    alpha_values = np.array(
        [[row["alpha_bar_1"], row["alpha_bar_2"]] for row in rows],
        dtype=float,
    )
    mean = weights @ alpha_values
    centered = alpha_values - mean
    covariance = centered.T @ (centered * weights[:, None])
    constraints = {}
    for index, parameter in enumerate(SOURCE_PARAMETERS):
        values = alpha_values[:, index]
        constraints[parameter] = {
            "central": float(mean[index]),
            "lower_90": weighted_quantile(values, weights, 0.05),
            "upper_90": weighted_quantile(values, weights, 0.95),
        }
    return {
        "parameter_constraints": constraints,
        "source_parameter_covariance": {
            "parameters": list(SOURCE_PARAMETERS),
            "matrix": covariance.tolist(),
        },
        "weighted_mean": {
            "alpha_bar_1": float(mean[0]),
            "alpha_bar_2": float(mean[1]),
        },
        "best_marginal_grid_point": network_likelihood["best_marginal_grid_point"],
        "best_profile_grid_point": network_likelihood["best_profile_grid_point"],
        "weight_summary": {
            "grid_points": int(len(rows)),
            "max_weight": float(np.max(weights)),
            "effective_sample_size": float(1.0 / np.sum(weights * weights)),
        },
    }


def marginal_alpha_source_native_packet(
    result: dict[str, Any],
) -> dict[str, Any]:
    stats = marginal_alpha_statistics(result["network_likelihood"])
    return {
        "label": "v2_115_lalsuite_marginal_alpha_likelihood_packet",
        "source_url": SOURCE_REFERENCE,
        "source_model": SOURCE_MODEL,
        "event": "GW170608",
        "source_parameters": list(SOURCE_PARAMETERS),
        "parameter_constraints": stats["parameter_constraints"],
        "posterior_or_likelihood_export": {
            "status": "reproduced_source_native_likelihood",
            "kind": "coarse_nuisance_marginal_lalsuite_imrphenomd_grid",
            "parameters": list(SOURCE_PARAMETERS),
            "grid_points": result["network_likelihood"]["grid_points"],
            "detectors": result["network_likelihood"]["detectors"],
            "nuisance_points_per_detector": result["detector_likelihoods"][0][
                "marginal_alpha_likelihood"
            ]["nuisance_grid"]["nuisance_points"],
            "best_marginal_grid_point": stats["best_marginal_grid_point"],
            "best_profile_grid_point": stats["best_profile_grid_point"],
            "weight_summary": stats["weight_summary"],
        },
        "source_parameter_covariance": stats["source_parameter_covariance"],
        "waveform_model_reference": "LALSuite_IMRPhenomD_linearized_cubic_EFT_response",
        "normalization_convention": "paper_native_dimensionless_alpha_bar",
        "engine_axis_strategy": {"status": "source_native_alpha_space_only"},
        "framework_projection_strategy": "not_attempted_source_native_only",
        "systematics_budget": {
            "status": "open",
            "components": {
                "waveform_systematics": "open",
                "detector_calibration": "open",
                "prior_sensitivity": "open",
                "eft_truncation": "open",
                "sampler_convergence": "open",
                "public_data_reproducibility": "bounded",
            },
        },
        "shared_eft_domain": "bounded_for_source_native_cubic_gw",
        "validation_reference": "v2.115_lalsuite_marginal_alpha_likelihood",
        "synthetic_fixture": False,
    }


def evaluate_packet_export(packet: dict[str, Any]) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    missing_fields = [
        field for field in REQUIRED_SOURCE_NATIVE_PACKET_FIELDS if field not in packet
    ]
    return {
        "packet_export_ready": not missing_fields,
        "missing_packet_fields": missing_fields,
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "removed_v2_115_blocker": (
            "source_native_packet_not_exported" if not missing_fields else None
        ),
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_budget_missing_or_open",
                "engine_projection_not_ready",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
            }
        ),
    }


def diagnose_gw_marginal_alpha_packet_export(
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
) -> dict[str, Any]:
    result = load_marginal_result(marginal_result_path)
    packet = marginal_alpha_source_native_packet(result)
    evaluation = evaluate_packet_export(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.115_lalsuite_marginal_alpha_likelihood",
            "v2.102_source_native_alpha_adapter",
        ],
        "marginal_result_path": str(marginal_result_path),
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "marginal_alpha_source_native_packet_exported_nonclaiming"
            if evaluation["packet_export_ready"]
            else "marginal_alpha_source_native_packet_export_not_ready"
        ),
        "selected_next_build_action": (
            "close_systematics_budget_and_engine_projection_for_alpha_packet"
        ),
        "best_next_artifact": (
            "Add calibrated noise evidence, detector calibration bounds, "
            "sampler convergence checks, and an explicit source-to-engine "
            "projection strategy before any claim promotion."
        ),
        "interpretation": (
            "The v2.115 nuisance-marginal alpha likelihood is now exported as a "
            "v2.102-shaped source-native packet. The adapter can parse the "
            "constraints, covariance, and likelihood export, but rejects the "
            "packet for claim promotion because systematics remain open and the "
            "engine/g8 projection is absent."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--marginal-result",
        default=str(DEFAULT_MARGINAL_RESULT_PATH),
    )
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.116/"
            "gw_marginal_alpha_packet_export.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_marginal_alpha_packet_export(Path(args.marginal_result))
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
