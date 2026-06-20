"""Tests for the v2.140 source K-factor decomposition audit."""

from experiments.source_k_factor_helicity_decomposition_audit import (
    decomposition_routes,
    diagnose_source_k_factor_helicity_decomposition_audit,
    k_factor_source_status_rows,
    required_k_decomposition_inputs,
)


def test_russo_references_k_without_defining_it_locally():
    rows = {row["source_id"]: row for row in k_factor_source_status_rows()}
    russo = rows["russo_1997_type_iib_four_graviton"]

    assert russo["provides_low_energy_r4_contact_factor"] is True
    assert russo["provides_local_k_formula"] is False
    assert russo["blocker"] == "source_k_factor_not_local_in_russo"


def test_gross_witten_is_identified_as_uningested_primary_k_source():
    rows = {row["source_id"]: row for row in k_factor_source_status_rows()}
    gross_witten = rows["gross_witten_1986"]

    assert gross_witten["status"] == "primary_k_factor_source_not_ingested"
    assert gross_witten["provides_helicity_decomposition"] is False
    assert gross_witten["blocker"] == (
        "gross_witten_kinematic_factor_definition_not_ingested"
    )


def test_required_inputs_keep_k_decomposition_blocked():
    inputs = required_k_decomposition_inputs()
    blockers = {row["blocker"] for row in inputs}

    assert all(row["status"] in {"missing", "partially_sourced"} for row in inputs)
    assert "source_K_plus_K_minus_components_missing" in blockers
    assert "weyl_projection_and_eom_policy_missing" in blockers


def test_routes_offer_ingestion_and_rederivation_paths():
    routes = {row["route"]: row for row in decomposition_routes()}

    assert routes["ingest_primary_k_factor"]["status"] == "preferred_next"
    assert routes["rederive_k_from_polarization_tensors"]["status"] == (
        "fallback_parallel_route"
    )


def test_diagnosis_records_no_solved_k_decomposition():
    result = diagnose_source_k_factor_helicity_decomposition_audit()

    assert result["version"] == "v2.140"
    assert result["machine_checkable_k_formula_sources"] == []
    assert result["source_backed_helicity_decomposition_sources"] == []
    assert result["can_solve_k_decomposition_now"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "source_k_factor_helicity_decomposition_blocked_on_k_formula"
    )
    assert result["selected_next_build_action"] == (
        "ingest_gross_witten_kinematic_factor_or_rederive_from_polarizations"
    )
