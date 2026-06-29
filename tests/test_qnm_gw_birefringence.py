"""Tests for GW amplitude birefringence in parity-violating gravity (v2.269)."""

import cmath
import math

import numpy as np

from experiments.qnm_gw_birefringence import (
    birefringence_exponent,
    circular_basis,
    induced_circular_polarization,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_circular_modes_are_helicity_eigenstates():
    eR, eL = circular_basis()
    psi = 0.37
    c, s = math.cos(psi), math.sin(psi)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
    lamR = np.sum(np.conj(eR) * (R @ eR @ R.T)) / np.sum(np.conj(eR) * eR)
    lamL = np.sum(np.conj(eL) * (R @ eL @ R.T)) / np.sum(np.conj(eL) * eL)
    assert abs(lamR - cmath.exp(-2j * psi)) < 1e-12   # helicity +2
    assert abs(lamL - cmath.exp(+2j * psi)) < 1e-12   # helicity -2


def test_circular_modes_orthonormal():
    eR, eL = circular_basis()
    assert abs(np.sum(np.conj(eR) * eL)) < 1e-12
    assert abs(np.sum(np.conj(eR) * eR) - 2.0) < 1e-12


def test_gr_limit_no_induced_polarization():
    assert abs(induced_circular_polarization(0.0)) < 1e-15
    res = run()
    assert abs(res["gr_limit_induced_V"]) < 1e-15


def test_birefringence_is_chromatic_linear_in_frequency():
    # zeta ~ kappa k D ~ f : doubling the frequency doubles the exponent
    z1 = birefringence_exponent(1e-27, 50.0, 1e25)
    z2 = birefringence_exponent(1e-27, 100.0, 1e25)
    assert abs(z2 - 2 * z1) < 1e-9 * z2
    res = run()
    assert res["consistency_checks"]["birefringence_is_chromatic"] is True


def test_induced_V_is_tanh_2zeta():
    for z in (1e-9, 1e-3, 0.5):
        assert abs(induced_circular_polarization(z) - math.tanh(2 * z)) < 1e-15


def test_honest_scope_flags_representative_coupling():
    res = run()
    sc = res["honest_scope"].lower()
    assert "representative" in sc
    assert "leading" in sc
    assert "not a re-derivation" in sc or "not a calibrated" in sc
    assert "g_R2_parity" in res["engine_link"]
