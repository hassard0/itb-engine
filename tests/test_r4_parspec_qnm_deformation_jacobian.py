"""Tests for the v2.197 ParSpec qNM deformation Jacobian."""

import json
import math
from pathlib import Path

from experiments.r4_parspec_qnm_deformation_jacobian import (
    ENGINE_AXES,
    QNM_AXES,
    diagnose_r4_parspec_qnm_deformation_jacobian,
    evaluate_qnm_deformation_jacobian,
    malformed_qnm_deformation_jacobian,
    normalized_gamma_derivative,
    normalized_gamma_from_ell,
    qeft_qnm_coefficient_vector,
    qeft_qnm_source_axis_deformation_jacobian,
)


def test_normalized_gamma_uses_qeft_power_six():
    assert normalized_gamma_from_ell(0.0, 51.3) == 0.0
    assert normalized_gamma_from_ell(51.3, 51.3) == 1.0
    assert math.isclose(normalized_gamma_from_ell(25.65, 51.3), 0.5**6)
    assert math.isclose(normalized_gamma_derivative(51.3, 51.3), 6.0 / 51.3)


def test_qnm_coefficient_vector_preserves_source_coefficients():
    coefficients = qeft_qnm_coefficient_vector()

    assert tuple(coefficients) == QNM_AXES
    assert coefficients["delta_omega_qeft_0"] == -0.2114
    assert coefficients["delta_tau_qeft_0"] == -0.607
    assert coefficients["delta_omega_qeft_1"] == -1.5263
    assert coefficients["delta_tau_qeft_1"] == 171.35


def test_qnm_deformation_jacobian_preserves_events_and_engine_blocker():
    bridge = qeft_qnm_source_axis_deformation_jacobian()

    assert [row["label"] for row in bridge["event_deformation_rows"]] == [
        "GW150914",
        "GW200129",
        "combined",
    ]
    assert tuple(bridge["qnm_axes"]) == QNM_AXES
    assert tuple(bridge["engine_axes"]) == ENGINE_AXES
    assert bridge["source_space_jacobian_ready"] is True
    assert bridge["engine_axis_map_ready"] is False
    assert bridge["claim_use_allowed"] is False


def test_published_bound_grid_point_matches_qnm_coefficients():
    bridge = qeft_qnm_source_axis_deformation_jacobian()
    coefficients = bridge["qnm_coefficient_vector"]

    for row in bridge["event_deformation_rows"]:
        bound = next(
            point for point in row["grid"]
            if point["fraction_of_published_bound"] == 1.0
        )
        assert bound["normalized_gamma"] == 1.0
        assert bound["qnm_deformation"] == coefficients


def test_diagnosis_is_ready_in_source_space_but_not_claiming():
    result = diagnose_r4_parspec_qnm_deformation_jacobian()
    evaluation = result["evaluation"]

    assert result["version"] == "v2.197"
    assert result["qnm_source_axis_jacobian_ready"] is True
    assert evaluation["qnm_source_axis_jacobian_ready"] is True
    assert evaluation["engine_axis_map_ready"] is False
    assert "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing" in (
        evaluation["claim_blockers"]
    )
    assert result["claimable_framework_exclusions_now"] == []


def test_malformed_jacobian_rejects_engine_map_and_claim_flag():
    malformed = malformed_qnm_deformation_jacobian()
    evaluation = evaluate_qnm_deformation_jacobian(malformed)

    assert evaluation["qnm_source_axis_jacobian_ready"] is False
    assert "engine_axis_map_unexpectedly_ready" in evaluation["jacobian_blockers"]
    assert "claim_use_not_disabled" in evaluation["jacobian_blockers"]
    assert "GW150914_published_bound_gamma_not_one" in (
        evaluation["jacobian_blockers"]
    )


def test_committed_artifact_records_source_space_jacobian():
    path = Path(
        "experiments/results/v2.197/r4_parspec_qnm_deformation_jacobian.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.197"
    assert result["route_status"] == (
        "parspec_qnm_deformation_jacobian_ready_engine_axis_map_missing"
    )
    assert result["qnm_source_axis_jacobian_ready"] is True
    assert result["evaluation"]["engine_axis_map_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
