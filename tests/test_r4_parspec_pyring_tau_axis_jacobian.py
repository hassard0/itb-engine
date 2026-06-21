"""Tests for the v2.202 pyRing imaginary-frequency to tau-axis Jacobian."""

from __future__ import annotations

import json
import math

from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH_HEAD_SHA,
    PYRING_SOURCE_DIRECTIONS,
)
from experiments.r4_parspec_pyring_tau_axis_jacobian import (
    DEFAULT_OUT,
    PARSPEC_HIGH_SPIN_TABLE,
    PARSPEC_TAU0_BY_MODE,
    PYRING_TAU_AXES,
    diagnose_r4_parspec_pyring_tau_axis_jacobian,
    evaluate_pyring_tau_axis_jacobian,
    exact_fractional_tau_shift,
    finite_difference_tau_derivative,
    linearized_fractional_tau_derivative,
    malformed_pyring_tau_snapshot,
    pyring_tau_axis_jacobian_matrix,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES


def test_source_table_manifest_is_pinned() -> None:
    result = diagnose_r4_parspec_pyring_tau_axis_jacobian()
    manifest = result["source_manifest"]

    assert manifest["branch_head_sha"] == PYRING_BRANCH_HEAD_SHA
    assert manifest["parspec_high_spin_table"] == PARSPEC_HIGH_SPIN_TABLE
    assert len(PARSPEC_HIGH_SPIN_TABLE["sha256"]) == 64
    assert len(PARSPEC_HIGH_SPIN_TABLE["git_lfs_pointer_blob_sha1"]) == 40
    assert manifest["source_line_refs"]["pyring_tau_eft_formula"] == (
        "waveform.pyx:534-540"
    )


def test_linearized_tau_derivative_matches_finite_difference() -> None:
    tau0 = PARSPEC_TAU0_BY_MODE["220"]
    domi = 0.057608
    expected = -0.64755510972

    assert math.isclose(
        linearized_fractional_tau_derivative(
            tau_gr_dimensionless=tau0,
            domi_coefficient=domi,
        ),
        expected,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        finite_difference_tau_derivative(
            tau_gr_dimensionless=tau0,
            domi_coefficient=domi,
        ),
        expected,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
    assert exact_fractional_tau_shift(
        gamma=1e-5,
        tau_gr_dimensionless=tau0,
        domi_coefficient=domi,
    ) < 0.0


def test_tau_axis_jacobian_matrix_shape_rank_and_known_values() -> None:
    jacobian = pyring_tau_axis_jacobian_matrix()

    assert jacobian["rows"] == list(PYRING_TAU_AXES)
    assert jacobian["columns"] == list(PYRING_SOURCE_DIRECTIONS)
    assert len(jacobian["matrix"]) == 2
    assert all(len(row) == 6 for row in jacobian["matrix"])
    assert jacobian["rank"] == 2
    assert jacobian["required_rank_for_exported_tau_axes"] == 2
    assert jacobian["columns_are_branch_splitting_directions"] is True
    assert jacobian["columns_are_independent_operator_axes"] is False

    first_row = jacobian["matrix"][0]
    second_row = jacobian["matrix"][1]
    assert math.isclose(first_row[0], -0.64755510972, abs_tol=1e-12)
    assert math.isclose(first_row[1], -2.746882283835, abs_tol=1e-12)
    assert math.isclose(second_row[0], 1.727967380004, abs_tol=1e-12)
    assert math.isclose(second_row[1], -4.49460774666, abs_tol=1e-12)


def test_evaluation_resolves_tau_subpiece_but_keeps_claim_gate_closed() -> None:
    evaluation = evaluate_pyring_tau_axis_jacobian()

    assert evaluation["pyring_imaginary_frequency_to_parspec_tau_jacobian_ready"]
    assert evaluation["spin_zero_tau_axis_matrix_ready"] is True
    assert evaluation["qnm_to_bresciani_sensitivity_ready"] is False
    assert evaluation["public_likelihood_ready"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["source_intake_blockers"] == []
    assert evaluation["resolved_v2201_subpieces"] == [
        "pyring_imaginary_frequency_to_parspec_tau_jacobian_defined"
    ]
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in evaluation[
        "remaining_claim_blockers"
    ]
    assert "pyring_plus_minus_branches_not_independent_operator_axes" in evaluation[
        "remaining_claim_blockers"
    ]


def test_malformed_zero_domi_snapshot_fails_rank_gate() -> None:
    evaluation = evaluate_pyring_tau_axis_jacobian(
        malformed_pyring_tau_snapshot()
    )

    assert evaluation["pyring_imaginary_frequency_to_parspec_tau_jacobian_ready"] is False
    assert evaluation["spin_zero_tau_axis_matrix_ready"] is False
    assert "tau_axis_jacobian_rank_deficient" in evaluation["source_intake_blockers"]
    assert "pyring_tau_axis_jacobian_not_ready" in evaluation[
        "remaining_claim_blockers"
    ]


def test_diagnosis_preserves_axis_boundaries_and_nonclaiming_status() -> None:
    result = diagnose_r4_parspec_pyring_tau_axis_jacobian()

    assert result["version"] == "v2.202"
    assert tuple(result["engine_target_axes"]) == ENGINE_AXES
    assert tuple(result["parspec_qnm_axes"]) == QNM_AXES
    assert result["pyring_tau_axes"] == list(PYRING_TAU_AXES)
    assert result["tau_axis_jacobian"]["rank"] == 2
    assert result["pyring_imaginary_frequency_to_parspec_tau_jacobian_ready"]
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False


def test_committed_artifact_matches_tau_axis_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.202"
    assert artifact["route_status"] == (
        "pyring_tau_axis_jacobian_ready_bresciani_map_missing"
    )
    assert artifact["pyring_imaginary_frequency_to_parspec_tau_jacobian_ready"]
    assert artifact["tau_axis_jacobian"]["rank"] == 2
    assert artifact["ready_for_framework_claim"] is False
