"""Minimal alpha-bar likelihood stub for v2.105."""

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
from experiments.gw_alpha_interval_surrogate import (
    build_alpha_interval_surrogate_packet,
    diagnose_gw_alpha_interval_surrogate,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.105"
PARAMETERS = ("alpha_bar_1", "alpha_bar_2")
CENTER = {"alpha_bar_1": 0.87, "alpha_bar_2": -0.35}
PRIOR_BOX = {"alpha_bar_1": (-8.0, 8.0), "alpha_bar_2": (-8.0, 8.0)}


def alpha_covariance_from_interval_surrogate() -> np.ndarray:
    covariance = diagnose_gw_alpha_interval_surrogate()["surrogate_covariance"]
    return np.array(covariance["matrix"], dtype=float)


def alpha_vector(alpha_bar_1: float, alpha_bar_2: float) -> np.ndarray:
    return np.array([float(alpha_bar_1), float(alpha_bar_2)], dtype=float)


def quadratic_alpha_log_likelihood(alpha_bar_1: float, alpha_bar_2: float) -> float:
    covariance = alpha_covariance_from_interval_surrogate()
    inverse_covariance = np.linalg.inv(covariance)
    delta = alpha_vector(alpha_bar_1, alpha_bar_2) - alpha_vector(
        CENTER["alpha_bar_1"],
        CENTER["alpha_bar_2"],
    )
    return -0.5 * float(delta.T @ inverse_covariance @ delta)


def deterministic_alpha_grid(points_per_axis: int = 31) -> list[dict[str, float]]:
    if points_per_axis < 3:
        raise ValueError("points_per_axis must be at least 3")
    covariance = alpha_covariance_from_interval_surrogate()
    sigma_1 = math.sqrt(float(covariance[0, 0]))
    sigma_2 = math.sqrt(float(covariance[1, 1]))
    axis_1 = np.linspace(
        CENTER["alpha_bar_1"] - 3.0 * sigma_1,
        CENTER["alpha_bar_1"] + 3.0 * sigma_1,
        points_per_axis,
    )
    axis_2 = np.linspace(
        CENTER["alpha_bar_2"] - 3.0 * sigma_2,
        CENTER["alpha_bar_2"] + 3.0 * sigma_2,
        points_per_axis,
    )
    rows = []
    for alpha_1 in axis_1:
        for alpha_2 in axis_2:
            rows.append(
                {
                    "alpha_bar_1": float(alpha_1),
                    "alpha_bar_2": float(alpha_2),
                    "log_likelihood": quadratic_alpha_log_likelihood(
                        float(alpha_1),
                        float(alpha_2),
                    ),
                }
            )
    return rows


def _best_grid_point(rows: list[dict[str, float]]) -> dict[str, float]:
    return max(rows, key=lambda row: row["log_likelihood"])


def synthetic_alpha_likelihood_stub_packet() -> dict[str, Any]:
    surrogate = build_alpha_interval_surrogate_packet()
    packet = {
        **surrogate,
        "label": "synthetic_alpha_likelihood_stub_packet",
        "source_url": "https://doi.org/10.0000/synthetic-alpha-likelihood-stub",
        "posterior_or_likelihood_export": {
            "status": "reproduced_source_native_likelihood",
            "kind": "quadratic_alpha_bar_likelihood_stub",
            "parameters": list(PARAMETERS),
            "grid_points": 31 * 31,
            "public_strain_connected": False,
        },
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
        "validation_reference": "v2.105_minimal_alpha_likelihood_stub",
        "synthetic_fixture": True,
    }
    return packet


def diagnose_gw_alpha_likelihood_stub() -> dict[str, Any]:
    grid = deterministic_alpha_grid()
    best = _best_grid_point(grid)
    packet = synthetic_alpha_likelihood_stub_packet()
    adapter_evaluation = evaluate_gw_cubic_source_native_packet(packet)
    center_log_like = quadratic_alpha_log_likelihood(
        CENTER["alpha_bar_1"],
        CENTER["alpha_bar_2"],
    )
    shifted_log_like = quadratic_alpha_log_likelihood(
        CENTER["alpha_bar_1"] + 1.0,
        CENTER["alpha_bar_2"] + 1.0,
    )

    return {
        "version": VERSION,
        "basis": [
            "v2.104_gw170608_alpha_reanalysis_manifest",
            "v2.103_interval_covariance_surrogate",
            "v2.102_source_native_adapter",
        ],
        "stub_scope": "synthetic_quadratic_alpha_likelihood_surface",
        "parameters": list(PARAMETERS),
        "prior_box": PRIOR_BOX,
        "center": CENTER,
        "covariance": alpha_covariance_from_interval_surrogate().tolist(),
        "grid_point_count": len(grid),
        "best_grid_point": best,
        "center_log_likelihood": center_log_like,
        "shifted_log_likelihood_alpha_plus_one": shifted_log_like,
        "source_native_packet_label": packet["label"],
        "adapter_evaluation": adapter_evaluation,
        "native_adapter_ready": adapter_evaluation["native_adapter_ready"],
        "claimable_discriminator_now": False,
        "route_status": "minimal_alpha_likelihood_stub_ready_synthetic_only",
        "selected_next_build_action": (
            "connect_public_strain_to_alpha_waveform_likelihood"
        ),
        "best_next_artifact": (
            "Replace the quadratic stub residual with a public-GW170608 "
            "strain-driven waveform likelihood while preserving this packet "
            "contract and v2.102 adapter evaluation."
        ),
        "interpretation": (
            "The alpha likelihood surface is now executable and exports a "
            "v2.102-compatible source-native packet, but it is synthetic and "
            "not connected to public strain. It is useful as a harness for the "
            "real reanalysis implementation, not as evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.105/gw_alpha_likelihood_stub.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_likelihood_stub()
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
