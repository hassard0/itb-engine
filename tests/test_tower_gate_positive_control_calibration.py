"""Regression tests for v2.39 tower-gate positive-control calibration."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_gate_positive_control_calibration import (  # noqa: E402
    diagnose_tower_gate_positive_control_calibration,
)


def test_positive_control_calibration_rejects_current_gate_as_discriminator():
    result = diagnose_tower_gate_positive_control_calibration()

    assert result["positive_control_count"] == 7
    assert result["positive_control_rejection_count"] == 7
    assert result["calibration_status"] == (
        "tower_gate_fails_positive_control_calibration"
    )
    assert result["calibrated_discriminator_ready"] is False
    assert result["tower_discriminator_candidates_now"] == []
    assert result["claimable_framework_exclusions_now"] == []


def test_positive_controls_are_known_qg_and_math_rejected():
    result = diagnose_tower_gate_positive_control_calibration()

    assert all(row["known_qg_positive_control"] for row in result["controls"])
    assert all(row["math_excluded_by_current_gate"] for row in result["controls"])
    assert all(
        row["calibration_verdict"] == "positive_control_rejected_by_tower_gate"
        for row in result["controls"]
    )


def test_positive_control_calibration_guardrail():
    result = diagnose_tower_gate_positive_control_calibration()

    assert "Do not promote tower-gate math exclusions" in result["action_required"]
    assert "not evidence for a solution claim" in result["literature_guardrail"]["claim"]
    assert "cannot support framework exclusions" in result["interpretation"]
