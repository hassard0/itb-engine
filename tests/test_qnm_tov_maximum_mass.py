"""Tests for the TOV maximum mass / stability turnover (v2.290)."""

import numpy as np

from experiments.qnm_tov_maximum_mass import eps_of_P, run, sound_speed_sq, tov_star


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_mass_radius_curve_has_interior_maximum():
    res = run()
    masses = [c["M_sun"] for c in res["mass_radius_curve"]]
    imax = int(np.argmax(masses))
    assert 0 < imax < len(masses) - 1          # the maximum is a genuine turnover, not an endpoint


def test_tov_limit_order_two_solar_masses():
    res = run()
    assert 1.0 < res["M_max_solar"] < 3.5
    assert 7.0 < res["R_at_Mmax_km"] < 16.0


def test_stability_flips_at_the_turnover():
    res = run()
    masses = [c["M_sun"] for c in res["mass_radius_curve"]]
    eps = [c["eps_c"] for c in res["mass_radius_curve"]]
    dM = np.gradient(masses, eps)
    imax = int(np.argmax(masses))
    assert np.all(dM[:imax] > -1e-6)            # stable branch: dM/d rho_c > 0
    assert dM[min(imax + 2, len(dM) - 1)] < 1e-6  # unstable branch: dM/d rho_c < 0


def test_eos_causal_on_stable_branch():
    res = run()
    masses = [c["M_sun"] for c in res["mass_radius_curve"]]
    imax = int(np.argmax(masses))
    for c in res["mass_radius_curve"][:imax + 1]:
        assert c["cs2_center"] <= 1.0 + 1e-9     # sound speed below light speed
    # polytrope sound speed grows with density
    assert sound_speed_sq(2e-3) > sound_speed_sq(1e-3)


def test_tov_star_smaller_for_higher_central_density_past_peak():
    # on the unstable branch, higher central density -> smaller radius
    M1, R1 = tov_star(2.0e-3)
    M2, R2 = tov_star(2.8e-3)
    assert R2 < R1
    assert abs(eps_of_P(220.0 * (1e-3) ** 2) - 1e-3) < 1e-9   # EOS inverse is consistent


def test_honest_scope_flags_toy_polytrope():
    res = run()
    sc = res["honest_scope"].lower()
    assert "toy" in sc
    assert "representative" in sc
    assert "not an engine constraint refit" in sc
