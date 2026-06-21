"""Tests for the v2.190 ParSpec-to-engine R4 axis map contract."""

import json
from copy import deepcopy
from pathlib import Path

from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES
from experiments.r4_parspec_engine_axis_map_contract import (
    diagnose_r4_parspec_engine_axis_map_contract,
    evaluate_parspec_engine_axis_map_packet,
    malformed_parspec_engine_axis_map_packet,
    parspec_engine_axis_map_contract,
    synthetic_ready_parspec_engine_axis_map_packet,
)


def test_contract_names_axis_map_requirements():
    contract = parspec_engine_axis_map_contract()

    assert contract["source_axis"] == "ell_qEFT_km"
    assert contract["target_engine_axes"] == list(AXES)
    assert "source_axis_power_policy" in contract["required_packet_fields"]
    assert "operator_basis_map" in contract["required_packet_fields"]
    assert "engine_axis_map" in contract["required_packet_fields"]
    assert "axis_normalization" in contract["required_packet_fields"]
    assert "event_set_policy" in contract["required_packet_fields"]


def test_synthetic_complete_packet_passes_attachment_but_not_claim_gate():
    result = evaluate_parspec_engine_axis_map_packet(
        synthetic_ready_parspec_engine_axis_map_packet()
    )

    assert result["source_bridge_ready"] is True
    assert result["axis_map_ready"] is True
    assert result["likelihood_attachment_ready"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "parspec_engine_axis_map_packet_ready_nonclaiming"
    )
    assert result["map_blockers"] == []
    assert result["attachment_blockers"] == []
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_current_v2188_bridge_fails_exact_map_and_attachment_subpieces():
    result = diagnose_r4_parspec_engine_axis_map_contract()
    current = result["current_v2188_evaluation"]

    assert current["source_bridge_ready"] is True
    assert current["axis_map_ready"] is False
    assert current["likelihood_attachment_ready"] is False
    assert "source_axis_power_policy_missing" in current["map_blockers"]
    assert "operator_basis_map_missing" in current["map_blockers"]
    assert "engine_axis_orientation_missing" in current["map_blockers"]
    assert "axis_normalization_missing" in current["map_blockers"]
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        current["attachment_blockers"]
    )
    assert "event_set_mismatch_gw170608_vs_gw150914_gw200129" in (
        current["attachment_blockers"]
    )


def test_real_like_packet_without_public_likelihood_remains_blocked():
    packet = deepcopy(synthetic_ready_parspec_engine_axis_map_packet())
    packet["source_type"] = "source_backed_parspec_qeft_axis_map"
    packet["claim_controls"].pop("synthetic_control_not_claim_evidence")
    packet["likelihood_reference"] = {
        "status": "published_bound_only",
        "source_axis": "ell_qEFT_km",
        "posterior_or_likelihood_exported": False,
    }

    result = evaluate_parspec_engine_axis_map_packet(packet)

    assert result["axis_map_ready"] is True
    assert result["likelihood_attachment_ready"] is False
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        result["attachment_blockers"]
    )
    assert "synthetic_control_not_claim_evidence" not in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]


def test_malformed_packet_blocks_source_bridge_and_claim_controls():
    result = evaluate_parspec_engine_axis_map_packet(
        malformed_parspec_engine_axis_map_packet()
    )

    assert result["source_bridge_ready"] is False
    assert result["axis_map_ready"] is False
    assert "parspec_primary_source_url_missing" in result["all_blockers"]
    assert "source_axis_units_not_km" in result["all_blockers"]
    assert "target_engine_axes_mismatch" in result["all_blockers"]
    assert "engine_axis_vector_incomplete" in result["all_blockers"]
    assert "claim_use_not_disabled" in result["all_blockers"]


def test_diagnosis_keeps_contract_nonclaiming_and_selects_real_packet_next():
    result = diagnose_r4_parspec_engine_axis_map_contract()

    assert result["version"] == "v2.190"
    assert result["contract_ready"] is True
    assert result["current_axis_map_ready"] is False
    assert result["current_likelihood_attachment_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "parspec_engine_axis_map_contract_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "derive_source_backed_parspec_qeft_axis_map_or_acquire_public_likelihood"
    )


def test_committed_artifact_records_current_v2188_blockers():
    path = Path(
        "experiments/results/v2.190/"
        "r4_parspec_engine_axis_map_contract.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.190"
    assert result["contract_ready"] is True
    assert result["current_v2188_evaluation"]["axis_map_ready"] is False
    assert result["current_v2188_evaluation"][
        "likelihood_attachment_ready"
    ] is False
    assert result["ready_for_framework_claim"] is False
