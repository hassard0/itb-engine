"""Tests for the v2.122 per-nuisance likelihood cube export."""

from pathlib import Path

import numpy as np

from experiments.gw_alpha_likelihood_cube_export import (
    DEFAULT_MARGINAL_RESULT_PATH,
    detector_likelihood_cube_from_packets,
    evaluate_likelihood_cube_export,
    likelihood_matrix_from_packets,
    load_json,
    network_surfaces_from_cube,
)
from experiments.gw_lalsuite_marginal_alpha_likelihood import (
    logsumexp,
    marginalize_alpha_grid_from_packets,
)


DEFAULT_CUBE_EXPORT_PATH = Path(
    "experiments/results/v2.122/gw_alpha_likelihood_cube_export.json"
)


def _toy_packets():
    return [
        {
            "nuisance": {"name": "left"},
            "data": np.array([1.0 + 0.0j, 0.0 + 1.0j]),
            "templates": {
                "alpha_bar_1": np.array([1.0 + 0.0j, 0.0 + 0.0j]),
                "alpha_bar_2": np.array([0.0 + 0.0j, 0.0 + 1.0j]),
            },
        },
        {
            "nuisance": {"name": "right"},
            "data": np.array([0.5 + 0.0j, 0.0 + 0.25j]),
            "templates": {
                "alpha_bar_1": np.array([1.0 + 0.0j, 0.0 + 0.0j]),
                "alpha_bar_2": np.array([0.0 + 0.0j, 0.0 + 1.0j]),
            },
        },
    ]


def _toy_alpha_grid():
    return [
        {"alpha_bar_1": 0.0, "alpha_bar_2": 0.0},
        {"alpha_bar_1": 0.5, "alpha_bar_2": 0.25},
        {"alpha_bar_1": 1.0, "alpha_bar_2": 1.0},
    ]


def test_likelihood_matrix_matches_direct_marginalization_inputs():
    packets = _toy_packets()
    grid = _toy_alpha_grid()
    matrix = likelihood_matrix_from_packets(packets, grid=grid)
    marginal = marginalize_alpha_grid_from_packets(packets, grid=grid)

    assert len(matrix) == len(packets)
    assert len(matrix[0]) == len(grid)
    for alpha_index, row in enumerate(marginal["grid"]):
        column = [nuisance_row[alpha_index] for nuisance_row in matrix]
        assert row["log_marginal_likelihood"] == logsumexp(column) - np.log(
            len(column)
        )
        assert row["profile_log_likelihood"] == max(column)


def test_network_surfaces_from_cube_sum_detector_marginals_and_profiles():
    packets = _toy_packets()
    grid = _toy_alpha_grid()
    h1 = detector_likelihood_cube_from_packets("H1", packets, grid=grid)
    l1 = detector_likelihood_cube_from_packets("L1", packets, grid=grid)
    cube = {"detector_cubes": [h1, l1]}
    network = network_surfaces_from_cube(cube)

    assert network["detectors"] == ["H1", "L1"]
    assert network["grid_points"] == len(grid)
    assert network["best_marginal_grid_point"]["alpha_bar_1"] == 0.5
    assert network["best_profile_grid_point"]["alpha_bar_2"] == 0.25


def test_committed_v2_122_cube_reconstructs_v2_115_surfaces():
    result = load_json(DEFAULT_CUBE_EXPORT_PATH)
    marginal = load_json(DEFAULT_MARGINAL_RESULT_PATH)
    evaluation = evaluate_likelihood_cube_export(result["likelihood_cube"], marginal)

    assert result["version"] == "v2.122"
    assert result["route_status"] == (
        "per_nuisance_likelihood_cube_exported_nonclaiming"
    )
    assert evaluation["likelihood_cube_ready"] is True
    assert evaluation["cube_cells"] == 71442
    assert evaluation["surface_reconstruction"]["within_tolerance"] is True
    assert result["selected_next_build_action"] == (
        "prior_reweight_sweep_from_likelihood_cube"
    )
