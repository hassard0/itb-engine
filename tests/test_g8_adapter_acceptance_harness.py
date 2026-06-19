"""Regression tests for the v2.79 g_8 adapter acceptance harness."""

from experiments.g8_adapter_acceptance_harness import (
    current_cms_energy_correlator_packet,
    diagnose_g8_adapter_acceptance_harness,
    evaluate_g8_adapter_packet,
    synthetic_ready_adapter_packet,
)


def test_synthetic_adapter_fixture_passes_acceptance_but_not_real_claim():
    result = evaluate_g8_adapter_packet(synthetic_ready_adapter_packet())

    assert result["adapter_acceptance_ready"] is True
    assert result["promotion_guard"]["ready_for_promotion"] is True
    assert result["ready_for_g8_claim"] is False
    assert result["claim_blockers"] == ["synthetic_fixture_not_real_source"]


def test_missing_likelihood_blocks_adapter_acceptance():
    packet = synthetic_ready_adapter_packet()
    packet["covariance_or_likelihood"] = None

    result = evaluate_g8_adapter_packet(packet)

    assert result["adapter_acceptance_ready"] is False
    assert "missing_public_likelihood_or_covariance" in result["acceptance_blockers"]
    assert "external_measurement_evidence_not_ready" not in result["acceptance_blockers"]
    assert result["promotion_guard"]["ready_for_promotion"] is True


def test_mixed_lower_moments_without_bounded_covariance_blocks_acceptance():
    packet = synthetic_ready_adapter_packet()
    packet["jacobian_or_projection_to_g_8"] = {
        "g_4": 0.25,
        "g_6": -0.1,
        "g_8": 1.0,
    }
    packet["mixing_with_g_4_g_6"] = "uncontrolled"

    result = evaluate_g8_adapter_packet(packet)

    assert result["projection_summary"]["pure_g8_projection"] is False
    assert (
        "g8_not_isolated_from_lower_matter_moments"
        in result["acceptance_blockers"]
    )


def test_wrong_axis_blocks_g8_adapter_acceptance():
    packet = synthetic_ready_adapter_packet()
    packet["axis"] = "g_C"

    result = evaluate_g8_adapter_packet(packet)

    assert result["adapter_acceptance_ready"] is False
    assert "axis_not_g8" in result["acceptance_blockers"]


def test_diagnosis_has_ready_harness_but_no_real_claim_ready_packet():
    result = diagnose_g8_adapter_acceptance_harness()

    assert result["version"] == "v2.79"
    assert result["route_status"] == "g8_adapter_acceptance_harness_ready_no_real_packet"
    assert result["synthetic_fixture"]["adapter_acceptance_ready"] is True
    assert result["real_claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False


def test_current_cms_seed_fails_engine_g8_gate():
    result = evaluate_g8_adapter_packet(current_cms_energy_correlator_packet())

    assert result["adapter_acceptance_ready"] is False
    assert result["ready_for_g8_claim"] is False
    assert "observable_basis_not_adapter_supported" in result["acceptance_blockers"]
    assert "wilson_coefficient_normalization_not_engine_g8" in (
        result["acceptance_blockers"]
    )
