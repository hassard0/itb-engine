"""Tests for the v2.116 marginal alpha packet export."""

import pytest

from experiments.gw_cubic_source_native_adapter import (
    REQUIRED_SOURCE_NATIVE_PACKET_FIELDS,
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_marginal_alpha_packet_export import (
    diagnose_gw_marginal_alpha_packet_export,
    evaluate_packet_export,
    load_marginal_result,
    marginal_alpha_source_native_packet,
    marginal_alpha_statistics,
    normalized_likelihood_weights,
    weighted_quantile,
)


def test_weighted_quantile_returns_expected_order_statistic():
    values = [0.0, 1.0, 2.0]
    weights = [0.2, 0.6, 0.2]

    assert weighted_quantile(values, weights, 0.5) == pytest.approx(0.5)


def test_normalized_likelihood_weights_sum_to_one():
    rows = [
        {"log_marginal_likelihood": -2.0},
        {"log_marginal_likelihood": -1.0},
        {"log_marginal_likelihood": -3.0},
    ]
    weights = normalized_likelihood_weights(rows)

    assert float(weights.sum()) == pytest.approx(1.0)
    assert weights[1] > weights[0] > weights[2]


def test_marginal_statistics_export_covariance_and_constraints():
    result = load_marginal_result()
    stats = marginal_alpha_statistics(result["network_likelihood"])

    assert set(stats["parameter_constraints"]) == {"alpha_bar_1", "alpha_bar_2"}
    assert stats["source_parameter_covariance"]["parameters"] == [
        "alpha_bar_1",
        "alpha_bar_2",
    ]
    assert len(stats["source_parameter_covariance"]["matrix"]) == 2
    assert stats["weight_summary"]["grid_points"] == 441
    assert stats["weight_summary"]["effective_sample_size"] > 1.0


def test_exported_packet_has_required_shape_and_real_source_marker():
    packet = marginal_alpha_source_native_packet(load_marginal_result())

    assert all(field in packet for field in REQUIRED_SOURCE_NATIVE_PACKET_FIELDS)
    assert packet["synthetic_fixture"] is False
    assert packet["event"] == "GW170608"
    assert packet["posterior_or_likelihood_export"]["status"] == (
        "reproduced_source_native_likelihood"
    )
    assert packet["source_parameter_covariance"]["parameters"] == [
        "alpha_bar_1",
        "alpha_bar_2",
    ]


def test_adapter_parses_packet_but_rejects_open_systematics():
    packet = marginal_alpha_source_native_packet(load_marginal_result())
    result = evaluate_gw_cubic_source_native_packet(packet)

    assert result["synthetic_fixture"] is False
    assert result["native_adapter_ready"] is False
    assert result["likelihood_summary"]["source_native_usable"] is True
    assert result["covariance_summary"]["numeric"] is True
    assert result["constraints_summary"]["all_source_parameters_numeric"] is True
    assert result["adapter_blockers"] == ["systematics_not_closed"]
    assert "engine_projection_not_ready" in result["claim_blockers"]


def test_packet_export_evaluation_removes_export_blocker_but_not_claim_blockers():
    packet = marginal_alpha_source_native_packet(load_marginal_result())
    result = evaluate_packet_export(packet)

    assert result["packet_export_ready"] is True
    assert result["claim_ready"] is False
    assert result["removed_v2_115_blocker"] == "source_native_packet_not_exported"
    assert "g8_joint_component_missing" in result["remaining_nonclaiming_reasons"]


def test_diagnosis_selects_systematics_and_engine_projection_next():
    result = diagnose_gw_marginal_alpha_packet_export()

    assert result["version"] == "v2.116"
    assert result["route_status"] == (
        "marginal_alpha_source_native_packet_exported_nonclaiming"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "close_systematics_budget_and_engine_projection_for_alpha_packet"
    )
