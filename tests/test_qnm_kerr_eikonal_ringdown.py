"""Tests for the eikonal Kerr ringdown frequency (v2.240)."""

import math

from experiments.qnm_kerr_eikonal_ringdown import omega_ph, run


def test_schwarzschild_limit():
    assert abs(omega_ph(0.0, True) - 1 / (3 * math.sqrt(3))) < 1e-9
    assert abs(omega_ph(0.0, False) - 1 / (3 * math.sqrt(3))) < 1e-9


def test_prograde_rises_retrograde_falls():
    res = run()
    assert res["prograde_frequency_rises_with_spin"] is True
    assert res["retrograde_frequency_falls_with_spin"] is True


def test_spin_splits_the_locking():
    # at nonzero spin the prograde and retrograde ringdown frequencies differ (locking split)
    assert omega_ph(0.7, True) > omega_ph(0.7, False)


def test_extremal_frequency_amplified():
    res = run()
    # extremal prograde photon-orbit frequency = 1/2 (the per-(l+1/2) ringdown ~2.6x Schwarzschild)
    assert abs(res["extremal_prograde_Omega_ph"] - 0.5) < 1e-9
    assert res["extremal_prograde_Omega_ph"] / (1 / (3 * math.sqrt(3))) > 2.5


def test_honest_scope_eikonal_limit():
    res = run()
    assert res["schwarzschild_limit_ok"] is True
    sc = res["honest_scope"].lower()
    assert "eikonal" in sc and "leaver" in sc
    assert "g_R4_c3" in res["honest_scope"]
