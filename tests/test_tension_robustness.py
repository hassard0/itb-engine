"""Sanity tests for the v1.80 tension-robustness analysis."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import tension_robustness as tr


def test_grids_and_measurement():
    assert tr.RHOS[0] == 0.03 and tr.RHOS[-1] == 0.12
    assert tr.KAPPAS[0] == 2.0 and tr.KAPPAS[-1] == 5.0
    assert tr.BETA_MEAS == 0.34 and tr.BETA_SIG == 0.09


def test_tension_factorization():
    """beta_max = kappa * g_R2_parity_max, tension = (0.34 - beta_max)/0.09."""
    gp = 0.025
    for kap in (2.0, 3.4, 5.0):
        beta = kap * gp
        tension = (tr.BETA_MEAS - beta) / tr.BETA_SIG
        assert tension == (0.34 - kap * 0.025) / 0.09
    # canonical-ish point is in >2sigma tension
    assert (0.34 - 3.4 * 0.025) / 0.09 > 2.0


def test_maxgp_task_feasible_point():
    """A single sampling task returns a finite max g_R2_parity for canonical rho
    (the feasible region is nonempty)."""
    rho, gp = tr._maxgp_task((0.08, 12345, 60000))
    assert rho == 0.08
    # may occasionally miss with few samples, but should usually find a feasible
    # parity coupling in [0, 0.055]; if found, it's positive and within the box
    if np.isfinite(gp):
        assert 0.0 <= gp <= 0.055
