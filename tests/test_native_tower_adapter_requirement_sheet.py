"""Tests for the v2.164 native tower adapter requirement sheet."""

from experiments.native_tower_adapter_requirement_sheet import (
    diagnose_native_tower_adapter_requirement_sheet,
    native_adapter_authoring_contract,
    per_framework_native_adapter_requirements,
)
from itb.predict import FRAMEWORKS


def test_requirement_sheet_covers_all_registered_frameworks():
    result = diagnose_native_tower_adapter_requirement_sheet()

    assert result["version"] == "v2.164"
    assert result["registered_framework_count"] == len(FRAMEWORKS)
    assert {row["framework"] for row in result["rows"]} == set(FRAMEWORKS)
    assert result["adapter_authoring_ready_frameworks"] == []
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "native_adapter_requirements_defined_no_source_ready"
    )


def test_authoring_contract_names_spectrum_evidence_ownership_and_claim_fields():
    contract = native_adapter_authoring_contract()

    assert "phi_tower_mean" in contract["tower_spectrum_required_fields"]
    assert "phi_tower_sigma" in contract["tower_spectrum_required_fields"]
    assert "source_url" in contract["tower_evidence_required_fields"]
    assert "native_framework_endpoint" in (
        contract["native_ownership_required_fields"]
    )
    assert "native_framework_displacement" in (
        contract["native_ownership_required_fields"]
    )
    assert "registered_framework_exclusion_math" in contract["claim_required_fields"]
    assert contract["threshold_rule"] == (
        "phi_tower_mean - 2 * phi_tower_sigma > critical_phi_tower"
    )


def test_string_tree_has_source_context_but_missing_native_contract_fields():
    rows = {
        row["framework"]: row
        for row in per_framework_native_adapter_requirements()
    }
    row = rows["string_tree_eft"]

    assert row["live_source_candidate_count"] == 2
    assert "dark_dimension_swampland_2022" in row["live_source_labels"]
    assert "emergence_swampland_2018" in row["live_source_labels"]
    assert row["adapter_authoring_ready"] is False
    assert "registered_target_match" in row["missing_requirements"]
    assert "native_framework_endpoint" in row["missing_requirements"]
    assert "source_owned_tower_evidence" in row["missing_requirements"]


def test_asymptotic_safety_has_registered_context_but_no_native_spectrum():
    rows = {
        row["framework"]: row
        for row in per_framework_native_adapter_requirements()
    }
    row = rows["asymptotic_safety"]

    assert row["live_source_candidate_count"] == 2
    assert "asymptotic_safety_swampland_2025" in row["live_source_labels"]
    assert "absolute_swampland_review_2024" in row["live_source_labels"]
    assert "spectrum.phi_tower_mean" in row["missing_requirements"]
    assert "spectrum.phi_tower_sigma" in row["missing_requirements"]
    assert "framework" in row["missing_requirements"]


def test_frameworks_without_live_source_context_are_explicitly_marked():
    result = diagnose_native_tower_adapter_requirement_sheet()

    assert "pure_gr" in result["frameworks_without_live_source_context"]
    assert "causal_set" in result["frameworks_without_live_source_context"]
    rows = {row["framework"]: row for row in result["rows"]}
    pure_gr = rows["pure_gr"]

    assert pure_gr["live_source_candidate_count"] == 0
    assert pure_gr["status"] == "no_live_source_context_requirements_defined"
    assert "live_source_candidate" in pure_gr["missing_requirements"]


def test_missing_requirement_counts_keep_claim_controls_global():
    result = diagnose_native_tower_adapter_requirement_sheet()

    assert result["missing_requirement_counts"]["external_adversarial_review_status"] == (
        len(FRAMEWORKS)
    )
    assert result["missing_requirement_counts"]["adapter_normalization"] == len(
        result["frameworks_with_live_source_context"]
    )
    assert result["selected_next_build_action"] == (
        "monitor_or_author_native_adapter_only_when_one_framework_row_fills_contract"
    )
