"""Tests for the Weak Gravity Conjecture probe (v2.254)."""

import math

from experiments.qnm_weak_gravity_conjecture import G_U1, run, wgc_ratio


def test_gauge_coupling_value():
    # e = sqrt(4 pi alpha) ~ 0.303
    assert abs(G_U1 - 0.303) < 0.01


def test_all_sm_particles_satisfy_wgc():
    res = run()
    assert res["all_satisfy_wgc"] is True
    for r in res["particles"]:
        assert r["wgc_ratio_z"] > 1e15      # by enormous margins


def test_force_ratio_is_z_squared():
    res = run()
    e = next(r for r in res["particles"] if r["particle"] == "electron")
    assert abs(e["force_ratio_gauge_over_grav"] / e["wgc_ratio_z"] ** 2 - 1) < 1e-9
    # electron EM beats gravity by ~5e43
    assert 1e43 < e["force_ratio_gauge_over_grav"] < 1e44


def test_lighter_particle_higher_ratio():
    # z ~ 1/m, so lighter charged particles are more super-extremal
    assert wgc_ratio(0.511e6) > wgc_ratio(938.3e6)


def test_honest_scope_conjecture():
    res = run()
    sc = res["honest_scope"].lower()
    assert "conjecture" in sc and "not a theorem" in sc
    assert "mild" in sc or "strong" in sc
    assert "g_R4_c3" in res["honest_scope"]
