"""Regression tests for v2.17 tower/species surrogate diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_surrogate_distance import TOWER_MODES, diagnose_tower_surrogates  # noqa: E402


PHASES = ROOT / "experiments/results/v2.13/phases_8d_1200.json"


def test_tower_surrogates_pass_basic_gate_at_species_cap_three():
    result = diagnose_tower_surrogates(
        PHASES,
        samples=31,
        nmax_values=[2.0, 2.4, 2.8, 3.0],
    )

    assert result["baselines"]["default"]["all_connected_by_parity_zero_detour"] is False
    assert (
        result["baselines"]["no_distance_or_species_prior"][
            "all_connected_by_parity_zero_detour"
        ]
        is True
    )

    for mode in TOWER_MODES:
        candidate = result["candidates_at_N_max_3"][mode]
        assert candidate["accepted_basic_surrogate_gate"] is True
        assert candidate["topology"]["all_connected_by_parity_zero_detour"] is True
        assert candidate["frameworks"]["additional_exclusions_vs_reference"] == []
        assert candidate["frameworks"]["prior_only_failures"] == []
        assert (
            candidate["epsilon_to_zero_continuity"]["has_punctured_gap_near_zero"]
            is False
        )
        assert candidate["curvature_monotonicity"]["tower_load_non_decreasing"] is True
        assert candidate["curvature_monotonicity"]["margin_non_increasing"] is True


def test_tower_surrogate_result_is_guardrailed_as_acceptance_test_not_sdc_solution():
    result = diagnose_tower_surrogates(
        PHASES,
        samples=11,
        nmax_values=[2.0, 3.0],
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
    assert "acceptance tests" in result["literature_guardrail"]["claim"]
    assert "not canonical SDC replacements" in result["literature_guardrail"]["claim"]
    assert all(
        result["N_max_sweeps"][mode]["first_accepting_N_max"] is not None
        for mode in TOWER_MODES
    )
