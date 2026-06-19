"""Tests for Ng PPV beta_1_0 candidate packet guards."""

from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    build_ng_ppv_beta10_candidate_packet,
)


def _restricted_likelihood():
    return {
        "schema": "ng_restricted_global_kappa_likelihood_v1",
        "ready": True,
        "restricted_kappa_5": -0.048,
        "restricted_kappa_median": -0.019,
        "restricted_kappa_95": 0.019,
        "restricted_kappa_plus_90": 0.038,
        "restricted_kappa_minus_90": 0.029,
    }


def test_ng_ppv_beta10_candidate_packet_carries_source_likelihood_only():
    packet = build_ng_ppv_beta10_candidate_packet(_restricted_likelihood())

    assert packet["schema"] == "ng_ppv_beta10_candidate_packet_v1"
    assert packet["candidate_ready"] is True
    assert packet["source_declared_mapping_ready"] is True
    assert packet["source_native_likelihood_ready"] is True
    assert packet["ppv_beta10_candidate_likelihood_ready"] is True
    assert packet["canonical_engine_beta10_ready"] is False
    assert packet["target_ppv_parameter"] == "beta_1_0_amplitude_branch"
    assert packet["frequency_reference_hz"] == 100.0
    assert packet["candidate_coefficient_units"] == "Gpc^-1"
    assert packet["source_native_constraint"]["kappa_Gpc_inv_median"] == -0.019
    assert packet["sign_conventions"]["engine_canonical_sign"] is None
    assert packet["readiness"]["helicity_harmonization_ready"] is False
    assert packet["readiness"]["dimensionless_ppv_normalization_ready"] is False
    assert packet["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert "source_declared_beta10_not_engine_axis" in packet["blockers"]
    assert "dimensionless_ppv_beta10_normalization_missing" in packet["blockers"]
    assert packet["engine_projection_ready"] is False
    assert packet["claimable_discriminator_now"] is False


def test_ng_ppv_beta10_candidate_packet_blocks_unready_likelihood():
    likelihood = _restricted_likelihood()
    likelihood["ready"] = False

    packet = build_ng_ppv_beta10_candidate_packet(likelihood)

    assert packet["candidate_ready"] is False
    assert "restricted_likelihood_not_ready" in packet["parser_blockers"]
    assert packet["engine_projection_ready"] is False


def test_ng_ppv_beta10_candidate_packet_blocks_missing_fields():
    likelihood = _restricted_likelihood()
    del likelihood["restricted_kappa_plus_90"]

    packet = build_ng_ppv_beta10_candidate_packet(likelihood)

    assert packet["candidate_ready"] is False
    assert packet["missing_fields"] == ["restricted_kappa_plus_90"]
    assert "missing_restricted_likelihood_fields" in packet["parser_blockers"]
