"""Tests for the v2.168 GW parity operator bridge specification."""

from copy import deepcopy

from experiments.gw_parity_operator_bridge_spec import (
    current_missing_parity_bridge_slot,
    current_parity_source_gap_rows,
    diagnose_gw_parity_operator_bridge_spec,
    evaluate_gw_parity_operator_bridge_packet,
    gw_parity_operator_bridge_contract,
    synthetic_ready_parity_bridge_packet,
)


def test_parity_bridge_contract_names_engine_axes_and_required_fields():
    contract = gw_parity_operator_bridge_contract()

    assert contract["route"] == "gw_parity_operator_normalization_search"
    assert "g_R2_parity" in contract["engine_parity_axes"]
    assert "g_R3_parity" in contract["engine_parity_axes"]
    assert "source_backed_operator_normalization" in (
        contract["required_bridge_fields"]
    )
    assert "frequency_reference" in contract["required_bridge_fields"]
    assert "external_adversarial_review_complete" in (
        contract["claim_control_fields"]
    )


def test_synthetic_parity_bridge_is_engine_ready_but_nonclaiming():
    result = evaluate_gw_parity_operator_bridge_packet(
        synthetic_ready_parity_bridge_packet()
    )

    assert result["ready_for_engine_parity_bridge"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["bridge_blockers"] == []
    assert result["route_status"] == "gw_parity_operator_bridge_ready_nonclaiming"
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_real_like_complete_bridge_still_requires_external_review_for_claim():
    packet = deepcopy(synthetic_ready_parity_bridge_packet())
    packet["label"] = "real_like_ppv_to_engine_parity_bridge"
    packet["source_url"] = "https://doi.org/10.0000/real-like-parity-bridge"
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")

    result = evaluate_gw_parity_operator_bridge_packet(packet)

    assert result["ready_for_engine_parity_bridge"] is True
    assert result["synthetic_control"] is False
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]
    assert "framework_claim_controls_disabled" in result["claim_blockers"]


def test_missing_current_bridge_slot_is_blocked_on_required_fields():
    result = evaluate_gw_parity_operator_bridge_packet(
        current_missing_parity_bridge_slot()
    )

    assert result["ready_for_engine_parity_bridge"] is False
    assert result["route_status"] == "gw_parity_operator_bridge_blocked"
    assert "source_backed_operator_normalization" in result["missing_required_fields"]
    assert "engine_axis_target" in result["missing_required_fields"]
    assert "parity_operator_bridge_not_ready" in result["claim_blockers"]


def test_current_source_gap_rows_keep_source_ready_material_nonpromoting():
    rows = current_parity_source_gap_rows()
    ng = next(row for row in rows if row["label"] == "ng_gwtc3_kappa_at_100hz")

    assert len(rows) == 5
    assert all(row["fills_operator_bridge_contract_now"] is False for row in rows)
    assert ng["source_side_likelihood_ready"] is True
    assert ng["engine_adapter_ready"] is False
    assert "missing_engine_axis_map" in ng["adapter_blockers"]
    assert "missing_dimensionful_to_engine_normalization" in ng["adapter_blockers"]


def test_diagnosis_has_ready_spec_but_no_current_real_bridge():
    result = diagnose_gw_parity_operator_bridge_spec()

    assert result["version"] == "v2.168"
    assert result["source_side_likelihood_ready_routes"] == [
        "ng_gwtc3_kappa_at_100hz",
        "callister_sgwb_kappaD_kappaz",
    ]
    assert result["engine_adapter_ready_routes_before_bridge"] == []
    assert result["ready_current_operator_bridges"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "gw_parity_operator_bridge_spec_ready_no_real_bridge"
    )
