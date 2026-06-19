"""Regression tests for the full-basis phase-mapping experiment."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

import phases  # noqa: E402


def test_phases_experiment_uses_current_eight_coefficient_basis():
    assert phases.KEYS == [
        "g_4",
        "g_6",
        "g_8",
        "g_R2",
        "g_R3",
        "g_C",
        "g_R2_parity",
        "g_R3_parity",
    ]
    assert len(phases.LO) == len(phases.HI) == 8
    assert phases.LO[phases.KEYS.index("g_C")] > 0.0


def test_phases_experiment_uses_live_framework_registry():
    assert "discovered_data_driven" in phases.KNOWN
    assert "group_field_theory" in phases.KNOWN
