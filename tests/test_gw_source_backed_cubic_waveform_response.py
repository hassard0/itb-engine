"""Tests for the v2.109 source-backed cubic waveform response."""

import numpy as np
import pytest

from experiments.gw_source_backed_cubic_waveform_response import (
    ETA_REFERENCE,
    amplitude_pn_coefficients,
    default_vf_grid,
    diagnose_gw_source_backed_cubic_waveform_response,
    evaluate_source_backed_cubic_response,
    phase_pn_coefficients,
    source_backed_cubic_inspiral_response,
    validate_eta,
)


def test_phase_coefficients_match_source_equations():
    eta = ETA_REFERENCE
    coeffs = phase_pn_coefficients(eta)

    assert coeffs["alpha_bar_1"]["a_5pn"] == 0.0
    assert coeffs["alpha_bar_1"]["a_6pn"] == pytest.approx(
        549360.0 / (12544.0 * eta)
    )
    assert coeffs["alpha_bar_2"]["a_5pn"] == pytest.approx(-351.0 / (8.0 * eta))
    assert coeffs["alpha_bar_2"]["a_6pn"] == pytest.approx(
        -45.0 * (43683.0 + 12908.0 * eta) / (12544.0 * eta)
    )


def test_amplitude_coefficients_match_source_equations():
    eta = ETA_REFERENCE
    coeffs = amplitude_pn_coefficients(eta)

    assert coeffs["alpha_bar_1"]["v_10"] == 0.0
    assert coeffs["alpha_bar_1"]["v_12"] == pytest.approx(606.0)
    assert coeffs["alpha_bar_2"]["v_10"] == pytest.approx(-198.0)
    assert coeffs["alpha_bar_2"]["v_12"] == pytest.approx(
        -3.0 * (53149.0 + 16660.0 * eta) / 112.0
    )


def test_response_grid_and_kernels_are_finite_and_monotonic():
    response = source_backed_cubic_inspiral_response()
    grid = np.asarray(response["v_f_grid"])
    phase_1 = np.asarray(response["kernels"]["phase_delta_psi"]["alpha_bar_1"])
    phase_2 = np.asarray(response["kernels"]["phase_delta_psi"]["alpha_bar_2"])
    amp_1 = np.asarray(
        response["kernels"]["relative_amplitude_delta_a_over_a_newt"][
            "alpha_bar_1"
        ]
    )
    amp_2 = np.asarray(
        response["kernels"]["relative_amplitude_delta_a_over_a_newt"][
            "alpha_bar_2"
        ]
    )

    assert np.all(np.diff(grid) > 0.0)
    assert np.isfinite(phase_1).all()
    assert np.isfinite(phase_2).all()
    assert np.isfinite(amp_1).all()
    assert np.isfinite(amp_2).all()
    assert phase_1.shape == grid.shape
    assert phase_2.shape == grid.shape
    assert amp_1.shape == grid.shape
    assert amp_2.shape == grid.shape
    assert response["source_backed"] is True


def test_response_evaluation_ready_but_nonclaiming():
    response = source_backed_cubic_inspiral_response()
    result = evaluate_source_backed_cubic_response(response)

    assert result["response_kernels_ready"] is True
    assert result["claim_ready"] is False
    assert result["response_blockers"] == []
    assert result["removed_v2_108_blocker"] == (
        "alpha_templates_proxy_not_source_backed"
    )
    assert "full_imr_merger_ringdown_response_missing" in result["claim_blockers"]
    assert "psd_whitening_and_calibration_likelihood_missing" in result[
        "claim_blockers"
    ]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_diagnosis_selects_strain_projection_as_next_build():
    result = diagnose_gw_source_backed_cubic_waveform_response()

    assert result["version"] == "v2.109"
    assert result["route_status"] == (
        "source_backed_cubic_inspiral_response_ready_nonclaiming"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "project_source_backed_inspiral_response_onto_conditioned_strain"
    )
    assert result["transition_from_v2_108"]["previous_blocker_removed"] == (
        "alpha_templates_proxy_not_source_backed"
    )


def test_eta_and_grid_validation_reject_unphysical_inputs():
    with pytest.raises(ValueError, match="eta"):
        validate_eta(0.0)
    with pytest.raises(ValueError, match="eta"):
        validate_eta(0.26)
    with pytest.raises(ValueError, match="count"):
        default_vf_grid(count=2)
