"""Tests for the horizon tidal-heating absorption channel (v2.249)."""

import math

from experiments.qnm_horizon_tidal_heating import omega_h, omega_orbit, r_crit, run


def test_flux_sign_is_superradiance_condition():
    # at r_crit, Omega_orbit == Omega_H exactly (the sign flip)
    for a in (0.3, 0.5, 0.9):
        rc = r_crit(a)
        assert abs(omega_orbit(rc, a) - omega_h(a)) < 1e-9


def test_fast_spin_inspiral_is_superradiant_at_isco():
    res = run()
    rows = {r["a_star"]: r for r in res["spin_sequence"]}
    # slow spin absorbs, fast spin is superradiant at the ISCO
    assert "absorbing" in rows[0.1]["regime_at_isco"]
    assert "superradiant" in rows[0.9]["regime_at_isco"]


def test_r_crit_drops_below_isco_for_fast_spin():
    res = run()
    fast = next(r for r in res["spin_sequence"] if r["a_star"] == 0.9)
    assert fast["r_crit"] < fast["r_isco_prograde"]


def test_crossover_spin_identified():
    res = run()
    assert res["regime_crossover_near_spin"] is not None
    assert 0.3 < res["regime_crossover_near_spin"] < 0.6


def test_honest_scope_sign_not_magnitude():
    res = run()
    sc = res["honest_scope"].lower()
    assert "sign" in sc and "magnitude" in sc and "teukolsky" in sc
    assert "2.5pn" in sc or "1.5pn" in sc
    assert "g_R4_c3" in res["honest_scope"]
