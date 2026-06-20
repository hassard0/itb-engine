"""Tests for the v2.163 native tower live-source triage."""

from experiments.native_tower_live_source_triage import (
    diagnose_native_tower_live_source_triage,
    live_native_tower_source_candidates,
)


def test_live_source_triage_finds_no_registered_native_adapter():
    result = diagnose_native_tower_live_source_triage()

    assert result["version"] == "v2.163"
    assert result["route"] == "framework_specific_native_tower_search"
    assert result["candidate_count"] == 7
    assert result["native_adapter_triage_ready_candidates"] == []
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "live_native_tower_sources_no_registered_adapter"
    )


def test_asymptotic_safety_sources_are_registered_but_not_adapters():
    rows = {row["label"]: row for row in live_native_tower_source_candidates()}
    row = rows["asymptotic_safety_swampland_2025"]

    assert row["target_framework"] == "asymptotic_safety"
    assert row["target_framework_registered"] is True
    assert row["registered_target_match"] is True
    assert row["native_adapter_triage_ready"] is False
    assert "conceptual_assessment_not_adapter" in row["blockers"]
    assert "missing_native_tower_spectrum" in row["blockers"]
    assert "missing_native_tower_evidence" in row["blockers"]


def test_dark_dimension_sources_have_tower_context_but_not_registered_adapter():
    rows = {row["label"]: row for row in live_native_tower_source_candidates()}
    row = rows["dark_dimension_swampland_2022"]

    assert row["native_tower_spectrum_present"] is True
    assert row["asymptotic_range"] is True
    assert row["registered_target_match"] is False
    assert "scenario_tower_not_registered_framework_adapter" in row["blockers"]
    assert "source_does_not_target_registered_framework_adapter" in row["blockers"]
    assert "missing_native_tower_evidence" in row["blockers"]


def test_horava_witten_candidate_does_not_match_registered_horava_lifshitz():
    rows = {row["label"]: row for row in live_native_tower_source_candidates()}
    row = rows["horava_witten_dark_dimension_2026"]

    assert row["target_framework"] == "horava_lifshitz"
    assert row["target_framework_registered"] is True
    assert row["registered_target_match"] is False
    assert "horava_witten_not_horava_lifshitz" in row["blockers"]
    assert "source_does_not_target_registered_framework_adapter" in row["blockers"]


def test_complexity_and_holographic_sources_are_not_native_tower_spectra():
    rows = {row["label"]: row for row in live_native_tower_source_candidates()}

    complexity = rows["finite_complexity_landscape_2026"]
    holographic = rows["holographic_swampland_constraints_2025"]

    assert "complexity_constraint_not_tower_spectrum" in complexity["blockers"]
    assert "missing_native_tower_spectrum" in complexity["blockers"]
    assert "holographic_constraint_not_native_tower_adapter" in (
        holographic["blockers"]
    )
    assert "missing_native_tower_evidence" in holographic["blockers"]


def test_triage_selects_per_framework_requirement_sheet_next():
    result = diagnose_native_tower_live_source_triage()

    assert result["selected_next_build_action"] == (
        "derive_minimum_native_tower_adapter_requirements_per_registered_framework"
    )
    assert result["blocker_counts"]["missing_framework_owned_endpoint"] == 7
    assert result["blocker_counts"]["adapter_normalization_missing"] == 7
