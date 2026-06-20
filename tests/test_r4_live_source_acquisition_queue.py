"""Tests for the v2.174 R4 live-source acquisition queue."""

from experiments.r4_live_source_acquisition_queue import (
    current_r4_live_source_candidates,
    diagnose_r4_live_source_acquisition_queue,
)


def test_live_source_candidates_include_formalism_data_and_mapping_routes():
    candidates = {row["label"]: row for row in current_r4_live_source_candidates()}

    assert "bresciani_partial_wave_unitarity_bounds_2025" in candidates
    assert "gwosc_public_catalog_and_event_data" in candidates
    assert "matching_tidal_deformability_wilson_coefficients_2026" in candidates
    assert "curvature_dependence_gw_tests_dictionary_2024" in candidates
    assert "g_R4_c1" in candidates[
        "bresciani_partial_wave_unitarity_bounds_2025"
    ]["potential_axes"]
    assert candidates["gwosc_public_catalog_and_event_data"]["source_type"] == (
        "public_data_product"
    )


def test_candidates_are_not_manifest_or_claim_ready():
    result = diagnose_r4_live_source_acquisition_queue()

    assert result["version"] == "v2.174"
    assert result["manifest_ready_candidates"] == []
    assert result["ingestion_ready_candidates"] == []
    assert result["claim_ready_candidates"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["ready_public_r4_likelihood_packets_now"] == []


def test_ranked_candidates_expose_missing_packet_capabilities_and_actions():
    result = diagnose_r4_live_source_acquisition_queue()

    for row in result["candidates_ranked"]:
        assert row["manifest_ready_now"] is False
        assert row["ingestion_ready_now"] is False
        assert row["missing_packet_capability_count"] > 0
        assert row["adapter_work_item_count"] > 0
        assert row["next_build_action"] == row["adapter_work_items"][0]


def test_selected_route_combines_bresciani_axis_work_with_public_gw_data():
    result = diagnose_r4_live_source_acquisition_queue()
    route = result["selected_next_build_route"]

    assert route["route"] == "bresciani_axis_dictionary_plus_public_gw_reanalysis"
    assert route["status"] == "buildable_but_not_packet_ready"
    assert "bresciani_partial_wave_unitarity_bounds_2025" in route["inputs"]
    assert "gwosc_public_catalog_and_event_data" in route["inputs"]
    assert "g_R4_c1" in route["can_attack"]
    assert route["next_build_action"] == (
        "derive_machine_axis_dictionary_from_bresciani_basis"
    )


def test_failure_counts_show_public_likelihood_and_axis_mapping_are_missing():
    result = diagnose_r4_live_source_acquisition_queue()

    assert result["route_status"] == "r4_live_source_queue_ready_no_packet"
    assert result["failure_counts"]["public_likelihood_or_covariance"] >= 3
    assert result["failure_counts"]["maps_to_bresciani_r4_axes"] >= 3
    assert result["failure_counts"]["r4_shape_covariance"] >= 1
    assert result["failure_counts"]["public_covariance_over_engine_r4_axes"] >= 2


def test_source_urls_are_primary_or_public_records():
    result = diagnose_r4_live_source_acquisition_queue()

    assert result["candidate_count"] == 6
    for url in result["source_urls_checked"]:
        assert url.startswith(("https://arxiv.org/", "https://gwosc.org/"))
