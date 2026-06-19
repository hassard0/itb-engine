"""Tests for Ng event-level Feather posterior parser guards."""

import numpy as np
import pyarrow as pa

from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS,
    parse_ng_event_level_feather_table,
)


def _fixture_table(**overrides):
    columns = {
        "event": ["E1", "E1", "E2", "E2"],
        "kappa": [-0.1, 0.0, 0.1, 0.2],
        "log_likelihood": [-1.0, -0.5, -0.25, -0.75],
        "log_prior": [-2.0, -2.0, -2.0, -2.0],
        "redshift": [0.1, 0.1, 0.2, 0.2],
        "comoving_distance": [0.4, 0.4, 0.8, 0.8],
        "extra": [1, 2, 3, 4],
    }
    columns.update(overrides)
    return pa.table(columns)


def test_ng_event_level_feather_parser_summarizes_release_shaped_table():
    result = parse_ng_event_level_feather_table(
        _fixture_table(),
        source_file="samples_posterior_birefringence.feather",
    )

    assert result["schema"] == "ng_event_level_feather_v1"
    assert result["required_columns"] == list(NG_EVENT_LEVEL_FEATHER_REQUIRED_COLUMNS)
    assert result["parser_ready"] is True
    assert result["parser_blockers"] == []
    assert result["row_count"] == 4
    assert result["column_count"] == 7
    assert result["event_count"] == 2
    assert result["event_sample_count_min"] == 2
    assert result["event_sample_count_max"] == 2
    assert result["event_counts_preview"] == [
        {"event": "E1", "sample_count": 2},
        {"event": "E2", "sample_count": 2},
    ]
    assert result["numeric_summaries"]["kappa"]["p50"] == 0.05
    assert result["numeric_summaries"]["redshift"]["max"] == 0.2
    assert result["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["restricted_global_kappa_likelihood_ready"] is False


def test_ng_event_level_feather_parser_blocks_missing_required_column():
    table = _fixture_table()
    table = table.drop(["log_prior"])

    result = parse_ng_event_level_feather_table(table)

    assert result["parser_ready"] is False
    assert result["parser_blockers"] == ["missing_ng_event_level_feather_columns"]
    assert result["missing_columns"] == ["log_prior"]


def test_ng_event_level_feather_parser_blocks_required_column_nulls():
    result = parse_ng_event_level_feather_table(
        _fixture_table(redshift=pa.array([0.1, None, 0.2, 0.2], type=pa.float64()))
    )

    assert result["parser_ready"] is False
    assert "redshift_contains_nulls" in result["parser_blockers"]


def test_ng_event_level_feather_parser_blocks_nonfinite_numeric_values():
    result = parse_ng_event_level_feather_table(
        _fixture_table(kappa=[-0.1, 0.0, np.inf, 0.2])
    )

    assert result["parser_ready"] is False
    assert "kappa_not_finite" in result["parser_blockers"]
