"""Regression tests for v2.27 SDC distance requirements."""

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from sdc_distance_requirements import diagnose_sdc_distance_requirements  # noqa: E402


def test_sharpened_sdc_distance_threshold_uses_dimension_slope():
    result = diagnose_sdc_distance_requirements(
        dimensions=[4],
        slopes=[],
        sigma_values=[0.05],
    )
    row = result["dimension_requirements"][0]
    threshold = row["distance_thresholds"][0]
    expected_lambda = 1.0 / math.sqrt(2.0)

    assert row["dimension"] == 4
    assert row["lambda_sdc"] == expected_lambda
    assert threshold["claimable_exclusion_requires_distance_gt"] == (
        (result["critical_phi_tower"] + 0.10) / expected_lambda
    )
    assert threshold["claimable_allowance_requires_distance_lte"] == (
        (result["critical_phi_tower"] - 0.10) / expected_lambda
    )


def test_sdc_distance_requirements_are_not_framework_claims():
    result = diagnose_sdc_distance_requirements(
        dimensions=[4, 10],
        slopes=[1.0],
        sigma_values=[0.0, 0.05],
    )

    assert result["claimable_framework_exclusions_now"] == []
    assert "not framework predictions" in result["literature_guardrail"]["claim"]
    assert "Delta_moduli" in result["interpretation"]
    assert len(result["dimension_requirements"]) == 2
    assert len(result["slope_requirements"]) == 1
