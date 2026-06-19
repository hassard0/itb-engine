"""Tests for native GW parity packet guards."""

import math

import pytest

from itb.gw_parity import (
    GWParityNativePacket,
    callister_sgwb_amplitude_log_gain,
    callister_sgwb_energy_hyperbolic_argument,
    ng_kappa_amplitude_log_gain,
    normalize_discrete_posterior,
    validate_gw_parity_native_packet,
)


def _ng_packet(**overrides):
    data = {
        "label": "ng_gwtc3_kappa_at_100hz",
        "source_url": "https://arxiv.org/abs/2305.05844",
        "parameter_basis": "ng_kappa_at_100hz",
        "measurement_kind": "external_native_posterior",
        "parameters": {
            "kappa_Gpc_inv": -0.019,
            "kappa_plus_90": 0.038,
            "kappa_minus_90": 0.029,
            "f_ref_hz": 100.0,
        },
        "public_code_url": (
            "https://github.com/thomasckng/"
            "Constraining-Birefringence-with-GWTC-3"
        ),
        "public_data_url": "https://zenodo.org/records/7935107",
        "public_likelihood_url": "https://zenodo.org/records/7935107",
    }
    data.update(overrides)
    return GWParityNativePacket(**data)


def test_native_packet_can_be_source_ready_without_engine_projection():
    result = validate_gw_parity_native_packet(_ng_packet())

    assert result["native_packet_ready"] is True
    assert result["engine_projection_ready"] is False
    assert result["native_blockers"] == []
    assert "missing_source_backed_operator_map" in result["projection_blockers"]
    assert "engine_projection_not_ready" in result["projection_blockers"]


def test_native_packet_requires_public_code_data_and_likelihood():
    result = validate_gw_parity_native_packet(_ng_packet(public_likelihood_url=None))

    assert result["native_packet_ready"] is False
    assert "missing_public_code_data_or_likelihood" in result["native_blockers"]


def test_native_packet_rejects_unknown_basis():
    result = validate_gw_parity_native_packet(
        _ng_packet(parameter_basis="engine_g_R2_parity")
    )

    assert result["native_packet_ready"] is False
    assert "native_basis_not_allowed" in result["native_blockers"]


def test_engine_projection_needs_all_adapter_pieces():
    packet = _ng_packet(
        source_backed_operator_map=True,
        frequency_normalization_ready=True,
        dimensional_conversion_ready=True,
        framework_exclusion_math_ready=True,
        engine_projection_status="engine_projection_ready",
    )
    result = validate_gw_parity_native_packet(packet)

    assert result["native_packet_ready"] is True
    assert result["engine_projection_ready"] is True
    assert result["projection_blockers"] == []


def test_ng_kappa_amplitude_log_gain_matches_source_formula():
    zero = ng_kappa_amplitude_log_gain(
        kappa_gpc_inv=0.0,
        distance_gpc=1.2,
        frequency_hz=100.0,
    )
    value = ng_kappa_amplitude_log_gain(
        kappa_gpc_inv=-0.019,
        distance_gpc=2.0,
        frequency_hz=200.0,
    )

    assert zero.value == 0.0
    assert value.value == pytest.approx(-0.019 * 2.0 * 2.0)
    assert value.engine_projection_allowed is False
    assert value.target_basis == "ppv_amplitude_log_gain"
    assert value.helicity_convention == "positive_kappa_enhances_left_in_ng_convention"


def test_callister_sgwb_log_gain_keeps_distance_and_redshift_terms():
    distance_only = callister_sgwb_amplitude_log_gain(
        kappa_d=0.1,
        kappa_z=0.0,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )
    redshift_only = callister_sgwb_amplitude_log_gain(
        kappa_d=0.0,
        kappa_z=0.1,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )

    assert distance_only.value == pytest.approx(0.2 * math.pi)
    assert redshift_only.value == pytest.approx(0.03 * math.pi)
    assert distance_only.engine_projection_allowed is False
    assert distance_only.helicity_convention == (
        "positive_vp_right_enhanced_in_callister_convention"
    )


def test_callister_energy_density_argument_is_twice_waveform_log_gain():
    waveform = callister_sgwb_amplitude_log_gain(
        kappa_d=0.1,
        kappa_z=0.0,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )
    energy_argument = callister_sgwb_energy_hyperbolic_argument(
        kappa_d=0.1,
        kappa_z=0.0,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )

    assert energy_argument.value == pytest.approx(2.0 * waveform.value)
    assert energy_argument.value == pytest.approx(2.0 * math.pi * 0.1 * 2.0)
    assert energy_argument.target_basis == "sgwb_energy_density_hyperbolic_argument"
    assert energy_argument.engine_projection_allowed is False


def test_discrete_posterior_normalizer_requires_clean_grid():
    normalized = normalize_discrete_posterior(
        coordinates=[-1.0, 0.0, 1.0],
        density=[0.0, 2.0, 0.0],
    )
    bad = normalize_discrete_posterior(
        coordinates=[0.0, 0.0, 1.0],
        density=[1.0, 1.0, 1.0],
    )

    assert normalized["ready"] is True
    assert normalized["normalized_norm"] == pytest.approx(1.0)
    assert bad["ready"] is False
    assert "posterior_coordinates_not_strictly_increasing" in bad["blockers"]
