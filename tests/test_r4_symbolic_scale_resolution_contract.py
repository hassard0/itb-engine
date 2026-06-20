"""Tests for the v2.170 R4 symbolic-scale resolution contract."""

from copy import deepcopy

from experiments.r4_symbolic_scale_resolution_contract import (
    current_r4_scale_source_gap_rows,
    current_symbolic_only_r4_scale_slot,
    diagnose_r4_symbolic_scale_resolution_contract,
    evaluate_r4_scale_policy_packet,
    r4_symbolic_scale_resolution_contract,
    synthetic_ready_r4_scale_policy_packet,
)


def test_scale_resolution_contract_names_required_numeric_policy_fields():
    contract = r4_symbolic_scale_resolution_contract()

    assert contract["route"] == "r4_symbolic_scale_resolution"
    assert contract["engine_scale_axis"] == "Lambda_R4"
    assert "four_dimensional_frame_policy" in (
        contract["required_scale_policy_fields"]
    )
    assert "alpha_prime_to_engine_lambda_r4" in (
        contract["required_scale_policy_fields"]
    )
    assert "compactification_volume_or_moduli_policy" in (
        contract["required_scale_policy_fields"]
    )
    assert "external_adversarial_review_complete" in (
        contract["claim_control_fields"]
    )


def test_synthetic_complete_scale_policy_is_engine_ready_but_nonclaiming():
    result = evaluate_r4_scale_policy_packet(
        synthetic_ready_r4_scale_policy_packet()
    )

    assert result["ready_for_numeric_lambda_r4_scale_policy"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["scale_policy_blockers"] == []
    assert result["route_status"] == "r4_numeric_scale_policy_ready_nonclaiming"
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_real_like_complete_scale_policy_still_requires_external_review():
    packet = deepcopy(synthetic_ready_r4_scale_policy_packet())
    packet["label"] = "real_like_numeric_lambda_r4_scale_policy"
    packet["source_url"] = "https://doi.org/10.0000/real-like-r4-scale-policy"
    packet["source_type"] = "source_backed_compactification_policy"
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_r4_scale_policy_packet(packet)

    assert result["ready_for_numeric_lambda_r4_scale_policy"] is True
    assert result["synthetic_control"] is False
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]
    assert "framework_claim_controls_disabled" in result["claim_blockers"]


def test_current_symbolic_only_slot_fails_numeric_scale_contract():
    result = evaluate_r4_scale_policy_packet(current_symbolic_only_r4_scale_slot())

    assert result["ready_for_numeric_lambda_r4_scale_policy"] is False
    assert result["route_status"] == "r4_numeric_scale_policy_blocked"
    assert "alpha_prime_to_engine_lambda_r4" in result["missing_required_fields"]
    assert "four_dimensional_frame_policy" in result["missing_required_fields"]
    assert "engine_lambda_r4_numeric_value" in result["missing_required_fields"]
    assert "numeric_lambda_r4_scale_policy_not_ready" in result["claim_blockers"]


def test_numeric_collapse_without_source_backing_is_rejected():
    packet = deepcopy(synthetic_ready_r4_scale_policy_packet())
    packet["alpha_prime_to_engine_lambda_r4"]["status"] = "symbolic_only"
    packet["engine_lambda_r4_numeric_value"]["source_backed"] = False
    packet["field_redefinition_policy"]["field_redefinition_ambiguity_closed"] = False

    result = evaluate_r4_scale_policy_packet(packet)

    assert result["ready_for_numeric_lambda_r4_scale_policy"] is False
    assert "numeric_alpha_prime_to_lambda_r4_not_source_backed" in (
        result["scale_policy_blockers"]
    )
    assert "engine_lambda_r4_source_backing_missing" in (
        result["scale_policy_blockers"]
    )
    assert "field_redefinition_ambiguity_not_closed" in (
        result["scale_policy_blockers"]
    )


def test_current_source_gap_rows_keep_all_real_rows_nonpromoting():
    rows = current_r4_scale_source_gap_rows()
    labels = {row["label"] for row in rows}

    assert "russo_1997_type_iib_virasoro_shapiro" in labels
    assert "symbolic_lambda_r4_sidecar_v1" in labels
    assert all(row["fills_numeric_scale_contract_now"] is False for row in rows)
    assert any(
        "engine Lambda_R4 numeric convention" in (
            row["missing_contract_capabilities"]
        )
        for row in rows
    )
    assert any(
        "numeric_alpha_prime_to_lambda_r4_value_missing" in (
            row["missing_contract_capabilities"]
        )
        for row in rows
    )


def test_diagnosis_has_ready_contract_but_no_current_numeric_policy():
    result = diagnose_r4_symbolic_scale_resolution_contract()

    assert result["version"] == "v2.170"
    assert result["symbolic_lambda_policy_ready"] is True
    assert result["symbolic_query_ready"] is True
    assert result["numeric_lambda_r4_ready_before_contract"] is False
    assert result["frame_scale_numeric_ready_candidates_before_contract"] == []
    assert result["ready_current_numeric_scale_policies"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "r4_scale_resolution_contract_ready_no_numeric_policy"
    )
