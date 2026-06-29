"""Tests for the stochastic GW background spectral zoo (v2.272)."""

import math

from experiments.qnm_stochastic_gw_background import (
    inflationary_omega_gw,
    omega_gw_from_hc,
    omega_slope,
    run,
    timing_residual_gamma,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_spectral_slope_conversions():
    # SMBH binaries: h_c ~ f^-2/3 -> Omega_GW ~ f^+2/3, gamma = 13/3
    assert abs(omega_slope(-2 / 3) - 2 / 3) < 1e-12
    assert abs(timing_residual_gamma(-2 / 3) - 13 / 3) < 1e-12
    # scale-invariant -> flat Omega_GW
    assert abs(omega_slope(-1.0)) < 1e-12


def test_gamma_plus_omega_slope_invariant():
    # gamma = 3-2a, Omega slope = 2a+2  ->  their sum is always 5
    for a in (-1.0, -2 / 3, -0.5, 0.0, 0.5):
        assert abs(timing_residual_gamma(a) + omega_slope(a) - 5.0) < 1e-12


def test_omega_from_hc_scales_correctly():
    # Omega_GW ~ f^2 h_c^2 : doubling f at fixed h_c quadruples Omega
    o1 = omega_gw_from_hc(1e-8, 1e-15)
    o2 = omega_gw_from_hc(2e-8, 1e-15)
    assert abs(o2 / o1 - 4.0) < 1e-9
    # and ~ h_c^2
    o3 = omega_gw_from_hc(1e-8, 2e-15)
    assert abs(o3 / o1 - 4.0) < 1e-9


def test_nanograv_omega_order_of_magnitude():
    res = run()
    assert 1e-9 < res["nanograv"]["omega_gw_at_1yr"] < 1e-7


def test_primordial_inflation_far_below_detectors():
    # at the current r bound the primordial background is ~1e-16, below every detector (>=1e-13)
    assert inflationary_omega_gw(0.036) < 1e-13
    res = run()
    assert res["consistency_checks"]["primordial_inflation_below_all_detectors"] is True
    # linear in r
    assert abs(inflationary_omega_gw(0.02) - 2 * inflationary_omega_gw(0.01)) < 1e-30


def test_honest_scope_flags_order_of_magnitude_and_gamma_tension():
    res = run()
    sc = res["honest_scope"].lower()
    assert "order-of-magnitude" in sc or "order of magnitude" in sc
    assert "3.2" in res["nanograv"]["note"] or "shallower" in res["nanograv"]["note"]
    assert "not an engine constraint refit" in sc
