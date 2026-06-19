"""Regression tests for v2.32 discriminator frontier audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from discriminator_frontier import diagnose_discriminator_frontier  # noqa: E402


def test_discriminator_frontier_counts_current_blockers():
    result = diagnose_discriminator_frontier()

    assert result["registered_framework_count"] == 13
    assert len(result["reference_feasible_frameworks"]) == 10
    assert result["tower_discriminator_claim_ready"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["frontier_status_counts"]["reference_excluded_before_tower"] == 3
    assert "missing_native_tower_spectrum" in result["frontier_status_counts"]


def test_discriminator_frontier_marks_reference_feasible_missing_tower_evidence():
    result = diagnose_discriminator_frontier()
    row = result["frameworks"]["string_tree_eft"]

    assert row["reference_feasible"] is True
    assert row["native_tower_spectrum_present"] is False
    assert row["native_tower_evidence_present"] is False
    assert row["frontier_status"] == "missing_native_tower_spectrum"
    assert row["tower_evidence_validation"]["blockers"] == ["missing_native_tower_evidence"]
    assert "sourced TowerEvidence" in result["interpretation"]


def test_discriminator_frontier_guardrail_and_scope():
    result = diagnose_discriminator_frontier()

    assert "not a solution claim" in result["literature_guardrail"]["claim"]
    assert result["frameworks"]["horava_lifshitz"]["reference_feasible"] is False
    assert result["frameworks"]["causal_set"]["engine_scope"]["in_scope"] is False
