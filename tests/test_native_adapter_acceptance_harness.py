"""Regression tests for v2.47 native adapter acceptance harness."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from native_adapter_acceptance_harness import (  # noqa: E402
    diagnose_native_adapter_acceptance_harness,
)


def test_owned_scope_fixture_reaches_claim_ready_branch():
    result = diagnose_native_adapter_acceptance_harness()
    row = next(
        item for item in result["cases"]
        if item["label"] == "owned_scope_acceptance_fixture"
    )

    assert row["tower_claimable_by_math"] is True
    assert row["promotion_guard_ready"] is True
    assert row["generic_claim_guard_ready"] is True
    assert row["generic_claim_guard_blockers"] == []
    assert row["frontier_status"] == "tower_discriminator_claim_ready"
    assert row["tower_discriminator_claim_ready"] == ["string_tree_eft"]
    assert row["claimable_now"] is False


def test_missing_ownership_fixture_stays_generic_guard_blocked():
    result = diagnose_native_adapter_acceptance_harness()
    row = next(
        item for item in result["cases"]
        if item["label"] == "missing_ownership_fixture"
    )

    assert row["tower_claimable_by_math"] is True
    assert row["promotion_guard_ready"] is True
    assert row["generic_claim_guard_ready"] is False
    assert row["frontier_status"] == "tower_generic_claim_guard_blocked"
    assert row["generic_claim_guard_blockers"] == [
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]


def test_acceptance_harness_is_synthetic_and_restores_registry():
    result = diagnose_native_adapter_acceptance_harness()

    assert result["claim_ready_synthetic_fixtures"] == [
        "owned_scope_acceptance_fixture"
    ]
    assert result["generic_claim_blocked_synthetic_fixtures"] == [
        "missing_ownership_fixture"
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert result["registry_restored_after_harness"] is True
    assert "synthetic acceptance harness" in result["literature_guardrail"]["claim"]
