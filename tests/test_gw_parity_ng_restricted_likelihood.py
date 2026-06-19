"""Tests for Ng restricted global kappa likelihood reproduction."""

import numpy as np
import pytest

from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    restricted_global_kappa_likelihood_from_event_samples,
)


def _fixture_samples():
    events = np.array(["E1"] * 6 + ["E2"] * 6 + ["E3"] * 6)
    kappas = np.array(
        [
            -0.030,
            -0.015,
            -0.005,
            0.005,
            0.015,
            0.030,
            -0.020,
            -0.010,
            -0.002,
            0.002,
            0.010,
            0.020,
            -0.025,
            -0.012,
            -0.004,
            0.004,
            0.012,
            0.025,
        ]
    )
    return events, kappas


def test_restricted_global_kappa_likelihood_normalizes_kde_product():
    events, kappas = _fixture_samples()

    result = restricted_global_kappa_likelihood_from_event_samples(
        events,
        kappas,
        grid_min=-0.08,
        grid_max=0.08,
        grid_size=201,
    )

    assert result["schema"] == "ng_restricted_global_kappa_likelihood_v1"
    assert result["ready"] is True
    assert result["parser_blockers"] == []
    assert result["sample_count"] == 18
    assert result["event_count"] == 3
    assert result["event_sample_count_min"] == 6
    assert result["density_norm"] == pytest.approx(1.0)
    assert result["restricted_kappa_5"] < result["restricted_kappa_median"]
    assert result["restricted_kappa_median"] < result["restricted_kappa_95"]
    assert abs(result["restricted_kappa_median"]) < 0.005
    assert result["absolute_kappa_68"] > 0.0
    assert result["absolute_kappa_90"] > result["absolute_kappa_68"]
    assert 0.0 <= result["credible_level_at_zero"] <= 1.0
    assert result["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False


def test_restricted_global_kappa_likelihood_blocks_shape_mismatch():
    result = restricted_global_kappa_likelihood_from_event_samples(
        ["E1", "E2"],
        [0.0],
    )

    assert result["ready"] is False
    assert "event_kappa_shape_mismatch" in result["parser_blockers"]


def test_restricted_global_kappa_likelihood_blocks_single_event():
    result = restricted_global_kappa_likelihood_from_event_samples(
        ["E1", "E1", "E1"],
        [-0.1, 0.0, 0.1],
    )

    assert result["ready"] is False
    assert "event_count_too_small" in result["parser_blockers"]


def test_restricted_global_kappa_likelihood_blocks_nonfinite_samples():
    events, kappas = _fixture_samples()
    kappas[0] = np.nan

    result = restricted_global_kappa_likelihood_from_event_samples(events, kappas)

    assert result["ready"] is False
    assert "kappa_not_finite" in result["parser_blockers"]
