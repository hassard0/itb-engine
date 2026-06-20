"""Tests for the v2.105 alpha-bar likelihood stub."""

import pytest

from experiments.gw_alpha_likelihood_stub import (
    CENTER,
    deterministic_alpha_grid,
    diagnose_gw_alpha_likelihood_stub,
    quadratic_alpha_log_likelihood,
    synthetic_alpha_likelihood_stub_packet,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


def test_quadratic_likelihood_peaks_at_source_interval_center():
    center = quadratic_alpha_log_likelihood(
        CENTER["alpha_bar_1"],
        CENTER["alpha_bar_2"],
    )
    shifted = quadratic_alpha_log_likelihood(
        CENTER["alpha_bar_1"] + 1.0,
        CENTER["alpha_bar_2"] + 1.0,
    )

    assert center == pytest.approx(0.0)
    assert shifted < center


def test_deterministic_grid_contains_center_as_best_point():
    grid = deterministic_alpha_grid(points_per_axis=31)
    best = max(grid, key=lambda row: row["log_likelihood"])

    assert len(grid) == 31 * 31
    assert best["alpha_bar_1"] == pytest.approx(CENTER["alpha_bar_1"])
    assert best["alpha_bar_2"] == pytest.approx(CENTER["alpha_bar_2"])
    assert best["log_likelihood"] == pytest.approx(0.0)


def test_stub_packet_is_source_native_adapter_ready_but_nonclaiming():
    result = evaluate_gw_cubic_source_native_packet(
        synthetic_alpha_likelihood_stub_packet()
    )

    assert result["native_adapter_ready"] is True
    assert result["claim_ready"] is False
    assert result["adapter_blockers"] == []
    assert "synthetic_fixture_not_real_source" in result["claim_blockers"]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_stub_packet_exports_valid_reproduced_likelihood_status():
    packet = synthetic_alpha_likelihood_stub_packet()
    likelihood = packet["posterior_or_likelihood_export"]

    assert likelihood["status"] == "reproduced_source_native_likelihood"
    assert likelihood["parameters"] == ["alpha_bar_1", "alpha_bar_2"]
    assert likelihood["grid_points"] == 31 * 31
    assert likelihood["public_strain_connected"] is False


def test_diagnosis_selects_public_strain_connection_next():
    result = diagnose_gw_alpha_likelihood_stub()

    assert result["version"] == "v2.105"
    assert result["native_adapter_ready"] is True
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "minimal_alpha_likelihood_stub_ready_synthetic_only"
    assert result["selected_next_build_action"] == (
        "connect_public_strain_to_alpha_waveform_likelihood"
    )


def test_diagnosis_embeds_nonclaiming_adapter_evaluation():
    result = diagnose_gw_alpha_likelihood_stub()
    evaluation = result["adapter_evaluation"]

    assert evaluation["label"] == "synthetic_alpha_likelihood_stub_packet"
    assert evaluation["native_adapter_ready"] is True
    assert evaluation["claim_ready"] is False
    assert result["best_grid_point"]["log_likelihood"] == pytest.approx(0.0)
