"""Convert pyRing EFT imaginary-frequency coefficients to tau deformations."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_pyring_source_probe import (
    PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT,
    PYRING_BRANCH,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_INITIALISE_SOURCE_URL,
    PYRING_QNM_PROBE_AXES,
    PYRING_QUARTIC_THEORIES,
    PYRING_SOURCE_DIRECTIONS,
    PYRING_TREE_URL,
    PYRING_WAVEFORM_SOURCE_URL,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank


VERSION = "v2.202"
DEFAULT_OUT = Path(
    "experiments/results/v2.202/r4_parspec_pyring_tau_axis_jacobian.json"
)

PARSPEC_HIGH_SPIN_TABLE = {
    "filename": "ParSpec_coefficients_high_spin.txt",
    "raw_url": (
        "https://git.ligo.org/lscsoft/pyring/-/raw/EFT_QNMs/"
        "pyRing/data/NR_data/ParSpec_coefficients_high_spin.txt"
    ),
    "sha256": "2948a4ea440b48f29e4abafb5be5e997c1ab120eb1ad5be666c8fdc93cadd256",
    "git_lfs_pointer_blob_sha1": "cea6a57e90acbd608269fa609092384ce1e9d743",
    "data_rows": 4,
    "columns": 19,
}
PARSPEC_TAU0_BY_MODE = {
    "220": 11.240715,
    "221": 3.650769,
}
PYRING_TAU_AXES = (
    "delta_tau_220_n0_spin0",
    "delta_tau_221_n1_spin0",
)
DOMI_ROW_BY_MODE = {
    "220": "domi_220_n0_spin0_pyring_sign",
    "221": "domi_221_n1_spin0_pyring_sign",
}
PARSPEC_TARGET_TAU_AXES = (
    "delta_tau_qeft_0",
    "delta_tau_qeft_1",
)


def exact_fractional_tau_shift(
    *,
    gamma: float,
    tau_gr_dimensionless: float,
    domi_coefficient: float,
) -> float:
    denominator = 1.0 + gamma * tau_gr_dimensionless * domi_coefficient
    if denominator == 0.0:
        raise ValueError("tau shift denominator is zero")
    return (1.0 / denominator) - 1.0


def linearized_fractional_tau_derivative(
    *,
    tau_gr_dimensionless: float,
    domi_coefficient: float,
) -> float:
    return -tau_gr_dimensionless * domi_coefficient


def finite_difference_tau_derivative(
    *,
    tau_gr_dimensionless: float,
    domi_coefficient: float,
    epsilon: float = 1e-7,
) -> float:
    plus = exact_fractional_tau_shift(
        gamma=epsilon,
        tau_gr_dimensionless=tau_gr_dimensionless,
        domi_coefficient=domi_coefficient,
    )
    minus = exact_fractional_tau_shift(
        gamma=-epsilon,
        tau_gr_dimensionless=tau_gr_dimensionless,
        domi_coefficient=domi_coefficient,
    )
    return (plus - minus) / (2.0 * epsilon)


def _domi_coefficients_by_direction(
    snapshot: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float]]:
    domi_220_index = PYRING_QNM_PROBE_AXES.index(DOMI_ROW_BY_MODE["220"])
    domi_221_index = PYRING_QNM_PROBE_AXES.index(DOMI_ROW_BY_MODE["221"])
    return canonicalize_json_floats({
        direction: {
            "domi_220_n0_spin0_pyring_sign": float(
                snapshot[direction]["spin_zero_220_221_vector"][domi_220_index]
            ),
            "domi_221_n1_spin0_pyring_sign": float(
                snapshot[direction]["spin_zero_220_221_vector"][domi_221_index]
            ),
        }
        for direction in PYRING_SOURCE_DIRECTIONS
    })


def pyring_tau_axis_jacobian_matrix(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
    domi = _domi_coefficients_by_direction(snapshot)
    matrix = []
    derivative_checks: list[dict[str, Any]] = []
    for axis, mode in zip(PYRING_TAU_AXES, ("220", "221"), strict=True):
        tau0 = PARSPEC_TAU0_BY_MODE[mode]
        domi_key = DOMI_ROW_BY_MODE[mode]
        row = []
        for direction in PYRING_SOURCE_DIRECTIONS:
            coefficient = domi[direction][domi_key]
            derivative = linearized_fractional_tau_derivative(
                tau_gr_dimensionless=tau0,
                domi_coefficient=coefficient,
            )
            row.append(derivative)
            derivative_checks.append({
                "axis": axis,
                "source_direction": direction,
                "tau_gr_dimensionless_spin0": tau0,
                "domi_coefficient": coefficient,
                "linearized_derivative": derivative,
                "finite_difference_derivative": finite_difference_tau_derivative(
                    tau_gr_dimensionless=tau0,
                    domi_coefficient=coefficient,
                ),
            })
        matrix.append(row)

    return canonicalize_json_floats({
        "matrix_id": "pyring_domi_to_fractional_tau_spin_zero_jacobian_v1",
        "rows": list(PYRING_TAU_AXES),
        "columns": list(PYRING_SOURCE_DIRECTIONS),
        "columns_are_branch_splitting_directions": True,
        "columns_are_independent_operator_axes": False,
        "matrix_kind": "d_fractional_tau_axis_d_pyring_branch_gamma",
        "matrix": matrix,
        "rank": matrix_rank(matrix),
        "required_rank_for_exported_tau_axes": len(PYRING_TAU_AXES),
        "source_formula": (
            "pyRing tau_EFT: tau = 1/(1/tau_GR + gamma*domi_EFT); "
            "therefore d((tau-tau_GR)/tau_GR)/d gamma at gamma=0 = "
            "-tau_GR_dimensionless*domi_fit."
        ),
        "source_scope": (
            "Spin-zero slice for modes (2,2,0) and (2,2,1), using pyRing "
            "EFT_QNMs quartic branch coefficients and ParSpec high-spin tau "
            "table t0 entries."
        ),
        "derivative_checks": derivative_checks,
    })


def evaluate_pyring_tau_axis_jacobian(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
    blockers: set[str] = set()
    for mode, tau0 in PARSPEC_TAU0_BY_MODE.items():
        if not isinstance(tau0, int | float) or not math.isfinite(float(tau0)):
            blockers.add(f"{mode}_tau0_nonfinite")
        elif tau0 <= 0.0:
            blockers.add(f"{mode}_tau0_not_positive")

    jacobian = pyring_tau_axis_jacobian_matrix(snapshot)
    if tuple(jacobian["rows"]) != PYRING_TAU_AXES:
        blockers.add("tau_axis_rows_mismatch")
    if tuple(jacobian["columns"]) != PYRING_SOURCE_DIRECTIONS:
        blockers.add("tau_axis_columns_mismatch")
    if jacobian["rank"] < len(PYRING_TAU_AXES):
        blockers.add("tau_axis_jacobian_rank_deficient")
    if jacobian.get("columns_are_independent_operator_axes") is not False:
        blockers.add("branch_columns_marked_as_operator_axes")

    for check in jacobian["derivative_checks"]:
        if not math.isclose(
            float(check["linearized_derivative"]),
            float(check["finite_difference_derivative"]),
            rel_tol=1e-8,
            abs_tol=1e-8,
        ):
            blockers.add(
                f"{check['axis']}_{check['source_direction']}_finite_diff_mismatch"
            )

    ready = not blockers
    remaining_claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_plus_minus_branches_not_independent_operator_axes",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if not ready:
        remaining_claim_blockers.add("pyring_tau_axis_jacobian_not_ready")

    return canonicalize_json_floats({
        "pyring_imaginary_frequency_to_parspec_tau_jacobian_ready": ready,
        "spin_zero_tau_axis_matrix_ready": ready,
        "qnm_to_bresciani_sensitivity_ready": False,
        "public_likelihood_ready": False,
        "ready_for_framework_claim": False,
        "source_intake_blockers": sorted(blockers),
        "resolved_v2201_subpieces": (
            ["pyring_imaginary_frequency_to_parspec_tau_jacobian_defined"]
            if ready
            else []
        ),
        "remaining_claim_blockers": sorted(remaining_claim_blockers),
        "route_status": (
            "pyring_tau_axis_jacobian_ready_bresciani_map_missing"
            if ready
            else "pyring_tau_axis_jacobian_not_ready"
        ),
    })


def malformed_pyring_tau_snapshot() -> dict[str, dict[str, Any]]:
    snapshot = copy.deepcopy(PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT)
    for direction in PYRING_SOURCE_DIRECTIONS:
        vector = list(snapshot[direction]["spin_zero_220_221_vector"])
        vector[1] = 0.0
        vector[3] = 0.0
        snapshot[direction]["spin_zero_220_221_vector"] = vector
    return snapshot


def diagnose_r4_parspec_pyring_tau_axis_jacobian() -> dict[str, Any]:
    jacobian = pyring_tau_axis_jacobian_matrix()
    evaluation = evaluate_pyring_tau_axis_jacobian()
    malformed_evaluation = evaluate_pyring_tau_axis_jacobian(
        malformed_pyring_tau_snapshot()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.200_parspec_qnm_to_bresciani_gate",
            "v2.201_pyring_source_probe",
            "public_pyring_EFT_QNMs_branch",
        ],
        "source_manifest": {
            "branch": PYRING_BRANCH,
            "branch_head_sha": PYRING_BRANCH_HEAD_SHA,
            "tree_url": PYRING_TREE_URL,
            "waveform_source_url": PYRING_WAVEFORM_SOURCE_URL,
            "initialise_source_url": PYRING_INITIALISE_SOURCE_URL,
            "parspec_high_spin_table": PARSPEC_HIGH_SPIN_TABLE,
            "source_line_refs": {
                "pyring_domi_sign_flip": "waveform.pyx:78-80",
                "pyring_tau_eft_formula": "waveform.pyx:534-540",
                "parspec_tau_fractional_form": "waveform.pyx:342-355",
                "tgr_dtau_fractional_use": "initialise.py:994-995",
            },
        },
        "engine_target_axes": list(ENGINE_AXES),
        "parspec_qnm_axes": list(QNM_AXES),
        "parspec_target_tau_axes": list(PARSPEC_TARGET_TAU_AXES),
        "pyring_tau_axes": list(PYRING_TAU_AXES),
        "pyring_quartic_theories": list(PYRING_QUARTIC_THEORIES),
        "pyring_source_directions": list(PYRING_SOURCE_DIRECTIONS),
        "parspec_tau0_by_mode": PARSPEC_TAU0_BY_MODE,
        "domi_coefficients_by_direction": _domi_coefficients_by_direction(
            PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT
        ),
        "tau_axis_jacobian": jacobian,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed_evaluation,
        "pyring_imaginary_frequency_to_parspec_tau_jacobian_ready": evaluation[
            "pyring_imaginary_frequency_to_parspec_tau_jacobian_ready"
        ],
        "qnm_to_bresciani_sensitivity_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_pyring_quartic_direction_to_bresciani_axis_orientation_or_"
            "obtain_public_parspec_likelihood"
        ),
        "route_status": evaluation["route_status"],
        "interpretation": (
            "v2.202 converts pyRing's imaginary-frequency coefficients into "
            "fractional damping-time deformation axes at the linearized "
            "source level. The formula is source-backed by pyRing's tau_EFT "
            "implementation and the ParSpec fractional dtau convention. The "
            "route remains nonclaiming because plus/minus are branch-splitting "
            "columns, not independent Bresciani operator axes, and no "
            "qNM-to-Bresciani map or public likelihood is attached."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_tau_axis_jacobian()
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
