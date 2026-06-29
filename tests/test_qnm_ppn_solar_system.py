"""Tests for the PPN solar-system tests of GR (v2.280)."""

from experiments.qnm_ppn_solar_system import (
    gravitational_redshift,
    light_deflection_arcsec,
    mercury_precession_arcsec_century,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_light_deflection_GR_value():
    # 1.75 arcsec at the solar limb for gamma = 1
    assert abs(light_deflection_arcsec(1.0) - 1.75) < 0.01


def test_newton_deflection_is_half():
    # gamma=0 (Newtonian) gives exactly half -- the 1919 eclipse discriminant
    assert abs(light_deflection_arcsec(0.0) / light_deflection_arcsec(1.0) - 0.5) < 1e-9


def test_deflection_scales_with_one_plus_gamma():
    for g in (0.0, 0.5, 1.0, 2.0):
        assert abs(light_deflection_arcsec(g) / light_deflection_arcsec(1.0) - (1 + g) / 2) < 1e-9


def test_mercury_precession_43_per_century():
    assert abs(mercury_precession_arcsec_century(1.0, 1.0) - 43.0) < 0.5


def test_mercury_mixes_gamma_and_beta():
    base = mercury_precession_arcsec_century(1.0, 1.0)
    # precession factor is (2 + 2 gamma - beta)/3
    assert abs(mercury_precession_arcsec_century(0.5, 0.5) / base - (2 + 1 - 0.5) / 3) < 1e-9


def test_pound_rebka_redshift():
    # Dnu/nu = g h / c^2 ~ 2.46e-15 over the 22.5 m tower
    assert abs(gravitational_redshift(22.5) - 2.46e-15) < 0.1e-15
    # linear in height
    assert abs(gravitational_redshift(45.0) - 2 * gravitational_redshift(22.5)) < 1e-30


def test_honest_scope_flags_residual_bookkeeping():
    res = run()
    sc = res["honest_scope"].lower()
    assert "contribution after subtracting" in sc or "newtonian-residual" in sc
    assert "cited not re-derived" in sc
    assert "not an engine constraint refit" in sc
