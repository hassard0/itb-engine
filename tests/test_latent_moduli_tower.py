"""Regression tests for v2.19 latent moduli/tower diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from latent_moduli_tower import DEFAULT_CONFIGS, diagnose_latent_moduli_tower  # noqa: E402


PHASES = ROOT / "experiments/results/v2.13/phases_8d_1200.json"


def test_latent_moduli_tower_records_explicit_tower_observables():
    result = diagnose_latent_moduli_tower(
        PHASES,
        samples=21,
        targeted_samples=500,
        seed=17,
        nmax_values=[1.8, 2.2, 3.0],
    )

    assert result["basis"] == [
        "g_4",
        "g_6",
        "g_8",
        "g_R2",
        "g_R3",
        "g_C",
        "g_R2_parity",
        "g_R3_parity",
    ]
    assert set(result["candidates_at_N_max_3"]) == {config.name for config in DEFAULT_CONFIGS}

    candidate = result["candidates_at_N_max_3"]["centroid_transverse"]
    component = candidate["centroid_latent_observables"][0]["centroid"]
    for key in ("latent_distance", "tower_mass", "N_tower", "species_cutoff"):
        assert key in component
    assert candidate["radial_monotonicity"]["distance_non_decreasing"] is True
    assert candidate["radial_monotonicity"]["tower_mass_non_increasing"] is True
    assert candidate["radial_monotonicity"]["species_non_decreasing"] is True
    assert candidate["radial_monotonicity"]["species_cutoff_non_increasing"] is True

    sensitivity = result["parameter_sensitivity"]["centroid_transverse"]
    assert sensitivity
    assert {"lambda_tower", "kappa", "transverse_weight"}.issubset(sensitivity[0])


def test_latent_moduli_tower_guardrails_and_basic_gate():
    result = diagnose_latent_moduli_tower(
        PHASES,
        samples=21,
        targeted_samples=400,
        seed=19,
        nmax_values=[1.8, 2.2, 3.0],
    )

    assert "not a physical implementation" in result["literature_guardrail"]["claim"]
    assert "not an SDC solution" in result["interpretation"]

    candidate = result["candidates_at_N_max_3"]["centroid_radial"]
    assert candidate["accepted_basic_latent_gate"] is True
    assert candidate["topology"]["all_connected_by_parity_zero_detour"] is True
    assert candidate["frameworks"]["additional_exclusions_vs_reference"] == []
    assert candidate["epsilon_to_zero_continuity"]["has_punctured_gap_near_zero"] is False
    assert result["N_max_sweeps"]["centroid_radial"]["first_accepting_N_max"] is not None
