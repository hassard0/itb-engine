"""Tests for the v2.113 optional LALSuite IMR projection."""

import importlib

import numpy as np
import pytest

from experiments.gw_lalsuite_imr_projection import (
    component_masses_from_total_eta,
    evaluate_lalsuite_imr_projection,
    generate_imrphenomd_reference,
    lalsuite_status,
    project_lalsuite_imr_response,
)
from experiments.gw_public_strain_connector import SAMPLE_RATE_HZ
from experiments.gw_source_backed_strain_projection import (
    REFERENCE_TOTAL_MASS_SOLAR,
    source_inspiral_frequency_window,
)


def _synthetic_32s_strain() -> np.ndarray:
    times = np.arange(32 * SAMPLE_RATE_HZ, dtype=float) / SAMPLE_RATE_HZ
    signal = 1.0e-21 * np.sin(2.0 * np.pi * 35.0 * times)
    signal += 4.0e-22 * np.sin(2.0 * np.pi * 90.0 * times)
    signal += 1.0e-22 * np.cos(2.0 * np.pi * 180.0 * times)
    return signal


def _skip_without_lalsuite():
    if (
        importlib.util.find_spec("lal") is None
        or importlib.util.find_spec("lalsimulation") is None
    ):
        pytest.skip("LALSuite optional dependency is not installed")


def test_component_masses_reconstruct_total_and_eta():
    masses = component_masses_from_total_eta()
    m1 = masses["mass_1_solar"]
    m2 = masses["mass_2_solar"]
    total = m1 + m2
    eta = m1 * m2 / total**2

    assert total == pytest.approx(REFERENCE_TOTAL_MASS_SOLAR)
    assert eta == pytest.approx(masses["eta"])
    assert m1 >= m2


def test_lalsuite_status_reports_expected_keys():
    status = lalsuite_status()

    assert sorted(status) == ["available", "has_imrphenomd", "lal_version"]
    assert isinstance(status["available"], bool)
    assert isinstance(status["has_imrphenomd"], bool)


def test_evaluation_ready_for_complete_fake_rows_when_lalsuite_available():
    _skip_without_lalsuite()
    projection = {
        "source_reference": "https://arxiv.org/abs/2407.08929",
        "projection_kind": "lalsuite_imrphenomd_psd_whitened_source_response",
        "reference_waveform": {"approximant": "IMRPhenomD"},
    }
    rows = [
        {
            "detector": "H1",
            "projection_ready": True,
            "lalsuite_imr_projection": projection,
        },
        {
            "detector": "L1",
            "projection_ready": True,
            "lalsuite_imr_projection": projection,
        },
    ]

    result = evaluate_lalsuite_imr_projection(rows)

    assert result["lalsuite_imr_projection_ready"] is True
    assert result["claim_ready"] is False
    assert result["projection_blockers"] == []
    assert result["removed_v2_112_blocker"] == (
        "leading_order_gr_reference_not_full_imr"
    )


def test_generate_imrphenomd_reference_produces_nonzero_complex_series():
    _skip_without_lalsuite()
    window = source_inspiral_frequency_window(4 * SAMPLE_RATE_HZ)
    result = generate_imrphenomd_reference(window["frequencies_hz"])

    assert result["waveform_summary"]["approximant"] == "IMRPhenomD"
    assert result["waveform_summary"]["nonzero_bins"] == window["bin_count"]
    assert np.iscomplexobj(result["h_plus"])
    assert np.max(np.abs(result["h_plus"])) > 0.0


def test_project_lalsuite_imr_response_returns_finite_values():
    _skip_without_lalsuite()
    result = project_lalsuite_imr_response(
        _synthetic_32s_strain(),
        gps_start=1180922479,
    )

    assert result["projection_ready"] is True
    assert result["reference_waveform"]["approximant"] == "IMRPhenomD"
    assert set(result["projections"]) == {"alpha_bar_1", "alpha_bar_2"}
    for row in result["projections"].values():
        assert np.isfinite(row["real"])
        assert np.isfinite(row["imag"])
        assert np.isfinite(row["abs"])
