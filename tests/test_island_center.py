"""Tests for the island-center (Chebyshev deepest-interior) result (v1.74).

We do NOT re-run the optimizer here (slow); we pin the computed center and assert
it is a genuine interior point with positive wall slack and a parity-even encoding.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import island_center as ic

# computed v1.74 center (g_4, g_6, g_8, g_R2, g_R3, g_C)
CENTER = np.array([0.5216, 0.3843, 0.4351, 0.2135, 0.0773, 0.2316])


def test_theory_is_parity_even():
    th = ic._theory(CENTER)
    assert th.coefficients["g_R2_parity"] == 0.0
    assert th.coefficients["g_R3_parity"] == 0.0


def test_center_is_interior():
    """Every constraint is satisfied at the center (a true interior point)."""
    th = ic._theory(CENTER)
    assert all(c.evaluate(th).satisfied for c in ic._STACK)


def test_wall_inradius_positive():
    """The minimum one-sided-wall signed-distance margin is comfortably > 0."""
    m = ic._margins(CENTER)
    wall_min = float(np.min(m[ic._WALL_IDX]))
    assert wall_min > 0.05
    # several walls are near-tight (the active set), not just one
    near = np.sum(m[ic._WALL_IDX] <= wall_min + 0.02)
    assert near >= 3


def test_bands_are_excluded_from_walls():
    assert "t_hooft_anomaly_matching" in ic._BANDS
    assert "anomaly_cancellation" in ic._BANDS
    assert len(ic._WALL_IDX) == len(ic._STACK) - len(ic._BANDS)
