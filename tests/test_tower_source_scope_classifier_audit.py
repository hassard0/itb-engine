"""Regression tests for v2.44 tower source-scope classifier audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_source_scope_classifier_audit import (  # noqa: E402
    diagnose_tower_source_scope_classifier_audit,
)


def test_source_scope_classifier_counts_current_candidate_classes():
    result = diagnose_tower_source_scope_classifier_audit()

    assert result["candidate_count"] == 9
    assert len(result["positive_control_candidates"]) == 7
    assert result["finite_range_candidates"] == ["ashmore_ruehle_quintic_kk"]
    assert result["promotion_guard_ready_candidates"] == [
        "non_positive_control_excluding_fixture"
    ]
    assert result["generic_framework_claim_ready_candidates"] == []
    assert result["claimable_framework_exclusions_now"] == []


def test_source_scope_classifier_marks_quintic_finite_single_compactification():
    result = diagnose_tower_source_scope_classifier_audit()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "ashmore_ruehle_quintic_kk"
    )

    assert row["source_scope"]["range_scope"] == "finite_range"
    assert row["source_scope"]["compactification_scope"] == "single_compactification"
    assert row["source_scope"]["tower_scope"] == "scalar_laplacian_subtower"
    assert "finite_range_not_asymptotic" in row["source_scope"]["scope_blockers"]
    assert "single_compactification_not_generic_framework" in (
        row["source_scope"]["scope_blockers"]
    )


def test_source_scope_classifier_guard_ready_is_not_generic_claim_ready():
    result = diagnose_tower_source_scope_classifier_audit()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "non_positive_control_excluding_fixture"
    )

    assert row["promotion_guard_ready"] is True
    assert row["generic_framework_claim_ready"] is False
    assert row["source_scope"]["scope_blockers"] == [
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]
    assert "Source-scope readiness is stricter" in result["literature_guardrail"]["claim"]
