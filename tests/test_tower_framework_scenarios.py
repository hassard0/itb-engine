"""Regression tests for v2.22 tower framework assignment scenarios."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_framework_scenarios import diagnose_tower_framework_scenarios  # noqa: E402


def test_tower_framework_scenarios_are_assignment_dependent():
    result = diagnose_tower_framework_scenarios()
    scenarios = result["scenarios"]

    assert scenarios["unassigned"]["n_tower_excluded_reference_feasible"] == 0
    assert scenarios["low_phi_all"]["n_tower_excluded_reference_feasible"] == 0
    assert scenarios["near_threshold_all"]["n_tower_excluded_reference_feasible"] > 0
    assert scenarios["curvature_ranked_strong"]["n_tower_excluded_reference_feasible"] > 0
    assert result["robust_tower_exclusions_across_assigned_scenarios"] == []


def test_tower_framework_scenarios_guardrail_and_rows():
    result = diagnose_tower_framework_scenarios()

    assert "not framework predictions" in result["literature_guardrail"]["claim"]
    assert "not a framework verdict" in result["interpretation"]
    assert result["critical_phi_tower"] is not None
    row = result["scenarios"]["curvature_ranked_strong"]["frameworks"]["discovered_data_driven"]
    assert "phi_tower" in row
    assert "tower_allowed" in row
    assert "reference_feasible" in row
