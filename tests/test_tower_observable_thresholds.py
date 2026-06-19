"""Regression tests for v2.21 tower-observable thresholds."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_observable_thresholds import diagnose_tower_observable_thresholds  # noqa: E402


def test_tower_observable_thresholds_quantify_required_measurements():
    result = diagnose_tower_observable_thresholds(
        phi_grid=[0.0, 0.5, 1.0, 1.5],
        lambda_eft_values=[0.5, 0.65],
        mass_floors=[0.4, 0.5],
        cutoff_floors=[0.5, 0.65],
        confidence_fractions=[0.25, 0.5],
    )

    assert result["basis"] == ["phi_tower", "m_tower", "Lambda_species"]
    threshold = next(row for row in result["lambda_eft_thresholds"] if row["lambda_eft"] == 0.65)
    assert threshold["critical_phi_tower"] is not None
    assert threshold["allowed_fraction_on_phi_grid"] < 1.0

    mass_floor = next(
        row for row in result["tower_mass_floor_thresholds"]
        if row["tower_mass_floor"] == 0.5
    )
    assert mass_floor["rules_out_tower_excluded_region"] is True


def test_tower_observable_thresholds_guardrail_and_scenarios():
    result = diagnose_tower_observable_thresholds(
        phi_grid=[0.0, 0.4, 0.8, 1.2],
        lambda_eft_values=[0.65],
    )

    assert "do not assign phi_tower" in result["literature_guardrail"]["claim"]
    assert "do not constitute a physical SDC solution" in result["literature_guardrail"]["claim"]
    assert any(row["rules_out_entire_tower_fiber"] for row in result["measurement_scenarios"])
    assert "observable" in result["interpretation"]
