"""Tests for the Swampland Distance Conjecture probe (v2.255)."""

import math

from experiments.qnm_swampland_distance_conjecture import (
    field_distance_to_cutoff,
    lyth_delta_phi,
    run,
    tower_mass_over_Mpl,
)


def test_tower_descends_exponentially():
    # m/M_Pl = exp(-alpha Delta phi/M_Pl): doubling the distance squares the mass ratio
    a = tower_mass_over_Mpl(2.0)
    b = tower_mass_over_Mpl(4.0)
    assert abs(b - a**2) < 1e-9
    assert tower_mass_over_Mpl(10.0) < 1e-4


def test_field_distance_to_cutoff_is_log():
    # Delta phi to descend to 1e-3 M_Pl ~ ln(1000) ~ 6.9
    assert abs(field_distance_to_cutoff(1e-3) - math.log(1000)) < 1e-9


def test_lyth_threshold_at_r_0p01():
    # r = 0.01 <-> Delta phi ~ M_Pl (the trans-Planckian threshold)
    assert abs(lyth_delta_phi(0.01) - 1.0) < 1e-9
    assert lyth_delta_phi(0.036) > 1.0       # current bound is trans-Planckian
    assert lyth_delta_phi(0.002) < 1.0       # future reach is sub-Planckian


def test_sdc_predicts_small_r():
    res = run()
    assert res["sdc_predicts_small_r"] is True
    rows = {r["r"]: r for r in res["lyth_bound_vs_r"]}
    assert rows[0.036]["trans_planckian"] is True
    assert rows[0.003]["trans_planckian"] is False


def test_honest_scope_conjecture_order_of_magnitude():
    res = run()
    sc = res["honest_scope"].lower()
    assert "conjecture" in sc and "order-of-magnitude" in sc
    assert "alpha" in sc
    assert "g_R4_c3" in res["honest_scope"]
