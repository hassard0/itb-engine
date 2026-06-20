"""Tests for the v2.115 nuisance-marginal alpha likelihood."""

import importlib

import numpy as np
import pytest

from experiments.gw_lalsuite_marginal_alpha_likelihood import (
    PHIC_RAD_GRID,
    TC_SHIFT_SECONDS_GRID,
    detector_marginal_alpha_likelihood,
    evaluate_lalsuite_marginal_alpha_likelihood,
    logsumexp,
    marginalize_alpha_grid_from_packets,
    nuisance_grid,
    rotate_templates_for_tc_phic,
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


def test_nuisance_grid_covers_mass_eta_time_and_phase():
    grid = nuisance_grid()

    assert len(grid) == 81
    assert {row["tc_shift_seconds"] for row in grid} == set(TC_SHIFT_SECONDS_GRID)
    assert {row["phic_rad"] for row in grid} == set(PHIC_RAD_GRID)
    assert any(
        row["total_mass_solar"] == 19.0
        and row["eta"] == 0.22
        and row["tc_shift_seconds"] == 0.0
        and row["phic_rad"] == 0.0
        for row in grid
    )


def test_logsumexp_is_stable_for_large_negative_values():
    result = logsumexp(np.array([-1000.0, -1000.0]))

    assert result == pytest.approx(-1000.0 + np.log(2.0))


def test_rotate_templates_preserves_unit_norms():
    frequencies = np.array([20.0, 20.25, 20.5])
    templates = {
        "alpha_bar_1": np.array([1.0 + 0.0j, 0.0 + 1.0j, 1.0 + 1.0j]),
        "alpha_bar_2": np.array([0.5 + 0.5j, 1.0 + 0.0j, 0.0 + 1.0j]),
    }
    rotated = rotate_templates_for_tc_phic(
        templates,
        frequencies,
        tc_shift_seconds=0.001,
        phic_rad=0.2,
    )

    assert sorted(rotated) == ["alpha_bar_1", "alpha_bar_2"]
    for template in rotated.values():
        assert np.linalg.norm(template) == pytest.approx(1.0)


def test_marginalize_alpha_grid_from_packets_prefers_matching_signal():
    template_1 = np.array([1.0 + 0.0j, 0.0 + 1.0j])
    template_2 = np.array([0.0 + 1.0j, 1.0 + 0.0j])
    data = 0.2 * template_1
    packets = [
        {
            "data": data,
            "templates": {"alpha_bar_1": template_1, "alpha_bar_2": template_2},
            "nuisance": {"case": 1},
        },
        {
            "data": data,
            "templates": {"alpha_bar_1": template_1, "alpha_bar_2": template_2},
            "nuisance": {"case": 2},
        },
    ]
    grid = [
        {"alpha_bar_1": 0.0, "alpha_bar_2": 0.0},
        {"alpha_bar_1": 0.2, "alpha_bar_2": 0.0},
    ]

    result = marginalize_alpha_grid_from_packets(packets, grid=grid)

    assert result["grid_points"] == 2
    assert result["nuisance_points"] == 2
    assert result["best_marginal_grid_point"]["alpha_bar_1"] == pytest.approx(0.2)


def test_evaluation_ready_for_complete_fake_marginals_when_lalsuite_available():
    _skip_without_lalsuite()
    rows = [
        {"detector": "H1", "likelihood_ready": True},
        {"detector": "L1", "likelihood_ready": True},
    ]
    network = {"grid_points": 21 * 21}

    result = evaluate_lalsuite_marginal_alpha_likelihood(rows, network)

    assert result["marginal_alpha_likelihood_ready"] is True
    assert result["claim_ready"] is False
    assert result["likelihood_blockers"] == []
    assert result["removed_v2_114_blocker"] == (
        "event_mass_eta_tc_phic_fixed_not_marginalized"
    )


def test_detector_marginal_alpha_likelihood_runs_with_lalsuite():
    _skip_without_lalsuite()
    result = detector_marginal_alpha_likelihood(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )

    assert result["likelihood_ready"] is True
    assert result["nuisance_grid"]["nuisance_points"] == 81
    assert result["alpha_grid"]["grid_points"] == 21 * 21
    assert np.isfinite(
        result["best_marginal_grid_point"]["log_marginal_likelihood"]
    )
