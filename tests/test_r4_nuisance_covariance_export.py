"""Tests for the v2.186 R4 nuisance covariance export."""

import numpy as np

from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES
from experiments.r4_nuisance_covariance_export import (
    AXES,
    DEFAULT_CALIBRATED_PROJECTION_PATH,
    diagnose_r4_nuisance_covariance_export,
    evaluate_r4_nuisance_covariance_export,
    load_json,
    malformed_r4_nuisance_covariance_result,
    nuisance_covariance_export,
    nuisance_shifted_r4_points,
    r4_nuisance_shift,
)


def _packet():
    return load_json(DEFAULT_CALIBRATED_PROJECTION_PATH)["projected_packet"]


def test_reference_nuisance_point_has_zero_shift():
    shift = r4_nuisance_shift({
        "total_mass_solar": 19.0,
        "eta": 0.22,
        "tc_shift_seconds": 0.0,
        "phic_rad": 0.0,
    })

    assert set(shift) == set(RESPONSE_AXES)
    assert all(value == 0.0 for value in shift.values())


def test_nuisance_shifted_points_preserve_r4_axes_and_count():
    rows = nuisance_shifted_r4_points(_packet())

    assert len(rows) == 81
    assert set(rows[0]["central_values"]) == set(AXES)
    assert set(rows[0]["r4_shift"]) == set(AXES)


def test_nuisance_covariance_export_is_positive_definite():
    export = nuisance_covariance_export(_packet())

    assert export["nuisance_grid"]["points"] == 81
    assert export["nuisance_grid"]["grid_is_posterior_sampler"] is False
    assert export["positive_definite"] is True
    assert export["axes"] == list(RESPONSE_AXES)
    covariance = np.asarray(export["exported_covariance"], dtype=float)
    assert covariance.shape == (3, 3)
    assert np.all(np.linalg.eigvalsh(covariance) > 0.0)


def test_nuisance_covariance_evaluation_removes_export_blocker():
    result = diagnose_r4_nuisance_covariance_export()
    evaluation = result["evaluation"]

    assert result["version"] == "v2.186"
    assert result["export_ready"] is True
    assert evaluation["export_ready"] is True
    assert evaluation["removed_v2_185_blocker"] == (
        "nuisance_marginalized_covariance_not_exported"
    )
    assert "nuisance_grid_is_coarse_not_posterior_sampler" in (
        evaluation["claim_blockers"]
    )
    assert evaluation["ready_for_framework_claim"] is False


def test_malformed_nuisance_covariance_rejects_shape_and_covariance():
    malformed = malformed_r4_nuisance_covariance_result()
    evaluation = evaluate_r4_nuisance_covariance_export(malformed)

    assert evaluation["export_ready"] is False
    assert "nuisance_grid_point_count_unexpected" in evaluation["export_blockers"]
    assert "exported_covariance_not_positive_definite" in (
        evaluation["export_blockers"]
    )


def test_diagnosis_selects_real_r4_likelihood_next():
    result = diagnose_r4_nuisance_covariance_export()

    assert result["route_status"] == (
        "r4_nuisance_covariance_export_ready_nonclaiming"
    )
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["selected_next_build_action"] == (
        "replace_coarse_nuisance_covariance_with_r4_waveform_likelihood"
    )
