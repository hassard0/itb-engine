"""Regression tests for v2.18 tower-surrogate overlap diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_surrogate_distance import TOWER_MODES  # noqa: E402
from tower_surrogate_overlap import audit_tower_surrogate_overlap  # noqa: E402


PHASES = ROOT / "experiments/results/v2.13/phases_8d_1200.json"


def test_tower_surrogate_overlap_records_all_modes_and_reference_gate():
    result = audit_tower_surrogate_overlap(PHASES, samples=600, seed=11, N_max=3.0)

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
    assert set(result["modes"]) == set(TOWER_MODES)

    for mode in TOWER_MODES:
        row = result["modes"][mode]
        assert row["reference_feasible"] > 0
        assert row["candidate_feasible"] > 0
        assert row["candidate_feasible"] <= row["reference_feasible"]
        assert row["irreplaceability_growth_pct"] is not None
        assert "swampland_distance_conjecture" in row["overlap_reference_gate"]
        assert "species_scale_bound" in row["overlap_all_surrogate_failures"]


def test_tower_surrogate_overlap_is_labeled_as_targeted_not_global_proof():
    result = audit_tower_surrogate_overlap(PHASES, samples=300, seed=13, N_max=3.0)

    assert "targeted" in result["sampling"]
    assert "not a global Monte Carlo volume theorem" in result["guardrail"]
    assert "not a validation" in result["guardrail"]
