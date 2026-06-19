"""Tests for the v2.93 external evidence intake gate."""

from experiments.external_evidence_intake_gate import (
    diagnose_external_evidence_intake_gate,
    evaluate_external_evidence_packet,
    incomplete_g8_packet,
    native_packet_missing_ownership,
    synthetic_complete_external_packet,
    unknown_route_packet,
)


def test_synthetic_complete_packet_is_schema_ready_but_not_claim_ready():
    packet = synthetic_complete_external_packet("future_public_g8_measurement_ingestion")
    result = evaluate_external_evidence_packet(packet)

    assert result["contract_found"] is True
    assert result["schema_ready"] is True
    assert result["claim_ready"] is False
    assert "synthetic_fixture_not_real_source" in result["blockers"]
    assert "claim_gate_not_satisfied:synthetic_fixture_false" in result["blockers"]


def test_incomplete_g8_packet_fails_required_fields_and_route_rejections():
    result = evaluate_external_evidence_packet(incomplete_g8_packet())

    assert result["schema_ready"] is False
    assert result["claim_ready"] is False
    assert "missing_required_fields" in result["blockers"]
    assert "missing_public_likelihood_or_covariance" in result["blockers"]
    assert "wilson_coefficient_normalization_not_engine_g8" in result["blockers"]


def test_native_packet_missing_ownership_is_route_rejected():
    result = evaluate_external_evidence_packet(native_packet_missing_ownership())

    assert result["schema_ready"] is False
    assert result["claim_ready"] is False
    assert "ownership_metadata" in result["missing_fields"]
    assert "ownership_metadata_missing" in result["active_rejection_tests"]
    assert "ownership_metadata_missing" in result["blockers"]


def test_unknown_route_packet_has_no_contract():
    result = evaluate_external_evidence_packet(unknown_route_packet())

    assert result["contract_found"] is False
    assert result["schema_ready"] is False
    assert result["claim_ready"] is False
    assert result["blockers"] == ["unknown_route_no_contract"]
    assert result["status"] == "external_packet_rejected_no_contract"


def test_diagnosis_has_no_claim_ready_sample_packets():
    result = diagnose_external_evidence_intake_gate()

    assert result["version"] == "v2.93"
    assert result["route_status"] == "external_evidence_intake_gate_ready_no_real_packet"
    assert result["contract_route_status"] == "external_evidence_contract_ready_no_packet"
    assert result["claim_ready_sample_packets"] == []
    assert result["claimable_discriminator_now"] is False


def test_diagnosis_records_schema_ready_synthetic_fixture_only():
    result = diagnose_external_evidence_intake_gate()

    assert result["schema_ready_sample_packets"] == [
        "synthetic_complete_future_public_g8_measurement_ingestion"
    ]
    assert result["blocker_counts"]["synthetic_fixture_not_real_source"] == 1
