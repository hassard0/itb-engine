"""Tests for the holographic / Bekenstein bound and cosmic entropy budget (v2.258)."""

import math

from experiments.qnm_holographic_bound import bh_bounds, run, universe_holographic_bound


def test_bh_saturates_both_bounds():
    for M in (1.0, 10.0, 100.0):
        b = bh_bounds(M)
        assert b["all_equal"] is True
        assert abs(b["S_BH"] - 4 * math.pi * M**2) < 1e-9


def test_universe_holographic_bound_is_1e122():
    s = universe_holographic_bound()
    assert 1e121 < s < 1e123


def test_cosmic_entropy_far_below_capacity():
    res = run()
    b = res["cosmic_entropy_budget"]
    # actual entropy << holographic capacity (the low-entropy-past puzzle)
    assert b["fraction_of_capacity_used"] < 1e-15
    # SMBHs dominate over the CMB by ~1e16
    assert b["actual_smbh_dominated"] / b["cmb"] > 1e15


def test_run_reports_saturation():
    res = run()
    assert res["bh_saturates_both"] is True


def test_honest_scope_covariant_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "covariant" in sc and "egan" in sc
    assert "order-of-magnitude" in sc
    assert "g_R4_c3" in res["honest_scope"]
