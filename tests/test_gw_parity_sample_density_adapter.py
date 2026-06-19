"""Tests for source-native sample-density posterior adapters."""

import numpy as np
import pytest

from itb.gw_parity import (
    histogram_posterior_from_samples,
    joint_histogram_posterior_from_samples,
)


def test_histogram_posterior_from_samples_normalizes_density():
    result = histogram_posterior_from_samples(
        [-0.1, -0.05, 0.0, 0.0, 0.02, 0.04, 0.1],
        bins=10,
        value_range=(-0.2, 0.2),
    )

    assert result["ready"] is True
    assert result["density_norm"] == pytest.approx(1.0)
    assert result["sample_count"] == 7
    assert abs(result["peak_coordinate"]) < 0.05
    assert result["blockers"] == []


def test_joint_histogram_posterior_from_samples_normalizes_density():
    x_samples = np.array([-0.1, -0.02, 0.0, 0.01, 0.08, 0.1])
    y_samples = np.array([-0.2, -0.05, 0.0, 0.02, 0.1, 0.2])

    result = joint_histogram_posterior_from_samples(
        x_samples,
        y_samples,
        bins=(8, 8),
        value_range=((-0.2, 0.2), (-0.4, 0.4)),
    )

    assert result["ready"] is True
    assert result["density_norm"] == pytest.approx(1.0)
    assert result["bins"] == [8, 8]
    assert result["sample_count"] == 6
    assert result["blockers"] == []


def test_histogram_posterior_blocks_bad_inputs():
    result = histogram_posterior_from_samples(
        [0.0, float("nan")],
        bins=1,
        value_range=(1.0, -1.0),
    )

    assert result["ready"] is False
    assert "histogram_bins_too_small" in result["blockers"]
    assert "histogram_range_not_increasing" in result["blockers"]
    assert "samples_not_finite" in result["blockers"]


def test_joint_histogram_blocks_shape_mismatch():
    result = joint_histogram_posterior_from_samples(
        [0.0, 1.0],
        [0.0],
    )

    assert result["ready"] is False
    assert "sample_shape_mismatch" in result["blockers"]
