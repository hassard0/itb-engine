"""Tests for the v2.205 pyRing-to-Bresciani orientation audit."""

from __future__ import annotations

import json

from experiments.r4_parspec_pyring_source_probe import PYRING_SOURCE_DIRECTIONS
from experiments.r4_parspec_pyring_to_bresciani_orientation import (
    DEFAULT_OUT,
    DISALLOWED_ORIENTATION_USES,
    REQUIRED_BRESCIANI_COORDINATES,
    REQUIRED_ORIENTATION_EVIDENCE,
    diagnose_r4_parspec_pyring_to_bresciani_orientation,
    evaluate_pyring_to_bresciani_orientation_audit,
    malformed_synthetic_orientation_claim,
    pyring_to_bresciani_orientation_audit_packet,
)


def test_orientation_packet_records_required_coordinate_systems() -> None:
    packet = pyring_to_bresciani_orientation_audit_packet()
    manifest = packet["source_manifest"]

    assert manifest["pyring"]["branch"] == "EFT_QNMs"
    assert len(manifest["pyring"]["quartic_tables"]) == 6
    assert tuple(manifest["pyring"]["source_directions"]) == (
        PYRING_SOURCE_DIRECTIONS
    )
    assert tuple(manifest["bresciani"]["source_coordinates"]) == (
        REQUIRED_BRESCIANI_COORDINATES
    )
    assert manifest["bresciani"]["engine_projection_axes"] == [
        "g_R4_c1",
        "g_R4_c2",
        "g_R4_c3",
    ]
    assert tuple(packet["required_orientation_evidence"]) == (
        REQUIRED_ORIENTATION_EVIDENCE
    )


def test_current_evidence_is_no_map_not_orientation_claim() -> None:
    packet = pyring_to_bresciani_orientation_audit_packet()
    evidence = packet["current_evidence"]

    assert evidence["pyring_has_hash_pinned_qnm_branch_tables"] is True
    assert evidence["bresciani_dictionary_maps_K_to_engine_axes"] is True
    assert evidence["normalization_policy_isolated"] is True
    assert evidence["pyring_has_bresciani_K_coordinate_labels"] is False
    assert evidence["pyring_has_field_redefinition_policy_to_bresciani_basis"] is False
    assert evidence["pyring_plus_minus_are_independent_operator_axes"] is False
    assert evidence["public_likelihood_attached"] is False
    assert packet["candidate_orientation_map"]["status"] == "absent"


def test_public_primary_source_findings_do_not_promote_map() -> None:
    packet = pyring_to_bresciani_orientation_audit_packet()
    findings = packet["public_primary_source_findings"]

    assert len(findings) == 6
    assert any(
        finding["source"] == "pyRing waveform.pyx"
        and "QNM branches" in finding["finding"]
        for finding in findings
    )
    assert any(
        finding["source"].startswith("Bresciani")
        and "does not tie" in finding["finding"]
        for finding in findings
    )
    assert all(
        "Bresciani" in finding["finding"]
        or "pyRing" in finding["finding"]
        or "QNM" in finding["finding"]
        for finding in findings
    )
    assert (
        packet["current_evidence"]["pyring_has_bresciani_K_coordinate_labels"]
        is False
    )
    assert packet["claim_controls"]["orientation_map_source_backed"] is False


def test_label_overlap_is_not_promoted_to_orientation_evidence() -> None:
    packet = pyring_to_bresciani_orientation_audit_packet()
    intersection = packet["label_intersection"]

    assert intersection["pyring_direction_labels"] == list(PYRING_SOURCE_DIRECTIONS)
    assert intersection["bresciani_coordinate_labels"] == list(
        REQUIRED_BRESCIANI_COORDINATES
    )
    assert intersection["shared_tokens_are_orientation_evidence"] is False


def test_evaluation_marks_no_map_ledger_ready_but_claim_gate_closed() -> None:
    evaluation = evaluate_pyring_to_bresciani_orientation_audit()

    assert evaluation["pyring_to_bresciani_orientation_audit_ready"] is True
    assert evaluation["no_map_ledger_ready"] is True
    assert evaluation["pyring_to_bresciani_orientation_source_backed"] is False
    assert evaluation["synthetic_orientation_allowed"] is False
    assert evaluation["rank_only_orientation_allowed"] is False
    assert evaluation["qnm_to_bresciani_sensitivity_ready"] is False
    assert evaluation["public_likelihood_ready"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["blockers"] == []
    assert "pyring_to_bresciani_orientation_audit_complete" in (
        evaluation["resolved_v2204_subpieces"]
    )
    assert "pyring_quartic_direction_to_bresciani_axis_orientation_missing" in (
        evaluation["remaining_claim_blockers"]
    )
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in (
        evaluation["remaining_claim_blockers"]
    )


def test_disallowed_orientation_uses_are_complete() -> None:
    packet = pyring_to_bresciani_orientation_audit_packet()

    assert set(DISALLOWED_ORIENTATION_USES).issubset(packet["disallowed_uses"])
    assert "synthetic_branch_to_operator_map" in packet["disallowed_uses"]
    assert "rank_only_orientation_claim" in packet["disallowed_uses"]
    assert "pyring_plus_minus_as_independent_wilson_axes" in (
        packet["disallowed_uses"]
    )
    assert packet["claim_controls"]["claim_use_allowed"] is False
    assert packet["claim_controls"]["orientation_map_source_backed"] is False


def test_malformed_synthetic_orientation_claim_fails() -> None:
    evaluation = evaluate_pyring_to_bresciani_orientation_audit(
        malformed_synthetic_orientation_claim()
    )

    assert evaluation["pyring_to_bresciani_orientation_audit_ready"] is False
    assert "unexpected_source_backed_orientation_claim" in evaluation["blockers"]
    assert "source_backed_orientation_field_policy_missing" in evaluation["blockers"]
    assert "source_backed_orientation_line_refs_missing" in evaluation["blockers"]
    assert "synthetic_orientation_not_forbidden" in evaluation["blockers"]
    assert "claim_use_not_disabled" in evaluation["blockers"]
    assert "orientation_claim_not_disabled" in evaluation["blockers"]


def test_diagnosis_records_nonclaiming_route_status() -> None:
    result = diagnose_r4_parspec_pyring_to_bresciani_orientation()

    assert result["version"] == "v2.205"
    assert result["pyring_to_bresciani_orientation_audit_ready"] is True
    assert result["pyring_to_bresciani_orientation_source_backed"] is False
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "pyring_to_bresciani_no_map_ledger_ready_claim_gate_blocked"
    )


def test_committed_artifact_matches_orientation_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.205"
    assert artifact["route_status"] == (
        "pyring_to_bresciani_no_map_ledger_ready_claim_gate_blocked"
    )
    assert artifact["pyring_to_bresciani_orientation_audit_ready"] is True
    assert artifact["pyring_to_bresciani_orientation_source_backed"] is False
    assert artifact["ready_for_framework_claim"] is False
