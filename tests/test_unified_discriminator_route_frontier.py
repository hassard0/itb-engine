"""Regression tests for v2.53 unified discriminator route frontier."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from unified_discriminator_route_frontier import (  # noqa: E402
    diagnose_unified_discriminator_route_frontier,
)


def test_unified_frontier_has_no_current_claim_ready_route():
    result = diagnose_unified_discriminator_route_frontier()

    assert result["route_count"] == 4
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "no_claim_ready_route"
    assert result["synthetic_positive_control"]["ready_routes"] == [
        "synthetic:ready_external_measurement"
    ]


def test_unified_frontier_covers_expected_routes_and_next_artifacts():
    result = diagnose_unified_discriminator_route_frontier()
    routes = {row["route"]: row for row in result["routes"]}

    assert set(routes) == {
        "native_tower_adapter",
        "cosmic_birefringence",
        "weyl_g_C",
        "matter_high_moment_g_8",
    }
    for row in routes.values():
        assert row["claim_ready"] is False
        assert row["blocker_summary"]
        assert row["next_required_artifact"]


def test_unified_frontier_prioritizes_g8_measurement_specification():
    result = diagnose_unified_discriminator_route_frontier()

    assert result["priority_order"][0] == "matter_high_moment_g_8"
    route = next(
        row for row in result["routes"]
        if row["route"] == "matter_high_moment_g_8"
    )
    assert route["evidence_snapshot"]["external_numeric_measurement_routes"] == 0
    assert "g_8" in route["next_required_artifact"]


def test_unified_frontier_preserves_birefringence_sub_claim_status():
    result = diagnose_unified_discriminator_route_frontier()
    route = next(row for row in result["routes"] if row["route"] == "cosmic_birefringence")

    assert route["evidence_snapshot"]["route_status"] == "alive_but_not_claimable"
    assert route["evidence_snapshot"]["positive_sign_dataset_count"] == 5
    assert route["evidence_snapshot"]["independent_pair_zero_exclusion_sigma"] < 5.0
    assert "no_5sigma_single_dataset_detection" in route["blocker_summary"]
