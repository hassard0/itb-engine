"""Tests for the convergence forecast (v1.92)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import convergence_forecast as cf
from itb.frameworks.data_driven import DiscoveredDataDriven


def test_fisher_psd():
    th = DiscoveredDataDriven().encode()
    for k in cf.PARAMS:
        th.coefficients.setdefault(k, 0.0)
    from itb.gravitational_observables import BlackHoleEntropyShift
    F = cf.fisher(BlackHoleEntropyShift(), 0.1, th)
    assert np.all(np.linalg.eigvalsh(F) >= -1e-9)


def test_stalls_at_six_without_blind_spot_probes():
    """g_8 and g_R3 have no funded probe -> the funded roadmap pins only 6/8."""
    th = DiscoveredDataDriven().encode()
    for k in cf.PARAMS:
        th.coefficients.setdefault(k, 0.0)
    F = 1e-6 * np.eye(cf.N)
    # funded-only Fisher: the observables with a milestone year (no g_8 / g_R3 probe)
    from itb.observables import ScalarForwardAmplitude
    from itb.gravitational_observables import (YukawaForceDeviation,
        GravitationalBirefringence, HolographicEtaOverS, BlackHoleEntropyShift)
    funded = [BlackHoleEntropyShift(), HolographicEtaOverS(),
              ScalarForwardAmplitude(np.array([0.5, 1.0])),
              YukawaForceDeviation([8e-5, 1e-4]), GravitationalBirefringence([1.0, 2.0])]
    for o in funded:
        F = F + cf.fisher(o, 0.1, th)
    rank = int(np.linalg.matrix_rank(F - 1e-6 * np.eye(cf.N), tol=1e-9))
    assert rank == 6                                    # g_8, g_R3 unconstrained


def test_blind_spot_probes_reach_full_rank():
    """Adding the high-moment (g_8) and cubic-graviton (g_R3) probes reaches rank 8."""
    from min_experiment_set import HighScatteringMoment, CubicGravitonAmplitude
    th = DiscoveredDataDriven().encode()
    for k in cf.PARAMS:
        th.coefficients.setdefault(k, 0.0)
    F = 1e-6 * np.eye(cf.N)
    from itb.observables import ScalarForwardAmplitude
    from itb.gravitational_observables import (YukawaForceDeviation,
        GravitationalBirefringence, HolographicEtaOverS, BlackHoleEntropyShift)
    allobs = [BlackHoleEntropyShift(), HolographicEtaOverS(),
              ScalarForwardAmplitude(np.array([0.5, 1.0])),
              YukawaForceDeviation([8e-5, 1e-4]), GravitationalBirefringence([1.0, 2.0]),
              HighScatteringMoment([1.0, 1.5]), CubicGravitonAmplitude()]
    for o in allobs:
        F = F + cf.fisher(o, 0.1, th)
    rank = int(np.linalg.matrix_rank(F - 1e-6 * np.eye(cf.N), tol=1e-9))
    assert rank == 8
