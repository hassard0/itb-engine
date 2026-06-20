"""Tests for the v2.128 G8 sidecar acceptance gate."""

from experiments.gw_alpha_g8_sidecar_acceptance_gate import (
    diagnose_gw_alpha_g8_sidecar_acceptance_gate,
    evaluate_g8_sidecar_packet,
    incomplete_g8_sidecar_packet,
    synthetic_ready_g8_sidecar_packet,
)


def test_synthetic_ready_sidecar_passes_acceptance_but_not_claim():
    result = evaluate_g8_sidecar_packet(synthetic_ready_g8_sidecar_packet())

    assert result["acceptance_ready"] is True
    assert result["acceptance_blockers"] == []
    assert result["claim_ready"] is False
    assert result["claim_blockers"] == ["synthetic_fixture_not_real_source"]
    assert result["likelihood_summary"]["public_engine_usable"] is True
    assert result["cross_covariance_summary"]["acceptable"] is True


def test_incomplete_sidecar_is_rejected_with_actionable_blockers():
    result = evaluate_g8_sidecar_packet(incomplete_g8_sidecar_packet())

    assert result["acceptance_ready"] is False
    assert result["claim_ready"] is False
    assert "missing_required_fields" in result["acceptance_blockers"]
    assert "engine_g8_normalization_missing" in result["acceptance_blockers"]
    assert "public_g8_likelihood_or_covariance_missing" in (
        result["acceptance_blockers"]
    )
    assert "g8_systematics_not_closed" in result["acceptance_blockers"]


def test_sidecar_diagnosis_has_no_real_claim_ready_packet():
    result = diagnose_gw_alpha_g8_sidecar_acceptance_gate()

    assert result["version"] == "v2.128"
    assert result["acceptance_ready_sample_packets"] == [
        "synthetic_ready_g8_sidecar_packet",
    ]
    assert result["claim_ready_sample_packets"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "g8_sidecar_acceptance_gate_ready_no_real_packet"
    )
    assert result["selected_next_build_action"] == (
        "run_gate_on_real_external_g8_sidecar_packet"
    )
