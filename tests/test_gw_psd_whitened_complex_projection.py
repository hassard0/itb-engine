"""Tests for the v2.111 PSD-whitened complex projection."""

import numpy as np
import pytest

from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_psd_whitened_complex_projection import (
    evaluate_psd_whitened_complex_projection,
    event_tapered_segment,
    normalized_complex_source_templates,
    project_psd_whitened_complex_response,
    psd_whitened_event_spectrum,
    welch_psd_estimate,
)


def _synthetic_32s_strain() -> np.ndarray:
    times = np.arange(32 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    signal = 1.0e-21 * np.sin(2.0 * np.pi * 35.0 * times)
    signal += 4.0e-22 * np.sin(2.0 * np.pi * 90.0 * times)
    signal += 1.0e-22 * np.cos(2.0 * np.pi * 180.0 * times)
    return signal


def test_event_tapered_segment_selects_four_second_window():
    strain = _synthetic_32s_strain()
    result = event_tapered_segment(strain, gps_start=1180922479)

    assert result["sample_count"] == 4 * SAMPLE_RATE_HZ
    assert result["start_index"] == int((15.5 - 2.0) * SAMPLE_RATE_HZ)
    assert result["stop_index"] == int((15.5 + 2.0) * SAMPLE_RATE_HZ)
    assert result["tapered_rms"] > 0.0


def test_welch_psd_estimate_uses_off_source_segments():
    strain = _synthetic_32s_strain()
    event = event_tapered_segment(strain, gps_start=1180922479)
    result = welch_psd_estimate(strain, exclude_slice=event["selection"])

    assert result["segment_count"] >= 5
    assert result["segment_length"] == 4 * SAMPLE_RATE_HZ
    assert np.all(np.isfinite(result["psd"]))
    assert np.all(result["psd"] > 0.0)


def test_psd_whitened_event_spectrum_is_unit_norm_complex():
    strain = _synthetic_32s_strain()
    result = psd_whitened_event_spectrum(strain, gps_start=1180922479)
    spectrum = result["normalized_whitened_spectrum"]

    assert np.iscomplexobj(spectrum)
    assert np.linalg.norm(spectrum) == pytest.approx(1.0)
    assert result["frequency_window"]["bin_count"] == spectrum.size
    assert result["psd_summary"]["segment_count"] >= 5


def test_normalized_complex_source_templates_are_unit_norm():
    strain = _synthetic_32s_strain()
    spectrum = psd_whitened_event_spectrum(strain, gps_start=1180922479)
    templates = normalized_complex_source_templates(spectrum["v_f"])

    assert sorted(templates) == ["alpha_bar_1", "alpha_bar_2"]
    for template in templates.values():
        assert np.iscomplexobj(template)
        assert np.linalg.norm(template) == pytest.approx(1.0)


def test_project_psd_whitened_complex_response_returns_finite_values():
    strain = _synthetic_32s_strain()
    result = project_psd_whitened_complex_response(
        strain,
        gps_start=1180922479,
    )

    assert result["projection_ready"] is True
    assert result["normalized_whitened_norm"] == pytest.approx(1.0)
    assert set(result["projections"]) == {"alpha_bar_1", "alpha_bar_2"}
    for row in result["projections"].values():
        assert np.isfinite(row["real"])
        assert np.isfinite(row["imag"])
        assert np.isfinite(row["abs"])


def test_evaluation_ready_but_nonclaiming():
    strain = _synthetic_32s_strain()
    projection = project_psd_whitened_complex_response(
        strain,
        gps_start=1180922479,
    )
    rows = [
        {
            "detector": "H1",
            "projection_ready": True,
            "psd_whitened_projection": projection,
        },
        {
            "detector": "L1",
            "projection_ready": True,
            "psd_whitened_projection": projection,
        },
    ]
    result = evaluate_psd_whitened_complex_projection(rows)

    assert result["psd_whitened_complex_projection_ready"] is True
    assert result["claim_ready"] is False
    assert result["projection_blockers"] == []
    assert result["removed_v2_110_blocker"] == (
        "psd_whitening_and_calibration_likelihood_missing"
    )
    assert "unit_gr_reference_not_physical_waveform" in result["claim_blockers"]
