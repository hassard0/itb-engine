"""Tests for the v2.99 joint g8 source-discovery queue."""

from experiments.g8_joint_source_discovery_queue import (
    current_joint_source_candidates,
    diagnose_g8_joint_source_discovery_queue,
)


def test_source_queue_is_not_claim_ready_but_selects_next_build_action():
    result = diagnose_g8_joint_source_discovery_queue()

    assert result["version"] == "v2.99"
    assert result["route_status"] == (
        "joint_source_queue_ready_next_adapter_build_selected"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["schema_ready_candidates"] == []
    assert result["claim_ready_candidates"] == []
    assert result["selected_next_build_action"]


def test_current_source_queue_contains_g8_secondary_and_public_reanalysis_inputs():
    candidates = {row["label"]: row for row in current_joint_source_candidates()}

    assert "bresciani_partial_wave_unitarity_bounds_2025" in candidates
    assert "gwosc_gw170608_open_data_release" in candidates
    assert "murata_short_range_inverse_square_review_2026" in candidates
    assert "sutton_quadratic_weyl_constraints_2025" in candidates
    assert candidates["bresciani_partial_wave_unitarity_bounds_2025"][
        "potential_axes"
    ] == ["g_8"]
    assert "g_R2" in candidates["murata_short_range_inverse_square_review_2026"][
        "potential_axes"
    ]
    assert "g_C" in candidates["sutton_quadratic_weyl_constraints_2025"][
        "potential_axes"
    ]


def test_candidate_rows_expose_gate_missing_capabilities_and_work_items():
    result = diagnose_g8_joint_source_discovery_queue()

    for row in result["candidates_ranked"]:
        assert row["blocks_v2_98_gate"] is True
        assert row["missing_gate_capability_count"] > 0
        assert row["adapter_work_item_count"] > 0
        assert row["next_build_action"] == row["adapter_work_items"][0]


def test_selected_route_is_public_gw_secondary_axis_reanalysis_path():
    result = diagnose_g8_joint_source_discovery_queue()
    route = result["selected_next_build_route"]

    assert route["route"] == "gw_reanalysis_to_joint_secondary_packet"
    assert route["status"] == "buildable_but_not_completed"
    assert "g_C" in route["can_attack"]
    assert "g_R2" in route["can_attack"]
    assert route["next_build_action"] == (
        "map_public_gw_reanalysis_parameters_to_engine_secondary_axis"
    )


def test_composite_routes_include_direct_g8_and_secondary_axis_adapter_paths():
    result = diagnose_g8_joint_source_discovery_queue()
    routes = {row["route"]: row for row in result["composite_build_routes_ranked"]}

    assert "partial_wave_g8_operator_identity_build" in routes
    assert "short_range_gR2_secondary_adapter" in routes
    assert "quadratic_weyl_gC_secondary_adapter" in routes
    assert routes["partial_wave_g8_operator_identity_build"]["can_attack"] == [
        "g_8"
    ]


def test_source_urls_are_primary_or_public_records():
    result = diagnose_g8_joint_source_discovery_queue()

    assert result["candidate_count"] == 7
    for url in result["source_urls_checked"]:
        assert url.startswith(
            (
                "https://arxiv.org/",
                "https://gwosc.org/",
                "https://github.com/",
            )
        )
