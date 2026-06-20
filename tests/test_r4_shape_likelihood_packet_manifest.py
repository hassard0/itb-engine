"""Tests for the v2.160 R4 shape likelihood packet manifest."""

from copy import deepcopy

from experiments.r4_shape_likelihood_packet_manifest import (
    REQUIRED_PACKET_FIELDS,
    TARGET_AXES,
    diagnose_r4_shape_likelihood_packet_manifest,
    empty_r4_shape_likelihood_packet,
    evaluate_r4_shape_likelihood_packet,
    r4_shape_likelihood_packet_schema,
    synthetic_complete_r4_shape_likelihood_packet,
)


def test_schema_names_required_fields_and_target_axes():
    schema = r4_shape_likelihood_packet_schema()

    assert set(schema["required_packet_fields"]) == set(REQUIRED_PACKET_FIELDS)
    assert set(schema["target_axes"]) == set(TARGET_AXES)
    assert "public_covariance_matrix" in schema["valid_likelihood_statuses"]
    assert "g_R4_c1" in schema["acceptance_contract"]["target_axes"]


def test_empty_packet_is_not_likelihood_ready():
    result = evaluate_r4_shape_likelihood_packet(empty_r4_shape_likelihood_packet())

    assert result["ready_for_engine_likelihood_packet"] is False
    assert result["ready_for_framework_claim"] is False
    assert "target_axes_incomplete" in result["blockers"]
    assert "public_likelihood_or_covariance_missing" in result["blockers"]
    assert "excluding_discriminator_math_missing" in result["blockers"]


def test_synthetic_complete_control_is_packet_ready_but_not_claim_evidence():
    result = evaluate_r4_shape_likelihood_packet(
        synthetic_complete_r4_shape_likelihood_packet()
    )

    assert result["ready_for_engine_likelihood_packet"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["blockers"] == ["synthetic_control_not_claim_evidence"]
    assert result["likelihood_status"] == "public_covariance_matrix"


def test_real_complete_like_packet_can_be_likelihood_ready_not_claim_ready():
    packet = deepcopy(synthetic_complete_r4_shape_likelihood_packet())
    packet["packet_id"] = "real_complete_like_packet"
    packet["source_url"] = "https://example.org/public-r4-likelihood"
    packet["provenance"]["synthetic_control"] = False
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_r4_shape_likelihood_packet(packet)

    assert result["ready_for_engine_likelihood_packet"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["blockers"] == []


def test_manifest_diagnosis_is_ready_nonclaiming_schema_only():
    result = diagnose_r4_shape_likelihood_packet_manifest()

    assert result["version"] == "v2.160"
    assert result["ready_likelihood_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "r4_shape_likelihood_packet_manifest_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "monitor_or_ingest_future_r4_likelihood_sources"
    )
