"""Tests for black-hole thermodynamics (v2.257)."""

from experiments.qnm_black_hole_thermodynamics import (
    AGE_YR,
    entropy_bits,
    evaporation_time_yr,
    hawking_temperature_K,
    mass_evaporating_now_kg,
    run,
)


def test_entropy_scales_as_mass_squared():
    # S ~ M^2 (area ~ M^2): doubling the mass quadruples the entropy
    assert abs(entropy_bits(2.0) / entropy_bits(1.0) - 4.0) < 1e-9


def test_temperature_inverse_mass():
    # T_H ~ 1/M
    assert abs(hawking_temperature_K(1.0) / hawking_temperature_K(2.0) - 2.0) < 1e-9


def test_evaporation_scales_as_mass_cubed():
    assert abs(evaporation_time_yr(2.0) / evaporation_time_yr(1.0) - 8.0) < 1e-9


def test_pbh_evaporating_now_has_universe_age_lifetime():
    M = mass_evaporating_now_kg()
    assert abs(evaporation_time_yr(M) / AGE_YR - 1.0) < 1e-3
    # ~1e11 kg
    assert 1e10 < M < 1e12


def test_stellar_holes_colder_than_cmb():
    res = run()
    rows = {r["object"][:6]: r for r in res["black_holes"]}
    sun = next(r for r in res["black_holes"] if "1 Msun" in r["object"])
    assert sun["colder_than_cmb"] is True
    pbh = next(r for r in res["black_holes"] if "PBH" in r["object"])
    assert pbh["colder_than_cmb"] is False


def test_honest_scope_species_factor():
    res = run()
    sc = res["honest_scope"].lower()
    assert "species" in sc and "order-of-magnitude" in sc
    assert "schwarzschild" in sc
    assert "g_R4_c3" in res["honest_scope"]
