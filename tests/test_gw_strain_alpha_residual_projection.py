"""Tests for the v2.108 strain conditioning and alpha proxy projection."""

import numpy as np
import pytest

from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_strain_alpha_residual_projection import (
    SEGMENT_SECONDS,
    alpha_proxy_templates,
    condition_strain_segment,
    evaluate_projection_harness,
    event_centered_slice,
    network_projection,
    project_conditioned_strain,
    template_summary,
)


def test_event_centered_slice_selects_four_second_window():
    selection = event_centered_slice(
        gps_start=1180922479,
        sample_count=32 * SAMPLE_RATE_HZ,
    )

    assert selection.start == int((15.5 - 2.0) * SAMPLE_RATE_HZ)
    assert selection.stop - selection.start == int(SEGMENT_SECONDS * SAMPLE_RATE_HZ)


def test_condition_strain_segment_demeans_tapers_and_normalizes():
    strain = np.linspace(-1.0, 1.0, 32 * SAMPLE_RATE_HZ)
    result = condition_strain_segment(strain, gps_start=1180922479)
    conditioned = result["conditioned"]

    assert result["sample_count"] == int(SEGMENT_SECONDS * SAMPLE_RATE_HZ)
    assert np.isfinite(conditioned).all()
    assert result["conditioned_rms"] == pytest.approx(1.0)
    assert abs(result["conditioned_mean"]) < 0.1


def test_alpha_proxy_templates_are_orthonormal():
    templates = alpha_proxy_templates(int(SEGMENT_SECONDS * SAMPLE_RATE_HZ))
    summary = template_summary(templates)

    assert summary["template_kind"] == (
        "deterministic_proxy_not_source_backed_eft_waveform"
    )
    assert summary["alpha_bar_1_norm"] == pytest.approx(1.0)
    assert summary["alpha_bar_2_norm"] == pytest.approx(1.0)
    assert summary["alpha_template_dot"] == pytest.approx(0.0, abs=1e-12)


def test_project_conditioned_strain_returns_finite_proxy_coefficients():
    strain = np.sin(np.linspace(0.0, 100.0, 32 * SAMPLE_RATE_HZ))
    conditioned = condition_strain_segment(strain, gps_start=1180922479)[
        "conditioned"
    ]
    templates = alpha_proxy_templates(conditioned.size)
    projection = project_conditioned_strain(conditioned, templates)

    assert np.isfinite(projection["alpha_bar_1_proxy_projection"])
    assert np.isfinite(projection["alpha_bar_2_proxy_projection"])
    assert projection["conditioned_energy"] == pytest.approx(1.0)


def test_evaluate_projection_harness_ready_but_nonclaiming():
    templates = alpha_proxy_templates(int(SEGMENT_SECONDS * SAMPLE_RATE_HZ))
    rows = [
        {
            "detector": "H1",
            "projection_ready": True,
            "projection": {
                "alpha_bar_1_proxy_projection": 0.1,
                "alpha_bar_2_proxy_projection": -0.2,
            },
        },
        {
            "detector": "L1",
            "projection_ready": True,
            "projection": {
                "alpha_bar_1_proxy_projection": 0.3,
                "alpha_bar_2_proxy_projection": -0.1,
            },
        },
    ]
    result = evaluate_projection_harness(rows, templates)

    assert result["projection_harness_ready"] is True
    assert result["claim_ready"] is False
    assert result["projection_blockers"] == []
    assert "alpha_templates_proxy_not_source_backed" in result["claim_blockers"]
    assert "psd_whitening_and_calibration_not_applied" in result["claim_blockers"]


def test_network_projection_averages_h1_l1_proxy_coefficients():
    rows = [
        {
            "detector": "H1",
            "projection": {
                "alpha_bar_1_proxy_projection": 0.1,
                "alpha_bar_2_proxy_projection": -0.2,
            },
        },
        {
            "detector": "L1",
            "projection": {
                "alpha_bar_1_proxy_projection": 0.3,
                "alpha_bar_2_proxy_projection": -0.1,
            },
        },
    ]
    result = network_projection(rows)

    assert result["detectors"] == ["H1", "L1"]
    assert result["alpha_bar_1_proxy_mean"] == pytest.approx(0.2)
    assert result["alpha_bar_2_proxy_mean"] == pytest.approx(-0.15)
    assert result["alpha_bar_1_detector_spread"] == pytest.approx(0.2)
