"""Regression tests for v2.28 SDC adapter candidate scan."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from sdc_adapter_candidate_scan import diagnose_sdc_adapter_candidate_scan  # noqa: E402


def test_sdc_adapter_scan_exercises_all_verdict_regimes():
    result = diagnose_sdc_adapter_candidate_scan()
    verdicts = {
        row["label"]: row["framework_tower_verdict"]
        for row in result["candidates"]
    }

    assert verdicts["d4_allowance_fixture"] == "tower_allowed_by_predictive_spectrum"
    assert verdicts["d4_overlap_fixture"] == "tower_prediction_overlaps_threshold"
    assert verdicts["d4_exclusion_fixture"] == "tower_excluded_by_predictive_spectrum"
    assert result["claimable_if_sourced"] == ["d4_exclusion_fixture"]
    assert result["claimable_framework_exclusions_now"] == []


def test_sdc_adapter_scan_guardrail_and_metadata():
    result = diagnose_sdc_adapter_candidate_scan()
    exclusion = next(
        row for row in result["candidates"]
        if row["label"] == "d4_exclusion_fixture"
    )

    assert "synthetic SDC adapter candidates" in result["literature_guardrail"]["claim"]
    assert exclusion["tower_spectrum"]["metadata"]["candidate_label"] == (
        "d4_exclusion_fixture"
    )
    assert exclusion["two_sigma_phi_interval"][0] > 0.743
