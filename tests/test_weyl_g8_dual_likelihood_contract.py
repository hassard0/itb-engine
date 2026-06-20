"""Tests for the v2.172 Weyl/G8 dual-likelihood contract."""

from copy import deepcopy

from experiments.weyl_g8_dual_likelihood_contract import (
    current_missing_weyl_g8_dual_likelihood_slot,
    current_weyl_g8_source_gap_rows,
    diagnose_weyl_g8_dual_likelihood_contract,
    evaluate_weyl_g8_dual_likelihood_packet,
    synthetic_ready_weyl_g8_dual_likelihood_packet,
    weyl_g8_dual_likelihood_contract,
)


def test_contract_wraps_base_joint_gate_with_weyl_extension_fields():
    contract = weyl_g8_dual_likelihood_contract()

    assert contract["route"] == "weyl_g8_joint_frontier"
    assert contract["external_object"] == "joint_engine_gC_g8_likelihood"
    assert contract["target_axes"] == ["g_8", "g_C"]
    assert "central_values" in contract["base_joint_packet_fields"]
    assert "engine_g_c_packet" in contract["weyl_extension_fields"]
    assert "engine_g8_packet" in contract["weyl_extension_fields"]
    assert "external_adversarial_review_complete" in (
        contract["claim_control_fields"]
    )


def test_synthetic_weyl_g8_packet_passes_engine_gate_but_not_claim_gate():
    result = evaluate_weyl_g8_dual_likelihood_packet(
        synthetic_ready_weyl_g8_dual_likelihood_packet()
    )

    assert result["ready_for_weyl_g8_dual_likelihood"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions"] == []
    assert result["base_joint_packet_evaluation"]["acceptance_ready"] is True
    assert result["weyl_extension_evaluation"][
        "ready_for_weyl_g8_extension"
    ] is True
    assert result["packet_blockers"] == []
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_real_like_complete_packet_still_requires_external_review():
    packet = deepcopy(synthetic_ready_weyl_g8_dual_likelihood_packet())
    packet["label"] = "real_like_weyl_g8_dual_likelihood_packet"
    packet["synthetic_fixture"] = False
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_weyl_g8_dual_likelihood_packet(packet)

    assert result["ready_for_weyl_g8_dual_likelihood"] is True
    assert result["synthetic_control"] is False
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]
    assert "framework_claim_controls_disabled" in result["claim_blockers"]


def test_current_missing_packet_slot_fails_base_and_extension_gates():
    result = evaluate_weyl_g8_dual_likelihood_packet(
        current_missing_weyl_g8_dual_likelihood_slot()
    )

    assert result["ready_for_weyl_g8_dual_likelihood"] is False
    assert "base_g8_gc_joint_gate_failed" in result["packet_blockers"]
    assert "weyl_g8_extension_gate_failed" in result["packet_blockers"]
    assert "engine_g_c_packet" in result["weyl_extension_evaluation"][
        "missing_weyl_extension_fields"
    ]
    assert "weyl_g8_dual_likelihood_not_ready" in result["claim_blockers"]


def test_extension_rejects_unbounded_correlation_or_weak_statistic():
    packet = deepcopy(synthetic_ready_weyl_g8_dual_likelihood_packet())
    packet["cross_axis_correlation_model"]["status"] = "open"
    packet["joint_exclusion_statistic"]["sigma_distance"] = 1.5

    result = evaluate_weyl_g8_dual_likelihood_packet(packet)

    assert result["ready_for_weyl_g8_dual_likelihood"] is False
    assert "cross_axis_correlation_not_bounded" in (
        result["weyl_extension_evaluation"]["extension_blockers"]
    )
    assert "joint_exclusion_statistic_below_2sigma" in (
        result["weyl_extension_evaluation"]["extension_blockers"]
    )


def test_current_source_gap_rows_include_g8_and_gc_candidates_nonpromoting():
    rows = current_weyl_g8_source_gap_rows()
    labels = {row["label"] for row in rows}

    assert "bresciani_partial_wave_unitarity_bounds_2025" in labels
    assert "sutton_quadratic_weyl_constraints_2025" in labels
    assert all(row["fills_weyl_g8_contract_now"] is False for row in rows)
    assert any(row["g8_axis_candidate"] is True for row in rows)
    assert any(row["g_c_axis_candidate"] is True for row in rows)
    assert any(
        "joint_likelihood_or_covariance" in row["missing_gate_capabilities"]
        or "joint_covariance" in row["missing_gate_capabilities"]
        for row in rows
    )


def test_diagnosis_has_ready_contract_but_no_real_weyl_g8_packet():
    result = diagnose_weyl_g8_dual_likelihood_contract()

    assert result["version"] == "v2.172"
    assert result["selected_source_queue_build_route"] == (
        "gw_reanalysis_to_joint_secondary_packet"
    )
    assert result["ready_current_weyl_g8_packets"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "weyl_g8_dual_likelihood_contract_ready_no_real_packet"
    )
