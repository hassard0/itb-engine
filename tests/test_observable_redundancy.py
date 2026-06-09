"""Tests for the observable redundancy map (v2.05)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import observable_redundancy as orr


def test_obs_vector_length_and_inflation_constant():
    x1 = np.array([0.4, 0.35, 0.4, 0.2, 0.1, 0.25, 0.05, 0.0])
    x2 = np.array([0.5, 0.40, 0.5, 0.3, 0.2, 0.35, 0.08, 0.0])
    v1, v2 = orr._obs_vector(x1), orr._obs_vector(x2)
    assert len(v1) == len(orr.OBS_NAMES) == 9
    # inflation_r is coefficient-independent (zero Jacobian, v1.88)
    i = orr.OBS_NAMES.index("inflation_r")
    assert v1[i] == v2[i]


def test_g_R2_driven_observables_move_together():
    """sub-mm Yukawa and eta/s are both g_R2-driven -> move together (the Euler block)."""
    base = np.array([0.4, 0.35, 0.4, 0.2, 0.1, 0.25, 0.05, 0.0])
    hi = base.copy(); hi[orr.COEFFS.index("g_R2")] = 0.35
    s = orr.OBS_NAMES.index("submm_yukawa"); e = orr.OBS_NAMES.index("eta_s")
    d_lo, d_hi = orr._obs_vector(base), orr._obs_vector(hi)
    assert np.sign(d_hi[s] - d_lo[s]) == np.sign(d_hi[e] - d_lo[e])


def test_correlation_matrix_symmetric_unit_diag():
    Y = np.random.default_rng(0).random((300, 9))
    C = np.corrcoef(Y.T)
    assert np.allclose(C, C.T)
    assert np.allclose(np.diag(C), 1.0)
