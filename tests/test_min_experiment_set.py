"""Tests for the minimum decisive experiment set (D-optimal design) -- v1.88."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import min_experiment_set as mes
from itb.gravitational_observables import StarobinskyInflation
from itb.theory import Theory


def test_design_probes_cover_blind_spots():
    """The two design-probe observables touch g_8 and g_R3 (which no core observable
    constrains)."""
    th = Theory(coefficients={k: 0.3 for k in mes.PARAMS})
    Jh = mes.HighScatteringMoment([1.0]).jacobian(th, mes.PARAMS)
    Jc = mes.CubicGravitonAmplitude().jacobian(th, mes.PARAMS)
    assert Jh[0, mes.PARAMS.index("g_8")] != 0.0
    assert Jc[0, mes.PARAMS.index("g_R3")] != 0.0


def test_fisher_psd_and_monotone():
    """Adding an observable's Fisher contribution never decreases log det."""
    th = Theory(coefficients={k: 0.3 for k in mes.PARAMS})
    F = 1e-6 * np.eye(len(mes.PARAMS))
    obs = mes.HighScatteringMoment([1.0, 1.5])
    J = obs.jacobian(th, mes.PARAMS)
    contrib = (J.T @ J) / 0.1 ** 2
    # PSD
    assert np.all(np.linalg.eigvalsh(contrib) >= -1e-9)
    # monotone in log det
    assert np.linalg.slogdet(F + contrib)[1] >= np.linalg.slogdet(F)[1]


def test_inflation_zero_jacobian_adds_nothing():
    """StarobinskyInflation has a zero Jacobian -> no Fisher information."""
    th = Theory(coefficients={k: 0.3 for k in mes.PARAMS})
    J = StarobinskyInflation().jacobian(th, mes.PARAMS)
    F = (J.T @ J)
    assert np.allclose(F, 0.0)
