"""Regression tests for v2.48 candidate-to-native adapter promotion audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from candidate_native_adapter_promotion_audit import (  # noqa: E402
    diagnose_candidate_native_adapter_promotion_audit,
)


def test_candidate_native_adapter_promotion_counts_current_rows():
    result = diagnose_candidate_native_adapter_promotion_audit()

    assert result["candidate_count"] == 8
    assert len(result["tower_math_excluding_candidates"]) == 7
    assert len(result["positive_control_candidates"]) == 7
    assert result["finite_range_candidates"] == ["ashmore_ruehle_quintic_kk"]
    assert result["generic_claim_guard_ready_candidates"] == []
    assert result["promotable_native_adapter_candidates"] == []
    assert result["claimable_framework_exclusions_now"] == []


def test_candidate_native_adapter_promotion_common_blockers():
    result = diagnose_candidate_native_adapter_promotion_audit()

    assert (
        result["promotion_blocker_counts"][
            "not_exposed_by_registered_framework_adapter"
        ]
        == 8
    )
    assert result["promotion_blocker_counts"]["missing_framework_owned_endpoint"] == 8
    assert (
        result["promotion_blocker_counts"]["missing_framework_owned_displacement"]
        == 8
    )
    assert result["promotion_blocker_counts"]["known_qg_positive_control_family"] == 7
    assert result["promotion_blocker_counts"]["tower_math_not_excluding"] == 1


def test_candidate_native_adapter_promotion_keeps_quintic_scope_blocked():
    result = diagnose_candidate_native_adapter_promotion_audit()
    row = next(
        item for item in result["candidates"]
        if item["label"] == "ashmore_ruehle_quintic_kk"
    )

    assert row["tower_claimable_by_math"] is False
    assert row["source_scope"]["range_scope"] == "finite_range"
    assert row["promotable_to_native_adapter_now"] is False
    assert row["promotion_blockers"] == [
        "finite_range_not_asymptotic",
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
        "not_exposed_by_registered_framework_adapter",
        "single_compactification_not_generic_framework",
        "tower_math_not_excluding",
    ]
    assert "none can be promoted into a live native adapter" in result["interpretation"]
