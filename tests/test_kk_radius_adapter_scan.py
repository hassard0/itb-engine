"""Regression tests for v2.29 KK-radius adapter scan."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from kk_radius_adapter_scan import diagnose_kk_radius_adapter_scan  # noqa: E402


def test_kk_radius_scan_exercises_all_verdict_regimes():
    result = diagnose_kk_radius_adapter_scan()
    verdicts = {
        row["label"]: row["framework_tower_verdict"]
        for row in result["candidates"]
    }

    assert verdicts["kk_allowance_fixture"] == "tower_allowed_by_predictive_spectrum"
    assert verdicts["kk_overlap_fixture"] == "tower_prediction_overlaps_threshold"
    assert verdicts["kk_exclusion_fixture"] == "tower_excluded_by_predictive_spectrum"
    assert result["claimable_if_sourced"] == ["kk_exclusion_fixture"]
    assert result["claimable_framework_exclusions_now"] == []


def test_kk_radius_scan_thresholds_and_guardrail():
    result = diagnose_kk_radius_adapter_scan()
    sigma_005 = next(
        row for row in result["radius_thresholds"]
        if row["phi_tower_sigma"] == 0.05
    )

    assert sigma_005["claimable_exclusion_requires_radius_ratio_gt"] > (
        sigma_005["claimable_allowance_requires_radius_ratio_lte"]
    )
    assert "synthetic KK-radius adapter candidates" in (
        result["literature_guardrail"]["claim"]
    )
    exclusion = next(
        row for row in result["candidates"]
        if row["label"] == "kk_exclusion_fixture"
    )
    assert exclusion["tower_spectrum"]["metadata"]["candidate_label"] == (
        "kk_exclusion_fixture"
    )
