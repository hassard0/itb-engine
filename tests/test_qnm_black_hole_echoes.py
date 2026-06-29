"""Tests for the black-hole echo time delay (v2.247)."""

import math

from experiments.qnm_black_hole_echoes import echo_delay_M, rstar, run


def test_echo_delay_log_scaling():
    # Delta t ~ -4 ln(eps) at leading order
    for eps in (1e-10, 1e-20, 1e-40):
        assert abs(echo_delay_M(eps) - (-4 * math.log(eps))) < 2.0


def test_delay_grows_as_surface_approaches_horizon():
    assert echo_delay_M(1e-40) > echo_delay_M(1e-20) > echo_delay_M(1e-4) > 0


def test_logarithmic_sensitivity():
    # 36 orders of magnitude in eps change the delay only ~10x
    res = run()
    assert res["delay_is_log_sensitive"] is True
    assert echo_delay_M(1e-40) / echo_delay_M(1e-4) < 12


def test_tortoise_coordinate_diverges_at_horizon():
    # r* -> -inf as r -> 2M; finite at the photon sphere
    assert rstar(2.001) < rstar(3.0)
    assert rstar(2.0001) < rstar(2.001)


def test_planck_delay_is_tens_of_ms_for_stellar_bh():
    res = run()
    stellar = next(p for p in res["physical_echo_delays_planck"] if "30 Msun" in p["system"])
    # ~50 ms, the LIGO echo-search regime
    assert 0.01 < stellar["echo_delay_s_planck"] < 0.2


def test_honest_scope_geometric_optics():
    res = run()
    sc = res["honest_scope"].lower()
    assert "geometric-optics" in sc and "waveform" in sc
    assert "not a detection claim" in sc
    assert "g_R4_c3" in res["honest_scope"]
