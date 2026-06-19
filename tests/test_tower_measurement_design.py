"""Regression tests for v2.23 tower measurement design."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_measurement_design import diagnose_tower_measurement_design  # noqa: E402


def test_mass_floor_measurement_disambiguates_assignments_not_frameworks():
    result = diagnose_tower_measurement_design(
        mass_floors=[0.5],
        phi_upper_bounds=[],
        measured_phi_intervals=[],
    )

    row = next(
        candidate
        for candidate in result["candidate_measurements"]
        if candidate["measurement"]["label"] == "mass_floor_0.5"
    )
    assert "near_threshold_all" in row["ruled_out_scoreable_scenarios"]
    assert row["n_ruled_out_scoreable_scenarios"] > 0
    assert row["claimable_framework_exclusions"] == []
    assert row["scenario_results"]["unassigned"]["measurement_scoreable"] is False


def test_measurement_design_guardrail_and_ranked_outputs():
    result = diagnose_tower_measurement_design(
        mass_floors=[0.5, 0.8],
        phi_upper_bounds=[0.6],
        measured_phi_intervals=[(0.75, 0.05)],
    )

    assert "measurement design audit" in result["literature_guardrail"]["claim"]
    assert "not framework exclusion" in result["literature_guardrail"]["claim"]
    assert "unassigned scenario remains viable" in result["interpretation"]
    assert result["top_measurement_designs"]
    assert all(
        row["claimable_framework_exclusions"] == []
        for row in result["top_measurement_designs"]
    )
