"""Tests for the v2.98 g8 joint-packet acceptance gate."""

import pytest

from experiments.g8_joint_packet_acceptance_gate import (
    diagnose_g8_joint_packet_acceptance_gate,
    evaluate_g8_joint_packet,
    imprecise_joint_packet,
    incomplete_joint_packet,
    synthetic_ready_joint_g8_g_c_packet,
    synthetic_ready_joint_g8_g_r2_packet,
)


def test_synthetic_ready_g8_gc_packet_is_accepted_but_not_claim_ready():
    result = evaluate_g8_joint_packet(synthetic_ready_joint_g8_g_c_packet())

    assert result["acceptance_ready"] is True
    assert result["claim_ready"] is False
    assert result["g8_total_uncertainty"] == pytest.approx(0.00111803398875)
    assert result["g8_required_total_sigma"] == pytest.approx(0.002)
    assert result["secondary_axis_total_uncertainty"] == pytest.approx(
        0.03162277660168
    )
    assert result["secondary_axis_required_total_sigma"] == pytest.approx(
        0.0508369565217391
    )
    assert result["acceptance_blockers"] == []
    assert result["claim_blockers"] == ["synthetic_fixture_not_real_source"]


def test_synthetic_ready_g8_gr2_packet_uses_best_secondary_axis_threshold():
    result = evaluate_g8_joint_packet(synthetic_ready_joint_g8_g_r2_packet())

    assert result["acceptance_ready"] is True
    assert result["claim_ready"] is False
    assert result["secondary_axis"] == "g_R2"
    assert result["secondary_axis_total_uncertainty"] == pytest.approx(
        0.03807886552932
    )
    assert result["secondary_axis_required_total_sigma"] == pytest.approx(0.0629)


def test_incomplete_joint_packet_fails_required_shape():
    result = evaluate_g8_joint_packet(incomplete_joint_packet())

    assert result["acceptance_ready"] is False
    assert result["claim_ready"] is False
    assert "missing_required_fields" in result["acceptance_blockers"]
    assert "axes_missing_secondary_axis" in result["acceptance_blockers"]
    assert "missing_joint_likelihood_or_covariance" in result["acceptance_blockers"]


def test_imprecise_joint_packet_fails_both_precision_targets():
    result = evaluate_g8_joint_packet(imprecise_joint_packet())

    assert result["synthetic_fixture"] is False
    assert result["acceptance_ready"] is False
    assert "g8_uncertainty_not_below_target" in result["acceptance_blockers"]
    assert (
        "secondary_axis_uncertainty_not_below_target"
        in result["acceptance_blockers"]
    )


def test_diagnosis_has_no_real_claim_ready_samples():
    result = diagnose_g8_joint_packet_acceptance_gate()

    assert result["version"] == "v2.98"
    assert result["route_status"] == "g8_joint_packet_gate_ready_no_real_packet"
    assert result["claimable_discriminator_now"] is False
    assert result["claim_ready_sample_packets"] == []
    assert result["acceptance_ready_sample_packets"] == [
        "synthetic_ready_joint_g8_g_c_packet",
        "synthetic_ready_joint_g8_g_r2_packet",
    ]


def test_diagnosis_records_synthetic_and_precision_blockers():
    result = diagnose_g8_joint_packet_acceptance_gate()

    assert result["blocker_counts"]["synthetic_fixture_not_real_source"] == 2
    assert result["blocker_counts"]["g8_uncertainty_not_below_target"] == 1
    assert (
        result["blocker_counts"]["secondary_axis_uncertainty_not_below_target"]
        == 1
    )
