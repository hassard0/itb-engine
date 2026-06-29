"""Tests for graviton-mass GW-dispersion bounds (v2.266)."""

import math

from experiments.qnm_graviton_mass_dispersion import (
    MG_BOUND_eV,
    compton_wavelength_m,
    dispersion_delay_s,
    graviton_velocity_over_c,
    mass_from_wavelength_eV,
    run,
    speed_deficit,
)


def test_compton_wavelength_reproduces_lvc_1e13_km():
    lam_km = compton_wavelength_m(MG_BOUND_eV) / 1e3
    assert 0.5e13 < lam_km < 5e13   # LVC: lambda_g > 1e13 km
    res = run()
    assert res["reproduces_lvc_1e13_km"] is True


def test_mass_wavelength_inverse():
    lam = compton_wavelength_m(MG_BOUND_eV)
    assert abs(mass_from_wavelength_eV(lam) - MG_BOUND_eV) < 1e-12 * MG_BOUND_eV


def test_speed_deficit_series_avoids_cancellation():
    # at m/E ~ 3e-11 the exact sqrt rounds to 1.0, but the series gives the true ~4.5e-22
    d = speed_deficit(4e-12, MG_BOUND_eV)
    assert abs(d - 0.5 * (MG_BOUND_eV / 4e-12) ** 2) < 1e-30
    assert d > 0.0
    assert graviton_velocity_over_c(4e-12, MG_BOUND_eV) == 1.0  # the cancellation it guards against


def test_consistent_with_gw170817_speed_bound():
    res = run()
    assert res["consistent_with_gw170817_speed_bound"] is True
    assert res["speed_deficit_at_ref"] < 1e-15


def test_dispersion_delay_scales_with_distance_and_is_detectable_for_gw150914():
    # GW150914: ~10 ms spread over a ~0.2 s signal -- the detectability scale that sets the bound
    res = run()
    gw = next(r for r in res["event_dispersion"] if r["name"] == "GW150914")
    assert 5e-3 < gw["dispersion_delay_s"] < 5e-2
    assert 0.01 < gw["delay_over_signal"] < 0.5
    # delay is linear in distance
    d1 = dispersion_delay_s(MG_BOUND_eV, 35.0, 250.0, 1.0e25)
    d2 = dispersion_delay_s(MG_BOUND_eV, 35.0, 250.0, 2.0e25)
    assert abs(d2 - 2 * d1) < 1e-9 * d2


def test_honest_scope_flags_order_of_magnitude_and_static_bounds():
    res = run()
    sc = res["honest_scope"].lower()
    assert "order of magnitude" in sc
    assert "matched-filter" in sc or "waveform-phase" in sc
    assert "yukawa" in sc
    # the LIV contrast is recorded
    assert "discriminant" in res["contrast_with_liv_v2251"]
