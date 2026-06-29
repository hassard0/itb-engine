"""Tests for the Hawking-Page phase transition (v2.276)."""

import math

from experiments.qnm_hawking_page_transition import (
    free_energy,
    mass,
    run,
    specific_heat,
    temperature,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_temperature_minimum_at_L_over_sqrt3():
    L = 1.0
    r_min = L / math.sqrt(3.0)
    # derivative vanishes and value is sqrt3/(2 pi L)
    dT = (temperature(r_min + 1e-6, L) - temperature(r_min - 1e-6, L)) / 2e-6
    assert abs(dT) < 1e-4
    assert abs(temperature(r_min, L) - math.sqrt(3.0) / (2 * math.pi * L)) < 1e-12


def test_free_energy_closed_form():
    L = 1.0
    for r in (0.4, 0.7, 1.0, 1.5, 2.0):
        assert abs(free_energy(r, L) - (r / 4.0) * (1 - r**2 / L**2)) < 1e-9
        assert abs(free_energy(r, L) - (mass(r, L) - temperature(r, L) * math.pi * r**2)) < 1e-9


def test_hawking_page_point_free_energy_sign_change():
    L = 1.0
    assert abs(free_energy(L, L)) < 1e-9          # F = 0 at r = L
    assert free_energy(0.8, L) > 0                 # thermal AdS dominates below
    assert free_energy(1.5, L) < 0                 # black hole dominates above


def test_T_HP_is_one_over_pi_L_and_above_T_min():
    L = 1.0
    T_hp = temperature(L, L)
    assert abs(T_hp - 1.0 / (math.pi * L)) < 1e-12
    assert T_hp > math.sqrt(3.0) / (2 * math.pi * L)   # transition is above the minimum temperature


def test_specific_heat_sign_change():
    # small branch unstable (C<0), large branch stable (C>0)
    assert specific_heat(0.4) < 0
    assert specific_heat(1.5) > 0


def test_honest_scope_flags_textbook_and_ads_cft_cited():
    res = run()
    sc = res["honest_scope"].lower()
    assert "textbook" in sc
    assert "cited not re-derived" in sc or "witten's result" in sc
    assert "not an engine constraint refit" in sc
    assert "confinement" in res["ads_cft_dual"].lower()
