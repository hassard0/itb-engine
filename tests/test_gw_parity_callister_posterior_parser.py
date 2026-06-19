"""Tests for Callister fixed-rate posterior parser guards."""

import numpy as np
import pytest

from itb.gw_parity import (
    CALLISTER_FIXED_RATE_HDF_KEYS,
    GW_PARITY_PROJECTION_BLOCKERS,
    normalize_callister_joint_posterior,
    parse_callister_fixed_rate_hdf_datasets,
)


def _release_like_datasets():
    kappa_d_1d = np.linspace(-0.2, 0.2, 21)
    probability_kappa_d = np.exp(-0.5 * (kappa_d_1d / 0.06) ** 2)
    kappa_z_1d = np.linspace(-0.4, 0.4, 23)
    probability_kappa_z = np.exp(-0.5 * (kappa_z_1d / 0.11) ** 2)

    kappa_d_2d = np.linspace(-0.5, 0.5, 17)
    kappa_z_2d = np.linspace(-1.0, 1.0, 19)
    probabilities = np.exp(
        -0.5
        * (
            (kappa_d_2d[:, None] / 0.18) ** 2
            + (kappa_z_2d[None, :] / 0.31) ** 2
        )
    )
    return {
        "kappa_dcs_1D": kappa_d_1d,
        "probability_kappa_dc_1D": probability_kappa_d,
        "kappa_zs_1D": kappa_z_1d,
        "probability_kappa_z_1D": probability_kappa_z,
        "kappa_dcs_2D": kappa_d_2d,
        "kappa_zs_2D": kappa_z_2d,
        "probabilities": probabilities,
    }


def test_callister_fixed_rate_parser_normalizes_release_schema():
    result = parse_callister_fixed_rate_hdf_datasets(
        _release_like_datasets(),
        source_file="fixed_rate_delayedSFR.hdf",
    )

    assert result["schema"] == "callister_fixed_rate_hdf_v1"
    assert result["source_file"] == "fixed_rate_delayedSFR.hdf"
    assert result["required_keys"] == list(CALLISTER_FIXED_RATE_HDF_KEYS)
    assert result["parser_ready"] is True
    assert result["parser_blockers"] == []
    assert result["missing_keys"] == []
    assert result["one_dimensional"]["kappa_D"]["normalized_norm"] == pytest.approx(1.0)
    assert result["one_dimensional"]["kappa_z"]["normalized_norm"] == pytest.approx(1.0)
    assert result["joint"]["normalized_norm"] == pytest.approx(1.0)
    assert result["joint"]["shape"] == [17, 19]
    assert result["engine_projection_ready"] is False
    assert result["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert result["claimable_discriminator_now"] is False


def test_callister_fixed_rate_parser_accepts_release_result_group():
    result = parse_callister_fixed_rate_hdf_datasets(
        {"result": _release_like_datasets()},
        source_file="fixed_rate_delayedSFR.hdf",
    )

    assert result["parser_ready"] is True
    assert result["one_dimensional"]["kappa_D"]["normalized_norm"] == pytest.approx(1.0)
    assert result["one_dimensional"]["kappa_z"]["normalized_norm"] == pytest.approx(1.0)
    assert result["joint"]["shape"] == [17, 19]


def test_callister_fixed_rate_parser_blocks_missing_release_keys():
    result = parse_callister_fixed_rate_hdf_datasets(
        {"kappa_dcs_1D": np.array([-0.1, 0.1])}
    )

    assert result["parser_ready"] is False
    assert result["parser_blockers"] == ["missing_callister_fixed_rate_hdf_keys"]
    assert "probabilities" in result["missing_keys"]
    assert result["engine_projection_ready"] is False


def test_callister_joint_parser_enforces_documented_d_by_z_order():
    datasets = _release_like_datasets()
    datasets["probabilities"] = datasets["probabilities"].T

    result = parse_callister_fixed_rate_hdf_datasets(datasets)

    assert result["parser_ready"] is False
    assert "joint_probability_shape_mismatch" in result["parser_blockers"]


def test_callister_joint_normalizer_rejects_negative_density():
    result = normalize_callister_joint_posterior(
        kappa_d_coordinates=[-0.1, 0.0, 0.1],
        kappa_z_coordinates=[-0.2, 0.0, 0.2],
        density=[
            [0.0, 1.0, 0.0],
            [1.0, -0.5, 1.0],
            [0.0, 1.0, 0.0],
        ],
    )

    assert result["ready"] is False
    assert "probability_negative" in result["blockers"]
