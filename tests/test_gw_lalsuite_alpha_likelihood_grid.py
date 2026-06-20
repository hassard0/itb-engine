"""Tests for the v2.114 LALSuite alpha likelihood grid."""

import importlib

import numpy as np
import pytest

from experiments.gw_lalsuite_alpha_likelihood_grid import (
    GRID_POINTS_PER_AXIS,
    alpha_grid,
    detector_alpha_likelihood_grid,
    evaluate_lalsuite_alpha_likelihood_grid,
    fixed_parameter_log_likelihood,
    real_alpha_least_squares,
)
from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ


def _synthetic_32s_strain() -> np.ndarray:
    times = np.arange(32 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    signal = 1.0e-21 * np.sin(2.0 * np.pi * 35.0 * times)
    signal += 4.0e-22 * np.sin(2.0 * np.pi * 90.0 * times)
    signal += 1.0e-22 * np.cos(2.0 * np.pi * 180.0 * times)
    return signal


def _skip_without_lalsuite():
    if (
        importlib.util.find_spec("lal") is None
        or importlib.util.find_spec("lalsimulation") is None
    ):
        pytest.skip("LALSuite optional dependency is not installed")


def test_alpha_grid_is_square_and_centered():
    grid = alpha_grid(points_per_axis=5, half_width=0.2)

    assert len(grid) == 25
    assert grid[0] == {"alpha_bar_1": -0.2, "alpha_bar_2": -0.2}
    assert grid[-1] == {"alpha_bar_1": 0.2, "alpha_bar_2": 0.2}
    assert {"alpha_bar_1": 0.0, "alpha_bar_2": 0.0} in grid


def test_real_alpha_least_squares_recovers_simple_signal():
    template_1 = np.array([1.0 + 0.0j, 0.0 + 1.0j])
    template_2 = np.array([0.0 + 1.0j, 1.0 + 0.0j])
    data = 0.3 * template_1 - 0.1 * template_2
    result = real_alpha_least_squares(
        data,
        {"alpha_bar_1": template_1, "alpha_bar_2": template_2},
    )

    assert result["alpha_bar_1_hat"] == pytest.approx(0.3)
    assert result["alpha_bar_2_hat"] == pytest.approx(-0.1)


def test_fixed_parameter_log_likelihood_prefers_matching_alpha():
    template_1 = np.array([1.0 + 0.0j, 0.0 + 1.0j])
    template_2 = np.array([0.0 + 1.0j, 1.0 + 0.0j])
    templates = {"alpha_bar_1": template_1, "alpha_bar_2": template_2}
    data = 0.1 * template_1 + 0.2 * template_2

    matched = fixed_parameter_log_likelihood(
        data,
        templates,
        alpha_bar_1=0.1,
        alpha_bar_2=0.2,
    )
    shifted = fixed_parameter_log_likelihood(
        data,
        templates,
        alpha_bar_1=0.0,
        alpha_bar_2=0.0,
    )

    assert matched > shifted


def test_evaluation_ready_for_complete_fake_grid_when_lalsuite_available():
    _skip_without_lalsuite()
    rows = [
        {"detector": "H1", "likelihood_ready": True},
        {"detector": "L1", "likelihood_ready": True},
    ]
    network = {"grid_points": GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS}

    result = evaluate_lalsuite_alpha_likelihood_grid(rows, network)

    assert result["fixed_alpha_likelihood_grid_ready"] is True
    assert result["claim_ready"] is False
    assert result["likelihood_blockers"] == []
    assert result["removed_v2_113_blocker"] == "alpha_likelihood_grid_not_sampled"


def test_detector_alpha_likelihood_grid_runs_with_lalsuite():
    _skip_without_lalsuite()
    result = detector_alpha_likelihood_grid(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )

    assert result["likelihood_ready"] is True
    assert result["grid_points"] == GRID_POINTS_PER_AXIS * GRID_POINTS_PER_AXIS
    assert np.isfinite(result["best_grid_point"]["log_likelihood"])
    assert result["waveform_summary"]["approximant"] == "IMRPhenomD"
