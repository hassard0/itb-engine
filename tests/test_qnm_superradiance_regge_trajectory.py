"""Tests for the superradiance spin-down endpoint / Regge trajectory (v2.246)."""

from experiments.qnm_superradiance_regge_trajectory import a_final, omega_h, run


def test_spin_down_endpoint_saturates_condition():
    # Omega_H(a_final(alpha)) == alpha by construction
    for alpha in (0.05, 0.1, 0.2, 0.3):
        assert abs(omega_h(a_final(alpha)) - alpha) < 1e-6


def test_heavier_boson_keeps_more_spin():
    # a larger alpha can only spin the hole down to a higher final spin
    assert a_final(0.1) < a_final(0.2) < a_final(0.3)


def test_extremal_boson_no_superradiance():
    # alpha >= 1/2 (= extremal Omega_H) cannot superradiate at all
    assert a_final(0.5) == 1.0
    assert a_final(0.6) == 1.0


def test_observed_spins_exclude_bosons():
    res = run()
    obs = {o["system"][:6]: o for o in res["observed_high_spin_systems"]}
    # a higher observed spin excludes heavier bosons (larger alpha)
    grs = next(o for o in res["observed_high_spin_systems"] if "GRS" in o["system"])
    cyg = next(o for o in res["observed_high_spin_systems"] if "Cyg" in o["system"])
    assert grs["excludes_alpha_below"] > cyg["excludes_alpha_below"]


def test_honest_scope_idealized_endpoint():
    res = run()
    sc = res["honest_scope"].lower()
    assert "idealized" in sc and "posteriors" in sc
    assert abs(res["consistency_check_Omega_H_at_a_final"] - 0.1) < 1e-6
    assert "g_R4_c3" in res["honest_scope"]
