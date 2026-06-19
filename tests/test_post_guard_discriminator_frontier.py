"""Regression tests for v2.43 post-guard discriminator frontier."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from post_guard_discriminator_frontier import (  # noqa: E402
    diagnose_post_guard_discriminator_frontier,
)


def test_post_guard_frontier_keeps_current_catalogue_blockers():
    result = diagnose_post_guard_discriminator_frontier()

    assert result["registered_framework_count"] == 13
    assert result["tower_discriminator_claim_ready"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["frontier_status_counts"]["missing_native_tower_spectrum"] == 8
    assert result["frontier_status_counts"]["reference_excluded_before_tower"] == 3
    assert result["frontier_status_counts"]["scope_limited_reference_survivor"] == 2


def test_post_guard_frontier_rows_include_promotion_guard():
    result = diagnose_post_guard_discriminator_frontier()

    assert result["promotion_guard_ready_frameworks"] == []
    assert result["promotion_guard_positive_control_blocked_frameworks"] == []
    assert all(
        "tower_promotion_guard" in row for row in result["frameworks"].values()
    )
    assert result["frameworks"]["string_tree_eft"]["tower_promotion_guard"][
        "blockers"
    ] == ["missing_native_tower_evidence"]
    assert "still blocked before that gate" in result["post_guard_interpretation"]
