"""Tests for the parametrized-ringdown-basis operator->QNM machinery (v2.214)."""

import numpy as np

from experiments.qnm_parametrized_basis import (
    E_J,
    R_H,
    basis_delta_V,
    decompose_delta_V,
    qnm_shift,
    validate,
)


def test_basis_function_decomposes_to_unit_alpha():
    for k in E_J:
        a = decompose_delta_V(basis_delta_V(k), max(E_J))
        assert abs(a[k] - 1.0) < 1e-8
        for j in range(len(a)):
            if j != k:
                assert abs(a[j]) < 1e-7


def test_basis_function_shift_equals_published_e_k():
    for k in E_J:
        a = decompose_delta_V(basis_delta_V(k), max(E_J))
        assert abs(qnm_shift(a) - E_J[k]) / abs(E_J[k]) < 1e-8


def test_linearity_of_the_contraction():
    combo = lambda r: (basis_delta_V(0)(r) + 2 * basis_delta_V(1)(r)
                       - 0.5 * basis_delta_V(2)(r))
    a = decompose_delta_V(combo, max(E_J))
    expected = E_J[0] + 2 * E_J[1] - 0.5 * E_J[2]
    assert abs(qnm_shift(a) - expected) / abs(expected) < 1e-8


def test_decomposition_of_a_polynomial_in_inverse_r():
    # delta_V = (1/r_H^2)[ (r_H/r)^1 + 3 (r_H/r)^2 ]  -> alpha_1=1, alpha_2=3
    dV = lambda r: (1.0 / R_H**2) * ((R_H / r) + 3.0 * (R_H / r) ** 2)
    a = decompose_delta_V(dV, 2)
    assert abs(a[0]) < 1e-7
    assert abs(a[1] - 1.0) < 1e-7
    assert abs(a[2] - 3.0) < 1e-7


def test_validate_machinery_passes_and_gate_closed():
    res = validate()
    assert res["machinery_validated"] is True
    assert res["claim_gate"].startswith("closed")
