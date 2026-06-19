"""Regression tests for v2.20 explicit tower-coordinate diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from explicit_tower_basis import EXTENDED_KEYS, diagnose_explicit_tower_basis  # noqa: E402


PHASES = ROOT / "experiments/results/v2.13/phases_8d_1200.json"


def test_explicit_tower_basis_adds_independent_gate_on_auxiliary_coordinate():
    result = diagnose_explicit_tower_basis(
        PHASES,
        samples=700,
        seed=23,
        phi_grid=[0.0, 0.5, 1.0, 1.5],
        lambda_eft_values=[0.6, 0.65],
    )

    gate = result["main_gate"]
    assert result["basis"] == EXTENDED_KEYS
    assert gate["explicit_tower_gate_count"] > 0
    assert gate["gate_passes_old_distance_and_species"] > 0
    assert gate["candidate_feasible_extended"] < gate["reference_feasible_extended"]
    assert gate["irreplaceability_growth_pct"] > 0.0
    assert result["old_stack_phi_isolation"]["old_stack_verdicts_invariant_under_phi_tower"] is True
    assert result["projection_audit"]["projected_island_unchanged"] is True


def test_explicit_tower_basis_records_cutoff_monotonicity_and_guardrails():
    result = diagnose_explicit_tower_basis(
        PHASES,
        samples=300,
        seed=29,
        phi_grid=[0.0, 0.4, 0.8, 1.2],
        lambda_eft_values=[0.5, 0.65],
    )

    monotone = result["tower_monotonicity"]
    assert monotone["tower_mass_non_increasing"] is True
    assert monotone["species_count_non_decreasing"] is True
    assert monotone["species_cutoff_non_increasing"] is True
    assert monotone["margin_non_increasing"] is True
    assert result["parameter_monotonicity"]["cutoff_non_increasing_with_density"] is True
    assert result["parameter_monotonicity"]["cutoff_non_increasing_with_lambda"] is True
    assert result["parameter_monotonicity"]["mass_non_increasing_with_lambda"] is True
    assert result["solver_edge_cases"]["max_abs_residual"] < 1e-12
    assert result["solver_edge_cases"]["all_cutoffs_in_unit_interval"] is True
    assert result["critical_phi"]["critical_phi"] is not None
    assert "diagnostic basis-extension test" in result["literature_guardrail"]["claim"]
    assert "not a validation" in result["literature_guardrail"]["claim"]
