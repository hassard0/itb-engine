"""Source-backed cubic EFT inspiral response kernels for v2.109."""

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


VERSION = "v2.109"
SOURCE_REFERENCE = "https://arxiv.org/abs/2407.08929"
SOURCE_MODEL = "cubic_parity_preserving_higher_curvature_eft"
PARAMETERS = ("alpha_bar_1", "alpha_bar_2")
ETA_REFERENCE = 0.22
VF_GRID_MIN = 0.08
VF_GRID_MAX = 0.32
VF_GRID_COUNT = 129


def validate_eta(eta: float) -> float:
    eta_value = float(eta)
    if not math.isfinite(eta_value) or eta_value <= 0.0 or eta_value > 0.25:
        raise ValueError("eta must be finite and in the physical interval (0, 0.25]")
    return eta_value


def default_vf_grid(
    *,
    count: int = VF_GRID_COUNT,
    minimum: float = VF_GRID_MIN,
    maximum: float = VF_GRID_MAX,
) -> np.ndarray:
    if count < 3:
        raise ValueError("count must be at least 3")
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise ValueError("grid bounds must be finite")
    if minimum <= 0.0 or minimum >= maximum:
        raise ValueError("grid must satisfy 0 < minimum < maximum")
    return np.linspace(float(minimum), float(maximum), int(count))


def phase_pn_coefficients(eta: float = ETA_REFERENCE) -> dict[str, dict[str, float]]:
    eta_value = validate_eta(eta)
    return {
        "alpha_bar_1": {
            "a_5pn": 0.0,
            "a_6pn": 549360.0 / (12544.0 * eta_value),
        },
        "alpha_bar_2": {
            "a_5pn": -351.0 / (8.0 * eta_value),
            "a_6pn": -45.0
            * (43683.0 + 12908.0 * eta_value)
            / (12544.0 * eta_value),
        },
    }


def amplitude_pn_coefficients(eta: float = ETA_REFERENCE) -> dict[str, dict[str, float]]:
    eta_value = validate_eta(eta)
    return {
        "alpha_bar_1": {
            "v_10": 0.0,
            "v_12": 3.0 * 22624.0 / 112.0,
        },
        "alpha_bar_2": {
            "v_10": -198.0,
            "v_12": -3.0 * (53149.0 + 16660.0 * eta_value) / 112.0,
        },
    }


def phase_response_kernels(
    v_f: np.ndarray,
    eta: float = ETA_REFERENCE,
) -> dict[str, np.ndarray]:
    coeffs = phase_pn_coefficients(eta)
    grid = np.asarray(v_f, dtype=float)
    return {
        "alpha_bar_1": (
            coeffs["alpha_bar_1"]["a_5pn"] * grid**5
            + coeffs["alpha_bar_1"]["a_6pn"] * grid**7
        ),
        "alpha_bar_2": (
            coeffs["alpha_bar_2"]["a_5pn"] * grid**5
            + coeffs["alpha_bar_2"]["a_6pn"] * grid**7
        ),
    }


def amplitude_response_kernels(
    v_f: np.ndarray,
    eta: float = ETA_REFERENCE,
) -> dict[str, np.ndarray]:
    coeffs = amplitude_pn_coefficients(eta)
    grid = np.asarray(v_f, dtype=float)
    return {
        "alpha_bar_1": (
            coeffs["alpha_bar_1"]["v_10"] * grid**10
            + coeffs["alpha_bar_1"]["v_12"] * grid**12
        ),
        "alpha_bar_2": (
            coeffs["alpha_bar_2"]["v_10"] * grid**10
            + coeffs["alpha_bar_2"]["v_12"] * grid**12
        ),
    }


def _as_floats(values: np.ndarray) -> list[float]:
    return [float(value) for value in np.asarray(values, dtype=float)]


def _kernel_summary(values: np.ndarray) -> dict[str, float]:
    kernel = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(kernel)),
        "max": float(np.max(kernel)),
        "l2_norm": float(np.linalg.norm(kernel)),
        "mean": float(np.mean(kernel)),
        "first": float(kernel[0]),
        "last": float(kernel[-1]),
    }


def _kernel_correlation(left: np.ndarray, right: np.ndarray) -> float:
    left_centered = np.asarray(left, dtype=float) - float(np.mean(left))
    right_centered = np.asarray(right, dtype=float) - float(np.mean(right))
    denom = float(np.linalg.norm(left_centered) * np.linalg.norm(right_centered))
    if denom == 0.0:
        return 0.0
    return float(np.dot(left_centered, right_centered) / denom)


def source_backed_cubic_inspiral_response(
    *,
    eta: float = ETA_REFERENCE,
    v_f: np.ndarray | None = None,
) -> dict[str, Any]:
    eta_value = validate_eta(eta)
    grid = default_vf_grid() if v_f is None else np.asarray(v_f, dtype=float)
    if grid.ndim != 1 or grid.size < 3:
        raise ValueError("v_f must be a one-dimensional grid with at least 3 points")
    if not np.all(np.isfinite(grid)) or not np.all(np.diff(grid) > 0.0):
        raise ValueError("v_f grid must be finite and strictly increasing")
    if float(grid[0]) <= 0.0:
        raise ValueError("v_f grid must be positive")

    phase = phase_response_kernels(grid, eta_value)
    amplitude = amplitude_response_kernels(grid, eta_value)
    phase_summary = {
        parameter: _kernel_summary(values) for parameter, values in phase.items()
    }
    amplitude_summary = {
        parameter: _kernel_summary(values) for parameter, values in amplitude.items()
    }
    phase_summary["alpha_kernel_correlation"] = _kernel_correlation(
        phase["alpha_bar_1"],
        phase["alpha_bar_2"],
    )
    amplitude_summary["alpha_kernel_correlation"] = _kernel_correlation(
        amplitude["alpha_bar_1"],
        amplitude["alpha_bar_2"],
    )

    return {
        "source_backed": True,
        "source_reference": SOURCE_REFERENCE,
        "source_model": SOURCE_MODEL,
        "response_scope": (
            "linearized_frequency_domain_inspiral_phase_and_relative_amplitude"
        ),
        "parameters": list(PARAMETERS),
        "eta": eta_value,
        "v_f_grid": _as_floats(grid),
        "source_equation_refs": {
            "phase": [
                "Eq. phase_EFT",
                "Eq. aPN_EFT",
                "Eq. aPN_EFT_2",
            ],
            "amplitude": ["Eq. amp_EFT"],
            "normalization": "dimensionless_alpha_bar_1_alpha_bar_2",
        },
        "pn_coefficients": {
            "phase_delta_psi": phase_pn_coefficients(eta_value),
            "relative_amplitude_delta_a_over_a_newt": amplitude_pn_coefficients(
                eta_value
            ),
        },
        "kernels": {
            "phase_delta_psi": {
                parameter: _as_floats(values) for parameter, values in phase.items()
            },
            "relative_amplitude_delta_a_over_a_newt": {
                parameter: _as_floats(values)
                for parameter, values in amplitude.items()
            },
        },
        "kernel_summary": {
            "phase_delta_psi": phase_summary,
            "relative_amplitude_delta_a_over_a_newt": amplitude_summary,
        },
    }


def evaluate_source_backed_cubic_response(
    response: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    if response.get("source_reference") != SOURCE_REFERENCE:
        blockers.add("source_reference_missing_or_unexpected")
    if response.get("source_model") != SOURCE_MODEL:
        blockers.add("source_model_missing_or_unexpected")
    if response.get("source_backed") is not True:
        blockers.add("response_not_marked_source_backed")

    grid = np.asarray(response.get("v_f_grid", []), dtype=float)
    if grid.ndim != 1 or grid.size < 3:
        blockers.add("vf_grid_missing_or_too_short")
    elif not np.all(np.isfinite(grid)) or not np.all(np.diff(grid) > 0.0):
        blockers.add("vf_grid_not_finite_and_monotonic")

    kernels = response.get("kernels")
    if not isinstance(kernels, dict):
        blockers.add("kernels_missing")
    else:
        for family in (
            "phase_delta_psi",
            "relative_amplitude_delta_a_over_a_newt",
        ):
            family_rows = kernels.get(family)
            if not isinstance(family_rows, dict):
                blockers.add(f"{family}_kernels_missing")
                continue
            for parameter in PARAMETERS:
                values = np.asarray(family_rows.get(parameter, []), dtype=float)
                if values.shape != grid.shape or not np.all(np.isfinite(values)):
                    blockers.add(f"{family}_{parameter}_kernel_invalid")

    coeffs = response.get("pn_coefficients")
    if not isinstance(coeffs, dict):
        blockers.add("pn_coefficients_missing")
    else:
        phase = coeffs.get("phase_delta_psi", {})
        amplitude = coeffs.get("relative_amplitude_delta_a_over_a_newt", {})
        if phase.get("alpha_bar_1", {}).get("a_5pn") != 0.0:
            blockers.add("alpha_bar_1_phase_5pn_term_should_be_zero")
        if not phase.get("alpha_bar_2", {}).get("a_5pn"):
            blockers.add("alpha_bar_2_phase_5pn_term_missing")
        if amplitude.get("alpha_bar_1", {}).get("v_12") != 606.0:
            blockers.add("alpha_bar_1_amplitude_12pn_coefficient_unexpected")
        if not amplitude.get("alpha_bar_2", {}).get("v_10"):
            blockers.add("alpha_bar_2_amplitude_10pn_term_missing")

    claim_blockers = set(blockers)
    claim_blockers.update(
        {
            "frequency_domain_to_strain_projection_missing",
            "full_imr_merger_ringdown_response_missing",
            "psd_whitening_and_calibration_likelihood_missing",
            "event_mass_eta_posterior_sampling_missing",
            "posterior_sampler_and_systematics_budget_missing",
            "g8_joint_component_missing",
        }
    )

    return {
        "response_kernels_ready": not blockers,
        "claim_ready": False,
        "response_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "removed_v2_108_blocker": (
            "alpha_templates_proxy_not_source_backed" if not blockers else None
        ),
        "remaining_projection_scope": (
            "source_backed_inspiral_response_not_yet_projected_to_public_strain"
        ),
    }


def diagnose_gw_source_backed_cubic_waveform_response() -> dict[str, Any]:
    response = source_backed_cubic_inspiral_response()
    evaluation = evaluate_source_backed_cubic_response(response)
    return {
        "version": VERSION,
        "basis": [
            "v2.108_public_strain_alpha_proxy_projection",
            "v2.102_source_native_alpha_adapter",
            "Liu_Yunes_2024_cubic_EFT_inspiral_phase_amplitude_equations",
        ],
        "source_reference": SOURCE_REFERENCE,
        "response": response,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "source_backed_cubic_inspiral_response_ready_nonclaiming"
            if evaluation["response_kernels_ready"]
            else "source_backed_cubic_inspiral_response_not_ready"
        ),
        "selected_next_build_action": (
            "project_source_backed_inspiral_response_onto_conditioned_strain"
        ),
        "best_next_artifact": (
            "Map the dimensionless v_f response kernels through the GW170608 "
            "mass-ratio/posterior context, PSD-whiten the public H1/L1 strain, "
            "and replace the v2.108 proxy dot-products with source-backed "
            "frequency-domain residual projections."
        ),
        "transition_from_v2_108": {
            "previous_blocker_removed": evaluation["removed_v2_108_blocker"],
            "previous_proxy_status": (
                "deterministic_proxy_not_source_backed_eft_waveform"
            ),
            "new_status": (
                "source_backed_inspiral_phase_and_amplitude_response_kernels"
            ),
            "still_nonclaiming_until": [
                "mass_eta_frequency_mapping",
                "calibrated_frequency_domain_strain_projection",
                "full_imr_merger_ringdown_or_justified_inspiral_window",
                "posterior_likelihood_export",
                "g8_joint_component",
            ],
        },
        "interpretation": (
            "The alpha response basis is no longer an arbitrary proxy: it is "
            "built from the source paper's cubic-EFT inspiral phase and "
            "relative-amplitude corrections for alpha_bar_1 and alpha_bar_2. "
            "This is still not an alpha_bar likelihood because the kernels have "
            "not been mapped through detector PSD/calibration, event mass and "
            "eta uncertainty, merger-ringdown treatment, or the source-native "
            "posterior packet gate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.109/"
            "gw_source_backed_cubic_waveform_response.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_source_backed_cubic_waveform_response()
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
