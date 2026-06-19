"""Tests for the v2.95 external-dependency blocker synthesis."""

from experiments.external_dependency_blocker_synthesis import (
    diagnose_external_dependency_blocker_synthesis,
)


def test_blocker_synthesis_declares_no_current_claimable_discriminator():
    result = diagnose_external_dependency_blocker_synthesis()

    assert result["version"] == "v2.95"
    assert result["route_status"] == (
        "research_frontier_blocked_pending_external_evidence"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["blocked_for_current_run"] is True
    assert result["repeated_blocker"] == "real_engine_normalized_external_packet_missing"


def test_blocker_synthesis_carries_current_source_probe_failures():
    result = diagnose_external_dependency_blocker_synthesis()

    assert result["current_source_candidate_count"] == 4
    assert result["current_schema_ready_candidates"] == []
    assert result["current_claim_ready_candidates"] == []
    assert result["source_probe_route_status"] == (
        "current_source_probe_no_external_packet_satisfies_gate"
    )


def test_blocker_synthesis_carries_no_in_repo_promotion_ready_routes():
    result = diagnose_external_dependency_blocker_synthesis()

    assert result["current_in_repo_promotion_ready_routes"] == []
    assert len(result["external_dependency_routes"]) == 6
    assert "future_public_g8_measurement_ingestion" in (
        result["external_dependency_routes"]
    )


def test_unblock_conditions_include_g8_native_tower_gw_and_joint_routes():
    result = diagnose_external_dependency_blocker_synthesis()
    routes = {row["route"] for row in result["unblock_conditions"]}

    assert "future_public_g8_measurement_ingestion" in routes
    assert "framework_specific_native_tower_search" in routes
    assert "gw_parity_operator_normalization_search" in routes
    assert "weyl_g8_joint_frontier" in routes


def test_synthesis_disallows_synthetic_or_source_incomplete_promotion():
    result = diagnose_external_dependency_blocker_synthesis()

    assert "synthetic_fixture_as_physics_claim" in result["disallowed_next_steps"]
    assert "source_incomplete_adapter_promotion" in result["disallowed_next_steps"]
    assert "ingest_and_validate_real_external_packet" in result["allowed_nonclaim_work"]
