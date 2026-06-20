"""Tests for the v2.187 R4 waveform-likelihood posterior bridge."""

import json
from pathlib import Path

import numpy as np
import pytest

from experiments.r4_lalsuite_waveform_likelihood_posterior import (
    AXES,
    GRID_OFFSETS,
    evaluate_r4_lalsuite_waveform_likelihood_posterior,
    marginalize_r4_grid_from_packets,
    network_r4_waveform_likelihood,
    posterior_summary_from_grid,
    r4_coefficient_grid,
    r4_fixed_parameter_log_likelihood,
)


def _central_values() -> dict[str, float]:
    return {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.49,
        "g_R4_c3": -0.01,
    }


def _templates() -> dict[str, np.ndarray]:
    return {
        "g_R4_c1": np.array([1.0 + 0.0j, 0.0 + 0.0j]),
        "g_R4_c2": np.array([0.0 + 0.0j, 1.0 + 0.0j]),
        "g_R4_c3": np.array([0.0 + 1.0j, 0.0 + 0.0j]),
    }


def test_r4_coefficient_grid_is_centered_and_three_dimensional():
    grid = r4_coefficient_grid(_central_values())

    assert len(grid) == len(GRID_OFFSETS) ** len(AXES)
    assert {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.49,
        "g_R4_c3": -0.01,
        "delta_g_R4_c1": 0.0,
        "delta_g_R4_c2": 0.0,
        "delta_g_R4_c3": 0.0,
    } in grid


def test_r4_fixed_parameter_log_likelihood_prefers_matching_delta():
    central = _central_values()
    data = 0.02 * _templates()["g_R4_c1"]
    matched = dict(central)
    matched["g_R4_c1"] += 0.02

    matched_ll = r4_fixed_parameter_log_likelihood(
        data,
        _templates(),
        matched,
        central_values=central,
    )
    center_ll = r4_fixed_parameter_log_likelihood(
        data,
        _templates(),
        central,
        central_values=central,
    )

    assert matched_ll > center_ll


def test_marginalize_r4_grid_from_packets_prefers_matching_point():
    central = _central_values()
    matched = dict(central)
    matched["g_R4_c1"] += 0.02
    packets = [
        {
            "data": 0.02 * _templates()["g_R4_c1"],
            "templates": _templates(),
            "nuisance": {"case": 1},
        },
        {
            "data": 0.02 * _templates()["g_R4_c1"],
            "templates": _templates(),
            "nuisance": {"case": 2},
        },
    ]
    grid = [central, matched]

    result = marginalize_r4_grid_from_packets(packets, central, grid=grid)

    assert result["grid_points"] == 2
    assert result["nuisance_points"] == 2
    assert result["best_marginal_grid_point"]["g_R4_c1"] == pytest.approx(
        matched["g_R4_c1"]
    )


def test_posterior_summary_normalizes_weights_and_covariance():
    rows = [
        {
            "g_R4_c1": 0.48,
            "g_R4_c2": 0.49,
            "g_R4_c3": -0.01,
            "log_marginal_likelihood": -1.0,
        },
        {
            "g_R4_c1": 0.5,
            "g_R4_c2": 0.49,
            "g_R4_c3": -0.01,
            "log_marginal_likelihood": 0.0,
        },
        {
            "g_R4_c1": 0.52,
            "g_R4_c2": 0.49,
            "g_R4_c3": -0.01,
            "log_marginal_likelihood": -1.0,
        },
    ]

    result = posterior_summary_from_grid(rows)

    assert result["posterior_normalized"] is True
    assert result["posterior_weight_sum"] == pytest.approx(1.0)
    assert result["posterior_positive_semidefinite"] is True
    assert result["maximum_posterior_grid_point"]["g_R4_c1"] == pytest.approx(0.5)


def test_network_likelihood_combines_detector_rows():
    central = _central_values()
    rows = []
    for detector in ("H1", "L1"):
        rows.append({
            "detector": detector,
            "nuisance_grid": {"nuisance_points": 81},
            "grid": [
                {
                    **central,
                    "delta_g_R4_c1": 0.0,
                    "delta_g_R4_c2": 0.0,
                    "delta_g_R4_c3": 0.0,
                    "log_marginal_likelihood": -0.5,
                    "profile_log_likelihood": -0.5,
                },
                {
                    "g_R4_c1": central["g_R4_c1"] + 0.02,
                    "g_R4_c2": central["g_R4_c2"],
                    "g_R4_c3": central["g_R4_c3"],
                    "delta_g_R4_c1": 0.02,
                    "delta_g_R4_c2": 0.0,
                    "delta_g_R4_c3": 0.0,
                    "log_marginal_likelihood": -0.1,
                    "profile_log_likelihood": -0.1,
                },
            ],
        })

    network = network_r4_waveform_likelihood(rows)

    assert network["detectors"] == ["H1", "L1"]
    assert network["grid_points"] == 2
    assert network["posterior"]["posterior_normalized"] is True
    assert network["best_marginal_grid_point"]["g_R4_c1"] == pytest.approx(0.52)


def test_evaluation_reports_missing_lalsuite_or_complete_fake_grid():
    rows = [
        {"detector": "H1", "likelihood_ready": True},
        {"detector": "L1", "likelihood_ready": True},
    ]
    network = {
        "grid_points": len(GRID_OFFSETS) ** len(AXES),
        "posterior": {
            "posterior_normalized": True,
            "posterior_positive_semidefinite": True,
        },
    }

    result = evaluate_r4_lalsuite_waveform_likelihood_posterior(rows, network)

    assert result["claim_ready"] is False
    if result["lalsuite_status"]["available"]:
        assert result["r4_waveform_likelihood_posterior_ready"] is True
        assert result["likelihood_blockers"] == []
    else:
        assert result["r4_waveform_likelihood_posterior_ready"] is False
        assert "lalsuite_not_installed" in result["likelihood_blockers"]


def test_committed_vulcan_artifact_is_ready_nonclaiming():
    path = Path(
        "experiments/results/v2.187/"
        "r4_lalsuite_waveform_likelihood_posterior.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.187"
    assert result["route_status"] == (
        "r4_lalsuite_waveform_likelihood_posterior_ready_nonclaiming"
    )
    assert result["evaluation"]["r4_waveform_likelihood_posterior_ready"] is True
    assert result["evaluation"]["ready_for_framework_claim"] is False
    assert result["network_likelihood"]["grid_points"] == 125
    assert result["network_likelihood"]["nuisance_points_per_detector"] == [81, 81]
    assert result["network_likelihood"]["posterior"]["posterior_normalized"] is True
    assert result["network_likelihood"]["posterior"][
        "posterior_positive_semidefinite"
    ] is True
