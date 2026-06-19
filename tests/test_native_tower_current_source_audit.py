"""Tests for the v2.83 native tower current-source audit."""

from experiments.native_tower_current_source_audit import (
    current_source_candidates,
    diagnose_native_tower_current_source_audit,
)


def test_native_tower_current_source_audit_finds_no_ready_native_adapter():
    result = diagnose_native_tower_current_source_audit()

    assert result["version"] == "v2.83"
    assert result["route"] == "native_tower_evidence"
    assert result["candidate_count"] == 6
    assert result["native_adapter_ready_candidates"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "current_sources_no_registered_native_tower_adapter"


def test_quintic_candidate_remains_single_compactification_finite_range():
    rows = {row["label"]: row for row in current_source_candidates()}
    row = rows["ashmore_ruehle_quintic_laplacian_kk"]

    assert row["native_tower_spectrum_present"] is True
    assert row["native_tower_evidence_present"] is True
    assert row["range_scope"] == "finite_range"
    assert "finite_range_not_asymptotic" in row["blockers"]
    assert "single_compactification_not_generic_framework" in row["blockers"]
    assert "not_exposed_by_registered_framework_adapter" in row["blockers"]


def test_known_string_positive_controls_are_blocked_from_claim_promotion():
    result = diagnose_native_tower_current_source_audit()

    assert result["blocker_counts"]["known_qg_positive_control_family"] == 2
    rows = {row["label"]: row for row in result["rows"]}
    assert "known_qg_positive_control_family" in (
        rows["blumenhagen_refined_sdc_large_volume"]["blockers"]
    )
    assert "known_qg_positive_control_family" in (
        rows["aoufia_laplacian_various_dimensions"]["blockers"]
    )


def test_asymptotic_safety_source_is_conceptual_not_native_spectrum():
    rows = {row["label"]: row for row in current_source_candidates()}
    row = rows["asymptotic_safety_swampland_assessment"]

    assert row["target_framework"] == "asymptotic_safety"
    assert row["target_framework_registered"] is True
    assert row["native_tower_spectrum_present"] is False
    assert "framework_relative_swampland_assessment_not_tower_spectrum" in (
        row["blockers"]
    )
    assert "missing_native_tower_spectrum" in row["blockers"]


def test_horava_witten_candidate_does_not_target_registered_horava_lifshitz():
    rows = {row["label"]: row for row in current_source_candidates()}
    row = rows["horava_witten_dark_dimension_candidate"]

    assert row["target_framework"] == "horava_lifshitz"
    assert row["target_framework_registered"] is True
    assert "horava_witten_string_setup_not_horava_lifshitz_framework" in (
        row["blockers"]
    )
    assert row["native_adapter_ready"] is False
