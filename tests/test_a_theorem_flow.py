"""Tests for the a-theorem along the RG phylogeny (v1.99)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import a_theorem_flow as af
from phylogeny import flow, COEFFS


def test_a_monotone_along_flow():
    """a = g_R2 is monotone along the toy flow (exponential approach to the fixed point)."""
    g0 = np.zeros(len(COEFFS)); g0[COEFFS.index("g_R2")] = 0.3
    t, Y = flow(g0)
    da = np.diff(Y[:, COEFFS.index("g_R2")])
    assert np.all(da <= 1e-9) or np.all(da >= -1e-9)


def test_violation_when_above_fixed_point():
    """a framework with g_R2 > a* violates the a-theorem (a increases toward the IR)."""
    assert af.A_STAR == 0.15
    # string tree-EFT has g_R2 = 0.2 > 0.15 -> violates
    from itb.frameworks.string_tree_eft import StringTreeEFT
    g = StringTreeEFT().encode().coefficients.get("g_R2", 0.0)
    assert g > af.A_STAR                      # above the fixed point -> would violate


def test_required_a_star_dominates():
    """The a-theorem requires a* >= the largest framework a."""
    from itb.predict import FRAMEWORKS
    max_a = max(f.encode().coefficients.get("g_R2", 0.0) for f in FRAMEWORKS.values())
    assert max_a > af.A_STAR                  # current fixed point is too low
    assert max_a == __import__("pytest").approx(0.45, abs=0.05)
