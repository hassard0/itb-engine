"""Tests for the v2.161 post-R4-likelihood-manifest frontier."""

from experiments.post_r4_likelihood_manifest_frontier import (
    diagnose_post_r4_likelihood_manifest_frontier,
    frontier_rows_after_r4_likelihood_manifest,
)


def test_post_r4_frontier_has_no_claim_ready_or_promotion_ready_routes():
    result = diagnose_post_r4_likelihood_manifest_frontier()

    assert result["version"] == "v2.161"
    assert result["claim_ready_routes"] == []
    assert result["current_in_repo_promotion_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "post_r4_frontier_diagnostic_ready_no_claim_ready_route"
    )


def test_r4_likelihood_ingestion_is_top_priority_but_external_blocked():
    result = diagnose_post_r4_likelihood_manifest_frontier()
    row = result["rows"][0]

    assert result["top_priority_route"] == "future_public_r4_shape_likelihood_ingestion"
    assert row["route"] == "future_public_r4_shape_likelihood_ingestion"
    assert row["current_in_repo_diagnostic_ready"] is True
    assert row["current_in_repo_promotion_ready"] is False
    assert row["claim_ready"] is False
    assert row["execution_class"] == "external_packet_required_before_claim_adapter"
    assert "public_r4_shape_likelihood_or_covariance_missing" in row["blockers"]
    assert "maps_to_bresciani_r4_axes_missing" in row["blockers"]


def test_g8_and_native_routes_are_carried_forward_after_r4():
    rows = {
        row["route"]: row
        for row in frontier_rows_after_r4_likelihood_manifest()
    }

    assert "future_public_g8_measurement_ingestion" in rows
    assert rows["future_public_g8_measurement_ingestion"]["priority_rank"] == 2
    assert "future_public_g8_packet_missing" in (
        rows["future_public_g8_measurement_ingestion"]["blockers"]
    )
    assert "framework_specific_native_tower_search" in rows
    assert rows["framework_specific_native_tower_search"]["priority_rank"] == 3


def test_symbolic_scale_resolution_is_retained_but_not_top_route():
    rows = {
        row["route"]: row
        for row in frontier_rows_after_r4_likelihood_manifest()
    }
    symbolic = rows["r4_symbolic_scale_resolution"]

    assert symbolic["priority_rank"] == 6
    assert symbolic["current_in_repo_diagnostic_ready"] is True
    assert symbolic["current_in_repo_promotion_ready"] is False
    assert symbolic["claim_ready"] is False
    assert "numeric_alpha_prime_to_lambda_r4_value_missing" in symbolic["blockers"]


def test_frontier_records_diagnostic_ready_routes_and_external_dependencies():
    result = diagnose_post_r4_likelihood_manifest_frontier()

    assert result["current_in_repo_diagnostic_ready_routes"] == [
        "future_public_r4_shape_likelihood_ingestion",
        "r4_symbolic_scale_resolution",
    ]
    assert result["r4_ready_likelihood_packets_now"] == []
    assert "future_public_r4_shape_likelihood_ingestion" in (
        result["external_dependency_routes"]
    )
    assert "future_public_g8_measurement_ingestion" in (
        result["external_dependency_routes"]
    )
