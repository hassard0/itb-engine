"""Tests for the black-hole superradiance ultralight-boson bound (v2.243)."""

from experiments.qnm_superradiance_boson_bound import (
    alpha_max,
    boson_mass_eV,
    horizon_angular_velocity,
    run,
)


def test_horizon_angular_velocity_limits():
    assert abs(horizon_angular_velocity(0.0)) < 1e-12          # Schwarzschild: no rotation
    assert abs(horizon_angular_velocity(1.0) - 0.5) < 1e-9     # extremal Kerr: Omega_H = 1/2


def test_superradiance_alpha_scales_with_mode():
    a = 0.9
    assert abs(alpha_max(a, 2) - 2 * alpha_max(a, 1)) < 1e-12
    assert alpha_max(a, 1) > 0


def test_boson_mass_window_inverse_with_bh_mass():
    # heavier black holes probe lighter bosons (mu ~ 1/M)
    light = boson_mass_eV(0.3, 10.0)
    heavy = boson_mass_eV(0.3, 1e9)
    assert light > heavy
    assert abs(light / heavy - 1e8) / 1e8 < 1e-6
    # stellar holes probe ~1e-12 eV, supermassive ~1e-20 eV
    assert 1e-13 < light < 1e-11


def test_run_windows_span_ultralight_range():
    res = run()
    masses = [w["mu_max_eV"] for w in res["boson_mass_windows"]]
    assert max(masses) > 1e-12 and min(masses) < 1e-20


def test_honest_scope_growth_timescale():
    res = run()
    sc = res["honest_scope"].lower()
    assert "growth" in sc and "exact kerr" in sc
    assert "alpha^9" in sc or "alpha^{4l+5}" in sc
    assert "g_R4_c3" in res["honest_scope"]
