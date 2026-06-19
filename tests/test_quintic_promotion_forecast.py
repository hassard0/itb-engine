"""Regression tests for v2.36 quintic promotion forecast."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from quintic_promotion_forecast import diagnose_quintic_promotion_forecast  # noqa: E402


def test_quintic_promotion_rejects_generic_string_tree_attachment():
    result = diagnose_quintic_promotion_forecast()
    mode = result["promotion_modes"]["attach_to_generic_string_tree_eft"]

    assert mode["allowed"] is False
    assert "source_covers_one_parameter_quintic_not_generic_string_tree_eft" in (
        mode["blockers"]
    )
    assert result["claimable_framework_exclusions_now"] == []


def test_quintic_promotion_scoped_framework_forecast_is_non_excluding():
    result = diagnose_quintic_promotion_forecast()
    forecast = result["promotion_modes"]["register_scoped_quintic_framework"]["forecast"]

    assert result["current_registered_framework_count"] == 13
    assert forecast["would_increase_registered_framework_count_to"] == 14
    assert forecast["would_have_native_tower_evidence"] is True
    assert forecast["expected_tower_verdict"] == "tower_allowed_by_predictive_spectrum"
    assert forecast["would_create_framework_exclusion"] is False
    assert forecast["expected_frontier_status"] == "tower_evidence_present_but_not_excluding"


def test_quintic_promotion_recommendation_prioritizes_new_science_not_registry_churn():
    result = diagnose_quintic_promotion_forecast()

    assert result["promotion_modes"]["keep_external_candidate"]["allowed"] is True
    assert "Do not attach the quintic row" in result["recommended_next_action"]
    assert "asymptotic lightest-tower extraction" in result["recommended_next_action"]
