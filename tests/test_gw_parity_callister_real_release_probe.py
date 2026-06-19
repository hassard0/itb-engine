"""Regression tests for compact real-release probe summaries."""

import pytest

from experiments.gw_parity_callister_real_release_probe import (
    _grid_summary,
    _joint_summary,
)


def test_grid_summary_keeps_compact_peak_and_norm():
    summary = _grid_summary(
        {
            "ready": True,
            "coordinates": [-1.0, 0.0, 1.0],
            "density": [0.0, 2.0, 0.0],
            "normalized_norm": 1.0,
            "blockers": [],
        },
        "coordinates",
    )

    assert summary["points"] == 3
    assert summary["coordinate_min"] == -1.0
    assert summary["coordinate_max"] == 1.0
    assert summary["peak_coordinate"] == 0.0
    assert summary["normalized_norm"] == 1.0


def test_joint_summary_preserves_d_by_z_peak_order():
    summary = _joint_summary(
        {
            "ready": True,
            "shape": [2, 3],
            "kappa_d_coordinates": [-0.5, 0.5],
            "kappa_z_coordinates": [-1.0, 0.0, 1.0],
            "density": [
                [0.1, 0.2, 0.3],
                [0.4, 0.9, 0.2],
            ],
            "normalized_norm": 1.0,
            "blockers": [],
        }
    )

    assert summary["shape"] == [2, 3]
    assert summary["peak_kappa_D"] == pytest.approx(0.5)
    assert summary["peak_kappa_z"] == pytest.approx(0.0)
    assert summary["normalized_norm"] == 1.0
