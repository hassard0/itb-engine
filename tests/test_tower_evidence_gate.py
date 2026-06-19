"""Regression tests for v2.31 tower evidence gate."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_evidence_gate import diagnose_tower_evidence_gate  # noqa: E402


def test_evidence_gate_rejects_math_exclusion_without_source():
    result = diagnose_tower_evidence_gate()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "math_excludes_but_missing_source"
    )

    assert row["tower_claimable_by_math"] is True
    assert row["evidence_validation"]["ready_for_framework_claim"] is False
    assert "missing_required_fields" in row["evidence_validation"]["blockers"]
    assert row["claimable_now"] is False
    assert "math_excludes_but_missing_source" in (
        result["math_excluding_but_evidence_rejected"]
    )


def test_evidence_gate_distinguishes_schema_ready_fixture_from_current_claim():
    result = diagnose_tower_evidence_gate()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "complete_schema_exclusion_fixture"
    )

    assert row["tower_claimable_by_math"] is True
    assert row["evidence_validation"]["ready_for_framework_claim"] is True
    assert row["schema_ready_and_tower_excluding"] is True
    assert row["claimable_now"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["schema_ready_and_tower_excluding_fixtures"] == [
        "complete_schema_exclusion_fixture"
    ]


def test_evidence_gate_primary_source_overlap_is_not_exclusion():
    result = diagnose_tower_evidence_gate()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "primary_source_but_overlaps_threshold"
    )

    assert row["evidence_validation"]["ready_for_framework_claim"] is True
    assert row["framework_tower_verdict"] == "tower_prediction_overlaps_threshold"
    assert row["schema_ready_and_tower_excluding"] is False
    assert "not a framework-level" in result["literature_guardrail"]["claim"]
