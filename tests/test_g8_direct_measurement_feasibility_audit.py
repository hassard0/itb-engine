"""Tests for the v2.89 direct g_8 measurement feasibility audit."""

from experiments.g8_direct_measurement_feasibility_audit import (
    diagnose_g8_direct_measurement_feasibility_audit,
    measurement_requirement_rows,
    repo_capability_rows,
)


def test_direct_g8_measurement_requires_external_experiment():
    result = diagnose_g8_direct_measurement_feasibility_audit()

    assert result["version"] == "v2.89"
    assert result["route"] == "new_spin4_or_detector_g8_measurement"
    assert result["repo_can_create_external_measurement_packet"] is False
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "direct_g8_measurement_requires_external_experiment"


def test_repo_capabilities_are_schema_and_audit_not_measurement_generation():
    rows = {row["capability"]: row for row in repo_capability_rows()}

    assert rows["measurement_contract_and_acceptance_gate"]["available_in_repo"] is True
    assert (
        rows["measurement_contract_and_acceptance_gate"][
            "can_create_external_measurement"
        ]
        is False
    )
    assert "schema_not_measurement" in (
        rows["measurement_contract_and_acceptance_gate"]["blockers"]
    )


def test_external_experiment_capability_is_not_available_in_repo():
    rows = {row["capability"]: row for row in repo_capability_rows()}
    row = rows["external_spin4_detector_experiment"]

    assert row["available_in_repo"] is False
    assert row["can_create_external_measurement"] is True
    assert "external_experimental_program_required" in row["blockers"]


def test_measurement_requirements_are_not_currently_satisfied():
    rows = measurement_requirement_rows()

    assert rows
    assert all(row["satisfied_now"] is False for row in rows)
    assert any(
        row["requirement"] == "public_g8_likelihood_or_covariance"
        and "public_likelihood_release_missing" in row["blockers"]
        for row in rows
    )


def test_framework_exclusion_math_waits_on_external_packet():
    rows = {row["requirement"]: row for row in measurement_requirement_rows()}
    row = rows["registered_framework_exclusion_math"]

    assert row["satisfiable_by_repo_only"] is True
    assert "blocked_until_external_packet_exists" in row["blockers"]
