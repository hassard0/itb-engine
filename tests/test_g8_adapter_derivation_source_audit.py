"""Tests for the v2.86 g_8 adapter derivation source audit."""

from experiments.g8_adapter_derivation_source_audit import (
    derivation_source_candidates,
    diagnose_g8_adapter_derivation_source_audit,
)


def test_g8_adapter_derivation_source_audit_finds_no_ready_identity():
    result = diagnose_g8_adapter_derivation_source_audit()

    assert result["version"] == "v2.86"
    assert result["route"] == "source_backed_g8_adapter_derivation"
    assert result["adapter_derivation_ready_candidates"] == []
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "current_sources_no_source_backed_g8_adapter_identity"
    )


def test_gravity_energy_correlator_formalism_lacks_g8_jacobian():
    rows = {row["label"]: row for row in derivation_source_candidates()}
    row = rows["energy_correlators_four_dimensional_gravity"]

    assert row["gates"]["detector_or_energy_correlator_observable"] is True
    assert row["gates"]["source_backed_operator_identity_to_engine_g8"] is False
    assert "source_backed_operator_identity_to_engine_g8_missing" in (
        row["blockers"]
    )
    assert "public_g8_jacobian_or_projection_missing" in row["blockers"]


def test_bootstrapping_string_eft_has_wilson_formalism_not_detector_adapter():
    rows = {row["label"]: row for row in derivation_source_candidates()}
    row = rows["bootstrapping_string_theory_eft"]

    assert row["gates"]["wilson_coefficient_formalism"] is True
    assert row["gates"]["detector_or_energy_correlator_observable"] is False
    assert "detector_or_energy_correlator_observable_missing" in row["blockers"]
    assert "public_covariance_or_likelihood_missing" in row["blockers"]


def test_all_current_candidates_lack_public_covariance():
    rows = derivation_source_candidates()

    assert rows
    assert all(row["gates"]["public_covariance_or_likelihood"] is False for row in rows)


def test_detector_and_wilson_formalisms_are_present_but_not_joined():
    result = diagnose_g8_adapter_derivation_source_audit()

    assert len(result["detector_formalism_sources"]) == 4
    assert len(result["wilson_formalism_sources"]) == 3
    assert result["blocker_counts"][
        "source_backed_operator_identity_to_engine_g8_missing"
    ] == result["candidate_count"]
