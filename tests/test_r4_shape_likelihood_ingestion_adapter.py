"""Tests for the v2.162 R4 shape likelihood ingestion adapter."""

from copy import deepcopy

from experiments.r4_shape_likelihood_ingestion_adapter import (
    diagnose_r4_shape_likelihood_ingestion_adapter,
    evaluate_r4_shape_likelihood_ingestion_packet,
    r4_shape_likelihood_score,
    synthetic_offset_r4_likelihood_packet,
)
from experiments.r4_shape_likelihood_packet_manifest import (
    empty_r4_shape_likelihood_packet,
    synthetic_complete_r4_shape_likelihood_packet,
)


def test_synthetic_exact_packet_ingests_and_scores_zero_distance_nonclaiming():
    result = evaluate_r4_shape_likelihood_ingestion_packet(
        synthetic_complete_r4_shape_likelihood_packet()
    )

    assert result["adapter_ingestion_ready"] is True
    assert result["ready_for_shape_likelihood_diagnostic"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions"] == []
    assert result["shape_score"]["score_available"] is True
    assert result["shape_score"]["chi_square_to_string_tree_r4_shape"] == 0.0
    assert result["shape_score"]["sigma_distance_to_string_tree_r4_shape"] == 0.0
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_offset_packet_computes_covariance_weighted_shape_distance():
    result = evaluate_r4_shape_likelihood_ingestion_packet(
        synthetic_offset_r4_likelihood_packet()
    )

    assert result["adapter_ingestion_ready"] is True
    assert result["shape_score"]["score_available"] is True
    assert result["shape_score"]["chi_square_to_string_tree_r4_shape"] == 1.0
    assert result["shape_score"]["sigma_distance_to_string_tree_r4_shape"] == 1.0
    assert result["shape_score"]["inside_one_sigma_shape_tube"] is True


def test_real_like_packet_can_ingest_but_still_cannot_claim():
    packet = deepcopy(synthetic_complete_r4_shape_likelihood_packet())
    packet["packet_id"] = "real_like_public_r4_packet"
    packet["source_url"] = "https://example.org/public-r4-shape-likelihood"
    packet["provenance"]["synthetic_control"] = False
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_r4_shape_likelihood_ingestion_packet(packet)

    assert result["adapter_ingestion_ready"] is True
    assert result["synthetic_control"] is False
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]
    assert "framework_claim_controls_disabled" in result["claim_blockers"]


def test_empty_public_slot_fails_manifest_and_shape_score():
    packet = empty_r4_shape_likelihood_packet()
    result = evaluate_r4_shape_likelihood_ingestion_packet(packet)

    assert result["adapter_ingestion_ready"] is False
    assert result["ready_for_shape_likelihood_diagnostic"] is False
    assert "manifest_packet_gate_failed" in result["ingestion_blockers"]
    assert "shape_likelihood_score_unavailable" in result["ingestion_blockers"]


def test_singular_covariance_blocks_shape_score():
    packet = synthetic_complete_r4_shape_likelihood_packet()
    packet["likelihood"]["covariance"] = [
        [0.01, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.01],
    ]

    result = r4_shape_likelihood_score(packet)

    assert result["score_available"] is False
    assert "covariance_nonpositive_variance_g_R4_c2" in result["blockers"]


def test_diagnosis_has_ready_adapter_but_no_current_public_packet_claim():
    result = diagnose_r4_shape_likelihood_ingestion_adapter()

    assert result["version"] == "v2.162"
    assert result["route"] == "future_public_r4_shape_likelihood_ingestion"
    assert result["synthetic_exact_control"]["adapter_ingestion_ready"] is True
    assert result["current_public_packet_assessments"][0]["adapter_ingestion_ready"] is False
    assert result["ready_public_r4_likelihood_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "r4_shape_likelihood_ingestion_adapter_ready_no_public_packet"
    )
