"""Tests for the v2.159 public R4 shape likelihood search."""

from experiments.r4_public_shape_likelihood_search import (
    LIKELIHOOD_ACCEPTANCE_FIELDS,
    diagnose_r4_public_shape_likelihood_search,
    evaluate_likelihood_candidate,
    public_r4_likelihood_candidates,
    r4_shape_likelihood_acceptance_contract,
)


def test_likelihood_acceptance_contract_targets_engine_r4_axes():
    contract = r4_shape_likelihood_acceptance_contract()

    assert "g_R4_c1" in contract["target_axes"]
    assert "g_R4_c2" in contract["target_axes"]
    assert "g_R4_c3" in contract["target_axes"]
    assert set(LIKELIHOOD_ACCEPTANCE_FIELDS) == set(contract["required_fields"])
    assert "public_likelihood_or_covariance" in contract["required_fields"]


def test_candidate_sources_include_public_data_and_greft_but_no_ready_likelihood():
    candidates = public_r4_likelihood_candidates()
    by_id = {row["candidate_id"]: row for row in candidates}

    assert "gwtc_public_catalog_data" in by_id
    assert by_id["gwtc_public_catalog_data"]["reproducible_data_or_code"] is True
    assert by_id["gwtc_public_catalog_data"][
        "public_likelihood_or_covariance"
    ] is False
    assert "greft_qnm_causality_observability" in by_id
    assert by_id["greft_qnm_causality_observability"][
        "maps_to_bresciani_r4_axes"
    ] is False


def test_each_candidate_fails_likelihood_packet_contract():
    for candidate in public_r4_likelihood_candidates():
        result = evaluate_likelihood_candidate(candidate)

        assert result["ready_for_likelihood_packet"] is False
        assert result["ready_for_framework_claim"] is False
        assert result["failed_criteria"]
        assert "public_likelihood_or_covariance" in result["failed_criteria"]
        assert "maps_to_bresciani_r4_axes" in result["failed_criteria"]


def test_synthetic_complete_candidate_would_pass_packet_gate_but_not_claim_here():
    candidate = {
        "candidate_id": "synthetic_complete_control",
        "evidence_family": "unit_test_control",
        "interpretation": "control only",
    }
    for field in LIKELIHOOD_ACCEPTANCE_FIELDS:
        candidate[field] = True

    result = evaluate_likelihood_candidate(candidate)

    assert result["ready_for_likelihood_packet"] is True
    assert result["failed_criteria"] == []
    assert result["ready_for_framework_claim"] is False


def test_diagnosis_records_no_ready_packet_and_next_manifest():
    result = diagnose_r4_public_shape_likelihood_search()

    assert result["version"] == "v2.159"
    assert result["ready_likelihood_packets"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_measurement_likelihood_claim"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["failure_counts"]["public_likelihood_or_covariance"] == len(
        public_r4_likelihood_candidates()
    )
    assert result["route_status"] == (
        "r4_public_shape_likelihood_search_no_ready_packet"
    )
    assert result["selected_next_build_action"] == (
        "build_r4_shape_likelihood_packet_requirements_manifest"
    )
