"""Regression tests for the v2.14 curved-bridge diagnostic."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from phase_bridges import diagnose  # noqa: E402


def test_phase_bridge_diagnostic_identifies_distance_prior_blocker():
    result = diagnose(ROOT / "experiments/results/v2.13/phases_8d_1200.json", samples=31)

    assert result["parity_zero_projections_mutually_connected"] is True
    assert result["first_failure_blockers"] == {"swampland_distance_conjecture": 4}
    assert "encoding artifact" in result["conclusion"]


def test_phase_bridge_diagnostic_records_current_basis():
    result = diagnose(ROOT / "experiments/results/v2.13/phases_8d_1200.json", samples=11)

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
    assert result["distance_constraint"]["R_max"] == 20.0
