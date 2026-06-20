"""Prior/nuisance treatment stress test for the GW alpha packet."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.121"
DEFAULT_CALIBRATION_BOUND_PATH = Path(
    "experiments/results/v2.120/gw_alpha_detector_calibration_bound.json"
)
DEFAULT_MARGINAL_RESULT_PATH = Path(
    "experiments/results/v2.115/gw_lalsuite_marginal_alpha_likelihood.json"
)
PROFILE_TEMPERATURE_GRID = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0)


def alpha_axis_step(grid_rows: list[dict[str, Any]]) -> float:
    axis = sorted({float(row["alpha_bar_1"]) for row in grid_rows})
    if len(axis) < 2:
        raise ValueError("alpha grid must contain at least two axis points")
    steps = [right - left for left, right in zip(axis, axis[1:])]
    step = steps[0]
    if step <= 0.0 or any(abs(candidate - step) > 1.0e-12 for candidate in steps):
        raise ValueError("alpha grid axis must be uniformly spaced")
    return float(step)


def tempered_profile_log_likelihood(row: dict[str, Any], profile_temperature: float) -> float:
    if not math.isfinite(profile_temperature) or not 0.0 <= profile_temperature <= 1.0:
        raise ValueError("profile_temperature must be in [0, 1]")
    marginal = float(row["log_marginal_likelihood"])
    profile = float(row["profile_log_likelihood"])
    return (1.0 - profile_temperature) * marginal + profile_temperature * profile


def best_grid_point_at_profile_temperature(
    grid_rows: list[dict[str, Any]],
    profile_temperature: float,
) -> dict[str, Any]:
    if not grid_rows:
        raise ValueError("grid_rows must not be empty")
    best = max(
        grid_rows,
        key=lambda row: tempered_profile_log_likelihood(row, profile_temperature),
    )
    return {
        "alpha_bar_1": float(best["alpha_bar_1"]),
        "alpha_bar_2": float(best["alpha_bar_2"]),
        "tempered_log_likelihood": tempered_profile_log_likelihood(
            best,
            profile_temperature,
        ),
        "log_marginal_likelihood": float(best["log_marginal_likelihood"]),
        "profile_log_likelihood": float(best["profile_log_likelihood"]),
    }


def profile_temperature_sweep(
    marginal_result: dict[str, Any],
    *,
    temperatures: tuple[float, ...] = PROFILE_TEMPERATURE_GRID,
) -> dict[str, Any]:
    grid_rows = marginal_result["network_likelihood"]["grid"]
    axis_step = alpha_axis_step(grid_rows)
    baseline = best_grid_point_at_profile_temperature(grid_rows, 0.0)
    rows = []
    max_best_point_shift = 0.0
    first_axis_step_temperature = None
    for temperature in temperatures:
        best = best_grid_point_at_profile_temperature(grid_rows, temperature)
        shift = math.dist(
            (baseline["alpha_bar_1"], baseline["alpha_bar_2"]),
            (best["alpha_bar_1"], best["alpha_bar_2"]),
        )
        row = {
            "profile_temperature": temperature,
            "best_grid_point": best,
            "best_point_shift_from_marginal": shift,
            "exceeds_one_axis_grid_step": shift > axis_step + 1.0e-12,
        }
        rows.append(row)
        max_best_point_shift = max(max_best_point_shift, shift)
        if row["exceeds_one_axis_grid_step"] and first_axis_step_temperature is None:
            first_axis_step_temperature = temperature

    stable_under_profile_stress = first_axis_step_temperature is None
    return {
        "status": "bounded" if stable_under_profile_stress else "open",
        "stress_test_kind": "marginal_to_profile_temperature_path_from_saved_grid",
        "alpha_axis_step": axis_step,
        "baseline_best_grid_point": baseline,
        "temperature_rows": rows,
        "max_best_point_shift": max_best_point_shift,
        "first_temperature_exceeding_one_axis_grid_step": first_axis_step_temperature,
        "stable_under_profile_stress": stable_under_profile_stress,
        "closure_target": (
            "Export the per-nuisance likelihood cube so physically justified "
            "mass, eta, coalescence-time, and phase priors can be reweighted "
            "directly instead of using marginal/profile endpoints."
        ),
    }


def packet_with_prior_treatment_stress_test(
    calibration_packet: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(calibration_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence["prior_sensitivity"] = profile_temperature_sweep(marginal_result)
    packet["label"] = "v2_121_prior_treatment_stress_test_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = {
        component: row["status"] for component, row in evidence.items()
    }
    packet["systematics_budget"]["status"] = (
        "bounded"
        if all(row["status"] == "bounded" for row in evidence.values())
        else "open"
    )
    packet["validation_reference"] = "v2.121_alpha_prior_treatment_stress_test"
    return packet


def evaluate_alpha_prior_treatment_stress_test(
    packet: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    prior = packet["systematics_budget"]["evidence"]["prior_sensitivity"]
    return {
        "prior_sensitivity_bounded": prior["status"] == "bounded",
        "prior_stress_max_best_point_shift": prior["max_best_point_shift"],
        "bounded_components": budget_eval["bounded_components"],
        "open_components": budget_eval["open_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "prior_nuisance_cube_missing",
                "waveform_and_eft_systematics_still_open",
            }
        ),
    }


def diagnose_gw_alpha_prior_treatment_stress_test(
    calibration_bound_path: Path = DEFAULT_CALIBRATION_BOUND_PATH,
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
) -> dict[str, Any]:
    calibration_bound = load_json(calibration_bound_path)
    marginal_result = load_json(marginal_result_path)
    packet = packet_with_prior_treatment_stress_test(
        calibration_bound["packet"],
        marginal_result,
    )
    evaluation = evaluate_alpha_prior_treatment_stress_test(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.120_alpha_detector_calibration_bound",
            "v2.115_lalsuite_marginal_alpha_likelihood",
        ],
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "prior_treatment_stress_test_nonclaiming",
        "selected_next_build_action": "export_per_nuisance_likelihood_cube",
        "best_next_artifact": (
            "Persist the detector-by-detector alpha/nuisance likelihood cube "
            "before marginalization so nuisance priors can be swept directly."
        ),
        "interpretation": (
            "The saved marginal/profile surfaces are enough to prove the current "
            "prior treatment is not bounded: the best alpha point shifts by more "
            "than one alpha-axis grid step as profile weighting is introduced. "
            "The next fix is not another summary proxy; it is a persisted "
            "per-nuisance likelihood cube."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--calibration-bound",
        default=str(DEFAULT_CALIBRATION_BOUND_PATH),
    )
    parser.add_argument("--marginal-result", default=str(DEFAULT_MARGINAL_RESULT_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.121/"
            "gw_alpha_prior_treatment_stress_test.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_prior_treatment_stress_test(
        calibration_bound_path=Path(args.calibration_bound),
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
