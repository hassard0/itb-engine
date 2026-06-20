"""Tests for the v2.110 source-backed strain projection."""

import numpy as np
import pytest

from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_source_backed_cubic_waveform_response import VF_GRID_MAX
from experiments.gw_source_backed_strain_projection import (
    M_SOLAR_SECONDS,
    REFERENCE_TOTAL_MASS_SOLAR,
    conditioned_frequency_feature,
    evaluate_source_backed_strain_projection,
    normalized_vector,
    project_conditioned_source_response,
    source_frequency_templates,
    source_inspiral_frequency_window,
    validate_total_mass_solar,
    vf_from_frequency_hz,
)


def test_vf_from_frequency_uses_total_mass_in_seconds():
    frequencies = np.array([20.0, 100.0, 200.0])
    v_f = vf_from_frequency_hz(
        frequencies,
        total_mass_solar=REFERENCE_TOTAL_MASS_SOLAR,
    )
    expected = (
        np.pi
        * REFERENCE_TOTAL_MASS_SOLAR
        * M_SOLAR_SECONDS
        * frequencies
    ) ** (1.0 / 3.0)

    assert np.allclose(v_f, expected)
    assert np.all(np.diff(v_f) > 0.0)


def test_source_inspiral_frequency_window_respects_detector_and_vf_bounds():
    window = source_inspiral_frequency_window(4 * SAMPLE_RATE_HZ)

    assert window["bin_count"] > 100
    assert window["frequency_min_hz"] >= 20.0
    assert window["v_f_max"] <= VF_GRID_MAX
    assert window["frequency_resolution_hz"] == pytest.approx(0.25)


def test_normalized_vector_centers_and_sets_unit_norm():
    vector = normalized_vector(np.array([1.0, 2.0, 4.0, 8.0]))

    assert float(np.mean(vector)) == pytest.approx(0.0)
    assert float(np.linalg.norm(vector)) == pytest.approx(1.0)
    with pytest.raises(ValueError, match="normalized"):
        normalized_vector(np.ones(4))


def test_source_frequency_templates_are_unit_norm():
    window = source_inspiral_frequency_window(4 * SAMPLE_RATE_HZ)
    templates = source_frequency_templates(window["v_f"])

    assert sorted(templates) == [
        "amplitude_alpha_bar_1",
        "amplitude_alpha_bar_2",
        "phase_alpha_bar_1",
        "phase_alpha_bar_2",
    ]
    for template in templates.values():
        assert np.linalg.norm(template) == pytest.approx(1.0)


def test_project_conditioned_source_response_returns_finite_projections():
    times = np.arange(4 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    conditioned = np.sin(2.0 * np.pi * 80.0 * times)
    conditioned = (conditioned - np.mean(conditioned)) / np.sqrt(
        np.mean(conditioned * conditioned)
    )
    result = project_conditioned_source_response(conditioned)

    assert result["projection_ready"] is True
    assert result["feature_norm"] == pytest.approx(1.0)
    assert set(result["projections"]) == {
        "amplitude_alpha_bar_1",
        "amplitude_alpha_bar_2",
        "phase_alpha_bar_1",
        "phase_alpha_bar_2",
    }
    assert all(np.isfinite(value) for value in result["projections"].values())


def test_frequency_feature_and_evaluation_are_ready_but_nonclaiming():
    times = np.arange(4 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    conditioned = np.cos(2.0 * np.pi * 60.0 * times)
    conditioned = (conditioned - np.mean(conditioned)) / np.sqrt(
        np.mean(conditioned * conditioned)
    )
    projection = project_conditioned_source_response(conditioned)
    rows = [
        {
            "detector": "H1",
            "projection_ready": True,
            "source_backed_projection": projection,
        },
        {
            "detector": "L1",
            "projection_ready": True,
            "source_backed_projection": projection,
        },
    ]
    evaluation = evaluate_source_backed_strain_projection(rows)
    feature = conditioned_frequency_feature(conditioned)

    assert feature["feature_kind"] == "centered_unit_log_magnitude_spectrum"
    assert evaluation["strain_projection_ready"] is True
    assert evaluation["claim_ready"] is False
    assert evaluation["projection_blockers"] == []
    assert evaluation["removed_v2_109_blocker"] == (
        "frequency_domain_to_strain_projection_missing"
    )
    assert "projection_is_spectral_shape_not_calibrated_likelihood" in evaluation[
        "claim_blockers"
    ]


def test_validate_total_mass_rejects_invalid_values():
    with pytest.raises(ValueError, match="total_mass_solar"):
        validate_total_mass_solar(0.0)
