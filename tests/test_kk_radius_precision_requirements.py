"""Regression tests for v2.30 KK-radius precision requirements."""

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from kk_radius_precision_requirements import (  # noqa: E402
    diagnose_kk_radius_precision_requirements,
)


def test_kk_radius_precision_requirements_invert_thresholds():
    result = diagnose_kk_radius_precision_requirements(
        radius_ratios=[1.70, 2.60],
        check_sigmas=[0.03, 0.05],
    )
    critical_phi = result["critical_phi_tower"]
    allowance = result["radius_precision_requirements"][0]
    exclusion = result["radius_precision_requirements"][1]

    assert allowance["side_of_critical_radius"] == "allowance_side"
    assert allowance["target_verdict"] == "tower_allowance"
    assert allowance["max_log_radius_sigma_for_target_verdict"] == (
        0.5 * (critical_phi - math.log(1.70))
    )

    assert exclusion["side_of_critical_radius"] == "exclusion_side"
    assert exclusion["target_verdict"] == "tower_exclusion"
    assert exclusion["max_log_radius_sigma_for_target_verdict"] == (
        0.5 * (math.log(2.60) - critical_phi)
    )


def test_kk_radius_precision_requirements_verdict_checks_and_guardrail():
    result = diagnose_kk_radius_precision_requirements(
        radius_ratios=[2.60],
        check_sigmas=[0.03, 0.20],
    )
    row = result["radius_precision_requirements"][0]
    verdicts = {
        item["log_radius_sigma"]: item["verdict"]
        for item in row["verdict_at_check_sigmas"]
    }

    assert verdicts[0.03] == "tower_exclusion"
    assert verdicts[0.20] == "overlap"
    assert result["claimable_framework_exclusions_now"] == []
    assert "do not assign a radius" in result["literature_guardrail"]["claim"]


def test_kk_radius_precision_requirements_classifies_critical_boundary():
    result = diagnose_kk_radius_precision_requirements(
        radius_ratios=[2.102867546654528],
        check_sigmas=[0.0, 0.01],
    )
    row = result["radius_precision_requirements"][0]

    assert row["side_of_critical_radius"] == "critical_boundary"
    assert row["max_log_radius_sigma_for_target_verdict"] == 0.0
    assert row["target_verdict"] == "tower_allowance_only_at_zero_uncertainty"
