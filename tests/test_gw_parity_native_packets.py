"""Tests for native GW parity packet guards."""

from itb.gw_parity import GWParityNativePacket, validate_gw_parity_native_packet


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
