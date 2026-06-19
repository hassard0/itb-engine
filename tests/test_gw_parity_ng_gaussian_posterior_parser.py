"""Tests for Ng Gaussian hyperposterior NPZ parser guards."""

import numpy as np

from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    NG_GAUSSIAN_NPZ_KEYS,
    parse_ng_gaussian_hyperposterior_npz_datasets,
)


def _fixture():
    chains = np.array(
        [
            [[-0.02, 0.01], [0.00, 0.02], [0.02, 0.03]],
            [[-0.01, 0.04], [0.01, 0.05], [0.03, 0.06]],
        ],
        dtype=float,
    )
    return {
        "chains": chains,
        "log_prob": np.ones(chains.shape[:2]) * 10.0,
        "local_accs": np.ones((chains.shape[0], 2)) * 0.8,
        "global_accs": np.ones((chains.shape[0], 2)) * 0.7,
    }


def test_ng_gaussian_npz_parser_summarizes_mu_sigma_samples():
    result = parse_ng_gaussian_hyperposterior_npz_datasets(
        _fixture(),
        source_file="samples_Gaussian.npz",
    )

    assert result["schema"] == "ng_gaussian_hyperposterior_npz_v1"
    assert result["required_keys"] == list(NG_GAUSSIAN_NPZ_KEYS)
    assert result["parser_ready"] is True
    assert result["parser_blockers"] == []
    assert result["chain_shape"] == [2, 3, 2]
    assert result["log_prob_shape"] == [2, 3]
    assert result["sample_count"] == 6
    assert result["parameter_names"] == ["mu", "sigma"]
    assert result["parameter_summaries"]["mu"]["p50"] == 0.005
    assert result["parameter_summaries"]["sigma"]["min"] == 0.01
    assert result["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False


def test_ng_gaussian_npz_parser_blocks_missing_keys():
    result = parse_ng_gaussian_hyperposterior_npz_datasets(
        {"chains": np.zeros((2, 3, 2))}
    )

    assert result["parser_ready"] is False
    assert result["parser_blockers"] == ["missing_ng_gaussian_npz_keys"]
    assert "log_prob" in result["missing_keys"]


def test_ng_gaussian_npz_parser_blocks_bad_chain_shape():
    fixture = _fixture()
    fixture["chains"] = np.zeros((2, 3))

    result = parse_ng_gaussian_hyperposterior_npz_datasets(fixture)

    assert result["parser_ready"] is False
    assert "chains_not_three_dimensional" in result["parser_blockers"]


def test_ng_gaussian_npz_parser_blocks_negative_sigma():
    fixture = _fixture()
    fixture["chains"][0, 0, 1] = -0.1

    result = parse_ng_gaussian_hyperposterior_npz_datasets(fixture)

    assert result["parser_ready"] is False
    assert "sigma_samples_negative" in result["parser_blockers"]
