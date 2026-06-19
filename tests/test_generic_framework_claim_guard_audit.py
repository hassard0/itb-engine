"""Regression tests for v2.45 generic framework claim guard audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from generic_framework_claim_guard_audit import (  # noqa: E402
    diagnose_generic_framework_claim_guard_audit,
)


def test_generic_claim_guard_blocks_all_current_candidates():
    result = diagnose_generic_framework_claim_guard_audit()

    assert result["candidate_count"] == 9
    assert result["promotion_guard_ready_candidates"] == [
        "non_positive_control_excluding_fixture"
    ]
    assert result["generic_claim_guard_ready_candidates"] == []
    assert result["generic_guard_blocked_after_promotion"] == [
        "non_positive_control_excluding_fixture"
    ]
    assert result["top_generic_claim_blockers"]["missing_framework_owned_endpoint"] == 9
    assert (
        result["top_generic_claim_blockers"]["missing_framework_owned_displacement"]
        == 9
    )
    assert result["claimable_framework_exclusions_now"] == []


def test_generic_claim_guard_adds_frontier_blocked_state():
    result = diagnose_generic_framework_claim_guard_audit()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "non_positive_control_excluding_fixture"
    )

    assert row["promotion_guard_ready"] is True
    assert row["generic_claim_guard_ready"] is False
    assert row["frontier_status"] == "tower_generic_claim_guard_blocked"
    assert row["generic_claim_guard_blockers"] == [
        "missing_asymptotic_range_scope",
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]


def test_generic_claim_guard_positive_branch_is_synthetic_only():
    result = diagnose_generic_framework_claim_guard_audit()
    fixture = result["synthetic_owned_scope_fixture"]

    assert fixture["generic_claim_guard_ready"] is True
    assert fixture["generic_claim_guard_blockers"] == []
    assert fixture["frontier_status"] == "tower_discriminator_claim_ready"
    assert fixture["claimable_now"] is False
    assert fixture["synthetic_fixture"] is True
    assert "synthetic owned-scope fixture" in result["literature_guardrail"]["claim"]
