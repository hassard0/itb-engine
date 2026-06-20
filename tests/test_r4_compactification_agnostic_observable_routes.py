"""Tests for the v2.157 compactification-agnostic R4 route ranking."""

from experiments.r4_compactification_agnostic_observable_routes import (
    compactification_agnostic_observable_spec,
    compactification_agnostic_route_requirements,
    compactification_agnostic_route_sources,
    diagnose_r4_compactification_agnostic_observable_routes,
    rank_compactification_agnostic_routes,
)


def test_route_sources_distinguish_theory_routes_from_likelihoods():
    sources = compactification_agnostic_route_sources()
    by_id = {row["source_id"]: row for row in sources}

    assert "bresciani_levati_paradisi_2025_partial_wave_unitarity" in by_id
    bresciani = by_id["bresciani_levati_paradisi_2025_partial_wave_unitarity"]
    assert bresciani["provides_machine_route"] is True
    assert bresciani["provides_public_likelihood"] is False
    assert bresciani["uses_absolute_lambda_scale"] is False
    assert "greft_qnm_observability_discussion" in by_id
    assert by_id["greft_qnm_observability_discussion"][
        "provides_public_likelihood"
    ] is False


def test_route_requirements_include_compactification_independence_and_claim_gate():
    requirements = compactification_agnostic_route_requirements()

    assert "does_not_require_numeric_alpha_prime_to_lambda_r4_ratio" in requirements
    assert "does_not_require_compactification_specific_planck_scale" in requirements
    assert "has_machine_usable_axis_mapping" in requirements
    assert "keeps_framework_claim_disabled_without_likelihood" in requirements


def test_route_ranking_selects_bresciani_shape_diagnostic():
    ranking = rank_compactification_agnostic_routes()
    route_id = "bresciani_levati_paradisi_2025_partial_wave_unitarity"
    route = ranking["route_scores"][route_id]

    assert ranking["best_internal_diagnostic_route"] == route_id
    assert route["ready_for_internal_diagnostic"] is True
    assert route["ready_for_framework_claim"] is False
    assert ranking["public_likelihood_ready_routes"] == []
    assert route["criteria"][
        "does_not_require_numeric_alpha_prime_to_lambda_r4_ratio"
    ] is True


def test_observable_spec_is_nonclaiming_and_scale_free():
    spec = compactification_agnostic_observable_spec()

    assert spec["route_id"] == (
        "bresciani_levati_paradisi_2025_partial_wave_unitarity"
    )
    assert spec["status"] == "internal_theory_diagnostic_ready_nonclaiming"
    assert spec["does_not_use_numeric_lambda_r4_scale"] is True
    assert spec["does_not_use_compactification_policy"] is True
    assert spec["claim_use_allowed"] is False
    assert spec["measurement_likelihood_attached"] is False
    assert "claim_blocker_ledger" in spec["diagnostic_outputs"]


def test_diagnosis_records_no_public_likelihood_and_next_adapter():
    result = diagnose_r4_compactification_agnostic_observable_routes()

    assert result["version"] == "v2.157"
    assert result["internal_diagnostic_ready_routes"] == [
        "bresciani_levati_paradisi_2025_partial_wave_unitarity"
    ]
    assert result["public_likelihood_ready_routes"] == []
    assert result["ready_for_internal_observable_diagnostic"] is True
    assert result["ready_for_measurement_likelihood_claim"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "compactification_agnostic_r4_routes_ranked_no_public_likelihood"
    )
    assert result["selected_next_build_action"] == (
        "implement_bresciani_r4_shape_unitarity_diagnostic"
    )
