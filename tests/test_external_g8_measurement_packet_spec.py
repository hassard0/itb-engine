"""Tests for the v2.166 external G8 measurement packet specification."""

from copy import deepcopy

from experiments.external_g8_measurement_packet_spec import (
    current_missing_external_g8_packet_slot,
    current_source_gap_rows,
    diagnose_external_g8_measurement_packet_spec,
    evaluate_external_g8_measurement_packet,
    external_g8_measurement_packet_contract,
    synthetic_alpha_join_g8_packet,
)


def test_contract_extends_base_g8_adapter_with_alpha_join_fields():
    contract = external_g8_measurement_packet_contract()

    assert "central_value_or_bound" in contract["base_g8_adapter_fields"]
    assert "joint_covariance_export" in contract["alpha_join_extension_fields"]
    assert "cross_covariance_with_alpha" in contract["alpha_join_extension_fields"]
    assert "analysis_code_or_likelihood_sampler" in (
        contract["source_reanalysis_required_fields"]
    )
    assert "external_adversarial_review_complete" in contract["claim_control_fields"]
    assert "joint_likelihood_or_covariance" in (
        contract["required_capabilities_for_alpha_join"]
    )


def test_synthetic_complete_packet_is_engine_join_ready_but_nonclaiming():
    result = evaluate_external_g8_measurement_packet(
        synthetic_alpha_join_g8_packet()
    )

    assert result["ready_for_engine_g8_join_packet"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions"] == []
    assert result["base_g8_adapter_evaluation"]["adapter_acceptance_ready"] is True
    assert result["alpha_join_extension_evaluation"][
        "ready_for_alpha_join_extension"
    ] is True
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_real_like_complete_packet_still_requires_external_review_for_claim():
    packet = deepcopy(synthetic_alpha_join_g8_packet())
    packet["label"] = "real_like_external_g8_packet"
    packet["source_url"] = "https://doi.org/10.0000/real-like-g8-packet"
    packet["synthetic_fixture"] = False
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_external_g8_measurement_packet(packet)

    assert result["ready_for_engine_g8_join_packet"] is True
    assert result["synthetic_control"] is False
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]
    assert "framework_claim_controls_disabled" in result["claim_blockers"]


def test_missing_current_slot_fails_base_and_join_gates():
    result = evaluate_external_g8_measurement_packet(
        current_missing_external_g8_packet_slot()
    )

    assert result["ready_for_engine_g8_join_packet"] is False
    assert "base_g8_adapter_gate_failed" in result["packet_blockers"]
    assert "alpha_join_extension_gate_failed" in result["packet_blockers"]
    assert result["alpha_join_extension_evaluation"][
        "missing_join_extension_fields"
    ] != []


def test_current_source_gap_rows_have_no_contract_ready_packet():
    rows = current_source_gap_rows()

    assert len(rows) >= 7
    assert all(row["fills_external_g8_packet_contract_now"] is False for row in rows)
    assert any(row["g8_axis_candidate"] is True for row in rows)
    assert any(
        "external_numeric_measurement" in row["missing_gate_capabilities"]
        for row in rows
        if row["g8_axis_candidate"]
    )


def test_diagnosis_is_ready_spec_but_no_real_external_packet():
    result = diagnose_external_g8_measurement_packet_spec()

    assert result["version"] == "v2.166"
    assert result["alpha_packet_ready_for_g8_join"] is True
    assert result["ready_current_external_g8_packets"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "external_g8_packet_spec_ready_no_real_packet"
    assert result["selected_next_build_action"] == (
        "search_or_request_real_external_g8_packet_that_fills_v2_166_contract"
    )
