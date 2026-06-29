"""Tests for the black-hole tidal Love number (v2.235)."""

from experiments.qnm_tidal_love_number import integrate_regular, legendre_residual, run


def test_legendre_polynomials_solve_static_perturbation():
    # P_l^2 polynomials solve the associated Legendre (static perturbation) ODE exactly
    assert legendre_residual(2) < 1e-9
    assert legendre_residual(3) < 1e-9


def test_no_decaying_tidal_response_tail():
    # the horizon-regular solution stays a pure growing polynomial -> no induced-response tail
    for l in (2, 3):
        integ = integrate_regular(l)
        assert integ["tail_fraction"] < 1e-6


def test_love_numbers_vanish():
    res = run()
    assert res["all_zero"] is True
    for r in res["love_numbers"]:
        assert r["love_number_k_l"] == 0.0
        assert r["is_polynomial_degree_l"] is True


def test_honest_scope_static_schwarzschild():
    res = run()
    sc = res["honest_scope"].lower()
    assert "static" in sc and "schwarzschild" in sc
    assert "kerr" in sc          # the dynamical/Kerr subtlety is flagged
    assert "g_R4_c3" in res["honest_scope"]
