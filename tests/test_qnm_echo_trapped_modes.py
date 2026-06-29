"""Tests for the echo trapped-mode comb (v2.248)."""

from experiments.qnm_echo_trapped_modes import (
    comb_spacing_hz,
    f_qnm_hz,
    n_trapped,
    run,
)


def test_comb_spacing_is_inverse_echo_delay():
    # Delta f = 1/Delta t_echo; smaller eps (longer delay) -> finer comb
    assert comb_spacing_hz(30.0, 1e-40) < comb_spacing_hz(30.0, 1e-10)


def test_n_trapped_scale_invariant():
    res = run()
    assert res["n_trapped_scale_invariant"] is True
    # the count depends only on eps, not the BH mass
    assert abs(n_trapped(30.0, 1e-40) - n_trapped(1e6, 1e-40)) < 1e-6


def test_n_trapped_grows_as_surface_nears_horizon():
    # smaller eps -> longer cavity -> more trapped modes
    assert n_trapped(30.0, 1e-40) > n_trapped(30.0, 1e-10)


def test_qnm_frequency_inverse_with_mass():
    assert f_qnm_hz(30.0) > f_qnm_hz(60.0)
    # ~400 Hz for a 30 Msun hole
    assert 200 < f_qnm_hz(30.0) < 600


def test_honest_scope_quasi_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "quasi-bound" in sc and "leading" in sc
    assert "not a detection claim" in sc
    assert "g_R4_c3" in res["honest_scope"]
