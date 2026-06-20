"""Tests for the v2.146 K-convention bridge audit."""

from experiments.k_convention_bridge_audit import (
    candidate_k_bridges,
    diagnose_k_convention_bridge_audit,
    evaluate_k_bridge_candidate,
    k_bridge_acceptance_criteria,
)


def test_acceptance_criteria_require_source_and_dimensionless_bridge():
    criteria = k_bridge_acceptance_criteria()

    assert "source_backed_primary_or_rederived" in criteria
    assert "dimensionless_against_v2_144_shape" in criteria
    assert "independent_of_gravitational_coupling_convention" in criteria


def test_raw_supergravity_pole_match_is_rejected_for_kappa_dependence():
    candidates = {row["candidate"]: row for row in candidate_k_bridges()}
    result = evaluate_k_bridge_candidate(candidates["match_supergravity_pole_raw"])

    assert result["candidate_expression"] == "K_Russo / shape = 1/(64*kappa^4)"
    assert result["acceptable_k_bridge"] is False
    assert "bridge_depends_on_kappa_convention" in result["blockers"]
    assert "dimensionless_against_v2_144_shape" in result["failed_criteria"]


def test_unit_shape_bridge_is_rejected_as_convention_not_source():
    candidates = {row["candidate"]: row for row in candidate_k_bridges()}
    result = evaluate_k_bridge_candidate(candidates["unit_shape_bridge"])

    assert result["candidate_expression"] == "K_Russo / shape = 1"
    assert result["acceptable_k_bridge"] is False
    assert "bridge_is_engine_convention_not_source_backed" in result["blockers"]
    assert "source_backed_primary_or_rederived" in result["failed_criteria"]


def test_primary_gross_witten_route_remains_missing():
    candidates = {row["candidate"]: row for row in candidate_k_bridges()}
    result = evaluate_k_bridge_candidate(candidates["gross_witten_primary_k_formula"])

    assert result["acceptable_k_bridge"] is False
    assert "primary_k_formula_not_ingested" in result["blockers"]
    assert "gross_witten_pdf_or_ocr_still_required" in result["blockers"]


def test_diagnosis_records_no_acceptable_bridge_and_no_claims():
    result = diagnose_k_convention_bridge_audit()

    assert result["version"] == "v2.146"
    assert result["acceptable_k_bridge_candidates"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "k_convention_bridge_candidates_audited_no_acceptable_bridge"
    )
    assert result["selected_next_build_action"] == (
        "ingest_primary_k_formula_or_define_engine_shape_normalization_convention"
    )
    assert "bridge_depends_on_kappa_convention" in result["current_blockers"]
