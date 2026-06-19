"""Regression tests for v2.40 tower-gate recalibration options."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_gate_recalibration_options import (  # noqa: E402
    diagnose_tower_gate_recalibration_options,
)


def test_recalibration_options_compute_positive_control_safe_threshold():
    result = diagnose_tower_gate_recalibration_options()

    assert result["current_critical_phi_tower"] == pytest.approx(0.7433019116911739)
    assert result["positive_control_safe_critical_phi_tower"] == pytest.approx(
        (3.0 / 2.0) ** 0.5
    )
    assert len(result["positive_controls_rejected_by_current_gate"]) == 7
    assert result["positive_controls_rejected_after_global_threshold_recalibration"] == []


def test_recalibration_options_do_not_create_claims_or_mutate_gate():
    result = diagnose_tower_gate_recalibration_options()

    assert result["claimable_framework_exclusions_now"] == []
    assert result["options"]["raise_global_threshold"][
        "production_change_recommended_now"
    ] is False
    assert result["options"]["positive_control_promotion_block"][
        "production_change_recommended_now"
    ] is True
    assert "does not change the engine gate" in result["literature_guardrail"]["claim"]


def test_recalibration_options_recommend_promotion_guard():
    result = diagnose_tower_gate_recalibration_options()

    assert "promotion guard" in result["recommended_next_implementation"]
    assert "known string-compatible decompactification" in (
        result["recommended_next_implementation"]
    )
    assert "source-scope classifier" in result["options"][
        "scope_limit_decompactification_controls"
    ]["tradeoff"]
