"""Regression tests for v2.33 tower evidence sourceability audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_evidence_sourceability import diagnose_tower_evidence_sourceability  # noqa: E402


def test_sourceability_counts_current_encoder_blockers():
    result = diagnose_tower_evidence_sourceability()

    assert result["registered_framework_count"] == 13
    assert len(result["in_scope_reference_feasible_frameworks"]) == 8
    assert result["sourceable_from_current_encoder"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["sourceability_status_counts"]["not_sourceable_from_current_encoder"] == 8
    assert result["sourceability_status_counts"]["not_target_reference_excluded"] == 3
    assert result["sourceability_status_counts"]["not_target_scope_limited"] == 2


def test_sourceability_inspects_encoded_theory_inputs():
    result = diagnose_tower_evidence_sourceability()
    row = result["frameworks"]["string_tree_eft"]

    assert row["sourceability_status"] == "not_sourceable_from_current_encoder"
    assert row["encoded_tower_inputs"]["has_any_tower_input"] is False
    assert row["encoded_tower_inputs"]["coefficient_hits"] == []
    assert "g_R2" in row["encoded_tower_inputs"]["encoded_coefficient_keys"]
    assert "R/R0" in row["required_next_data"]


def test_sourceability_guardrail():
    result = diagnose_tower_evidence_sourceability()

    assert "not a literature exhaustion proof" in result["literature_guardrail"]["claim"]
    assert "new sourced data" in result["interpretation"]
