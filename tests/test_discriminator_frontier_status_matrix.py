"""Regression tests for v2.42 discriminator frontier status matrix."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from discriminator_frontier_status_matrix import (  # noqa: E402
    diagnose_discriminator_frontier_status_matrix,
)


def test_frontier_status_matrix_covers_all_status_branches():
    result = diagnose_discriminator_frontier_status_matrix()

    assert result["scenario_count"] == 8
    assert result["status_counts"]["reference_excluded_before_tower"] == 1
    assert result["status_counts"]["scope_limited_reference_survivor"] == 1
    assert result["status_counts"]["missing_native_tower_spectrum"] == 1
    assert result["status_counts"]["missing_or_rejected_tower_evidence"] == 1
    assert result["status_counts"]["tower_evidence_present_but_not_excluding"] == 1
    assert result["status_counts"]["tower_promotion_guard_blocked"] == 1
    assert result["status_counts"]["tower_generic_claim_guard_blocked"] == 1
    assert result["status_counts"]["tower_discriminator_claim_ready"] == 1


def test_frontier_status_matrix_separates_guard_states_from_claim_ready():
    result = diagnose_discriminator_frontier_status_matrix()

    assert result["promotion_guard_blocked_fixtures"] == [
        "promotion_guard_blocked_fixture"
    ]
    assert result["generic_claim_guard_blocked_fixtures"] == [
        "generic_claim_guard_blocked_fixture"
    ]
    assert result["tower_discriminator_claim_ready_fixtures"] == [
        "claim_ready_fixture"
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert "generic-claim-guard" in result["interpretation"]


def test_frontier_status_matrix_guardrail():
    result = diagnose_discriminator_frontier_status_matrix()

    assert "synthetic branch matrix" in result["literature_guardrail"]["claim"]
    assert all(row["claimable_now"] is False for row in result["scenarios"])
