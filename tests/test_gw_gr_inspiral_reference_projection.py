"""Tests for the v2.112 GR inspiral reference projection."""

import numpy as np
import pytest

from experiments.gw_gr_inspiral_reference_projection import (
    chirp_mass_solar,
    evaluate_gr_inspiral_reference_projection,
    gr_inspiral_source_response_templates,
    leading_order_gr_inspiral_reference,
    project_gr_inspiral_reference_response,
    psd_whitened_reference_context,
)
from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_source_backed_cubic_waveform_response import ETA_REFERENCE
from experiments.gw_source_backed_strain_projection import REFERENCE_TOTAL_MASS_SOLAR


def _synthetic_32s_strain() -> np.ndarray:
    times = np.arange(32 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    signal = 1.0e-21 * np.sin(2.0 * np.pi * 35.0 * times)
    signal += 4.0e-22 * np.sin(2.0 * np.pi * 90.0 * times)
    signal += 1.0e-22 * np.cos(2.0 * np.pi * 180.0 * times)
    return signal


def test_chirp_mass_uses_standard_total_mass_eta_relation():
    expected = REFERENCE_TOTAL_MASS_SOLAR * ETA_REFERENCE ** (3.0 / 5.0)

    assert chirp_mass_solar() == pytest.approx(expected)


def test_leading_order_reference_is_complex_and_decreases_in_amplitude():
    frequencies = np.array([20.0, 40.0, 80.0])
    v_f = np.array([0.18, 0.23, 0.29])
    reference = leading_order_gr_inspiral_reference(frequencies, v_f)

    assert np.iscomplexobj(reference)
    assert np.isfinite(reference).all()
    assert abs(reference[0]) > abs(reference[-1])


def test_psd_whitened_reference_context_returns_unit_data():
    context = psd_whitened_reference_context(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )

    assert context["normalized_data_norm"] == pytest.approx(1.0)
    assert context["frequency_window"]["bin_count"] == context[
        "normalized_whitened_data"
    ].size
    assert context["psd_summary"]["segment_count"] >= 5


def test_gr_inspiral_source_response_templates_are_unit_norm():
    context = psd_whitened_reference_context(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )
    templates = gr_inspiral_source_response_templates(
        context["frequencies_hz"],
        context["v_f"],
        context["psd_interp"],
    )

    assert sorted(templates) == ["alpha_bar_1", "alpha_bar_2"]
    for template in templates.values():
        assert np.iscomplexobj(template)
        assert np.linalg.norm(template) == pytest.approx(1.0)


def test_project_gr_inspiral_reference_response_returns_finite_values():
    result = project_gr_inspiral_reference_response(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )

    assert result["projection_ready"] is True
    assert result["reference_waveform"]["kind"] == (
        "leading_order_stationary_phase_gr_inspiral"
    )
    assert set(result["projections"]) == {"alpha_bar_1", "alpha_bar_2"}
    for row in result["projections"].values():
        assert np.isfinite(row["real"])
        assert np.isfinite(row["imag"])
        assert np.isfinite(row["abs"])


def test_evaluation_ready_but_nonclaiming():
    projection = project_gr_inspiral_reference_response(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )
    rows = [
        {
            "detector": "H1",
            "projection_ready": True,
            "gr_inspiral_projection": projection,
        },
        {
            "detector": "L1",
            "projection_ready": True,
            "gr_inspiral_projection": projection,
        },
    ]
    result = evaluate_gr_inspiral_reference_projection(rows)

    assert result["gr_inspiral_reference_projection_ready"] is True
    assert result["claim_ready"] is False
    assert result["projection_blockers"] == []
    assert result["removed_v2_111_blocker"] == (
        "unit_gr_reference_not_physical_waveform"
    )
    assert "leading_order_gr_reference_not_full_imr" in result["claim_blockers"]
