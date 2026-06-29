"""Tests for the Lorentz-violation modified-dispersion probe (v2.251)."""

from experiments.qnm_lorentz_violation_dispersion import e_qg_bound_linear, run


def test_bound_scales_linearly_with_energy_at_fixed_distance():
    # E_QG bound = (D/c) Delta E / Delta t -> linear in messenger energy
    b1 = e_qg_bound_linear(1e16, 1e9, 1.0)
    b2 = e_qg_bound_linear(1e16, 2e9, 1.0)
    assert abs(b2 / b1 - 2.0) < 1e-9
    res = run()
    assert res["energy_scaling"]["scales_linearly"] is True


def test_grb_reaches_planck_scale():
    res = run()
    grb = next(r for r in res["messenger_bounds"] if "GRB" in r["name"])
    # a single GeV GRB photon reaches ~Planck scale for linear LIV
    assert 0.1 < grb["in_units_of_E_Planck"] < 10


def test_gw_dispersion_is_weak():
    res = run()
    gw = next(r for r in res["messenger_bounds"] if "GW" in r["name"])
    # gravitons are low-energy -> a far weaker dispersion bound
    assert gw["in_units_of_E_Planck"] < 1e-15


def test_messenger_complementarity():
    res = run()
    # GW170817 supplies the strong constant-offset (n=0) bound the dispersion channel lacks
    assert "delta v" in res["gw170817_speed_bound"]["observable"].lower()
    assert "n=0" in res["gw170817_speed_bound"]["sector"]


def test_honest_scope_order_of_magnitude():
    res = run()
    sc = res["honest_scope"].lower()
    assert "order-of-magnitude" in sc and "intrinsic" in sc
    assert "n=2" in sc or "quadratic" in sc
    assert "g_R4_c3" in res["honest_scope"]
