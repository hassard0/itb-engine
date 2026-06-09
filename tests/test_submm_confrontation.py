"""Tests for the sub-mm gravity confrontation (v1.76)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import submm_confrontation as sc


def test_exclusion_curve_monotone():
    """The 95% CL excluded-|alpha| falls as lambda grows (more sensitive at
    longer range)."""
    lams = [25, 40, 60, 80, 120, 180]
    bounds = [sc.alpha_excluded_at(l) for l in lams]
    assert all(bounds[i] > bounds[i + 1] for i in range(len(bounds) - 1))


def test_central_prediction_excluded():
    """alpha=1/3 at lambda=80um is above the exclusion curve (excluded)."""
    bound = sc.alpha_excluded_at(80.0)
    assert sc.ALPHA > bound
    assert sc.ALPHA / bound > 3.0          # excluded by a healthy margin


def test_gR2_lambda_inversion():
    """g_R2_for_lambda inverts the lambda(g_R2) map at the center."""
    assert sc.g_R2_for_lambda(80.0) == __import__("pytest").approx(0.158, abs=0.01)
    # to evade (lambda < ~50um) requires a smaller g_R2 than the center's ~0.16
    assert sc.g_R2_for_lambda(50.0) < 0.158
